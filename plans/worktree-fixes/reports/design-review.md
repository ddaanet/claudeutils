# Design Review: Worktree Fixes

**Design Document**: `plans/worktree-fixes/design.md`
**Review Date**: 2026-02-13
**Reviewer**: design-vet-agent (opus)

## Summary

The design addresses five worktree bugs across task name validation, session merge, merge commit creation, and session automation. It introduces a well-motivated shared `session.py` module for task-block parsing, reused by both merge conflict resolution and CLI task movement. The architecture is sound, phasing is logical, and design decisions are well-reasoned with clear rationale.

**Overall Assessment**: Ready

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **Test file naming mismatch with existing codebase**
   - Problem: Phase 1 testing section referenced `test_worktree_merge.py`, which does not exist. Existing merge tests are split across `test_worktree_merge_conflicts.py`, `test_worktree_merge_parent.py`, `test_worktree_merge_submodule.py`, etc.
   - Impact: Planner would create a new test file breaking the established naming convention, or waste time determining correct placement.
   - Fix Applied: Updated test file references to `test_worktree_merge_conflicts.py` (for `_resolve_session_md_conflict` tests) and `test_worktree_merge_parent.py` (for `_phase4` MERGE_HEAD tests), with explicit per-test-case file assignments.

### Minor Issues

1. **Function name inconsistency between definition and usage**
   - Problem: Line 74 referenced `validate_task_name(task_name)` but the function defined on line 137 is `validate_task_name_format()`.
   - Fix Applied: Changed to `validate_task_name_format(task_name)` and added note that it raises `ValueError` if invalid.

2. **Phase 3 SKILL.md step references imprecise**
   - Problem: "removes Mode A step 4, Mode B step 4, Mode C step 3" was imprecise. Mode C step 3 is the entire merge success handler (session.md editing + `rm` invocation + output message). Only the session.md editing portion is automated; the rest of the step remains.
   - Fix Applied: Clarified that session.md editing is removed from each step, not the entire steps. Documented that `rm` handles task movement automatically.

3. **`focus_session()` not assigned to a phase**
   - Problem: `focus_session()` changes were listed under cli.py modifications but not explicitly assigned to any phase in the Phase Structure table or descriptions. It depends on `extract_task_blocks()` from Phase 1.
   - Fix Applied: Added "(Phase 1)" annotation to `focus_session()` section, added `cli.py (focus_session)` to Phase 1 files in table, and added `focus_session()` to Phase 1 description.

4. **Missing `find_section_bounds()` usage context**
   - Problem: `find_section_bounds()` was defined in session.py but no caller in the design explicitly referenced it. Both `_resolve_session_md_conflict()` and `move_task_to_worktree()` need section boundary detection.
   - Fix Applied: Added `find_section_bounds()` reference to `_resolve_session_md_conflict()` specification. The function's role in `move_task_to_worktree()` was already implicit from its description (locate Worktree Tasks section).

5. **FR-1.3 acceptance criterion not addressed in focus_session**
   - Problem: Requirements FR-1 acceptance criterion "focus_session() pattern matches constrained names without escaping issues" had no corresponding note in the design's `focus_session()` section.
   - Fix Applied: Added note that constrained task names simplify pattern matching (no complex escaping needed).

## Requirements Alignment

**Requirements Source:** `plans/worktree-fixes/requirements.md`

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1.1: Lossless slugs | Yes | `derive_slug()` changes, Decision 5 |
| FR-1.2: Remove max_length | Yes | `derive_slug()` specification |
| FR-1.3: focus_session pattern matching | Yes | `focus_session()` section (fixed) |
| FR-1.4: Validation function exists | Yes | `validate_task_name_format()` in validation/tasks.py |
| FR-2.1: Precommit scans sections | Yes | Integration into existing `validate()` |
| FR-2.2: Rejects forbidden characters | Yes | `validate_task_name_format()` spec |
| FR-2.3: Clear error message | Yes | Error message format specified |
| FR-2.4: Integration with just precommit | Yes | Existing `claudeutils validate` pipeline |
| FR-4.1: Full multi-line blocks | Yes | `extract_task_blocks()` + `_resolve_session_md_conflict()` |
| FR-4.2: Proper blank line separation | Yes | Merge fix specification |
| FR-4.3: Detection by name | Yes | Decision 1 (TaskBlock as lines) |
| FR-5.1: MERGE_HEAD detection | Yes | `_phase4` changes with code example |
| FR-5.2: branch -d succeeds | Yes | Decision 4 (`--allow-empty`) |
| FR-5.3: No change for non-empty | Yes | Dual-branch code (MERGE_HEAD vs staged check) |
| FR-6.1: new --task moves task | Yes | `move_task_to_worktree()` + `new` command changes |
| FR-6.2: Preserves full block | Yes | TaskBlock preserves all lines |
| FR-6.3: rm conditional removal | Yes | `remove_worktree_task()` branch check logic |
| FR-6.4: Idempotent | Yes | Explicit idempotency noted for both functions |

**Gaps:** None. All requirements traced to design elements.

## Positive Observations

- Shared `session.py` module is well-motivated: two independent features (FR-4 merge fix, FR-6 automation) share the same parsing infrastructure. This avoids duplication and ensures consistent task-block handling.
- `TaskBlock` as opaque lines (Decision 1) is the right abstraction level. Avoiding structured field parsing keeps the implementation simple when the only operation is copy/move.
- Branch-check strategy for `remove_worktree_task()` (Decision 3) elegantly avoids coupling to merge resolution internals. The rationale about "ours" side being unchanged after merge is clear.
- MERGE_HEAD detection (Decision 4) is the correct git-native approach. The dual-branch code example clearly shows both merge and non-merge paths.
- Defense-in-depth validation (Decision 5) matches the project's established pattern and resolves the requirements open question (Q-1) decisively.
- Phase structure has clean dependency ordering: Phase 0 (validation) before Phase 1 (parsing infra) before Phase 2 (automation using both).
- Documentation Perimeter is well-scoped: no unnecessary external research, correct references to existing documentation.

## Recommendations

- The `remove_worktree_task()` branch name assumption (`slug = branch name`) is always true for the current codebase but could be documented as an invariant in session.py, since future changes to branch naming would break this.
- Phase 1 is the largest phase (session.py creation + merge.py fixes + cli.py focus_session update + phase4 MERGE_HEAD fix). The planner should consider cycle count carefully during runbook expansion to stay within reasonable bounds.

## Next Steps

1. Proceed to `/runbook plans/worktree-fixes/design.md` for runbook generation.
