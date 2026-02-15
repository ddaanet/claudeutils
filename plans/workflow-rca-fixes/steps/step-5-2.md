# Step 5.2

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 5

---

## Step 5.2: Add density checkpoint, repetition helper, and validation steps to design skill

**Objective**: Enhance design skill Phase C with density validation, helper extraction guidance, agent-name validation, and late-addition completeness check.

**Prerequisites**:
- Read `agent-core/skills/design/SKILL.md` Phase C section
- Read `agents/decisions/runbook-review.md` density axis (reference from Phase 2)

**Implementation**:

Update `agent-core/skills/design/SKILL.md` Phase C:

1. **Add density checkpoint to Phase C (FR-14)**:
   - **Placement**: After outline generation, before deliverables table
   - **Content**:
     - Flag too-granular phases: >8 items per phase, adjacent items <20 LOC delta
     - Flag too-coarse phases: single item handling >3 unrelated concerns
     - Recommend split or merge based on density analysis
   - **Heuristic**: items per phase × avg LOC per item should be 100-300 range

2. **Add repetition helper prescription (FR-15)**:
   - **Placement**: Within Phase C outline guidance or design principles
   - **Content**:
     - When >5 operations follow same pattern (e.g., "update field X in files A, B, C, D, E, F")
     - Recommend extracting helper function/script
     - Threshold: 5+ repetitions of same operation structure
   - **Note**: Reduces token cost and error rate in implementation

3. **Add agent-name validation step (FR-19)**:
   - **Placement**: Phase C validation checklist
   - **Content**:
     - Before finalizing design: Glob agent directories to verify all agent references resolve to actual files
     - Check: `agent-core/agents/`, `.claude/agents/`
     - If agent name doesn't exist: flag as design error (not implementation issue)
   - **Prevention**: Catches outline-review-agent vs runbook-outline-review-agent type errors

4. **Add late-addition completeness check (FR-19)**:
   - **Placement**: Phase C validation checklist (after agent-name validation)
   - **Content**:
     - Requirements added after outline review must trigger re-validation for:
       - Traceability: does new FR map to outline step?
       - Mechanism: does new FR specify concrete implementation approach?
     - If added post-outline without mechanism: flag for completion
   - **Grounding**: FR-18 added during design session bypassed outline-level validation

**Expected Outcome**: design skill Phase C has density checkpoint with LOC-based heuristics, repetition helper guidance with 5+ threshold, agent-name Glob validation, and late-addition re-validation protocol.

**Error Conditions**:
- If density heuristic unclear → add concrete LOC ranges and item count thresholds
- If helper threshold arbitrary → justify with token cost or error rate rationale
- If validation steps non-actionable → specify tools (Glob) and failure actions
- If late-addition check vague → specify what to re-validate and when

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer: "Review design skill Phase C additions. Verify density checkpoint has concrete heuristics, repetition helper has justified threshold, agent-name validation specifies Glob directories, and late-addition check is grounded in session finding with clear re-validation steps."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-5.2-skill-review.md

---
