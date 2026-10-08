"""Ingest a docs site into a local SQLite store.

    python -m docs_mcp.ingest polkadot-eval/source.json            # sync (only changed pages)
    python -m docs_mcp.ingest polkadot-eval/source.json --rechunk  # rebuild chunks offline
    python -m docs_mcp.ingest polkadot-eval/source.json --stats    # print chunk stats

The source config is a JSON file; relative paths in it resolve against the config's directory:

    {
      "llms_txt": "https://docs.polkadot.com/llms.txt",
      "db": "data/docs.sqlite",
      "chunking": {"max_tokens": 600, "min_tokens": 100, "split_tabs": false}
    }

Sync compares each page's front-matter `version_hash` (or a hash of the raw Markdown when a
site has none) with the stored one, and only re-chunks pages that changed. Pages no longer in
llms.txt are deleted. If the chunker or its settings change, all pages are re-chunked.
"""
import argparse
import json
import statistics
import sys
from pathlib import Path

from . import chunking, store
from .mdlines import FenceTracker
from .mkdocs_clean import clean
from .sources import fetch_pages, http_get, md_url_for, parse_llms_txt, split_front_matter

# Markup that should never survive cleaning, outside code. Any count above 0 is a cleaner bug.
LEFTOVER_MARKUP = {
    "termynal": "<span data-ty",
    "admonition": "\n!!! ",
    "tab": '\n=== "',
    "div": "<div",
    "svg": "<svg",
    "block marker": "%%end-block",
}


def load_config(path):
    path = Path(path)
    config = json.loads(path.read_text())
    config["db"] = str((path.parent / config["db"]).resolve())
    config.setdefault("chunking", {})
    return config


def chunker_signature(config):
    return json.dumps({"version": chunking.CHUNKER_VERSION, **config["chunking"]}, sort_keys=True)


def build_chunks(page_raw, title, config):
    _, body = split_front_matter(page_raw)
    return chunking.chunk_page(clean(body), fallback_title=title, **config["chunking"])


def categories_of(front_matter):
    return [category.strip() for category in front_matter.get("categories", "").split(",")
            if category.strip()]


def sync(config, workers=8):
    db = store.connect(config["db"])
    links = parse_llms_txt(http_get(config["llms_txt"]))
    urls = list(dict.fromkeys(url for _, url in links))
    skipped = [url for url in urls if md_url_for(url) is None]
    urls = [url for url in urls if url not in skipped]
    print(f"llms.txt lists {len(urls) + len(skipped)} links; fetching {len(urls)}...")
    pages, failures = fetch_pages(urls, workers)

    signature = chunker_signature(config)
    rechunk_all = store.get_meta(db, "chunker") != signature
    known = store.page_hashes(db)
    counts = {"added": 0, "changed": 0, "unchanged": 0, "rechunked": 0}
    with db:
        for page in pages:
            version_hash = (page.front_matter.get("version_hash")
                            or "sha256:" + store.sha256(page.raw))
            status = ("added" if page.url not in known else
                      "unchanged" if known[page.url] == version_hash else "changed")
            if status == "unchanged" and not rechunk_all:
                counts["unchanged"] += 1
                continue
            store.upsert_page(db, page, version_hash, categories_of(page.front_matter))
            store.replace_chunks(db, page.url,
                                 build_chunks(page.raw, page.front_matter.get("title"), config))
            counts["rechunked" if status == "unchanged" else status] += 1

        # Only prune when every page fetched, so a network blip doesn't delete half the corpus.
        listed = {page.url for page in pages}
        removed = [] if failures else [url for url in known if url not in listed]
        store.delete_pages(db, removed)
        # Only record the new chunker signature when every page fetched. Otherwise a page that
        # failed would keep chunks from the old chunker, and later syncs wouldn't know to redo it.
        if not failures:
            store.set_meta(db, "chunker", signature)
        store.set_meta(db, "llms_txt", config["llms_txt"])

    print(", ".join(f"{status}: {count}" for status, count in counts.items())
          + f", removed: {len(removed)}")
    for url in skipped:
        print(f"SKIPPED {url}: not a Markdown page", file=sys.stderr)
    for url, error in failures:
        print(f"FAILED {url}: {error}", file=sys.stderr)
    return db


def rechunk(config):
    db = store.connect(config["db"])
    with db:
        rows = db.execute("SELECT url, title, raw FROM pages").fetchall()
        for row in rows:
            store.replace_chunks(db, row["url"], build_chunks(row["raw"], row["title"], config))
        store.set_meta(db, "chunker", chunker_signature(config))
    print(f"re-chunked {len(rows)} pages")
    return db


def print_stats(db):
    texts = [row["text"] for row in db.execute("SELECT text FROM chunks")]
    tokens = [row["tokens"] for row in db.execute("SELECT tokens FROM chunks")]
    page_count = db.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
    if not tokens:
        print("no chunks")
        return
    percentiles = statistics.quantiles(tokens, n=20)
    continuation_parts = db.execute("SELECT COUNT(*) FROM chunks WHERE part > 0").fetchone()[0]
    print(f"pages: {page_count}  chunks: {len(tokens)}  ({len(tokens) / page_count:.1f}/page)")
    print(f"tokens/chunk: median {statistics.median(tokens):.0f}, p5 {percentiles[0]:.0f}, "
          f"p95 {percentiles[-1]:.0f}, max {max(tokens)}")
    print(f"chunks under 50 tokens: {sum(count < 50 for count in tokens)}; "
          f"continuation parts of long sections: {continuation_parts}")
    prose = [_prose(text) for text in texts]
    found = {name: sum(needle in chunk_prose for chunk_prose in prose)
             for name, needle in LEFTOVER_MARKUP.items()}
    print("leftover markup outside code: "
          + ", ".join(f"{name} {count}" for name, count in found.items()))


def _prose(text):
    """The chunk's text outside fenced code, with a leading newline so line-start needles match."""
    fence = FenceTracker()
    return "\n" + "\n".join(line for line in text.split("\n") if not fence.is_code(line))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("config", help="path to a source JSON config")
    parser.add_argument("--rechunk", action="store_true", help="rebuild chunks from stored pages")
    parser.add_argument("--stats", action="store_true", help="only print stats for the existing db")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.stats:
        db = store.connect(config["db"])
    elif args.rechunk:
        db = rechunk(config)
    else:
        db = sync(config, args.workers)
    print_stats(db)


if __name__ == "__main__":
    main()
