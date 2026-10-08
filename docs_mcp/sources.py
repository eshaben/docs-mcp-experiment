"""Fetch a docs site's page list from llms.txt and each page's resolved Markdown."""
import concurrent.futures as cf
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

# Define a user agent to avoid any potential bot filters or failures
USER_AGENT = "docs-mcp-experiment/0.1 (+https://github.com/eshaben/docs-mcp-experiment)"
LINK_RE = re.compile(r"^\s*-\s*\[([^\]]+)\]\((\S+?)\)")


@dataclass
class Page:
    url: str
    md_url: str
    raw: str
    front_matter: dict = field(default_factory=dict)
    body: str = ""


def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def parse_llms_txt(text):
    """Return [(title, url)] for every `- [Title](url)` list item in llms.txt.

    Other lines, such as headings or bare URLs in the intro text, are ignored.
    """
    links = []
    for line in text.splitlines():
        match = LINK_RE.match(line)
        if match:
            links.append((match.group(1).strip(), match.group(2).strip()))
    return links


def md_url_for(page_url):
    """Where to fetch a page's Markdown, or None if the link isn't a page we can handle.

    - Links that already point at a `.md` file are used as-is.
    - Links to any other file type (`.html`, `.pdf`, `.jsonl`, ...) return None so the caller
      can flag them; guessing a Markdown URL for those would just produce 404s.
    - Everything else follows the llms.txt convention: page URL (no trailing slash) + `.md`.
    """
    path = urllib.parse.urlsplit(page_url).path
    ext = file_extension(path)
    if ext == ".md":
        return page_url
    if ext:
        return None
    return page_url.rstrip("/") + ".md"


def file_extension(path):
    """Extension of the last path segment ('' for directory-style paths like `/a/b/`)."""
    if path.endswith("/"):
        return ""
    last = path.rsplit("/", 1)[-1]
    return "." + last.rsplit(".", 1)[1].lower() if "." in last else ""


def split_front_matter(raw):
    """Split a `---`-delimited front matter block (flat `key: value` lines) from the body."""
    if not raw.startswith("---\n"):
        return {}, raw
    end = raw.find("\n---\n", 4)
    if end == -1:
        return {}, raw
    front_matter = {}
    for line in raw[4:end].splitlines():
        key, colon, value = line.partition(":")
        if colon and key.strip():
            front_matter[key.strip()] = value.strip().strip("'\"")
    return front_matter, raw[end + 5:]


def fetch_page(url):
    md_url = md_url_for(url)
    raw = http_get(md_url)
    front_matter, body = split_front_matter(raw)
    return Page(url=front_matter.get("url") or url, md_url=md_url, raw=raw, front_matter=front_matter, body=body)


def fetch_pages(urls, workers=8):
    """Fetch pages concurrently. Returns (pages, failures) where failures is [(url, error)]."""
    pages, failures = [], []
    with cf.ThreadPoolExecutor(workers) as executor:
        futures = {executor.submit(fetch_page, url): url for url in urls}
        for future in cf.as_completed(futures):
            try:
                pages.append(future.result())
            except Exception as error:  # report and keep going
                failures.append((futures[future], str(error)))
    return pages, failures
