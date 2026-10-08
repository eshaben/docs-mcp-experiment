"""Heading-based chunking of cleaned Markdown.

Strategy:
  - The H1 is the page title (or `fallback_title`, from front matter, if there's no H1). Text
    before the first H2 is the page's intro chunk. A page with several H1s holds several guides;
    each H1 titles the chunks below it.
  - Every H2 section is a chunk. If it's longer than `max_tokens`, it is split at its H3s
    (the H2's own intro text becomes one chunk, each H3 another).
  - Anything still too long is packed paragraph by paragraph into parts. Fenced code blocks are
    never split, and bold label lines (tab names, admonition titles) stay with what follows.
Each chunk records its heading path (Page > H2 > H3) and the anchor of its deepest heading.
"""
import re
import unicodedata
from dataclasses import dataclass, field
from typing import NamedTuple

from .mdlines import FenceTracker
from .mkdocs_clean import BLOCK_END_LINE, LABEL_LINE, remove_block_markers

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
# Bump when a change to this file or to mkdocs_clean.py changes what the chunks contain, so the
# next ingest re-chunks every page. (Changes to the chunking settings are detected on their own.)
CHUNKER_VERSION = "3"


class Settings(NamedTuple):
    max_tokens: int
    min_tokens: int
    split_tabs: bool


class Heading(NamedTuple):
    line_index: int
    level: int
    text: str


@dataclass
class Chunk:
    heading_path: list
    anchor: str
    text: str
    part: int = 0
    tokens: int = field(init=False)

    def __post_init__(self):
        self.tokens = estimate_tokens(self.text)


def estimate_tokens(text):
    """Characters ÷ 4: a rough estimate, used only for sizing chunks and comparing runs, where
    consistency matters more than accuracy. It fits English prose; code usually needs more
    tokens per character, so code-heavy chunks are bigger than this says. Embedding limits
    need the embedding model's own tokenizer, not this."""
    return max(1, len(text) // 4)


def slugify(heading):
    """Python-Markdown `toc` default slug: strip markup, lowercase, drop punctuation, dash spaces.
    Underscores inside words (`eth_call`) and everything inside code spans are kept."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    pieces = re.split(r"(`[^`]*`)", text)
    text = "".join(piece[1:-1] if piece.startswith("`") else _strip_emphasis(piece)
                   for piece in pieces)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


def _strip_emphasis(text):
    """Remove `*` and emphasis underscores (`_word_`), keeping underscores inside words."""
    text = text.replace("*", "")
    return re.sub(r"(?<![A-Za-z0-9])_+|_+(?![A-Za-z0-9])", "", text)


def plain_heading(heading):
    return re.sub(r"`([^`]*)`", r"\1", heading).strip()


def chunk_page(markdown, fallback_title=None, max_tokens=600, min_tokens=100, split_tabs=False):
    """Split cleaned Markdown into chunks. With `split_tabs`, a section too long for one chunk is
    split between its content tabs before it's packed, each tab gets its own heading path entry,
    and a part that starts partway into a tab or admonition repeats its label."""
    if not split_tabs:
        markdown = remove_block_markers(markdown)
    lines = markdown.split("\n")
    headings = _find_headings(lines)
    anchors = _anchors(headings)

    chunks = []
    settings = Settings(max_tokens, min_tokens, split_tabs)
    h1s = [heading for heading in headings if heading.level == 1]
    if not h1s:
        _split(lines, headings, anchors, 0, len(lines), [fallback_title or ""], "", 2, settings,
               chunks, force=True)
        return chunks
    # Some pages hold several guides, each under its own H1. Each H1 titles the chunks below it.
    guide_ends = [h1.line_index for h1 in h1s[1:]] + [len(lines)]
    for guide_number, (h1, guide_end) in enumerate(zip(h1s, guide_ends)):
        anchor = "" if guide_number == 0 else anchors[h1.line_index]
        _split(lines, headings, anchors, h1.line_index + 1, guide_end, [plain_heading(h1.text)],
               anchor, 2, settings, chunks, force=True)
    return chunks


def _find_headings(lines):
    """Every ATX heading outside fenced code, as a Heading."""
    fence, found = FenceTracker(), []
    for line_index, line in enumerate(lines):
        if fence.is_code(line):
            continue
        heading_match = HEADING.match(line)
        if heading_match:
            found.append(Heading(line_index, len(heading_match.group(1)), heading_match.group(2)))
    return found


def _anchors(headings):
    """Anchor per heading line, with MkDocs-style _1, _2 suffixes for duplicates."""
    times_seen, anchor_by_line = {}, {}
    for heading in headings:
        slug = slugify(heading.text)
        earlier_count = times_seen.get(slug, 0)
        times_seen[slug] = earlier_count + 1
        anchor_by_line[heading.line_index] = slug if earlier_count == 0 else f"{slug}_{earlier_count}"
    return anchor_by_line


def _tokens(text):
    """Token estimate of the text a reader will see (block markers don't count)."""
    return estimate_tokens(remove_block_markers(text))


def _split(lines, headings, anchors, start, end, path, anchor, level, settings, chunks, force=False):
    """Emit chunks for lines[start:end], splitting at headings of `level` if needed."""
    text = "\n".join(lines[start:end]).strip()
    if not remove_block_markers(text).strip():
        return
    if not force and (_tokens(text) <= settings.max_tokens or level > 3):
        _emit(text, path, anchor, settings, chunks)
        return
    split_headings = [heading for heading in headings
                      if start <= heading.line_index < end and heading.level == level]
    if not split_headings:
        if level < 3:
            _split(lines, headings, anchors, start, end, path, anchor, level + 1, settings, chunks)
        else:
            _emit(text, path, anchor, settings, chunks)
        return
    intro = "\n".join(lines[start:split_headings[0].line_index]).strip()
    if intro and not _only_headings(intro):
        _emit(intro, path, anchor, settings, chunks)
    section_ends = [heading.line_index for heading in split_headings[1:]] + [end]
    for heading, section_end in zip(split_headings, section_ends):
        _split(lines, headings, anchors, heading.line_index, section_end,
               path + [plain_heading(heading.text)], anchors[heading.line_index],
               level + 1, settings, chunks)


def _only_headings(text):
    return all(HEADING.match(line) or BLOCK_END_LINE.match(line) or not line.strip()
               for line in text.split("\n"))


def _emit(text, path, anchor, settings, chunks):
    """Emit text as one chunk, or split it into parts of at most max_tokens: first between
    content tabs (with `split_tabs`), then by packing blocks."""
    if _tokens(text) <= settings.max_tokens:
        chunks.append(Chunk(list(path), anchor, remove_block_markers(text).strip()))
        return
    blocks = _annotate(_blocks(text))
    units = _tab_units(blocks, settings.min_tokens) if settings.split_tabs else [(None, blocks)]
    part_numbers = {}
    for tab_label, unit_blocks in units:
        unit_path = path + [plain_heading(tab_label.strip().strip("*"))] if tab_label else list(path)
        for part_text in _pack(unit_blocks, settings):
            part_number = part_numbers.get(tuple(unit_path), 0)
            part_numbers[tuple(unit_path)] = part_number + 1
            chunks.append(Chunk(unit_path, anchor, part_text, part_number))


def _pack(blocks, settings):
    """Pack blocks into parts of at most max_tokens. A part is only closed once it has
    min_tokens, so a lead-in sentence stays with the code it introduces (the part may then run
    over max_tokens); a short tail is folded into the previous part. With `split_tabs`, a part
    that starts inside a tab or admonition begins with its label, marked "(continued)"."""
    max_tokens, min_tokens, repeat_labels = settings
    parts, current_part, repeated_count = [], [], 0
    for block in blocks:
        current_text = "\n\n".join(current_part)
        if current_part and estimate_tokens(current_text) >= min_tokens \
                and estimate_tokens(current_text + "\n\n" + block.text) > max_tokens:
            parts.append(current_text)
            current_part = []
        if not current_part and parts and repeat_labels and block.open_labels:
            current_part = [_continued(label) for label in block.open_labels]
            repeated_count = len(current_part)
        elif not current_part:
            repeated_count = 0
        current_part.append(block.text)
    if current_part:
        if parts and estimate_tokens("\n\n".join(current_part)) < min_tokens:
            # Folded into the previous part, where the repeated labels aren't needed.
            parts[-1] += "\n\n" + "\n\n".join(current_part[repeated_count:])
        else:
            parts.append("\n\n".join(current_part))
    return parts


def _continued(label):
    return label.strip()[:-2] + " (continued)**"


def _blocks(text):
    """Split into paragraph-level blocks: blank-line separated, code fences kept whole, and
    label lines (bold-only) glued to the block that follows them. Block markers stay as their
    own blocks."""
    blocks, current_block, fence = [], [], FenceTracker()
    for line in text.split("\n"):
        in_code = fence.is_code(line)
        if not in_code and not line.strip():
            if current_block:
                blocks.append("\n".join(current_block))
                current_block = []
            continue
        current_block.append(line)
    if current_block:
        blocks.append("\n".join(current_block))

    merged = []
    for block in blocks:
        # Check the last line, so a stack of labels (a tab label, then a note title) stays glued.
        previous_last_line = merged[-1].rsplit("\n", 1)[-1] if merged else ""
        if merged and not BLOCK_END_LINE.match(block) \
                and (LABEL_LINE.match(previous_last_line) or HEADING.match(previous_last_line)):
            merged[-1] = merged[-1] + "\n\n" + block
        else:
            merged.append(block)
    return merged


class Block(NamedTuple):
    text: str
    open_labels: list    # labels of tabs/admonitions still open where this block starts
    opened_labels: list  # labels of tabs/admonitions that this block opens


def _annotate(blocks):
    """Drop the block markers, recording for each remaining block which labels are open.

    A label counts as a tab or admonition only if a marker later closes it. Authors' own
    bold-only lines (like `**Parameters**:`) look the same but have no marker, so they're ignored.
    """
    # Pass 1: match each marker to the nearest open label with the same text.
    open_stack, matched = [], set()  # stack of (block_index, label); matched (block_index, label)
    for block_index, block in enumerate(blocks):
        marker = BLOCK_END_LINE.match(block)
        if marker:
            closed_label = marker.group(1).strip()
            for stack_index in range(len(open_stack) - 1, -1, -1):
                if open_stack[stack_index][1] == closed_label:
                    matched.add(open_stack[stack_index])
                    del open_stack[stack_index:]
                    break
            continue
        open_stack.extend((block_index, label) for label in _label_lines(block))
    # Pass 2: walk the blocks, tracking which matched labels are open.
    annotated, open_labels = [], []
    for block_index, block in enumerate(blocks):
        marker = BLOCK_END_LINE.match(block)
        if marker:
            closed_label = marker.group(1).strip()
            if closed_label in open_labels:
                del open_labels[len(open_labels) - 1 - open_labels[::-1].index(closed_label):]
            continue
        opened = [label for label in _label_lines(block) if (block_index, label) in matched]
        annotated.append(Block(block, list(open_labels), opened))
        open_labels.extend(opened)
    return annotated


def _label_lines(block):
    fence, labels = FenceTracker(), []
    for line in block.split("\n"):
        if not fence.is_code(line) and LABEL_LINE.match(line):
            labels.append(line.strip())
    return labels


def _tab_units(blocks, min_tokens):
    """Group blocks into units: one per top-level content tab, and one per run of blocks outside
    any tab. A short run outside tabs (such as "Choose your SDK:") joins the unit after it."""
    units = []  # [tab_label or None, blocks]
    for block in blocks:
        outermost = block.open_labels[0] if block.open_labels else \
            (block.opened_labels[0] if block.opened_labels else None)
        tab_label = outermost if outermost and outermost.startswith("**Tab:") else None
        starts_tab = not block.open_labels and tab_label is not None
        if units and units[-1][0] == tab_label and not starts_tab:
            units[-1][1].append(block)
        else:
            units.append([tab_label, [block]])
    merged = []
    for unit_index, (tab_label, unit_blocks) in enumerate(units):
        unit_text = "\n\n".join(block.text for block in unit_blocks)
        if tab_label is None and estimate_tokens(unit_text) < min_tokens and len(units) > 1:
            if unit_index + 1 < len(units):
                units[unit_index + 1][1][:0] = unit_blocks
            else:
                merged[-1][1].extend(unit_blocks)
            continue
        merged.append([tab_label, unit_blocks])
    return merged
