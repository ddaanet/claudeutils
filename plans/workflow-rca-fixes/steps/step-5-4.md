# Step 5.4

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 5

---

## Step 5.4: Add review criteria to design-vet-agent

**Objective**: Add cross-reference agent-name validation and mechanism-check criteria to design-vet-agent.

**Prerequisites**:
- Read `agent-core/agents/design-vet-agent.md` (current review criteria)
- Step 5.2 committed (design skill validation as parallel reference)

**Implementation**:

Update `agent-core/agents/design-vet-agent.md`:

1. **Add cross-reference criterion (FR-20)**:
   - **Placement**: Under completeness or verification section
   - **Content**:
     - Glob agent directories (`agent-core/agents/`, `.claude/agents/`) to verify all agent names referenced in design resolve to actual files
     - Check deliverables table, phase specifications, any prose mentioning "agent X"
     - Flag mismatches: agent referenced but doesn't exist, or name typo (e.g., outline-review-agent vs runbook-outline-review-agent)
   - **Grounding**: Design targeted wrong agent in current plan

2. **Add mechanism-check criterion (FR-20)**:
   - **Placement**: Under feasibility or clarity section
   - **Content**:
     - For each FR or deliverable specifying behavior change: verify concrete mechanism present
     - Red flags: "improve", "enhance", "better" without specifying how
     - Requirements: algorithm description, data structure choice, control flow change, or reference to existing pattern
     - Flag mechanism-free specifications that planner cannot implement
   - **Grounding**: FR-18 in current plan lacked implementation approach

**Expected Outcome**: design-vet-agent has cross-reference criterion with Glob-based validation and mechanism-check criterion flagging behavior-without-mechanism patterns.

**Error Conditions**:
- If cross-reference unclear → specify Glob patterns and what to verify
- If mechanism-check abstract → add concrete red flags and requirement examples
- If criteria placement disrupts flow → integrate within existing sections (completeness, feasibility)

**Validation**:
1. Commit changes
2. Delegate to agent-creator (plugin-dev): "Review design-vet-agent.md criteria additions. Verify cross-reference criterion specifies Glob directories and validation logic, mechanism-check has concrete red flags and mechanism requirements, and both are grounded in session findings."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-5.4-agent-review.md

---

**Phase 5 Checkpoint**:
1. All content edits complete (runbook references, design skill, workflows terminology, design-vet-agent)
2. Restart session required (design-vet-agent change + workflows-terminology.md fragment loaded via CLAUDE.md)
3. Proceed to Phase 6

---


**Complexity:** Low (2 steps, ~50 lines)
**Model:** Sonnet
**Restart required:** No
**Diagnostic review:** No
**FRs addressed:** FR-6, FR-17

---
