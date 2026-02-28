# Deliverable Review: Task Classification (Code + Test)

**Date:** 2026-02-28
**Reviewer model:** opus
**Design reference:** `plans/task-classification/outline.md`
**Test suite:** 135/135 passing, `just precommit` green

---

## Summary

The implementation correctly delivers the two-section task classification system (D-4 through D-9). The core behavioral change -- static classification with no move semantics -- is clean and significantly simpler than the replaced `move_task_to_worktree()` / `remove_worktree_task()` / `_update_session_and_amend()` machinery. Deleted code (~111 lines net from session.py, ~20 lines from cli.py) removed correctly with no orphaned references in production code.

**Critical findings:** 0
**Major findings:** 1
**Minor findings:** 4

---

## Findings

### [Major] `add_slug_marker` matches first occurrence of task line globally, not within Worktree Tasks section
- **File:** `/Users/david/code/claudeutils-wt/task-classification/src/claudeutils/worktree/session.py`:177-179
- **Axis:** Robustness
- **Description:** After `extract_task_blocks` finds the task in Worktree Tasks, `add_slug_marker` locates the task line in the file by scanning all lines with `if line == task_block.lines[0]`. If the exact same task line text appears in another section (e.g., a reference, a comment, or a task with identical formatting in In-tree Tasks), the marker would be inserted on the wrong line. The function should constrain its search to the Worktree Tasks section bounds, not the entire file. In practice, cross-section task name uniqueness (enforced by `session_structure.py` validation) makes collision unlikely but not impossible -- the uniqueness check is case-insensitive while line matching is exact, and non-task lines could contain matching text. The `remove_slug_marker` function has a similar pattern (line 210-213) but is lower risk since the ` -> \`slug\`` pattern is unlikely to appear outside a task line.

### [Minor] TASK_PATTERN in session_structure.py and session.py does not match `[!]`, `[x]` (checkmark), or `[-]` task statuses
- **File:** `/Users/david/code/claudeutils-wt/task-classification/src/claudeutils/validation/session_structure.py`:12
- **File:** `/Users/david/code/claudeutils-wt/task-classification/src/claudeutils/worktree/session.py`:30
- **Axis:** Functional completeness
- **Description:** The execute-rule.md defines task status notations including `[!]` (blocked), `[x]` (failed -- note: this uses a Unicode checkmark in the spec but `x` in the pattern), and `[-]` (canceled). The regex `r"^- \[[ x>]\] \*\*(.+?)\*\*"` matches `[ ]`, `[x]`, and `[>]` but not `[!]`, `[-]` (canceled with en-dash). This is a pre-existing condition not introduced by this PR, but the task classification work touches these patterns and the new section names increase their surface area. Tasks in blocked/canceled states would be invisible to `extract_task_blocks`, `check_worktree_format`, and `check_cross_section_uniqueness`.

### [Minor] Residual "Pending Tasks" references in tests outside the reviewed file set
- **File:** Multiple test files (see grep output)
- **Axis:** Conformance (D-5)
- **Description:** Several test files outside the reviewed set still use `"## Pending Tasks"` in their fixtures: `test_validation_tasks.py`, `test_validation_tasks_validate.py`, `test_worktree_merge_blocker_fixes.py`, `test_worktree_merge_sections.py`, `test_worktree_merge_parent_conflicts.py`, `test_validation_task_format.py`. These tests still pass because `extract_task_blocks` and `find_section_bounds` are section-name-agnostic -- they parse whatever section name appears. However, this creates a documentation drift: tests describe the old schema while production code documents the new one. Per D-5 (no backward migration -- handoff rewrites on first post-impl handoff), this is expected for existing sessions, but test fixtures should ideally reflect the current schema. Not a functional issue.

### [Minor] `_merge_session_contents` iterates with empty string `""` as third section value
- **File:** `/Users/david/code/claudeutils-wt/task-classification/src/claudeutils/worktree/resolve.py`:80
- **Axis:** Testability
- **Description:** The loop `for section in ("In-tree Tasks", "Worktree Tasks", "")` includes `""` to catch tasks not under any `## ` header. This is a backward-compatibility path for old-format sessions where tasks might appear outside named sections. The `""` case has no direct test coverage -- all merge strategy tests use properly sectioned content. The code path is reachable (tasks before any `## ` header get `section=""` from `extract_task_blocks`), and the `bounds = ... if section else None` guard is correct, but the lack of a test for unsectioned tasks means a regression here would be silent.

### [Minor] `focus_session` output places worktree task under "In-tree Tasks" header
- **File:** `/Users/david/code/claudeutils-wt/task-classification/src/claudeutils/worktree/session.py`:262
- **Axis:** Conformance (D-6)
- **Description:** `focus_session()` reads from "Worktree Tasks" (correct per D-6) but outputs the focused task under `## In-tree Tasks` in the worktree's session.md. This is intentional per the design -- a focused worktree session has a single task that becomes in-tree for that worktree's context. The behavior is well-tested (`test_focus_session_multiline`, `test_focus_session_strips_slug_marker`). Noting for documentation clarity only -- the section name change from the source section to the output section is a semantic transformation, not a bug.

---

## Design Decision Verification

| Decision | Status | Notes |
|----------|--------|-------|
| D-4: Static classification, no move semantics | Verified | `add_slug_marker` modifies in-place; `remove_slug_marker` strips marker only. `move_task_to_worktree` deleted. |
| D-5: No backward migration | Verified | No code migrates "Pending Tasks" to "In-tree Tasks". Old section name still parseable by generic functions. |
| D-6: `focus_session()` reads Worktree Tasks | Verified | Line 247: `section="Worktree Tasks"`. Test coverage confirms Pending Tasks tasks are not found. |
| D-8: `#execute` picks in-tree, `wt` picks worktree | Verified (prose) | Routing is in execute-rule.md prose, not code. `aggregation.py:171` uses `section="In-tree Tasks"` for task summary. |
| D-9: Classification heuristic | Verified (prose) | Heuristic is in handoff skill prose, not code. No code enforces classification rules. |

---

## Cross-Reference Verification

- **API contract:** `session.py` exports `add_slug_marker`, `remove_slug_marker`, `focus_session`, `extract_task_blocks`, `find_section_bounds`, `extract_blockers`. All consumers in `cli.py` and `resolve.py` use correct signatures.
- **Import cleanup:** `_is_merge_of` removed from cli.py imports (was only used by deleted `_update_session_and_amend`). No orphaned imports.
- **Naming consistency:** "In-tree Tasks" and "Worktree Tasks" used consistently across `session.py`, `session_structure.py`, `aggregation.py`, `resolve.py`. No mixed old/new naming in production code.
- **`focus-session.py` (agent-core/bin):** Diff shows +1/-1 but the diff against main is empty, meaning the change was already on main or the file was unchanged. The standalone script uses its own `extract_task` function (not `extract_task_blocks`), searching all sections -- it does not need updating for the section rename since it pattern-matches task lines directly.

---

## Verdict

Ship with awareness of the Major finding. The `add_slug_marker` section-scoping issue has low practical risk due to the cross-section uniqueness validation, but the code's intent (operate within Worktree Tasks) is not structurally enforced. The fix is straightforward: use `find_section_bounds("Worktree Tasks")` to constrain the line search range.
