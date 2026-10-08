# Polkadot Docs: Site Folder

Everything specific to the Polkadot developer docs (docs.polkadot.com). The general pipeline lives in `../docs_mcp/`; this folder holds only what that pipeline needs to know about Polkadot, plus Polkadot's eval set and results.

## What's here

| File | What it is |
|---|---|
| `source.json` | Site config for `docs_mcp`: the llms.txt URL, the database path, chunk sizes, search settings, and where the eval set is. |
| `eval_set.csv` / `eval_set.jsonl` | 63 seed questions, each tied to the page **and section** that answers it. All 63 were checked against the published docs on 2026-10-08. |
| `seed_questions.py` | The source list. Edit here, then rerun `verify.py`. |
| `verify.py` | Downloads each expected page's published Markdown and checks that the page exists, the section heading exists, and the evidence phrase appears in that section and nowhere else on the page. Rewrites the CSV and JSONL files, and exits with status 1 if any question fails. |
| `results/` | One `.json` and one `.md` per eval run, named with the date and the config it tested. Written by `docs_mcp/evaluate.py`. The runs are listed under "Results so far". |

## Results so far

Recall is hits out of 63 questions. Each run's `.md` file has the per-group scores and the per-question ranks.

| Run | What changed | Page @1 / @3 / @5 | Section @1 / @3 / @5 |
|---|---|---|---|
| `2026-10-08-bm25-baseline` | Keyword search (BM25) with every switch off. | 32 / 47 / 53 | 15 / 25 / 31 |
| `2026-10-08-bm25-split-tabs` | `chunking.split_tabs` on. | 34 / 47 / 54 | 16 / 25 / 33 |
| `2026-10-08-bm25-heading-path` | `search.index_heading_path` on. | 35 / 50 / 54 | 17 / 25 / 31 |

Both switches are still off in `source.json`. Neither has been decided yet.

## Plan

| File | Phase | What it will do |
|---|---|---|
| `llms_full_baseline.py` | 5 | Load Polkadot's own pre-chunked corpus so it can be scored like any other search method. |

`llms_full_baseline.py` in pseudocode:

```
download https://docs.polkadot.com/ai/llms-full.jsonl
    (check its format first: which fields hold the text, page URL, and heading)
for each line (one pre-made chunk):
    save it to a separate `baseline_chunks` table in the same database
run the same docs_mcp search methods over those chunks
score them with docs_mcp/evaluate.py, same questions, same metrics
    -> "their chunks vs. our chunks, same search, same questions"
```

## Seed set at a glance

- **Areas:** 14 smart contracts, 18 chain interactions, 16 parachains, 7 node infrastructure, 8 apps.
- **Styles:** `error` (someone pastes a symptom or error message), `howto`, and `concept`.
- **Phrasing:** the questions are written the way developers talk ("my factory contract works on Sepolia but fails here"), not in the docs' own vocabulary, so they make keyword search work for its results.

## Targeted question groups

Most questions are general. Some were written to test one specific chunking decision: their answers sit in exactly the place that decision affects. Each group's recall is reported next to the overall numbers, so we can see whether a change helped the case it was meant to fix. Membership is set in `GROUPS` in `seed_questions.py`, and `verify.py` writes it to each question's `group` field.

A question's group is fixed when the question is written. It isn't recomputed from the current chunks, because the chunker changes are what we're measuring, and a recomputed group would shift with them.

| Group | Questions | Where the answer is (when the question was added) | What it measures |
|---|---|---|---|
| `packing` | s13, s14, c15, c16, p15, p16, n05, n06, a07, a08 | Part 1+ of a long section that was packed into parts. Those parts don't contain the section's heading line. | Whether packed content stays findable. Also whether indexing the heading path helps, and whether 600/100 are good sizes. |
| `tabs` | c17, c18, n07 | The part after a tab's label, split away from it (a Python SDK script, a Dedot script, a systemd unit file). | The tab split (tabs as a split level, with labels repeated on continuation parts). Expect these to improve after that change. |

When adding a group: write the questions against the chunker *before* the change, confirm their evidence lands where the group says, add a row here, and log the group's baseline score.

**Caveat:** these are *seed* questions. I wrote them from the docs, so they're still easier than real ones. Every row has `origin: seed`, so any hand-collected questions added later (`origin: field`) can be scored separately.

## Field reference

`id`, `question`, `expected_url`, `expected_section`, `expected_anchor` (the section's link, with the anchor generated the way the chunker generates it), `style`, `area`, `evidence` (a phrase that appears in the answering section and nowhere else on that page), `origin` (`seed`, or `field` for hand-collected questions), `group` (empty, or one of the targeted groups above), `verified`.

**Scoring tip:** count a hit at the page level (`expected_url` in the top k results) *and* at the section level (a retrieved chunk is on the expected page and contains `evidence`, case-insensitive). The page is part of the test because a phrase can also appear on other pages. The section isn't, because `verify.py` already guarantees the phrase appears on its page only inside the expected section. That keeps the test independent of how the page was chunked. Reporting both numbers makes the effect of your chunking changes visible.
