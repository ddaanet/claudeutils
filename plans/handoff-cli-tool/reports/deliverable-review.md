# Deliverable Review: handoff-cli-tool (RC6)

**Date:** 2026-03-23
**Methodology:** agents/decisions/deliverable-review.md
**Approach:** Layer 1 (three opus agents: code, test, prose+config) + Layer 2 (interactive cross-cutting)

## Inventory

| Type | Files | + | - | Net |
|------|-------|---|---|-----|
| Code | 26 | +1675 | -95 | +1580 |
| Test | 20 | +3438 | -59 | +3379 |
| Agentic prose | 2 | +9 | -6 | +3 |
| Configuration | 2 | +2 | -2 | +0 |
| **Total** | **50** | **+5124** | **-162** | **+4962** |

### RC5 Finding Verification

| RC5 Finding | Status | Evidence |
|-------------|--------|----------|
| M-1 (`_strip_hints` continuation state) | FIXED | commit_pipeline.py:204-205 — `prev_was_hint = True` for tab/double-space continuations |
| M-2 (`vet_check`/helpers accept `cwd`) | FIXED | commit_gate.py:108,120,141 — all three accept `cwd: Path \| None = None`; call site at commit_pipeline.py:176 passes `cwd=cwd` |
| m-1 (`_split_sections` `in_message`) | FIXED | commit.py:61,65,70-71 — flag set on `## Message`, checked before heading detection |
| m-2 (`step_reached` vestigial) | ACCEPTED | Idempotent replay is safe; field is dead code |
| m-3 (pipeline ordering deviation) | ACCEPTED | Staging before precommit is technically required |
| m-4 (unconditional diagnostics) | FIXED | handoff/cli.py:57-58 — no `if git_output:` guard |
| m-5 (stderr capture) | FIXED | commit_pipeline.py:35-36,53-54 — stderr appended when non-empty |
| m-6 (`_git()` docstring) | FIXED | git.py:17-19 — warns against porcelain usage |
| m-7 (parenthesized ternary) | FIXED | commit_gate.py:91 — `(dirty \| _head_files(cwd)) if amend else dirty` |
| m-8 (init_repo_minimal consolidation) | FIXED | Both planstate test files import from `tests.pytest_helpers` |
| m-9 (strip_hints tests) | FIXED | test_session_commit_pipeline.py:121-128,132-138 |
| m-10 (dash-prefix assertion) | FIXED | test_status_rework.py:112 — `assert second_line.startswith("- ")` |

10 of 10 actionable RC5 findings verified fixed. 2 accepted as-is (m-2, m-3).

## Critical Findings

None.

## Major Findings

1. **M-1: No test for `_split_sections` `in_message` flag** (test_session_commit.py, coverage)
   - Design outline.md:162-164: "Everything from `## Message` to EOF is message body — safe for content containing `## ` lines. ... Unknown `## ` within blockquotes treated as message body."
   - Implementation: `_split_sections` (commit.py:61-71) has dedicated `in_message` flag stopping section detection after `## Message`.
   - No test verifies this behavior. A regression removing the flag would silently truncate commit messages containing `## ` lines, with no test catching it.
   - Practical risk is low — the blockquote format (`> ## `) naturally prevents matching `^## (.+)$`. The flag is defense-in-depth against raw `## ` lines in message body.
   - **Found by:** Layer 1 test agent, confirmed by Layer 2 independent search

## Minor Findings

### Test Quality

1. **m-1: `test_commit_cli_success` vacuous on commit creation** (test_session_commit_cli.py:18-36, specificity)
   - Asserts `exit_code == 0` and output substring but not `git log` confirmation. The pipeline test covers commit creation, making this test's commit verification vacuous. Low severity — covered by integration path.

2. **m-2: Imprecise submodule assertion** (test_session_handoff_cli.py:234, specificity)
   - Asserts `"## Submodule" in result.output` — matches any substring. `"## Submodule: agent-core"` would pin the exact format.

3. **m-3: Multi-submodule commit order not tested** (test_session_commit_pipeline_ext.py, coverage)
   - Design outline.md:265-267 specifies discovery-order commits with pointer staging. Only single-submodule tested. Rare real-world scenario.

### Clarity

4. **m-4: Redundant checkbox check in `render_pending`** (render.py:45, clarity)
   - `pending` already filtered to `checkbox == " "` at line 37. Inner-loop check at line 45 is always true.

5. **m-5: `ParsedTask` imported from different modules** (test_session_parser.py:8 vs test_session_status.py:17, consistency)
   - `session.parse` re-exports from `validation.task_parsing`. Both valid, but inconsistent canonical path.

### Carried Forward (not counted)

- `step_reached` vestigial (RC5 m-2, accepted as-is — idempotent replay is safe)
- `→ wt` marker not detected by `WORKTREE_MARKER_PATTERN` (pre-existing parser limitation, mitigated by section placement)
- `SESSION_FIXTURE` defined after first usage (pre-existing quality issue)

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| S-1: Package structure | Covered | session/ package with sub-packages |
| S-2: `_git()` extraction + submodule discovery | Covered | git.py, worktree imports updated |
| S-3: Output and error conventions | Covered | stdout only, exit 0/1/2 |
| S-4: Session.md parser | Covered | parse.py composes existing functions |
| S-5: Git changes utility | Covered | git_cli.py with submodule-aware output |
| H-1: Domain boundaries | Covered | CLI writes status + completed only |
| H-2: Committed detection | Covered | Idempotent overwrite |
| H-3: Diagnostic output | Covered | Unconditional after RC5 fix |
| H-4: State caching | Covered | step_reached vestigial but safe |
| C-1: Scripted vet check | Covered | Patterns + reports with cwd propagation |
| C-2: Submodule coordination | Covered | Partition, validate, commit-first |
| C-3: Input validation | Covered | CleanFileError with STOP directive |
| C-4: Validation levels | Covered | Orthogonal just-lint/no-vet options |
| C-5: Amend semantics | Covered | amend, no-edit, message validation |
| C-Message: EOF semantics | Covered (M-1) | in_message flag works but untested |
| ST-0: Worktree-destined tasks | Covered | worktree_marker check in ▶ selection |
| ST-1: Parallel detection | Covered | Consecutive windows, blocker edges, cap at 5 |
| ST-2: Preconditions | Covered | Missing file/old format → exit 2 |
| Registration in cli.py | Covered | All four commands registered |
| Coupled skill update | Covered | Handoff skill precommit gate (Step 7) |

## Summary

| Severity | Count | Delta from RC5 |
|----------|-------|----------------|
| Critical | 0 | 0 (unchanged) |
| Major | 1 | -1 (RC5: 2M resolved, 1 new M) |
| Minor | 5 | -5 (RC5: 10m, RC6: 5m) |

**RC5 fixes:** 10 of 10 actionable findings verified fixed. All Majors resolved.

**New M-1:** Test coverage gap for `in_message` flag — design-specified defense-in-depth behavior with code but no regression test. Low practical risk (blockquote format prevents the edge case).

**Trend:** RC4 2M/9m → RC5 2M/10m → RC6 1M/5m. Convergence continues — Major count reduced, Minor count halved.
