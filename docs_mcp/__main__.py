"""docs_mcp: the plan.

Entry point: `python -m docs_mcp <command> <site-config>`.

This package works for any docs site that publishes an llms.txt file. Anything specific to
one site (its config, eval set, and results) lives in that site's own folder.


COMMANDS
========

    ingest   download the site's pages, clean them, split them into chunks, and store them
    eval     score each search method against the site's eval set
    serve    run the MCP server


SITE CONFIG
===========

    llms_txt    URL of the site's llms.txt
    db          where to store the pages and chunks
    eval_set    path to the site's eval questions
    chunking    chunk size settings


MODULES
=======

Ingest (Phase 2)
----------------
sources.py        read the page list from llms.txt and download each page's Markdown
mkdocs_clean.py   convert docs-generator markup into plain Markdown
chunking.py       split each page into chunks by heading; never split a code block
store.py          save pages and chunks to SQLite
ingest.py         run the steps above; on re-sync, only re-process pages that changed

Search (Phase 3)
----------------
search_keyword.py      keyword search (BM25)
search_embeddings.py   search by meaning (embeddings)
search_hybrid.py       combine keyword and embedding results
evaluate.py            for each search method and each eval question:
                           did the right page come back in the top 1, 3, 5?
                           did the right section come back?
                       save the scores to the site's results folder

MCP server (Phase 4)
--------------------
server.py   expose search_docs(query), get_page(url), and list_sections() as MCP tools

Comparison (Phase 5)
--------------------
navigate.py   an LLM agent that answers eval questions by browsing list_sections() and
              get_page() instead of searching; scored the same way as evaluate.py

A site's own baselines (e.g. its pre-chunked corpus) live in the site folder and are
scored by evaluate.py like any other search method.
"""

if __name__ == "__main__":
    raise SystemExit("Not implemented yet. See the plan in docs_mcp/__main__.py.")
