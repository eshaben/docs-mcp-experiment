# Eval run: hybrid-baseline (2026-10-08)

- **Method:** hybrid
- **Chunker:** `{"max_tokens": 600, "min_tokens": 100, "split_tabs": false, "version": "3"}`
- **Search:** `{"embedding_model": "Alibaba-NLP/gte-modernbert-base", "index_heading_path": false}`
- **Corpus:** 247 pages, 2181 chunks
- **Questions:** 63
- **Evidence in no chunk** (unfindable by any search; fix before reading the scores): none
- **Mean tokens returned in the top 1 / 3 / 5:** 292 / 843 / 1426
- **Baseline:** gte-baseline (2026-10-08, embeddings), mean tokens 245 / 689 / 1133

## Recall

Hits out of the questions in each row.

| questions | count | page@1 | page@3 | page@5 | section@1 | section@3 | section@5 |
|---|---|---|---|---|---|---|---|
| all | 63 | 44 (70%) | 52 (83%) | 56 (89%) | 20 (32%) | 29 (46%) | 36 (57%) |
| origin: seed | 63 | 44 (70%) | 52 (83%) | 56 (89%) | 20 (32%) | 29 (46%) | 36 (57%) |
| general | 50 | 34 (68%) | 41 (82%) | 44 (88%) | 15 (30%) | 20 (40%) | 25 (50%) |
| group: packing | 10 | 7 (70%) | 8 (80%) | 9 (90%) | 5 (50%) | 8 (80%) | 9 (90%) |
| group: tabs | 3 | 3 (100%) | 3 (100%) | 3 (100%) | 0 (0%) | 1 (33%) | 2 (67%) |

### Baseline: gte-baseline

| questions | count | page@1 | page@3 | page@5 | section@1 | section@3 | section@5 |
|---|---|---|---|---|---|---|---|
| all | 63 | 40 (63%) | 50 (79%) | 51 (81%) | 23 (37%) | 28 (44%) | 31 (49%) |
| origin: seed | 63 | 40 (63%) | 50 (79%) | 51 (81%) | 23 (37%) | 28 (44%) | 31 (49%) |
| general | 50 | 30 (60%) | 40 (80%) | 41 (82%) | 18 (36%) | 21 (42%) | 22 (44%) |
| group: packing | 10 | 7 (70%) | 7 (70%) | 7 (70%) | 5 (50%) | 7 (70%) | 7 (70%) |
| group: tabs | 3 | 3 (100%) | 3 (100%) | 3 (100%) | 0 (0%) | 0 (0%) | 2 (67%) |

## Per question

The rank of the first result that counts (`-` means not in the top 50).

| id | group | page rank | section rank before | section rank | change |
|---|---|---|---|---|---|
| s01 |  | 5 | 37 | 5 | better |
| s02 |  | 16 | 12 | 27 | worse |
| s03 |  | 1 | - | - |  |
| s04 |  | 1 | 6 | 3 | better |
| s05 |  | 2 | 13 | 32 | worse |
| s06 |  | 3 | 22 | 8 | better |
| s07 |  | 2 | - | - |  |
| s08 |  | 1 | 1 | 1 |  |
| s09 |  | 1 | 8 | 1 | better |
| s10 |  | 1 | 1 | 3 | worse |
| s11 |  | 9 | - | - |  |
| s12 |  | 1 | 10 | 4 | better |
| s13 | packing | 1 | 1 | 1 |  |
| s14 | packing | 1 | 2 | 1 | better |
| c01 |  | 1 | 1 | 4 | worse |
| c02 |  | 6 | 7 | 16 | worse |
| c03 |  | 1 | 2 | 1 | better |
| c04 |  | 8 | 35 | 8 | better |
| c05 |  | 3 | - | - |  |
| c06 |  | 1 | 1 | 2 | worse |
| c07 |  | 1 | 1 | 1 |  |
| c08 |  | 1 | 1 | 1 |  |
| c09 |  | 1 | 1 | 1 |  |
| c10 |  | 1 | 3 | 13 | worse |
| c11 |  | 1 | 1 | 1 |  |
| c12 |  | 3 | - | 38 | found |
| c13 |  | 5 | 6 | 6 |  |
| c14 |  | 1 | 1 | 1 |  |
| c15 | packing | 1 | 1 | 2 | worse |
| c16 | packing | 4 | 8 | 4 | better |
| c17 | tabs | 1 | 8 | 5 | better |
| c18 | tabs | 1 | 5 | 3 | better |
| p01 |  | 1 | 5 | 4 | better |
| p02 |  | 1 | 6 | 1 | better |
| p03 |  | 1 | 19 | 9 | better |
| p04 |  | 1 | 1 | 8 | worse |
| p05 |  | 1 | 1 | 1 |  |
| p06 |  | 1 | 38 | - | lost |
| p07 |  | 1 | 26 | 6 | better |
| p08 |  | 1 | - | - |  |
| p09 |  | 1 | 8 | 6 | better |
| p10 |  | 41 | - | - |  |
| p11 |  | 7 | 15 | 35 | worse |
| p12 |  | 1 | 1 | 13 | worse |
| p13 |  | 1 | 1 | 2 | worse |
| p14 |  | 1 | 1 | 1 |  |
| p15 | packing | 1 | 1 | 2 | worse |
| p16 | packing | 1 | 3 | 1 | better |
| n01 |  | 1 | 1 | 1 |  |
| n02 |  | 3 | 7 | 6 | better |
| n03 |  | 1 | - | - |  |
| n04 |  | 1 | 11 | 6 | better |
| n05 | packing | 20 | - | 20 | found |
| n06 | packing | 1 | 1 | 1 |  |
| n07 | tabs | 1 | 5 | 6 | worse |
| a01 |  | 3 | 2 | 3 | worse |
| a02 |  | 1 | 1 | 1 |  |
| a03 |  | 1 | 1 | 1 |  |
| a04 |  | 4 | 6 | 4 | better |
| a05 |  | 1 | 1 | 1 |  |
| a06 |  | 1 | 44 | - | lost |
| a07 | packing | 2 | 13 | 2 | better |
| a08 | packing | 1 | 1 | 1 |  |
