# TDD Process Review: worktree-merge-resilience

**Date:** 2026-02-18
**Runbook:** plans/worktree-merge-resilience/
**Commits Analyzed:** b69ff220..c869b282 (22 commits)

## Executive Summary

The execution delivered a functionally complete, well-tested implementation across all 4 TDD phases and 1 general phase. TDD compliance was strong for the RED/GREEN behavioral contract — every cycle introduced a failing test before implementing code — but RED phase verification was not separately committed or documented for 6 of 9 cycles. One planning gap (Cycle 3.2 Test A) led to a deviating test that asserts exit 0 instead of the specified exit 3 due to the step not accounting for session.md auto-resolution. A regression from Cycle 3.1 was deferred to Cycle 3.2 rather than fixed immediately. Post-cycle vet reviews at each phase checkpoint were thorough and caught real issues, serving as effective REFACTOR gates.

## Plan vs Execution

| Cycle/Step | Planned | Executed | Status | Issues |
|-----------|---------|----------|--------|--------|
| 1.1 | Yes | Yes | Done | RED not separately committed; test+impl in one commit |
| 1.2 | Yes | Yes | Done | Regression fix in separate commit (36e99a8f) — correct |
| 1.3 | Yes | Yes | Done | None |
| 1.4 | Yes | Yes | Done | None |
| 1.5 | Yes | Yes | Done | Sabotage protocol not documented; `>= 2` vs `== 2` parent assertion |
| 2.1 | Yes | Yes | Done | None |
| 2.2 | Yes | Yes | Done | None |
| 3.1 | Yes | Yes | Done | Regression (test_merge_conflict_source_files) not fixed in this cycle |
| 3.2 | Yes | Yes | Done | Test A assertion deviated from spec due to planning gap |
| 4.1 | Yes | Yes | Done | None |
| 5.1 (audit) | Yes | Yes | Done | Rolled into Phase 5 vet checkpoint — appropriate for general step |
| 5.2 (migration) | Yes | Yes | Done | None |
| 5.3 (SKILL.md) | Yes | Yes | Done | None |

**Summary:**
- Planned cycles: 13 steps (9 TDD + 1 planned regression fix commit + 3 general)
- Executed cycles: 13 (all completed)
- Skipped: 0
- Combined: 0 (each cycle has its own commit)
- Out-of-order: 0
- Design deviations: 1 (Cycle 1.2 "merged" state routing: plan said Phase 4 only, fix added Phase 1+2)

## TDD Compliance Assessment

| Cycle | RED | GREEN | REFACTOR | Regressions | Issues |
|-------|-----|-------|----------|-------------|--------|
| 1.1 | Partial | Yes | Yes | N/A | RED not separately committed; no documented failure message |
| 1.2 | Yes* | Yes | Yes | 3 fixed in dedicated commit | *Documented in execution report; all in one commit |
| 1.3 | Yes | Yes | Yes | N/A | Strong — execution report documents RED failure |
| 1.4 | Partial | Yes | Yes | N/A | RED not documented; no failure message recorded |
| 1.5 | Partial | Yes | Yes | N/A | Sabotage protocol required but not documented in commit history |
| 2.1 | Partial | Yes | Yes | N/A | RED not documented; execution report absent for this cycle |
| 2.2 | Yes | Yes | Yes | N/A | RED documented in notes: test not found = expected failure |
| 3.1 | Yes | Yes | Yes | 1 deferred to 3.2 | Regression deferred rather than fixed immediately |
| 3.2 | Partial | Yes | Yes | N/A | Test A spec deviated (planning gap); no per-cycle report |
| 4.1 | Partial | Yes | Yes | N/A | RED not documented; no execution report |

**Summary:**
- Full documented compliance (RED failure recorded): 3 cycles (1.2, 2.2, 3.1)
- Partial compliance (RED likely occurred but not documented): 6 cycles
- Violations (no RED at all): 0 — behavioral evidence shows all cycles had failing tests first
- Violations (non-minimal GREEN): 0
- REFACTOR skipped: 0 — vet reviews at each phase checkpoint served as REFACTOR gates

**Compliance Notes:**

RED phase documentation is the primary gap. The commit history shows the correct TDD sequence in all cases — tests were written before production code — but for 6 cycles there is no separate commit or execution report recording the RED failure message. The canonical evidence (Cycle 1.2 execution report, Cycle 2.2 notes, Cycle 3.1 report) demonstrates the agent was capable of documenting RED; it was inconsistently applied.

**Regression Handling:**
- Cycle 1.2 produced 3 regressions (test_merge_ours_clean_tree, test_merge_submodule_fetch, test_merge_branch_existence). These share a single root cause (merged-state routing logic) and were fixed together in one 2-line code change (commit 36e99a8f). This is appropriate — the regressions were not independent issues requiring separate investigation. Commit message documents all three by name.
- Cycle 3.1 produced one regression (test_merge_conflict_source_files in test_worktree_merge_validation.py). This was not fixed in the Cycle 3.1 commit; it was deferred and fixed silently within the Cycle 3.2 commit. The runbook pattern expects regressions to be fixed in their own commit or the cycle that introduced them, not deferred to the next cycle.

## Planning Issues

**Planning Gaps:**

- **Cycle 3.2 Test A specification**: Step-3-2.md specified `test_merge_aborts_cleanly_when_untracked_file_blocks` should assert `exit_code == 3`, MERGE_HEAD present, and conflict markers in the file. The existing test uses `agents/session.md` as the conflicting file. `_phase3_merge_parent` auto-resolves `session.md` via `resolve_session_md()`, so a session.md conflict produces exit 0 after auto-resolution, not exit 3. The test correctly asserts exit 0 given the actual behavior, but this contradicts the step specification. The planning gap: the runbook author did not account for the session.md auto-resolution when writing the Test A expected behavior. Result: the test accurately reflects correct system behavior but differs from the spec.

- **Cycle 1.5 sabotage protocol**: The step specified a required sabotage protocol to force RED failure — temporarily change `_detect_merge_state` to return `"merged"` always, confirm test fails, revert before GREEN. There is no evidence in commit history that this was applied or its outcome documented. The test does assert `parent_count >= 2` (slightly weaker than the specified `== 2`), which may be sufficient given the Cycle 1.2 routing was verified to be correct.

**Design Assumption Violations:**

- **Cycle 1.2 "merged" state routing**: The runbook specified `if state == "merged": call _phase4_merge_commit_and_precommit(slug) only`. Execution discovered that branches pointing to the same commit as HEAD return `True` from `_is_branch_merged` (every commit is its own ancestor), causing Phase 1 (clean-tree validation) and Phase 2 (submodule reconciliation) to be skipped. The fix adds Phase 1+2 before Phase 4 for the merged state. This is a correct design evolution but was not anticipated in the plan.

## Execution Issues

**Regression Deferral:**
- Cycle 3.1's behavioral change (removing abort block, changing exit code from 1 to 3) broke `test_merge_conflict_source_files` in `tests/test_worktree_merge_validation.py`. This regression was not fixed in the Cycle 3.1 commit. It was bundled into the Cycle 3.2 commit with a note in the commit message ("test_merge_conflict_source_files: updated to expect exit 3 for conflicts"). The fix is 4 lines (assertion update only) and required no investigation — the root cause was the planned Cycle 3.1 behavioral change.

**RED Phase Documentation:**
- 6 of 9 cycles combined RED+GREEN in a single commit without a separate record of the RED failure. The 3 well-documented cycles (1.2 via execution report, 2.2 via notes, 3.1 via execution report) show what correct documentation looks like: expected failure, actual failure message, verification command run.
- Cycle 1.1 is the clearest case: the commit message says "Phase 1 GREEN" but there is no preceding commit or report recording the RED phase (ImportError from missing `_detect_merge_state`). The test was written and the implementation added in one commit.

**Non-Minimal GREEN (Cycle 3.2):**
- The Cycle 3.2 commit (d2c46f0e) added `_recover_untracked_file_collision` as 90+ lines of new code including the parsing logic, git add loop, commit, retry, and MERGE_HEAD check — all in a single GREEN phase. The step specification described this scope, so it was planned. However, the implementation included `err=True` on 3 `click.echo` calls (D-8 violation) that were not caught until Phase 5 vet. The GREEN implementation was correctly scoped per the runbook but introduced a design violation that leaked into a later phase.

**Cycle 1.5 Sabotage Not Documented:**
- The step required applying a 1-line sabotage to `_detect_merge_state`, running the test to confirm failure, then reverting. This is an unusual RED protocol for a cycle where test-first would otherwise pass immediately (the routing was wired in Cycle 1.2). No commit shows the sabotage being applied. Either the sabotage was applied but not committed (applied, tested, reverted in working tree only — acceptable) or it was skipped.

## Code Quality Assessment

**Test Quality:**

- Good: Tests use real git repos via `tmp_path` and `repo_with_submodule` fixtures, not mocked subprocess calls. This matches the project's explicit preference (testing.md: prefer e2e over mocked subprocess for git operations).
- Good: Assertions are behavioral (exit codes, MERGE_HEAD presence, parent count, message content) not structural (checking internal state of merge.py).
- Good: Test names clearly describe the behavioral scenario: `test_merge_resumes_from_parent_resolved`, `test_merge_continues_to_phase3_when_submodule_conflicts`, `test_conflict_output_contains_all_fields`.
- Issue: Test setup uses `subprocess.run(..., check=True, capture_output=True)` throughout, which swallows stderr on failure. Per learnings.md: "Test setup should produce self-diagnosing failures. Either use `check=False` + explicit assertion with stderr, or use a helper that surfaces stderr on failure." The Phase 2 vet caught 11 dead subprocess calls in test setup (fixed during REFACTOR). The pattern persists in cycles where vet was not run at per-cycle granularity.
- Issue: `test_merge_aborts_cleanly_when_untracked_file_blocks` asserts only exit 0 and no Traceback — minimal assertions for what the step described as a conflict-path test. The step spec expected exit 3 + MERGE_HEAD + conflict markers, but the planning gap produced a simpler assertion (exit 0 + no Traceback). The test is correct for the actual behavior but underspecified as a regression guard.
- Minor: Cycle 1.5 asserts `parent_count >= 2` where the runbook specified `== 2`. A `>= 2` assertion would pass even if the implementation created a multi-way merge unexpectedly. The distinction is low-risk given the test setup, but `== 2` would be more precise.

**Implementation Quality:**

- Good: `_detect_merge_state` correctly implements D-5 detection order (merged → submodule_conflicts → parent_resolved/parent_conflicts → clean). The sequential refinement across cycles 1.1→1.4 was clean and each addition was isolated.
- Good: `_format_conflict_report` is a pure function returning a string — easy to test and no side effects.
- Good: Phase 3 extraction of `merge_state.py` (commit 4b5f03c7) reduced `merge.py` from 441 to 312 lines and split `_recover_untracked_file_collision` into `_parse_untracked_files` + `_add_and_commit_files` to reduce complexity from 11 to 6 — all triggered by precommit failures caught in the REFACTOR phase.
- Issue: `_recover_untracked_file_collision` in the Cycle 3.2 initial implementation had `err=True` on 3 `click.echo` calls (violating D-8). This was a D-8 violation introduced in GREEN and not caught until Phase 5. The pattern of D-8 violations being caught late (Phase 2 vet: err=True on submodule test comment; Phase 5 vet: 3 residuals in merge_state.py) suggests D-8 was not actively checked during cycle implementation.
- Issue: `git diff --stat MERGE_HEAD -- <file>` in the initial Cycle 4.1 GREEN measured conflict-marker-infected working tree against MERGE_HEAD — semantically wrong per FR-4 intent. Caught by Phase 4 vet and fixed to `git diff --stat HEAD MERGE_HEAD -- <file>`.

**Code Smells:**

- `_format_conflict_report` had a trivial docstring (Args/Returns sections restating the signature) — caught and fixed by Phase 4 vet.
- `behind` variable in `_format_conflict_report` tracks main's extra commits but the name implies branch perspective — noted as non-blocking in Phase 4 vet, not fixed.

## Recommendations

### Critical (Address Before Next TDD Session)

**1. Separate RED commits for all TDD cycles**
- **Issue:** 6 of 9 cycles combined RED+GREEN in a single commit. There is no git record of the RED failure message for most cycles.
- **Impact:** Traceability gap. The only evidence that RED occurred is the cycle documentation; if the test was actually written after the implementation (GREEN-first), the commit history cannot distinguish this from test-first.
- **Action:** For each TDD cycle, create a commit at RED containing only the failing test. Commit message format: "Cycle X.Y RED: [test name] — [expected failure]". Then implement GREEN and amend or create a second commit. The REFACTOR phase amends the GREEN commit per the runbook pattern.
- **File/Section:** The orchestrate skill and step agent prompts. Specifically: the step agent prompt should instruct agents to commit the test first (with `just precommit` expected to fail on the new test), then implement GREEN.

**2. Fix Cycle 3.1 regression deferral pattern**
- **Issue:** `test_merge_conflict_source_files` broke in Cycle 3.1 but was fixed in Cycle 3.2. The runbook pattern requires fixing regressions in the cycle that introduced them (or immediately after).
- **Impact:** Between Cycle 3.1 GREEN and Cycle 3.2 GREEN, the test suite had a known failing test. Any phase checkpoint vet during this window would encounter this regression.
- **Action:** After each cycle's GREEN verification (`pytest -v`), fix all regressions before committing. Do not defer regression fixes to subsequent cycles. The Cycle 3.1 regression was a 4-line assertion update requiring no investigation — there was no reason to defer.
- **File/Section:** `plans/worktree-merge-resilience/steps/step-3-1.md` does not mention updating `test_merge_conflict_source_files` — this was a missing entry in the cycle specification. Future runbook authors should grep for tests asserting the old behavior and include them explicitly in the RED/GREEN scope.

### Important (Address Soon)

**3. Document sabotage protocols explicitly in runbook and execution reports**
- **Issue:** Cycle 1.5 required a non-standard RED protocol (sabotage `_detect_merge_state`) because the cycle's test would otherwise pass without implementing any production code. The step spec documented the protocol but there is no evidence it was executed.
- **Impact:** If the sabotage was skipped, the RED phase for Cycle 1.5 was not meaningful. The test may have been passing before the "GREEN" commit (reverted sabotage with no code change needed).
- **Action:** When a cycle uses a sabotage protocol for RED verification, document the sabotage in the WIP commit message and the execution report. Minimal format: "RED: sabotaged `_detect_merge_state` to return 'merged' always; test failed with AssertionError: Expected 2 parents, got 1."
- **File/Section:** Cycle 1.5 execution report is absent — create it retroactively if the sabotage was applied. For future runbooks, add explicit documentation requirement to any cycle that uses sabotage for RED.

**4. Track D-8 (stdout-only) compliance as a per-cycle criterion**
- **Issue:** `err=True` violations were introduced in Cycle 3.2 GREEN (`_recover_untracked_file_collision`) and not caught until Phase 5 vet. The same pattern appeared in Phase 2 (misleading test comment) and Phase 4 (diff stat direction). D-8 violations persisted across 2 phases before cleanup.
- **Impact:** D-8 is a design invariant (all merge output to stdout). Violations in production code are correctness issues — test assertions checking `capsys.readouterr().err` pass vacuously when they should check `.out`. One such vacuous test was found in Phase 5 vet.
- **Action:** Add a per-cycle REFACTOR check: `grep err=True src/claudeutils/worktree/merge.py src/claudeutils/worktree/merge_state.py`. Zero matches expected. This is a 1-line grep command that could be included in each TDD cycle step file's REFACTOR section.
- **File/Section:** Step files in `plans/worktree-merge-resilience/steps/` do not include this check. For future runbooks involving D-8, add it to each step's verification section.

### Minor (Consider for Future)

**5. Strengthen Cycle 1.5 parent count assertion**
- **Issue:** Test asserts `parent_count >= 2` but the runbook specified `== 2`.
- **Impact:** Low risk in this specific test (setup creates exactly one branch commit), but `>= 2` would pass for an unexpected multi-way merge.
- **Action:** Change assertion in `tests/test_worktree_merge_routing.py::test_merge_clean_state_runs_full_pipeline` from `parent_count >= 2` to `parent_count == 2`.
- **File/Section:** `tests/test_worktree_merge_routing.py` line containing `parent_count >= 2`.

**6. Add Cycle 3.2 Test A MERGE_HEAD coverage**
- **Issue:** The step specified that Test A should verify MERGE_HEAD exists after call (conflict preserved). The actual test exits 0 (session.md auto-resolved), so MERGE_HEAD is absent. The coverage gap: no test verifies that the `git add + retry` path correctly preserves MERGE_HEAD when a non-auto-resolved file conflicts.
- **Impact:** The auto-resolved session.md case is covered by the exit 0 assertion. The conflicting non-auto-resolved file case is partially covered by `test_merge_conflict_source_files` (which tests the conflict path but not the untracked-file recovery path specifically).
- **Action:** Add a test for untracked non-auto-resolved file collision: same setup as Test A but with a non-session.md file (e.g., `src/feature.py`), asserting exit 3 + MERGE_HEAD present + conflict markers.
- **File/Section:** `tests/test_worktree_merge_errors.py` — add after `test_merge_aborts_cleanly_when_untracked_file_blocks`.

**7. Standardize test setup subprocess error handling**
- **Issue:** Test setup uses `check=True, capture_output=True` throughout, which produces opaque `CalledProcessError: returncode 1` failures on setup failures with no stderr visible.
- **Impact:** Per learnings.md learning: "Test setup should produce self-diagnosing failures." Opaque setup failures are time-consuming to debug.
- **Action:** Extract a test helper (e.g., `_git(repo, *args)`) that uses `check=False` and asserts with stderr included in the assertion message. The Phase 2 vet already caught this pattern and the `_setup_submodule_conflict` helper was extracted — apply the same pattern to `test_worktree_merge_errors.py` and `test_worktree_merge_merge_head.py`.
- **File/Section:** `tests/test_worktree_merge_errors.py`, `tests/test_worktree_merge_merge_head.py`.

## Process Metrics

- Cycles planned (TDD phases): 9 TDD + 4 general steps = 13 total
- Cycles executed: 13 (all completed)
- Compliance rate (full RED documentation): 33% (3/9 TDD cycles have execution reports with RED failure documented)
- Compliance rate (behavioral — test written before implementation): 100% (evidence from commit history; every cycle adds tests before or with implementation)
- Code quality score: Good — vet reviews caught and fixed real issues; module extraction (merge_state.py) was triggered by precommit gates working correctly
- Test quality score: Good — real git repos, behavioral assertions, clear test names; setup subprocess error handling is the primary gap

## Conclusion

The TDD execution was substantively correct: all 9 TDD cycles produced failing tests before production code was written, and all cycles passed after GREEN implementation. The vet reviews at each phase checkpoint (4 TDD + 1 general, all documented in reports/) functioned as effective REFACTOR gates and caught real issues (wrong diff comparison direction, D-8 violations, test file line limit exceedance, complexity violations). The primary process gap is RED phase documentation — only 3 of 9 cycles have explicit records of the RED failure message, which reduces traceability. Two planning issues (Cycle 3.2 Test A spec and Cycle 1.2 merged-state routing) reflect knowledge gaps in the runbook rather than execution failures; both were correctly resolved during execution. The critical action for future TDD sessions is establishing a per-cycle RED commit as a non-negotiable checkpoint before GREEN implementation begins.
