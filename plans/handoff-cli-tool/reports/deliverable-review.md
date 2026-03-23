# Deliverable Review: handoff-cli-tool (RC5)

**Date:** 2026-03-23
**Methodology:** agents/decisions/deliverable-review.md
**Approach:** Layer 1 (three opus agents: code, test, prose+config) + Layer 2 (interactive cross-cutting)

## Inventory

| Type | Files | + | - | Net |
|------|-------|---|---|-----|
| Code | 26 | +1662 | -95 | +1567 |
| Test | 20 | +3411 | -16 | +3395 |
| Agentic prose | 2 | +9 | -6 | +3 |
| Configuration | 2 | +2 | -2 | +0 |
| **Total** | **50** | **+5084** | **-119** | **+4965** |

### RC4 Finding Verification

| RC4 Finding | Status | Evidence |
|-------------|--------|----------|
| M-1 (H-2 committed detection test) | FIXED | test_session_handoff.py:258-274 — `init_repo_minimal`, commits session.md, verifies overwrite replaces committed content |
| M-2 (`init_repo_minimal` helper) | FIXED | pytest_helpers.py:79-89 — cwd-style init, used by 5 session test files. No local `_init_repo` in session tests. |
| m-1 (`step_reached` field) | FIXED | handoff/pipeline.py:20 — `step_reached: str = "write_session"` |
| m-2 (ANSI color) | FIXED | render.py:30,49-50 — `color: bool = False` kwarg, `click.style(bold=True, fg="green")`, CLI passes `sys.stdout.isatty()` |
| m-3 (▶ two-line format) | FIXED | render.py:48,52 — `▶ {name} ({model}) \| Restart: {Yes/No}` + `  \`{cmd}\`` |
| m-4 (`_strip_hints` continuations) | PARTIAL | commit_pipeline.py:187-207 — stateful loop added, but see M-1 below |
| m-5 (parallel cap test) | FIXED | test_session_status.py:208-213 — 7 tasks → `len(result) == 5` |
| m-6 (or-disjunction split) | FIXED | test_session_commit_pipeline.py:43,79 — separate assertions |
| m-7 (integration test extension) | FIXED | test_session_integration.py:72-77 — session.md content assertions |
| m-8, m-9 | SKIPPED | Per RC4 disposition (incidental config, pre-existing worktree hardcode) |

8 of 9 actionable RC4 findings verified fixed. 1 partial (m-4: continuation logic has residual issue).

## Critical Findings

None.

## Major Findings

1. **M-1: `_strip_hints` resets state after first continuation line** (session/commit_pipeline.py:196-201)
   - Both continuation branches (tab at :197, double-space at :198) set `prev_was_hint = False`. Multi-line hint blocks (hint + 2+ continuation lines) only filter the first continuation; remaining lines pass through.
   - Example: `"hint: foo\n  line1\n  line2\nnormal"` keeps `"  line2"`.
   - **Fix:** Change `prev_was_hint = False` to `prev_was_hint = True` in the continuation-detected branch so the next line continues the hint context check.
   - **Impact:** Low practical impact — git hint lines typically each carry the `hint:` prefix. Residual issue from RC4 m-4 fix.
   - **Found by:** Layer 1 code agent + Layer 2 independent verification

2. **M-2: `vet_check` and helpers ignore `cwd` parameter** (session/commit_gate.py:108-129,141-183)
   - `_load_review_patterns()` reads `Path("pyproject.toml")` relative to process CWD. `_find_reports()` globs `Path("plans")` relative to process CWD. The commit pipeline passes `cwd` through to `validate_files` but `vet_check()` has no `cwd` parameter and cannot receive it.
   - **Impact:** No production impact (CLI runs from project root). API inconsistency — all other gate functions accept `cwd`.
   - **Found by:** Layer 1 code agent

## Minor Findings

### Conformance

1. **m-1: `## Message` EOF semantics relies on blockquote escaping** (session/commit.py:56-74)
   - Design line 162: "Everything from `## Message` to EOF is message body — safe for content containing `## ` lines." Implementation: `_split_sections` splits on all `## ` headings unconditionally. Safety is provided by the blockquote format (`> ## ` doesn't match `^## `), not by EOF semantics. Design line 164 confirms: "Unknown `## ` within blockquotes treated as message body."
   - Practically unreachable: input format requires blockquoted messages. A defensive `is_message_section` flag stopping section splitting after `## Message` would match the spec exactly.

2. **m-2: `step_reached` field exists but is never checked or updated** (session/handoff/pipeline.py:20, session/handoff/cli.py:46-52)
   - Design H-4: "re-execute from `step_reached`." Field is persisted and roundtrips JSON, but resume always replays the full pipeline. Operations are idempotent so full replay is correct. Field is vestigial metadata — schema-conformant but behaviorally unused.

3. **m-3: Pipeline stage ordering deviates from design** (session/commit_pipeline.py:279-311)
   - Design: "validate → vet check → precommit → stage → commit". Implementation: validate → stage → precommit/vet → commit. Staging before precommit is technically necessary (`just precommit` needs staged state). Valid deviation.

4. **m-4: Diagnostic output conditionally suppressed** (session/handoff/cli.py:57-59)
   - Design H-3: diagnostics emitted "Always." Implementation guards with `if git_output:`. After session.md writes there will always be changes, so the guard is practically always true, but contradicts the spec's unconditional language.

### Robustness

5. **m-5: stderr discarded from precommit/lint** (session/commit_pipeline.py:34,49)
   - `_run_precommit` and `_run_lint` return `result.stdout.strip()` only. Some tools write diagnostics to stderr. Gate-specific diagnostics may be incomplete on failure.

6. **m-6: `_git()` strips stdout** (git.py:24)
   - `r.stdout.strip()` destroys leading-space XY format for porcelain callers. Current callers avoid `_git()` for porcelain (using raw subprocess). Docstring warning would prevent regression. Aligns with learnings entry on porcelain parsing.

7. **m-7: Ternary precedence in `validate_files`** (session/commit_gate.py:91)
   - `dirty | _head_files(cwd) if amend else dirty` parses as `dirty | (_head_files(cwd) if amend else dirty)`. Functionally correct (both branches produce right result) but parenthesizing clarifies intent.

### Test Quality

8. **m-8: Local init helpers persist in pre-existing test files** (test_planstate_aggregation_integration.py:14, test_planstate_aggregation.py:65)
   - RC4 M-2 replaced 5 session test variants. 2 pre-existing non-session test files retain local helpers. Not a deliverable regression.

9. **m-9: No test for multi-continuation or single-space edge case in `_strip_hints`** (test_session_commit_pipeline.py:101-118)
   - Tests cover single-continuation scenarios only. Multi-line continuations and single-space indentation untested.

10. **m-10: `test_status_format_merged_next` missing dash-prefix assertion** (test_status_rework.py:111)
    - Verifies command is absent from non-first tasks but doesn't assert the `- ` prefix format specified in design.

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| S-1: Package structure | Covered | session/ package with sub-packages for handoff and status |
| S-2: `_git()` extraction + submodule discovery | Covered | git.py, worktree imports updated |
| S-3: Output and error conventions | Covered | stdout only, exit codes 0/1/2, `**Header:** content` |
| S-4: Session.md parser | Covered | parse.py composes existing functions |
| S-5: Git changes utility | Covered | git_cli.py, submodule-aware output |
| H-1: Domain boundaries | Covered | CLI writes status + completed only |
| H-2: Committed detection | Covered | Always-overwrite, tested against git state |
| H-3: Diagnostic output | Covered (m-4) | Conditional guard, practically always true |
| H-4: State caching | Covered (m-2) | step_reached field present, unused in resume |
| C-1: Scripted vet check | Covered (M-2) | Patterns + reports, missing cwd propagation |
| C-2: Submodule coordination | Covered | Partition, validate, commit-first, pointer staging |
| C-3: Input validation | Covered | CleanFileError with STOP directive, amend awareness |
| C-4: Validation levels | Covered | just-lint/no-vet orthogonal options |
| C-5: Amend semantics | Covered | amend, no-edit, message validation |
| C-Message: EOF semantics | Covered (m-1) | Blockquote format provides safety |
| ST-0: Worktree-destined tasks | Covered | worktree_marker check in ▶ selection |
| ST-1: Parallel detection | Covered | Consecutive windows, blocker edges, cap at 5 |
| ST-2: Preconditions | Covered | Missing file/old format → exit 2 |
| Registration in cli.py | Covered | All four commands registered |
| Coupled skill update | Covered | Handoff skill precommit gate added |

## Summary

| Severity | Count | Delta from RC4 |
|----------|-------|----------------|
| Critical | 0 | 0 (unchanged) |
| Major | 2 | 0 (net: RC4's 2M resolved, 2 new M found) |
| Minor | 10 | +1 (RC4: 9m, RC5: 10m) |

**RC4 fixes:** 8 of 9 actionable findings verified fixed. m-4 (`_strip_hints`) partial — continuation logic added but has residual multi-continuation bug (now M-1).

**New findings:** M-1 (strip_hints state reset) emerged from deeper analysis of the m-4 fix. M-2 (vet_check cwd) is a latent API inconsistency with no production impact.

**Pre-existing/carried (not counted):** Hardcoded "agent-core" in worktree/cli.py (RC4 m-9), design/SKILL.md scope attribution (RC4 m-8).
