# Eval run: gte-heading-path (2026-10-08)

- **Method:** embeddings
- **Chunker:** `{"max_tokens": 600, "min_tokens": 100, "split_tabs": false, "version": "3"}`
- **Search:** `{"embedding_model": "Alibaba-NLP/gte-modernbert-base", "index_heading_path": true}`
- **Corpus:** 247 pages, 2181 chunks
- **Questions:** 63
- **Evidence in no chunk** (unfindable by any search; fix before reading the scores): none
- **Mean tokens returned in the top 1 / 3 / 5:** 225 / 691 / 1171
- **Baseline:** gte-baseline (2026-10-08, embeddings), mean tokens 245 / 689 / 1133

## Recall

Hits out of the questions in each row.

| questions | count | page@1 | page@3 | page@5 | section@1 | section@3 | section@5 |
|---|---|---|---|---|---|---|---|
| all | 63 | 42 (67%) | 50 (79%) | 53 (84%) | 22 (35%) | 27 (43%) | 35 (56%) |
| origin: seed | 63 | 42 (67%) | 50 (79%) | 53 (84%) | 22 (35%) | 27 (43%) | 35 (56%) |
| general | 50 | 33 (66%) | 40 (80%) | 42 (84%) | 18 (36%) | 20 (40%) | 26 (52%) |
| group: packing | 10 | 7 (70%) | 7 (70%) | 8 (80%) | 4 (40%) | 7 (70%) | 8 (80%) |
| group: tabs | 3 | 2 (67%) | 3 (100%) | 3 (100%) | 0 (0%) | 0 (0%) | 1 (33%) |

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
| s01 |  | 8 | 37 | 8 | better |
| s02 |  | 3 | 12 | 4 | better |
| s03 |  | 2 | - | - |  |
| s04 |  | 1 | 6 | 6 |  |
| s05 |  | 1 | 13 | 11 | better |
| s06 |  | 1 | 22 | 5 | better |
| s07 |  | 1 | - | 9 | found |
| s08 |  | 1 | 1 | 1 |  |
| s09 |  | 2 | 8 | 9 | worse |
| s10 |  | 1 | 1 | 1 |  |
| s11 |  | 6 | - | - |  |
| s12 |  | 2 | 10 | 9 | better |
| s13 | packing | 1 | 1 | 2 | worse |
| s14 | packing | 1 | 2 | 3 | worse |
| c01 |  | 1 | 1 | 1 |  |
| c02 |  | 6 | 7 | 6 | better |
| c03 |  | 3 | 2 | 3 | worse |
| c04 |  | 24 | 35 | 24 | better |
| c05 |  | 4 | - | - |  |
| c06 |  | 1 | 1 | 1 |  |
| c07 |  | 1 | 1 | 2 | worse |
| c08 |  | 1 | 1 | 1 |  |
| c09 |  | 1 | 1 | 1 |  |
| c10 |  | 1 | 3 | 4 | worse |
| c11 |  | 1 | 1 | 1 |  |
| c12 |  | 2 | - | - |  |
| c13 |  | 10 | 6 | 18 | worse |
| c14 |  | 1 | 1 | 1 |  |
| c15 | packing | 1 | 1 | 1 |  |
| c16 | packing | 18 | 8 | 20 | worse |
| c17 | tabs | 2 | 8 | 12 | worse |
| c18 | tabs | 1 | 5 | 4 | better |
| p01 |  | 1 | 5 | 5 |  |
| p02 |  | 2 | 6 | 14 | worse |
| p03 |  | 1 | 19 | 12 | better |
| p04 |  | 1 | 1 | 1 |  |
| p05 |  | 1 | 1 | 1 |  |
| p06 |  | 1 | 38 | 16 | better |
| p07 |  | 1 | 26 | 24 | better |
| p08 |  | 5 | - | - |  |
| p09 |  | 1 | 8 | 4 | better |
| p10 |  | - | - | - |  |
| p11 |  | 1 | 15 | 4 | better |
| p12 |  | 1 | 1 | 1 |  |
| p13 |  | 1 | 1 | 1 |  |
| p14 |  | 1 | 1 | 1 |  |
| p15 | packing | 1 | 1 | 1 |  |
| p16 | packing | 1 | 3 | 2 | better |
| n01 |  | 1 | 1 | 1 |  |
| n02 |  | 7 | 7 | 7 |  |
| n03 |  | 1 | - | 18 | found |
| n04 |  | 1 | 11 | 6 | better |
| n05 | packing | - | - | - |  |
| n06 | packing | 1 | 1 | 1 |  |
| n07 | tabs | 1 | 5 | 6 | worse |
| a01 |  | 1 | 2 | 1 | better |
| a02 |  | 1 | 1 | 1 |  |
| a03 |  | 1 | 1 | 1 |  |
| a04 |  | 9 | 6 | 9 | worse |
| a05 |  | 1 | 1 | 1 |  |
| a06 |  | 1 | 44 | 20 | better |
| a07 | packing | 4 | 13 | 4 | better |
| a08 | packing | 1 | 1 | 1 |  |
