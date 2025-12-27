# Code Review Module

---
author_model: claude-opus-4-5-20251101
semantic_type: workflow
expansion_sensitivity: medium
target_rules:
  strong: 8-10
  standard: 14-18
  weak: 20-26
---

## Semantic Intent

Review examines code after implementation, looking for issues not caught during
development. Focus on correctness, efficiency, and maintainability. Review without
bias from the original plan—evaluate code on its own merits.

---

## Critical (Tier 1)

### Review Without Plan Bias

Do NOT look at plan files during review. Evaluate code on its own merits. The goal is
to catch issues the implementation agent missed, not verify plan compliance.

### Correctness First

Check for:
- Logic errors, off-by-one, boundary conditions
- Null/None handling, error propagation
- Concurrency issues if applicable

These are highest priority—incorrect code should not ship.

### No Scope Expansion

Review identifies issues; it does not add features. Do not expand scope beyond what
review identifies. If design-level issues are found, stop and report rather than
attempting fixes.

---

## Important (Tier 2)

### Algorithmic Complexity

- Verify time/space complexity appropriate for expected data sizes
- Flag O(n²) or worse where O(n) or O(n log n) is achievable
- Identify unnecessary repeated computation

### Memory Concerns

- Look for memory leaks (unclosed resources, growing caches)
- Flag excessive memory use (loading entire files when streaming suffices)
- Check for reference cycles that prevent garbage collection

### Expressiveness

- Code should read naturally; intent clear from structure
- Prefer domain vocabulary over generic names
- Functions do one thing with descriptive names

### Factorization

- No copy-paste code; extract shared logic
- Functions at consistent abstraction levels
- Modules have clear, single responsibilities

### Concision

- Remove dead code, unused imports, unreachable branches
- Collapse verbose patterns into idiomatic forms
- Eliminate redundant intermediate variables

### Tracing and Debug Code

- Verify logging/tracing is disabled by default
- No print statements left in production code
- Debug flags default to off

---

## Important (Tier 2) - Test Review

### Setup vs Implementation Ratio

Test setup SHOULD NOT dominate implementation under test. If setup exceeds
implementation:
- Propose fixtures for shared setup across tests
- Propose helpers that encapsulate meaningful test operations
- Fixtures/helpers MUST be meaningful, not arbitrary groupings

### Test Concision

- Remove redundant assertions that don't add coverage
- Collapse similar test cases into parametrized tests
- Each test verifies one logical behavior

### Test Docstrings

- Keep test docstrings compact: what behavior is verified
- Docstring SHOULD NOT exceed implementation length
- Omit docstrings on self-documenting test names

---

## Important (Tier 2) - Structure Review

### Function Length

If a function requires internal section comments to navigate:
- Extract sections into smaller functions
- Each extracted function should have a clear, single purpose
- Prefer many small functions over few large ones

### Complexity

- Flag deeply nested conditionals (3+ levels)
- Suggest early returns to flatten logic
- Identify candidates for pattern matching or dispatch tables

---

## Preferred (Tier 3)

### Review Output

Save review to `plans/review-<plan-name>.md` matching the plan being implemented.

Simple changes (< 10 edits): implement directly in single tool batch.
Complex changes: create plan for haiku execution with standard plan format.

### Documentation Review

Remove comments that add no information:
- "Initialize the list" before `items = []`
- "Return the result" before `return result`
Keep comments explaining WHY, not WHAT.

### Blank Line Discipline

- Max 1 blank line between logical sections within function
- Max 2 blank lines between top-level definitions
- Remove trailing blank lines
