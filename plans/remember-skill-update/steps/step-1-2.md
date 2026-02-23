# Cycle 1.2

**Plan**: `plans/remember-skill-update/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Structural validation in `src/claudeutils/validation/learnings.py`. Three new checks added to existing `validate()` function.

**Files:** `src/claudeutils/validation/learnings.py`, `tests/test_validation_learnings.py`
**Baseline:** 7 existing tests, all passing. Precommit integration already wired in `src/claudeutils/validation/cli.py`.

---

## Cycle 1.2: Min 2 content words after prefix

**RED:**
- New test: `test_insufficient_content_words_returns_error`
- Fixture: learnings file with `## When testing` (1 content word after prefix)
- Assert: `validate()` returns error mentioning content words + line number
- Expected failure: No content word count check, returns `[]`

**Verify RED:** `just test tests/test_validation_learnings.py::test_insufficient_content_words_returns_error -v`

**GREEN:**
- Strip prefix, count remaining words, require ≥2
- Implementation: if title starts with `How to `, content = words[2:]; if `When `, content = words[1:]. Check `len(content) < 2`.

**Verify GREEN:** `just test tests/test_validation_learnings.py -v`
**Verify no regression:** `just test -v`

**Stop/Error Conditions:**
- Content word count logic differs for "When" (1-word prefix) vs "How to" (2-word prefix) — verify both paths

**Dependencies:** Cycle 1.1 (prefix check must exist before content word check)

---
