from claudeutils.markdown import process_lines

with open("/tmp/claude/test_example.md") as f:
    lines = f.readlines()

result = process_lines(lines)
print("".join(result))
