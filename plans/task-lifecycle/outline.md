# Outline: Task Lifecycle Awareness

## Problem

Two gaps in workflow continuity after skill execution:

1. **Stale task commands in session.md** — After `/design` advances a plan from `requirements` → `designed`, the task command still says `/design plans/X/requirements.md`. Handoff writes what's in session.md verbatim. Next session's `x` runs the stale command.

2. **No session-level continuation guidance** — After running `/design` directly (outside `x`/`xc`), STATUS doesn't indicate what comes next. The CPS default-exit handles the skill chain (`/handoff --commit → /commit`), but STATUS between skill invocations doesn't show where you are in the lifecycle or what the task needs next.

The underlying issue: STATUS reads commands from session.md (static), but `_derive_next_action()` in `inference.py` already computes the correct command from planstate (dynamic). These two sources are disconnected.

## Approach

**Unify command source**: STATUS and handoff both derive task commands from planstate for plan-associated tasks. Session.md commands become the fallback for tasks without plans.

### Change 1: STATUS derives commands from planstate

STATUS already calls `claudeutils _worktree ls` which calls `_derive_next_action()`. The CLI output includes `Plan: X [status] → /correct-command`.

**Current behavior:** STATUS reads session.md for task commands, uses CLI for plan status display.

**New behavior:** For tasks with an associated plan, STATUS uses the CLI-derived command instead of the session.md command. Session.md command used only for tasks without plans.

**Implementation:** execute-rule.md STATUS format: "For tasks with a plan directory, display the CLI-derived next action as the command." The `Next:` section already shows plan status — add the derived command.

### Change 2: Handoff derives commands from planstate

When handoff writes session.md Pending Tasks (Step 2, carry-forward rule), it currently preserves commands verbatim.

**New behavior:** For tasks with an associated plan, handoff reads the plan's current status and derives the command via the same `_NEXT_ACTION_TEMPLATES` mapping. Non-plan tasks keep their static command.

**Implementation:** Handoff skill Step 2 addition: "For each task with a plan directory, check plan status and update the backtick command to match `_NEXT_ACTION_TEMPLATES` mapping."

The mapping (already in `inference.py`):
- `requirements` → `/design plans/{name}/requirements.md`
- `designed` → `/runbook plans/{name}/design.md`
- `planned` → `agent-core/bin/prepare-runbook.py plans/{name}`
- `ready` → `/orchestrate {name}`
- `review-pending` → `/deliverable-review plans/{name}`

### Change 3: STATUS shows session-level continuation

After a skill completes and before handoff runs, STATUS should indicate the natural next steps.

**Detection:** Git tree is dirty (uncommitted changes exist).

**Display:** When tree is dirty, prepend to STATUS output:
```
Session: uncommitted changes
  next: `/handoff`, `/commit`
```

If a plan-associated task's status is `review-pending`, append `/deliverable-review`:
```
Session: uncommitted changes
  next: `/handoff`, `/commit`, `/deliverable-review plans/X`
```

**Note:** This is advisory. The CPS default-exit already chains these for cooperative skills. This covers: (a) non-cooperative skill output, (b) manual edits, (c) interrupted chains.

## Key Decisions

- D-1: Planstate is authoritative for commands, session.md is fallback for non-plan tasks
- D-2: Same `_NEXT_ACTION_TEMPLATES` mapping used everywhere (CLI, STATUS, handoff) — single source of truth
- D-3: Session-level continuation is advisory display only, not execution control (CPS handles execution)
- D-4: Dirty-tree detection is sufficient for session-level — no need to track "which skill ran"

## Scope

**IN:**
- execute-rule.md STATUS format (Change 1 + Change 3)
- handoff/SKILL.md carry-forward logic (Change 2)

**OUT:**
- CPS default-exit changes — CPS works correctly, not broken
- Python code changes — `_derive_next_action()` already exists, no changes needed
- New CLI commands — existing `_worktree ls` output is sufficient

## Affected Files

- `agent-core/fragments/execute-rule.md` — STATUS format adds planstate-derived commands and session-level continuation
- `agent-core/skills/handoff/SKILL.md` — carry-forward rule adds command derivation

## Complexity Assessment

All changes are prose edits to two files. No behavioral code, no cross-file coordination, no implementation loops. Changes are additive (new rules augmenting existing behavior). Execution-ready from outline.
