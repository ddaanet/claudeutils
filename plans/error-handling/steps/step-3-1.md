# Step 3.1

**Plan**: `plans/error-handling/runbook.md`
**Execution Model**: opus
**Phase**: 3

---

## Step 3.1: Create task-failure-lifecycle.md fragment

**Objective**: Create new fragment defining the extended task state model — blocked, failed, and canceled states with notation, state machine, error recording template, and grounding.
**Script Evaluation**: Small (create new file, ~35 lines)
**Execution Model**: Opus (fragment artifact)

**Prerequisite**: Read `agent-core/fragments/error-handling.md` and scan `agents/session.md` (already in context via CLAUDE.md @-reference) — understand existing `[x]` complete notation before adding new states.

**Implementation**:
Create `agent-core/fragments/task-failure-lifecycle.md` with:

1. Section: "Extended Task State Notation (D-2)" — define the three new states:
   - `- [!] **Task Name** — reason: [why blocked]` — blocked: waiting on external signal, transitions back to pending when unblocked
   - `- [✗] **Task Name** — failed: [what failed and why]` — failed: terminal, system-detected; requires explicit user decision to retry or abandon
   - `- [–] **Task Name** — canceled: [reason]` — canceled: terminal, user-initiated; distinct from failed (intentional choice vs system detection)
   - All three states include mandatory reason text — state without reason is invalid notation

2. Section: "State Machine" — transitions:
   ```
   pending → in-progress → complete [x]
                         → blocked  [!]  → pending (when unblocked)
                         → failed   [✗]  (terminal — user decision required)
                         → canceled [–]  (terminal — user-initiated)
   ```
   - Blocked is the only non-terminal non-complete state (can return to pending)
   - Failed and canceled both require explicit user action — handoff does NOT trim them
   - Grounding: Subset of Temporal WorkflowExecutionStatus (Running, Completed, Failed, Canceled, TimedOut — TimedOut maps to blocked in practice)

3. Section: "Error Context Recording Template" — when transitioning a task to blocked/failed/canceled, record:
   ```markdown
   - [✗] **Task Name** — failed: [brief reason]
     - Error: [error category from error-classification.md] — [specific message]
     - Chain: [which skill failed] → [continuation that was pending]
     - Resume: fix [root cause]; `r` to resume
   ```
   Use `[!]` for blocked (pending fix), `[✗]` for failed (terminal), `[–]` for canceled.

**Expected Outcome**: New file `agent-core/fragments/task-failure-lifecycle.md` exists with state notation, state machine, and recording template.

**Error Conditions**:
- STOP if file already exists (unexpected state)

**Validation**:
- `test -f agent-core/fragments/task-failure-lifecycle.md` succeeds
- All 3 new state symbols present: `[!]`, `[✗]`, `[–]`
- State machine section present
- Recording template present with Chain and Resume fields

---
