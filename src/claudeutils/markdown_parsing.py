"""Segment parsing for markdown processing.

Splits markdown documents into processable and protected segments (code blocks,
YAML prologs, etc.) to allow targeted fixes without corrupting protected
content.
"""

import re
from collections.abc import Callable

from pydantic import BaseModel


class Segment(BaseModel):
    """A segment of markdown document (processable or protected)."""

    processable: bool
    language: str | None
    lines: list[str]
    start_line: int


def flatten_segments(segments: list[Segment]) -> list[str]:
    """Flatten segments back into a list of lines."""
    result: list[str] = []
    for segment in segments:
        result.extend(segment.lines)
    return result


def apply_fix_to_segments(
    segments: list[Segment],
    fix_fn: Callable[[list[str]], list[str]],
) -> list[Segment]:
    """Apply a fix function to processable segments only.

    Args:
        segments: List of segments to process
        fix_fn: Function that takes list[str] and returns list[str]

    Returns:
        New list of segments with fix applied to processable ones only

    Note: Protected segments (processable=False) are returned unchanged,
    regardless of their language or content. This includes bare fences,
    code blocks, YAML prologs, and markdown blocks.
    """
    result = []
    for segment in segments:
        if segment.processable:
            fixed_lines = fix_fn(segment.lines)
            result.append(
                Segment(
                    processable=segment.processable,
                    language=segment.language,
                    lines=fixed_lines,
                    start_line=segment.start_line,
                )
            )
        else:
            # Protected segment - skip this fix
            result.append(segment)
    return result


def parse_segments(lines: list[str]) -> list[Segment]:
    """Parse document into segments (processable vs protected)."""
    if not lines:
        return []

    segments: list[Segment] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check if this is a YAML prolog section
        if stripped == "---":
            # Look ahead to see if this is a YAML prolog
            # Must have closing ---, no blank lines INSIDE, and at least one key: value
            # The next line after opening --- must NOT be blank (no intervening blank line)
            prolog_lines = [line]
            j = i + 1
            has_key_value = False
            has_blank_line_inside = False
            found_closing = False
            is_valid_prolog = False

            # Check if next line exists and is not blank (immediate content required)
            if j < len(lines) and lines[j].strip():
                # Has content immediately after opening ---
                while j < len(lines):
                    current_line = lines[j]
                    current_stripped = current_line.strip()

                    # Check for blank line inside the prolog
                    if not current_stripped:
                        has_blank_line_inside = True
                        break

                    # Check for closing ---
                    if current_stripped == "---":
                        prolog_lines.append(current_line)
                        found_closing = True
                        j += 1
                        break

                    # Check for key: value pattern
                    # Accepts: "key: value", "key:", "key_name:", "key-name:", "key123:"
                    # Pattern allows underscores, hyphens, and digits except as first character
                    if re.match(r"^[a-zA-Z_][\w-]*:", current_stripped):
                        has_key_value = True

                    prolog_lines.append(current_line)
                    j += 1

                # Is this a valid YAML prolog?
                if found_closing and has_key_value and not has_blank_line_inside:
                    is_valid_prolog = True

            if is_valid_prolog:
                # Valid YAML prolog section
                segments.append(
                    Segment(
                        processable=False,
                        language="yaml-prolog",
                        lines=prolog_lines,
                        start_line=i,
                    )
                )
                i = j
                continue
            # Not a valid prolog, fall through to collect as plain text

        # Check if this is a fence opening
        if stripped.startswith("```"):
            # Count opening backticks
            backtick_count = 0
            for char in stripped:
                if char == "`":
                    backtick_count += 1
                else:
                    break

            # Extract language
            language = stripped[backtick_count:].strip() or None
            fence_lines = [line]
            i += 1

            # Find closing fence, handling nested blocks
            # Use a stack to track nested fence opening (language tags)
            fence_stack: list[tuple[int, str | None]] = [(backtick_count, language)]

            while i < len(lines) and fence_stack:
                current_stripped = lines[i].strip()
                fence_lines.append(lines[i])

                # Count backticks if this is a fence line
                if current_stripped.startswith("```"):
                    backtick_in_line = 0
                    for char in current_stripped:
                        if char == "`":
                            backtick_in_line += 1
                        else:
                            break

                    # Extract language
                    language_in_line = (
                        current_stripped[backtick_in_line:].strip() or None
                    )

                    # Check if this is a fence with matching backtick count
                    if backtick_in_line == backtick_count:
                        if language_in_line:
                            # Fence with language - this is an opening
                            fence_stack.append((backtick_in_line, language_in_line))
                        else:
                            # Bare fence - closes the most recent opening
                            fence_stack.pop()
                            if not fence_stack:
                                # This closes our main fence
                                i += 1
                                break
                i += 1

            # Extract the original language from the first fence line
            open_lang = (
                stripped[backtick_count:].strip() or None
            )  # Ensure we use original
            # Markdown blocks are processable, others are protected
            processable = open_lang == "markdown"

            # Recursive parsing for markdown blocks
            if processable and len(fence_lines) > 2:
                # Extract inner content (exclude opening and closing fence lines)
                inner_content = fence_lines[1:-1]
                inner_start_line = (i - len(fence_lines)) + 1

                # Recursively parse inner content
                inner_segments = parse_segments(inner_content)

                # Adjust start_line for each nested segment
                for seg in inner_segments:
                    seg.start_line += inner_start_line

                # Add opening fence as segment
                segments.append(
                    Segment(
                        processable=True,
                        language=open_lang,
                        lines=[fence_lines[0]],
                        start_line=i - len(fence_lines),
                    )
                )

                # Add recursively parsed segments
                segments.extend(inner_segments)

                # Add closing fence as segment
                segments.append(
                    Segment(
                        processable=True,
                        language=open_lang,
                        lines=[fence_lines[-1]],
                        start_line=i - 1,
                    )
                )
            else:
                # Non-markdown blocks or empty markdown blocks - no recursion
                segments.append(
                    Segment(
                        processable=processable,
                        language=open_lang,
                        lines=fence_lines,
                        start_line=i - len(fence_lines),
                    )
                )
        else:
            # Collect plain text until next fence or potential YAML prolog
            text_lines: list[str] = []
            start_i = i
            while i < len(lines):
                stripped = lines[i].strip()
                # Break on fence markers (but collect at least one line first)
                if text_lines and stripped.startswith("```"):
                    break
                # Only break on "---" if it could be a valid YAML prolog
                # (has non-blank content immediately after) and we've collected at least one line
                if (
                    text_lines
                    and stripped == "---"
                    and i + 1 < len(lines)
                    and lines[i + 1].strip()
                ):
                    break
                text_lines.append(lines[i])
                i += 1

            if text_lines:
                segments.append(
                    Segment(
                        processable=True,
                        language=None,
                        lines=text_lines,
                        start_line=start_i,
                    )
                )

    return segments


def fix_dunder_references(line: str) -> str:
    """Wrap __name__.py in backticks within headings."""
    if line.startswith("#"):
        # Negative lookbehind/lookahead to avoid double-wrapping
        line = re.sub(r"(?<!`)(__[A-Za-z0-9_]+__(\.py)?)(?!`)", r"`\1`", line)
    return line
