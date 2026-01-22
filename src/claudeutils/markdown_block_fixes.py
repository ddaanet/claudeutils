"""Code block markdown fixes.

Handles nesting of markdown blocks containing inner fence markers.
"""


def fix_markdown_code_blocks(lines: list[str]) -> list[str]:
    """Nest ```markdown blocks that contain inner ``` fences.

    Claude sometimes generates ```markdown blocks containing code examples
    with their own ``` fences. This uses ```` (4 backticks) for the outer
    fence to properly nest the content.

    Note: Only processes ```markdown blocks. Other language blocks with
          inner fences are left as-is, since inline backtick escaping
          handles them correctly.
    """
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```") and len(stripped) > 3:
            language = stripped[3:]

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
                # Upgrade any block with inner fences to use ````
                # This handles Claude output that discusses fenced blocks
                result.append(f"````{language}\n")
                result.extend(block_lines[1:-1])
                result.append("````\n")
            else:
                # No inner fences, pass through as-is
                result.extend(block_lines)

            i = j + 1
            continue

        result.append(line)
        i += 1

    return result
