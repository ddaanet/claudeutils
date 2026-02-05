# RCA: Prose Gates Invisible to Execution-Mode Cognition

## Deviation Instance

Commit skill Step 0 (session freshness check) skipped. Agent loaded skill, jumped directly to `just precommit` (Step 1). Session.md was stale — said "COMPLETE" while 7 parity fixes + test plan were uncommitted and undocumented.

## Pattern: Three Recurrences

| Instance | What was skipped | Skill/Rule | Rule clarity |
|---|---|---|---|
| Phase boundary checkpoint | vet-fix-agent delegation | orchestrate 3.4 | Unambiguous |
| Vet before commit | vet review of production artifacts | vet-requirement.md | Unambiguous |
| Session freshness check | handoff before commit | commit skill Step 0 | Unambiguous |

All three: **"stop and verify" gate rationalized away despite clear rules.**

## Surface Diagnosis (Insufficient)

"Behavioral — agent rationalized past clear rule under momentum."

This diagnosis implies a discipline fix (stronger language, "no exceptions"). But three recurrences with strengthened language each time proves discipline fixes don't work.

## Structural Root Cause

**Execution-mode cognition optimizes for "next tool call."** Steps without tool calls get scanned but not executed.

### Evidence: Commit Skill Step Structure

| Step | Type | First action |
|---|---|---|
| 0 (freshness) | Prose judgment | "check if stale" (mental comparison) |
| 0b (vet) | Prose judgment | "were production artifacts created?" |
| 1 (validate) | **Bash command** | `just precommit` |
| 2 (draft) | Generation | Write commit message |
| 3 (gitmoji) | Read + select | Read index, pick emoji |
| 4 (commit) | **Bash command** | `git add && git commit` |

Steps 0 and 0b are the only steps with no tool call. They are **cognitive gates** requiring the agent to stop and evaluate. Every other step has a concrete first action.

### Generalized Pattern

Same structure exists across skills:
- **Orchestrate:** checkpoint delegation is prose between concrete cycle executions
- **Vet requirement:** "delegate to vet" is prose between "write code" and "commit"

**Pattern:** Prose gates between concrete execution steps get skipped because execution-mode cognition gravitates toward the next actionable tool call.

### Why "Behavioral" Misdiagnoses This

- Implies the agent willfully chose to skip the gate
- Actual mechanism: the gate doesn't register during execution-mode scanning
- Strengthening language ("MUST", "no exceptions") doesn't help — the text isn't being evaluated, it's being scanned past
- Each recurrence added stronger language; each recurrence still failed

## Fix Directions (Not Yet Implemented)

### Option A: Concrete Gate Actions

Give prose gates a mandatory tool call as first action:
- Step 0: Script that checks session.md freshness (compares timestamps, scans for staleness indicators)
- Step 0b: Script that lists uncommitted production artifacts
- Result: Gate becomes a command to run, not a judgment to make

### Option B: Gate-Before-Command Structure

Restructure skill so prose gates BLOCK the first bash command:
- Move `just precommit` after gate evaluation
- Force the agent to produce gate evaluation output before any tool call

### Option C: Hook Enforcement

Pre-commit hook that validates session.md freshness:
- Check if session.md was modified in this commit
- Check if production files changed but session.md didn't
- Hard fail if stale

### Option D: Skill Structure Convention

Establish convention: every skill step MUST have a concrete first action (tool call, file read, command). Pure prose judgment steps are an anti-pattern in skill design.

## Open Questions

- Does Option A create false confidence? (Script passes → gate "done" without real evaluation)
- Does Option D over-constrain skill design? Some gates genuinely require judgment
- Is the real fix at the skill-design level or the execution-pattern level?
- Would a "gate checklist" pattern work? (Emit explicit pass/fail for each gate before proceeding)

## Status

RCA complete. Fix implementation deferred for further analysis.
