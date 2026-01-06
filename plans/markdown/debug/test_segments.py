#!/usr/bin/env python3
import importlib.util

# Load markdown module directly without going through __init__.py
spec = importlib.util.spec_from_file_location(
    "markdown", "/Users/david/code/claudeutils/src/claudeutils/markdown.py"
)
markdown = importlib.util.module_from_spec(spec)
spec.loader.exec_module(markdown)

parse_segments = markdown.parse_segments
process_lines = markdown.process_lines

# Test content from actual file
input_lines = [
    "### Checklist Detection\n",
    "\n",
    "**Input:**\n",
    "\n",
    "```\n",
    "✅ Issue #1: XPASS tests visible\n",
    "✅ Issue #2: Setup failures captured\n",
    "❌ Issue #3: Not fixed yet\n",
    "```\n",
    "\n",
    "**Output:**\n",
]

print("INPUT LINES:")
for i, line in enumerate(input_lines):
    print(f"  {i}: {line!r}")

print("\nPARSED SEGMENTS:")
segments = parse_segments(input_lines)
for seg in segments:
    print(
        f"  Segment: processable={seg.processable}, language={seg.language!r}, lines={len(seg.lines)}, start={seg.start_line}"
    )
    for j, line in enumerate(seg.lines):
        print(f"    [{seg.start_line + j}] {line!r}")

print("\nPROCESSED OUTPUT:")
result = process_lines(input_lines)
for i, line in enumerate(result):
    print(f"  {i}: {line!r}")

print("\nCHANGED LINES:")
for i in range(len(input_lines)):
    if i < len(result) and input_lines[i] != result[i]:
        print(f"  Line {i}: {input_lines[i]!r} -> {result[i]!r}")
