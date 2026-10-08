import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from docs_mcp import store
from docs_mcp.chunking import Chunk
from docs_mcp.sources import Page

try:
    import numpy
    from docs_mcp import search_embeddings
except ImportError:
    numpy = None

GUIDE = "https://x/guide/"
NODES = "https://x/nodes/"
VOCABULARY = ["deploy", "contract", "receipt", "pruned", "node", "binary"]


class FakeEncoder:
    """Stands in for the model: a text's vector counts the vocabulary words in it. It records
    every text it's asked to embed."""

    def __init__(self):
        self.embedded = []

    def __call__(self, texts):
        self.embedded += texts
        vectors = numpy.array([[text.lower().count(word) for word in VOCABULARY]
                               for text in texts], dtype=float) + 0.01
        return vectors / numpy.linalg.norm(vectors, axis=1, keepdims=True)


@unittest.skipUnless(numpy, "embedding search needs numpy")
class SearchEmbeddingsTest(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.db = store.connect(Path(folder.name) / "docs.sqlite")
        self.addCleanup(self.db.close)
        self.encoder = FakeEncoder()
        with self.db:
            for url in (GUIDE, NODES):
                page = Page(url=url, md_url=url[:-1] + ".md", raw="# Page\n", front_matter={})
                store.upsert_page(self.db, page, "hash", [])
            store.replace_chunks(self.db, GUIDE, [
                Chunk(["Guide", "Install"], "install", "Download the binary."),
                Chunk(["Guide", "Deploy a Contract"], "deploy-a-contract",
                      "Send it and wait for the receipt.", part=1),
            ])
            store.replace_chunks(self.db, NODES, [
                Chunk(["Nodes", "Pruning"], "pruning", "A pruned node keeps recent state."),
            ])

    def index(self, model_name="fake-model", **settings):
        with mock.patch.object(search_embeddings, "load_encoder", return_value=self.encoder), \
                contextlib.redirect_stderr(io.StringIO()):
            return search_embeddings.EmbeddingIndex(self.db, model_name, **settings)

    def test_closest_chunk_comes_first_with_its_metadata(self):
        results = self.index().search("where is my receipt", limit=2)
        self.assertEqual(len(results), 2)
        self.assertEqual((results[0].url, results[0].part), (GUIDE, 1))
        self.assertEqual(results[0].heading_path, ["Guide", "Deploy a Contract"])
        self.assertEqual(results[0].anchor, "deploy-a-contract")
        self.assertGreater(results[0].score, results[1].score)

    def test_empty_query(self):
        self.assertEqual(self.index().search("  "), [])

    def test_vectors_are_cached_and_only_new_text_is_embedded(self):
        self.index()
        self.assertEqual(len(self.encoder.embedded), 3)
        self.index()
        self.assertEqual(len(self.encoder.embedded), 3)

        with self.db:
            store.replace_chunks(self.db, NODES, [
                Chunk(["Nodes", "Pruning"], "pruning", "A pruned node keeps recent state."),
                Chunk(["Nodes", "Archive"], "archive", "An archive node keeps everything."),
            ])
        index = self.index()
        self.assertEqual(self.encoder.embedded[3:], ["An archive node keeps everything."])
        self.assertEqual(index.search("pruned node", limit=1)[0].anchor, "pruning")

    def test_each_model_has_its_own_cache(self):
        self.index()
        self.index(model_name="another-model")
        self.assertEqual(len(self.encoder.embedded), 6)

    def test_heading_path_is_embedded_only_when_switched_on(self):
        # The chunk's own text says nothing about deploying a contract.
        results = self.index().search("deploy contract", limit=1)
        self.assertNotEqual(results[0].anchor, "deploy-a-contract")

        index = self.index(index_heading_path=True)
        self.assertIn("Guide > Deploy a Contract\n\nSend it and wait for the receipt.",
                      self.encoder.embedded)
        self.assertEqual(index.search("deploy contract", limit=1)[0].anchor, "deploy-a-contract")
