"""Line-level Markdown helpers shared by the cleaner and the chunker."""
import re

FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")


class FenceTracker:
    """Tracks whether we're inside a fenced code block.

    Call `is_code(line)` on each line of a page, in order. It returns True if the line
    is code, counting the opening and closing ``` lines as code too.
    """

    def __init__(self):
        self.open_fence = None  # (char, length) of the open fence, or None outside code

    def is_code(self, line):
        fence_match = FENCE_RE.match(line)
        if self.open_fence is None:
            if fence_match:
                fence = fence_match.group(2)
                self.open_fence = (fence[0], len(fence))
                return True
            return False
        if fence_match:
            fence = fence_match.group(2)
            open_char, open_length = self.open_fence
            nothing_after_fence = not line[fence_match.end():].strip()
            if fence[0] == open_char and len(fence) >= open_length and nothing_after_fence:
                self.open_fence = None
        return True


def indent_of(line):
    """Number of leading spaces on `line`."""
    return len(line) - len(line.lstrip(" "))
