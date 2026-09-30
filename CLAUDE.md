# Docs MCP Server: Project Context

## Goal
A docs MCP server with a measured retrieval pipeline, built for any llms.txt site and demonstrated on the Polkadot docs.

**Findability is the measure of success:** a change is worth keeping only if it helps users find answers, as measured by the eval.

## Plan (phases)
0. Pick the docs and tools: the Polkadot developer docs as the first site, and Python 3.10+.
1. Build an evaluation set for the site.
2. Ingest and chunk.
3. Search, one layer at a time: keyword (BM25) → embeddings → hybrid. Score each layer against the eval set.
4. Wrap it as an MCP server with tools `search_docs(query)`, `get_page(url)`, and `list_sections()`. Test it in an MCP client and refine the tool descriptions.
5. Comparison experiment: classic retrieval vs. agentic table-of-contents navigation vs. the site's own pre-chunked corpus. Log which failures are really docs gaps.

Each folder's plan lives in that folder: `docs_mcp/__main__.py` for the general package, `polkadot-eval/README.md` for Polkadot.

## Layout
- `docs_mcp/` is general: no site-specific code, URLs, or constants.
- Each docs site gets its own folder (`polkadot-eval/`) for its config, eval set, and results. That folder's `CLAUDE.md` holds the site-specific details.
- Tests go in `tests/`.

## Ingest and chunking decisions
- **Source:** each page's resolved Markdown, found through the site's `llms.txt`. A link ending in `.md` is fetched as-is. A link with no extension gets `.md` appended, after its trailing `/` is removed. Links with any other extension are skipped and flagged.
- **Front matter:** use it when present. Use `url` and `categories` as chunk metadata. Use `version_hash` to re-process only changed pages on re-sync, falling back to a hash of the raw Markdown.
- **Chunking:** split by heading (H2, with H3 as sub-chunks when a section is long). Store the heading path, for example `Page > H2 > H3`. Ignore `#` lines inside fenced code (they're comments, not headings). Keep code blocks whole, so some chunks will be large; keep that in mind when picking an embedding model.
- **Cleanup:** convert MkDocs Material leftovers (termynal HTML, admonitions, content tabs) into plain Markdown, keeping tab labels with their content. Measure its effect in Phase 3 by running the eval with and without it.

## Evaluation
- Fields: `id`, `question`, `expected_url`, `expected_section`, `expected_anchor`, `source_file`, `style` (error/howto/concept), `area`, `evidence`, `origin` (seed / field), `verified`.
- **Scoring:** report a hit at the page level (`expected_url` in the top k) and at the section level (the retrieved chunk contains `evidence`, case-insensitive). Report recall@1, @3, and @5.
- **Keep origins separate:** `seed` questions were written from the docs and are easier than real ones. If hand-collected `field` questions are added, report their scores separately.

## Conventions
- Keep dependencies light, and prefer local-first storage: SQLite (FTS5 for keyword search, plus a vector extension) or LanceDB/Chroma. No hosted vector database.
- Every search change gets an eval run, and the results are logged to the site's `results/` folder with a date and a config description.
