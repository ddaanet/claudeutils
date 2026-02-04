# Design Review: Workflow Feedback Loops

**Design Document**: plans/workflow-feedback-loops/design.md
**Review Date**: 2026-02-04
**Reviewer**: design-vet-agent (opus)

## Summary

This design proposes a comprehensive feedback loop architecture with five feedback points (FP-1 through FP-5) inserted at expansion boundaries throughout the design, planning, and execution phases. The architecture adds outline-level validation before full document generation, introduces a "fix-all" policy for review agents, and strengthens input validation across all review agents. The design is well-structured with clear requirements traceability and builds directly on the exploration report's gap analysis.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Fix-All Policy Contradicts Current Tier 1/2 Vet Pattern**
   - Problem: Design specifies "ALL review agents apply ALL fixes" (FR-6), but vet-requirement.md explicitly distinguishes between vet-agent (review only, caller applies fixes) and vet-fix-agent (review + fixes).
   - Impact: Changing vet-agent to apply fixes breaks the Tier 1/2 pattern where the caller (with full context) applies fixes.
   - Suggestion: Clarify that fix-all applies to new agents (outline-review-agent, runbook-outline-review-agent) and enhanced agents in orchestration context, but preserve the vet-agent/vet-fix-agent distinction for caller-context-aware fix application.

2. **Outline Files Added Without Requirements Spec Integration**
   - Problem: Design adds `outline.md` and `runbook-outline.md` as new artifacts but doesn't address how requirements.md should reference or validate against these outlines.
   - Impact: Outlines become yet another document in the chain without clear traceability. Requirements section says "From design's Requirements section" but outlines precede design.
   - Suggestion: Clarify relationship: Should outline validate against requirements before design? Should runbook-outline validate against design's Requirements section?

3. **FP-5 Artifact Scope Ambiguous for Multi-File Changes**
   - Problem: FP-5 specifies artifact as "Git diff of phase changes" but doesn't explain how vet-fix-agent receives this. The agent currently expects files or git commands, not diff output.
   - Impact: Implementation unclear — does orchestrator pass diff as text? Run git commands? Specify changed file list?
   - Suggestion: Specify explicitly how phase changes are scoped to vet-fix-agent (e.g., "Changed files since last checkpoint" with file list, or "Run git diff <previous-checkpoint-commit>..HEAD").

### Minor Issues

1. **New Agents Use Sonnet but design-vet-agent Uses Opus**
   - Note: Both new agents (outline-review-agent, runbook-outline-review-agent) use sonnet, while design-vet-agent uses opus. This may be intentional (outlines are less architecturally complex), but rationale not stated. Consider documenting model selection rationale for consistency with Model Selection for Design Guidance pattern.

2. **Runbook Outline Format Introduces New Artifact Structure**
   - Note: The runbook outline format (lines 182-214) introduces a new document structure that planners must learn. Consider adding this format to a reference location (e.g., agents/decisions/workflows.md) for discoverability.

3. **Phase Boundary Detection Mechanism Not Specified**
   - Note: Design says FP-5 triggers at "explicit `## Phase N` boundaries" but doesn't specify how orchestrator detects these during execution (runbook parsing? step file metadata?).

## Requirements Alignment

**Requirements Source:** Inline (design lines 13-33)

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1: Feedback after expansion steps | Yes | FP-1 through FP-5 checkpoints |
| FR-2: Feedback after implementation phases | Yes | FP-5 phase-vet |
| FR-3: Review agents validate soundness | Yes | Checkpoint Specifications sections |
| FR-4: Review agents validate requirements alignment | Yes | Input Validation Model (lines 84-90) |
| FR-5: Review agents validate design alignment | Yes | Input Validation Model, FP-3/FP-4 specs |
| FR-6: Review agents apply ALL fixes | Partial | Fix Policy section, but contradicts current vet-agent pattern |
| FR-7: Runbook outline step before full runbook | Yes | FP-3 specification |
| FR-8: Review agents validate correct inputs only | Yes | Input Validation Matrix (lines 383-400) |
| NFR-1: Reuse existing skills | Yes | Enhanced agents leverage existing infrastructure |
| NFR-2: Minimize agent proliferation | Yes | Only 2 new agents (outline-review-agent, runbook-outline-review-agent) |

**Gaps:** FR-6 implementation conflicts with established Tier 1/2 vet pattern (see Major Issue 1).

## Positive Observations

- **Thorough Gap Analysis Integration**: Design directly addresses all 7 gaps identified in the exploration report, with explicit checkpoint mapping.
- **Clear Input Validation Matrix**: The validation matrix (lines 383-400) provides unambiguous agent routing, preventing document type confusion.
- **Rejection Pattern Consistency**: Structured error format for wrong document types aligns with existing agent patterns.
- **Documentation Perimeter Properly Scoped**: Required reading files verified to exist (workflows.md, vet-requirement.md, explore-current-feedback.md).
- **Plugin Topic Addressed**: Next steps correctly includes `plugin-dev:agent-development` for new agent creation.
- **Affected Files Comprehensive**: All modified skills and agents listed in Implementation Notes.

## Recommendations

1. **Reconcile Fix-All with Tier Pattern**: Either (a) limit fix-all to orchestration context (vet-fix-agent behavior), (b) create new "outline-fix-agent" variants that fix, or (c) explicitly document why outlines warrant fix-all while code does not.

2. **Add Outline-to-Requirements Traceability**: Define whether outlines must reference requirements and how early validation catches requirements gaps before full design/runbook generation.

3. **Specify Phase Detection Mechanism**: Add implementation note on how orchestrator identifies phase boundaries (e.g., regex pattern on step files, explicit marker in runbook metadata).

4. **Consider Checkpoint Fatigue Mitigation**: Five feedback points per workflow may increase latency. Consider documenting expected token cost increase vs. rework reduction benefit.

## Next Steps

1. Address Major Issue 1: Clarify fix-all policy scope relative to existing vet-agent/vet-fix-agent distinction.
2. Address Major Issue 2: Add requirements-to-outline traceability specification.
3. Address Major Issue 3: Specify phase change artifact delivery mechanism for FP-5.
4. Route to `/plan-adhoc` after design updates accepted.
5. Load `plugin-dev:agent-development` during planning (two new agents).
