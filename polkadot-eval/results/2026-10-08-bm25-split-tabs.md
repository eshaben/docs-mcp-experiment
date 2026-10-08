# Eval run: bm25-split-tabs (2026-10-08)

- **Method:** keyword
- **Chunker:** `{"max_tokens": 600, "min_tokens": 100, "split_tabs": true, "version": "3"}`
- **Search:** `{"index_heading_path": false}`
- **Corpus:** 247 pages, 2233 chunks
- **Questions:** 63
- **Evidence in no chunk** (unfindable by any search; fix before reading the scores): none
- **Mean tokens returned in the top 1 / 3 / 5:** 302 / 947 / 1617
- **Baseline:** bm25-baseline (2026-10-08), mean tokens 315 / 972 / 1635

## Recall

Hits out of the questions in each row.

| questions | count | page@1 | page@3 | page@5 | section@1 | section@3 | section@5 |
|---|---|---|---|---|---|---|---|
| all | 63 | 34 (54%) | 47 (75%) | 54 (86%) | 16 (25%) | 25 (40%) | 33 (52%) |
| origin: seed | 63 | 34 (54%) | 47 (75%) | 54 (86%) | 16 (25%) | 25 (40%) | 33 (52%) |
| general | 50 | 25 (50%) | 36 (72%) | 41 (82%) | 11 (22%) | 18 (36%) | 22 (44%) |
| group: packing | 10 | 7 (70%) | 8 (80%) | 10 (100%) | 5 (50%) | 7 (70%) | 8 (80%) |
| group: tabs | 3 | 2 (67%) | 3 (100%) | 3 (100%) | 0 (0%) | 0 (0%) | 3 (100%) |

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
| s02 |  | - | - | - |  |
| s03 |  | 4 | - | - |  |
| s04 |  | 1 | 1 | 1 |  |
| s05 |  | 1 | - | - |  |
| s06 |  | 34 | 47 | 47 |  |
| s07 |  | 31 | 38 | 40 | worse |
| s08 |  | 2 | 5 | 5 |  |
| s09 |  | 1 | 1 | 1 |  |
| s10 |  | 13 | 17 | 17 |  |
| s11 |  | 22 | - | - |  |
| s12 |  | 1 | 3 | 3 |  |
| s13 | packing | 3 | 3 | 3 |  |
| s14 | packing | 1 | 1 | 1 |  |
| c01 |  | 2 | 19 | 20 | worse |
| c02 |  | 31 | - | - |  |
| c03 |  | 1 | 2 | 2 |  |
| c04 |  | 9 | 9 | 9 |  |
| c05 |  | 6 | - | - |  |
| c06 |  | 1 | 3 | 3 |  |
| c07 |  | 1 | 1 | 1 |  |
| c08 |  | 1 | 1 | 1 |  |
| c09 |  | 1 | 1 | 1 |  |
| c10 |  | 1 | - | - |  |
| c11 |  | 3 | 3 | 3 |  |
| c12 |  | 1 | 22 | 22 |  |
| c13 |  | 1 | 23 | 24 | worse |
| c14 |  | 1 | 1 | 1 |  |
| c15 | packing | 1 | 9 | 8 | better |
| c16 | packing | 4 | 7 | 7 |  |
| c17 | tabs | 1 | 5 | 4 | better |
| c18 | tabs | 3 | 6 | 5 | better |
| p01 |  | 2 | 28 | 27 | better |
| p02 |  | 1 | 1 | 1 |  |
| p03 |  | 2 | 19 | 20 | worse |
| p04 |  | 1 | 28 | 29 | worse |
| p05 |  | 1 | 1 | 1 |  |
| p06 |  | 1 | - | - |  |
| p07 |  | 1 | 1 | 1 |  |
| p08 |  | 1 | 39 | 39 |  |
| p09 |  | 1 | 25 | 25 |  |
| p10 |  | 25 | - | - |  |
| p11 |  | 5 | - | - |  |
| p12 |  | 2 | - | - |  |
| p13 |  | 1 | 10 | 10 |  |
| p14 |  | 5 | 4 | 5 | worse |
| p15 | packing | 1 | 3 | 3 |  |
| p16 | packing | 1 | 1 | 1 |  |
| n01 |  | 2 | 2 | 2 |  |
| n02 |  | 3 | 14 | 14 |  |
| n03 |  | 1 | - | - |  |
| n04 |  | 1 | 17 | 18 | worse |
| n05 | packing | 4 | 4 | 4 |  |
| n06 | packing | 1 | 3 | 1 | better |
| n07 | tabs | 1 | 6 | 4 | better |
| a01 |  | 5 | 5 | 5 |  |
| a02 |  | 1 | 1 | 1 |  |
| a03 |  | 2 | 2 | 2 |  |
| a04 |  | 5 | 5 | 5 |  |
| a05 |  | 1 | 1 | 1 |  |
| a06 |  | 2 | - | - |  |
| a07 | packing | 1 | 1 | 1 |  |
| a08 | packing | 1 | 1 | 1 |  |
