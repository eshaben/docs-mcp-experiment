import unittest

from docs_mcp.chunking import chunk_page, slugify
from docs_mcp.mkdocs_clean import clean
from docs_mcp.sources import md_url_for, parse_llms_txt, split_front_matter

PAGE = '''# My Page

Intro text.

## Setup

!!! note "Heads up"
    Use the HTTP endpoint.

=== "npm"

    ```bash
    npm install foo
    ```

=== "yarn"

    === "v1"

        ```bash
        yarn add foo
        ```

<div id="termynal" data-termynal>
  <span data-ty="input"><span class="file-path"></span>foo --version</span>
  <span data-ty>foo 1.2.3</span>
  <span data-ty>  indented &lt;ok&gt;</span>
</div>

## Code

```python
# not a heading
x = Vec<T>
```

Keep `Vec<T>` and <span class="badge">Badge</span> text. :octicons-arrow-right-24: :custom-polkadot:

<button>Copy <svg viewBox="0 0 24 24"><path d="M20 6L9 17"/></svg></button>
<svg viewBox="0 0 24 24">
  <rect x="9" y="9"/>
</svg>
After the icon.
'''


class CleanTest(unittest.TestCase):
    def setUp(self):
        self.out = clean(PAGE)

    def test_admonition(self):
        self.assertIn("**Note: Heads up**\n\nUse the HTTP endpoint.", self.out)

    def test_tabs_keep_labels_and_nesting(self):
        self.assertIn("**Tab: npm**\n\n```bash\nnpm install foo\n```", self.out)
        self.assertIn("**Tab: yarn › v1**\n\n```bash\nyarn add foo\n```", self.out)

    def test_termynal(self):
        self.assertIn("```text\n$ foo --version\nfoo 1.2.3\n  indented <ok>\n```", self.out)

    def test_html_and_code(self):
        self.assertIn("# not a heading\nx = Vec<T>", self.out)
        self.assertIn("Keep `Vec<T>` and Badge text.", self.out)
        self.assertNotIn("octicons", self.out)
        self.assertNotIn("custom-", self.out)

    def test_svg_removed_with_contents(self):
        self.assertIn("Copy\n\nAfter the icon.", self.out)
        self.assertNotIn("viewBox", self.out)
        self.assertNotIn("rect", self.out)


class ChunkTest(unittest.TestCase):
    def test_heading_paths_and_code_headings(self):
        chunks = chunk_page(clean(PAGE))
        paths = [c.heading_path for c in chunks]
        self.assertEqual(paths, [["My Page"], ["My Page", "Setup"], ["My Page", "Code"]])
        self.assertEqual([c.anchor for c in chunks], ["", "setup", "code"])

    def test_long_section_splits_at_h3_and_keeps_code_whole(self):
        code = "```\n" + "\n\n".join(f"line {i}" for i in range(400)) + "\n```"
        md = f"# T\n\n## Big\n\nLead.\n\n### A\n\nSee:\n\n{code}\n\n### B\n\n" + "word " * 50
        chunks = chunk_page(md, max_tokens=200, min_tokens=20)
        self.assertEqual([c.heading_path[1:] for c in chunks],
                         [["Big"], ["Big", "A"], ["Big", "B"]])
        self.assertIn("See:", chunks[1].text)  # lead-in stays with its code block
        self.assertTrue(chunks[1].text.rstrip().endswith("```"))

    def test_stacked_labels_stay_with_content(self):
        code = "```\n" + "\n\n".join(f"line {i}" for i in range(100)) + "\n```"
        md = f"# T\n\n## S\n\n" + "word " * 60 + f"\n\n**Tab: JS**\n\n**Note: Full code**\n\n{code}"
        chunks = chunk_page(md, max_tokens=100, min_tokens=20)
        self.assertEqual(len(chunks), 2)
        self.assertTrue(chunks[1].text.startswith("**Tab: JS**\n\n**Note: Full code**\n\n```"))

    def test_each_h1_titles_its_own_guide(self):
        md = "# Hardhat\n\n## Introduction\n\nOne.\n\n# Hardhat Polkadot\n\n## Introduction\n\nTwo.\n"
        chunks = chunk_page(md, fallback_title="Front Matter Title")
        self.assertEqual([chunk.heading_path for chunk in chunks],
                         [["Hardhat", "Introduction"], ["Hardhat Polkadot", "Introduction"]])
        self.assertNotIn("# Hardhat Polkadot", chunks[0].text)


def _code_block(line_count):
    return "```\n" + "\n\n".join(f"line {number}" for number in range(line_count)) + "\n```"


# A long section with a lead-in, two SDK tabs (the second too long for one part), and text
# after the tabs that includes an author's own bold line, which must not be treated as a label.
TABS_PAGE = f'''# T

## Query

Choose an SDK:

=== "PAPI"

    Create the script:

    {_code_block(30).replace(chr(10), chr(10) + "    ")}

=== "Dedot"

    Create the script:

    {_code_block(60).replace(chr(10), chr(10) + "    ")}

    Output:

    {_code_block(40).replace(chr(10), chr(10) + "    ")}

**Parameters**:

After the tabs. {"word " * 150}
'''


class TabSplitTest(unittest.TestCase):
    def test_off_matches_plain_packing_and_hides_markers(self):
        chunks = chunk_page(clean(TABS_PAGE), max_tokens=200, min_tokens=20)
        self.assertTrue(all(chunk.heading_path == ["T", "Query"] for chunk in chunks))
        self.assertFalse(any("%%end-block" in chunk.text for chunk in chunks))

    def test_on_gives_each_tab_its_own_path(self):
        chunks = chunk_page(clean(TABS_PAGE), max_tokens=200, min_tokens=20, split_tabs=True)
        paths = [chunk.heading_path[1:] for chunk in chunks]
        self.assertEqual(paths[0], ["Query", "Tab: PAPI"])
        self.assertIn("Choose an SDK:", chunks[0].text)  # short lead-in joins the first tab
        self.assertIn(["Query", "Tab: Dedot"], paths)
        self.assertEqual(paths[-1], ["Query"])  # text after the tabs isn't in any tab
        self.assertFalse(any("%%end-block" in chunk.text for chunk in chunks))

    def test_on_repeats_label_on_continuation_parts(self):
        chunks = chunk_page(clean(TABS_PAGE), max_tokens=200, min_tokens=20, split_tabs=True)
        dedot_parts = [chunk for chunk in chunks if chunk.heading_path[-1] == "Tab: Dedot"]
        self.assertGreater(len(dedot_parts), 1)
        self.assertEqual([chunk.part for chunk in dedot_parts], list(range(len(dedot_parts))))
        for chunk in dedot_parts[1:]:
            self.assertTrue(chunk.text.startswith("**Tab: Dedot (continued)**"))
        after_tabs = [chunk for chunk in chunks if chunk.heading_path[-1] == "Query"]
        self.assertFalse(any("(continued)" in chunk.text for chunk in after_tabs))

    def test_slugify(self):
        self.assertEqual(slugify("Install Dependencies: macOS"), "install-dependencies-macos")
        self.assertEqual(slugify("Uploads Are Rejected or `Host storage unavailable`"),
                         "uploads-are-rejected-or-host-storage-unavailable")
        self.assertEqual(slugify("eth_getBalance"), "eth_getbalance")
        self.assertEqual(slugify("The under_alias Runtime Origin"), "the-under_alias-runtime-origin")
        self.assertEqual(slugify("An _emphasized_ **bold** word"), "an-emphasized-bold-word")
        self.assertEqual(slugify("Call `_private_fn`"), "call-_private_fn")


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
        fm, body = split_front_matter("---\ntitle: T\nurl: https://x/a/\n---\n\n# T\n")
        self.assertEqual(fm, {"title": "T", "url": "https://x/a/"})
        self.assertEqual(body, "\n# T\n")


if __name__ == "__main__":
    unittest.main()
