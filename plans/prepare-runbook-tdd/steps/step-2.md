# Step 2

**Plan**: `plans/prepare-runbook-tdd/runbook.md`
**Common Context**: See plan file for context

---

## Step 2: Design Cycle Detection and Parsing Logic

**Objective**: Design regex patterns, control flow, and data structures for TDD cycle detection and parsing.

**Script Evaluation**: Prose description (design task)

**Execution Model**: Sonnet

**Implementation**:

1. Design cycle detection regex:
   - Pattern for `## Cycle X.Y: [name]` format
   - Capture groups for major (X), minor (Y), and name
   - Differentiation from step pattern
2. Design conditional extraction logic:
   - Input: runbook frontmatter with `type` field
   - Control flow: if `type: tdd` → extract cycles, else → extract steps
   - Shared parsing logic where possible
3. Design cycle numbering validation:
   - Sequential major numbers (1, 2, 3...)
   - Sequential minor numbers within major (1.1, 1.2, 1.3...)
   - Gap detection algorithm
   - Duplicate detection algorithm
4. Design cycle content extraction:
   - Full cycle section (including subsections)
   - RED/GREEN/REFACTOR phase preservation
   - Stop conditions inclusion
5. Design data structure for cycles:
   - Mirror existing step data structure
   - Fields: cycle_number, major, minor, name, content
6. Document design decisions:
   - Why specific regex patterns chosen
   - How validation will work
   - Error messages for validation failures

**Expected Outcome**: Complete design specification for cycle detection and parsing.

**Unexpected Result Handling**:
- If requirements conflict with existing code patterns → document alternatives and escalate

**Error Conditions**:
- Design conflicts with existing architecture → Escalate to user

**Validation**:
- Design covers all requirements from planning request § 3.2
- Regex pattern tested with example cycle headers
- Validation algorithm handles edge cases

**Success Criteria**:
- Design document created at report path
- Document includes tested regex pattern
- Document includes validation algorithm pseudocode
- Document includes example data structures

**Report Path**: `plans/prepare-runbook-tdd/reports/step-2-report.md`

---
