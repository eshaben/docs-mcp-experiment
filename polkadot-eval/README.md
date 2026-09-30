# Polkadot Docs: Site Folder

Everything specific to the Polkadot developer docs (docs.polkadot.com). The general pipeline lives in `../docs_mcp/`; this folder holds only what that pipeline needs to know about Polkadot, plus Polkadot's eval set and results.

## What's here

| File | What it is |
|---|---|
| `source.json` | Site config for `docs_mcp`: the llms.txt URL, the database path, chunk sizes, and where the eval set is. |
| `eval_set.csv` / `eval_set.jsonl` | 50 seed questions, each tied to the page **and section** that answers it. All 50 were checked against the published docs on 2026-09-29. |
| `seed_questions.py` | The source list. Edit here, then rerun `verify.py`. |

## Plan

| File | Phase | What it will do |
|---|---|---|
| `results/` | 3 onward | One file per eval run, named with the date and the config it tested. Written by `docs_mcp`'s `eval` command. |
| `llms_full_baseline.py` | 5 | Load Polkadot's own pre-chunked corpus so it can be scored like any other search method. |

`llms_full_baseline.py` in pseudocode:

```
download https://docs.polkadot.com/ai/llms-full.jsonl
    (check its format first: which fields hold the text, page URL, and heading)
for each line (one pre-made chunk):
    save it to a separate `baseline_chunks` table in the same database
run the same docs_mcp search methods over those chunks
score them with docs_mcp's `eval`, same questions, same metrics
    -> "their chunks vs. our chunks, same search, same questions"
```

## Seed set at a glance

- **Areas:** 12 smart contracts, 14 chain interactions, 14 parachains, 4 node infrastructure, 6 apps.
- **Styles:** `error` (someone pastes a symptom or error message), `howto`, and `concept`.
- **Phrasing:** the questions are written the way developers talk ("my factory contract works on Sepolia but fails here"), not in the docs' own vocabulary, so they make keyword search work for its results.

**Caveat:** these are *seed* questions. I wrote them from the docs, so they're still easier than real ones. Every row has `origin: seed`, so any hand-collected questions added later (`origin: field`) can be scored separately.

## Field reference

`id`, `question`, `expected_url`, `expected_section`, `expected_anchor` (a best-guess heading anchor), `source_file`, `style`, `area`, `evidence` (a phrase that must appear in the answering section), `origin` (`seed`, or `field` for hand-collected questions), `verified`.

**Scoring tip:** count a hit at the page level (`expected_url` in the top k results) *and* at the section level (the retrieved chunk contains `evidence`). Reporting both numbers makes the effect of your chunking changes visible.
