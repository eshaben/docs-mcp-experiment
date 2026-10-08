"""Score search against a site's eval set.

    python -m docs_mcp.evaluate polkadot-eval/source.json --label bm25-baseline
    python -m docs_mcp.evaluate polkadot-eval/source.json --label bm25-split-tabs \\
        --baseline polkadot-eval/results/2026-10-08-bm25-baseline.json
    python -m docs_mcp.evaluate polkadot-eval/source.json --method embeddings --label gte-baseline

`--method` is `keyword` (the default) or `embeddings`. Embedding search needs the
`sentence-transformers` package, and embeds any chunks it hasn't seen before it scores.

It scores the chunks already in the database, so after changing a `chunking` setting, run
`python -m docs_mcp.ingest <config> --rechunk` first. (It stops if the stored chunks weren't
built with the config's settings.) Search settings come from the config's `search` block:

    "search": {"index_heading_path": false}

`index_heading_path` applies to both methods. `embedding_model` can be added to name a model
other than the default.

For each question it searches once and records two ranks:
  - page rank: the first result on the expected page
  - section rank: the first result on the expected page whose text contains the evidence phrase
Recall@k is the share of questions whose rank is k or better.

Each run writes two files to the site's `results/` folder, named `<date>-<label>`: a `.json`
with everything (it's what `--baseline` reads) and a `.md` with the report that's printed.
The method is in the root README, "Evaluating a change".
"""
import argparse
import json
from datetime import date
from pathlib import Path

from . import search_keyword, store
from .ingest import chunker_signature, load_config

CUTOFFS = (1, 3, 5)
# How far down the results to look for a question's rank. Recall only needs the top 5, but
# "rank 6" and "rank 40" are different failures, and the per-question diff should show which.
RANK_DEPTH = 50


def load_questions(path):
    with open(path) as lines:
        return [json.loads(line) for line in lines if line.strip()]


def has_evidence(question, url, text):
    """The section-hit rule: the chunk is on the expected page and contains the evidence."""
    return url == question["expected_url"] and question["evidence"].lower() in text.lower()


def first_rank(results, counts):
    """The 1-based position of the first result that `counts`, or None."""
    for rank, result in enumerate(results, start=1):
        if counts(result):
            return rank
    return None


def score_question(question, results):
    return {
        "id": question["id"],
        "group": question["group"],
        "origin": question["origin"],
        "page_rank": first_rank(results, lambda result: result.url == question["expected_url"]),
        "section_rank": first_rank(
            results, lambda result: has_evidence(question, result.url, result.text)),
    }


def recall_rows(scores):
    """One row of hit counts per subset: all questions, each origin, general questions (no
    group), and each targeted group."""
    subsets = [("all", scores)]
    for origin in sorted({score["origin"] for score in scores}):
        subsets.append((f"origin: {origin}",
                        [score for score in scores if score["origin"] == origin]))
    subsets.append(("general", [score for score in scores if not score["group"]]))
    for group in sorted({score["group"] for score in scores if score["group"]}):
        subsets.append((f"group: {group}", [score for score in scores if score["group"] == group]))

    rows = []
    for name, subset in subsets:
        row = {"questions": name, "count": len(subset)}
        for level in ("page", "section"):
            for cutoff in CUTOFFS:
                row[f"{level}@{cutoff}"] = sum(
                    score[f"{level}_rank"] is not None and score[f"{level}_rank"] <= cutoff
                    for score in subset)
        rows.append(row)
    return rows


def searcher(db, method, config):
    """The search function for a method, `search(query, limit)`, and the settings it used."""
    settings = dict(config.get("search", {}))
    index_heading_path = settings.get("index_heading_path", False)
    if method == "keyword":
        with db:
            search_keyword.build_index(db, index_heading_path)
        return (lambda query, limit: search_keyword.search(db, query, limit),
                {"index_heading_path": index_heading_path})
    # Imported here so that keyword search works without the embedding packages installed.
    from . import search_embeddings
    model_name = settings.get("embedding_model", search_embeddings.DEFAULT_MODEL)
    index = search_embeddings.EmbeddingIndex(db, model_name, index_heading_path)
    return index.search, {"index_heading_path": index_heading_path, "embedding_model": model_name}


def run(config, questions, label, method="keyword"):
    db = store.connect(config["db"])
    if store.get_meta(db, "chunker") != chunker_signature(config):
        raise SystemExit("The stored chunks weren't built with this config's chunking settings. "
                         "Run `python -m docs_mcp.ingest <config> --rechunk` first.")
    search, search_settings = searcher(db, method, config)

    # A question whose evidence is in no chunk can't be found by any search method. That's a
    # chunking or eval-set bug (or the stored pages are older than the eval set), not a miss.
    chunks = db.execute("SELECT url, text FROM chunks").fetchall()
    evidence_in_no_chunk = [
        question["id"] for question in questions
        if not any(has_evidence(question, chunk["url"], chunk["text"]) for chunk in chunks)]

    scores = []
    tokens_returned = {cutoff: 0 for cutoff in CUTOFFS}
    for question in questions:
        results = search(question["question"], RANK_DEPTH)
        scores.append(score_question(question, results))
        for cutoff in CUTOFFS:
            tokens_returned[cutoff] += sum(result.tokens for result in results[:cutoff])

    result = {
        "label": label,
        "date": date.today().isoformat(),
        "method": method,
        "chunker": json.loads(chunker_signature(config)),
        "search": search_settings,
        "pages": db.execute("SELECT COUNT(*) FROM pages").fetchone()[0],
        "chunks": len(chunks),
        "evidence_in_no_chunk": evidence_in_no_chunk,
        "recall": recall_rows(scores),
        "mean_tokens_in_top": {str(cutoff): round(total / len(questions))
                               for cutoff, total in tokens_returned.items()},
        "questions": scores,
        "page_version_hashes": store.page_hashes(db),
    }
    db.close()
    return result


def format_report(result, baseline=None):
    lines = [
        f"# Eval run: {result['label']} ({result['date']})",
        "",
        f"- **Method:** {result['method']}",
        f"- **Chunker:** `{json.dumps(result['chunker'], sort_keys=True)}`",
        f"- **Search:** `{json.dumps(result['search'], sort_keys=True)}`",
        f"- **Corpus:** {result['pages']} pages, {result['chunks']} chunks",
        f"- **Questions:** {len(result['questions'])}",
        "- **Evidence in no chunk** (unfindable by any search; fix before reading the scores): "
        + (", ".join(result["evidence_in_no_chunk"]) or "none"),
        "- **Mean tokens returned in the top 1 / 3 / 5:** "
        + " / ".join(str(result["mean_tokens_in_top"][str(cutoff)]) for cutoff in CUTOFFS),
    ]
    if baseline:
        lines.append(f"- **Baseline:** {baseline['label']} ({baseline['date']}, "
                     f"{baseline['method']}), mean tokens "
                     + " / ".join(str(baseline["mean_tokens_in_top"][str(cutoff)])
                                  for cutoff in CUTOFFS))
        lines += [f"- **Warning:** {warning}" for warning in _baseline_warnings(result, baseline)]

    lines += ["", "## Recall", "", "Hits out of the questions in each row.", ""]
    lines += _recall_table(result)
    if baseline:
        lines += ["", f"### Baseline: {baseline['label']}", ""]
        lines += _recall_table(baseline)

    lines += ["", "## Per question", "",
              f"The rank of the first result that counts (`-` means not in the top {RANK_DEPTH})."]
    if baseline:
        before = {score["id"]: score for score in baseline["questions"]}
        lines += ["", "| id | group | page rank | section rank before | section rank | change |",
                  "|---|---|---|---|---|---|"]
        for score in result["questions"]:
            rank_before = before.get(score["id"], {}).get("section_rank")
            lines.append(f"| {score['id']} | {score['group']} | {_rank(score['page_rank'])} "
                         f"| {_rank(rank_before)} | {_rank(score['section_rank'])} "
                         f"| {_change(rank_before, score['section_rank'])} |")
    else:
        lines += ["", "| id | group | page rank | section rank |", "|---|---|---|---|"]
        for score in result["questions"]:
            lines.append(f"| {score['id']} | {score['group']} | {_rank(score['page_rank'])} "
                         f"| {_rank(score['section_rank'])} |")
    return "\n".join(lines) + "\n"


def _recall_table(result):
    columns = [f"{level}@{cutoff}" for level in ("page", "section") for cutoff in CUTOFFS]
    lines = ["| questions | count | " + " | ".join(columns) + " |",
             "|---|---|" + "---|" * len(columns)]
    for row in result["recall"]:
        cells = [f"{row[column]} ({row[column] / row['count']:.0%})" if row["count"] else "-"
                 for column in columns]
        lines.append(f"| {row['questions']} | {row['count']} | " + " | ".join(cells) + " |")
    return lines


def _baseline_warnings(result, baseline):
    """Differences that make the two runs not comparable."""
    warnings = []
    if result["page_version_hashes"] != baseline["page_version_hashes"]:
        warnings.append("the stored pages differ from the baseline's")
    if ([score["id"] for score in result["questions"]]
            != [score["id"] for score in baseline["questions"]]):
        warnings.append("the questions differ from the baseline's")
    return warnings


def _rank(rank):
    return "-" if rank is None else str(rank)


def _change(rank_before, rank_after):
    if rank_before == rank_after:
        return ""
    if rank_after is None:
        return "lost"
    if rank_before is None:
        return "found"
    return "better" if rank_after < rank_before else "worse"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("config", help="path to a source JSON config")
    parser.add_argument("--label", required=True,
                        help="a short name for the config being tested, used in the file name")
    parser.add_argument("--method", choices=("keyword", "embeddings"), default="keyword")
    parser.add_argument("--baseline", help="a results .json to compare against")
    args = parser.parse_args(argv)

    site_folder = Path(args.config).resolve().parent
    config = load_config(args.config)
    result = run(config, load_questions(site_folder / config["eval_set"]), args.label,
                 args.method)
    baseline = json.loads(Path(args.baseline).read_text()) if args.baseline else None
    report = format_report(result, baseline)

    results_folder = site_folder / "results"
    results_folder.mkdir(exist_ok=True)
    name = f"{result['date']}-{args.label}"
    (results_folder / f"{name}.json").write_text(json.dumps(result, indent=1) + "\n")
    (results_folder / f"{name}.md").write_text(report)
    print(report)
    print(f"saved to {results_folder / name}.json and .md")


if __name__ == "__main__":
    main()
