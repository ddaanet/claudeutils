# Deliverable Review: handoff-cli-tool (RC8)

**Date:** 2026-03-24
**Methodology:** agents/decisions/deliverable-review.md
**Approach:** Layer 1 (three opus agents: code, test, prose+config) + Layer 2 (interactive cross-cutting)

## Inventory

| Type | Files | + | - | Net |
|------|-------|---|---|-----|
| Code | 26 | +1733 | -95 | +1638 |
| Test | 20 | +3513 | -59 | +3454 |
| Agentic prose | 2 | +9 | -6 | +3 |
| Configuration | 2 | +2 | -2 | +0 |
| **Total** | **50** | **+5257** | **-162** | **+5095** |

### RC7 Finding Verification

| RC7 Finding | Status | Evidence |
|-------------|--------|----------|
| m-1: Vacuous disjunction in commit_format test | FIXED | test_session_commit_format.py:21 — `output.split("\n")[0].startswith("[")` |
| m-2: Four parametrize cases → combined assertion | FIXED | test_session_commit.py:50-67 — single `test_parse_commit_input` asserting all fields |
| m-3: `ParsedTask` import path inconsistency | FIXED | test_status_rework.py:11 — `from claudeutils.session.parse import ParsedTask` |
| m-4: Missing `just-lint` + `no-vet` combination test | FIXED | test_session_commit_validation.py:259-291 — `test_commit_just_lint_no_vet` |
| m-5: Imprecise "clean" assertion | FIXED | test_git_cli.py:83 — `"Tree is clean." in result.output` |
| m-6: Imprecise "Git status" assertion | FIXED | test_session_handoff_cli.py:90 — `"**Git status:**" in result.output` |

6 of 6 RC7 findings verified fixed.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

### Test Specificity

1. **m-1: Bare `pytest.raises` without match** (test_session_commit.py:101, specificity)
   - `pytest.raises(CommitInputError)` for no-edit + Message contradiction case lacks `match=` parameter. All other raises in `test_parse_commit_input_edge_cases` use `match=` to verify the error reason. This case passes on any `CommitInputError`, not specifically the contradictory-options check.

2. **m-2: Heading format not verified in handoff parse test** (test_session_handoff.py:45-46, specificity)
   - `test_parse_handoff_input` asserts `len(result.completed_lines) > 0` and `any("Produced outline" in line ...)`. Does not verify the `### Handoff CLI tool design (Phase A)` heading line is present, despite H-1/H-2 specifying `### ` headings in completed entries.

### Code Robustness

3. **m-3: Empty `## Files` section not rejected** (src/claudeutils/session/commit.py:38-40, robustness)
   - `_parse_files` returns `[]` for a `## Files` section with no `- path` entries. `_validate` checks `files is None` but not `files == []`. Empty list passes through pipeline to `git commit` which fails with opaque "nothing to commit" error. Explicit empty-list check with clear error message would be more informative.

4. **m-4: `ci.message or ""` fallback masks unreachable state** (src/claudeutils/session/commit_pipeline.py:336, robustness)
   - `_git_commit(ci.message or "", ...)` passes empty string when `ci.message is None` and `no_edit is False`. The `_validate_inputs` guard at line 262 prevents this path, but the `or ""` fallback silently masks what should be an impossible state. An assertion would make the invariant explicit.

5. **m-5: `_strip_hints` fragile continuation detection** (src/claudeutils/session/commit_pipeline.py:204, robustness)
   - Hint continuation detection uses nested condition: tab or double-space after a hint line is treated as continuation. Single-space-prefixed non-double-spaced lines break detection. Edge case unlikely in practice (git hint output uses consistent indentation), but the logic is fragile.

### Cross-Cutting Consistency

6. **m-6: `ParsedTask` import bypasses S-4 interface in render.py** (src/claudeutils/session/status/render.py:7, consistency)
   - Imports `ParsedTask` from `claudeutils.validation.task_parsing` instead of `claudeutils.session.parse`. The sibling `status/cli.py:14` correctly imports from `session.parse`. The S-4 parser re-exports `ParsedTask` as its public interface. Same class as RC7 m-3 (which fixed the identical pattern in test code) — now identified in production code.

### Carried Forward (not counted)

- `step_reached` vestigial in HandoffState (RC5 m-2, accepted — idempotent replay is safe)
- Pipeline ordering: staging before precommit (RC5 m-3, accepted — required for precommit to see staged state)
- `→ wt` marker not detected by `WORKTREE_MARKER_PATTERN` (pre-existing parser limitation)
- `SESSION_FIXTURE` defined after first usage in test_session_status.py (pre-existing quality issue, not plan-introduced)

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| S-1: Package structure | Covered | session/ package with sub-packages |
| S-2: `_git()` extraction + submodule discovery | Covered | git.py, worktree imports updated |
| S-3: Output and error conventions | Covered | stdout only, exit 0/1/2 |
| S-4: Session.md parser | Covered | parse.py composes existing functions |
| S-5: Git changes utility | Covered | git_cli.py with submodule-aware output |
| H-1: Domain boundaries | Covered | CLI writes status + completed only |
| H-2: Committed detection | Covered | Uniform overwrite |
| H-3: Diagnostic output | Covered | Unconditional after writes |
| H-4: State caching | Covered | step_reached vestigial but safe |
| C-1: Scripted vet check | Covered | Patterns + reports with cwd propagation |
| C-2: Submodule coordination | Covered | Partition, validate, commit-first |
| C-3: Input validation | Covered | CleanFileError with STOP directive |
| C-4: Validation levels | Covered | Orthogonal just-lint/no-vet options |
| C-5: Amend semantics | Covered | amend, no-edit, message validation |
| C-Message: EOF semantics | Covered | in_message flag with regression test |
| ST-0: Worktree-destined tasks | Covered | worktree_marker check in ▶ selection |
| ST-1: Parallel detection | Covered | Consecutive windows, blocker edges, cap 5 |
| ST-2: Preconditions | Covered | Missing file/old format → exit 2 |
| Registration in cli.py | Covered | All four commands registered |
| Coupled skill update | Covered | Handoff skill Step 7 precommit gate |

## Summary

| Severity | Count | Delta from RC7 |
|----------|-------|----------------|
| Critical | 0 | 0 (unchanged) |
| Major | 0 | 0 (unchanged) |
| Minor | 6 | 0 (RC7: 6m resolved, 6 new m) |

**RC7 fixes:** 6 of 6 findings verified fixed.

**New minors:** 2 test specificity (m-1, m-2), 3 code robustness (m-3, m-4, m-5), 1 cross-cutting consistency (m-6). Code robustness findings are defensive — no functional correctness issues, all edge cases. The consistency finding (m-6) is the production-code equivalent of the RC7 m-3 test fix.

**Trend:** RC4 2M/9m → RC5 2M/10m → RC6 1M/5m → RC7 0C/0M/6m → RC8 0C/0M/6m. Zero Critical and Major across three consecutive rounds. Minor count stable at 6 but composition shifted from test-only to mixed (code + test + cross-cutting).
