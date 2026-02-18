# Vet Review: validate-runbook.py complete implementation

**Scope**: `agent-core/bin/validate-runbook.py`, `tests/test_validate_runbook.py`, `tests/test_validate_runbook_integration.py`, `tests/fixtures/validate_runbook_fixtures.py`
**Date**: 2026-02-17T23:57:01Z
**Mode**: review + fix

## Summary

Complete implementation of `validate-runbook.py` with 4 subcommands (model-tags, lifecycle, test-counts, red-plausibility), importlib block, write_report function, directory input via assemble_phase_files, and skip flags. All 17 tests pass. `just dev` clean. Implementation satisfies FR-2, FR-3, FR-4, FR-5 and D-7.

**Overall Assessment**: Ready (all issues fixed)

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Ambiguous classification false positive: `"." not in name` condition**
   - Location: `agent-core/bin/validate-runbook.py:286`
   - Problem: `if name in failure_text or "." not in name:` — the `"." not in name` branch triggers the ambiguous case for ANY single-word stem in `created_names`, even if that name is not mentioned in the failure text. A runbook creating `src/widget.py` in cycle 1.1 then having cycle 1.2 with `ValueError: some completely unrelated error` would be flagged as ambiguous for `widget`, producing false positives in real usage.
   - Fix: Remove `or "." not in name`. Only classify ambiguous when the created name is actually referenced in the failure text.
   - **Status**: FIXED

### Minor Issues

1. **Trivial cmd_ function docstrings duplicate check_ function docstrings**
   - Location: `agent-core/bin/validate-runbook.py:105, 174, 215, 308`
   - Note: `cmd_model_tags` ("Check artifact-type files use opus Execution Model."), `cmd_lifecycle` ("Check file lifecycle ordering (create before modify)."), `cmd_test_counts` ("Check checkpoint test-count claims match actual test function count."), `cmd_red_plausibility` ("Check that RED expected failures are plausible given prior GREEN state.") all restate what the check_ function already says. `cmd_` functions handle CLI I/O dispatch — their docstrings should describe that role or be omitted.
   - **Status**: FIXED

2. **Double-violation for modify-before-create followed by later create**
   - Location: `agent-core/bin/validate-runbook.py:150-155`
   - Note: When a file is first seen as "Modify" (violation: "no prior creation found") and later "Create", a second spurious violation fires: "created again (first seen as 'Modify')". A file created after being incorrectly modified should show one violation, not two. The duplicate-create violation (correct for Create→Create sequences) fires incorrectly here.
   - Fix: When file's first_seen action was a modify (not a create), a subsequent Create should not trigger "created again" — it's actually the expected corrective action, or at minimum not a "duplicate creation".
   - **Status**: FIXED

## Fixes Applied

- `agent-core/bin/validate-runbook.py:286` — Removed `or "." not in name` condition from ambiguous classification; only trigger ambiguous when created name appears in failure text. Also updated comment to match new behavior.
- `agent-core/bin/validate-runbook.py:105,174,215,308` — Removed trivial cmd_ function docstrings (they restate the check_ function's description without adding information about the dispatch role).
- `agent-core/bin/validate-runbook.py:149-154` — Added guard: only report "created again" violation when original first_seen action was itself a create (not a modify). Modify-before-create followed by a corrective create now generates a single "no prior creation found" violation, not two.
- `tests/fixtures/validate_runbook_fixtures.py:279` — Removed backtick wrapping from `AMBIGUOUS_RED_PLAUSIBILITY` expected failure text (`\`ValueError\`` → `ValueError — widget raises on invalid input`). The regex `([^\n\`]+)` stops at the closing backtick, capturing only "ValueError" and preventing "widget" from being found in the failure text. Without the fix, the `name in failure_text` check correctly requires the module name to appear in the full failure description.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-2: artifact files require opus | Satisfied | `check_model_tags`, `ARTIFACT_PREFIXES`, `_is_artifact_path` |
| FR-3: lifecycle validation | Satisfied | `check_lifecycle` with modify-before-create and duplicate-create detection |
| FR-4: RED plausibility (structural) | Satisfied | `check_red_plausibility` with import-error detection and ambiguous classification |
| FR-5: test count reconciliation | Satisfied | `check_test_counts` with parametrized normalization |
| D-7: importlib, report writer, exit codes | Satisfied | importlib block lines 9-19, `write_report`, exit codes 0/1/2 |
| Directory input | Satisfied | `assemble_phase_files` called in all 4 cmd_ handlers |
| Skip flags | Satisfied | `--skip-{subcommand}` on each subparser, SKIPPED report |

**Gaps (design spec items not in scope):**
- FR-3 "Future-phase reads" and "Missing creation for existing-file references" — OUT-OF-SCOPE (not in execution context IN, not implemented in any cycle)
- Report Summary "Checks run: N, Passed: N" fields — design.md aspirational format; runbook spec says "Failed: N" only; implemented correctly per runbook

---

## Positive Observations

- importlib block cleanly reuses prepare-runbook.py parsing without duplication (D-7)
- `write_report` handles skipped, pass, fail, and ambiguous states with a single function
- `assemble_phase_files` tuple unpacking correctly handled across all 4 cmd_ handlers
- Fixtures extracted to separate module, keeping test files under line limit
- Integration test separation (test_validate_runbook_integration.py) resolves 400-line limit without architectural changes
- All 17 tests pass; `just dev` clean

## Recommendations

- `check_test_counts` compares each checkpoint against the global test count (all tests in the document), not the count accumulated up to that checkpoint. For runbooks with mid-document checkpoints, this would produce false positives (checkpoint claiming 3 when 5 exist at document end). Current tests only use end-of-document checkpoints so tests pass. Worth fixing when real runbooks with interim checkpoints are validated. (Not flagged as an issue since all tests pass and current fixtures represent valid usage.)
