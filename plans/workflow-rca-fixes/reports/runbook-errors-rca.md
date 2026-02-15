# Root Cause Analysis: Runbook Planning Errors

**Date:** 2026-02-15
**Runbook:** workflow-rca-fixes
**Scope:** Errors introduced during runbook outline → full runbook promotion

---

## Executive Summary

**Findings:** 12 errors identified (3 critical, 8 major, 1 minor) in runbook.md after promotion from outline.

**Root Causes:**
1. Insufficient post-promotion consistency validation
2. Missing mechanical guidance requirements for weak orchestrator
3. Working directory context not enforced in checkpoints
4. Scope drift during detail expansion without FR traceability checks

**Impact:** Critical errors would block execution; major errors would cause confusion and potential failures.

**Status:** All errors fixed in runbook.md. Process improvements needed to prevent recurrence.

---

## Detailed Analysis

### Root Cause 1: Insufficient Post-Promotion Consistency Validation

**Evidence:**

1. **Step 3.1 file size contradiction**
   - Prerequisites: "projected +150 lines exceeds 400-line threshold → split required"
   - Expected Outcome: "vet-fix-agent reduced to ~440" (still exceeds threshold)
   - **Error type:** Numeric claim inconsistency

2. **Step 3.2 field name inconsistency**
   - Uses "Dependencies:" field instead of "Prerequisites:"
   - Other steps use "Prerequisites:" consistently
   - **Error type:** Terminology inconsistency

3. **Step 4.1 scope creep**
   - Phase header: "FRs addressed: FR-5, FR-11" (2 FRs)
   - Implementation: 3 items (growth, semantic propagation, deliverable traceability)
   - Third item not mapped to either FR
   - References FR-10 from Phase 3 (wrong phase)
   - **Error type:** FR traceability break

**Root Cause:**

The runbook was promoted from outline to full format without a final consistency check. The outline review (runbook-outline-review-agent) validates:
- FR coverage (does each FR have a step?)
- Structural soundness
- Dependencies

But it does NOT validate detail-level consistency:
- Field name standardization
- Numeric claim verification
- Implementation-level FR traceability

**Why It Happened:**

Phase 0.95 in the runbook skill has a "sufficiency check" before fast-path promotion, but this check is qualitative ("is outline sufficient detail?"), not mechanical ("are all claims consistent?").

During outline → runbook expansion:
1. Planner adds implementation details
2. Makes local decisions (split vet-taxonomy.md to manage size)
3. Updates expected outcome (440 lines acceptable)
4. But doesn't verify this is consistent with prerequisites (which still say "exceeds threshold")

**Contributing Factor:**

The runbook-outline-review-agent (invoked before promotion) checks outline-level structure but doesn't have access to step-level implementation details (those are added AFTER outline review, during promotion).

---

### Root Cause 2: Missing Mechanical Guidance for Weak Orchestrator

**Evidence:**

1. **Step 2.3: "Fix inline" without tool specification**
   - Says: "Fix inline before promotion"
   - Doesn't specify: Use Edit tool, modify outline, re-check

2. **Step 6.1: "Update TOC if present" without detection method**
   - Says: "Update table of contents if present"
   - Doesn't specify: Grep for "## Table of Contents", what to do if found

3. **Step 6.2: Global replanning triggers too vague**
   - Lists: "Design assumptions invalidated", "Scope creep detected"
   - Doesn't specify: How to detect (3+ UNFIXABLE of same type? Threshold?)

4. **Step 2.1: Complex behavioral vacuity phrasing**
   - Says: "verify step N+1 produces outcome not achievable by extending step N's implementation alone"
   - Doesn't provide: Concrete examples or mechanical test

**Root Cause:**

The runbook assumes a capable orchestrator can interpret procedural guidance and choose appropriate tools/methods. But the weak orchestrator pattern requires mechanical, tool-specific instructions.

**Why It Happened:**

General-step guidance (to be created in Phase 5, Step 5.1 of this very runbook!) doesn't yet exist. The planner filled in implementation guidance using natural language procedural instructions, which work for human readers but not for weak orchestrators.

From the design decisions in this runbook:
- Decision 6: "All general phase types — No TDD phases — all prose edits, no behavioral code changes"
- This is correct (all prose edits)
- But prose edit steps STILL need mechanical guidance for tool selection

**Contributing Factor:**

The review-plan skill (Section 11, to be updated in Phase 2 of this runbook) doesn't yet have General-step criteria for mechanicalness. The TDD sections check for prescriptive code (anti-pattern), but General sections don't check for vague procedures (equivalent anti-pattern).

---

### Root Cause 3: Working Directory Context Not Enforced

**Evidence:**

**Phase 1 Checkpoint missing working directory**
- Says: "Run `just sync-to-parent`"
- Doesn't say: "In agent-core/ directory, run `just sync-to-parent`"
- From sandbox-exemptions.md: "Recipe: `just sync-to-parent` (in agent-core/ directory)"

**Root Cause:**

Checkpoint guidance templates don't include working directory as a required element.

**Why It Happened:**

1. The justfile recipes exist in a subdirectory (agent-core/)
2. The sandbox-exemptions.md fragment documents this requirement
3. But checkpoint steps don't have a "working directory" field in their template
4. Planner assumed context was obvious (it's the only justfile with this recipe)

**Contributing Factor:**

The orchestrate skill doesn't have checkpoint template guidance that includes working directory. From the runbook:

Step 3.3 adds a checkpoint delegation template for vet reviews, but this is for vet delegation, not for general checkpoints. There's no checkpoint template that includes:
- Artifact verification
- **Working directory** (if not project root)
- Command invocation
- Verification steps

---

### Root Cause 4: Scope Drift During Detail Expansion

**Evidence:**

**Step 4.1 adds unmapped feature**
- Phase 4 FRs: FR-5 (growth), FR-11 (semantic propagation)
- Implementation item 3: Deliverable-level traceability
- Not mentioned in FR-5 or FR-11
- Grounding says "caught FR-10" but FR-10 is in Phase 3 (vet execution context)

**Root Cause:**

During runbook promotion (outline → full runbook), the planner added implementation details based on session findings without validating FR traceability.

**Why It Happened:**

Session context included an opus review finding:
- "FR-10 with 2 deliverables but 1 step mapping"
- This was a real finding from interactive review
- Planner incorporated this as a criterion for outline review
- But didn't verify:
  1. Is this already covered by FR-5 or FR-11?
  2. Should this be a new FR?
  3. Does it belong in Phase 4 (outline review) or Phase 5 (design review)?

**Contributing Factor:**

Outline review checks FR coverage at the STEP level:
- "Does each FR have a step?"

But doesn't check FR traceability at the IMPLEMENTATION level:
- "Does each implementation item within a step map to an FR?"

When a step handles 2 FRs (like Step 4.1 handles FR-5 + FR-11), adding a third criterion breaks the mapping unless:
- It's folded into one of the existing FRs, OR
- A new FR is created, OR
- It's moved to a different step/phase

---

## Impact Analysis

### Execution Impact (if not fixed)

**Critical errors:**
- Step 3.1 contradiction would confuse executing agent (is 440 lines acceptable or not?)
- Phase 1 checkpoint would fail (wrong directory for justfile)
- Step 4.1 scope creep would implement unmapped feature (FR audit fails)

**Major errors:**
- Vague procedures would require human interpretation (breaks weak orchestrator)
- Field inconsistency makes runbook harder to parse
- Missing working directory could cause other failures in future runbooks

**Minor errors:**
- Organizational issues reduce readability but don't block execution

---

## Process Gaps

### Gap 1: Post-Promotion Consistency Check

**Current state:** Outline reviewed → promoted to runbook → no final check

**Missing:** Mechanical consistency validation after promotion:
1. Field name consistency (Prerequisites vs Dependencies)
2. Numeric claim verification (thresholds, line counts)
3. Implementation-level FR traceability

**Recommendation:** Add Phase 1.5 (or Phase 0.97) consistency check in runbook skill

---

### Gap 2: Mechanical Guidance Requirements

**Current state:** General-step reference material doesn't exist yet (to be created in Phase 5, Step 5.1 of THIS runbook)

**Missing:** Guidance requiring tool + pattern specification for all procedures

**Recommendation:** When creating general-patterns.md (Step 5.1), include:
- "Mechanical guidance requirement: specify tools and patterns, not just goals"
- Examples of vague vs specific instructions
- Requirement that weak orchestrator can execute without interpretation

---

### Gap 3: Checkpoint Template

**Current state:** Checkpoint guidance ad-hoc, no standard template

**Missing:** Checkpoint template including working directory field

**Recommendation:** Add to orchestrate skill (or runbook skill):
```
**Phase N Checkpoint:**
1. [Artifact verification]
2. Working directory: [specify if not project root, or state "project root"]
3. Run [command with args]
4. [Verification steps]
5. Proceed to Phase N+1
```

---

### Gap 4: Implementation-Level FR Traceability

**Current state:** Outline review checks step → FR mapping

**Missing:** Check that each implementation item within a step maps to the step's FRs

**Recommendation:** Add to runbook skill (Phase 1 or outline review):

"**Implementation FR traceability:**
For each step, verify each implementation item (numbered/bulleted action) contributes to an FR from the step's 'FRs addressed' field. Flag unmapped items as scope creep."

---

## Recommendations Summary

### Immediate (for this runbook execution)

1. ✅ **Fixed:** All 12 errors corrected in runbook.md
2. **Next:** Proceed with execution using corrected runbook

### Process Improvements (for future runbooks)

**High Priority:**

1. **Add post-promotion consistency check**
   - Where: runbook skill, Phase 0.97 or Phase 1.5
   - What: Mechanical validation (fields, numbers, FR traceability)
   - Benefit: Catches detail-level errors before execution

2. **Add mechanical guidance requirement to general-patterns.md**
   - Where: Step 5.1 of this runbook (when creating general-patterns.md)
   - What: Require tool + pattern specification for all procedures
   - Benefit: Ensures weak orchestrator can execute without interpretation

3. **Add checkpoint template with working directory**
   - Where: orchestrate skill
   - What: Standard template including working directory field
   - Benefit: Prevents directory-related failures

**Medium Priority:**

4. **Add implementation-level FR traceability check**
   - Where: runbook skill or outline-review-agent
   - What: Verify each implementation item maps to an FR
   - Benefit: Prevents scope drift during detail expansion

5. **Strengthen review-plan Section 11 for General steps**
   - Where: Phase 2, Step 2.2 of this runbook (already planned)
   - What: Add criteria checking for mechanical guidance sufficiency
   - Benefit: Review catches vague procedures before execution

---

## Lessons Learned

1. **Outline-level review ≠ detail-level consistency**
   - Outline review checks structure and FR coverage
   - Needs separate pass for field names, numeric claims, implementation FR mapping

2. **Procedural language for humans ≠ mechanical instructions for orchestrators**
   - "Fix inline" is clear to human, ambiguous to weak orchestrator
   - Need: "Use Edit tool to modify X, then re-run Y"

3. **Session findings need FR validation before incorporation**
   - Real finding from opus review: deliverable-level traceability gap
   - But adding to implementation without FR mapping creates traceability break
   - Solution: Create new FR or fold into existing FR explicitly

4. **Context that's "obvious" to humans needs to be explicit for agents**
   - Working directory seems obvious (only one justfile has that recipe)
   - But orchestrator needs explicit "cd agent-core" instruction

---

## Timeline of Error Introduction

1. **Outline created:** runbook-outline.md (16 steps, 6 phases)
2. **Outline reviewed:** runbook-outline-review-agent found issues, applied fixes
3. **Interactive opus review:** Found additional issues, applied 3 fixes
4. **Promotion to full runbook:** Outline expanded to full step format
   - **Errors introduced HERE during detail expansion**
   - Field names not standardized (Dependencies vs Prerequisites)
   - Numeric claims not verified against prerequisites
   - Implementation items added without FR validation
   - Procedural language not mechanized
   - Working directory not specified
5. **This review:** All 12 errors found and fixed

**Key insight:** Errors introduced during outline → runbook promotion, not during outline creation. This is the gap in the pipeline.

---

## Validation

All errors have been fixed in runbook.md:
- ✅ C-1: File size threshold clarified (not hard limit, split keeps both manageable)
- ✅ C-2: Working directory added to Phase 1 checkpoint
- ✅ C-3: Deliverable-level traceability removed from Step 4.1 (scope creep)
- ✅ M-1: Execution pattern clarified (parallel edits)
- ✅ M-2: Design-vet-agent verification clarified
- ✅ M-3: Behavioral vacuity examples added
- ✅ M-4: "Fix inline" mechanism specified (Edit tool)
- ✅ M-5: Field name standardized (Dependencies → Prerequisites)
- ✅ M-6: Workflow notation made consistent (vet-fix-agent specified)
- ✅ M-7: TOC check detection method added (Grep pattern)
- ✅ M-8: Global replanning triggers mechanized (thresholds, counts)
- ✅ m-1: Phase 4 note aligned with 2-FR scope

**Next steps:**
1. Commit fixed runbook
2. Execute runbook (errors now resolved)
3. Implement process improvements during execution:
   - Step 2.2: Add mechanical guidance checks to review-plan
   - Step 5.1: Include mechanical guidance requirement in general-patterns.md
   - Step 5.3 or follow-up: Add checkpoint template to orchestrate skill
4. Create separate improvement task for post-promotion consistency check and implementation FR traceability (not in this runbook's scope)

