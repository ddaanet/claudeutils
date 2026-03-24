# Classification: Fix handoff-cli RC10 findings

**Date:** 2026-03-24
**Input:** plans/handoff-cli-tool/reports/deliverable-review.md (RC10: 0C/2M/13m)
**Plan status:** rework
**Round:** 10

## Composite Decomposition

| # | Finding | Behavioral? | Classification | Action |
|---|---------|-------------|----------------|--------|
| M-1 | `load_state()` backward compat — crashes on pre-m-7 state files (pipeline.py:44) | Yes — adds field filtering | Moderate | Filter `data` to `HandoffState.__dataclass_fields__` before unpacking |
| M-2 | Handoff CLI missing session.md existence check (handoff/cli.py) | Yes — adds try/except routing | Moderate | Wrap pipeline calls in try/except, route through `_fail` |
| m-1 | Submodule CleanFileError paths lack repo context (commit_pipeline.py:269-273) | Yes — changes error output | Moderate | Prepend submodule prefix back into error paths |
| m-2 | `overwrite_status` regex backreference vulnerability (pipeline.py:75) | Yes — replacement callback | Moderate | Use function callback for `re.subn` replacement |
| m-3 | `_build_repo_section` heading/content gap (git_cli.py:32) | No — string literal | Simple | Add blank line after header |
| m-4 | Blocker dependency edges overly conservative (status/render.py:118) | Yes — logic change | Moderate | **DEFERRED** — functionally safe (false positive only) |
| m-5 | `list_plans` relative path (status/cli.py:67) | No — matches existing pattern | Simple | **DEFERRED** — consistent with `_is_dirty()` and session file |
| m-6 | Redundant `len > 0` assertion (test_session_parser.py:138) | No — removal | Simple | Remove `assert len(data.completed) > 0` |
| m-7 | Bare `pytest.raises(CleanFileError)` (test_session_commit.py:217) | No — add `match=` | Simple | Add `match=` pattern |
| m-8 | Bare `pytest.raises(CalledProcessError)` (test_worktree_merge_errors.py:83) | No — add `match=` | Simple | Add `match=` pattern |
| m-9 | Ambiguous assertion string (test_session_commit_pipeline.py:121-127) | No — tighten assertion | Simple | Use more specific assertion string |
| m-10 | Disjunctive assertion (test_session_status.py:263) | No — tighten assertion | Simple | Assert specific expected section |
| m-11 | Integration test references nonexistent plan dir (test_session_integration.py:34-35) | No — add fixture | Simple | Add plan dir to test setup |
| m-12 | Un-parenthesized except clauses (worktree/cli.py:104,176) | No — add parens | Simple | Add parentheses to except tuples |
| m-13 | Unreachable `return None` after `_fail` (worktree/cli.py:286) | No — removal | Simple | Remove dead code |

## Overall

- **Classification:** Mixed — Moderate (M-1, M-2, m-1, m-2) + Simple (m-3, m-6..m-13)
- **Implementation certainty:** High — all fixes have file:line and fix direction from review
- **Requirement stability:** High — RC10 findings with concrete mechanisms
- **Behavioral code check:** M-1, M-2, m-1, m-2 change production logic paths
- **Work type:** Production
- **Artifact destination:** production (src + tests)
- **Evidence:** RC10 deliverable-review.md; recall: behavioral-code-as-simple, error-handling-call-chain, composite-task

## Deferrals

- **m-4** (blocker dependency edges): Functionally safe — prevents valid parallelism but never allows unsafe. Conservative false-positive behavior.
- **m-5** (`list_plans` relative path): Consistent with `_is_dirty()` and session file assumptions. Fixing one creates inconsistency.
- **m-8 (RC9)**: `_AGENT_CORE_PATTERNS` hardcoded submodule name — deferred per design C-1 (carried forward)

## Routing

Moderate items present → `/runbook plans/handoff-cli-tool`
- TDD phases: M-1 (state file compat), M-2 (error handling), m-1 (error paths), m-2 (regex safety)
- General phase: m-3, m-6..m-13 (mechanical fixes batch)
- Deferred: m-4, m-5 (carried forward with rationale)
