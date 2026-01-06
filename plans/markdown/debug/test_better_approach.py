import re


def escape_inline_backticks_v1(lines):
    """Current broken version."""
    result = []
    in_code_block = False
    pattern = r"(?<!`` )(`{3,})(\w*)(?! ``)"

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            result.append(line)
            continue
        if in_code_block:
            result.append(line)
            continue
        escaped_line = re.sub(pattern, r"`` \1\2 ``", line)
        result.append(escaped_line)
    return result


def escape_inline_backticks_v2(lines):
    """Fixed version: Skip lines that already have escaped sequences."""
    result = []
    in_code_block = False
    pattern = r"(?<!`` )(`{3,})(\w*)(?! ``)"

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            result.append(line)
            continue
        if in_code_block:
            result.append(line)
            continue

        # Check if line contains already-escaped sequences (`` ``` ... ``)
        # If it does, skip processing to maintain idempotency
        if re.search(r"`` `{3,}", line):
            result.append(line)
            continue

        escaped_line = re.sub(pattern, r"`` \1\2 ``", line)
        result.append(escaped_line)
    return result


# Test cases - actual content lines (not fence lines)
test_lines = [
    "   - Changed: `````markdown block\n",  # Indented, not a fence
    "Output: ````markdown\n",
    "Already escaped: `` `````markdown `` block\n",
    "Normal text with no backticks\n",
]

print("=" * 70)
print("V1 (Current - Broken):")
print("=" * 70)
pass1 = escape_inline_backticks_v1(test_lines)
pass2 = escape_inline_backticks_v1(pass1)
pass3 = escape_inline_backticks_v1(pass2)
for i, (orig, p1, p2, p3) in enumerate(
    zip(test_lines, pass1, pass2, pass3, strict=False)
):
    print(f"\nLine {i}:")
    print(f"  Orig:   {orig!r}")
    print(f"  Pass 1: {p1!r}")
    print(f"  Pass 2: {p2!r}")
    print(f"  Pass 3: {p3!r}")
    if p1 == p2 == p3:
        print("  ✅ IDEMPOTENT")
    else:
        print("  ❌ NOT IDEMPOTENT")

print("\n" + "=" * 70)
print("V2 (Fixed - Skip already-escaped):")
print("=" * 70)
pass1 = escape_inline_backticks_v2(test_lines)
pass2 = escape_inline_backticks_v2(pass1)
pass3 = escape_inline_backticks_v2(pass2)
for i, (orig, p1, p2, p3) in enumerate(
    zip(test_lines, pass1, pass2, pass3, strict=False)
):
    print(f"\nLine {i}:")
    print(f"  Orig:   {orig!r}")
    print(f"  Pass 1: {p1!r}")
    print(f"  Pass 2: {p2!r}")
    print(f"  Pass 3: {p3!r}")
    if p1 == p2 == p3:
        print("  ✅ IDEMPOTENT")
    else:
        print("  ❌ NOT IDEMPOTENT")
