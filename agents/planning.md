---
name: planning
description: Test-first design for TDD execution
---

# Planning Skill

**Agent:** Strong models (opus/sonnet). Plans are executed by haiku.

**Prerequisites:** `START.md`, `AGENTS.md`, `agents/PLAN.md`

---

## Core Principle

Plans must force incremental implementation. Each test should require exactly one new piece of code—if a test passes unexpectedly, the sequence is wrong.

---

## Test Ordering

**Key insight:** Consecutive tests expecting the same output will cause the second to pass unexpectedly.

Prefer testing normal cases first (non-empty output), then edge cases. Empty-input-returns-empty tests are usually unnecessary—this behavior emerges from loops. Only test empty input when it should be an error.

**Example progression:**
1. One matching item → `[path]` (requires: read file, check ID, collect)
2. Multiple items, some match → `[path1, path2]` (requires: loop, filter)
3. No matches → `[]` (no new code needed—validates filtering works)

---

## Specification Format

Haiku agents need explicit scope boundaries. For each test, specify:
- Given/When/Then with exact fixture data inline
- What NEW code this test requires
- What it does NOT require yet

Group tests by capability (discovery → filtering → error handling → recursion).

---

## Validation Checkpoints

Build checkpoints into the plan at natural boundaries (every 3-5 tests or after completing a feature group). At each checkpoint:

1. All tests pass (`just test`)
2. Run `just check` - if it fails, STOP (code agent does NOT fix lint errors)
3. User reviews progress before continuing

**Checkpoint language must be explicit.** Write: "Run `just check` - if it fails, STOP (do not fix lint errors)" not "Verify `just check` passes" (ambiguous - could be read as "make it pass").

Haiku agents execute between checkpoints. Strong models review at checkpoints and adjust the plan if needed.

---

## Artifacts

- Document design decisions in `agents/DESIGN_DECISIONS.md`
- Keep modules under 300 lines (hard limit: 400)
