"""Search by meaning: embed every chunk as a vector, and rank chunks by how close their vector
is to the question's.

This is the only module that needs installed packages: `sentence-transformers` (which brings
PyTorch and NumPy). Nothing else in `docs_mcp` imports it unless embedding search is asked for.

An `EmbeddingIndex` embeds the chunks when it's created. Vectors are cached in the database's
`embeddings` table, keyed by the model and a hash of exactly the text that was embedded, so
only new or changed chunks are embedded on later runs. A question is compared against every
chunk's vector directly. With a few thousand chunks that takes milliseconds, so there's no
vector index.

The default model reads up to 8,192 tokens, so no chunk is cut off, and it needs no prefix
on queries or documents. A model that does need them would need changes here.
"""
import json
import sys

import numpy

from . import store
from .search_keyword import Result

DEFAULT_MODEL = "Alibaba-NLP/gte-modernbert-base"


def load_encoder(model_name):
    """A function that turns a list of texts into one unit-length vector per text."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)

    def encode(texts):
        return model.encode(texts, batch_size=8, normalize_embeddings=True)
    return encode


def embedded_text(heading_path, text, index_heading_path):
    """What gets embedded for a chunk: its text, with its heading path ("Page > H2 > H3") on
    a line above when `index_heading_path` is on."""
    if not index_heading_path:
        return text
    return " > ".join(heading_path) + "\n\n" + text


class EmbeddingIndex:
    def __init__(self, db, model_name=DEFAULT_MODEL, index_heading_path=False):
        self.encode = load_encoder(model_name)
        db.execute("""CREATE TABLE IF NOT EXISTS embeddings (
                          model      TEXT NOT NULL,
                          text_hash  TEXT NOT NULL,   -- sha256 of the text that was embedded
                          vector     BLOB NOT NULL,   -- float32
                          PRIMARY KEY (model, text_hash))""")
        # In page order, so chunks with the same score come back in a fixed order.
        self.chunks = db.execute("SELECT url, heading_path, anchor, part, text, tokens "
                                 "FROM chunks ORDER BY url, ord").fetchall()
        texts = [embedded_text(json.loads(chunk["heading_path"]), chunk["text"],
                               index_heading_path) for chunk in self.chunks]
        text_hashes = [store.sha256(text) for text in texts]

        vectors = {row["text_hash"]: numpy.frombuffer(row["vector"], dtype=numpy.float32)
                   for row in db.execute("SELECT text_hash, vector FROM embeddings "
                                         "WHERE model = ?", (model_name,))}
        missing = {text_hash: text for text_hash, text in zip(text_hashes, texts)
                   if text_hash not in vectors}
        if missing:
            print(f"embedding {len(missing)} chunks with {model_name}...", file=sys.stderr)
            new_vectors = numpy.asarray(self.encode(list(missing.values())), dtype=numpy.float32)
            vectors.update(zip(missing, new_vectors))
            with db:
                db.executemany(
                    "INSERT INTO embeddings(model, text_hash, vector) VALUES (?,?,?)",
                    [(model_name, text_hash, vectors[text_hash].tobytes())
                     for text_hash in missing])
        self.matrix = numpy.stack([vectors[text_hash] for text_hash in text_hashes])

    def search(self, query, limit=5):
        """The `limit` chunks closest in meaning to the query, closest first."""
        if not query.strip():
            return []
        query_vector = numpy.asarray(self.encode([query]), dtype=numpy.float32)[0]
        # The vectors are unit length, so the dot product is the cosine similarity.
        scores = self.matrix @ query_vector
        best = numpy.argsort(-scores, kind="stable")[:limit]
        results = []
        for index in best:
            chunk = self.chunks[index]
            results.append(Result(chunk["url"], json.loads(chunk["heading_path"]),
                                  chunk["anchor"], chunk["part"], chunk["text"], chunk["tokens"],
                                  float(scores[index])))
        return results
