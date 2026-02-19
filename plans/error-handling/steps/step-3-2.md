# Step 3.2

**Plan**: `plans/error-handling/runbook.md`
**Execution Model**: opus
**Phase**: 3

---

## Step 3.2: Update handoff/SKILL.md for failed/blocked task handling

**Objective**: Extend handoff skill to explicitly preserve failed/blocked/canceled tasks (not trim them), and reference task-failure-lifecycle.md for state notation.
**Script Evaluation**: Prose (25-100 lines — targeted additions to 330-line file)
**Execution Model**: Opus (skill artifact)

**Prerequisite**: Read `agent-core/skills/handoff/SKILL.md` section "### 7. Trim Completed Tasks" — understand current trim logic before extending it.

**Implementation**:

1. **Extend Section 7 (Trim Completed Tasks)**:
   Add explicit exclusion rule immediately after "Rule: Delete completed tasks only if BOTH conditions are true":
   > **NEVER trim tasks in blocked `[!]`, failed `[✗]`, or canceled `[–]` states.** These states signal unresolved issues requiring user attention — trimming them on handoff silently loses the signal. Failed/canceled tasks persist until the user explicitly resolves them (retries, abandons, or cancels). This differs from completed `[x]` tasks, which trim after commit + prior session.

2. **Add reference to task-failure-lifecycle.md**:
   In Section 1 (Gather Context) or at the start of Section 7, add:
   > Task failure states ([!] blocked, [✗] failed, [–] canceled) are defined in `agent-core/fragments/task-failure-lifecycle.md`. See that fragment for notation, state transitions, and error context recording template.

**Expected Outcome**: Section 7 explicitly excludes [!], [✗], [–] states from trimming with rationale. task-failure-lifecycle.md referenced.

**Error Conditions**:
- If "Trim Completed Tasks" section has moved or been renamed, search for trim-related content and add the exclusion rule in the appropriate location

**Validation**:
- `grep -n "\[!\]\|\[✗\]\|\[–\]" agent-core/skills/handoff/SKILL.md` returns match in section 7 area
- `grep "task-failure-lifecycle" agent-core/skills/handoff/SKILL.md` returns match
- Rationale for non-trimming present ("signal", "user attention", or equivalent)

---

*Depends on: Phase 2 (escalation-acceptance.md content) AND Phase 3 (task-failure-lifecycle.md state notation)*
