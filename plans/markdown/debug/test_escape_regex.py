import re

pattern = r"(?<!`` )(`{3,})(\w*)(?! ``)"
test_inputs = [
    "`````markdown block",
    "Output: ````markdown",
    "Changed: `````markdown block → `` ```` `` markdown block`",
]

for inp in test_inputs:
    result = re.sub(pattern, r"`` \1\2 ``", inp)
    if inp != result:
        print(f"INPUT:  {inp!r}")
        print(f"OUTPUT: {result!r}")
        # Show what the regex matched
        for match in re.finditer(pattern, inp):
            print(f"  Match: {match.group(0)!r} at {match.span()}")
            print(f"    Group 1 (backticks): {match.group(1)!r}")
            print(f"    Group 2 (word): {match.group(2)!r}")
        print()
