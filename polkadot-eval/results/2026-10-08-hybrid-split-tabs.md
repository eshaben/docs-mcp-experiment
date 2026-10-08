# Eval run: hybrid-split-tabs (2026-10-08)

- **Method:** hybrid
- **Chunker:** `{"max_tokens": 600, "min_tokens": 100, "split_tabs": true, "version": "3"}`
- **Search:** `{"embedding_model": "Alibaba-NLP/gte-modernbert-base", "index_heading_path": false}`
- **Corpus:** 247 pages, 2233 chunks
- **Questions:** 63
- **Evidence in no chunk** (unfindable by any search; fix before reading the scores): none
- **Mean tokens returned in the top 1 / 3 / 5:** 276 / 820 / 1404
- **Baseline:** hybrid-baseline (2026-10-08, hybrid), mean tokens 292 / 843 / 1426

## Recall

Hits out of the questions in each row.

| questions | count | page@1 | page@3 | page@5 | section@1 | section@3 | section@5 |
|---|---|---|---|---|---|---|---|
| all | 63 | 44 (70%) | 52 (83%) | 56 (89%) | 21 (33%) | 31 (49%) | 37 (59%) |
| origin: seed | 63 | 44 (70%) | 52 (83%) | 56 (89%) | 21 (33%) | 31 (49%) | 37 (59%) |
| general | 50 | 34 (68%) | 41 (82%) | 44 (88%) | 15 (30%) | 20 (40%) | 25 (50%) |
| group: packing | 10 | 7 (70%) | 8 (80%) | 9 (90%) | 5 (50%) | 8 (80%) | 9 (90%) |
| group: tabs | 3 | 3 (100%) | 3 (100%) | 3 (100%) | 1 (33%) | 3 (100%) | 3 (100%) |

### Baseline: hybrid-baseline

| questions | count | page@1 | page@3 | page@5 | section@1 | section@3 | section@5 |
|---|---|---|---|---|---|---|---|
| all | 63 | 44 (70%) | 52 (83%) | 56 (89%) | 20 (32%) | 29 (46%) | 36 (57%) |
| origin: seed | 63 | 44 (70%) | 52 (83%) | 56 (89%) | 20 (32%) | 29 (46%) | 36 (57%) |
| general | 50 | 34 (68%) | 41 (82%) | 44 (88%) | 15 (30%) | 20 (40%) | 25 (50%) |
| group: packing | 10 | 7 (70%) | 8 (80%) | 9 (90%) | 5 (50%) | 8 (80%) | 9 (90%) |
| group: tabs | 3 | 3 (100%) | 3 (100%) | 3 (100%) | 0 (0%) | 1 (33%) | 2 (67%) |

## Per question

The rank of the first result that counts (`-` means not in the top 50).

| id | group | page rank | section rank before | section rank | change |
|---|---|---|---|---|---|
| s01 |  | 5 | 5 | 5 |  |
| s02 |  | 17 | 27 | 29 | worse |
| s03 |  | 1 | - | - |  |
| s04 |  | 1 | 3 | 3 |  |
| s05 |  | 2 | 32 | 32 |  |
| s06 |  | 3 | 8 | 8 |  |
| s07 |  | 2 | - | - |  |
| s08 |  | 1 | 1 | 1 |  |
| s09 |  | 1 | 1 | 1 |  |
| s10 |  | 1 | 3 | 3 |  |
| s11 |  | 9 | - | - |  |
| s12 |  | 1 | 4 | 4 |  |
| s13 | packing | 1 | 1 | 1 |  |
| s14 | packing | 1 | 1 | 1 |  |
| c01 |  | 1 | 4 | 4 |  |
| c02 |  | 6 | 16 | 16 |  |
| c03 |  | 1 | 1 | 1 |  |
| c04 |  | 8 | 8 | 8 |  |
| c05 |  | 3 | - | - |  |
| c06 |  | 1 | 2 | 2 |  |
| c07 |  | 1 | 1 | 1 |  |
| c08 |  | 1 | 1 | 1 |  |
| c09 |  | 1 | 1 | 1 |  |
| c10 |  | 1 | 13 | 13 |  |
| c11 |  | 1 | 1 | 1 |  |
| c12 |  | 3 | 38 | 38 |  |
| c13 |  | 5 | 6 | 6 |  |
| c14 |  | 1 | 1 | 1 |  |
| c15 | packing | 1 | 2 | 2 |  |
| c16 | packing | 4 | 4 | 4 |  |
| c17 | tabs | 1 | 5 | 3 | better |
| c18 | tabs | 1 | 3 | 3 |  |
| p01 |  | 1 | 4 | 4 |  |
| p02 |  | 1 | 1 | 1 |  |
| p03 |  | 1 | 9 | 9 |  |
| p04 |  | 1 | 8 | 8 |  |
| p05 |  | 1 | 1 | 1 |  |
| p06 |  | 1 | - | - |  |
| p07 |  | 1 | 6 | 6 |  |
| p08 |  | 1 | - | - |  |
| p09 |  | 1 | 6 | 6 |  |
| p10 |  | 41 | - | - |  |
| p11 |  | 7 | 35 | 37 | worse |
| p12 |  | 1 | 13 | 13 |  |
| p13 |  | 1 | 2 | 2 |  |
| p14 |  | 1 | 1 | 1 |  |
| p15 | packing | 1 | 2 | 2 |  |
| p16 | packing | 1 | 1 | 1 |  |
| n01 |  | 1 | 1 | 1 |  |
| n02 |  | 3 | 6 | 6 |  |
| n03 |  | 1 | - | - |  |
| n04 |  | 1 | 6 | 6 |  |
| n05 | packing | 21 | 20 | 21 | worse |
| n06 | packing | 1 | 1 | 1 |  |
| n07 | tabs | 1 | 6 | 1 | better |
| a01 |  | 3 | 3 | 3 |  |
| a02 |  | 1 | 1 | 1 |  |
| a03 |  | 1 | 1 | 1 |  |
| a04 |  | 4 | 4 | 4 |  |
| a05 |  | 1 | 1 | 1 |  |
| a06 |  | 1 | - | - |  |
| a07 | packing | 2 | 2 | 2 |  |
| a08 | packing | 1 | 1 | 1 |  |
