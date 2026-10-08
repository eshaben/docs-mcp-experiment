"""Verify the seed eval items against the published docs, then write the eval set files.

For each item in seed_questions.py, downloads the page's published Markdown (the same source
the pipeline ingests) and checks that:
  1. the page exists,
  2. the expected section heading exists on that page,
  3. the evidence phrase appears in that section,
  4. the evidence phrase appears nowhere else on the page. With that, "a chunk of this page
     contains the evidence" means "a chunk of this section", however the page is chunked.
Writes eval_set.jsonl (read by the pipeline) and eval_set.csv (for browsing). Exits with
status 1 if any item fails, so a broken eval set is noticed before an eval run.

Run from anywhere:  python3 polkadot-eval/verify.py
"""
import csv
import json
import re
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))  # so `docs_mcp` can be imported
sys.path.insert(0, str(HERE))

from docs_mcp.chunking import slugify
from docs_mcp.mdlines import FenceTracker
from docs_mcp.sources import http_get, md_url_for, split_front_matter
from seed_questions import GROUPS, SEED

AREAS = {"s": "smart-contracts", "c": "chain-interactions", "p": "parachains",
         "n": "node-infrastructure", "a": "apps"}


def site_base_url():
    """The site's root URL, taken from the llms.txt URL in source.json."""
    config = json.loads((HERE / "source.json").read_text())
    parts = urllib.parse.urlsplit(config["llms_txt"])
    return f"{parts.scheme}://{parts.netloc}/"


def page_url(base_url, doc_path):
    """`smart-contracts/connect.md` -> `https://docs.polkadot.com/smart-contracts/connect/`"""
    path = doc_path[:-len(".md")]
    if path == "index" or path.endswith("/index"):
        path = path[:-len("index")]
    else:
        path += "/"
    return base_url + path


def section_text(markdown, heading):
    """The text under `heading`, up to the next heading of the same or higher level.
    Returns None if the heading isn't on the page."""
    fence, collected, inside, level = FenceTracker(), [], False, 0
    for line in markdown.split("\n"):
        match = None if fence.is_code(line) else re.match(r"^(#+) (.*)", line)
        if match:
            if inside and len(match.group(1)) <= level:
                break
            if match.group(2).strip() == heading.strip():
                inside, level = True, len(match.group(1))
                continue
        if inside:
            collected.append(line)
    return "\n".join(collected) if inside else None


def main():
    base_url = site_base_url()
    pages = {}  # url -> page body, so each page is downloaded once
    rows, failures = [], []
    group_of = {question_id: group for group, ids in GROUPS.items() for question_id in ids}
    unknown_ids = sorted(set(group_of) - {item[0] for item in SEED})
    if unknown_ids:
        sys.exit(f"GROUPS names ids that aren't in SEED: {', '.join(unknown_ids)}")
    for question_id, question, doc_path, heading, style, evidence in SEED:
        url = page_url(base_url, doc_path)
        problem = None
        if url not in pages:
            try:
                pages[url] = split_front_matter(http_get(md_url_for(url)))[1]
            except Exception as error:
                pages[url] = None
                print(f"  could not fetch {url}: {error}", file=sys.stderr)
        body = pages[url]
        if body is None:
            problem = "page missing"
        else:
            section = section_text(body, heading)
            if section is None:
                problem = "heading missing"
            elif evidence.lower() not in section.lower():
                problem = f"evidence '{evidence}' not in section"
            elif body.lower().count(evidence.lower()) > section.lower().count(evidence.lower()):
                problem = f"evidence '{evidence}' also appears outside the section"
        if problem:
            failures.append((question_id, problem))
        rows.append({
            "id": question_id,
            "question": question,
            "expected_url": url,
            "expected_section": heading,
            "expected_anchor": url + "#" + slugify(heading),
            "style": style,
            "area": AREAS[question_id[0]],
            "evidence": evidence,
            "origin": "seed",
            "group": group_of.get(question_id, ""),
            "verified": problem is None,
        })

    with open(HERE / "eval_set.jsonl", "w") as jsonl_file:
        for row in rows:
            jsonl_file.write(json.dumps(row) + "\n")
    with open(HERE / "eval_set.csv", "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} items, {len(rows) - len(failures)} verified "
          f"against {len(pages)} published pages")
    for question_id, problem in failures:
        print(f"  FAIL {question_id}: {problem}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
