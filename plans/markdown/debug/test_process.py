import sys

sys.path.insert(0, "/Users/david/code/claudeutils/src")
from claudeutils.markdown import process_markdown

with open("/tmp/claude/test_line.txt") as f:
    content = f.read()

result = process_markdown(content)
print("ORIGINAL:")
print(repr(content))
print("\nRESULT:")
print(repr(result))
print("\nVISUAL COMPARISON:")
print("Before:", content)
print("After: ", result)
