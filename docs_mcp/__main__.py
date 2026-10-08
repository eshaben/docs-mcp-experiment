"""docs_mcp: the plan.

Planned entry point: `python -m docs_mcp <command> <site-config>`. It isn't wired up yet.
Today ingest and eval exist, and they run as `python -m docs_mcp.ingest <site-config>` and
`python -m docs_mcp.evaluate <site-config> --label <name> [--method embeddings|hybrid]`.

This package works for any docs site that publishes an llms.txt file. Anything specific to
one site (its config, eval set, and results) lives in that site's own folder.


COMMANDS
========

    ingest   download the site's pages, clean them, split them into chunks, and store them
             (built: `python -m docs_mcp.ingest`)
    eval     score each search method against the site's eval set (Phase 3)
             (built for all three search methods: `python -m docs_mcp.evaluate`)
    serve    run the MCP server (Phase 4)


SITE CONFIG
===========

    llms_txt    URL of the site's llms.txt
    db          where to store the pages and chunks
    eval_set    path to the site's eval questions
    chunking    chunking settings: the chunk sizes, and switches for changes under evaluation
    search      search settings: switches for changes under evaluation


MODULES
=======

Ingest (Phase 2)
----------------
sources.py        read the page list from llms.txt and download each page's Markdown
mdlines.py        track, line by line, whether a line is inside a fenced code block
mkdocs_clean.py   convert docs-generator markup into plain Markdown
chunking.py       split each page into chunks by heading; never split a code block
store.py          save pages and chunks to SQLite
ingest.py         run the steps above; on re-sync, only re-process pages that changed

Search (Phase 3)
----------------
search_keyword.py      keyword search (BM25, SQLite FTS5)   (built)
search_embeddings.py   search by meaning (embeddings)   (built; the only module that needs
                           installed packages: `pip install -r requirements.txt`)
search_hybrid.py       combine keyword and embedding results   (built: reciprocal rank fusion)
evaluate.py            (built, for all three search methods: `--method`)
                       for each search method and each eval question:
                           did the right page come back in the top 1, 3, 5?
                           did the right section come back? (a chunk on the expected page
                               that contains the evidence)
                       report recall for all questions, general questions only, each
                           targeted `group`, and seed vs. field questions
                       report each question's rank, and a diff against a baseline run
                       report the tokens returned in the top k
                       save the scores, the config, and the page version_hashes used
                           to the site's results folder
                       (the method is in the root README, "Evaluating a change")

MCP server (Phase 4)
--------------------
server.py   expose search_docs(query), get_page(url), and list_sections() as MCP tools
            (get_page serves cleaned text: call mkdocs_clean.remove_block_markers on it)
pyproject.toml (repo root)
            make the package installable, so an MCP client can start the server with one
            command; it replaces requirements.txt, with the embedding packages as an
            optional extra, and wires up `python -m docs_mcp <command>`

Comparison (Phase 5)
--------------------
navigate.py   an LLM agent that answers eval questions by browsing list_sections() and
              get_page() instead of searching; scored the same way as evaluate.py

A site's own baselines (e.g. its pre-chunked corpus) live in the site folder and are
scored by evaluate.py like any other search method.
"""

if __name__ == "__main__":
    raise SystemExit("Not wired up yet. Run `python -m docs_mcp.ingest <site-config>` or "
                     "`python -m docs_mcp.evaluate <site-config> --label <name>`. "
                     "The plan is in docs_mcp/__main__.py.")
