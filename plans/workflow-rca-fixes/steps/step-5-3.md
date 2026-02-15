# Step 5.3

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 5

---

## Step 5.3: Add deliverable review to workflow terminology

**Objective**: Document deliverable review as post-orchestration workflow step in workflows-terminology.md.

**Prerequisites**:
- Read `agent-core/fragments/workflows-terminology.md` (current workflow route)
- Read `agents/decisions/deliverable-review.md` (context for deliverable identification)

**Implementation**:

Update `agent-core/fragments/workflows-terminology.md`:

1. **Add to implementation workflow route** (after orchestrate, before handoff):
   - Current: `/design` → `/runbook` → [plan-reviewer] → prepare-runbook.py → `/orchestrate` → [vet agent]
   - Updated: `/design` → `/runbook` → [plan-reviewer] → prepare-runbook.py → `/orchestrate` → [vet agent] → **[deliverable-review] (opus)**

2. **Add deliverable review description**:
   - **Trigger**: After orchestration complete, before final handoff
   - **Model**: Opus (architectural assessment)
   - **Scope**: Production artifacts requiring quality assessment
   - **Process**: Parallel opus agents partitioned by artifact type, consolidated findings
   - **Reference**: `/deliverable-review` skill for invocation

3. **Note optional nature**:
   - Required for: multi-artifact plans, novel implementations, architectural changes
   - Optional for: single-artifact plans, routine updates, well-tested patterns
   - User judgment determines applicability

**Expected Outcome**: workflows-terminology.md has deliverable review as documented workflow step with opus model requirement and optional-applicability guidance.

**Error Conditions**:
- If workflow route unclear → verify arrow notation and agent bracketing consistent
- If deliverable review description vague → specify opus requirement and parallel-agent pattern
- If optional-nature ambiguous → add concrete triggers for when required vs optional

**Validation**:
1. Commit changes
2. Delegate to vet-fix-agent: "Review workflows-terminology.md deliverable review addition. Verify workflow route updated with deliverable-review step, description specifies opus and parallel-agent pattern, and optional-nature guidance has concrete applicability criteria."
3. Read review report, grep for UNFIXABLE
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-5.3-vet-review.md

---
