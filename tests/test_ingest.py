import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from docs_mcp import ingest, store

LLMS_TXT = "https://x/llms.txt"
ALPHA = "https://x/alpha/"
BETA = "https://x/beta/"


def _markdown(title, version_hash, text):
    return f"---\ntitle: {title}\nversion_hash: {version_hash}\n---\n\n# {title}\n\n## Section\n\n{text}\n"


class FakeSite:
    """Stands in for the network. `pages` maps each page URL to its Markdown, `listed` is what
    llms.txt links to, and any URL in `broken` fails to download."""

    def __init__(self):
        self.pages = {ALPHA: _markdown("Alpha", "a1", "Alpha text."),
                      BETA: _markdown("Beta", "b1", "Beta text.")}
        self.listed = [ALPHA, BETA]
        self.broken = set()
        self.requested = []

    def get(self, url, timeout=30):
        self.requested.append(url)
        if url == LLMS_TXT:
            return "# X\n\n" + "\n".join(f"- [Page]({page_url})" for page_url in self.listed)
        page_url = url[:-len(".md")] + "/"
        if page_url in self.broken or page_url not in self.pages:
            raise OSError("HTTP Error 500")
        return self.pages[page_url]


def _no_network(url, timeout=30):
    raise AssertionError(f"unexpected download of {url}")


class IngestTest(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.db_path = str(Path(folder.name) / "docs.sqlite")
        self.site = FakeSite()

    def config(self, max_tokens=600):
        return {"llms_txt": LLMS_TXT, "db": self.db_path,
                "chunking": {"max_tokens": max_tokens, "min_tokens": 100}}

    def run_quietly(self, command, config, http_get):
        """Run `ingest.sync` or `ingest.rechunk` against a fake network, with its printing hidden.
        Returns the titles of the pages it chunked."""
        with mock.patch.object(ingest, "http_get", http_get), \
                mock.patch("docs_mcp.sources.http_get", http_get), \
                mock.patch.object(ingest, "build_chunks", wraps=ingest.build_chunks) as build_chunks, \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            command(config).close()
        return sorted(call.args[1] for call in build_chunks.call_args_list)

    def sync(self, max_tokens=600):
        return self.run_quietly(ingest.sync, self.config(max_tokens), self.site.get)

    def stored(self):
        db = store.connect(self.db_path)
        self.addCleanup(db.close)
        return db

    def stored_urls(self):
        return sorted(store.page_hashes(self.stored()))

    def test_first_sync_stores_and_chunks_every_page(self):
        self.assertEqual(self.sync(), ["Alpha", "Beta"])
        self.assertEqual(self.stored_urls(), [ALPHA, BETA])
        chunk_rows = self.stored().execute("SELECT url, text FROM chunks ORDER BY url").fetchall()
        self.assertEqual([row["url"] for row in chunk_rows], [ALPHA, BETA])
        self.assertIn("Alpha text.", chunk_rows[0]["text"])
        self.assertEqual(store.get_meta(self.stored(), "chunker"),
                         ingest.chunker_signature(self.config()))

    def test_second_sync_only_rechunks_the_changed_page(self):
        self.sync()
        self.site.pages[BETA] = _markdown("Beta", "b2", "Beta text, edited.")
        self.assertEqual(self.sync(), ["Beta"])
        beta_text = self.stored().execute("SELECT text FROM chunks WHERE url = ?", (BETA,)).fetchone()
        self.assertIn("edited", beta_text["text"])

    def test_link_to_another_file_type_is_skipped(self):
        self.site.listed.append("https://x/handbook.pdf")
        self.sync()
        self.assertEqual(self.stored_urls(), [ALPHA, BETA])
        self.assertFalse(any("handbook" in url for url in self.site.requested))

    def test_page_dropped_from_llms_txt_is_deleted(self):
        self.sync()
        self.site.listed.remove(BETA)
        self.sync()
        self.assertEqual(self.stored_urls(), [ALPHA])
        chunk_urls = {row["url"] for row in self.stored().execute("SELECT url FROM chunks")}
        self.assertEqual(chunk_urls, {ALPHA})

    def test_changed_settings_rechunk_every_page(self):
        self.sync(max_tokens=600)
        self.assertEqual(self.sync(max_tokens=300), ["Alpha", "Beta"])

    def test_failed_download_deletes_nothing(self):
        self.sync()
        self.site.listed.remove(BETA)
        self.site.broken.add(ALPHA)
        self.sync()
        self.assertEqual(self.stored_urls(), [ALPHA, BETA])

    def test_failed_download_does_not_record_the_new_chunker(self):
        self.sync(max_tokens=600)
        self.site.broken.add(ALPHA)
        self.assertEqual(self.sync(max_tokens=300), ["Beta"])
        # Alpha still has chunks from the old settings, so the old signature has to stay.
        self.assertEqual(store.get_meta(self.stored(), "chunker"),
                         ingest.chunker_signature(self.config(max_tokens=600)))

        self.site.broken.clear()
        self.assertIn("Alpha", self.sync(max_tokens=300))
        self.assertEqual(store.get_meta(self.stored(), "chunker"),
                         ingest.chunker_signature(self.config(max_tokens=300)))

    def test_rechunk_uses_stored_pages_without_the_network(self):
        self.sync(max_tokens=600)
        rechunked = self.run_quietly(ingest.rechunk, self.config(max_tokens=300), _no_network)
        self.assertEqual(rechunked, ["Alpha", "Beta"])
        self.assertEqual(store.get_meta(self.stored(), "chunker"),
                         ingest.chunker_signature(self.config(max_tokens=300)))


if __name__ == "__main__":
    unittest.main()
