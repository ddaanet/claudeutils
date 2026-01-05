r"""Preprocessor for Claude markdown-like output.

This module fixes structural issues in Claude-generated markdown before
dprint formatting. It handles patterns that Claude commonly produces but
aren't valid markdown, such as:

- Consecutive lines with emoji/symbol prefixes needing list formatting
- Code blocks with improper fence nesting
- Metadata labels followed by lists needing indentation
- Other structural patterns from Claude output

Processing Pipeline:
    Claude output → markdown.py fixes → dprint formatting

Future Direction:
    This should eventually evolve into a dprint plugin for better integration.

Usage:
    # Process single file
    from pathlib import Path
    from claudeutils.markdown import process_file

    filepath = Path("output.md")
    modified = process_file(filepath)  # Returns True if file was changed

    # Process lines in memory
    from claudeutils.markdown import process_lines

    lines = ["**File:** test.md\n", "**Model:** Sonnet\n"]
    fixed_lines = process_lines(lines)
"""

import re
from pathlib import Path

from pydantic import BaseModel

from claudeutils.exceptions import (
    MarkdownInnerFenceError,
    MarkdownProcessingError,
)


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
    fix_fn: callable[..., list[str]],  # type: ignore[type-arg]
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
            text_lines = []
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


def escape_inline_backticks(lines: list[str]) -> list[str]:
    """Escape triple backticks when they appear inline in text.

    Wraps ```language and ``` with double backticks (`` ``` ``) to prevent
    them from being interpreted as code fence markers by markdown parsers.

    - Skips lines that start with ``` (real code fences)
    - Skips content inside code blocks
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

        # Escape inline triple backticks (with or without language)
        # Negative lookbehind ensures we don't re-escape already escaped ones
        escaped_line = re.sub(r"(?<!`` )```(\w*)", r"`` ```\1 ``", line)
        result.append(escaped_line)

    return result


def fix_metadata_blocks(lines: list[str]) -> list[str]:
    """Convert consecutive **Label:** lines to list items and indent following
    lists."""
    result = []
    i = 0
    # Match both **Label:** and **Label**: patterns (with optional content after)
    pattern = r"^\*\*[A-Za-z][^*]+:\*\*|^\*\*[A-Za-z][^*]+\*\*:"
    while i < len(lines):
        line = lines[i]
        if re.match(pattern, line.strip()):
            metadata_lines = [line]
            j = i + 1
            found_blank = False
            while j < len(lines):
                next_line = lines[j]
                if re.match(pattern, next_line.strip()):
                    metadata_lines.append(next_line)
                    j += 1
                elif next_line.strip() == "":
                    # Empty line ends block
                    found_blank = True
                    j += 1
                    break
                else:
                    break
            if len(metadata_lines) >= 2:
                for meta_line in metadata_lines:
                    stripped = meta_line.strip()
                    if stripped:
                        result.append(f"- {stripped}\n")
                # Preserve blank line
                if found_blank:
                    result.append("\n")

                # Indent following list items (if any)
                while j < len(lines):
                    list_line = lines[j]
                    list_stripped = list_line.strip()

                    if list_stripped == "":
                        result.append(list_line)
                        j += 1
                        break

                    if not re.match(r"^[-*] |^\d+\. ", list_stripped):
                        break

                    result.append(f"  {list_stripped}\n")
                    j += 1

                i = j
                continue
        result.append(line)
        i += 1
    return result


def fix_numbered_list_spacing(lines: list[str]) -> list[str]:
    """Ensure numbered lists have proper blank line spacing.

    Rules:
    1. Add blank line before a numbered list when it follows non-list content
    2. Add blank line after **Label:** when followed by a numbered list
    3. Do NOT add blank lines within a numbered list (between items or continuations)
    """
    result: list[str] = []
    numbered_list_pattern = r"^[0-9]+\. \S"
    bullet_list_pattern = r"^[*+-] \S"
    label_pattern = r"^\*\*[^*]+:\*\*\s*$"

    in_numbered_list = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        is_numbered_item = bool(
            re.match(numbered_list_pattern, stripped)
        ) and not line.startswith("   ")
        is_blank = stripped == ""
        is_continuation = in_numbered_list and line.startswith("   ") and not is_blank

        # Update list context BEFORE processing
        if is_blank:
            in_numbered_list = False
        elif is_numbered_item:
            # Check if we should add blank before this list item
            if not in_numbered_list and len(result) > 0:
                prev = result[-1].strip()
                # Add blank only if prev is not blank, not a list item, not **Label:**
                if (
                    prev != ""
                    and not re.match(numbered_list_pattern, prev)
                    and not re.match(bullet_list_pattern, prev)
                    and not re.match(label_pattern, prev)
                ):
                    result.append("\n")
            in_numbered_list = True
        elif not is_continuation:
            # Non-blank, non-numbered, non-continuation exits list context
            in_numbered_list = False

        result.append(line)

        # Add blank line after **Label:** ONLY if next line is a numbered list
        if re.match(label_pattern, stripped) and i + 1 < len(lines):
            next_line = lines[i + 1]
            next_stripped = next_line.strip()
            if re.match(
                numbered_list_pattern, next_stripped
            ) and not next_line.startswith("   "):
                result.append("\n")

    return result


def fix_warning_lines(lines: list[str]) -> list[str]:
    """Convert to list items lines with consistent non-markup prefixes.

    Claude often generates consecutive lines with emoji or symbol prefixes
    that should be formatted as lists. This detects patterns like:
    - ✅ Task completed
    - ❌ Task failed
    - ⚠️ Warning message
    - [TODO] Action item

    Only converts groups of 2+ lines with similar prefix patterns.
    Skips lines already formatted as lists (-, *, numbered).
    """
    result = []
    i = 0

    def extract_prefix(line: str) -> str | None:
        """Extract non-markup prefix from line.

        Returns None if line is empty, is already a list item, or has no clear
        prefix. Returns prefix string (e.g., "✅", "[TODO]", "NOTE:") if found.

        ONLY matches:
        - Emoji-like symbols (non-alphanumeric at start)
        - Bracketed text [like this]
        - Uppercase words ending with colon (NOTE:, WARNING:, TODO:)

        Explicitly excludes:
        - Regular prose (lowercase words)
        - Block quotes (>)
        - Tree diagrams (├, └, │)
        - YAML keys or section headers (lowercase word + colon)
        """
        stripped = line.strip()
        if not stripped:
            return None
        if re.match(r"^[-*]|^\d+\.", stripped):
            return None

        # Skip table rows (start with | and contain 2+ pipes)
        if stripped.startswith("|") and stripped.count("|") >= 2:
            return None

        # Skip block quotes (start with >)
        if stripped.startswith(">"):
            return None

        # Skip tree diagram symbols
        if any(sym in stripped[:3] for sym in ["├", "└", "│"]):
            return None

        # Match emoji-like prefixes (non-alphanumeric, non-whitespace at start)
        # Exclude: [ ( { - * | > ` (these have special meanings)
        emoji_match = re.match(r"^([^\w\s\[\(\{\-\*\|>`]+)(\s|$)", stripped)
        if emoji_match:
            return emoji_match.group(1)

        # Match bracketed prefixes [like this]
        bracket_match = re.match(r"^(\[[^\]]+\])(\s|$)", stripped)
        if bracket_match:
            return bracket_match.group(1)

        # Match ONLY uppercase word + colon at start (followed by space)
        # NOTE: This, WARNING: That, TODO: Item
        # But NOT lowercase: Implementation:, description:
        colon_match = re.match(r"^([A-Z][A-Z0-9_]*:)\s", stripped)
        if colon_match:
            return colon_match.group(1)

        # No valid prefix found
        return None

    def is_similar_prefix(p1: str | None, p2: str | None) -> bool:
        """Check if two prefixes are similar (emoji, bracket, colon types)."""
        if p1 is None or p2 is None:
            return False
        if p1 == p2:
            return True

        def is_emoji_prefix(prefix: str) -> bool:
            return bool(re.match(r"^[^\w\s\[\(\{\-\*]", prefix))

        def is_bracket_prefix(prefix: str) -> bool:
            return prefix.startswith("[")

        def is_colon_prefix(prefix: str) -> bool:
            return prefix.endswith(":")

        return (
            (is_emoji_prefix(p1) and is_emoji_prefix(p2))
            or (is_bracket_prefix(p1) and is_bracket_prefix(p2))
            or (is_colon_prefix(p1) and is_colon_prefix(p2))
        )

    while i < len(lines):
        line = lines[i]
        prefix = extract_prefix(line)

        if prefix:
            prefixed_lines = [line]
            j = i + 1
            while j < len(lines):
                next_prefix = extract_prefix(lines[j])
                if is_similar_prefix(prefix, next_prefix):
                    prefixed_lines.append(lines[j])
                    j += 1
                else:
                    break

            if len(prefixed_lines) >= 2:
                for pline in prefixed_lines:
                    stripped = pline.strip()
                    result.append(f"- {stripped}\n")
                i = j
                continue

        result.append(line)
        i += 1

    return result


def fix_nested_lists(lines: list[str]) -> list[str]:
    """Convert lettered sub-items (a., b., c.) to numbered lists."""
    result = []
    for line in lines:
        stripped = line.strip()
        match = re.match(r"^([a-z])\.\s+(.+)$", stripped)
        if match:
            letter = match.group(1)
            content = match.group(2)
            num = ord(letter) - ord("a") + 1  # a=1, b=2, etc.
            indent = line[: len(line) - len(line.lstrip())]
            result.append(f"{indent}{num}. {content}\n")
        else:
            result.append(line)
    return result


def fix_backtick_spaces(lines: list[str]) -> list[str]:
    """Quote content in backticks when it has leading/trailing spaces.

    Makes whitespace explicit in inline code, preventing ambiguity when
    documenting strings with intentional leading/trailing spaces.

    Examples:
        `` `blah ` `` → `` `"blah "` `` (trailing space now visible)
        `` ` blah` `` → `` `" blah"` `` (leading space now visible)
        `` `code` `` → `` `code` `` (unchanged if no spaces)

    Skips escaped backticks (`` `` ``) to avoid processing them twice.
    """
    result = []
    for line in lines:
        # Skip if line contains escaped backticks - don't process twice
        if "`` " in line or " ``" in line:
            result.append(line)
            continue

        # Find all backtick pairs and check for leading/trailing spaces
        def replace_backticks(match: re.Match[str]) -> str:
            content = match.group(1)
            # Check if content has leading or trailing space
            if content and (content[0] == " " or content[-1] == " "):
                return f'`"{content}"`'
            return f"`{content}`"

        # Match backtick pairs with content inside
        modified = re.sub(r"`([^`]*)`", replace_backticks, line)
        result.append(modified)
    return result


def fix_metadata_list_indentation(lines: list[str]) -> list[str]:
    """Convert metadata labels to list items and indent following lists.

    Claude generates metadata labels like **Plan Files:** followed by lists.
    This converts the label to a list item and indents the following list
    by 2 spaces to create proper nested list structure.

    Example:
        **Plan Files:**          →    - **Plan Files:**
        - phase-1.md                    - phase-1.md
        - phase-2.md                    - phase-2.md

    Works with both **Label:** and **Label**: patterns.
    """
    result: list[str] = []
    i = 0
    label_pattern = r"^\*\*[^*]+:\*\*\s*$|^\*\*[^*]+\*\*:\s*$"

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        indent = line[: len(line) - len(line.lstrip())]

        if (
            re.match(label_pattern, stripped)
            and i + 1 < len(lines)
            and re.match(r"^[-*]|^\d+\.", lines[i + 1].strip())
        ):
            result.append(f"{indent}- {stripped}\n")

            j = i + 1
            while j < len(lines):
                list_line = lines[j]
                list_stripped = list_line.strip()

                if list_stripped == "":
                    result.append(list_line)
                    j += 1
                    break

                if not re.match(r"^[-*]|^\d+\.", list_stripped):
                    break

                indent_len = len(list_line) - len(list_line.lstrip())
                list_indent = list_line[:indent_len]
                result.append(f"{list_indent}  {list_stripped}\n")
                j += 1

            i = j
            continue

        result.append(line)
        i += 1

    return result


def fix_markdown_code_blocks(lines: list[str]) -> list[str]:
    """Nest ```markdown blocks that contain inner ``` fences.

    Claude sometimes generates ```markdown blocks containing code examples
    with their own ``` fences. This uses ```` (4 backticks) for the outer
    fence to properly nest the content.

    Raises:
        ValueError: If inner fence detected in non-markdown code block.
                    This prevents dprint formatting failures downstream.

    Note: Only processes ```markdown blocks. Other language blocks with
          inner fences will error out to prevent silent formatting issues.
    """
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```") and len(stripped) > 3:
            language = stripped[3:]
            is_markdown = language == "markdown"

            block_lines = [line]
            j = i + 1
            fence_depth = 0
            has_inner_fence = False

            while j < len(lines):
                block_line = lines[j]
                block_lines.append(block_line)
                block_stripped = block_line.strip()

                if block_stripped.startswith("```"):
                    if len(block_stripped) > 3:
                        fence_depth += 1
                        has_inner_fence = True
                    elif block_stripped == "```":
                        if fence_depth > 0:
                            fence_depth -= 1
                            has_inner_fence = True
                        else:
                            # At fence_depth==0: is this inner opening or outer closing?
                            # Look ahead for matching closing fence
                            found_matching_close = False
                            for k in range(j + 1, len(lines)):
                                check_line = lines[k].strip()
                                if check_line == "```":
                                    found_matching_close = True
                                    break
                                if check_line.startswith("```") and len(check_line) > 3:
                                    # Opening fence before close - stop looking
                                    break

                            if found_matching_close:
                                # This is an inner opening fence
                                fence_depth += 1
                                has_inner_fence = True
                            else:
                                # This is the outer closing fence
                                has_inner = any(
                                    "```" in lines[k] for k in range(i + 1, j)
                                )
                                if j > i + 1 and has_inner:
                                    has_inner_fence = True
                                break

                j += 1
            else:
                result.extend(block_lines)
                i = j
                continue

            if has_inner_fence:
                if is_markdown:
                    result.append("````markdown\n")
                    result.extend(block_lines[1:-1])
                    result.append("````\n")
                else:
                    msg = (
                        f"Inner fence detected in non-markdown block "
                        f"(language: {language}, line: {i + 1}). "
                        f"This will cause dprint formatting to fail."
                    )
                    raise MarkdownInnerFenceError(msg)
            else:
                result.extend(block_lines)

            i = j + 1
            continue

        result.append(line)
        i += 1

    return result


# ============================================================================
# Processing Pipeline
# ============================================================================
#
# This module applies multiple fixes in a specific order to handle
# Claude-generated markdown patterns:
#
# 1. escape_inline_backticks  - Escape ``` in inline text to prevent ambiguity
# 2. fix_dunder_references    - Wrap `__init__.py` in backticks
# 3. fix_metadata_blocks      - Convert consecutive **Label:** to lists
# 4. fix_warning_lines        - Convert emoji/symbol prefixed lines to lists
# 5. fix_nested_lists         - Convert lettered items (a., b.) to numbered
# 6. fix_metadata_list_indentation - Indent lists after metadata labels
# 7. fix_numbered_list_spacing - Add proper blank lines around numbered lists
# 8. fix_markdown_code_blocks - Nest markdown blocks with inner fences
#
# Order matters: Line-based fixes run before block-based fixes to avoid
# interference. Spacing fixes run near the end after structure is correct.
# escape_inline_backticks runs first to prevent ``` in text from being
# confused with code fences.
#


def process_lines(lines: list[str]) -> list[str]:
    """Apply all markdown structure fixes to lines."""
    # Parse document into segments (processable vs protected)
    segments = parse_segments(lines)

    # Apply fixes to processable segments only
    segments = apply_fix_to_segments(segments, escape_inline_backticks)
    segments = apply_fix_to_segments(
        segments, lambda ls: [fix_dunder_references(line) for line in ls]
    )
    segments = apply_fix_to_segments(segments, fix_metadata_blocks)
    segments = apply_fix_to_segments(segments, fix_warning_lines)
    segments = apply_fix_to_segments(segments, fix_nested_lists)
    # Disabled: fix_metadata_blocks now handles list indentation after metadata blocks
    # segments = apply_fix_to_segments(segments, fix_metadata_list_indentation)
    segments = apply_fix_to_segments(segments, fix_numbered_list_spacing)
    segments = apply_fix_to_segments(segments, fix_backtick_spaces)

    # Flatten segments back to lines
    result = flatten_segments(segments)

    # fix_markdown_code_blocks runs on flattened output (needs full document view)
    return fix_markdown_code_blocks(result)


def process_file(filepath: Path) -> bool:
    """Process a markdown file, returning True if modified."""
    with filepath.open(encoding="utf-8") as f:
        original_lines = f.readlines()
    try:
        lines = process_lines(original_lines)
    except MarkdownInnerFenceError as e:
        raise MarkdownProcessingError(str(filepath), e) from e
    if lines == original_lines:
        return False
    with filepath.open("w", encoding="utf-8") as f:
        f.writelines(lines)
    return True
