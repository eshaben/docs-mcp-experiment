import unittest

from docs_mcp.chunking import chunk_page, slugify
from docs_mcp.mkdocs_clean import clean

PAGE = '''# My Page

Intro text.

## Setup

Install it first.

## Code

```python
# not a heading
x = 1
```
'''


def _code_block(line_count):
    return "```\n" + "\n\n".join(f"line {number}" for number in range(line_count)) + "\n```"


class ChunkTest(unittest.TestCase):
    def test_heading_paths_and_code_headings(self):
        chunks = chunk_page(PAGE)
        self.assertEqual([chunk.heading_path for chunk in chunks],
                         [["My Page"], ["My Page", "Setup"], ["My Page", "Code"]])
        self.assertEqual([chunk.anchor for chunk in chunks], ["", "setup", "code"])

    def test_long_section_splits_at_h3_and_keeps_code_whole(self):
        markdown = (f"# T\n\n## Big\n\nLead.\n\n### A\n\nSee:\n\n{_code_block(400)}\n\n### B\n\n"
                    + "word " * 50)
        chunks = chunk_page(markdown, max_tokens=200, min_tokens=20)
        self.assertEqual([chunk.heading_path[1:] for chunk in chunks],
                         [["Big"], ["Big", "A"], ["Big", "B"]])
        self.assertIn("See:", chunks[1].text)  # lead-in stays with its code block
        self.assertTrue(chunks[1].text.rstrip().endswith("```"))

    def test_stacked_labels_stay_with_content(self):
        markdown = ("# T\n\n## S\n\n" + "word " * 60
                    + f"\n\n**Tab: JS**\n\n**Note: Full code**\n\n{_code_block(100)}")
        chunks = chunk_page(markdown, max_tokens=100, min_tokens=20)
        self.assertEqual(len(chunks), 2)
        self.assertTrue(chunks[1].text.startswith("**Tab: JS**\n\n**Note: Full code**\n\n```"))

    def test_each_h1_titles_its_own_guide(self):
        markdown = "# Hardhat\n\n## Introduction\n\nOne.\n\n# Hardhat Polkadot\n\n## Introduction\n\nTwo.\n"
        chunks = chunk_page(markdown, fallback_title="Front Matter Title")
        self.assertEqual([chunk.heading_path for chunk in chunks],
                         [["Hardhat", "Introduction"], ["Hardhat Polkadot", "Introduction"]])
        self.assertNotIn("# Hardhat Polkadot", chunks[0].text)


class SlugifyTest(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(slugify("Install Dependencies: macOS"), "install-dependencies-macos")
        self.assertEqual(slugify("Uploads Are Rejected or `Host storage unavailable`"),
                         "uploads-are-rejected-or-host-storage-unavailable")
        self.assertEqual(slugify("eth_getBalance"), "eth_getbalance")
        self.assertEqual(slugify("The under_alias Runtime Origin"), "the-under_alias-runtime-origin")
        self.assertEqual(slugify("An _emphasized_ **bold** word"), "an-emphasized-bold-word")
        self.assertEqual(slugify("Call `_private_fn`"), "call-_private_fn")


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


if __name__ == "__main__":
    unittest.main()
