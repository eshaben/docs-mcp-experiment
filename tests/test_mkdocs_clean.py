import unittest

from docs_mcp.mkdocs_clean import clean

# One page with every MkDocs Material construct the cleaner handles.
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
        self.cleaned = clean(PAGE)

    def test_admonition(self):
        self.assertIn("**Note: Heads up**\n\nUse the HTTP endpoint.", self.cleaned)

    def test_tabs_keep_labels_and_nesting(self):
        self.assertIn("**Tab: npm**\n\n```bash\nnpm install foo\n```", self.cleaned)
        self.assertIn("**Tab: yarn › v1**\n\n```bash\nyarn add foo\n```", self.cleaned)

    def test_termynal(self):
        self.assertIn("```text\n$ foo --version\nfoo 1.2.3\n  indented <ok>\n```", self.cleaned)

    def test_html_and_code(self):
        self.assertIn("# not a heading\nx = Vec<T>", self.cleaned)
        self.assertIn("Keep `Vec<T>` and Badge text.", self.cleaned)
        self.assertNotIn("octicons", self.cleaned)
        self.assertNotIn("custom-", self.cleaned)

    def test_svg_removed_with_contents(self):
        self.assertIn("Copy\n\nAfter the icon.", self.cleaned)
        self.assertNotIn("viewBox", self.cleaned)
        self.assertNotIn("rect", self.cleaned)


if __name__ == "__main__":
    unittest.main()
