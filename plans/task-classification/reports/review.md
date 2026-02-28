# Review: Task Classification Implementation

**Scope**: All changes since baseline `ee824b64` (Feature 1: `/prime` skill; Feature 2: task classification)
**Date**: 2026-02-28
**Mode**: review + fix

## Summary

Two features implemented: a new `/prime` skill for ad-hoc plan context loading, and a two-section task classification model replacing the single "Pending Tasks" section with "In-tree Tasks" + "Worktree Tasks". Core implementation is solid — `session.py`, `cli.py`, `resolve.py`, `session_structure.py`, `aggregation.py`, `handoff/SKILL.md`, and `execute-rule.md` are all correctly updated. Three issues found: stale docstring comments in `session.py`, stale "Pending Tasks" move-semantics language in `worktree/SKILL.md`, and untested behavior in `test_worktree_session.py` which exercises the old "Pending Tasks" section name and would miss regressions in the new section name flow.

**Overall Assessment**: Ready (all issues fixed)

---

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Worktree skill describes old move semantics and wrong source section**
   - Location: `agent-core/skills/worktree/SKILL.md:36`, `:44`, `:56`, `:71`, `:131`
   - Problem: Mode A Step 1 says "locate task in Pending Tasks". Mode A Step 4 note says "`new` command automatically moves the task from Pending Tasks to Worktree Tasks". Mode B Step 2 says "Check Pending Tasks section for explicit ordering hints". Mode B Step 4 says "The `new` command automatically moves each task to the Worktree Tasks section." Usage Notes bullet says "`new` moves the task from Pending Tasks to Worktree Tasks... `rm` removes the task from Worktree Tasks when it was completed in the worktree branch (checked via `git show`)." These all describe the old move-semantics design: task lives in "Pending Tasks", gets moved by `new`, gets removed by `rm`. The new design: tasks start in "Worktree Tasks" (classified at creation), `new` adds `→ slug` marker, `rm` removes just the marker.
   - Fix: Update Mode A Step 1 to "locate task in Worktree Tasks". Update the automated notes to describe add/remove marker semantics, not move/remove task semantics.
   - **Status**: FIXED

2. **`test_worktree_session.py` exercises old section names in core tests**
   - Location: `tests/test_worktree_session.py:14–95`, `:97–131`
   - Problem: `test_extract_single_line_task`, `test_find_section_bounds_existing`, `test_find_section_bounds_not_found`, `test_extract_multi_line_task` all use `## Pending Tasks` and verify `blocks[0].section == "Pending Tasks"`. `test_extract_section_filter` uses `## Pending Tasks` as the primary section alongside `## Worktree Tasks`. These tests pass because `extract_task_blocks` is section-agnostic (it captures whatever section name is in the content), but they don't verify the new "In-tree Tasks" path. A regression to the In-tree section parsing would not be caught. The carry-forward graceful degradation rule in execute-rule.md says "Old section name ('Pending Tasks') → treat as 'In-tree Tasks'" — which confirms backward compat is intentional — but core parsing tests should exercise the new canonical name.
   - Fix: Update the content fixtures in core parsing tests (`test_extract_single_line_task`, `test_find_section_bounds_existing`, `test_find_section_bounds_not_found`, `test_extract_multi_line_task`) to use `## In-tree Tasks` as the primary section. Keep `test_extract_section_filter` updated since it also covers `## Worktree Tasks`. The `test_focus_session_*` and `test_focus_session_worktree_only` tests already use correct section names.
   - **Status**: FIXED

### Minor Issues

1. **Stale docstring examples in `session.py` `TaskBlock` and `extract_task_blocks`**
   - Location: `src/claudeutils/worktree/session.py:14`, `:22`
   - Problem: `TaskBlock.section` inline comment says `# Section name: "Pending Tasks" or "Worktree Tasks"`. `extract_task_blocks` docstring param says `section: Optional section name filter ("Pending Tasks", "Worktree Tasks")`. Both reference "Pending Tasks" — the old section name. The new canonical sections are "In-tree Tasks" and "Worktree Tasks".
   - Fix: Update both to list `"In-tree Tasks"` instead of `"Pending Tasks"`.
   - **Status**: FIXED

2. **`handoff-haiku/SKILL.md` still references "Pending Tasks" section**
   - Location: `agent-core/skills/handoff-haiku/SKILL.md:26`, `:38`, `:57`
   - Problem: Haiku handoff skill lists "Pending Tasks" as a MERGE section and uses that name in the template. Under the new two-section model it should list "In-tree Tasks" and "Worktree Tasks" separately. This is a behavioral issue — haiku handoffs would generate "Pending Tasks" instead of "In-tree Tasks"/"Worktree Tasks", accumulating format drift.
   - Fix: Update MERGE list to "In-tree Tasks", "Worktree Tasks"; update merge semantics header; update template.
   - **Status**: FIXED

3. **`agent-core/bin/focus-session.py` still writes `## Pending Tasks`**
   - Location: `agent-core/bin/focus-session.py:207`
   - Problem: The standalone Python script `focus-session.py` generates focused session content with `## Pending Tasks` header. The Python implementation in `session.py` (`focus_session()`) now correctly writes `## In-tree Tasks`. The CLI uses `session.py`, so normal flow is correct. However `focus-session.py` is a separate script — if invoked directly it produces stale format. This creates a dual-implementation divergence.
   - Fix: Update `focus-session.py` line 207 to write `## In-tree Tasks`.
   - **Status**: FIXED

---

## Fixes Applied

- `agent-core/skills/worktree/SKILL.md` — Updated Mode A Step 1, Step 4 note, Mode B Step 2 and Step 4, Usage Notes bullet to describe "Worktree Tasks" source and add/remove marker semantics rather than move-from-Pending-Tasks semantics.
- `tests/test_worktree_session.py` — Updated `test_extract_single_line_task`, `test_find_section_bounds_existing`, `test_find_section_bounds_not_found`, `test_extract_multi_line_task`, `test_extract_section_filter` to use `## In-tree Tasks` as the canonical primary section name.
- `src/claudeutils/worktree/session.py:14,22` — Updated `TaskBlock.section` inline comment and `extract_task_blocks` docstring to list `"In-tree Tasks"` instead of `"Pending Tasks"`.
- `agent-core/skills/handoff-haiku/SKILL.md` — Updated MERGE section list and template to use "In-tree Tasks" and "Worktree Tasks".
- `agent-core/bin/focus-session.py:207` — Updated `## Pending Tasks` to `## In-tree Tasks`.

---

## Requirements Validation

No explicit requirements context provided. Implementation validated against design `plans/task-classification/outline.md`.

| Design Decision | Status | Evidence |
|---|---|---|
| D-1: `/prime` for ad-hoc work only | Satisfied | `prime/SKILL.md` scoped to ad-hoc use, no workflow skill modifications |
| D-2: No frozen artifact restriction | Satisfied | Uses Read calls, not @ref injection |
| D-3: Chain-call `/recall` | Satisfied | Step 2 invokes Skill(skill: "recall") |
| D-3a: D+B compliance | Satisfied | Step 1 anchors with Glob+Read calls |
| D-4: Static classification, no move semantics | Satisfied | `add_slug_marker`/`remove_slug_marker` implemented; `move_task_to_worktree` deleted |
| D-5: No backward migration | Satisfied | execute-rule.md adds graceful degradation for old "Pending Tasks" name |
| D-6: `focus_session()` reads from "Worktree Tasks" | Satisfied | `session.py:247` uses `section="Worktree Tasks"` |
| D-7: In-tree first, then Worktree in status | Satisfied | execute-rule.md STATUS format shows In-tree first |
| D-8: `#execute` picks in-tree, `wt` picks worktree | Satisfied | MODE 2 behavior updated in execute-rule.md |
| D-9: Classification heuristic | Satisfied | `handoff/SKILL.md` Task classification section |

**Gaps:** None relative to design scope IN list. Scope OUT items (worktree skill Mode B scan scope, `_worktree merge` session autostrategy) not flagged.

---

## Positive Observations

- `add_slug_marker` and `remove_slug_marker` are focused, minimal replacements — exactly what the design called for. No scope creep from the deleted `move_task_to_worktree`/`remove_worktree_task`.
- `_merge_session_contents` refactor (resolve.py) cleanly generalizes to iterate both sections with a for-loop rather than special-casing "Pending Tasks". Strategy table comment updated in sync.
- `session_structure.py` validation correctly checks cross-section uniqueness using "In-tree Tasks" (not "Pending Tasks") as the pending side, and validates `→ slug` format only for Worktree Tasks.
- `_task_summary` in `aggregation.py` correctly reads from "In-tree Tasks" — this is the right source for main-tree task display.
- `focus_session()` correctly strips the `→ slug` marker before writing the focused session (so the worktree session doesn't see its own slug redundantly).
- Test coverage for `add_slug_marker`, `remove_slug_marker`, and `session_structure.py` validation is thorough and uses the correct section names throughout.
- `operational-tooling.md` decision entry updated with correct date and new pattern description.
- `handoff/SKILL.md` classification heuristic (D-9) is prescriptive for clear cases and defaults to In-tree when uncertain — matches design recommendation from Open Questions §2.
- execute-rule.md backward compat note ("Old section name ('Pending Tasks') → treat as 'In-tree Tasks'") prevents breakage on existing session files during migration (D-5).

## Recommendations

- `agent-core/skills/reflect/SKILL.md` (lines 148, 168) and `agent-core/skills/next/SKILL.md` (line 19) reference "Pending Tasks" but in shelved/roadmap file contexts rather than live session.md — low-risk deferred cleanup appropriate once the rest of the ecosystem has migrated through handoffs.
- `agent-core/skills/worktree/SKILL.md` Mode B still reads "all pending tasks" generically (step 1) and "Pending Tasks section" (step 2 logical dependencies). Now that classification is static, Mode B should read from "Worktree Tasks" only — but this is scope OUT per outline.md ("`wt` scan scope" listed as Open Question, not implemented here). Leave for follow-up.
