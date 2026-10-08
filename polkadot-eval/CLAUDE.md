# Polkadot Docs: Site-Specific Context

The first site for the project. The general plan and conventions are in the root `CLAUDE.md`.

## Source
- Page list: `https://docs.polkadot.com/llms.txt`. Each page's Markdown is at the page URL + `.md`, for example `https://docs.polkadot.com/smart-contracts/connect.md`. Snippet includes and `{{ }}` variables are already resolved.
- Front matter on every page: `title`, `description`, `categories`, `url`, `word_count`, `token_estimate`, `version_hash`, `last_updated`.
- **Don't build on `llms-full.jsonl`** (linked in the intro of `llms.txt`). It's the site's own pre-chunked corpus; use it only as a Phase 5 baseline.
- Site config for the ingester: `source.json`.

## Phase 5 baseline
- Pre-chunked corpus: `https://docs.polkadot.com/ai/llms-full.jsonl`.

## Evaluation set
- 63 seed questions in `eval_set.csv` / `eval_set.jsonl`. Edit them in `seed_questions.py`, then rerun `verify.py`. Some belong to targeted groups that test one chunking decision each; see "Targeted question groups" in `README.md`.
- **Re-verifying:** `python3 polkadot-eval/verify.py` checks every item against the live published Markdown pages, the same source the pipeline ingests. Don't verify against a clone of the docs repo. All 63 passed on 2026-10-08. The live site changes, so rerun it before each eval run.
