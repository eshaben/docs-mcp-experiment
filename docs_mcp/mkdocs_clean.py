"""Turn MkDocs Material Markdown into plain Markdown suitable for chunking and search.

Handles:
  - termynal terminal widgets (<div ... termynal>) -> fenced ```text blocks, `$ ` on input lines
  - admonitions (`!!! note "Title"`, collapsible `??? tip`, `???+`) -> bold label + dedented body
  - content tabs (`=== "Tab name"`) -> `**Tab: Tab name**` + dedented body, so the label stays
    attached to its content
  - after each tab or admonition body, a `%%end-block <label>%%` marker line for the chunker
  - leftover HTML tags (whitelisted names only, so `Vec<T>` and `<your-address>` survive),
    HTML comments, whole <svg> elements, and icon shortcodes like `:octicons-arrow-right-24:`
Fenced code is never modified, and inline code spans are left as-is.
"""
import html
import re

from .mdlines import FenceTracker, indent_of

TERMYNAL_OPEN = re.compile(r"^(\s*)<div\b[^>]*\btermynal\b[^>]*>")
TERMYNAL_INPUT = re.compile(r'<span[^>]*data-ty="input"')
ADMONITION = re.compile(r'^(\s*)(!!!|\?\?\?\+?)\s*([\w-]+)((?:\s+[\w-]+)*)\s*(?:"([^"]*)")?\s*$')
TAB = re.compile(r'^(\s*)===\+?\s+"([^"]*)"\s*$')
HTML_TAGS = (
    "a|abbr|b|br|button|center|code|dd|del|details|div|dl|dt|em|figcaption|figure|form|"
    "h[1-6]|hr|i|iframe|img|input|ins|kbd|label|li|mark|ol|option|p|pre|s|section|select|"
    "small|source|span|strong|sub|summary|sup|table|tbody|td|textarea|tfoot|th|thead|tr|u|ul|video"
)
HTML_TAG = re.compile(rf"</?(?:{HTML_TAGS})(?:\s[^<>]*)?/?>", re.IGNORECASE)
HTML_COMMENT = re.compile(r"<!--.*?-->")
# An SVG's contents are drawing instructions, never text, so the whole element is removed.
SVG_ELEMENT = re.compile(r"<svg\b.*?</svg>", re.IGNORECASE)
# Elements removed with everything inside them, even across lines: (opening, closing) markers.
DROPPED_ELEMENTS = (("<!--", "-->"), ("<svg", "</svg>"))
ICON_SHORTCODE = re.compile(r":(?:octicons|material|fontawesome|simple|custom)-[\w-]+:")
INLINE_CODE = re.compile(r"(`+)(.+?)\1")

# Bold-only lines produced here (tab labels, admonition titles) act as mini headings; the chunker
# keeps them glued to the block that follows.
LABEL_LINE = re.compile(r"^\s*\*\*[^*]+\*\*:?\s*$")

# After the body of each tab or admonition, a marker line names the label it closes, so the
# chunker knows where the tab ends once its body is un-indented. The chunker removes these lines;
# anything else that shows cleaned text should call remove_block_markers.
BLOCK_END = "%%end-block {label}%%"
BLOCK_END_LINE = re.compile(r"^[ \t]*%%end-block (.*)%%[ \t]*$")
_BLOCK_END_LINES = re.compile(r"(?m)^[ \t]*%%end-block .*%%[ \t]*(?:\n|$)")


def remove_block_markers(text):
    return collapse_blank_lines(_BLOCK_END_LINES.sub("", text))


def clean(body):
    lines = body.split("\n")
    lines = convert_termynal(lines)
    lines = convert_blocks(lines)
    lines = strip_html(lines)
    return collapse_blank_lines("\n".join(lines)).strip() + "\n"


def convert_termynal(lines):
    """Replace each termynal widget with a ```text block: `$ command` lines plus program output."""
    cleaned_lines, fence, line_index = [], FenceTracker(), 0
    while line_index < len(lines):
        line = lines[line_index]
        termynal_match = None if fence.is_code(line) else TERMYNAL_OPEN.match(line)
        if not termynal_match:
            cleaned_lines.append(line)
            line_index += 1
            continue
        indent = termynal_match.group(1)
        widget_lines = [line[termynal_match.end():]]
        while "</div>" not in widget_lines[-1] and line_index + 1 < len(lines):
            line_index += 1
            widget_lines.append(lines[line_index])
        line_index += 1
        widget_lines[-1] = widget_lines[-1].split("</div>")[0]
        cleaned_lines.append(f"{indent}```text")
        markup_indent = None  # indentation of the <span> markup itself, not of the output
        for widget_line in widget_lines:
            if widget_line.lstrip().startswith("<span"):
                markup_indent = indent_of(widget_line)
            text = html.unescape(HTML_TAG.sub("", widget_line)).rstrip()
            if not text.strip():
                continue
            if TERMYNAL_INPUT.search(widget_line):
                cleaned_lines.append(f"{indent}$ {text.strip()}")
            else:
                dedent_by = min(markup_indent or 0, indent_of(text))
                cleaned_lines.append(indent + text[dedent_by:])
        cleaned_lines.append(f"{indent}```")
    return cleaned_lines


def convert_blocks(lines, parent_tab=None):
    """Rewrite admonitions and content tabs (recursively, since they nest). A nested tab's
    label includes its parent tab, e.g. `**Tab: Polkadot Hub TestNet › Parity**`."""
    converted_lines, fence, line_index = [], FenceTracker(), 0
    while line_index < len(lines):
        line = lines[line_index]
        if fence.is_code(line):
            converted_lines.append(line)
            line_index += 1
            continue
        admonition_match, tab_match = ADMONITION.match(line), TAB.match(line)
        if not (admonition_match or tab_match):
            converted_lines.append(line)
            line_index += 1
            continue
        indent = (admonition_match or tab_match).group(1)
        tab_name = None
        if tab_match:
            tab_name = tab_match.group(2).strip()
            if parent_tab:
                tab_name = f"{parent_tab} › {tab_name}"
            label = f"**Tab: {tab_name}**"
        else:
            admonition_type = admonition_match.group(3).capitalize()
            title = (admonition_match.group(5) or "").strip()
            label = f"**{admonition_type}: {title}**" if title else f"**{admonition_type}:**"
        # The body is every following line that's blank or indented 4 more spaces than the marker.
        body_end = line_index + 1
        while body_end < len(lines) and (
            not lines[body_end].strip() or indent_of(lines[body_end]) >= len(indent) + 4
        ):
            body_end += 1
        while body_end > line_index + 1 and not lines[body_end - 1].strip():
            body_end -= 1  # leave trailing blanks outside the block
        body = [
            indent + body_line[len(indent) + 4:] if body_line.strip() else ""
            for body_line in lines[line_index + 1:body_end]
        ]
        converted_lines.append(indent + label)
        converted_lines.append("")
        converted_lines.extend(convert_blocks(body, tab_name or parent_tab))
        converted_lines.extend(["", indent + BLOCK_END.format(label=label), ""])
        line_index = body_end
    return converted_lines


def strip_html(lines):
    """Remove HTML tags, HTML comments, SVG images and icon shortcodes from prose. Fenced code
    and inline code spans are left untouched."""
    cleaned_lines, fence = [], FenceTracker()
    drop_until = None  # closing marker of a comment or SVG that spans lines, while inside one
    for line in lines:
        if fence.is_code(line):
            cleaned_lines.append(line)
            continue
        if drop_until:
            if drop_until not in line:
                continue
            line, drop_until = line.split(drop_until, 1)[1], None
        pieces, prose_start = [], 0
        for code_match in INLINE_CODE.finditer(line):
            pieces.append(_strip_prose(line[prose_start:code_match.start()]))
            pieces.append(code_match.group(0))
            prose_start = code_match.end()
        remainder = line[prose_start:]
        for opener, closer in DROPPED_ELEMENTS:
            if opener in remainder and closer not in remainder.split(opener, 1)[1]:
                remainder, drop_until = remainder.split(opener, 1)[0], closer
                break
        pieces.append(_strip_prose(remainder))
        cleaned_line = "".join(pieces)
        # A line that was only markup becomes a blank line, not a line of leftover spaces.
        cleaned_lines.append("" if not cleaned_line.strip() and line.strip() else cleaned_line.rstrip())
    return cleaned_lines


def _strip_prose(prose):
    prose = HTML_COMMENT.sub("", prose)
    prose = SVG_ELEMENT.sub("", prose)
    prose = HTML_TAG.sub("", prose)
    prose = ICON_SHORTCODE.sub("", prose)
    return prose


def collapse_blank_lines(text):
    return re.sub(r"\n{3,}", "\n\n", text)
