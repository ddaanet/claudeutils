#!/usr/bin/env python3
"""Fix markdown structure before reformatting."""

import re
import sys
from pathlib import Path


def fix_dunder_references(line: str) -> str:
    """Wrap __name__.py in backticks within headings."""
    if line.startswith("#"):
        # Negative lookbehind/lookahead to avoid double-wrapping
        line = re.sub(r"(?<!`)(__[A-Za-z0-9_]+__(\.py)?)(?!`)", r"`\1`", line)
    return line


def fix_metadata_blocks(lines: list[str]) -> list[str]:
    """Convert consecutive **Label:** or **Label**: value lines to list items."""
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
    """Ensure lists after **Label:** have blank line before them."""
    result = []
    numbered_list_pattern = r"^[0-9]+\. \S"
    bullet_list_pattern = r"^[*+-] \S"

    for i, line in enumerate(lines):
        # Add blank line before top-level numbered lists
        # Skip if previous line is already blank or is a bullet/numbered list
        if (
            i > 0
            and re.match(numbered_list_pattern, line.strip())
            and not line.startswith("   ")
        ):
            prev_line_idx = len(result) - 1
            if prev_line_idx >= 0:
                prev = result[prev_line_idx].strip()
                # Add blank only if prev is not blank, not a list item, not **Label:**
                if (
                    prev != ""
                    and not re.match(numbered_list_pattern, prev)
                    and not re.match(bullet_list_pattern, prev)
                    and not re.match(r"^\*\*[^*]+:\*\*\s*$", prev)
                ):
                    result.append("\n")

        result.append(line)

        # Add blank line after **Label:**
        if re.match(r"^\*\*[^*]+:\*\*\s*$", line.strip()):
            if i + 1 < len(lines) and lines[i + 1].strip() != "":
                result.append("\n")
    return result


def fix_warning_lines(lines: list[str]) -> list[str]:
    """Convert consecutive ⚠️ or Option X: lines to list items."""
    result = []
    i = 0
    option_pattern = r"^Option [A-Z]: "

    def is_listable_line(line: str) -> bool:
        stripped = line.strip()
        return stripped.startswith("⚠️ ") or bool(re.match(option_pattern, stripped))

    while i < len(lines):
        line = lines[i]
        if is_listable_line(line):
            warning_lines = [line]
            j = i + 1
            while j < len(lines) and is_listable_line(lines[j]):
                warning_lines.append(lines[j])
                j += 1
            if len(warning_lines) >= 2:
                for warn_line in warning_lines:
                    stripped = warn_line.strip()
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


def process_lines(lines: list[str]) -> list[str]:
    """Apply all markdown structure fixes to lines."""
    lines = [fix_dunder_references(line) for line in lines]
    lines = fix_metadata_blocks(lines)
    lines = fix_warning_lines(lines)
    lines = fix_nested_lists(lines)
    return fix_numbered_list_spacing(lines)


def process_file(filepath: Path) -> bool:
    """Process a markdown file. Returns True if modified."""
    with open(filepath, encoding="utf-8") as f:
        original_lines = f.readlines()
    lines = process_lines(original_lines)
    if lines == original_lines:
        return False
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return True


def main() -> None:
    files = [line.strip() for line in sys.stdin if line.strip()]
    if not files:
        return
    for filepath_str in files:
        filepath = Path(filepath_str)
        if filepath.exists() and filepath.suffix == ".md":
            if process_file(filepath):
                print(filepath_str)  # noqa: T201 - print expected in scripts


if __name__ == "__main__":
    main()
