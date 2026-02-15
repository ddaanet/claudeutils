# Step 4.1

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Step 4.1: Add outline growth validation and semantic propagation checklist

**Objective**: Add file growth projection validation and semantic propagation checklist to runbook-outline-review-agent for execution readiness.

**Prerequisites**:
- Read `agent-core/agents/runbook-outline-review-agent.md` (current review criteria)
- Read `plans/workflow-rca-fixes/reports/runbook-outline-review.md` (context from this session's outline review)

**Implementation**:

Update `agent-core/agents/runbook-outline-review-agent.md`:

1. **Add growth validation criterion** (FR-5):
   - **Placement**: Under execution readiness or outline quality section
   - **Content**:
     - Validate projected file sizes vs 400-line threshold
     - Formula: current_lines + (items × avg_lines_per_item)
     - Split phases must precede first phase exceeding 350 cumulative lines
     - Flag outlines with >10 cycles/steps on same file without projection note
   - **Fix action**: Recommend split-phase insertion or consolidation

2. **Add semantic propagation checklist** (FR-11):
   - **Placement**: Under execution readiness section
   - **Content**:
     - When design introduces new terminology/types: verify artifact inventory complete
     - Grep-based classification: producer files (rewrite with new semantics) vs consumer files (update to use new semantics)
     - All files referencing old semantics must appear in outline (producers as rewrites, consumers as updates)
   - **Detection**: Grep design for "terminology change", "rename", "semantic shift" patterns
   - **Fix action**: List missing consumer files, recommend outline items

3. **Add deliverable-level traceability check**:
   - **Grounding**: Interactive opus review this session caught FR-10 with 2 deliverables but 1 step mapping
   - **Content**:
     - Cross-reference outline coverage against design deliverables table, not just FR numbers
     - Each design deliverable row must map to an outline step
     - FRs with multiple deliverables need multiple step mappings
   - **Detection**: Extract deliverables table from design, verify each row has outline step reference
   - **Fix action**: Identify unmapped deliverables, recommend outline additions

**Expected Outcome**: runbook-outline-review-agent has growth projection validation with 350-line threshold and split-phase placement logic, semantic propagation checklist with grep-based classification, and deliverable-level traceability verification.

**Error Conditions**:
- If growth formula unclear → specify calculation with concrete example
- If semantic propagation abstract → add grep patterns and classification criteria
- If traceability check vague → specify table extraction and row-by-row verification
- If placement disrupts flow → integrate within existing execution readiness section

**Validation**:
1. Commit changes
2. Delegate to agent-creator (plugin-dev): "Review runbook-outline-review-agent.md additions. Verify growth validation has concrete formula and 350-line threshold, semantic propagation checklist has grep-based detection and producer/consumer classification, deliverable-level traceability check is grounded in session finding, and all criteria are actionable."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-4.1-agent-review.md

---

**Phase 4 Checkpoint**:
1. Outline review logic updated with growth validation, semantic propagation, and deliverable traceability
2. Restart session required (agent definition changes)
3. Proceed to Phase 5

---


**Complexity:** Medium (4 steps, ~250 lines)
**Model:** Sonnet
**Restart required:** Yes (design-vet-agent.md + workflows-terminology.md fragment)
**Diagnostic review:** No (content edits informed by diagnostic findings)
**FRs addressed:** FR-4, FR-14, FR-15, FR-16, FR-19, FR-20

---
