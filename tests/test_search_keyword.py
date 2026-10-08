import tempfile
import unittest
from pathlib import Path

from docs_mcp import search_keyword, store
from docs_mcp.chunking import Chunk
from docs_mcp.sources import Page

GUIDE = "https://x/guide/"
NODES = "https://x/nodes/"


class SearchKeywordTest(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.db = store.connect(Path(folder.name) / "docs.sqlite")
        self.addCleanup(self.db.close)
        with self.db:
            for url in (GUIDE, NODES):
                page = Page(url=url, md_url=url[:-1] + ".md", raw="# Page\n", front_matter={})
                store.upsert_page(self.db, page, "hash", [])
            store.replace_chunks(self.db, GUIDE, [
                Chunk(["Guide", "Install"], "install", "Download the binary and add it to PATH."),
                Chunk(["Guide", "Deploy a Contract"], "deploy-a-contract",
                      "Compile first.", part=0),
                Chunk(["Guide", "Deploy a Contract"], "deploy-a-contract",
                      "Then send the transaction and wait for the receipt.", part=1),
            ])
            store.replace_chunks(self.db, NODES, [
                Chunk(["Nodes", "Pruning"], "pruning", "A pruned node keeps only recent state."),
            ])

    def index(self, **settings):
        with self.db:
            search_keyword.build_index(self.db, **settings)

    def test_match_query_quotes_each_distinct_word(self):
        self.assertEqual(search_keyword.match_query('Why AND "why" not: eth_call?'),
                         '"why" OR "and" OR "not" OR "eth" OR "call"')
        self.assertEqual(search_keyword.match_query("?!"), "")

    def test_best_match_comes_first_with_its_metadata(self):
        self.index()
        results = search_keyword.search(self.db, "How do I run a pruned node?")
        self.assertEqual(results[0].url, NODES)
        self.assertEqual(results[0].heading_path, ["Nodes", "Pruning"])
        self.assertEqual(results[0].anchor, "pruning")
        self.assertEqual(results[0].text, "A pruned node keeps only recent state.")
        self.assertEqual(results, sorted(results, key=lambda result: -result.score))

    def test_a_question_needs_only_some_of_its_words_to_match(self):
        self.index()
        results = search_keyword.search(self.db, "where is the receipt for my swap")
        self.assertEqual([(result.url, result.part) for result in results][:1], [(GUIDE, 1)])

    def test_no_match_and_empty_query(self):
        self.index()
        self.assertEqual(search_keyword.search(self.db, "zebra"), [])
        self.assertEqual(search_keyword.search(self.db, "?!"), [])

    def test_limit(self):
        self.index()
        self.assertEqual(len(search_keyword.search(self.db, "the a it node", limit=2)), 2)

    def test_heading_path_is_searchable_only_when_switched_on(self):
        # Part 1 of the packed section doesn't contain its heading's words.
        self.index()
        parts = [result.part for result in search_keyword.search(self.db, "deploy contract")]
        self.assertEqual(parts, [])

        self.index(index_heading_path=True)
        parts = [result.part for result in search_keyword.search(self.db, "deploy contract")]
        self.assertEqual(sorted(parts), [0, 1])

    def test_rebuilding_the_index_follows_the_chunks(self):
        self.index()
        with self.db:
            store.replace_chunks(self.db, NODES, [
                Chunk(["Nodes", "Archive"], "archive", "An archive node keeps everything.")])
        self.index()
        self.assertEqual(search_keyword.search(self.db, "pruned"), [])
        self.assertEqual(len(search_keyword.search(self.db, "archive")), 1)
