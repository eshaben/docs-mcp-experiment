# Eval run: gte-split-tabs (2026-10-08)

- **Method:** embeddings
- **Chunker:** `{"max_tokens": 600, "min_tokens": 100, "split_tabs": true, "version": "3"}`
- **Search:** `{"embedding_model": "Alibaba-NLP/gte-modernbert-base", "index_heading_path": false}`
- **Corpus:** 247 pages, 2233 chunks
- **Questions:** 63
- **Evidence in no chunk** (unfindable by any search; fix before reading the scores): none
- **Mean tokens returned in the top 1 / 3 / 5:** 226 / 674 / 1140
- **Baseline:** gte-baseline (2026-10-08, embeddings), mean tokens 245 / 689 / 1133

## Recall

Hits out of the questions in each row.

| questions | count | page@1 | page@3 | page@5 | section@1 | section@3 | section@5 |
|---|---|---|---|---|---|---|---|
| all | 63 | 39 (62%) | 50 (79%) | 51 (81%) | 22 (35%) | 28 (44%) | 32 (51%) |
| origin: seed | 63 | 39 (62%) | 50 (79%) | 51 (81%) | 22 (35%) | 28 (44%) | 32 (51%) |
| general | 50 | 30 (60%) | 40 (80%) | 41 (82%) | 18 (36%) | 21 (42%) | 22 (44%) |
| group: packing | 10 | 6 (60%) | 7 (70%) | 7 (70%) | 4 (40%) | 6 (60%) | 7 (70%) |
| group: tabs | 3 | 3 (100%) | 3 (100%) | 3 (100%) | 0 (0%) | 1 (33%) | 3 (100%) |

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
| s01 |  | 8 | 37 | 38 | worse |
| s02 |  | 3 | 12 | 13 | worse |
| s03 |  | 2 | - | - |  |
| s04 |  | 1 | 6 | 6 |  |
| s05 |  | 2 | 13 | 13 |  |
| s06 |  | 1 | 22 | 22 |  |
| s07 |  | 1 | - | - |  |
| s08 |  | 1 | 1 | 1 |  |
| s09 |  | 2 | 8 | 11 | worse |
| s10 |  | 1 | 1 | 1 |  |
| s11 |  | 8 | - | - |  |
| s12 |  | 2 | 10 | 10 |  |
| s13 | packing | 1 | 1 | 1 |  |
| s14 | packing | 1 | 2 | 2 |  |
| c01 |  | 1 | 1 | 1 |  |
| c02 |  | 7 | 7 | 7 |  |
| c03 |  | 2 | 2 | 2 |  |
| c04 |  | 40 | 35 | 40 | worse |
| c05 |  | 8 | - | - |  |
| c06 |  | 1 | 1 | 1 |  |
| c07 |  | 1 | 1 | 1 |  |
| c08 |  | 1 | 1 | 1 |  |
| c09 |  | 1 | 1 | 1 |  |
| c10 |  | 1 | 3 | 3 |  |
| c11 |  | 1 | 1 | 1 |  |
| c12 |  | 5 | - | - |  |
| c13 |  | 3 | 6 | 6 |  |
| c14 |  | 1 | 1 | 1 |  |
| c15 | packing | 1 | 1 | 1 |  |
| c16 | packing | 8 | 8 | 8 |  |
| c17 | tabs | 1 | 8 | 4 | better |
| c18 | tabs | 1 | 5 | 4 | better |
| p01 |  | 1 | 5 | 5 |  |
| p02 |  | 2 | 6 | 6 |  |
| p03 |  | 1 | 19 | 19 |  |
| p04 |  | 1 | 1 | 1 |  |
| p05 |  | 1 | 1 | 1 |  |
| p06 |  | 1 | 38 | 38 |  |
| p07 |  | 1 | 26 | 26 |  |
| p08 |  | 2 | - | - |  |
| p09 |  | 1 | 8 | 8 |  |
| p10 |  | - | - | - |  |
| p11 |  | 1 | 15 | 16 | worse |
| p12 |  | 1 | 1 | 1 |  |
| p13 |  | 1 | 1 | 1 |  |
| p14 |  | 1 | 1 | 1 |  |
| p15 | packing | 1 | 1 | 1 |  |
| p16 | packing | 1 | 3 | 3 |  |
| n01 |  | 1 | 1 | 1 |  |
| n02 |  | 6 | 7 | 7 |  |
| n03 |  | 1 | - | - |  |
| n04 |  | 1 | 11 | 11 |  |
| n05 | packing | 48 | - | - |  |
| n06 | packing | 2 | 1 | 5 | worse |
| n07 | tabs | 1 | 5 | 2 | better |
| a01 |  | 2 | 2 | 2 |  |
| a02 |  | 1 | 1 | 1 |  |
| a03 |  | 1 | 1 | 1 |  |
| a04 |  | 6 | 6 | 6 |  |
| a05 |  | 1 | 1 | 1 |  |
| a06 |  | 6 | 44 | 45 | worse |
| a07 | packing | 15 | 13 | 15 | worse |
| a08 | packing | 1 | 1 | 1 |  |
