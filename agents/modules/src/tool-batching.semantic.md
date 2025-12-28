# Tool Batching Module

---
author_model: claude-opus-4-5-20251101
semantic_type: cross_cutting
expansion_sensitivity: low
target_rules:
  strong: 4-6
  standard: 6-8
  weak: 8-12
---

## Semantic Intent

Agent should minimize round-trips by batching tool calls efficiently. Independent
operations run in parallel; dependent operations run sequentially. Same-file edits
require special care to avoid line number drift.

---

## Critical (Tier 1)

### Batch Independent Operations

Read multiple files in one message when all are needed soon. Edit different files in
parallel when changes are independent. Do not serialize operations that could run
concurrently.

### Sequential Same-File Edits

When making multiple edits to the same file, edit sequentially (not parallel) to avoid
line number drift. When inserting content, work bottom-to-top so earlier insertions
don't shift line numbers of later targets.

---

## Important (Tier 2)

### Plan Before Executing

Before making tool calls, identify ALL changes needed for the current task. Group by
file: same-file edits are sequential, different-file edits can be parallel.

### Refresh Context After Writes

After a batch of writes, read modified files to refresh context before making dependent
edits. Stale line numbers cause edit failures.

---

## Preferred (Tier 3)

### Minimize Tool Call Count

Each tool call has overhead. Prefer fewer calls with more content over many small calls.
But do not sacrifice correctness for efficiency.
