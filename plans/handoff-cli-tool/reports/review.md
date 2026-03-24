# Review: handoff-cli-tool RC6 fixes

**Scope**: Changes since baseline commit 5ba43dc5 — RC6 fix implementation (M-1 + m-1..m-5)
**Date**: 2026-03-23
**Mode**: review + fix

## Summary

Six fixes implement all RC6 findings: one major (M-1 regression test for `_split_sections` `in_message` flag) and five minor (git log confirmation, submodule assertion tightening, multi-submodule order test, redundant checkbox removal, import alignment). The submodule helper extraction to `pytest_helpers` (prerequisite for m-3) correctly factors repeated setup into reusable utilities. Implementation quality is high across all changes.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Split import block for `pytest_helpers`**
   - Location: `tests/test_session_commit_pipeline_ext.py:13-21`
   - Note: Two separate `from tests.pytest_helpers import` blocks where one would suffice. Cosmetic only.
   - **Status**: OUT-OF-SCOPE — linter-catchable; `just lint` handles import ordering deterministically.

## Fixes Applied

No fixes required — the one identified issue is OUT-OF-SCOPE (linter-catchable).

## Verification Against Findings

| Finding | Implementation | Match |
|---------|---------------|-------|
| M-1: `_split_sections` `in_message` test | `test_split_sections_in_message_preserves_headings` (test_session_commit.py:142-159); imports `_split_sections` directly; asserts section names `== ["Files", "Message"]` and `"## Not a section"` in Message body lines | Exact |
| m-1: `git log` confirmation in `test_commit_cli_success` | subprocess `git log --oneline -1` against `tmp_path`; asserts `"foo" in log.stdout.lower()` | Exact |
| m-2: Submodule assertion tightened | `"## Submodule: agent-core"` at test_session_handoff_cli.py:234 | Exact |
| m-3: Multi-submodule order test | `test_commit_multi_submodule_order` with alpha/beta submodules; verifies each submodule commit message and parent commit | Exact; helper extraction also applied |
| m-4: Redundant `task.checkbox == " "` removed | render.py:45 — condition reduced to `first_eligible and task.worktree_marker is None` | Exact |
| m-5: `ParsedTask` import aligned | test_session_status.py imports from `claudeutils.session.parse` (re-export path) | Exact |

## Design Conformance Notes

**M-1 test scope:** Uses `_split_sections` directly (white-box), bypassing blockquote wrapping. Correct — the finding specifies defense-in-depth against raw `## ` lines (not blockquoted), so the test correctly exercises raw `## ` in message body to hit the branch.

**Helper extraction:** `create_submodule_origin` and `add_submodule` in `pytest_helpers.py` cleanly generalize the single-submodule pattern. `add_submodule` correctly includes `protocol.file.allow=always` (previously inlined). Identity config set on the submodule directory post-add matches prior manual pattern.

**Multi-submodule test coverage:** Verifies each submodule commit independently and the parent commit. Does not assert ordering between alpha and beta — correct, as outline.md:265-267 specifies submodules before parent, not a fixed inter-submodule order.

---

## Positive Observations

- `_split_sections` test asserts section names as an equality check (`assert names == ["Files", "Message"]`) — pinned, not substring-matched.
- Helper extraction eliminates ~50 lines of duplicated subprocess setup across two test contexts without introducing unnecessary abstraction.
- `git log --oneline -1` pattern used consistently across m-1, m-3, and pipeline tests — single pattern for commit confirmation.
- render.py fix is a pure deletion (one condition term removed) — no new code, zero regression risk.
