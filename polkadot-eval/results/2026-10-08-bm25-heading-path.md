# Eval run: bm25-heading-path (2026-10-08)

- **Method:** keyword
- **Chunker:** `{"max_tokens": 600, "min_tokens": 100, "split_tabs": false, "version": "3"}`
- **Search:** `{"index_heading_path": true}`
- **Corpus:** 247 pages, 2181 chunks
- **Questions:** 63
- **Evidence in no chunk** (unfindable by any search; fix before reading the scores): none
- **Mean tokens returned in the top 1 / 3 / 5:** 314 / 938 / 1569
- **Baseline:** bm25-baseline (2026-10-08), mean tokens 315 / 972 / 1635

## Recall

Hits out of the questions in each row.

| questions | count | page@1 | page@3 | page@5 | section@1 | section@3 | section@5 |
|---|---|---|---|---|---|---|---|
| all | 63 | 35 (56%) | 50 (79%) | 54 (86%) | 17 (27%) | 25 (40%) | 31 (49%) |
| origin: seed | 63 | 35 (56%) | 50 (79%) | 54 (86%) | 17 (27%) | 25 (40%) | 31 (49%) |
| general | 50 | 26 (52%) | 37 (74%) | 41 (82%) | 12 (24%) | 18 (36%) | 23 (46%) |
| group: packing | 10 | 7 (70%) | 10 (100%) | 10 (100%) | 5 (50%) | 7 (70%) | 8 (80%) |
| group: tabs | 3 | 2 (67%) | 3 (100%) | 3 (100%) | 0 (0%) | 0 (0%) | 0 (0%) |

### Baseline: bm25-baseline

| questions | count | page@1 | page@3 | page@5 | section@1 | section@3 | section@5 |
|---|---|---|---|---|---|---|---|
| all | 63 | 32 (51%) | 47 (75%) | 53 (84%) | 15 (24%) | 25 (40%) | 31 (49%) |
| origin: seed | 63 | 32 (51%) | 47 (75%) | 53 (84%) | 15 (24%) | 25 (40%) | 31 (49%) |
| general | 50 | 24 (48%) | 36 (72%) | 40 (80%) | 11 (22%) | 18 (36%) | 22 (44%) |
| group: packing | 10 | 6 (60%) | 8 (80%) | 10 (100%) | 4 (40%) | 7 (70%) | 8 (80%) |
| group: tabs | 3 | 2 (67%) | 3 (100%) | 3 (100%) | 0 (0%) | 0 (0%) | 1 (33%) |

## Per question

The rank of the first result that counts (`-` means not in the top 50).

| id | group | page rank | section rank before | section rank | change |
|---|---|---|---|---|---|
| s01 |  | 2 | 2 | 2 |  |
| s02 |  | 27 | - | 27 | found |
| s03 |  | 4 | - | - |  |
| s04 |  | 1 | 1 | 1 |  |
| s05 |  | 1 | - | 43 | found |
| s06 |  | 40 | 47 | - | lost |
| s07 |  | 3 | 38 | 3 | better |
| s08 |  | 2 | 5 | 5 |  |
| s09 |  | 1 | 1 | 1 |  |
| s10 |  | 12 | 17 | 15 | better |
| s11 |  | 24 | - | - |  |
| s12 |  | 1 | 3 | 3 |  |
| s13 | packing | 2 | 3 | 2 | better |
| s14 | packing | 1 | 1 | 1 |  |
| c01 |  | 2 | 19 | 6 | better |
| c02 |  | 35 | - | - |  |
| c03 |  | 1 | 2 | 2 |  |
| c04 |  | 12 | 9 | 12 | worse |
| c05 |  | 7 | - | 45 | found |
| c06 |  | 1 | 3 | 5 | worse |
| c07 |  | 1 | 1 | 1 |  |
| c08 |  | 1 | 1 | 1 |  |
| c09 |  | 1 | 1 | 1 |  |
| c10 |  | 1 | - | - |  |
| c11 |  | 3 | 3 | 3 |  |
| c12 |  | 1 | 22 | 14 | better |
| c13 |  | 1 | 23 | 24 | worse |
| c14 |  | 1 | 1 | 1 |  |
| c15 | packing | 1 | 9 | 9 |  |
| c16 | packing | 3 | 7 | 7 |  |
| c17 | tabs | 1 | 5 | 7 | worse |
| c18 | tabs | 2 | 6 | 6 |  |
| p01 |  | 2 | 28 | 31 | worse |
| p02 |  | 1 | 1 | 1 |  |
| p03 |  | 2 | 19 | 20 | worse |
| p04 |  | 1 | 28 | 26 | better |
| p05 |  | 1 | 1 | 1 |  |
| p06 |  | 1 | - | - |  |
| p07 |  | 1 | 1 | 1 |  |
| p08 |  | 2 | 39 | 43 | worse |
| p09 |  | 1 | 25 | 25 |  |
| p10 |  | 27 | - | - |  |
| p11 |  | 10 | - | - |  |
| p12 |  | 1 | - | - |  |
| p13 |  | 1 | 10 | 6 | better |
| p14 |  | 5 | 4 | 5 | worse |
| p15 | packing | 1 | 3 | 4 | worse |
| p16 | packing | 1 | 1 | 1 |  |
| n01 |  | 2 | 2 | 2 |  |
| n02 |  | 3 | 14 | 15 | worse |
| n03 |  | 1 | - | - |  |
| n04 |  | 1 | 17 | 17 |  |
| n05 | packing | 3 | 4 | 3 | better |
| n06 | packing | 1 | 3 | 1 | better |
| n07 | tabs | 1 | 6 | 6 |  |
| a01 |  | 4 | 5 | 4 | better |
| a02 |  | 1 | 1 | 1 |  |
| a03 |  | 1 | 2 | 1 | better |
| a04 |  | 4 | 5 | 4 | better |
| a05 |  | 1 | 1 | 1 |  |
| a06 |  | 2 | - | - |  |
| a07 | packing | 1 | 1 | 1 |  |
| a08 | packing | 1 | 1 | 1 |  |
