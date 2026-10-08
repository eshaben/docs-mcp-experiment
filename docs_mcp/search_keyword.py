"""Keyword search (BM25) over the stored chunks, using SQLite's FTS5.

`build_index` copies the chunks into an FTS5 table, `chunks_fts`, in the same database. Call it
again whenever the chunks change: it's rebuilt from scratch each time (well under a second).

A question is searched as an OR of its words, so a chunk doesn't need every word to match.
BM25 then ranks the matches: rare words count for more than common ones, and a short chunk
that mentions a word ranks above a long one that mentions it as often.

Words are matched exactly, apart from case and accents (FTS5's default `unicode61` tokenizer).
There's no stemming, so "deploying" doesn't match "deploy".
"""
import json
import re
from typing import NamedTuple

# A run of letters and digits: the same pieces the `unicode61` tokenizer indexes.
WORD = re.compile(r"[^\W_]+")


class Result(NamedTuple):
    url: str
    heading_path: list
    anchor: str
    part: int
    text: str
    tokens: int
    score: float    # higher is better


def build_index(db, index_heading_path=False):
    """Rebuild `chunks_fts` from the `chunks` table. With `index_heading_path`, each chunk's
    heading path ("Page > H2 > H3") is searchable along with its text."""
    db.execute("DROP TABLE IF EXISTS chunks_fts")
    db.execute("CREATE VIRTUAL TABLE chunks_fts USING fts5(heading_path, text)")
    rows = db.execute("SELECT id, heading_path, text FROM chunks").fetchall()
    db.executemany(
        "INSERT INTO chunks_fts(rowid, heading_path, text) VALUES (?,?,?)",
        [(row["id"],
          " > ".join(json.loads(row["heading_path"])) if index_heading_path else "",
          row["text"])
         for row in rows],
    )


def match_query(query):
    """The FTS5 MATCH expression for a free-text query: each distinct word, quoted so FTS5
    doesn't read it as query syntax, joined with OR."""
    words = dict.fromkeys(word.lower() for word in WORD.findall(query))
    return " OR ".join(f'"{word}"' for word in words)


def search(db, query, limit=5):
    """The `limit` best-matching chunks, best first."""
    match = match_query(query)
    if not match:
        return []
    # FTS5's bm25() is lower for better matches, so it's negated into a score.
    rows = db.execute(
        """SELECT chunks.url, chunks.heading_path, chunks.anchor, chunks.part, chunks.text,
                  chunks.tokens, -bm25(chunks_fts) AS score
           FROM chunks_fts JOIN chunks ON chunks.id = chunks_fts.rowid
           WHERE chunks_fts MATCH ?
           ORDER BY score DESC, chunks.url, chunks.ord
           LIMIT ?""",
        (match, limit),
    )
    return [Result(row["url"], json.loads(row["heading_path"]), row["anchor"], row["part"],
                   row["text"], row["tokens"], row["score"])
            for row in rows]
