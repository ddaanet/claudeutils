# Cycle 1.3

**Plan**: `plans/remember-skill-update/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Structural validation in `src/claudeutils/validation/learnings.py`. Three new checks added to existing `validate()` function.

**Files:** `src/claudeutils/validation/learnings.py`, `tests/test_validation_learnings.py`
**Baseline:** 7 existing tests, all passing. Precommit integration already wired in `src/claudeutils/validation/cli.py`.

---

## Cycle 1.3: Edge cases and combined validation

**RED:** Three new tests:
- `test_how_to_prefix_accepted` — `## How to encode paths` (2 content words) → passes (no errors)
- `test_how_without_to_rejected` — `## How encode` → prefix error (not `How to`)
- `test_combined_errors_reported` — file with `## When testing` (prefix OK, 1 content word → content error) and `## Bad` (prefix error) → both errors reported

**Verify RED:** `just test tests/test_validation_learnings.py -k "how_to or how_without or combined" -v`

**GREEN:**
- No implementation change required. Cycles 1.1-1.2 implement complete logic: prefix check rejects anything not starting with `When ` or `How to ` (covers `How encode`), content-word check covers all prefix-passing titles. Verify all 12 tests pass with no code changes.

**Verify GREEN:** `just test tests/test_validation_learnings.py -v`
**Verify no regression:** `just test -v`

**Stop/Error Conditions:**
- `test_how_to_prefix_accepted` passes immediately (no RED fail) → expected, this is a regression-guard test verifying existing logic accepts valid "How to" prefix

**Dependencies:** Cycles 1.1, 1.2 (edge cases validate the combined logic)

**Phase 1 Checkpoint:** `just precommit` — validates new checks propagate through CLI.

---

### Phase 2: Semantic Guidance + Pipeline Simplification (type: general, model: opus)

Prose edits to skills, agents, and CLAUDE.md. All decisions pre-resolved.

**Note:** SKILL.md also edited in Phase 3 (agent routing). Phase 3 depends on Phase 2 completion.

**Platform prerequisite:** Load `/plugin-dev:skill-development` before editing skill files.
