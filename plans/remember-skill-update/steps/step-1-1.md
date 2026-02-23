# Cycle 1.1

**Plan**: `plans/remember-skill-update/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Structural validation in `src/claudeutils/validation/learnings.py`. Three new checks added to existing `validate()` function.

**Files:** `src/claudeutils/validation/learnings.py`, `tests/test_validation_learnings.py`
**Baseline:** 7 existing tests, all passing. Precommit integration already wired in `src/claudeutils/validation/cli.py`.

---

## Cycle 1.1: When/How prefix required

**RED:**
- New test: `test_title_without_prefix_returns_error`
- Fixture: learnings file with `## Bad Title` after preamble
- Assert: `validate()` returns error containing prefix requirement + line number
- Expected failure: No prefix check in validate(), returns `[]`

**Verify RED:** `just test tests/test_validation_learnings.py::test_title_without_prefix_returns_error -v`

**GREEN:**
- Add prefix check in `validate()`: title must start with `When ` or `How to `
- Update 5 existing test fixtures to use prefixed titles while preserving their error conditions:
  - "Learning One" → "When learning one"
  - "Learning Two" → "When learning two"
  - "First Learning Title" → "When first learning"
  - "First Valid Title" → "When valid title"
  - Long title → `## When this title has way too many words for the validator`
  - Multiple errors fixture: update all titles to use prefixes while preserving word count and duplicate error conditions

**Verify GREEN:** `just test tests/test_validation_learnings.py -v`
**Verify no regression:** `just test -v`

**Stop/Error Conditions:**
- Existing test fixtures break after prefix check: update fixture titles per mapping above, don't remove error conditions they test

**Dependencies:** None (first cycle)

---
