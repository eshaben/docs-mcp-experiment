"""Hybrid search: run several search methods and merge their ranked lists into one.

The lists are merged by reciprocal rank fusion. Each method gives a chunk 1 / (60 + rank)
points, where rank is the chunk's position in that method's list, and the points are added
up. A chunk that both methods rank well beats one that only one method ranks first.

Only ranks are used, never the methods' own scores. BM25 scores and cosine similarities are
on different scales, so they can't be added, and ranks need no tuning to combine.
"""

# The constant from the original reciprocal rank fusion paper, and the usual choice. A larger
# value makes first place worth less compared with fifth.
RANK_CONSTANT = 60
# How many results to take from each method before merging.
CANDIDATES = 50


def fuse(result_lists, limit=5):
    """Merge ranked lists of results into one, best first. `score` becomes the fused score."""
    scores = {}
    results_by_chunk = {}
    for results in result_lists:
        for rank, result in enumerate(results, start=1):
            chunk = (result.url, result.position)
            scores[chunk] = scores.get(chunk, 0.0) + 1 / (RANK_CONSTANT + rank)
            results_by_chunk.setdefault(chunk, result)
    # Ties go to page order, so a run gives the same result every time.
    best = sorted(scores, key=lambda chunk: (-scores[chunk], chunk))[:limit]
    return [results_by_chunk[chunk]._replace(score=scores[chunk]) for chunk in best]


def search(searches, query, limit=5):
    """`searches` is a list of search functions, each called as `search(query, limit)`."""
    candidates = max(limit, CANDIDATES)
    return fuse([search_one(query, candidates) for search_one in searches], limit)
