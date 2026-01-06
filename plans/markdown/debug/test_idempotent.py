import re

pattern = r"(?<!`` )(`{3,})(\w*)(?! ``)"

# Simulate what happens
line1 = "   - Changed: `````markdown block → `` ```` `` markdown block`\n"
print("ORIGINAL:")
print(repr(line1))

# First pass
result1 = re.sub(pattern, r"`` \1\2 ``", line1)
print("\nAFTER FIRST PASS:")
print(repr(result1))
print("Matches:")
for match in re.finditer(pattern, line1):
    print(f"  {match.group(0)!r} at pos {match.span()}")

# Second pass
result2 = re.sub(pattern, r"`` \1\2 ``", result1)
print("\nAFTER SECOND PASS:")
print(repr(result2))
print("Matches:")
for match in re.finditer(pattern, result1):
    print(f"  {match.group(0)!r} at pos {match.span()}, groups: {match.groups()}")
    # Show context
    start = max(0, match.start() - 5)
    end = min(len(result1), match.end() + 5)
    print(f"  Context: {result1[start:end]!r}")

# Third pass to see if it stabilizes
result3 = re.sub(pattern, r"`` \1\2 ``", result2)
print("\nAFTER THIRD PASS:")
print(repr(result3))
print("Changed from second? ", result2 != result3)
