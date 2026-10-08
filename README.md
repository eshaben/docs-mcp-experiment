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

## Evaluating a change

A change to cleaning, chunking or search is kept only if it helps people find answers. Unit tests and corpus checks show that the code does what was intended. Only the eval shows whether that intention was right.

**1. Change one thing at a time.**
- **Same pages.** Eval runs re-chunk the pages already stored in the database (`ingest --rechunk`, no network), because the live site changes between runs. Each result records the `version_hash` of every page it used.
- **Same questions, same search method.**
- **Each change is a switch.** A chunking or search option being evaluated gets an on/off setting in the site config, so "before" and "after" are two runs of the same code. It stays off by default until the eval shows it helps.

A run is `python3 -m docs_mcp.evaluate <site>/source.json --label <name>`, with `--baseline <results .json>` to compare it against an earlier run.

**2. Record a baseline first.** Run with the switch off and log the result. Then turn it on and run again. Questions written to test a change are written against the code *before* the change, so their baseline score shows the problem.

**3. Report enough to explain the result.**
- **Recall@1, @3 and @5, at the page level and the section level**. A page hit means the expected page is in the top k. A section hit means a chunk in the top k is on the expected page and contains the question's evidence phrase. Each phrase is chosen to appear on its page only inside the answering section, and the site's verify script enforces that, so the test gives the same verdict however the page is chunked. Both are reported for all questions, for general questions only, and for each targeted group. `seed` and `field` questions are reported separately.
- **A per-question diff:** for each question, the rank of the first chunk that counts as a section hit, before and after. With small groups, the group score is only a headline. The per-question table is the evidence, and each change in it should be explainable.
- **Tokens returned in the top k.** A chunking change also changes chunk sizes. If chunks get bigger, recall can go up just because the top 5 results cover more text.

**4. Decide by a rule written down before the run.** Keep the change if its targeted group improves, overall recall doesn't drop, and every per-question change can be explained. Log the result either way, in the site's `results/` folder, with the date and the config.

**Targeted groups.** Some questions are written to test one decision: their answer sits exactly where that decision matters, such as in a later part of a long section. Each question's `group` field is set when the question is written and never recomputed from the current chunks, so a before/after comparison always uses the same questions. Each site's README lists its groups and what each one measures.

**Limits to keep in mind.**
- **Small samples.** A group of 10 questions can show a clear win or loss, not a small effect. Aim for about 10 questions per group.
- **Easy questions.** `seed` questions are written from the docs, so they're easier than real ones. Hand-collected `field` questions are the stronger test.
- **Recall doesn't measure usefulness.** It checks that the answering passage is in a retrieved chunk, not that the chunk makes sense on its own, for example that a code snippet still shows which SDK it's for. The Phase 5 comparison, where an agent answers the questions, is where that shows.

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

3. **`#`-style headings.** The `# H1` is the page title, and pages are split at `## H2`, then at `### H3` when a section is long. A page with several H1s is treated as several guides, and each H1 titles the chunks below it.

**Optional (used when present)**

- **Front matter** as a `---` block of `key: value` lines, such as `title`, `url`, `categories` and `version_hash`. With a `version_hash`, a re-sync only re-processes pages that changed.
- **MkDocs Material syntax.** Admonitions, content tabs, and termynal terminal widgets are converted into plain Markdown. Syntax from other docs generators is left as it is.

## Requirements

Python 3.10+. There are no other dependencies so far.
