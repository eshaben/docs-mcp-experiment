# Eval run: hybrid-split-tabs-heading-path (2026-10-08)

- **Method:** hybrid
- **Chunker:** `{"max_tokens": 600, "min_tokens": 100, "split_tabs": true, "version": "3"}`
- **Search:** `{"embedding_model": "Alibaba-NLP/gte-modernbert-base", "index_heading_path": true}`
- **Corpus:** 247 pages, 2233 chunks
- **Questions:** 63
- **Evidence in no chunk** (unfindable by any search; fix before reading the scores): none
- **Mean tokens returned in the top 1 / 3 / 5:** 265 / 791 / 1371
- **Baseline:** hybrid-baseline (2026-10-08, hybrid), mean tokens 292 / 843 / 1426

## Recall

Hits out of the questions in each row.

| questions | count | page@1 | page@3 | page@5 | section@1 | section@3 | section@5 |
|---|---|---|---|---|---|---|---|
| all | 63 | 43 (68%) | 54 (86%) | 56 (89%) | 19 (30%) | 33 (52%) | 38 (60%) |
| origin: seed | 63 | 43 (68%) | 54 (86%) | 56 (89%) | 19 (30%) | 33 (52%) | 38 (60%) |
| general | 50 | 34 (68%) | 43 (86%) | 45 (90%) | 14 (28%) | 23 (46%) | 28 (56%) |
| group: packing | 10 | 7 (70%) | 8 (80%) | 8 (80%) | 5 (50%) | 8 (80%) | 8 (80%) |
| group: tabs | 3 | 2 (67%) | 3 (100%) | 3 (100%) | 0 (0%) | 2 (67%) | 2 (67%) |

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
| s01 |  | 2 | 5 | 2 | better |
| s02 |  | 7 | 27 | 7 | better |
| s03 |  | 1 | - | - |  |
| s04 |  | 1 | 3 | 2 | better |
| s05 |  | 2 | 32 | 18 | better |
| s06 |  | 3 | 8 | 5 | better |
| s07 |  | 1 | - | 1 | found |
| s08 |  | 1 | 1 | 1 |  |
| s09 |  | 2 | 1 | 2 | worse |
| s10 |  | 1 | 3 | 2 | better |
| s11 |  | 8 | - | - |  |
| s12 |  | 1 | 4 | 4 |  |
| s13 | packing | 1 | 1 | 1 |  |
| s14 | packing | 1 | 1 | 1 |  |
| c01 |  | 1 | 4 | 2 | better |
| c02 |  | 6 | 16 | 16 |  |
| c03 |  | 1 | 1 | 1 |  |
| c04 |  | 8 | 8 | 8 |  |
| c05 |  | 3 | - | - |  |
| c06 |  | 1 | 2 | 2 |  |
| c07 |  | 1 | 1 | 1 |  |
| c08 |  | 1 | 1 | 1 |  |
| c09 |  | 1 | 1 | 1 |  |
| c10 |  | 1 | 13 | 15 | worse |
| c11 |  | 1 | 1 | 1 |  |
| c12 |  | 1 | 38 | 28 | better |
| c13 |  | 2 | 6 | 10 | worse |
| c14 |  | 1 | 1 | 1 |  |
| c15 | packing | 1 | 2 | 2 |  |
| c16 | packing | 6 | 4 | 6 | worse |
| c17 | tabs | 1 | 5 | 7 | worse |
| c18 | tabs | 2 | 3 | 3 |  |
| p01 |  | 1 | 4 | 4 |  |
| p02 |  | 1 | 1 | 4 | worse |
| p03 |  | 1 | 9 | 7 | better |
| p04 |  | 1 | 8 | 9 | worse |
| p05 |  | 1 | 1 | 1 |  |
| p06 |  | 1 | - | 35 | found |
| p07 |  | 1 | 6 | 9 | worse |
| p08 |  | 2 | - | - |  |
| p09 |  | 1 | 6 | 6 |  |
| p10 |  | 49 | - | - |  |
| p11 |  | 4 | 35 | 21 | better |
| p12 |  | 1 | 13 | 12 | better |
| p13 |  | 1 | 2 | 2 |  |
| p14 |  | 1 | 1 | 1 |  |
| p15 | packing | 1 | 2 | 2 |  |
| p16 | packing | 1 | 1 | 1 |  |
| n01 |  | 1 | 1 | 1 |  |
| n02 |  | 4 | 6 | 6 |  |
| n03 |  | 1 | - | 33 | found |
| n04 |  | 1 | 6 | 5 | better |
| n05 | packing | 21 | 20 | 21 | worse |
| n06 | packing | 1 | 1 | 1 |  |
| n07 | tabs | 1 | 6 | 2 | better |
| a01 |  | 2 | 3 | 2 | better |
| a02 |  | 1 | 1 | 1 |  |
| a03 |  | 1 | 1 | 1 |  |
| a04 |  | 3 | 4 | 3 | better |
| a05 |  | 1 | 1 | 1 |  |
| a06 |  | 1 | - | 42 | found |
| a07 | packing | 2 | 2 | 2 |  |
| a08 | packing | 1 | 1 | 1 |  |
