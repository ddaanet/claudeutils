---
name: planning
description: Test-first design for TDD execution
---

# Planning Role

**Target Model:** Sonnet (default) or Opus (deep architecture). Plans executed by code
role agents.

**Prerequisites:** `START.md`, `AGENTS.md`

---

## Core Principle

Plans must force incremental implementation. Each test should require exactly one new
piece of code—if a test passes unexpectedly, the sequence is wrong.

---

## Test Ordering

**Key insight:** Consecutive tests expecting the same output will cause the second to
pass unexpectedly.

Prefer testing normal cases first (non-empty output), then edge cases.
Empty-input-returns-empty tests are usually unnecessary—this behavior emerges from
loops. Only test empty input when it should be an error.

**Example progression:**

1. One matching item → `[path]` (requires: read file, check ID, collect)
2. Multiple items, some match → `[path1, path2]` (requires: loop, filter)
3. No matches → `[]` (no new code needed—validates filtering works)

---

## Specification Format

Code role agents need explicit scope boundaries. For each test, specify:

- Given/When/Then with exact fixture data inline
- What NEW code this test requires
- What it does NOT require yet

Group tests by capability (discovery → filtering → error handling → recursion).

---

## Validation Checkpoints

Build checkpoints into the plan at natural boundaries (every 3-5 tests or after
completing a feature group). At each checkpoint:

1. All tests pass (`just role-code`)
2. User reviews progress before continuing

**Checkpoint language must be explicit.** Write: "Run `just role-code tests/test_X.py` -
awaiting approval" not "Verify tests pass" (ambiguous).

Strong models review at checkpoints and adjust the plan if needed.

---

## Plan Structure

Write sections in implementation order. Feature 1 is implemented first.

---

## Plan Format

Markdown is 34-38% more token-efficient than JSON. Code agents follow explicit structure
better than prose.

**Use:**

- Numbered lists for sequential steps
- Backticks for paths and commands: `` `src/auth.ts` ``
- **Bold** for constraints: `**MUST**`, `**NEVER**`
- Action verbs to start each step: Read, Add, Run, Extract

**Omit:**

- Rationale (decision already made)
- Alternatives (planner chose)
- Error handling logic (executor handles)
- Nested lists deeper than 2 levels

**Step format:** `<verb> <target> → $output_var`

```markdown
# ❌ Verbose

- **Tool**: read_file
- **Input**: src/auth.ts
- **Reasoning**: We need to understand the current implementation

# ✅ Compact

1. Read `src/auth.ts` → $auth_code
```

---

## Artifacts

- Document design decisions in `agents/DESIGN_DECISIONS.md`
- Keep modules under 300 lines (hard limit: 400)
