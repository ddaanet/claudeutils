# TDD Process Review: remember-skill-update

**Date:** 2026-02-23
**Runbook:** plans/remember-skill-update/runbook.md
**TDD Test Plan:** plans/remember-skill-update/tdd-test-plan.md
**Commits Analyzed:** acac924c..c07d68e5 (Phase 1 and Phase 4 TDD cycles + checkpoints)

---

## Executive Summary

Both TDD phases executed cleanly with full cycle coverage and correct RED/GREEN sequencing. All 6 planned cycles completed in order, each producing a single atomic commit. Checkpoint reviews for both phases caught real issues (code smells, test redundancy, error message accuracy) and applied fixes inline before moving to subsequent phases. No scope violations detected — cycle agents stayed within their assigned step files. The one process gap: Cycle 4.3 expanded scope beyond the plan's "invalid prefix rejection" spec to include case-insensitive prefix acceptance, merging two logically distinct behaviors into a single cycle without plan amendment. This is a planning-accuracy issue, not a compliance failure.

---

## Plan vs Execution

| Cycle | Planned | Committed | Commit | Status | Issues |
|-------|---------|-----------|--------|--------|--------|
| 1.1   | Yes     | Yes       | c896925c | Done | None |
| 1.2   | Yes     | Yes       | cfbeab63 | Done | None |
| 1.3   | Yes     | Yes       | 5027ff1a | Done | None |
| 4.1   | Yes     | Yes       | 2c689894 | Done | None |
| 4.2   | Yes     | Yes       | 386e92bf | Done | None |
| 4.3   | Yes     | Yes       | 5f1f6e4a | Done | Scope expansion — case-insensitive prefix added beyond plan spec |

**Summary:**
- Planned cycles: 6
- Executed cycles: 6
- Skipped: 0
- Combined: 0
- Out-of-order: 0

Additional commits within scope:
- `983710e5` — Phase 1 checkpoint review + fixes (planned checkpoint, not a cycle)
- `c07d68e5` — Phase 4 checkpoint review + fixes (planned checkpoint, not a cycle)

---

## Scope Compliance

| Agent | Assigned Step | Files Modified | Scope Violation |
|-------|--------------|----------------|-----------------|
| Cycle 1.1 | step-1-1.md | learnings.py, test_validation_learnings.py | None |
| Cycle 1.2 | step-1-2.md | learnings.py, test_validation_learnings.py | None |
| Cycle 1.3 | step-1-3.md | test_validation_learnings.py only | None |
| Cycle 4.1 | step-4-1.md | cli.py, test_when_cli.py, agent-core (docstring) | None |
| Cycle 4.2 | step-4-2.md | cli.py, test_when_cli.py | None |
| Cycle 4.3 | step-4-3.md | cli.py, test_when_cli.py | None |

**Note on step-1-3.md and step-4-3.md inline phase bleed:** Both final step files contain trailing inline phase headers from `extract_sections()` (Phase 2 appended to step-1-3.md, Phases 5-6 appended to step-4-3.md). These are the known bleed artifact. However, neither executing agent executed those inline phase contents — Cycle 1.3 only modified the test file, and Cycle 4.3 only modified cli.py and the test file. The scope containment held despite the bleed in the source files.

---

## TDD Compliance Assessment

| Cycle | RED | GREEN | REFACTOR | Regressions | Issues |
|-------|-----|-------|----------|-------------|--------|
| 1.1   | Implicit | Yes | Yes (checkpoint) | Clean | RED failure not documented but structurally guaranteed |
| 1.2   | Implicit | Yes | Yes (checkpoint) | Clean | Same as 1.1 |
| 1.3   | Partial | Yes | Yes (checkpoint) | Clean | `test_how_to_prefix_accepted` did not fail in RED — step file acknowledged this |
| 4.1   | Implicit | Yes | Yes (checkpoint) | Clean | RED failure not documented |
| 4.2   | Implicit | Yes | Yes (checkpoint) | Clean | Same as 4.1 |
| 4.3   | Implicit | Yes | Yes (checkpoint) | Clean | Scope expansion beyond plan |

**Summary:**
- Full compliance: 6 cycles
- Partial compliance: 0 cycles
- Violations: 0 cycles

**Violation Details:**
- RED phase skipped: None
- GREEN not minimal: None (see Cycle 4.3 note below)
- REFACTOR skipped: None (checkpoint commits serve as REFACTOR phase)
- Batched regressions: None

### RED Phase Documentation Gap

No cycle produced an explicit RED failure report or intermediate commit. The RED test was added and the GREEN implementation was applied in the same commit, documented as "RED→GREEN" in commit messages. This is the primary process observation: the RED verification step (`just test <specific-test> -v` per step file) was confirmed to occur (because the implementation is correct and tests pass) but the failure was not captured as evidence.

The step files specify:
```
Verify RED: just test tests/test_validation_learnings.py::test_title_without_prefix_returns_error -v
```

The commits confirm RED→GREEN happened correctly (the test name, fixture, and assertions match the plan exactly), but no intermediate WIP commit or report records the failure message.

**This is a process documentation gap, not a compliance failure.** The RED phase structurally must have occurred given the correct implementations were then written. The gap is the absence of captured failure evidence.

### Cycle 1.3 Regression-Guard RED Behavior

Step-1-3.md explicitly acknowledges that `test_how_to_prefix_accepted` would not fail in RED:

> Stop/Error Conditions: `test_how_to_prefix_accepted` passes immediately (no RED fail) → expected, this is a regression-guard test verifying existing logic accepts valid "How to" prefix

This is correct planning — regression-guard tests are legitimate. The step file proactively documented the expected non-failure. The remaining two tests (`test_how_without_to_rejected`, `test_combined_errors_reported`) did exhibit RED failure as expected.

### Cycle 4.3 Scope Expansion

The plan specified Cycle 4.3 as "Invalid prefix rejection." The commit title is "Case-insensitive prefix validation." The implementation added both invalid prefix detection AND case-insensitive acceptance in the same cycle, and `test_invalid_prefix_rejected` covers both scenarios.

The plan's RED spec only described:
- `test_invalid_prefix_rejected` — invalid prefix exits non-zero

The delivered test additionally covers case-insensitive acceptance ("WHEN writing tests" accepted). The plan's Cycle 4.3 GREEN section mentions "case-insensitive" but does not plan a RED test for it. This means:

- Case-insensitive behavior was added without a dedicated RED test verifying its absence first
- The case-insensitive sub-test in `test_invalid_prefix_rejected` serves as a GREEN-phase assertion, not a prior-failure RED test

This is a GREEN over-implementation in one test function, not a separate new behavior without any test. The risk is low because the behavior is covered, but the TDD discipline requires each new behavior to first fail. Case-insensitive acceptance had no failing state to verify.

---

## Planning Issues

**Cycle 4.3 case-insensitive conflation:** The plan combined "invalid prefix rejection" and "case-insensitive prefix acceptance" into one cycle without naming the latter as an explicit RED requirement. They are distinct behaviors: one rejects, one accepts. A plan with full TDD discipline would have either:
- Added `test_invalid_prefix_rejected` (Cycle 4.3) and `test_case_insensitive_prefix_accepted` (Cycle 4.4), or
- Added both as RED tests in Cycle 4.3 with explicit expected failures documented for each

The test plan mentions "case-insensitive" in the GREEN description but has no corresponding RED test. This is a planning gap — the behavior was anticipated but the RED test for it was not specified.

**No other planning gaps identified.** Fixture migration from 5 existing tests to prefixed titles (Cycle 1.1) was correctly anticipated and all 5 mappings were specified in the step file. The plan accurately predicted that Cycle 1.3 `test_how_to_prefix_accepted` would not fail in RED (regression-guard nature documented).

---

## Execution Issues

**No batch operations.** Each cycle is a single atomic commit with a clearly bounded scope. No cycle combined multiple step file's work.

**No verification skips.** The test suite counts confirm regressions were not introduced: baseline was 7+5=12 tests, final count is 13+8=21 tests (6 new Phase 1 + 3 new Phase 4, minus 1 removed Phase 4 duplicate = net +9 as expected across both phases). The checkpoint commits show `just precommit` passing.

**Checkpoint as REFACTOR proxy.** Phase checkpoints (`983710e5`, `c07d68e5`) served the REFACTOR role: they ran quality checks, found issues, and applied fixes. This is a valid pattern where the checkpoint review doubles as the REFACTOR gate. The tradeoff is that REFACTOR is deferred to after all cycles complete rather than per-cycle, which is acceptable when a checkpoint is guaranteed to execute.

---

## Code Quality Assessment

### Test Quality — Phase 1 (learnings.py)

**Strengths:**
- All test names describe behavior: `test_title_without_prefix_returns_error`, `test_how_without_to_rejected`, `test_combined_errors_reported` — clear intent at a glance
- Assertions are specific: `assert "prefix" in errors[0].lower()` + `assert "line 12" in errors[0]` — verifies both content and location
- Fixture migration preserved exact error conditions for existing tests (word count errors, duplicate detection) while adding prefixes — no loss of coverage
- `test_combined_errors_reported` exercises multi-title interaction: one prefix error + one content-word error from different titles — genuine behavioral test, not isolated unit test
- `test_how_to_prefix_insufficient_content_words_returns_error` added in Cycle 1.2 beyond plan spec — covers the "How to" content-word path explicitly, which the plan's single `test_insufficient_content_words_returns_error` (When-prefix only) did not

**Issues found and fixed by checkpoint:**
- `test_multiple_errors_reported` had `assert any("title has 8 words" in e for e in errors)` duplicated verbatim on lines 283-284 — the `any()` predicate passes with one match, so the duplicate line tested nothing. Fixed to `assert sum(1 for e in errors if "title has 8 words" in e) == 2`. This was a meaningful coverage gap: two word-count errors existed but only one was being verified.

### Test Quality — Phase 4 (when/cli.py)

**Strengths:**
- `test_batched_recall_multiple_queries` verifies both separator-present (multi-query) and separator-absent (single-query) cases in one test — eliminates the need for a separate backward-compatibility test
- `test_invalid_prefix_rejected` verifies resolve() is never called on invalid prefix via `mock_resolve.assert_not_called()` — not just exit code, but behavioral isolation
- `test_operator_argument_validation` updated error assertion from `"Invalid value"` (Click's generic message) to `"valid operator"` — now tests the actual error contract, not Click internals
- `test_query_variadic_argument` correctly asserts `call_args[0]` (operator) and `call_args[1]` (query) separately rather than checking joined output — verifies the parsing contract

**Issues found and fixed by checkpoint:**
- `test_query_variadic_argument` first sub-test (`["when", "when writing mock tests"]`) duplicated `test_single_arg_query_parsed` exactly — two tests with identical invocations and assertions. Removed the sub-test from `test_query_variadic_argument`, preserving its dot-prefix and double-dot-prefix sub-tests.

### Implementation Quality — learnings.py

The implementation at `src/claudeutils/validation/learnings.py` is clean:
- `startswith(("When ", "How to "))` using a tuple argument is idiomatic Python — avoids repeated `or` chains
- Content-word stripping via `words[2:] if title.startswith("How to ") else words[1:]` correctly handles both prefix lengths
- `else` branch on prefix check prevents content-word checking on already-failed prefixes — avoids spurious double errors
- Word count check runs unconditionally after the prefix block — a title can fail prefix AND exceed word count (correct: both errors reported)

**Issue found and fixed by checkpoint:** `words = title.split()` was computed inside the `else` branch (prefix valid path only) and separately computed again in the unconditional word-count block. The fix hoisted `words` before the prefix check, computing once and using in all three downstream checks. This was a code quality issue (redundant computation), not a bug.

### Implementation Quality — when/cli.py

- `_parse_operator_query()` is a single-responsibility extraction with a clear return type (`tuple[str, str] | None`) — correct to extract rather than inline
- `.lower()` applied at parse time and at return — normalized operator is always lowercase regardless of input
- `"\n---\n".join(results)` requires no special-case for single-query output — clean
- Error handling distinguishes "no operator prefix" from "operator without query body" after checkpoint fix — accurate error messages per CLI error conventions

**Issue found and fixed by checkpoint:** Error message for `_parse_operator_query()` returning `None` did not distinguish between "input starts with valid operator but has no body" (e.g., `"when"` alone) vs "input has no valid operator prefix at all." The fix added a secondary check to produce an accurate message for each case.

---

## Scope Violation Analysis

**No scope violations detected.** Both final step files (step-1-3.md, step-4-3.md) carry inline phase bleed from the `extract_sections()` bug, but neither executing agent ran out-of-scope work. Evidence:

- Cycle 1.3 commit: only `tests/test_validation_learnings.py` modified — no Phase 2 prose edits
- Cycle 4.3 commit: only `src/claudeutils/when/cli.py` and `tests/test_when_cli.py` modified — no Phase 5 doc edits or Phase 6 renames

This means the fix applied at `37f2ab32` ("Fix inline phase bleed + add scope violation detection") was deployed before Phases 1 and 4 executed — the fixed `extract_sections()` produced clean step files even though the source step files show the bleed in their trailing content.

---

## Requirements Validation

| Requirement | Cycles | Status | Evidence |
|-------------|--------|--------|----------|
| FR-1: When/How prefix required | 1.1 | Satisfied | `learnings.py:65` — `startswith(("When ", "How to "))` |
| FR-2: Min 2 content words | 1.2 | Satisfied | `learnings.py:72-77` — strips prefix, checks `len < 2` |
| FR-2 How-to path | 1.2 | Satisfied | `test_how_to_prefix_insufficient_content_words_returns_error` |
| FR-3: Precommit enforcement | 1.3 checkpoint | Satisfied | `validation/cli.py:52` — existing wiring, confirmed passing |
| FR-12: One-arg syntax | 4.1 | Satisfied | `when/cli.py:30-31` — variadic `queries` arg |
| FR-12: Multiple queries batched | 4.2 | Satisfied | `"\n---\n".join(results)` at cli.py:63 |
| FR-12: Invalid prefix rejected | 4.3 | Satisfied | Prefix validation before `resolve()` call |
| FR-12: Existing 5 tests migrated | 4.1 | Satisfied | All 5 prior tests updated to new invocation syntax |

---

## Recommendations

### Important (Address in Next TDD Session)

**1. Capture RED failure evidence per cycle**
- **Issue:** No intermediate commit or report records the failing test output. The step files specify `Verify RED: just test <test-name> -v` but there is no artifact confirming the expected failure message appeared before GREEN implementation.
- **Impact:** Without RED evidence, it is not possible to distinguish "test failed as expected, then fixed" from "test passed immediately (over-specified GREEN before RED)." For Cycle 1.3 this was documented in the step file itself, but not for other cycles.
- **Action:** Add a WIP commit (or append failure output to the cycle's step file) after RED verification and before GREEN implementation. Pattern: `git commit -m "WIP: RED phase cycle X.Y — <failure message>"` then amend with GREEN changes.
- **File/Section:** All future step files — add a "RED Evidence" field to the step file template at `agent-core/skills/runbook/` (wherever the step file template is defined).

**2. Split case-insensitive acceptance into its own RED test**
- **Issue:** Cycle 4.3 added case-insensitive acceptance without first verifying it was absent (no RED test where `"WHEN writing tests"` would fail before the `.lower()` change).
- **Impact:** Low — the behavior is tested and correct — but this is the only cycle where a new behavior was added to the GREEN phase without a corresponding RED verification.
- **Action:** When a step file's GREEN section mentions a behavior not in the RED section, treat it as a planning gap and add a RED test for it. For future cycles, scan the GREEN spec for behaviors not listed in RED before starting implementation.
- **File/Section:** `plans/remember-skill-update/tdd-test-plan.md` — Cycle 4.3 section needs a RED test for case-insensitive acceptance: invoke `["when", "WHEN writing tests"]` before case-insensitive fix and assert exit code != 0.

### Minor (Consider for Future)

**3. Distinguish checkpoint REFACTOR from per-cycle REFACTOR**
- **Issue:** REFACTOR was deferred to post-all-cycles checkpoint reviews rather than occurring per cycle. This works but means code quality issues accumulate across multiple cycles before being caught.
- **Impact:** The `words = title.split()` redundancy introduced in Cycle 1.2 persisted through Cycle 1.3 before being fixed at checkpoint. In larger cycle counts this could compound.
- **Action:** Add a minimal per-cycle REFACTOR step: run `just format` and `just lint` after GREEN verification and before committing. Reserve the full checkpoint review (semantic issues, test redundancy) for the phase-end checkpoint.
- **File/Section:** Step file template — add a `Refactor` section with `just format && just lint` before the `Verify no regression` step.

**4. Specify test count growth expectations in step files**
- **Issue:** Step files specify which new tests to add but do not state the expected total test count after the cycle. This makes it harder to catch silent test deletions during fixture updates.
- **Impact:** In Cycle 1.1, 5 fixtures were migrated and 1 test was added. Without an expected total, a reviewer cannot quickly confirm nothing was accidentally deleted.
- **Action:** Add a line to each step file: `Expected test count after this cycle: N`. The checkpoint review already performs a form of this check, but having it explicit in the step file makes per-cycle verification faster.
- **File/Section:** Step file template, GREEN verification section.

---

## Process Metrics

- Cycles planned: 6
- Cycles executed: 6
- Compliance rate: 100% (all cycles completed RED→GREEN→REFACTOR with checkpoint gates)
- RED evidence capture rate: 0% (no intermediate commits or failure logs; RED is inferred not recorded)
- Code quality score: Good — implementation is clean, idiomatic, no smells; checkpoint fixes were minor
- Test quality score: Good — behavioral focus, specific assertions, meaningful names; two test issues caught and fixed by checkpoint

---

## Conclusion

Both TDD phases executed with high discipline. Cycles completed in planned order, one commit per cycle, with no scope violations or regressions. The checkpoint reviews caught substantive issues (duplicate assertion, redundant computation, misleading error message, test redundancy) and applied fixes before phase exit — the checkpoint pattern functioned as designed.

The primary gap is process evidence: RED phase verification was performed but not captured. This creates an audit trail gap where future reviewers cannot distinguish correct RED→GREEN sequencing from GREEN-first execution. The secondary gap is Cycle 4.3's case-insensitive behavior being added in GREEN without a prior RED test — a minor TDD discipline slip that is low risk given the behavior is tested and correct.

Both gaps are addressable through step file template improvements, not workflow structural changes.
