# Step 3.3

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Step 3.3: Add orchestrate template enforcement

**Objective**: Add checkpoint delegation template with structured IN/OUT scope enforcement to orchestrate skill.

**Prerequisites**:
- Read `agent-core/skills/orchestrate/SKILL.md` (current delegation patterns)
- Steps 3.1-3.2 committed (vet-requirement.md enforcement as reference)

**Implementation**:

Update `agent-core/skills/orchestrate/SKILL.md`:

1. **Add checkpoint delegation template section**:
   - Placement: In delegation or checkpoint guidance area
   - Template content:
     ```
     Review [scope description].

     **Scope:**
     - IN: [list what was implemented]
     - OUT: [list what is NOT yet done — do NOT flag these]

     **Changed files:** [file list from git diff --name-only]

     **Requirements:**
     - [requirement 1]
     - [requirement 2]

     Fix all issues. Write report to: [report-path]
     Return filepath or error.
     ```

2. **Add enforcement guidance**:
   - Require structured IN/OUT scope fields (bulleted lists)
   - Fail loudly if empty or prose-only
   - Specify: run precommit first to ground "Changed files" in reality
   - Note: prevents confabulating future-phase issues

**Expected Outcome**: orchestrate skill has checkpoint delegation template with strict IN/OUT scope structure and enforcement guidance.

**Error Conditions**:
- If template missing required fields → verify IN, OUT, Changed files, Requirements all present
- If enforcement guidance weak → add "must" language and failure protocol
- If precommit-first ordering unclear → specify sequence explicitly

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer: "Review orchestrate skill checkpoint delegation template addition. Verify template has all required fields (IN, OUT, Changed files, Requirements), enforcement guidance is strict, and precommit-first ordering is clear."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-3.3-skill-review.md

---

**Phase 3 Checkpoint**:
1. All vet logic updated (taxonomy created, vet-fix-agent uses 4-status, vet-requirement enforces validation, orchestrate has template)
2. Restart session required (agent definition + fragment changes)
3. Proceed to Phase 4

---


**Complexity:** Medium (1 step, ~100 lines, handles 2 FRs)
**Model:** Sonnet
**Restart required:** Yes (agent definition changes)
**Diagnostic review:** Yes (improving outline review)
**FRs addressed:** FR-5, FR-11

**Note on step density**: Single step handles two related criteria (growth validation + semantic propagation) for same agent. Splitting would create unnecessary commits/reviews for same file. Both criteria enhance same review phase (execution readiness).

---
