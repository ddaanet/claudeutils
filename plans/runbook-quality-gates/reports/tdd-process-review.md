# TDD Process Review: runbook-quality-gates

**Date:** 2026-02-18
**Runbook:** plans/runbook-quality-gates/runbook-phase-{1..5}.md
**Commits Analyzed:** a847c344..ed064571 (13 TDD cycles, 5 checkpoint/vet commits)

## Executive Summary

The execution completed all 13 planned cycles across 5 phases and produced a working `validate-runbook.py` with 17 passing tests. TDD discipline was followed for RED/GREEN verification in every cycle. The principal recurring issue is GREEN over-implementation: 3 of 13 cycles (2.1, 3.1, 4.1) implemented the next cycle's violation-detection logic as part of the happy-path GREEN, collapsing two distinct RED/GREEN rounds into one and causing the following cycle's RED to pass unexpectedly. Cycle execution order deviated from plan for Phase 4 (4.1 → 4.3 → 4.2 instead of 4.1 → 4.2 → 4.3). The stop condition in Cycle 3.2 was handled correctly and resolved by a clean refactor commit. Vet reviews at each phase checkpoint caught real issues (report format, false positive in ambiguous classification, lifecycle double-violation).

## Plan vs Execution

| Cycle | Planned | Executed | Status | Issues |
|-------|---------|----------|--------|--------|
| 1.1   | Yes     | Yes      | ✓      | None |
| 1.2   | Yes     | Yes      | ✓      | None |
| 1.3   | Yes     | Yes      | ✓      | None |
| 2.1   | Yes     | Yes      | ✓ (over-impl) | GREEN implemented Cycle 2.3's duplicate-creation detection |
| 2.2   | Yes     | Yes      | ✓      | None |
| 2.3   | Yes     | Yes      | RED passed unexpectedly | Caused by 2.1 over-implementation; documented and continued |
| 3.1   | Yes     | Yes      | ✓ (over-impl) | GREEN implemented Cycle 3.2's mismatch detection |
| 3.2   | Yes     | Yes      | ✓ (stop condition) | Stop condition triggered (432-line limit); resolved by refactor commit |
| 3.3   | Yes     | Yes      | ✓      | None |
| 4.1   | Yes     | Yes      | ✓ (over-impl) | GREEN implemented Cycle 4.2's violation detection (no cycle ID in message) |
| 4.2   | Yes     | Yes, out of order | Executed 3rd (plan: 2nd) | Swapped with 4.3 |
| 4.3   | Yes     | Yes, out of order | Executed 2nd (plan: 3rd) | Swapped with 4.2 |
| 5.1   | Yes     | Yes      | ✓      | None |

**Summary:**
- Planned cycles: 13
- Executed cycles: 13
- Skipped: 0
- Combined: 0
- Over-implemented (RED passed): 3 (2.3, caused by 2.1; 3.2's mismatch detection pre-implemented by 3.1; 4.2's violation partially pre-implemented by 4.1)
- Out-of-order: 2 (4.2 and 4.3 swapped)

## TDD Compliance Assessment

| Cycle | RED | GREEN | REFACTOR | Regressions | Issues |
|-------|-----|-------|----------|-------------|--------|
| 1.1   | ✓   | ✓     | ✓        | N/A (first)  | None |
| 1.2   | ✓   | ✓     | ✓ (lint) | 2/2 pass    | None |
| 1.3   | ✓   | ✓     | ✓ (lint) | 3/3 pass    | None |
| 2.1   | ✓   | Over-impl | ✓ (lint) | 4/4 pass | GREEN implements duplicate-create check (Cycle 2.3 scope) |
| 2.2   | ✓   | ✓     | ✓        | 5/5 pass    | None |
| 2.3   | RED passed | N/A | ✓ (lint) | 6/6 pass | RED passed due to 2.1 over-impl; documented; correct continuation decision |
| 3.1   | ✓   | Over-impl | ✓ (lint) | 7/7 pass | GREEN implements mismatch comparison (Cycle 3.2 scope) |
| 3.2   | ✓   | ✓     | Stop condition | 8/8 pass | 432-line file triggers stop; resolved by dedicated refactor commit |
| 3.3   | ✓   | ✓     | ✓ (lint) | 9/9 pass    | None |
| 4.1   | ✓   | Over-impl | ✓     | 10/10 pass  | GREEN implements violation detection (Cycle 4.2 scope, no cycle ID in message) |
| 4.2   | ✓ (partial) | ✓ | ✓    | 11/11 pass  | RED "failed" only on cycle ID format, not on absence of violation detection |
| 4.3   | ✓   | ✓     | ✓        | 12/12 pass  | Executed before 4.2 (out of plan order) |
| 5.1   | ✓   | ✓     | ✓ (file split) | 17/17 pass | Integration test file extracted during REFACTOR |

**Summary:**
- Full compliance (correct RED→GREEN with no over-impl): 9 cycles (1.1, 1.2, 1.3, 2.2, 3.2, 3.3, 4.2, 4.3, 5.1)
- Over-implementation (GREEN pre-implements next cycle): 3 cycles (2.1, 3.1, 4.1)
- RED passed unexpectedly: 1 cycle (2.3, caused by 2.1)
- Out-of-order execution: 2 cycles (4.2, 4.3)

**Violation Details:**
- RED phase passed unexpectedly: 2.3
- GREEN not minimal (over-implementation): 2.1, 3.1, 4.1
- REFACTOR skipped: 0
- Batched regressions: 0

## Planning Issues

**VALID_TDD fixture count inconsistency:**
- Common Context (runbook-phase-1.md:47) specified "All 1 tests pass" but the VALID_TDD fixture required two test functions (`test_foo`, `test_bar`) to satisfy all four subcommand checks simultaneously. The executor corrected the fixture at Cycle 3.1. The vet checkpoint for Phase 3 then updated the Common Context to match. This was a planning defect (the cross-phase VALID_TDD spec was not validated against the fixture plan), resolved cleanly at execution time.

**Phase 4 cycle ordering:**
- The runbook specified 4.1 (happy path) → 4.2 (violation) → 4.3 (ambiguous). Execution ran 4.1 → 4.3 → 4.2. The execution report documents 4.3 before 4.2 but records them as 4.2 and 4.3 in swapped order. Both passed cleanly. The reordering is benign (no inter-cycle dependency between 4.2 and 4.3) but is an unexplained deviation from plan.

**GREEN over-implementation pattern (systemic):**
- Cycles 2.1, 3.1, and 4.1 are all happy-path cycles where the plan explicitly called for the violation branch to be deferred to the next cycle. In all three cases the executor implemented both the happy path and the violation detection in the same GREEN pass. This is a recurring pattern, not an isolated incident. The runbook's GREEN phase descriptions for happy-path cycles read: "Write PASS report, exit 0" — without an explicit "do not implement the violation branch." The absence of a prohibition left space for the executor to over-implement.

**Cycle 4.2 RED diagnosis:**
- The execution report states Cycle 4.2's RED failed because the cycle ID was missing from the violation message (`assert "1.1" in content` failed), not because violation detection was absent. This means the RED boundary was effectively the violation message format, not the violation detection itself. While the test ultimately failed for the right reasons (content assertion), the failure type was narrower than planned. This is a consequence of 4.1 over-implementation.

## Execution Issues

**Over-implementation (Cycles 2.1, 3.1, 4.1):**

- **Cycle 2.1:** `check_lifecycle` added the `elif is_create` branch (duplicate-create detection). The runbook's 2.1 GREEN description says "No violations if all first occurrences are 'create'... Write PASS report, exit 0" — no duplicate detection needed. The `elif is_create` branch was Cycle 2.3's scope.
- **Cycle 3.1:** `check_test_counts` added the `if claimed != actual` comparison and violation-append logic. The runbook's 3.1 GREEN description says "If no checkpoints, no violations. Write PASS report." Mismatch detection was Cycle 3.2's scope.
- **Cycle 4.1:** `check_red_plausibility` added the full `import_err_pattern` matching and `violations.append()` logic. The runbook's 4.1 GREEN description says "Write PASS report, exit 0." Clear-violation detection was Cycle 4.2's scope.

In each case the over-implementation was caught because the following cycle's RED still found something to fail on: Cycle 2.3 found nothing (RED passed — the over-implementation was complete); Cycle 3.2 found the missing violation append (partial — mismatch detection was present but name-listing was absent); Cycle 4.2 found the missing cycle ID in the violation message (partial).

**Stop condition handling (Cycle 3.2):**
- The 432-line stop condition was correctly raised, documented, and resolved by a clean standalone refactor commit (`d677ac8b`) that moved fixture constants to `tests/fixtures/validate_runbook_fixtures.py`. The commit is structurally separate from any GREEN implementation. This is textbook handling.

**Out-of-order Phase 4:**
- Cycles 4.2 and 4.3 were executed in reversed order (4.3 before 4.2) relative to the plan. The execution report records them in this reversed order as well. The reordering did not cause regressions — both passed with correct regression counts. No explanation for the reordering appears in the execution report or commit messages. Since 4.2 and 4.3 have no dependency between them, functional correctness was preserved.

## Code Quality Assessment

**Test Quality:**

- Test names are descriptive and behavior-focused (`test_lifecycle_modify_before_create`, `test_red_plausibility_ambiguous`). Each name describes the scenario, not the implementation.
- Assertions are specific: tests assert exit codes AND report content (result line, specific file paths, counts, exact strings like `"1.1"` and `"1.2"`). No vacuous `assert x` patterns observed.
- `monkeypatch.setattr(sys, 'argv', [...])` + `main()` invocation correctly exercises the full production path. Vet checkpoint 1 caught the raw `sys.argv = [...]` mutation and fixed it.
- `tmp_path` + `monkeypatch.chdir` correctly isolates each test's report output. No cross-test file system contamination.
- Fixtures are constant strings (not separate .md files), clear in intent, minimal. Fixture names match the Common Context plan exactly.
- Parametrized test for skip flags (`test_integration_skip_flag`) correctly covers all 4 subcommands with a single test body.
- Integration test extraction to `test_validate_runbook_integration.py` resolved the line-limit stop condition cleanly and kept test files under 400 lines.

**Implementation Quality:**

- `_is_artifact_path` cleanly separates classification from violation logic — correct single-responsibility structure.
- `write_report` correctly handles all result states (PASS, FAIL, AMBIGUOUS, SKIPPED) from a single function, parameterized by violations/ambiguous lists.
- `created_names` accumulation in `check_red_plausibility` correctly populates after the RED check for each cycle (not before), satisfying the D-7 constraint that current cycle's own GREEN is invisible to that cycle's RED.
- `re.sub(r'\[.*?\]$', '', name)` for parametrized test normalization is minimal and correct.
- `setdefault` used for `created_names` dict accumulation — avoids overwriting first-seen cycle ID.

**Code Smells / Issues Found:**

- **Ambiguous false-positive condition (fixed by final vet):** `"." not in name` in `check_red_plausibility` triggered ambiguous classification for any single-word stem in `created_names`, regardless of whether it appeared in the failure text. Real runbooks would generate false positives. This was a logic error introduced in Cycle 4.3's GREEN and caught by the final vet review. Fix: removed `or "." not in name`.
- **`AMBIGUOUS_RED_PLAUSIBILITY` fixture backtick wrapping:** The fixture's failure text had backtick-wrapped `ValueError` (`\`ValueError\``), which caused the regex to stop at the backtick and not capture "widget" from the failure description. This prevented the ambiguous case from being correctly triggered. The fix was to unwrap the backtick in the fixture (final vet report `tests/fixtures/validate_runbook_fixtures.py:279`). The fixture defect meant the Cycle 4.3 GREEN test had a weak assertion that happened to pass despite the false-positive condition.
- **Global vs accumulated test count in `check_test_counts`:** The implementation checks each checkpoint claim against the global (total document) test count, not the count accumulated up to that checkpoint. For multi-phase runbooks with mid-document checkpoints, this produces false violations. Noted by vet-review as a deferral (current fixtures only use end-of-document checkpoints). Not a blocking issue but worth tracking.
- **Double-violation for modify-before-create followed by corrective create (fixed by final vet):** `check_lifecycle` generated two violation entries when a file was first seen as Modify (violation 1) and later as Create (incorrectly flagged as duplicate creation — violation 2). Fix applied in final vet.

## Recommendations

### Critical (Address Before Next TDD Session)

1. **Add explicit "Do NOT implement violation branch" guard to happy-path GREEN descriptions**
   - **Issue:** Three consecutive happy-path GREENs (2.1, 3.1, 4.1) over-implemented by adding violation logic from the next cycle. The runbook descriptions did not prohibit this; they described the happy-path behavior without bounding the implementation scope.
   - **Impact:** Over-implementation collapses two TDD cycles into one, removing the incremental RED→GREEN discipline that TDD is designed to enforce. When the following cycle's RED happens to detect residual gaps (missing message format, missing name list), the failure is on format rather than functionality — a weaker test.
   - **Action:** In the runbook's GREEN Phase description for happy-path cycles, add an explicit scope bound. Example addition to Cycle 2.1 GREEN: "Implement `check_lifecycle` with first-occurrence tracking only. Do not add the violation or duplicate-creation detection branches — those are Cycles 2.2 and 2.3." This follows the same pattern as the "Changes" section listing explicit file targets.
   - **File/Section:** `plans/runbook-quality-gates/runbook-phase-{2,3,4}.md` — GREEN Phase descriptions for cycles 2.1, 3.1, 4.1. The pattern applies to any future happy-path cycle preceding a violation-detection cycle.

### Important (Address Soon)

2. **Document Phase 4 cycle order deviation in execution report**
   - **Issue:** Cycles 4.2 and 4.3 were executed in reversed order relative to the runbook plan (4.3 before 4.2). The execution report records them in swapped sequence without explanation. This is a silent deviation.
   - **Impact:** If cycles had had a dependency (e.g., if 4.3 relied on 4.2's violation-tracking infrastructure), the reorder would have caused incorrect REDs. In this case correctness was preserved by coincidence.
   - **Action:** Add a note to the execution report under Cycle 4.2 or 4.3 explaining the order deviation: reason (executor judgment), and confirmation that no inter-cycle dependency exists between them. Establish a convention that out-of-order execution requires explicit justification in the execution report.
   - **File/Section:** `plans/runbook-quality-gates/reports/execution-report.md` — Phase 4 section.

3. **Fix VALID_TDD cross-phase spec before plan execution begins**
   - **Issue:** The VALID_TDD fixture's test count was specified as "All 1 tests pass" in Common Context but required "All 2 tests pass" to satisfy the two test functions (`test_foo`, `test_bar`) already present in the fixture. This was caught and fixed at Cycle 3.1 execution time.
   - **Impact:** The correction required updating the VALID_TDD fixture and the Common Context mid-execution. While handled cleanly, mid-execution spec corrections risk silently invalidating earlier cycles' assumptions if the fixture is shared across phases.
   - **Action:** During runbook expansion review, validate that VALID_TDD cross-phase specs are internally consistent: count the test function names listed in the fixture plan against the checkpoint claim. This check is mechanical and could be a preparation-runbook.py validation step or a checklist item in plan-reviewer.
   - **File/Section:** `plans/runbook-quality-gates/runbook-phase-1.md` — Common Context `VALID_TDD` specification block.

### Minor (Consider for Future)

4. **Track mid-document checkpoint accumulation in `check_test_counts`**
   - **Issue:** `check_test_counts` compares each checkpoint claim against the total test count for the full document, not the count accumulated up to that checkpoint's position. For runbooks with multiple intermediate checkpoints (e.g., "All 2 tests pass" at Phase 1 end, "All 5 tests pass" at Phase 3 end), the Phase 1 checkpoint would be checked against the Phase 3 total and incorrectly flag as a violation.
   - **Impact:** No current test exercises this — all fixtures use end-of-document checkpoints. Will produce false violations when the tool is used on real multi-phase runbooks with per-phase checkpoints.
   - **Action:** Refactor `check_test_counts` to process document sequentially: maintain a running `test_names` set and check each checkpoint claim against the count at that document position, then continue accumulating. Add a test fixture with two checkpoints at different positions.
   - **File/Section:** `agent-core/bin/validate-runbook.py` — `check_test_counts` function (~lines 167–189).

5. **Add cycle-order boundary note to refactor commit convention**
   - **Issue:** The fixture-extraction refactor commit (`d677ac8b`) was placed between Cycles 3.2 and 3.3 — correctly outside any cycle's RED/GREEN boundary. This was good judgment, but the pattern is implicit.
   - **Action:** Document in the TDD execution protocol (runbook-phase-1.md Common Context or the tdd-task agent) that standalone refactor commits (not WIP amendments) are allowed between cycles when stop conditions are resolved and are distinct from cycle commits. The current protocol only mentions "WIP commit amended to final" — standalone refactor commits needed for structural fixes are not explicitly covered.
   - **File/Section:** `plans/runbook-quality-gates/runbook-phase-1.md` — Common Context "TDD Protocol" section; or `.claude/agents/runbook-quality-gates-task.md`.

## Process Metrics

- Cycles planned: 13
- Cycles executed: 13
- RED failed as expected: 11 (correct RED discipline)
- RED passed unexpectedly: 1 (Cycle 2.3 — over-implementation consequence)
- RED partially failed (format only, not functionality): 1 (Cycle 4.2)
- Compliance rate: 69% (9/13 cycles with no over-implementation and correct RED failure)
- Over-implementation rate: 23% (3/13 GREEN phases exceeded their cycle scope)
- Stop conditions raised and resolved correctly: 1 (Cycle 3.2)
- Vet reviews conducted: 5 (Phases 1–4 checkpoints + final)
- Vet issues found across reviews: 9 (2 minor Phase 1, 3 Phase 2, 2 Phase 3, 0 Phase 4, 4 final) — all FIXED or DEFERRED, 0 UNFIXABLE
- Code quality score: Good (clean structure, correct abstractions, 2 logic bugs caught by vet)
- Test quality score: Good (behavior-focused names, specific assertions, proper test isolation)

## Conclusion

The execution demonstrates sound TDD fundamentals: RED was verified before GREEN in all cycles, regressions were tracked per cycle, REFACTOR was run after every GREEN, and stop conditions were handled correctly. The dominant process failure is a recurring over-implementation pattern in happy-path GREENs: when the runbook specifies "exit 0 for valid input," the executor consistently also implemented the violation-detection branch scheduled for the next cycle. This is not random drift — it occurred in 3 of the 4 subcommand happy-path cycles and indicates that the GREEN phase descriptions for happy-path cycles need explicit scope bounds ("do not implement X") to counteract the executor's tendency toward completeness. The vet checkpoint system worked effectively, catching logic errors (ambiguous false-positive, double-violation) that tests did not. Adding explicit negative scope constraints to GREEN phase descriptions in happy-path cycles is the highest-priority improvement before the next TDD execution.
