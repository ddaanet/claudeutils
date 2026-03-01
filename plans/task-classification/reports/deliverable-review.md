# Deliverable Review: task-classification

**Date:** 2026-02-28
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | Lines (+/-) |
|------|------|-------------|
| Code | src/claudeutils/planstate/aggregation.py | +1/-1 |
| Code | src/claudeutils/validation/session_structure.py | +5/-5 |
| Code | src/claudeutils/worktree/cli.py | +12/-32 |
| Code | src/claudeutils/worktree/resolve.py | +20/-16 |
| Code | src/claudeutils/worktree/session.py | +33/-111 |
| Code | agent-core/bin/focus-session.py | +1/-1 |
| Test | tests/test_add_slug_marker.py | +124/-0 (NEW) |
| Test | tests/test_planstate_aggregation_integration.py | +5/-5 |
| Test | tests/test_remove_slug_marker.py | +108/-0 (NEW) |
| Test | tests/test_validation_session_structure.py | +15/-15 |
| Test | tests/test_worktree_commands.py | +4/-1 |
| Test | tests/test_worktree_merge_conflicts.py | +6/-6 |
| Test | tests/test_worktree_merge_session_integration.py | +249/-0 (NEW) |
| Test | tests/test_worktree_merge_session_resolution.py | +52/-226 |
| Test | tests/test_worktree_merge_strategies.py | +19/-19 |
| Test | tests/test_worktree_new_config.py | +2/-0 |
| Test | tests/test_worktree_new_creation.py | +30/-14 |
| Test | tests/test_worktree_remerge_session.py | +4/-4 |
| Test | tests/test_worktree_rm.py | +10/-100 |
| Test | tests/test_worktree_session.py | +50/-119 |
| Test | tests/test_worktree_session_automation.py | +46/-84 |
| Test | tests/test_worktree_utils.py | +9/-6 |
| Agentic prose | agents/decisions/operational-tooling.md | +4/-4 |
| Agentic prose | agents/memory-index.md | +2/-2 |
| Agentic prose | agent-core/fragments/execute-rule.md | +19/-16 |
| Agentic prose | agent-core/skills/handoff-haiku/SKILL.md | +8/-5 |
| Agentic prose | agent-core/skills/handoff/SKILL.md | +9/-4 |
| Agentic prose | agent-core/skills/prime/SKILL.md | +50/-0 (NEW) |
| Agentic prose | agent-core/skills/worktree/SKILL.md | +5/-5 |

**Totals:** 29 files, +902/-801 lines, net +101

Design conformance: All 9 design scope IN items have corresponding deliverables. No missing deliverables. 7 unspecified deliverables (corrector-identified consistency fixes and test coverage) — all justified.

## Critical Findings

None.

## Major Findings

1. **`add_slug_marker` searches entire file instead of Worktree Tasks section**
   - File: `src/claudeutils/worktree/session.py:177-179`
   - Axis: Robustness
   - After `extract_task_blocks` finds the task in Worktree Tasks, the line search `if line == task_block.lines[0]` iterates all lines in the file. If identical task line text appears elsewhere (another section, a comment, reference content), the marker would be inserted on the wrong line. Cross-section uniqueness validation (`session_structure.py`) mitigates practical risk, but the intent (operate within Worktree Tasks) is not structurally enforced. Fix: constrain line search to `find_section_bounds("Worktree Tasks")` range. `remove_slug_marker` (line 210-213) has the same pattern but lower risk since `→ \`slug\`` is unlikely to appear outside task lines.

2. **execute-rule.md references nonexistent `--task` flag**
   - File: `agent-core/fragments/execute-rule.md:226`
   - Axis: Functional correctness
   - Line 226: "`→ <slug>` added by `_worktree new --task` when worktree created". The CLI uses positional `[TASK_NAME]`, not `--task`. Actual signature: `claudeutils _worktree new [TASK_NAME] [--branch TEXT] [--base TEXT]`. The worktree skill (SKILL.md:123) explicitly documents: "There is no `--task` flag — the task name is always positional." This is new content introduced by this branch. An agent reading execute-rule.md would form an incorrect CLI mental model.

## Minor Findings

**Terminology & naming:**
- `agent-core/skills/worktree/SKILL.md:50,52,64` — Mode B uses stale "pending tasks" terminology. Design scope OUT (Open Question 1), but naming is inconsistent with the rename. Should say "all tasks" or "tasks from both sections" rather than "pending tasks."
- `agent-core/skills/worktree/references/branch-mode.md:15,20,23` — References `--task` flag three times. Pre-existing but contradicts new line 123 ("There is no `--task` flag"). Within-skill contradiction.
- `tests/test_worktree_rm.py:158` — Comment references deleted `remove_worktree_task` function. Should reference `remove_slug_marker`.
- `tests/test_worktree_merge_strategies.py:102` — `TestKeepOursStrategies` class docstring says "Worktree Tasks... keep ours" but the strategy changed to additive (union). Test passes because parametrized case uses same task name (de-dup = keep ours), but docstring is stale.

**Coverage gaps:**
- `src/claudeutils/worktree/resolve.py:80` — The `""` (unsectioned tasks) path in `_merge_session_contents` has no direct test. Old-format sessions with tasks before any `## ` header reach this path. Code is correct but regression would be silent.
- `src/claudeutils/validation/session_structure.py:12`, `src/claudeutils/worktree/session.py:30` — TASK_PATTERN `r"^- \[[ x>]\] \*\*(.+?)\*\*"` doesn't match `[!]` (blocked), `[✗]` (failed), or `[–]` (canceled) statuses from execute-rule.md. Pre-existing; not introduced by this PR but the new section names increase the surface area. Tasks in these states are invisible to extraction, validation, and merge.
- Multiple test files outside deliverable set (`test_validation_tasks.py`, `test_validation_tasks_validate.py`, `test_worktree_merge_blocker_fixes.py`, `test_worktree_merge_sections.py`, `test_worktree_merge_parent_conflicts.py`, `test_validation_task_format.py`) use `"## Pending Tasks"` in fixtures. Functional (section-agnostic parsing) but documents old schema.

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| D-1: `/prime` for ad-hoc plan work | Covered | `prime/SKILL.md` — scoped to ad-hoc, "What This Is Not" excludes workflow optimization |
| D-2: No frozen artifact restriction | Covered | Uses Read calls, allowed-tools: Read, Glob, Skill |
| D-3: Chain-call `/recall` | Covered | Step 2: `Skill(skill: "recall")` with no explicit topic |
| D-3a: D+B compliance | Covered | Step 1 anchors with Glob+Read — concrete tool calls |
| D-4: Static classification, no move semantics | Covered | `add_slug_marker`/`remove_slug_marker`; `move_task_to_worktree` deleted |
| D-5: No backward migration | Covered | execute-rule.md graceful degradation; old name parseable |
| D-6: `focus_session()` reads Worktree Tasks | Covered | session.py:247 `section="Worktree Tasks"` |
| D-7: In-tree first, then Worktree in status | Covered | execute-rule.md STATUS format |
| D-8: `#execute` picks in-tree, `wt` picks worktree | Covered | execute-rule.md MODE 2; aggregation.py:171 `section="In-tree Tasks"` |
| D-9: Classification heuristic | Covered | handoff/SKILL.md:77-80 prescriptive for clear cases, defaults in-tree |
| Handoff two-section task list | Covered | handoff/SKILL.md carry-forward rule, classification section |
| `operational-tooling.md` decision update | Covered | Updated with new pattern, supersession date |

## Summary

- **Critical:** 0
- **Major:** 2
- **Minor:** 7
