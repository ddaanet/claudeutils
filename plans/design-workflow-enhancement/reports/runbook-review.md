# Vet Review: Design Workflow Enhancement Runbook

**Scope**: Runbook at `plans/design-workflow-enhancement/runbook.md`
**Date**: 2026-02-01T16:00:00Z

## Summary

Reviewed runbook for implementing outline-first design workflow with documentation checkpoint and quiet-explore agent. The runbook has solid structure and clear instructions, but contains one critical issue (missing plugin-dev:agent-creator skill), multiple major structural/specification issues, and several minor clarity concerns.

**Overall Assessment**: Needs Significant Changes

## Issues Found

### Critical Issues

1. **plugin-dev:agent-creator skill does not exist**
   - Location: Step 2, lines 143-157; Orchestrator Instructions line 308
   - Problem: Runbook specifies using `plugin-dev:agent-creator` skill for agent review, but this skill is not present in the codebase. Verified via Glob and find — no plugin-dev:* skills exist in `.claude/skills/` directory. Only 17 skills are symlinked, none matching plugin-dev pattern.
   - Fix: Either (1) create the skill first, (2) use different review mechanism (general-purpose opus, vet-agent), or (3) skip review step and rely on just dev validation only. Recommend option 2 (vet-agent) as it already exists and provides implementation review.

### Major Issues

1. **Incorrect line number reference for agent spec**
   - Location: Step 1, line 91
   - Problem: Says "Read design section 'quiet-explore Agent' (lines 128-167)" but design document has 262 total lines. Lines 128-167 are correct (verified via Read).
   - Suggestion: Line reference is actually correct — not an issue. (Downgrading to note in positive observations)

2. **Step 3 structural assumptions not validated**
   - Location: Step 3.1, lines 190-208
   - Problem: Says to replace "Steps 1-7" and references specific sections by step numbers, but actual skill structure uses "Process" with numbered steps 0-7. The section headings are "### 0. Complexity Triage", "### 1. Understand Request", etc. Runbook assumes these exist but doesn't verify.
   - Suggestion: Add validation instruction: "Read full skill file first to identify current section structure and line numbers for changes."

3. **plan-adhoc Point 0.5 insertion location unclear**
   - Location: Step 3.2, lines 210-224
   - Problem: Says to insert "after Point 0.5 heading" but Point 0.5 is at line 95 with heading "### Point 0.5: Discover Codebase Structure (REQUIRED)". The new content block starts with "**0. Read documentation perimeter**" which suggests it should be a separate point (0.4?) not inserted within Point 0.5.
   - Suggestion: Clarify whether this is (a) a new numbered item within Point 0.5's discovery process, or (b) a new Point 0.4 that runs before Point 0.5. Based on design guidance "first action in planner's intake/discovery phase", it should precede Point 0.5.

4. **plan-tdd Phase 1 insertion point ambiguous**
   - Location: Step 3.3, lines 226-236
   - Problem: Says "insert at start of Phase 1" but Phase 1 line 104 has heading "### Phase 1: Intake (Tier 3 Only)" followed by objective and actions. Unclear if new step should be (a) first bullet in Actions list, (b) new section before "Determine design path", or (c) rename existing structure.
   - Suggestion: Specify exact insertion: "Insert as Step 0 before the existing 'Determine design path' section, making it the first action in Phase 1."

5. **Step 3 expected outcome doesn't match actions**
   - Location: Step 3, line 238
   - Problem: Says "All 3 skill files updated" but Step 3.1 is restructuring (not just updating) — replacing Steps 1-7 with Phases A-C. "Updated" understates the scope of changes. Step 3.2 and 3.3 are updates (insertions).
   - Suggestion: Revise to "design skill restructured into 3-phase workflow, plan-adhoc and plan-tdd updated with documentation perimeter reading"

6. **Missing guidance on preserving existing skill content**
   - Location: Step 3.1, line 208
   - Problem: Says "Preserve: Complexity triage (Step 0), plugin-topic skill-loading directive, tail-call to /handoff --commit" but doesn't specify HOW to preserve during restructure. Are these moved into Phase A/C sections? Renamed? Kept in place?
   - Suggestion: Add explicit mapping: "Step 0 complexity triage → keep as-is before Phase A; plugin-topic detection (currently in Step 4) → move to Phase A.5 outline section; tail-call (currently Step 7) → becomes Phase C.5"

7. **Validation criteria too weak for Step 2**
   - Location: Step 2, lines 168-177
   - Problem: Validation checks "No UNFIXABLE critical issues in report" but doesn't check if review actually improved the agent file. Agent-creator might not make any changes if agent is already perfect, or might introduce new issues.
   - Suggestion: Add validation: "Compare agent file before/after review (git diff or Read twice), verify improvements were made or report explains why no changes needed"

### Minor Issues

1. **Success criteria for Step 1 redundant**
   - Location: Step 1, lines 129-133
   - Note: Success criteria duplicates validation checks (lines 123-128). Either remove success criteria section or consolidate with validation.

2. **Step 4 report path inconsistent with quiet execution pattern**
   - Location: Step 4, line 301
   - Note: Uses singular "step-4-symlinks-validation.md" but previous steps use descriptive names (step-1-agent-creation, step-2-agent-review, step-3-skill-updates). Consider "step-4-integration.md" or similar.

3. **Unexpected result handling for Step 3 is vague**
   - Location: Step 3, lines 239-241
   - Note: Says "If skill structure doesn't match expected sections: Read full skill file to identify actual structure, then apply changes" but this should be done BEFORE attempting changes (see Major Issue #2). Consider moving to Implementation section.

4. **Step 4 combines two distinct operations**
   - Location: Step 4, lines 264-301
   - Note: Symlink creation and validation are different concerns. Runbook guidance (line 247) says "combine with a validation step" but this makes debugging harder if symlink succeeds but validation fails. Consider keeping as is (combined is acceptable) or noting that failures should indicate which operation failed.

5. **Design decisions section references learnings.md line numbers**
   - Location: Design Decisions, line 329
   - Note: Says "learnings.md line 85-89" and "lines 74-78" but these line numbers will drift as learnings file grows. Better to reference by topic: "learnings.md: agent-creator integration pattern" and "learnings.md: model selection for interpreting design"

6. **Prerequisites section says "verified via Glob" but doesn't show Glob commands**
   - Location: Weak Orchestrator Metadata, lines 47-48
   - Note: Claims verification but doesn't show evidence. For runbook review context this is fine (I verified separately), but for actual execution this should include the Glob patterns used.

7. **Missing stop condition for infinite revision loops**
   - Location: Design section references Phase B "Iterative Discussion"
   - Note: Design mentions convergence guidance (line 59) but Step 3.1 instructions don't include this. Not critical since Step 3 is about editing skills to implement the workflow, not executing the workflow itself.

## Positive Observations

- **Comprehensive metadata section**: Weak Orchestrator Metadata (lines 17-53) provides clear execution model, dependencies, error escalation paths, and success criteria. This is excellent runbook structure.
- **Common Context section reduces repetition**: Lines 56-80 establish shared knowledge used across all steps, following DRY principle.
- **Correct line number references**: Step 1 line 91 correctly references design lines 128-167 for agent spec (verified).
- **Step 1 agent spec is detailed and complete**: Lines 93-112 provide all necessary YAML fields and system prompt directives from design. Agent creator has everything needed.
- **Step 2 uses cooperative review pattern**: Recognizes that agent-creator works in review mode (line 162), per learnings.md entry.
- **Step 3.1 preserves critical skill elements**: Line 208 explicitly lists what must be preserved during restructure (complexity triage, plugin-topic, handoff tail-call).
- **Step 4 uses absolute paths**: Lines 272-279 use absolute paths throughout, following CLAUDE.md guidance for agent execution.
- **Orchestrator Instructions section provides step-specific overrides**: Line 308 specifies plugin-dev:agent-creator for Step 2, enabling per-step model/agent selection.
- **Dependencies section clearly separates before/after states**: Lines 333-343 define prerequisites and expected outcomes.
- **Design Decisions section provides rationale**: Lines 321-329 explain WHY specific patterns were chosen, not just WHAT to do.

## Recommendations

1. **Critical path fix**: Resolve plugin-dev:agent-creator availability before execution. If skill doesn't exist, either create it as a prerequisite step or substitute with vet-agent sonnet review.

2. **Structural validation**: Add a Step 0 or pre-execution validation that reads all three skill files and reports their current section structure. This prevents execution failures from incorrect assumptions.

3. **Clarify insertion points**: For Steps 3.2 and 3.3, provide exact line numbers or unique text anchors to insert after/before. Current "after Point 0.5 heading" is ambiguous when Point 0.5 has subsections.

4. **Consider splitting Step 3**: design skill restructure (3.1) is complex and high-risk. plan-adhoc and plan-tdd updates (3.2-3.3) are simple insertions. Splitting into separate steps would enable better error recovery and checkpointing.

5. **Add rollback guidance**: If Step 3 fails midway (design skill restructured but plan skills not updated), how should execution recover? Consider adding "Error Conditions" → "Partial completion: git checkout affected files and restart step"

## Next Steps

1. **BLOCKER**: Determine plugin-dev:agent-creator availability. If missing, revise Step 2 to use alternative review mechanism.
2. Apply fixes for Major Issues #2-7 (structural validation, insertion point clarity, preservation mapping, validation criteria).
3. Consider Recommendations #2-5 for robustness improvements.
4. Re-review after fixes applied, particularly Step 2 and Step 3 specifications.
