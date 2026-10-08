import unittest

from docs_mcp import search_hybrid
from docs_mcp.search_keyword import Result

GUIDE = "https://x/guide/"
NODES = "https://x/nodes/"


def _result(url, position, score=1.0):
    return Result(url, position, ["Page"], "", 0, f"{url} {position}", 10, score)


def _chunks(results):
    return [(result.url, result.position) for result in results]


class FuseTest(unittest.TestCase):
    def test_a_chunk_both_lists_rank_well_beats_one_ranked_first_by_one(self):
        keyword = [_result(GUIDE, 0), _result(GUIDE, 1), _result(NODES, 0)]
        embeddings = [_result(NODES, 1), _result(GUIDE, 1), _result(GUIDE, 2)]
        fused = search_hybrid.fuse([keyword, embeddings])
        self.assertEqual(_chunks(fused)[0], (GUIDE, 1))
        self.assertEqual(len(fused), 5)    # every distinct chunk, once
        self.assertAlmostEqual(fused[0].score, 2 / (search_hybrid.RANK_CONSTANT + 2))

    def test_scores_are_ignored_and_only_ranks_count(self):
        keyword = [_result(GUIDE, 0, score=900.0), _result(GUIDE, 1, score=1.0)]
        embeddings = [_result(GUIDE, 1, score=0.9), _result(GUIDE, 0, score=0.1)]
        fused = search_hybrid.fuse([keyword, embeddings])
        self.assertEqual(fused[0].score, fused[1].score)
        self.assertEqual(_chunks(fused), [(GUIDE, 0), (GUIDE, 1)])    # a tie: page order

    def test_limit(self):
        keyword = [_result(GUIDE, position) for position in range(4)]
        self.assertEqual(_chunks(search_hybrid.fuse([keyword, []], limit=2)),
                         [(GUIDE, 0), (GUIDE, 1)])


class SearchTest(unittest.TestCase):
    def test_each_method_is_asked_for_more_than_the_limit(self):
        asked = []

        def search_one(query, limit):
            asked.append((query, limit))
            return [_result(GUIDE, position) for position in range(limit)]

        results = search_hybrid.search([search_one, search_one], "a question", limit=3)
        self.assertEqual(asked, [("a question", search_hybrid.CANDIDATES)] * 2)
        self.assertEqual(_chunks(results), [(GUIDE, 0), (GUIDE, 1), (GUIDE, 2)])
