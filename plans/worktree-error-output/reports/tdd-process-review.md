# TDD Process Review: worktree-error-output

**Date:** 2026-02-23
**Runbook:** plans/worktree-error-output/runbook.md
**Commits Analyzed:** a097b114..b7fcb340 (12 commits)

## Executive Summary

The worktree-error-output execution completed all 5 planned steps and achieved the design requirements: `_fail()` is defined, `err=True` is absent, and `derive_slug` ValueError is caught cleanly. TDD discipline for Phases 1 and 2 was largely followed, with one notable compliance issue: lint errors introduced at the GREEN commit required a separate fix commit before the REFACTOR phase, indicating the GREEN phase was committed in a broken state. Phase 3 (general steps) was executed correctly with appropriate post-hoc checkpoint reviews. Two minor scope issues were found: trailing phase headers in step files were present but caused no agent overrun. Recommendations focus on preventing broken GREEN commits and aligning execution artifacts with the 5-step runbook plan.

## Plan vs Execution

| Step | Planned | Executed | Status | Issues |
|------|---------|----------|--------|--------|
| Cycle 1.1 | Yes | Yes | Partial | GREEN commit had lint errors; required separate fix commit before REFACTOR |
| Cycle 2.1 | Yes | Yes | Done | Clean execution |
| Step 3.1 | Yes | Yes | Done | Missed 2 pre-existing echo+exit sites (clean_tree, merge); caught by checkpoint |
| Step 3.2 | Yes | Yes | Done | Clean — 4 warning sites removed in single commit |
| Step 3.3 | Yes | Partial | Done | No dedicated Step 3.3 commit or report; validation absorbed into Phase 3 checkpoint |

**Summary:**
- Planned steps: 5
- Executed steps: 5 (all)
- Skipped: 0
- Combined: Step 3.3 absorbed into Phase 3 checkpoint — no standalone report
- Out-of-order: 0

**Unplanned commits:**
The following commits were not anticipated in the runbook:
- `561efa87` — Cycle 1.1 execution report committed separately (after GREEN, before lint fix)
- `1100569d` — Fix Cycle 1.1 lint errors (broken GREEN state required correction)
- `b519b2ca` — Phase 1 checkpoint review + fixes (extra REFACTOR artifact)
- `cf95eab8` — Phase 2 checkpoint review (extra review artifact)
- `74d4b037` — Phase 3 checkpoint: converted 2 additional missed sites
- `b7fcb340` — Final review report + `_fail()` keyword arg fix (extra REFACTOR artifact)

The runbook specified a single commit per cycle; actual execution required 3 commits for Cycle 1.1 and produced post-phase checkpoint reviews not called for in the plan.

## Scope Compliance

| Step File | Trailing Content | Agent Output | Scope Violation |
|-----------|-----------------|--------------|-----------------|
| step-1-1.md (line 71) | `### Phase 2: ValueError catch...` header | Only cli.py + test_worktree_utils.py changed | No — trailing header present but not executed |
| step-2-1.md (line 67) | `### Phase 3: Drop err=True...` header | Only cli.py + test_worktree_new_creation.py changed | No — trailing header present but not executed |

The `extract_sections()` fix (commit `eb12d9c9`) was merged before this runbook was created, so the trailing phase headers in step files were inert. The haiku agents correctly scoped their work to their assigned cycle. No scope violations detected.

## TDD Compliance Assessment

| Step | RED | GREEN | REFACTOR | Regressions | Issues |
|------|-----|-------|----------|-------------|--------|
| Cycle 1.1 | Partial | Broken | Yes | N/A | RED verified per report; GREEN committed with lint errors (F821, PLC0415) requiring a separate fix commit |
| Cycle 2.1 | Yes | Yes | Yes | None | Clean — RED confirmed exit code 1 with traceback; GREEN achieved exit code 2 clean |
| Step 3.1 | N/A | Yes | Yes | 1 test updated | Missed 2 pre-existing sites; checkpoint caught and fixed |
| Step 3.2 | N/A | Yes | N/A | None | Clean 4-site removal |
| Step 3.3 | N/A | N/A | N/A | N/A | Step absorbed into Phase 3 checkpoint — no discrete execution artifact |

**Summary:**
- Full compliance: 1 cycle (Cycle 2.1)
- Partial compliance: 1 cycle (Cycle 1.1 — broken GREEN)
- General steps executed correctly: 2 (Steps 3.1, 3.2)
- Violations: 1

**Violation Details:**

**Broken GREEN commit (Cycle 1.1):**

Commit `a097b114` (GREEN) was committed without running `just precommit`. It contained:
- `F821`: `Never` name used in `_fail()` return type but `from typing import Never` not imported at that point
- `PLC0415`: `from claudeutils.worktree.cli import _fail` placed inside the test functions instead of at module top-level

Commit `1100569d` was required to fix these before the REFACTOR checkpoint could run. The runbook specifies "Verify GREEN" with `pytest`, but the cycle also expected `just test` for regression. A pre-commit hook or lint-first-run discipline would have caught these before the commit.

The report for Cycle 1.1 was also written before the lint fix (`561efa87` precedes `1100569d`), meaning the report recorded the cycle as "COMPLETE" before the implementation was actually in a clean state.

**Step 3.1 missed sites:**

Commit `763b670d` converted 7 of 9 echo+exit pairs. The 2 missed sites (`clean_tree` and `merge`) were pre-existing echo+raise patterns not using `err=True`, so they were not in the runbook's grep target (`err=True | SystemExit`). The checkpoint review (`74d4b037`) correctly identified and fixed them. This is a planning gap (Step 3.1 scoped by `err=True` sites only, missing pre-existing patterns), not an execution error.

## Planning Issues

**Planning gaps:**

- Step 3.1 table listed 7 `err=True + SystemExit` pairs. Two additional echo+exit sites in `clean_tree()` and `merge()` used `click.echo()` + `raise SystemExit(1)` without `err=True` — these were out-of-scope for the grep-based discovery but should have been converted for `_fail()` consistency. The design requirement was "consolidate echo+exit pairs," not only `err=True` ones. The Phase 3 checkpoint review caught this, but Step 3.1 should have explicitly included these sites.

- No Step 3.3 report was produced. The precommit validation step was executed implicitly as part of the Phase 3 checkpoint but left no discrete artifact. The runbook called for `just precommit` as a standalone step with a standalone report.

**Design assumption validation:**

- Runbook anticipated `from typing import Never` was not yet imported. Correct — it wasn't. The assumption held.
- Runbook anticipated `capsys` would be needed only for `test_fail_writes_to_stdout`. The agent added `capsys` to all three tests initially, then the checkpoint removed it from the two that didn't use it. Minor deviation caught by review.
- Runbook note said initial `_fail(str(e), code=2)` in GREEN. Agent wrote it as `code=2` keyword form; final review standardized to positional. Minor style deviation, correctly resolved.

## Execution Issues

**Broken GREEN commit:**

Cycle 1.1's GREEN commit (`a097b114`) was committed without running lint checks. The runbook specified `just test` for regression verification but the implicit contract for TDD GREEN is that the implementation is syntactically and lint-clean before commit. The agent ran `pytest` (tests passed) but did not run `just precommit` or even `just lint`. This required a correction commit (`1100569d`) in the sequence:

```
a097b114  GREEN (broken — lint errors)
561efa87  Report (written against broken state)
1100569d  Fix lint errors
b519b2ca  REFACTOR checkpoint
```

The report was written after the broken GREEN but before the fix, recording the cycle as complete when it was not.

**Checkpoint reviews not in plan:**

Four checkpoint review artifacts were created (checkpoint-1, checkpoint-2, checkpoint-3, review.md) not specified in the runbook. These added value — each found and fixed real issues — but represent unplanned work. The pattern of an orchestrator adding checkpoint reviews after each phase is good practice that should be formalized in the runbook template.

**Step report committed without implementation:**

`561efa87` (cycle 1.1 report) was committed at 16:36:28, the same second as `a097b114` (GREEN). The report was committed while the implementation was still broken (lint failures discovered at `1100569d` at 16:38:40). The report states "Verification: GREEN Phase ✓ All 3 tests pass" which was accurate for pytest but not for the full quality gate.

## Code Quality Assessment

**Test Quality:**

- `test_fail_writes_to_stdout` is the strongest test: asserts exit code, stdout content, and explicit stderr emptiness. This directly encodes the key design invariant.
- `test_fail_default_code` and `test_fail_custom_code` are appropriately minimal — exit code only, no output assertion needed for those behaviors.
- `test_new_invalid_task_name_clean_error` uses four assertions covering exit code, positive output content, and two negative content checks (no Traceback, no ValueError). The negative assertions are good regression guards.
- Initial tests had local imports inside test functions (fixed by lint). Final tests have correct module-level imports.
- Unused `capsys` fixtures in two tests were caught and removed by checkpoint review.

**Implementation Quality:**

- `_fail()` is 3 lines: clean, readable, minimal. `Never` return type is correct.
- ValueError catch in `new()` is correctly scoped to the `if task_name:` block — only path that calls `derive_slug`.
- Multi-line echo extraction to local `msg` variable (per Step 3.1 spec) was applied correctly at 3 sites.
- `_fail(str(e), code=2)` keyword-argument inconsistency was minor but correctly resolved by final review.

**Code Smells:**

- None introduced by this change. The `_fail()` helper reduced repetition across 10 call sites.

**Post-phase checkpoint reviews:**

The four checkpoint reviews added genuine value:
- Checkpoint 1 caught unused `capsys` and narrating docstring.
- Checkpoint 2 found nothing (clean cycle).
- Checkpoint 3 caught 2 missed echo+exit sites and performed a lifecycle audit.
- Final review caught the `code=` keyword inconsistency.

The lifecycle audit in checkpoint 3 was particularly thorough — it traced temp file cleanup paths and verified no exit-0 with active error state.

## Recommendations

### Critical (Address Before Next TDD Session)

1. **Run `just lint` or `just precommit` before GREEN commit**
   - **Issue:** Cycle 1.1 GREEN was committed with `F821` (undefined name `Never`) and `PLC0415` (local import). Tests passed but lint failed.
   - **Impact:** Broken GREEN commits corrupt the TDD cycle — the report is written against a broken state, and a correction commit breaks the one-commit-per-cycle invariant.
   - **Action:** Add to step file GREEN verification sequence: run `just lint` before `just test`. Or change the GREEN verification command to `just check && just test` instead of `pytest` alone.
   - **File/Section:** `plans/worktree-error-output/runbook.md` — Verify GREEN sections for both TDD cycles. Also update the runbook template at `agent-core/skills/runbook/SKILL.md` to include lint in the GREEN verification sequence.

### Important (Address Soon)

2. **Formalize checkpoint reviews in the runbook**
   - **Issue:** Four checkpoint reviews added significant value but were not planned. When not planned, their scope and timing is ad-hoc.
   - **Impact:** Checkpoint reviews caught: unused fixtures, missed echo+exit sites, keyword arg inconsistency. These would have shipped without checkpoint reviews.
   - **Action:** Add an explicit post-phase checkpoint step after each TDD phase and after general Phase 3 completion. Specify: reviewer model, scope (changed files + design anchoring), and output location.
   - **File/Section:** Runbook template in `agent-core/skills/runbook/SKILL.md` — add checkpoint step pattern to phase boundary documentation.

3. **Step 3.1 scope should include all echo+exit pairs, not just `err=True` ones**
   - **Issue:** Step 3.1 scoped discovery by `grep "err=True"`, missing 2 pre-existing `click.echo()` + `raise SystemExit(1)` sites without `err=True`.
   - **Impact:** Required an unplanned Phase 3 checkpoint commit to fix missed sites.
   - **Action:** When a step goal is "all echo+exit pairs use `_fail()`", the discovery grep should be `grep "raise SystemExit"` not `grep "err=True"`. Update the step spec to include: `grep -n "raise SystemExit\|err=True" src/claudeutils/worktree/cli.py` as the inventory command.
   - **File/Section:** `plans/worktree-error-output/steps/step-3-1.md` — verification grep. And `plans/worktree-error-output/runbook.md` Step 3.1 Validation section.

### Minor (Consider for Future)

4. **Commit report after fix, not alongside broken state**
   - **Issue:** Cycle 1.1 report (`561efa87`) was committed at the same timestamp as the broken GREEN (`a097b114`), recording COMPLETE before lint was clean.
   - **Impact:** Execution report is inaccurate — lists GREEN as passing when the full gate had not passed.
   - **Action:** Step agent should write the report as the final action, after all verification including lint. The report should be committed in the same commit as the implementation (or after fixes are applied). Add to reporting protocol: "Write report only after `just test` AND `just lint` pass."
   - **File/Section:** Step file execution protocol — add lint check before report write step.

5. **Produce a Step 3.3 artifact**
   - **Issue:** Step 3.3 (precommit validation) was absorbed into the Phase 3 checkpoint with no standalone report.
   - **Impact:** No record of when `just precommit` passed for this execution.
   - **Action:** Step 3.3 agent should produce `plans/worktree-error-output/reports/step-3-3-report.md` recording: command run, output summary, pass/fail, and timestamp.
   - **File/Section:** `plans/worktree-error-output/steps/step-3-3.md` — add report write instruction.

## Process Metrics

- Cycles planned: 2 (TDD) + 3 steps (general) = 5 total
- Cycles executed: 5 (all)
- Planned commits: 5 (one per step)
- Actual commits: 12 (extra fix, report, and checkpoint commits)
- Compliance rate: 50% (1 of 2 TDD cycles with clean RED/GREEN/REFACTOR — Cycle 1.1 had broken GREEN)
- Code quality score: Good — minimal helper, correct types, good test coverage
- Test quality score: Good — behavioral assertions, direct invariant testing, negative guards; initial lint issues corrected

## Conclusion

The execution achieved its design goals: all `err=True` sites eliminated, `_fail()` helper in place, `ValueError` caught cleanly. The primary process failure was the Cycle 1.1 GREEN commit containing lint errors, which required a correction commit and produced an inaccurate execution report. The checkpoint review pattern (unplanned but valuable) caught additional missed sites and style inconsistencies. The most impactful runbook template change would be adding `just lint` to the GREEN verification sequence, preventing broken-state commits from occurring. The checkpoint review pattern should be formalized as a post-phase step rather than remaining ad-hoc.
