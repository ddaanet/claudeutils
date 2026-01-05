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


def fix_dunder_references(line: str) -> str:
    """Wrap __name__.py in backticks within headings."""
    if line.startswith("#"):
        # Negative lookbehind/lookahead to avoid double-wrapping
        line = re.sub(r"(?<!`)(__[A-Za-z0-9_]+__(\.py)?)(?!`)", r"`\1`", line)
    return line


def fix_metadata_blocks(lines: list[str]) -> list[str]:
    """Convert consecutive **Label:** lines to list items."""
    result = []
    i = 0
    # Match both **Label:** and **Label**: patterns
    pattern = r"^\*\*[A-Za-z][^*]+:\*\* |^\*\*[A-Za-z][^*]+\*\*: "
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
        """
        stripped = line.strip()
        if not stripped:
            return None
        if re.match(r'^[-*]|^\d+\.', stripped):
            return None

        match = re.match(r'^(\S+(?:\s|:))', stripped)
        if match:
            return match.group(1).rstrip()
        return None

    def is_similar_prefix(p1: str | None, p2: str | None) -> bool:
        """Check if two prefixes are similar (emoji, bracket, colon types)."""
        if p1 is None or p2 is None:
            return False
        if p1 == p2:
            return True

        def is_emoji_prefix(prefix: str) -> bool:
            return bool(re.match(r'^[^\w\s\[\(\{\-\*]', prefix))

        def is_bracket_prefix(prefix: str) -> bool:
            return prefix.startswith('[')

        def is_colon_prefix(prefix: str) -> bool:
            return prefix.endswith(':')

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
                                if (
                                    check_line.startswith("```")
                                    and len(check_line) > 3
                                ):
                                    # Opening fence before close - stop looking
                                    break

                            if found_matching_close:
                                # This is an inner opening fence
                                fence_depth += 1
                                has_inner_fence = True
                            else:
                                # This is the outer closing fence
                                has_inner = any(
                                    "```" in lines[k]
                                    for k in range(i + 1, j)
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
                    raise ValueError(msg)
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
# 1. fix_dunder_references    - Wrap `__init__.py` in backticks
# 2. fix_metadata_blocks      - Convert consecutive **Label:** to lists
# 3. fix_warning_lines        - Convert emoji/symbol prefixed lines to lists
# 4. fix_nested_lists         - Convert lettered items (a., b.) to numbered
# 5. fix_metadata_list_indentation - Indent lists after metadata labels
# 6. fix_numbered_list_spacing - Add proper blank lines around numbered lists
# 7. fix_markdown_code_blocks - Nest markdown blocks with inner fences
#
# Order matters: Line-based fixes run before block-based fixes to avoid
# interference. Spacing fixes run near the end after structure is correct.
#


def process_lines(lines: list[str]) -> list[str]:
    """Apply all markdown structure fixes to lines."""
    result = [fix_dunder_references(line) for line in lines]
    result = fix_metadata_blocks(result)
    result = fix_warning_lines(result)
    result = fix_nested_lists(result)
    result = fix_metadata_list_indentation(result)
    result = fix_numbered_list_spacing(result)
    return fix_markdown_code_blocks(result)


def process_file(filepath: Path) -> bool:
    """Process a markdown file, returning True if modified."""
    with filepath.open(encoding="utf-8") as f:
        original_lines = f.readlines()
    lines = process_lines(original_lines)
    if lines == original_lines:
        return False
    with filepath.open("w", encoding="utf-8") as f:
        f.writelines(lines)
    return True
