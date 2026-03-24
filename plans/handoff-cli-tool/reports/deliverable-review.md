# Deliverable Review: handoff-cli-tool (RC10)

**Date:** 2026-03-24
**Methodology:** agents/decisions/deliverable-review.md
**Approach:** Layer 1 (three opus agents: code, test, prose+config) + Layer 2 (interactive cross-cutting)

## Inventory

| Type | Files | + | - | Net |
|------|-------|---|---|-----|
| Code | 26 | +1744 | -95 | +1649 |
| Test | 20 | +3535 | -59 | +3476 |
| Agentic prose | 2 | +9 | -6 | +3 |
| Configuration | 2 | +2 | -2 | +0 |
| **Total** | **50** | **+5290** | **-162** | **+5128** |

### RC9 Finding Verification

| RC9 Finding | Status | Evidence |
|-------------|--------|----------|
| M-1: `vet_check` path resolution (commit_gate.py:164-165) | FIXED | `root = Path(cwd or ".")` and `matched_paths = [root / f ...]` |
| m-1: Bare `pytest.raises(CleanFileError)` (test_session_commit.py:257) | FIXED | `pytest.raises(CleanFileError, match="no uncommitted changes")` |
| m-2: Bare `pytest.raises(SessionFileError)` (test_session_parser.py:146) | FIXED | `pytest.raises(SessionFileError, match="not found")` |
| m-3: Bare `pytest.raises(CalledProcessError)` (test_commit_pipeline_errors.py:26) | FIXED | `pytest.raises(subprocess.CalledProcessError, match="non-zero exit status")` |
| m-4: Redundant `len(…) > 0` (test_session_handoff.py) | FIXED | No `len(...) > 0` patterns in file |
| m-5: Redundant `len(…) > 0` (test_session_parser.py:57) | FIXED | Specific instance at line 57 removed |
| m-6: `HANDOFF_INPUT_FIXTURE` bold-colon format (test_session_handoff.py:31) | FIXED | Uses `### Handoff CLI tool design (Phase A)` heading format |
| m-7: `step_reached` vestigial field (handoff/pipeline.py) | FIXED | `HandoffState` has only `input_markdown` and `timestamp` |
| m-8: `_AGENT_CORE_PATTERNS` hardcoded submodule name (commit_gate.py:143) | CARRIED | Deferred per design C-1 |
| m-9: `_git_output` docstring (commit_gate.py:34-39) | FIXED | Porcelain-safety warning added |
| m-10: `format_commit_output` unconditional append (commit_pipeline.py:234) | FIXED | `if parent_output:` guard |

10 of 10 fixable RC9 findings verified fixed. m-8 correctly carried forward.

## Critical Findings

None.

## Major Findings

**M-1: `load_state()` crashes on pre-m-7 state files** — handoff/pipeline.py:44-45
- Axis: robustness (code)
- `load_state()` uses `HandoffState(**data)` to deserialize from JSON. RC9 m-7 removed `step_reached` from `HandoffState`. Pre-existing state files (written before the fix, persisting in `tmp/.handoff-state.json` after a mid-pipeline crash) still contain `step_reached` → `TypeError: unexpected keyword argument`. State files persist across sessions — this is a legitimate recovery path.
- Fix: filter `data` to `HandoffState.__dataclass_fields__` before unpacking, or catch `TypeError` and clear corrupt state.
- Layer: Layer 1 code agent

**M-2: Handoff CLI missing session.md existence check** — handoff/cli.py
- Axis: error signaling (code), conformance (S-3)
- `handoff_cmd` calls `overwrite_status(session_path, ...)` and `write_completed(session_path, ...)` without validating `session_path` exists. If session.md is missing, `FileNotFoundError` propagates as an unhandled exception with Python traceback. Status CLI handles this identically-situated error gracefully (status/cli.py:55-56: `try/except OSError → _fail(msg, code=2)`). Same gap applies to `ValueError` from missing headings in `overwrite_status` and `_write_completed_section`.
- Violates S-3: "All output to stdout as structured markdown — results, diagnostics, AND errors."
- Fix: wrap pipeline calls in try/except, route through `_fail(msg, code=2)`.
- Layer: Layer 2 cross-cutting

## Minor Findings

### Code Robustness

1. **m-1: Submodule CleanFileError paths lack repo context** (commit_pipeline.py:269-273, error signaling)
   - `_partition_by_submodule` strips submodule prefix (line 107). When `validate_files` raises `CleanFileError` for submodule files, error message shows paths relative to submodule root (`fragments/foo.md`) instead of full paths (`agent-core/fragments/foo.md`).

2. **m-2: `overwrite_status` regex replacement vulnerable to backreferences** (handoff/pipeline.py:75, robustness)
   - `re.subn(replacement, text)` where replacement includes `status_text` from user input. If status_text contains `\g<1>` or `\1`, `re.subn` interprets them as backreferences. Low probability (status lines are prose) but violates defensive coding principle. Fix: use function callback for replacement.

3. **m-3: `_build_repo_section` heading/content gap** (git_cli.py:32, functional correctness)
   - `header + "\n\n".join(parts)` — header `"## Parent\n"` runs directly into first part with no blank line. Markdown heading without separator. Output is machine-consumed, so rendering impact is minimal.

4. **m-4: Blocker dependency edges overly conservative** (status/render.py:118, robustness)
   - `_build_dependency_edges` joins all blocker groups into one string and checks task name substring membership. Two tasks mentioned in unrelated blocker entries are falsely marked dependent. Functionally safe (prevents parallelism that might be valid, never allows unsafe parallelism).

5. **m-5: `list_plans` uses relative path** (status/cli.py:67, robustness)
   - `list_plans(Path("plans"))` assumes cwd = project root. Consistent with session file and `_is_dirty()` — all three make the same assumption. Not defensively coded but matches the CLI invocation context (skills run from project root).

### Test Specificity

6. **m-6: Redundant `len(data.completed) > 0` assertion** (test_session_parser.py:138, vacuity)
   - Same class as RC9 m-4/m-5 (fixed at other locations). This instance was not in the RC9 report — different test function (`test_parse_session_full` vs parametrized test at line 57).

7. **m-7: Bare `pytest.raises(CleanFileError)` without `match=`** (test_session_commit.py:217, specificity)
   - Same class as RC9 m-1. The test has manual assertions on `err.clean_files` and `str(err)` at lines 221-223, but lacks the `match=` pattern applied to the sibling at line 257.

8. **m-8: Bare `pytest.raises(CalledProcessError)` without `match=`** (test_worktree_merge_errors.py:83, specificity)
   - Same class as RC9 m-3. Manual stderr assertions follow (lines 86-89) but `match=` would tighten the initial catch.

9. **m-9: Ambiguous assertion string** (test_session_commit_pipeline.py:121-127, specificity)
   - `"continuation" not in result` — the word could match unrelated content if test data changed. Test verifies correct behavior but assertion string is fragile.

10. **m-10: Disjunctive assertion weakens specificity** (test_session_status.py:263, specificity)
    - `"Next:" in result.output or "In-tree:" in result.output` — passes if either is present. Design spec defines when each appears; test should assert the specific expected section.

### Test Coverage

11. **m-11: Integration test references nonexistent plan directory** (test_session_integration.py:34-35, coverage)
    - Task `**Build widget**` references `/design plans/widget/brief.md` but no `plans/widget/` exists in test setup. Test passes because missing plans produce empty state — plan state rendering is untested in the integration path.

### Code Style (Extraction Regressions)

12. **m-12: Un-parenthesized except clauses** (worktree/cli.py:104,176, conformance)
    - `except FileNotFoundError, subprocess.CalledProcessError:` and `except subprocess.CalledProcessError, OSError:` — parentheses removed during S-2 extraction refactoring. Functionally equivalent in Python 3.14 but unconventional; parenthesized form is canonical.

13. **m-13: Unreachable `return None` after `_fail`** (worktree/cli.py:286, vacuity)
    - `return None` after `_fail(msg, 2)` — dead code since `_fail` returns `Never`. Also wrong type (`None` vs `tuple[bool, str | None]`). Added during extraction, likely to satisfy a linter.

### Carried Forward (not counted)

- m-8 (RC9): `_AGENT_CORE_PATTERNS` hardcoded submodule name — deferred per design C-1
- `SESSION_FIXTURE` defined after first usage in test_session_status.py (pre-existing style)
- Pipeline ordering: staging before precommit (accepted — required for precommit to see staged state)
- Skill integration "(future)" for _commit/_handoff/_status (tracked as separate worktree task "Skill-CLI integration")

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| S-1: Package structure | Covered | session/ package with sub-packages |
| S-2: `_git()` extraction + submodule discovery | Covered | git.py, worktree imports updated |
| S-3: Output and error conventions | Partial | Handoff CLI missing error handling for absent session.md (M-2) |
| S-4: Session.md parser | Covered | parse.py |
| S-5: Git changes utility | Covered | git_cli.py with submodule-aware output |
| H-1: Domain boundaries | Covered | CLI writes status + completed only |
| H-2: Committed detection | Covered | Uniform overwrite |
| H-3: Diagnostic output | Covered | Unconditional after writes |
| H-4: State caching | Partial | Backward compat gap for pre-m-7 state files (M-1) |
| C-1: Scripted vet check | Covered | RC9 M-1 path resolution fixed and verified |
| C-2: Submodule coordination | Covered | Partition, validate, commit-first |
| C-3: Input validation | Covered | CleanFileError with STOP directive |
| C-4: Validation levels | Covered | Orthogonal just-lint/no-vet options |
| C-5: Amend semantics | Covered | amend, no-edit, message validation |
| ST-0: Worktree-destined tasks | Covered | worktree_marker check in ▶ selection |
| ST-1: Parallel detection | Covered | Consecutive windows, blocker edges, cap 5 |
| ST-2: Preconditions | Covered | Missing file/old format → exit 2 |
| Registration in cli.py | Covered | All four commands registered |
| Coupled skill update | Covered | Handoff skill Step 7 precommit gate |

## Summary

| Severity | Count | Delta from RC9 |
|----------|-------|----------------|
| Critical | 0 | 0 (unchanged) |
| Major | 2 | +1 (RC9 M-1 fixed, 2 new) |
| Minor | 13 | +3 (RC9: 9 fixed, 13 new) |

**RC9 fixes:** 10 of 10 fixable findings verified fixed. m-8 carried forward.

**New majors:** M-1 (`load_state` backward compat after m-7 removal) is a regression introduced by the RC9 fix itself — removing `step_reached` from the dataclass without handling existing state files. M-2 (handoff CLI missing error handling) is a gap missed in all prior rounds, exposed by cross-module consistency check against status CLI.

**New minors:** 2 bare `pytest.raises` without `match=` at locations prior rounds didn't fix (same class as RC9 m-1/m-2/m-3). 1 redundant `len > 0` at a different location than the one fixed (same class as RC9 m-4/m-5). 2 extraction regressions in worktree/cli.py. 8 other test/code quality items.

**Trend:** RC4 2M/9m → RC5 2M/10m → RC6 1M/5m → RC7 0C/0M/6m → RC8 0C/0M/6m → RC9 0C/1M/10m → RC10 0C/2M/13m. Finding count increased because (a) RC9 fixes introduced a regression (M-1), (b) cross-cutting analysis caught a gap missed in all prior per-file reviews (M-2), and (c) same-class test specificity findings at new locations continue surfacing (m-6, m-7, m-8).
