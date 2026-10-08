"""Local SQLite store for pages and chunks.

Pages keep their raw Markdown, so chunks can be rebuilt offline when the chunker changes.
Each chunk has a `content_hash`; later layers (embeddings) should key their caches on it so
only chunks whose text actually changed get re-embedded.
"""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS pages (
    url            TEXT PRIMARY KEY,
    md_url         TEXT NOT NULL,
    title          TEXT,
    description    TEXT,
    categories     TEXT,          -- JSON list
    version_hash   TEXT,
    last_updated   TEXT,
    word_count     INTEGER,
    token_estimate INTEGER,
    raw            TEXT NOT NULL,
    fetched_at     TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chunks (
    id             INTEGER PRIMARY KEY,
    url            TEXT NOT NULL REFERENCES pages(url) ON DELETE CASCADE,
    ord            INTEGER NOT NULL,   -- position within the page
    heading_path   TEXT NOT NULL,      -- JSON list: [page title, H2, H3], maybe a "Tab: …"
    anchor         TEXT NOT NULL,      -- '' for the page intro
    part           INTEGER NOT NULL,   -- >0 when a long section was packed into several parts
    text           TEXT NOT NULL,
    tokens         INTEGER NOT NULL,
    content_hash   TEXT NOT NULL,
    UNIQUE (url, ord)
);
CREATE INDEX IF NOT EXISTS chunks_url ON chunks(url);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
"""


def connect(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(SCHEMA)
    return db


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_meta(db, key, default=None):
    row = db.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_meta(db, key, value):
    db.execute("INSERT INTO meta(key, value) VALUES (?, ?) "
               "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, value))


def page_hashes(db):
    return {row["url"]: row["version_hash"]
            for row in db.execute("SELECT url, version_hash FROM pages")}


def upsert_page(db, page, version_hash, categories):
    front_matter = page.front_matter
    db.execute(
        """INSERT INTO pages(url, md_url, title, description, categories, version_hash,
                             last_updated, word_count, token_estimate, raw, fetched_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(url) DO UPDATE SET
             md_url=excluded.md_url, title=excluded.title, description=excluded.description,
             categories=excluded.categories, version_hash=excluded.version_hash,
             last_updated=excluded.last_updated, word_count=excluded.word_count,
             token_estimate=excluded.token_estimate, raw=excluded.raw,
             fetched_at=excluded.fetched_at""",
        (page.url, page.md_url, front_matter.get("title"), front_matter.get("description"),
         json.dumps(categories), version_hash, front_matter.get("last_updated"),
         _int(front_matter.get("word_count")), _int(front_matter.get("token_estimate")), page.raw,
         datetime.now(timezone.utc).isoformat()),
    )


def replace_chunks(db, url, chunks):
    db.execute("DELETE FROM chunks WHERE url = ?", (url,))
    db.executemany(
        "INSERT INTO chunks(url, ord, heading_path, anchor, part, text, tokens, content_hash) "
        "VALUES (?,?,?,?,?,?,?,?)",
        [(url, order, json.dumps(chunk.heading_path), chunk.anchor, chunk.part, chunk.text,
          chunk.tokens, sha256(chunk.text))
         for order, chunk in enumerate(chunks)],
    )


def delete_pages(db, urls):
    db.executemany("DELETE FROM pages WHERE url = ?", [(url,) for url in urls])


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
