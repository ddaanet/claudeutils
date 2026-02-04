# Design Review: Workflow Feedback Loops

**Design Document**: plans/workflow-feedback-loops/design.md
**Review Date**: 2026-02-04
**Reviewer**: design-vet-agent (opus)

## Summary

This design introduces five feedback checkpoints across design, planning, and execution workflows to catch errors earlier. The architecture is well-structured with clear agent responsibilities, input validation matrices, and consistent patterns. All fixes applied during this review.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

All major issues have been fixed:

1. **Fix policy inconsistency for vet-agent/tdd-plan-reviewer**
   - Problem: Original design said "Change fix policy: Apply ALL fixes" for vet-agent/tdd-plan-reviewer, but earlier section correctly identified them as "review-only agents (caller applies fixes)"
   - Impact: Would have created contradiction with established Tier 1/2/3 pattern from vet-requirement.md
   - Fix: Clarified that vet-agent and tdd-plan-reviewer remain review-only; only new outline agents and design-vet-agent get fix-all policy
   - **Status**: FIXED

2. **Missing prerequisite for FP-1: /design Phase A.5 behavioral change**
   - Problem: Current /design skill presents outline inline in conversation, but FP-1 depends on outline being written to file
   - Impact: FP-1 would fail because `plans/<job>/outline.md` does not exist in current workflow
   - Fix: Added explicit "Prerequisite change to /design skill" note and marked Phase A.5 as "BEHAVIORAL CHANGE" throughout
   - **Status**: FIXED

3. **vet-fix-agent fix policy discrepancy**
   - Problem: Original design listed vet-fix-agent under "Fix-all agents" but later said "Fix-all policy already applies" while existing agent only does critical/major
   - Impact: Ambiguous whether to change vet-fix-agent behavior
   - Fix: Clarified vet-fix-agent keeps existing critical/major policy because implementation fixes carry higher risk than document fixes
   - **Status**: FIXED

### Minor Issues

All minor issues have been fixed:

1. **Missing Bash tool in agent specs**
   - Note: Added Bash to both outline-review-agent and runbook-outline-review-agent tool lists for consistency with other agents
   - **Status**: FIXED

2. **Vague enhancement description for design-vet-agent**
   - Note: Changed "Add Step 0.5" to "Add requirements input validation" since the agent already has Step 4.5 for requirements; clarified what the enhancement actually does
   - **Status**: FIXED

3. **Missing explicit "(review-only)" annotations in FP-4**
   - Note: Added explicit annotations to clarify callers apply fixes, consistent with earlier sections
   - **Status**: FIXED

4. **Risk areas incomplete**
   - Note: Added risk for behavioral change in /design Phase A.5 requiring user adjustment
   - **Status**: FIXED

## Requirements Alignment

**Requirements Source:** inline

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Y | Architecture: Feedback Checkpoint Model (5 FPs) |
| FR-2 | Y | FP-5: Phase Boundary Review |
| FR-3 | Y | Each FP specifies review criteria |
| FR-4 | Y | Agent Input Validation Model, all FPs include requirements validation |
| FR-5 | Y | FP-2 through FP-5 validate against design |
| FR-6 | Y | Fix Policy section, fix-all for outline/design agents |
| FR-7 | Y | FP-3: Runbook Outline Review |
| FR-8 | Y | Input Validation Matrix, rejection patterns |
| NFR-1 | Y | Reuses vet-agent, vet-fix-agent, tdd-plan-reviewer, design-vet-agent |
| NFR-2 | Y | Only 2 new agents (outline-review, runbook-outline-review) |

**Gaps:** None

## Positive Observations

- Clear separation of concerns: outline review (structure) vs design review (architecture) vs implementation review (code)
- Input validation matrix provides comprehensive view of what each agent accepts/rejects
- Preserves existing Tier 1/2/3 pattern from vet-requirement.md rather than overriding it
- Phase-by-phase expansion with fallback for small runbooks balances thoroughness with efficiency
- Documentation Perimeter correctly references all required reading for planner
- Next steps correctly includes plugin-dev:agent-development for new agent creation

## Recommendations

None. Design is ready for planning.

## Next Steps

1. Proceed to `/plan-adhoc` for runbook generation
2. Load `plugin-dev:agent-development` before planning (2 new agents to create)
