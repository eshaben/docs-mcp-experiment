import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from docs_mcp import evaluate, ingest, store
from docs_mcp.search_keyword import Result
from docs_mcp.sources import Page

GUIDE = "https://x/guide/"
NODES = "https://x/nodes/"
GUIDE_MARKDOWN = ("# Guide\n\n## Install\n\nDownload the binary and add it to PATH.\n\n"
                  "## Deploy\n\nSend the transaction and wait for the receipt.\n")
NODES_MARKDOWN = "# Nodes\n\n## Pruning\n\nA pruned node keeps only recent state.\n"


def _question(question_id, text, url, evidence, group="", origin="seed"):
    return {"id": question_id, "question": text, "expected_url": url, "evidence": evidence,
            "group": group, "origin": origin}


def _result(url, text):
    return Result(url, ["Page"], "", 0, text, 10, 1.0)


class ScoringTest(unittest.TestCase):
    def test_page_rank_and_section_rank(self):
        question = _question("q1", "?", GUIDE, "Wait for the Receipt")
        results = [_result(NODES, "wait for the receipt"),    # the evidence, on the wrong page
                   _result(GUIDE, "Download the binary."),    # the right page, wrong section
                   _result(GUIDE, "Then wait for the receipt.")]
        score = evaluate.score_question(question, results)
        self.assertEqual((score["page_rank"], score["section_rank"]), (2, 3))

        score = evaluate.score_question(question, results[:1])
        self.assertEqual((score["page_rank"], score["section_rank"]), (None, None))

    def test_recall_rows_count_hits_per_subset(self):
        scores = [
            {"id": "q1", "group": "", "origin": "seed", "page_rank": 1, "section_rank": 1},
            {"id": "q2", "group": "", "origin": "field", "page_rank": 3, "section_rank": None},
            {"id": "q3", "group": "tabs", "origin": "seed", "page_rank": 1, "section_rank": 5},
            {"id": "q4", "group": "tabs", "origin": "seed", "page_rank": 6, "section_rank": 6},
        ]
        rows = {row["questions"]: row for row in evaluate.recall_rows(scores)}
        self.assertEqual(list(rows), ["all", "origin: field", "origin: seed", "general",
                                      "group: tabs"])
        self.assertEqual([rows["all"][column] for column in
                          ("count", "page@1", "page@3", "page@5",
                           "section@1", "section@3", "section@5")], [4, 2, 3, 3, 1, 1, 2])
        self.assertEqual((rows["general"]["count"], rows["general"]["section@5"]), (2, 1))
        self.assertEqual((rows["group: tabs"]["count"], rows["group: tabs"]["page@5"]), (2, 1))
        self.assertEqual((rows["origin: field"]["count"], rows["origin: field"]["page@1"]), (1, 0))


class RunTest(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.site_folder = Path(folder.name)
        self.config_path = self.site_folder / "source.json"
        self.write_config(max_tokens=600)
        questions = [
            _question("q1", "how do I run a pruned node", NODES, "only recent state"),
            _question("q2", "where is my receipt", GUIDE, "wait for the receipt", group="tabs"),
            _question("q3", "what about zebras", GUIDE, "a phrase that is in no chunk"),
        ]
        (self.site_folder / "eval_set.jsonl").write_text(
            "\n".join(json.dumps(question) for question in questions) + "\n")

        config = ingest.load_config(self.config_path)
        db = store.connect(config["db"])
        with db:
            for url, markdown in ((GUIDE, GUIDE_MARKDOWN), (NODES, NODES_MARKDOWN)):
                page = Page(url=url, md_url=url[:-1] + ".md", raw=markdown, front_matter={})
                store.upsert_page(db, page, "hash-" + url, [])
        db.close()
        with contextlib.redirect_stdout(io.StringIO()):
            ingest.rechunk(config).close()

    def write_config(self, max_tokens):
        self.config_path.write_text(json.dumps({
            "llms_txt": "https://x/llms.txt", "db": "data/docs.sqlite",
            "chunking": {"max_tokens": max_tokens, "min_tokens": 100},
            "eval_set": "eval_set.jsonl"}))

    def evaluate(self, *arguments):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            evaluate.main([str(self.config_path), *arguments])
        return output.getvalue()

    def saved(self, label):
        results_folder = self.site_folder / "results"
        return json.loads(next(results_folder.glob(f"*-{label}.json")).read_text())

    def test_run_scores_and_saves(self):
        report = self.evaluate("--label", "first")
        result = self.saved("first")
        ranks = {score["id"]: (score["page_rank"], score["section_rank"])
                 for score in result["questions"]}
        self.assertEqual(ranks, {"q1": (1, 1), "q2": (1, 1), "q3": (None, None)})
        self.assertEqual(result["evidence_in_no_chunk"], ["q3"])
        self.assertEqual(result["recall"][0]["section@5"], 2)
        self.assertEqual(result["chunker"]["max_tokens"], 600)
        self.assertEqual(result["search"], {"index_heading_path": False})
        self.assertEqual(result["page_version_hashes"],
                         {GUIDE: "hash-" + GUIDE, NODES: "hash-" + NODES})
        self.assertEqual((result["pages"], result["chunks"]), (2, 3))
        self.assertIn("| group: tabs | 1 | 1 (100%)", report)
        self.assertEqual(next((self.site_folder / "results").glob("*-first.md")).read_text() + "\n",
                         report.rsplit("saved to", 1)[0])

    def test_baseline_diff(self):
        self.evaluate("--label", "before")
        baseline_path = next((self.site_folder / "results").glob("*-before.json"))
        baseline = json.loads(baseline_path.read_text())
        baseline["questions"][0]["section_rank"] = 4       # q1 was worse before
        baseline["questions"][1]["section_rank"] = None    # q2 wasn't found before
        baseline["page_version_hashes"][GUIDE] = "an older hash"
        baseline_path.write_text(json.dumps(baseline))

        report = self.evaluate("--label", "after", "--baseline", str(baseline_path))
        self.assertIn("| q1 |  | 1 | 4 | 1 | better |", report)
        self.assertIn("| q2 | tabs | 1 | - | 1 | found |", report)
        self.assertIn("| q3 |  | - | - | - |  |", report)
        self.assertIn("**Warning:** the stored pages differ from the baseline's", report)

    def test_stops_when_chunks_dont_match_the_config(self):
        self.write_config(max_tokens=300)
        with self.assertRaises(SystemExit) as stopped:
            self.evaluate("--label", "stale")
        self.assertIn("--rechunk", str(stopped.exception))
        self.assertFalse((self.site_folder / "results").exists())
