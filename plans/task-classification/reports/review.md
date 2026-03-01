# Review: Task Classification — Deliverable Review Fixes

**Scope**: `git diff bdd8fbc5` — deliverable review fix changes (12 files, agent-core submodule dirty)
**Date**: 2026-03-01
**Mode**: review + fix

## Summary

Changes address both Major findings and all 7 Minor findings from the deliverable review (`plans/task-classification/reports/deliverable-review.md`). The session-bounded search fix in `session.py` is correct and tests cover the cross-section collision scenario. The `--task` flag prose fix propagates correctly through execute-rule.md, SKILL.md, and branch-mode.md. All six test files named in Minor finding 7 have been updated. No remaining stale terminology or incorrect CLI references found.

The submodule is dirty (agent-core has uncommitted changes). That is the expected state for this review — the changes are present in the working tree.

**Overall Assessment**: Ready (all issues fixed or explicitly deferred)

---

## Issues Found

### Critical Issues

None.

### Major Issues

1. **`add_slug_marker` searches entire file instead of Worktree Tasks section**
   - Location: `src/claudeutils/worktree/session.py:174-183` (baseline: `:177-179`)
   - Problem: Line search `if line == task_block.lines[0]` iterated all file lines. Identical task text elsewhere in the file could cause the marker to land on the wrong line.
   - Fix: `find_section_bounds("Worktree Tasks")` called before the loop; iteration constrained to `range(section_start, section_end)`. Fallback `(0, len(lines))` handles sessions without a Worktree Tasks section (no regression). Same fix applied to `remove_slug_marker`.
   - **Status**: FIXED

2. **execute-rule.md references nonexistent `--task` flag**
   - Location: `agent-core/fragments/execute-rule.md:226` (baseline)
   - Problem: `_worktree new --task` is not a valid invocation. CLI uses positional `[TASK_NAME]`.
   - Fix: Changed to `` `_worktree new [TASK_NAME]` `` — matches actual CLI signature. Consistent with SKILL.md:123 disclaimer and branch-mode.md update in same diff.
   - **Status**: FIXED

### Major Issues — Agent-Core Submodule

The deliverable review findings that touch agent-core files are addressed in the submodule working tree (not yet committed as a submodule bump). All three files modified:

- `fragments/execute-rule.md` — `--task` → `[TASK_NAME]` (Major 2)
- `skills/worktree/SKILL.md` — "pending tasks" terminology → "all tasks" (Minor 1)
- `skills/worktree/references/branch-mode.md` — three `--task` references removed (Minor 2)

### Minor Issues

1. **worktree SKILL.md stale "pending tasks" terminology (Mode B)**
   - Location: `agent-core/skills/worktree/SKILL.md:50,52,64` (deliverable review baseline)
   - Problem: Mode B steps used "pending tasks" / "all pending tasks" rather than "all tasks".
   - Fix: Updated to "all tasks" in steps 1, 2, 3. No remaining "pending" references in SKILL.md.
   - **Status**: FIXED

2. **branch-mode.md references `--task` flag (three places)**
   - Location: `agent-core/skills/worktree/references/branch-mode.md:15,20,23`
   - Problem: Section header "Prefer `--task` Form", code example `claudeutils _worktree new --task`, and prose "The `--task` form automates all side effects." All contradict SKILL.md:123 which explicitly states there is no `--task` flag.
   - Fix: Header renamed "Prefer Task Name Form"; code example updated to bare positional form; prose updated to "The task name form automates all side effects."
   - **Status**: FIXED

3. **test_worktree_rm.py comment references deleted function**
   - Location: `tests/test_worktree_rm.py:158`
   - Problem: Comment said `remove_worktree_task is only in working tree` — function was deleted; replacement is `remove_slug_marker`.
   - Fix: Updated to `remove_slug_marker is only in working tree`.
   - **Status**: FIXED

4. **TestKeepOursStrategies docstring stale (Worktree Tasks strategy changed)**
   - Location: `tests/test_worktree_merge_strategies.py:102`
   - Problem: Class docstring said "Worktree Tasks... keep ours" but the strategy is additive (union). The parametrized test that exercises Worktree Tasks happens to deduplicate identically-named entries, making it behaviorally correct — but the docstring misrepresented the strategy.
   - Fix: Updated to "sections with additive (union) merge strategy."
   - **Status**: FIXED

5. **`""` (unsectioned tasks) path in `_merge_session_contents` had no test**
   - Location: `src/claudeutils/worktree/resolve.py:80`
   - Problem: Old-format sessions (tasks before any `## ` header) hit the `""` key path. Code correct but regression would be silent.
   - Fix: `TestUnsectionedTasksMerge` class added to `test_worktree_merge_strategies.py` with two tests: `test_unsectioned_tasks_merged_from_theirs` (both tasks present) and `test_unsectioned_dedup_by_name` (de-dup by name).
   - **Status**: FIXED

6. **TASK_PATTERN misses `[!]`, `[✗]`, `[–]` statuses**
   - Location: `src/claudeutils/validation/session_structure.py:12`, `src/claudeutils/worktree/session.py:30`
   - Problem: `r"^- \[[ x>]\] \*\*(.+?)\*\*"` doesn't match blocked, failed, or canceled tasks. Tasks in these states are invisible to extraction, validation, and merge.
   - Investigation:
     1. Scope OUT: not listed in execution context, but deliverable review notes it as pre-existing, not introduced by this PR
     2. Design deferral: not deferred in design — pre-existing defect flagged for awareness
     3. Codebase patterns: no existing fix pattern; pattern used in two places
     4. Conclusion: pre-existing defect, not introduced by this PR. Deliverable review classified it as Minor with note "Pre-existing; not introduced by this PR." Fixing TASK_PATTERN requires evaluating downstream impact (validation behavior changes for blocked/canceled tasks) which is outside this fix scope.
   - **Status**: DEFERRED — pre-existing, not introduced by this PR. Deliverable review explicitly noted "Pre-existing" and the new section names increase surface area. Separate task needed with downstream impact analysis.

7. **Test files with `"## Pending Tasks"` fixtures (outside deliverable set)**
   - Location: six files: `test_validation_tasks.py`, `test_validation_tasks_validate.py`, `test_worktree_merge_blocker_fixes.py`, `test_worktree_merge_sections.py`, `test_worktree_merge_parent_conflicts.py`, `test_validation_task_format.py`
   - Problem: All used `"## Pending Tasks"` in fixtures, documenting old schema.
   - Fix: All six files updated to `"## In-tree Tasks"`. Confirmed zero remaining `"## Pending Tasks"` occurrences in these files.
   - **Status**: FIXED

### Additional cross-section marker tests (new coverage)

Two new tests cover the section-bounded behavior introduced by the Major 1 fix:

- `test_add_slug_marker_identical_task_both_sections` (`test_add_slug_marker.py:127`) — verifies that when an identical task name exists in both In-tree Tasks and Worktree Tasks, only the Worktree Tasks entry receives the marker. Test logic: compare `in_tree_section` (substring before `## Worktree Tasks`) and `worktree_section` (substring from `## Worktree Tasks` onwards). Correct.
- `test_remove_slug_marker_only_modifies_worktree_section` (`test_remove_slug_marker.py:111`) — verifies that a slug pattern appearing in In-tree Tasks prose (e.g., a reference) is not removed. Only the Worktree Tasks marker is stripped. Correct.

---

## Fixes Applied

All issues found in this review were pre-fixed by the diff under review. No additional edits applied by this review pass.

---

## Requirements Validation

Design reference: `plans/task-classification/reports/deliverable-review.md`

| Finding | Status | Evidence |
|---------|--------|----------|
| Major 1: add_slug_marker section-bounded search | FIXED | `session.py:176-183` uses `find_section_bounds` range |
| Major 1: remove_slug_marker section-bounded search | FIXED | `session.py:211-219` uses `find_section_bounds` range |
| Major 2: execute-rule.md `--task` flag | FIXED | `execute-rule.md:226` updated to `[TASK_NAME]` |
| Minor 1: SKILL.md "pending tasks" terminology | FIXED | SKILL.md:50,52,64 updated to "all tasks" |
| Minor 2: branch-mode.md `--task` flag (3x) | FIXED | branch-mode.md header, example, prose all updated |
| Minor 3: test_worktree_rm.py stale comment | FIXED | Line 158 updated |
| Minor 4: TestKeepOursStrategies stale docstring | FIXED | Line 102 updated |
| Minor 5: unsectioned tasks path untested | FIXED | TestUnsectionedTasksMerge class added (2 tests) |
| Minor 6: TASK_PATTERN missing statuses | DEFERRED | Pre-existing; requires downstream impact analysis |
| Minor 7: Pending Tasks fixtures in 6 test files | FIXED | All 6 files updated to In-tree Tasks |

**All Major findings fixed. 6/7 Minor findings fixed. 1 Minor deferred (pre-existing defect, out of scope).**

---

## Deferred Items

- **TASK_PATTERN missing `[!]`, `[✗]`, `[–]` statuses** — Reason: pre-existing defect not introduced by this PR. Deliverable review explicitly marked it pre-existing. Fix requires downstream impact analysis on validation behavior for blocked/failed/canceled tasks.

---

## Positive Observations

- Section-bounded search implementation is minimal and correct: `find_section_bounds` called once, result unpacked with fallback, range-limited loop replaces enumerate. No unnecessary abstraction.
- The `remove_slug_marker` fallback `(0, len(lines))` when Worktree Tasks section is absent preserves no-op behavior for sessions in transition — correct defensive behavior.
- New cross-section collision tests accurately replicate the failure scenario described in the deliverable review (identical task name in both sections).
- The `test_remove_slug_marker_only_modifies_worktree_section` fixture is well-constructed: it places `→ \`task-a\`` in both sections in different forms, verifying the constraint is structural (section bounds) not content-based (unique pattern).
- Unsectioned tasks tests cover both the merge path (tasks from theirs reach result) and dedup path (identical task name deduplicated), matching the two behaviors in the `""` key handler in `_merge_session_contents`.
- The worktree SKILL.md and branch-mode.md changes are consistent: both drop `--task` in favor of the positional form, and SKILL.md drops the "pending" qualifier to match the two-section model.
