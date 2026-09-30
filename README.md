# Docs MCP Experiment

A docs MCP server with a measured retrieval pipeline, built for any llms.txt site and demonstrated on the Polkadot docs.

The idea: point it at a docs site's `llms.txt`, and it downloads the pages, splits them into searchable chunks, and serves them to AI assistants through an MCP server. Every search change is scored against an evaluation set of questions phrased the way developers ask them, so each design decision is backed by numbers rather than guesses.

## How it works

1. **Ingest:** read the page list from the site's `llms.txt`, and download each page's Markdown.
2. **Clean and chunk:** convert docs-generator markup into plain Markdown, then split each page by its headings. Code blocks are never split.
3. **Search, one layer at a time:** keyword search (BM25), then embeddings, then a hybrid of the two. Each layer is scored against the site's eval set.
4. **Serve:** an MCP server with `search_docs`, `get_page`, and `list_sections` tools.
5. **Compare:** classic retrieval vs. an agent that navigates the table of contents vs. the site's own pre-chunked corpus, where one exists.

Each question in the eval set names the page and section that answer it. Search is scored on whether it finds the right page and the right section in its top 1, 3 and 5 results.

## Layout

| Path | What it is |
|---|---|
| `docs_mcp/` | The general pipeline and MCP server. It contains no site-specific code. The plan for each module is in `docs_mcp/__main__.py`. |
| `polkadot-eval/` | Everything specific to the first site, the Polkadot developer docs: its config, eval set and results. See its README. |
| `tests/` | Unit tests for `docs_mcp/`. |

To add another docs site, add a sibling folder with its own `source.json` config and eval set. `docs_mcp/` doesn't change.

## What a docs site needs to provide

**Required**

1. **An `llms.txt` file** that lists the pages as Markdown list links: `- [Page title](https://site/path/)`. Every list link is used, whichever `## ` section it's under. Other lines, such as bare URLs in the intro text, are ignored.
2. **Resolved Markdown for every page.** Snippet includes and template variables must already be filled in. The Markdown URL for each link is worked out like this:

   | Link in `llms.txt` | What gets fetched |
   |---|---|
   | ends in `.md` (`https://site/path.md`) | the link itself |
   | has no file extension (`https://site/path/`) | the link with the trailing `/` removed, plus `.md`: `https://site/path.md` |
   | ends in any other extension (`.html`, `.pdf`, `.jsonl`, …) | nothing: the link is skipped and flagged |

3. **`#`-style headings.** The `# H1` is the page title, and pages are split at `## H2`, then at `### H3` when a section is long.

**Optional (used when present)**

- **Front matter** as a `---` block of `key: value` lines, such as `title`, `url`, `categories` and `version_hash`. With a `version_hash`, a re-sync only re-processes pages that changed.
- **MkDocs Material syntax.** Admonitions, content tabs, and termynal terminal widgets are converted into plain Markdown. Syntax from other docs generators is left as it is.

## Requirements

Python 3.10+. There are no other dependencies so far.
