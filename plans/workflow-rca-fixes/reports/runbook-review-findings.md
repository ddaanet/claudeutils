# Runbook Review Findings: workflow-rca-fixes

**Runbook:** plans/workflow-rca-fixes/runbook.md
**Review Date:** 2026-02-15
**Reviewer:** Sonnet (following runbook-review-guide.md)
**Methodology:** Three-layer context model (Baseline → Common Context → Steps)

---

## Layer 1: Baseline Agent Verification

**Baseline Identified:** quiet-task.md (model: sonnet, no type: tdd → general runbook default)

**Baseline Check:**
- ✅ Tool usage instructions present in quiet-task.md (lines 56-87)
- ✅ Execution protocol defined (When to Proceed/Stop)
- ✅ Error handling patterns specified
- ✅ Output format guidance provided

**Conclusion:** Tool usage reminders NOT required in individual steps (already in baseline).

---

## Layer 2: Common Context Verification

**Common Context Check (lines 43-91):**
- ✅ Requirements Summary: All 20 FRs mapped across 6 phases
- ✅ Scope Boundaries: IN/OUT scope clearly defined
- ✅ Key Constraints: C-1 to C-4 documented
- ✅ Key Design Decisions: 7 decisions with rationale
- ✅ Project Structure: Paths to agents, skills, decisions, fragments

**Conclusion:** Common Context section is complete and appropriate.

---

## Layer 3: Individual Steps Review

### Critical Issues (Block Execution)

#### C-1: Step 3.1 File Size Contradiction

**Location:** Step 3.1, Prerequisites and Expected Outcome (lines 419-474)

**Issue:**
- Line 420 says: "Note: projected +150 lines exceeds 400-line threshold → split required"
- Line 474 says: "Combined file sizes under threshold (taxonomy ~150, vet-fix-agent reduced to ~440)"

**Problem:** 440 lines EXCEEDS the 400-line threshold mentioned in Prerequisites. The step acknowledges the need for a split, proposes creating vet-taxonomy.md, but the Expected Outcome still shows vet-fix-agent at 440 lines.

**Impact:** Executing agent receives contradictory guidance. Is 400 lines a hard limit or not?

**Recommendation:**
- If 400 is hard limit: Expected Outcome should show vet-fix-agent ≤ 400 lines
- If 400 is soft limit: Remove "exceeds threshold" language from Prerequisites, or specify tolerance (e.g., "400-line target, 450 acceptable")
- Clarify whether the split is to prevent future growth or to address current excess

---

#### C-2: Phase 1 Checkpoint Missing Working Directory

**Location:** Phase 1 Checkpoint (lines 233-238)

**Issue:**
Line 234: "Run `just sync-to-parent` with dangerouslyDisableSandbox: true"

**Problem:** The command `just sync-to-parent` must be run from the `agent-core/` directory (per sandbox-exemptions.md fragment), but the checkpoint doesn't specify this.

**Impact:** Orchestrator may run command from wrong directory, causing failure.

**Recommendation:**
Change line 234 to:
"In agent-core/ directory, run `just sync-to-parent` with dangerouslyDisableSandbox: true"

---

#### C-3: Step 4.1 Scope Creep and FR Traceability Break

**Location:** Step 4.1, Implementation item 3 (lines 643-652)

**Issues:**
1. **Unmapped feature:** Implementation adds "deliverable-level traceability check" which doesn't map to FR-5 or FR-11 (the only FRs for Phase 4)
2. **Wrong FR reference:** Line 649 says "Grounding: Interactive opus review this session caught FR-10..." but FR-10 is "Vet execution context enforcement" (Phase 3), not outline review
3. **Density note inconsistency:** Line 612 note says "Single step handles two related criteria" but implementation has THREE items

**Problem:** This is scope creep during detail expansion. The outline likely had 2 items (FR-5, FR-11), but during full runbook expansion, a third feature was added without FR mapping.

**Impact:**
- Breaks FR traceability (can't verify all FRs implemented if new features appear unmapped)
- Confuses which phase owns which functionality
- The FR-10 reference is likely a copy-paste error

**Recommendation:**
Option 1: Remove deliverable-level traceability from Step 4.1 (out of scope for Phase 4)
Option 2: Add it as part of FR-11 definition (if it's a type of completeness check)
Option 3: Create new FR-21 and add to Phase 4's FRs addressed list
Option 4: Move to Phase 5 with design-vet-agent enhancements (more appropriate location)

**Preferred:** Option 4 - move to Step 5.4 (design-vet-agent already adds cross-reference validation; deliverable traceability fits better there)

---

### Major Issues (Clarity/Consistency)

#### M-1: Step 1.3 Execution Pattern Ambiguous

**Location:** Step 1.3, Implementation (lines 195-215)

**Issue:**
Line 196 says "Update frontmatter for 5 agents in single edit session" but then lists actions as numbered items 1-5.

**Problem:**
- "Single edit session" suggests parallel execution (one message, 5 Edit calls)
- Numbered list suggests sequential steps
- Tool batching guidance (CLAUDE.md) says "Different files: Edit in parallel when independent"

**Impact:** Orchestrator may execute sequentially instead of in parallel, wasting round-trips.

**Recommendation:**
Add execution pattern guidance:
"Use parallel Edit calls in single message for all 5 agents (independent files, no dependencies)."

---

#### M-2: Step 1.3 Design-Vet-Agent Verification Confusing

**Location:** Step 1.3, Implementation item 2 (lines 201-203)

**Issue:**
Lines 202-203: "Verify `skills: [project-conventions]` present (early bootstrap)" - Add if missing"

**Problem:**
- "Verify ... present" implies checking existing state
- "(early bootstrap)" is cryptic - what does this mean?
- "Add if missing" makes it conditional, but step doesn't provide detection guidance

**Impact:** Executing agent unclear whether to check-then-add or just add unconditionally.

**Recommendation:**
Clarify intent:
- If already present: "Verify `skills: [project-conventions]` exists (added in early bootstrap), skip if already present"
- If might be missing: "Add `skills: [project-conventions]` if not already present (Read file first to check)"

---

#### M-3: Step 2.1 Behavioral Vacuity Phrasing Complex

**Location:** Step 2.1, Implementation item 4 (lines 278-282)

**Issue:**
Line 279 (TDD): "For each cycle pair (N, N+1) on same function, verify N+1's RED assertion would fail given N's GREEN."
Line 280 (General): "For consecutive steps modifying same artifact, verify step N+1 produces outcome not achievable by extending step N's implementation alone."

**Problem:** These are complex conditional statements requiring sophisticated reasoning. Weak orchestrator with haiku/sonnet may struggle to apply this mechanically.

**Impact:** May be misapplied or skipped during execution.

**Recommendation:**
Add concrete detection heuristic:
"**Heuristic (both):** cycles/steps > LOC/20 signals consolidation needed."

Already present (line 282), good. But consider adding examples:
- TDD example: "Cycle 5 adds getter, Cycle 6 adds setter for same field → merge into single cycle"
- General example: "Step 3 creates file, Step 4 adds one function to same file → merge into single step"

---

#### M-4: Step 2.3 "Fix Inline" Mechanism Ambiguous

**Location:** Step 2.3, Gate content (lines 368-375)

**Issue:**
Line 374: "Fix inline before promotion. If unfixable, fall through to Phase 1 expansion."

**Problem:** "Fix inline" doesn't specify tools or mechanism. Should agent:
- Use Edit to modify outline?
- Create temporary file?
- Just mental note and continue?

**Impact:** Weak orchestrator cannot execute open-ended procedural guidance.

**Recommendation:**
Specify mechanism:
"Fix inline before promotion (use Edit tool to modify outline, then re-check criteria). If unfixable, fall through to Phase 1 expansion."

---

#### M-5: Step 3.2 Field Name Inconsistency

**Location:** Step 3.2, Dependencies field (line 496)

**Issue:**
Line 496: "**Dependencies**: Step 3.1 (vet-taxonomy.md must exist and be committed)"

**Problem:** Other steps use "**Prerequisites**" for this purpose. "Dependencies" should be for inter-step blocking (orchestration-level), while "Prerequisites" is for prep work (step-level).

**Impact:** Terminology inconsistency makes runbook harder to parse mechanically.

**Recommendation:**
Change to:
"**Prerequisites**:
- Step 3.1 committed (vet-taxonomy.md must exist as reference)
- Read `agent-core/fragments/vet-requirement.md` (current state)"

---

#### M-6: Step 5.3 Workflow Notation Inconsistent

**Location:** Step 5.3, Implementation item 1 (lines 837-840)

**Issue:**
Line 838: "Current: ... → `/orchestrate` → [vet agent]"
Line 839: "Updated: ... → **[deliverable-review] (opus)**"

**Problems:**
1. "[vet agent]" doesn't specify WHICH vet agent (vet-agent vs vet-fix-agent vs design-vet-agent)
2. Notation inconsistency: "[vet agent]" has no model specified, but "[deliverable-review] (opus)" does

**Impact:**
- Unclear which vet agent the workflow uses
- Inconsistent notation makes workflow route harder to parse

**Recommendation:**
Standardize notation:
"Current: ... → `/orchestrate` → [vet-fix-agent] (sonnet)
Updated: ... → [vet-fix-agent] (sonnet) → [deliverable-review] (opus)"

---

#### M-7: Step 6.1 TOC Check Ambiguous

**Location:** Step 6.1, Implementation item 3 (lines 956-958)

**Issue:**
Line 957: "Update table of contents if present"

**Problem:** Doesn't specify:
- How to detect if TOC exists (Grep pattern? Section heading?)
- What "update" means (regenerate? manually edit?)
- What format TOC would be in

**Impact:** Executing agent cannot mechanically apply this step.

**Recommendation:**
Add detection and action guidance:
"Grep SKILL.md for '## Table of Contents' heading. If found, update section by removing Phase 1.4 entry. If not found, no action needed."

Or if TOC doesn't actually exist:
"Verify no table of contents exists (Grep for '## Table of Contents'). If found, update. Most skills don't have TOCs, likely no action needed."

---

#### M-8: Step 6.2 Global Replanning Triggers Vague

**Location:** Step 6.2, Implementation item 3 (lines 992-1001)

**Issue:**
Lines 998-1001 list global replanning triggers:
- "Design assumptions invalidated by implementation"
- "Scope creep detected during execution"
- "Runbook structure broken"
- "Test plan inadequate"

**Problem:** These are vague conditions. How would a weak orchestrator detect them? They need mechanical patterns or thresholds.

**Impact:** Triggers cannot be applied programmatically, only by human judgment.

**Recommendation:**
Add detection criteria:
- "Design assumptions invalidated": 3+ consecutive UNFIXABLE issues citing same design assumption
- "Scope creep detected": 5+ new requirements discovered during execution (threshold)
- "Runbook structure broken": Circular dependencies detected, or >50% of remaining items blocked
- "Test plan inadequate": Coverage drops below 80% (or other metric), or critical path untested

These are still heuristics, but they're measurable.

---

### Minor Issues (Quality/Style)

#### m-1: Step 2.1 Numbering Structure

**Location:** Step 2.1, Implementation (lines 262-282)

**Issue:**
Items 1-3 are restructuring operations, item 4 is adding new content. The flat numbering doesn't reflect this conceptual grouping.

**Problem:** Makes structure harder to scan.

**Recommendation:**
Group as:
```
**Part A: Restructure existing axes (1-4)**
1. Four axes restructure (vacuity, ordering, density, checkpoints):
   [content]

**Part B: Add new axis**
2. Add file growth as 5th axis:
   [content]

**Part C: Update terminology**
3. Update process section:
   [content]

**Part D: Add detection criteria**
4. Add behavioral vacuity detection:
   [content]
```

Alternative: Keep flat if restructure and additions are interleaved in the actual editing work.

---

## Summary

### Issue Counts
- **Critical:** 3 issues (block execution)
- **Major:** 8 issues (clarity/consistency problems)
- **Minor:** 1 issue (organizational)

### Critical Issues Summary
1. **Step 3.1:** File size contradiction (400-line threshold vs 440-line outcome)
2. **Phase 1 Checkpoint:** Missing working directory for `just sync-to-parent`
3. **Step 4.1:** Scope creep (unmapped deliverable-level traceability, wrong FR reference)

### Recommendation
**Status:** NEEDS_REVISION (critical issues must be fixed before execution)

**Priority fixes:**
1. Resolve Step 3.1 file size threshold contradiction
2. Add working directory to Phase 1 checkpoint
3. Address Step 4.1 scope creep (remove, remap, or create new FR)

**Secondary fixes (major issues):**
- Standardize field names (Prerequisites vs Dependencies)
- Add mechanical guidance where vague ("fix inline", "update TOC if present")
- Clarify execution patterns (parallel vs sequential)
- Add detection criteria for triggers

---

## False Positives Avoided

Per runbook-review-guide.md, the following were NOT flagged:

✅ **Tool usage reminders** - Present in quiet-task.md baseline (lines 56-87)
✅ **Execution protocol** - Present in quiet-task.md baseline
✅ **Report file handling** - Present in quiet-task.md baseline
✅ **Error escalation patterns** - Present in quiet-task.md baseline
✅ **Project paths** - Present in Common Context section (lines 85-90)
✅ **Key constraints** - Present in Common Context section (lines 63-67)

These are in higher layers and do NOT need to be repeated in individual steps.

---

## Validation Checklist

- [x] Baseline agent identified and verified
- [x] Common Context checked for completeness
- [x] Individual steps reviewed for step-specific content only
- [x] Did NOT flag information already in baseline/common context
- [x] Checked for contradictions and inconsistencies
- [x] Verified FR traceability
- [x] Checked for mechanical guidance sufficiency
- [ ] All critical issues resolved (pending fixes)

