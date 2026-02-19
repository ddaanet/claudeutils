# Step 4.2

**Plan**: `plans/error-handling/runbook.md`
**Execution Model**: opus
**Phase**: 4

---

## Step 4.2: Add error handling cross-references to all cooperative skills

**Objective**: Add a brief error handling note to the Continuation section of all four cooperative skills (design, runbook, orchestrate, handoff) — directing each to abort and record in Blockers per the continuation-passing.md protocol.
**Script Evaluation**: Small (≤25 lines — ~5 lines added to each of 4 files)
**Execution Model**: Opus (skill artifacts)

**Prerequisite**: Read all four skill files — `agent-core/skills/design/SKILL.md`, `agent-core/skills/runbook/SKILL.md`, `agent-core/skills/orchestrate/SKILL.md`, `agent-core/skills/handoff/SKILL.md` — locate the Continuation section in each (or identify where to add one).

**Implementation**:
In each skill's Continuation section, add a short error handling note immediately before or after the consumption protocol steps:

```
**On error during this skill's execution:** Abort the remaining continuation — do not propagate to the next skill. Record the failure in session.md Blockers using the template in `agent-core/fragments/task-failure-lifecycle.md`. The continuation-passing.md error protocol is authoritative for the abort-and-record model.
```

Do NOT duplicate the full protocol — these are cross-references only. The skills point to continuation-passing.md as the source of truth.

**Expected Outcome**: All four cooperative skills (design, runbook, orchestrate, handoff) have the error handling note in or near their Continuation/tail-call section. Notes reference continuation-passing.md.

**Error Conditions**:
- If a skill does not have a Continuation section, add the note adjacent to the existing tail-call or handoff invocation (do not restructure the skill's exit flow)

**Validation**:
- `grep "continuation-passing\|abort.*continuation\|Blockers" agent-core/skills/design/SKILL.md` returns match
- `grep "continuation-passing\|abort.*continuation\|Blockers" agent-core/skills/runbook/SKILL.md` returns match
- `grep "continuation-passing\|abort.*continuation\|Blockers" agent-core/skills/orchestrate/SKILL.md` returns match
- `grep "continuation-passing\|abort.*continuation\|Blockers" agent-core/skills/handoff/SKILL.md` returns match

---

*Depends on: Phases 1–4 complete*
