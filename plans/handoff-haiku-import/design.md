# Design: Import Handoff-Haiku Fix Context from Home Repo

**Input:** 3 commits from `../home` repo (8eb2ebe, 2079274, 49eff39) + agent-core commit 150b178
**Scope:** Import design documents + learnings into claudeutils, sync agent-core reference
**Mode:** General (oneshot)

## Problem Statement

The handoff-haiku fixes (root cause analysis → design → review → implementation) were developed in the `../home` repo. The design documents and learnings need to live in claudeutils alongside agent-core (where the implementation landed). Agent-core already has commit 150b178 but claudeutils session.md and plans/ don't reflect this work.

Additionally, the vet review for commit-unification noted "design/implementation scope misalignment" because the reviewer lacked context about skill composition decisions. The handoff-haiku design provides that context (especially Fix 1: decoupling skills, and design-review Q5: inline vs references for model-specific skills).

## Requirements

**Import:**
- Copy 3 plan documents from `../home` into `claudeutils/plans/`
- Merge 4 new learnings from home session.md into claudeutils session.md
- Update session.md to reflect import completion and handoff-haiku context

**Sync:**
- Agent-core already at 018d631 (3 commits past 150b178) — no submodule action needed
- Stale symlink `handoff-lite` may need cleanup (verify `just sync-to-parent` state)

**Out of scope:**
- Modifying agent-core files (already implemented)
- Vet review reevaluation (separate task, after import)
- Commit (separate task, user controls)

## Plan

### Step 1: Copy Plan Documents

Copy from `../home/plans/` to `claudeutils/plans/`:

```
../home/plans/handoff-lite-issue/transcript.md  → plans/handoff-lite-issue/transcript.md
../home/plans/handoff-lite-fixes/design.md      → plans/handoff-lite-fixes/design.md
../home/plans/handoff-lite-fixes/design-review.md → plans/handoff-lite-fixes/design-review.md
```

These are reference documents — copy as-is, no edits.

### Step 2: Merge Learnings into session.md

Add 4 learnings from home session.md to claudeutils session.md Recent Learnings section. These don't overlap with existing learnings:

- **Skill Model Constraints Must Be Enforced** — name encodes constraint, `user-invocable: false`
- **Template Ambiguity: Replace vs Augment** — PRESERVE/ADD/REPLACE merge semantics
- **Skill Delegation Ambiguity** — decouple skills, two commands
- **Skill Description Overlap Causes Misrouting** — internal skills have no user-facing triggers

### Step 3: Update session.md Status

Update Completed/Pending/Next Steps to reflect:
- Import complete
- Pending tasks shift to: reevaluate vet review, then commit work

### Step 4: Verify Stale Symlinks

Check if `.claude/skills/handoff-lite` symlink exists and is broken. If so, remove it. The `handoff-haiku` symlink should exist (created by `just sync-to-parent`).

## Affected Files

| File | Action |
|------|--------|
| `plans/handoff-lite-issue/transcript.md` | Create (copy from home) |
| `plans/handoff-lite-fixes/design.md` | Create (copy from home) |
| `plans/handoff-lite-fixes/design-review.md` | Create (copy from home) |
| `agents/session.md` | Edit (merge learnings, update status) |
| `.claude/skills/handoff-lite` | Delete if broken symlink |

## Context for Vet Reevaluation

After import, the vet reviewer should note:
- Handoff-haiku Fix 1 established the pattern: decouple skills for separation of concerns
- Design-review Q5 explicitly approved keeping content inline for Haiku consumption
- The commit-unification user edits (reverting to /gitmoji skill invocation) align with the handoff-haiku design philosophy: user controls skill composition decisions
- The vet's "scope misalignment" finding is resolved: user intentionally edited SKILL.md, and the final state is a valid design choice
