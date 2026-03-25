# Deliverable Review: handoff-cli-tool (RC12)

**Date:** 2026-03-25
**Methodology:** agents/decisions/deliverable-review.md
**Review type:** Full-scope (no delta-scoping per learnings)
**Layers:** L1 (3 opus agents: code, test, prose+config) + L2 (interactive cross-cutting)

## Inventory

| Type | Files | + | - | Net |
|------|-------|---|---|-----|
| Code | 26 | +1898 | -97 | +1801 |
| Test | 21 | +3866 | -60 | +3806 |
| Agentic prose | 2 | +10 | -10 | +0 |
| Configuration | 2 | +2 | -2 | +0 |
| **Total** | **51** | **+5776** | **-169** | **+5607** |

### RC11 Finding Verification

| RC11 Finding | Status | Evidence |
|-------------|--------|----------|
| M-1: H-2 committed detection | FIXED | pipeline.py:143-233 — three modes (overwrite/append/autostrip) |
| M-2: H-4 step_reached | FIXED | HandoffState field + cli.py:59 resume skip |
| m-1: WORKTREE_MARKER_PATTERN | FIXED | task_parsing.py:21-23 documentation |
| m-2/m-3: Submodule missing-message | **REGRESSION** | Raises CommitInputError but CLI handler doesn't catch it (C-1) |
| m-4: _strip_hints continuation | FIXED | commit_pipeline.py:207-208 comment |
| m-5: _dirty_files -u flag | DOCUMENTED | commit_gate.py:56 comment |
| m-6: git_changes() unconditional | FIXED | handoff/cli.py:68 comment |
| m-7: dependency edges substring | FIXED | render.py:118-120 comment |
| m-8: list_plans relative path | FIXED | status/cli.py:67-68 comment |
| m-9: testability comment | FIXED | commit_pipeline.py:25,43 |
| m-10: TODO consolidate | FIXED | commit_gate.py:41 |
| m-11: SESSION_FIXTURE ordering | NOT FIXED | Still defined at line 280, first used at line 253 |
| m-12: assertion strings | PARTIAL | Some tests improved, others unchanged |
| m-13/m-14/m-15: test structure | NOT FIXED | Expected — session.md stated "not addressed" |
| Corrector: autostrip guard | FIXED | pipeline.py:217 catches both exceptions |
| Corrector: dead mock | FIXED | No dead mocks remain |

## Critical Findings

**C-1** `session/cli.py:29-32` — error signaling, conformance (S-3)

`commit_pipeline(ci)` can raise `CommitInputError` from `_validate_inputs()` (commit_pipeline.py:276-278: "Files under {path}/ but no ## Submodule {path} section"). The except clause at cli.py:31 catches `CleanFileError` only.

Propagation path: `_validate_inputs` raises `CommitInputError` → `commit_pipeline` doesn't catch it → `commit_cmd` except only matches `CleanFileError` → exception propagates to Click → stderr "Error:" format, exit 1.

Violates S-3 on three axes:
- **Output channel:** stderr instead of stdout
- **Output format:** Click's "Error:" prefix instead of `**Error:**` structured markdown
- **Exit code:** 1 (pipeline error) instead of 2 (input validation)

This is a regression from the m-2/m-3 fix. Pre-fix: `_validate_inputs` returned `CommitResult(success=False)` → wrong exit code (1 instead of 2) but structured stdout output. Post-fix: raises `CommitInputError` → correct error semantics but unhandled → worse behavior on all three S-3 axes.

**Fix:** Add `CommitInputError` to the except clause at cli.py:31:
```python
try:
    result = commit_pipeline(ci)
except (CleanFileError, CommitInputError) as e:
    _fail(str(e) if isinstance(e, CleanFileError) else f"**Error:** {e}", code=2)
```

**Test gap:** No CLI-level test exercises the missing-submodule-message path through `commit_cmd`. Unit test at test_session_commit_pipeline_ext.py:104 catches `CommitInputError` directly from `commit_pipeline()` but doesn't test the CLI handler.

## Major Findings

None.

## Minor Findings

### Code (7)

**m-1** `handoff/pipeline.py:203,228` — functional correctness — Append and autostrip modes strip blank lines (`if line.strip()`) from current section before combining. Loses inter-group markdown spacing (blank lines between `###` sub-groups).

**m-2** `handoff/pipeline.py:206-219` — modularity — Autostrip mode re-executes `_find_repo_root` + `git show HEAD:` already done in `_detect_write_mode`. Could pass committed content from detection.

**m-3** `status/cli.py:60-65` — robustness — Old-format detection compares raw task line count against parsed task count. Malformed lines (matching `- [` but failing parse) produce misleading "Old-format" error.

**m-4** `commit_gate.py:66` — functional correctness — `len(line) > 3` guard in `_dirty_files()` should be `>= 3` per porcelain format spec. No practical impact (git never produces empty paths).

**m-5** `handoff/pipeline.py:173-178` — robustness — `_detect_write_mode` compares stripped lines for set membership. Different indentation between committed and current content → false match after `.strip()`. Edge case — completed content is typically unindented.

**m-6** `handoff/cli.py:70` — functional correctness — When tree is clean, `git_changes()` returns empty string → output is an empty fenced code block. The Click command wrapper (`changes_cmd`) handles this with "Tree is clean." but handoff CLI calls the Python function directly.

**m-7** `handoff/pipeline.py:115-140,170` — robustness — `_extract_completed_section` with `splitlines(keepends=True)` preserves trailing newlines, but mode detection compares raw text with `==` (newline-sensitive) while writers use `.splitlines()` (newline-insensitive). Trailing newline difference could trigger append when overwrite was intended.

### Test (10)

**m-8** `test_session_status.py:280` — conformance — SESSION_FIXTURE defined after first usage (line 253). Carried from RC11 m-11; claimed fix not applied.

**m-9** `test_session_commit_pipeline.py:108-125` — specificity — Generic assertion words ("continuation", "other line"). Carried from RC11 m-12. Partially improved in adjacent tests.

**m-10** `test_planstate_aggregation.py:102-197` — independence — Conflates positive/negative paths in one function. Carried from RC11 m-13.

**m-11** `test_session_handoff.py:217-248` — independence — Two tests exercise same `_write_completed_section` path. Near-redundant. Carried from RC11 m-14.

**m-12** `test_session_commit_pipeline.py:157-212` / `test_session_commit_pipeline_ext.py:22-35` — conformance — Inconsistent submodule setup helpers. Carried from RC11 m-15.

**m-13** `test_session_handoff_committed.py:99-100` — functional correctness — Comment "Simulate prior uncommitted handoff" describes agent behavior but not mode-detection rationale. Misleading.

**m-14** `test_session_handoff_committed.py` — coverage — Autostrip error fallback path (`_find_repo_root` ValueError or `git show` failure) has no dedicated test.

**m-15** `test_session_handoff_cli.py` — coverage — No test for resume from `step_reached="write_session"` (writes performed during resume). Only diagnostics-skip tested.

**m-16** `test_session_handoff.py:217` — excess — Pre-H-2 accumulated content test now redundant with committed detection tests in test_session_handoff_committed.py.

**m-17** `test_session_handoff_committed.py` — coverage — No direct `_detect_write_mode` unit test. Integration tests verify final output but don't assert mode selection.

### Prose+Config (5)

**m-18** handoff/SKILL.md:146 — actionability — "STOP — fix issues and retry" competes with communication rule 1 (stop and wait for guidance).

**m-19** handoff/SKILL.md:27 — constraint precision — H-2 reference identifier unresolvable by agents.

**m-20** design/SKILL.md:135-142 — scope — Changes are standalone bugfix, not handoff-cli-tool deliverable. Scope attribution note.

**m-21** .claude/settings.local.json — vacuity — Trailing newline change only.

**m-22** .gitignore:17 — scope — `.vscode/` → `.vscode` broadening unrelated to plan scope.

## Gap Analysis

| Design Requirement | Status | Reference |
|-------------------|--------|-----------|
| S-1: Package structure | Covered | session/ subpackage |
| S-2: `_git()` extraction + submodule discovery | Covered | git.py, worktree imports updated |
| S-3: Output and error conventions | **Regression** | C-1: CommitInputError uncaught in commit_cmd |
| S-4: Session.md parser | Covered | session/parse.py |
| S-5: Git changes utility | Covered | git_cli.py |
| H-1: Domain boundaries | Covered | CLI: status + completed writes |
| H-2: Committed detection | Covered | Three modes implemented (RC11 M-1 fixed) |
| H-3: Diagnostic output | Covered | git_changes() after writes |
| H-4: State caching + step_reached | Covered | HandoffState field + resume logic (RC11 M-2 fixed) |
| C-1: Scripted vet check | Covered | pyproject.toml patterns + report freshness |
| C-2: Submodule coordination | **Partial** | 4-state matrix works; error path violates S-3 (C-1) |
| C-3: Input validation + STOP | Covered | CleanFileError |
| C-4: Validation levels | Covered | Orthogonal options |
| C-5: Amend semantics | Covered | diff-tree, directional propagation |
| ST-0: Worktree-destined tasks | Covered | Marker skip in Next selection |
| ST-1: Parallel detection | Covered | Consecutive windows, cap 5 |
| ST-2: Preconditions | Covered | Missing file/old format → exit 2 |
| Registration in cli.py | Covered | All commands registered |
| Coupled skill update | Covered | Handoff SKILL.md Step 7 |

## Cross-Cutting Analysis (Layer 2)

- **Path consistency:** `CLAUDEUTILS_SESSION_FILE` env var consistent between handoff and status ✓
- **API contract alignment:** `CommitInputError` raised by `commit_pipeline._validate_inputs` but not caught by `cli.commit_cmd` ✗ (C-1)
- **Naming uniformity:** Error classes, data classes, private functions — consistent ✓
- **`_fail()` consolidation:** Single definition in `git.py`, all subcommands import ✓
- **Import chain (S-2):** All worktree modules updated to import from `claudeutils.git` ✓
- **Fragment convention:** Skill changes follow patterns ✓
- **State file coverage:** `tmp/.handoff-state.json` covered by existing `/tmp/` gitignore ✓
- **RC11 fix verification:** L1 code agent incorrectly marked m-2/m-3 as FIXED; the fix introduced a regression (C-1)

## Summary

| Severity | Count |
|----------|-------|
| Critical | 1 |
| Major | 0 |
| Minor | 22 |

**RC11 fix verification:** Both majors (M-1 H-2, M-2 H-4) confirmed fixed. m-2/m-3 fix introduced a regression (C-1). 7 of 10 code minors addressed. 1 of 5 test minors partially addressed; 4 unaddressed as stated. Corrector fixes verified.

**Critical finding (C-1):** The m-2/m-3 fix changed `_validate_inputs` to raise `CommitInputError` (correct error type for exit 2) but didn't update `commit_cmd`'s except clause to catch it from `commit_pipeline()`. The exception propagates to Click, producing stderr output with exit 1 — worse than the pre-fix behavior on all three S-3 axes (channel, format, code). One-line fix: add `CommitInputError` to the except clause at cli.py:31.

**Trend:** RC9 0C/2M/13m → RC10 0C/2M/13m → RC11 0C/2M/15m → RC12 1C/0M/22m. Both long-standing majors resolved. New Critical from incomplete error handler update. Minor count reflects full-scope review of new H-2/H-4 code surface (7 code, 5 new test) plus 5 carried test minors and 5 prose/config scope notes.
