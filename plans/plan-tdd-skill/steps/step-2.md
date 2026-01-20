# Step 2

**Plan**: `plans/plan-tdd-skill/runbook.md`
**Common Context**: See plan file for context

---

## Step 2: Design Cycle Breakdown Algorithm

**Objective**: Design algorithm for decomposing design documents into atomic TDD cycles.

**Script Evaluation**: Prose description (design task)

**Execution Model**: Sonnet

**Implementation**:

Design algorithm with these components:

1. **Input Validation**:
   - Verify design document format
   - Check for TDD-specific sections (Spike Test, design decisions)
   - Identify unresolved `(REQUIRES CONFIRMATION)` markers

2. **Feature Decomposition**:
   - Parse design document phases/sections
   - Identify behavioral increments
   - Create cycle numbering (X = phase, Y = increment)

3. **Cycle Definition**:
   - For each increment: define RED assertions, expected failure, GREEN minimal implementation
   - Assign dependencies (sequential within phase, cross-phase if needed)
   - Mark regression verification cycles

4. **Validation**:
   - Check dependency graph for cycles
   - Verify all cycle IDs valid (X.Y format)
   - Ensure each cycle has RED/GREEN/Stop Conditions

Document algorithm in `plans/plan-tdd-skill/reports/step-2-algorithm.md`:
- Input validation rules
- Decomposition strategy
- Cycle definition process
- Validation checks
- Edge cases handling

**Expected Outcome**: Algorithm specification for cycle breakdown logic.

**Error Conditions**:
- Cannot determine decomposition strategy → STOP, escalate for design clarification

**Validation**:
- Algorithm document exists
- Contains sections: Input Validation, Decomposition, Validation
- Edge cases documented

**Success Criteria**:
- Clear algorithm for feature → cycles transformation
- Edge cases identified (empty cycles, circular deps, invalid IDs)
- Validation strategy defined

**Report Path**: `plans/plan-tdd-skill/reports/step-2-algorithm.md`

---
