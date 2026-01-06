import re

# The regex from escape_inline_backticks
pattern = r"(?<!`` )```(\w*)"

test_cases = [
    "- Output: ````markdown block",  # Original (4 backticks)
    "- Output: `` ````markdown `` block",  # Proposed fix (inline code)
    "- Input: `` ```markdown `` block",  # Current working (3 backticks)
]

for test in test_cases:
    result = re.sub(pattern, r"`` ```\1 ``", test)
    print(f"Input:  {test}")
    print(f"Output: {result}")
    print(f"Changed: {result != test}")
    print()
