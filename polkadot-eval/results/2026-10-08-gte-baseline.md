# Eval run: gte-baseline (2026-10-08)

- **Method:** embeddings
- **Chunker:** `{"max_tokens": 600, "min_tokens": 100, "split_tabs": false, "version": "3"}`
- **Search:** `{"embedding_model": "Alibaba-NLP/gte-modernbert-base", "index_heading_path": false}`
- **Corpus:** 247 pages, 2181 chunks
- **Questions:** 63
- **Evidence in no chunk** (unfindable by any search; fix before reading the scores): none
- **Mean tokens returned in the top 1 / 3 / 5:** 245 / 689 / 1133
- **Baseline:** bm25-baseline (2026-10-08, keyword), mean tokens 315 / 972 / 1635

## Recall

Hits out of the questions in each row.

| questions | count | page@1 | page@3 | page@5 | section@1 | section@3 | section@5 |
|---|---|---|---|---|---|---|---|
| all | 63 | 40 (63%) | 50 (79%) | 51 (81%) | 23 (37%) | 28 (44%) | 31 (49%) |
| origin: seed | 63 | 40 (63%) | 50 (79%) | 51 (81%) | 23 (37%) | 28 (44%) | 31 (49%) |
| general | 50 | 30 (60%) | 40 (80%) | 41 (82%) | 18 (36%) | 21 (42%) | 22 (44%) |
| group: packing | 10 | 7 (70%) | 7 (70%) | 7 (70%) | 5 (50%) | 7 (70%) | 7 (70%) |
| group: tabs | 3 | 3 (100%) | 3 (100%) | 3 (100%) | 0 (0%) | 0 (0%) | 2 (67%) |

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
| s01 |  | 8 | 2 | 37 | worse |
| s02 |  | 3 | - | 12 | found |
| s03 |  | 2 | - | - |  |
| s04 |  | 1 | 1 | 6 | worse |
| s05 |  | 2 | - | 13 | found |
| s06 |  | 1 | 47 | 22 | better |
| s07 |  | 1 | 38 | - | lost |
| s08 |  | 1 | 5 | 1 | better |
| s09 |  | 2 | 1 | 8 | worse |
| s10 |  | 1 | 17 | 1 | better |
| s11 |  | 8 | - | - |  |
| s12 |  | 2 | 3 | 10 | worse |
| s13 | packing | 1 | 3 | 1 | better |
| s14 | packing | 1 | 1 | 2 | worse |
| c01 |  | 1 | 19 | 1 | better |
| c02 |  | 7 | - | 7 | found |
| c03 |  | 2 | 2 | 2 |  |
| c04 |  | 35 | 9 | 35 | worse |
| c05 |  | 8 | - | - |  |
| c06 |  | 1 | 3 | 1 | better |
| c07 |  | 1 | 1 | 1 |  |
| c08 |  | 1 | 1 | 1 |  |
| c09 |  | 1 | 1 | 1 |  |
| c10 |  | 1 | - | 3 | found |
| c11 |  | 1 | 3 | 1 | better |
| c12 |  | 5 | 22 | - | lost |
| c13 |  | 3 | 23 | 6 | better |
| c14 |  | 1 | 1 | 1 |  |
| c15 | packing | 1 | 9 | 1 | better |
| c16 | packing | 8 | 7 | 8 | worse |
| c17 | tabs | 1 | 5 | 8 | worse |
| c18 | tabs | 1 | 6 | 5 | better |
| p01 |  | 1 | 28 | 5 | better |
| p02 |  | 2 | 1 | 6 | worse |
| p03 |  | 1 | 19 | 19 |  |
| p04 |  | 1 | 28 | 1 | better |
| p05 |  | 1 | 1 | 1 |  |
| p06 |  | 1 | - | 38 | found |
| p07 |  | 1 | 1 | 26 | worse |
| p08 |  | 2 | 39 | - | lost |
| p09 |  | 1 | 25 | 8 | better |
| p10 |  | - | - | - |  |
| p11 |  | 1 | - | 15 | found |
| p12 |  | 1 | - | 1 | found |
| p13 |  | 1 | 10 | 1 | better |
| p14 |  | 1 | 4 | 1 | better |
| p15 | packing | 1 | 3 | 1 | better |
| p16 | packing | 1 | 1 | 3 | worse |
| n01 |  | 1 | 2 | 1 | better |
| n02 |  | 6 | 14 | 7 | better |
| n03 |  | 1 | - | - |  |
| n04 |  | 1 | 17 | 11 | better |
| n05 | packing | 49 | 4 | - | lost |
| n06 | packing | 1 | 3 | 1 | better |
| n07 | tabs | 1 | 6 | 5 | better |
| a01 |  | 2 | 5 | 2 | better |
| a02 |  | 1 | 1 | 1 |  |
| a03 |  | 1 | 2 | 1 | better |
| a04 |  | 6 | 5 | 6 | worse |
| a05 |  | 1 | 1 | 1 |  |
| a06 |  | 6 | - | 44 | found |
| a07 | packing | 13 | 1 | 13 | worse |
| a08 | packing | 1 | 1 | 1 |  |
