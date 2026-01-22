"""Inline markdown fixes for backticks and references.

Handles escaping triple backticks in inline text and wrapping dunder references
in backticks.
"""

import re
from re import Match


def fix_dunder_references(line: str) -> str:
    """Wrap __name__.py in backticks within headings."""
    if line.startswith("#"):
        # Negative lookbehind/lookahead to avoid double-wrapping
        line = re.sub(r"(?<!`)(__[A-Za-z0-9_]+__(\.py)?)(?!`)", r"`\1`", line)
    return line


def find_inline_code_spans(line: str) -> list[tuple[int, int]]:
    """Find all inline code spans according to CommonMark specification.

    Returns list of (start, end) tuples marking protected regions.

    DESIGN DECISION (2026-01-06):
    Only protects spans delimited by 1-2 backticks (typical inline code).
    Spans with 3+ backtick delimiters are intentionally IGNORED.

    Rationale:
    - Single/double backtick spans like `code` and ``code`` are legitimate
      inline code that should be preserved
    - Triple+ backtick sequences like ```python are fence markers that should
      be escaped by escape_inline_backticks() to prevent them from being
      interpreted as block delimiters
    - While ```...``` is technically valid CommonMark inline code, in practice
      these sequences are almost always intended as fence markers in markdown
      about markdown, so we treat them as escapable rather than protected

    CommonMark inline code span rules:
    - A backtick string is a run of one or more backtick characters
    - An opening delimiter is a backtick string not followed by another backtick
    - A closing delimiter is a backtick string not preceded by another backtick
    - A code span begins with opening delimiter and ends with closing delimiter
      of equal length
    - Backtick strings are atomic and cannot be split
    """
    spans = []
    i = 0

    while i < len(line):
        if line[i] != "`":
            i += 1
            continue

        # Count the opening backtick string
        start_pos = i
        while i < len(line) and line[i] == "`":
            i += 1
        delimiter_len = i - start_pos

        # Only protect spans with 1-2 backtick delimiters
        # (3+ backticks are likely fence markers, not inline code)
        if delimiter_len > 2:
            # Skip this backtick string and continue
            continue

        # Search for closing backtick string of EXACT same length
        search_pos = i
        found = False

        while search_pos < len(line):
            if line[search_pos] == "`":
                # Count this backtick string
                run_start = search_pos
                while search_pos < len(line) and line[search_pos] == "`":
                    search_pos += 1
                run_len = search_pos - run_start

                # Check if this matches our opening delimiter length
                if run_len == delimiter_len:
                    # Found matching closing delimiter
                    spans.append((start_pos, search_pos))
                    i = search_pos
                    found = True
                    break
                # If not a match, continue searching from after this run
            else:
                search_pos += 1

        # If no closing delimiter found, the opening backticks are literal text
        # Skip the entire backtick string (CommonMark: backtick strings are atomic)
        if not found:
            i = start_pos + delimiter_len

    return spans


def escape_inline_backticks(lines: list[str]) -> list[str]:
    """Escape triple backticks when they appear inline in text.

    Wraps ```language and ``` with double backticks (`` ``` ``) to prevent
    them from being interpreted as code fence markers by markdown parsers.

    - Skips lines that start with ``` (real code fences)
    - Skips content inside code blocks
    - Protects content inside inline code spans (`` `...` `` and ``` ``...`` ```)
    - Idempotent: won't re-escape already escaped backticks
    """
    result = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        # Track code block state
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            result.append(line)
            continue

        # Skip lines inside code blocks
        if in_code_block:
            result.append(line)
            continue

        # Find all inline code spans to protect
        spans = find_inline_code_spans(line)

        if not spans:
            # No inline code spans - apply escape pattern to whole line
            pattern = r"`` (`{3,}\w*) ``|(`{3,})(\w*)"

            def replacer(m: Match[str]) -> str:
                if m.group(1):  # Already escaped
                    return m.group(0)
                # Unescaped - wrap it
                return f"`` {m.group(2)}{m.group(3)} ``"

            escaped_line = re.sub(pattern, replacer, line)
            result.append(escaped_line)
        else:
            # Process only text outside protected spans
            escaped_parts = []
            pos = 0

            for start, end in spans:
                # Process gap before this span
                if pos < start:
                    gap = line[pos:start]
                    pattern = r"`` (`{3,}\w*) ``|(`{3,})(\w*)"

                    def replacer(m: Match[str]) -> str:
                        if m.group(1):
                            return m.group(0)
                        return f"`` {m.group(2)}{m.group(3)} ``"

                    gap_escaped = re.sub(pattern, replacer, gap)
                    escaped_parts.append(gap_escaped)

                # Add protected span unchanged
                escaped_parts.append(line[start:end])
                pos = end

            # Process remaining text after last span
            if pos < len(line):
                gap = line[pos:]
                pattern = r"`` (`{3,}\w*) ``|(`{3,})(\w*)"

                def replacer(m: Match[str]) -> str:
                    if m.group(1):
                        return m.group(0)
                    return f"`` {m.group(2)}{m.group(3)} ``"

                gap_escaped = re.sub(pattern, replacer, gap)
                escaped_parts.append(gap_escaped)

            escaped_line = "".join(escaped_parts)
            result.append(escaped_line)

    return result
