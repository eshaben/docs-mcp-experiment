import json
import tempfile
import unittest
from pathlib import Path

from docs_mcp import store
from docs_mcp.chunking import Chunk
from docs_mcp.sources import Page

URL = "https://x/guide/"


def _page(raw="# Guide\n", **front_matter):
    return Page(url=URL, md_url="https://x/guide.md", raw=raw, front_matter=front_matter)


class StoreTest(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        # The database's folder doesn't exist yet: `connect` has to create it.
        self.db = store.connect(Path(folder.name) / "data" / "docs.sqlite")
        self.addCleanup(self.db.close)

    def test_page_and_chunks_round_trip(self):
        page = _page(title="Guide", word_count="120", token_estimate="not a number")
        chunks = [Chunk(["Guide", "Setup"], "setup", "Install it."),
                  Chunk(["Guide", "Setup"], "setup", "Then run it.", part=1)]
        with self.db:
            store.upsert_page(self.db, page, "hash-1", ["Tooling", "Basics"])
            store.replace_chunks(self.db, URL, chunks)

        self.assertEqual(store.page_hashes(self.db), {URL: "hash-1"})
        page_row = self.db.execute("SELECT * FROM pages").fetchone()
        self.assertEqual(page_row["raw"], "# Guide\n")
        self.assertEqual(json.loads(page_row["categories"]), ["Tooling", "Basics"])
        self.assertEqual(page_row["word_count"], 120)
        self.assertIsNone(page_row["token_estimate"])

        chunk_rows = self.db.execute("SELECT * FROM chunks ORDER BY ord").fetchall()
        self.assertEqual([row["text"] for row in chunk_rows], ["Install it.", "Then run it."])
        self.assertEqual([row["part"] for row in chunk_rows], [0, 1])
        self.assertEqual(json.loads(chunk_rows[0]["heading_path"]), ["Guide", "Setup"])
        self.assertEqual(chunk_rows[0]["anchor"], "setup")
        self.assertEqual(chunk_rows[0]["content_hash"], store.sha256("Install it."))

    def test_replace_chunks_removes_the_old_ones(self):
        with self.db:
            store.upsert_page(self.db, _page(), "hash-1", [])
            store.replace_chunks(self.db, URL, [Chunk(["Guide"], "", "Old one."),
                                                Chunk(["Guide"], "", "Old two.")])
            store.replace_chunks(self.db, URL, [Chunk(["Guide"], "", "New.")])
        texts = [row["text"] for row in self.db.execute("SELECT text FROM chunks")]
        self.assertEqual(texts, ["New."])

    def test_upsert_updates_an_existing_page(self):
        with self.db:
            store.upsert_page(self.db, _page(raw="# Guide\n\nOld.\n"), "hash-1", [])
            store.upsert_page(self.db, _page(raw="# Guide\n\nNew.\n"), "hash-2", [])
        rows = self.db.execute("SELECT version_hash, raw FROM pages").fetchall()
        self.assertEqual([tuple(row) for row in rows], [("hash-2", "# Guide\n\nNew.\n")])

    def test_deleting_a_page_deletes_its_chunks(self):
        with self.db:
            store.upsert_page(self.db, _page(), "hash-1", [])
            store.replace_chunks(self.db, URL, [Chunk(["Guide"], "", "Text.")])
            store.delete_pages(self.db, [URL])
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM pages").fetchone()[0], 0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0], 0)

    def test_meta_values(self):
        self.assertIsNone(store.get_meta(self.db, "chunker"))
        self.assertEqual(store.get_meta(self.db, "chunker", "none yet"), "none yet")
        store.set_meta(self.db, "chunker", "first")
        store.set_meta(self.db, "chunker", "second")
        self.assertEqual(store.get_meta(self.db, "chunker"), "second")


if __name__ == "__main__":
    unittest.main()
