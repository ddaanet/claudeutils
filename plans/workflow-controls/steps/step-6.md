# Step 6

**Plan**: `plans/workflow-controls/runbook.md`
**Common Context**: See plan file for context

---

## Step 6: Update design Skill - Add Tail-Call

**Objective**: Add step 7 that invokes `/handoff --commit` after applying fixes.

**Script Evaluation**: Direct execution (surgical edit)

**Execution Model**: Sonnet

**Implementation**:

Edit `agent-core/skills/design/SKILL.md`.

Find the "### 6. Apply Fixes" section (around line 72-76) and add new step 7 after it:

```markdown
### 7. Handoff and Commit

**CRITICAL: As the final action, invoke `/handoff --commit`.**

This tail-call chains:
1. `/handoff` updates session.md with completed design work
2. Tail-calls `/commit` which commits the design document
3. `/commit` displays STATUS showing next pending task

The next pending task will typically be the planning phase (`/plan-adhoc` or `/plan-tdd`).

**Why:** Universal tail behavior ensures consistent workflow termination. User always sees what's next.
```

**Note:** The Process section intro doesn't currently mention a step count, so no update needed there.

**Expected Outcome**: Design skill chains into handoff → commit → status.

**Unexpected Result Handling**:
- If step count in intro unclear → verify and update

**Error Conditions**:
- Edit fails → report structure

**Validation**:
- Step 7 exists
- Tail-call instruction present
- Process intro updated to 7 steps

**Success Criteria**:
- Tail-call step added
- Chain documented
- Step count correct

**Report Path**: `plans/workflow-controls/reports/step-6.md`

---
