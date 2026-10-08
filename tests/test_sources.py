import unittest

from docs_mcp.sources import md_url_for, parse_llms_txt, split_front_matter


class SourcesTest(unittest.TestCase):
    def test_llms_txt_only_list_links(self):
        text = "# X\n\n> Corpus: https://x/full.jsonl\n\n## Pages\n\n- [A](https://x/a/)\n\n## More\n\n- [B](https://x/b/)\n"
        self.assertEqual(parse_llms_txt(text), [("A", "https://x/a/"), ("B", "https://x/b/")])

    def test_md_url(self):
        self.assertEqual(md_url_for("https://x/a/b/"), "https://x/a/b.md")
        self.assertEqual(md_url_for("https://x/a/b.md"), "https://x/a/b.md")
        self.assertIsNone(md_url_for("https://x/a/b.html"))
        self.assertIsNone(md_url_for("https://x/ai/llms-full.jsonl"))
        self.assertEqual(md_url_for("https://x/v1.2/"), "https://x/v1.2.md")

    def test_front_matter(self):
        front_matter, body = split_front_matter("---\ntitle: T\nurl: https://x/a/\n---\n\n# T\n")
        self.assertEqual(front_matter, {"title": "T", "url": "https://x/a/"})
        self.assertEqual(body, "\n# T\n")


if __name__ == "__main__":
    unittest.main()
