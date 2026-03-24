# Test Review: handoff-cli-tool (RC10 Layer 1)

**Date:** 2026-03-24
**Scope:** 21 test files, full-scope review
**Axes:** conformance, functional correctness, functional completeness, vacuity, excess, specificity, coverage, independence

## RC9 Fix Verification

| Finding | Status | File:Line | Evidence |
|---------|--------|-----------|----------|
| m-1: `match=` added to bare `pytest.raises(CleanFileError)` | VERIFIED | test_session_commit.py:257 | `pytest.raises(CleanFileError, match="no uncommitted changes")` |
| m-2: `match=` added to bare `pytest.raises(SessionFileError)` | VERIFIED | test_session_parser.py:146 | `pytest.raises(SessionFileError, match="not found")` |
| m-3: `match=` added to bare `pytest.raises(CalledProcessError)` | VERIFIED | test_commit_pipeline_errors.py:26 | `pytest.raises(subprocess.CalledProcessError, match="non-zero exit status")` |
| m-4: Redundant `len(…) > 0` removed from test_session_handoff.py | VERIFIED | test_session_handoff.py | No `len(...) > 0` patterns in file |
| m-5: Redundant `len(…) > 0` removed from test_session_parser.py | REGRESSION | test_session_parser.py:138 | `assert len(data.completed) > 0` still present |
| m-6: `HANDOFF_INPUT_FIXTURE` updated to `### ` heading format | VERIFIED | test_session_handoff.py:31 | Uses `### Handoff CLI tool design (Phase A)` |

5 of 6 RC9 test fixes verified. 1 regression: m-5 not applied.

## Findings

### Minor

[m-1] test_session_parser.py:138 — vacuity — `assert len(data.completed) > 0` is redundant. Subsequent assertion at line 139 (`data.in_tree_tasks[0].name == "Build parser"`) exercises the parsed data; the `any(...)` pattern used elsewhere is more specific. RC9 m-5 fix did not land.

[m-2] test_session_commit.py:217 — specificity — `pytest.raises(CleanFileError) as exc_info:` without `match=`. The test performs subsequent manual assertions on `err.clean_files` and `str(err)`, so it is not truly bare — but it lacks the `match=` pattern applied to the sibling at line 257 (RC9 m-1 fix). Bare raises without `match=` would pass on any CleanFileError, though the manual assertions mitigate this. Same class as prior m-1/m-2/m-3 findings, missed across 9 prior rounds.

[m-3] test_worktree_merge_errors.py:83 — specificity — `pytest.raises(subprocess.CalledProcessError) as exc_info:` without `match=`. Same pattern as the CalledProcessError fixed in test_commit_pipeline_errors.py. The manual assertion on `exc_info.value.stderr` provides some specificity, but `match=` would fail faster on wrong exception cause.

[m-4] test_session_status.py:280-298 — conformance — `SESSION_FIXTURE` module constant defined after its first usage at line 253. Forward reference works in Python but violates conventional top-of-module placement for test fixtures. Carried from RC8/RC9 (previously noted as "not counted").

[m-5] test_session_commit_pipeline.py:121-127 — specificity — `test_strip_hints_single_space_then_double` docstring says "Double-space lines after hint stay filtered after a single-space line" but the assertion `"continuation" not in result` is ambiguous — the word "continuation" could appear in the double-space line for any reason. The test verifies behavior correctly but the assertion string could match unrelated content if the test data changed.

[m-6] test_session_status.py:263 — coverage — `test_session_status_cli` assertion `"Next:" in result.output or "In-tree:" in result.output` is a disjunction. The design spec says `Next:` is suppressed when it duplicates the first in-tree task (single-task case not present here). The test should assert the specific expected section based on the fixture content (multi-task fixture should produce `In-tree:` with `▶` marker, not `Next:`).

[m-7] test_session_integration.py:34-35 — conformance — Integration test task `**Build widget**` has command `/design plans/widget/brief.md` but there is no `plans/widget/` directory created in the test setup. The status command reads plan states from filesystem. The test passes because missing plan directories produce empty state, but this means plan state rendering is untested in the integration path.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 7 |

**RC9 verification:** 5/6 verified, 1 regression (m-5 `len > 0` not removed from test_session_parser.py:138).

**New findings:** 6 new minors. Two are specificity issues with bare `pytest.raises` (m-2, m-3) that prior rounds fixed in sibling locations but missed here. One is a carried-forward fixture ordering issue (m-4). Three are test quality concerns: ambiguous assertion string (m-5), disjunctive assertion weakening specificity (m-6), and missing filesystem setup weakening integration coverage (m-7).

**Axes summary:**

| Axis | Status |
|------|--------|
| Conformance | 2 minors (m-4 fixture ordering, m-7 integration setup) |
| Functional correctness | Pass — tests verify actual git state and command output |
| Functional completeness | Pass — design sections (S-1 through S-5, H-1 through H-4, C-1 through C-5, ST-0 through ST-2) all have test coverage |
| Vacuity | 1 minor (m-1 redundant len check — RC9 regression) |
| Excess | Pass |
| Specificity | 3 minors (m-2, m-3 bare raises; m-6 disjunctive assertion) |
| Coverage | 1 minor (m-7 integration plan state untested) |
| Independence | Pass — no inter-test dependencies detected |
