import re

# Current broken pattern
old_pattern = r"(?<!`` )(`{3,})(\w*)(?! ``)"

# Proposed fix: Also check for being preceded/followed by single backtick + space
# This prevents matching inside `` ``` ... `` sequences
new_pattern = r"(?<!`` )(?<!` )(`{3,})(\w*)(?! ``)(?! `)"

test_cases = [
    # Should be escaped on first pass
    "`````markdown block",
    "Output: ````markdown",
    # Should NOT be re-escaped (already escaped)
    "`` `````markdown `` block",
    "`` ````markdown ``",
    # Should handle multiple on same line
    "Before ``` after ````test end",
]

print("=" * 70)
print("OLD PATTERN (current):")
print("=" * 70)
for test in test_cases:
    result1 = re.sub(old_pattern, r"`` \1\2 ``", test)
    result2 = re.sub(old_pattern, r"`` \1\2 ``", result1)  # Second pass
    print(f"\nInput:  {test!r}")
    print(f"Pass 1: {result1!r}")
    print(f"Pass 2: {result2!r}")
    if result1 != result2:
        print("  ❌ NOT IDEMPOTENT!")

print("\n" + "=" * 70)
print("NEW PATTERN (proposed):")
print("=" * 70)
for test in test_cases:
    result1 = re.sub(new_pattern, r"`` \1\2 ``", test)
    result2 = re.sub(new_pattern, r"`` \1\2 ``", result1)  # Second pass
    result3 = re.sub(new_pattern, r"`` \1\2 ``", result2)  # Third pass
    print(f"\nInput:  {test!r}")
    print(f"Pass 1: {result1!r}")
    print(f"Pass 2: {result2!r}")
    print(f"Pass 3: {result3!r}")
    if result1 == result2 == result3:
        print("  ✅ IDEMPOTENT!")
    else:
        print("  ❌ NOT IDEMPOTENT!")
