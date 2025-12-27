# Plan Creation Module

---
author_model: claude-opus-4-5-20251101
semantic_type: workflow
expansion_sensitivity: medium
target_rules:
  strong: 6-8
  standard: 10-14
  weak: 14-18
---

## Semantic Intent

Planning agents create plans that force incremental implementation. Tests must be
ordered so each one requires exactly one new piece of code. Plans include checkpoints
for user validation.

---

## Critical (Tier 1)

### Force Incremental Implementation

Each test should require exactly one new piece of code. If a test passes unexpectedly,
the sequence is wrong. Order tests so consecutive tests don't expect the same output.

### Include Checkpoints

Build checkpoints into plans at natural boundaries (every 3-5 tests or after completing
a feature group). Checkpoints are mandatory stopping points.

### Explicit Checkpoint Language

Write: "Run `just role-code tests/test_X.py` - awaiting approval"
Not: "Verify tests pass" (ambiguous)

Checkpoints must specify the exact verification command.

---

## Important (Tier 2)

### Test Ordering Strategy

Prefer testing normal cases first (non-empty output), then edge cases. Empty-input
tests are usually unnecessary - this behavior emerges from loops. Only test empty
input when it should be an error.

Example progression:
1. One matching item (requires: read, check, collect)
2. Multiple items, some match (requires: loop, filter)
3. No matches (no new code - validates filtering)

### Specification Format

For each test, specify:
- Given/When/Then with exact fixture data inline
- What NEW code this test requires
- What it does NOT require yet

### Group by Capability

Group tests by capability progression: discovery -> filtering -> error handling ->
recursion. Complete one capability before moving to the next.

---

## Preferred (Tier 3)

### Plan Format Efficiency

Markdown is 34-38% more token-efficient than JSON. Use:
- Numbered lists for sequential steps
- Backticks for paths and commands
- Bold for constraints: **MUST**, **NEVER**
- Action verbs to start each step

### Omit Noise

Omit from plans:
- Rationale (decision already made)
- Alternatives (planner chose)
- Error handling logic (executor handles)
- Nested lists deeper than 2 levels
