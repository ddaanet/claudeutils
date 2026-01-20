# Step 6

**Plan**: `plans/plan-tdd-skill/runbook.md`
**Common Context**: See plan file for context

---

## Step 6: Add Cycle Breakdown Guidance

**Objective**: Add detailed guidance for cycle decomposition to skill.md.

**Script Evaluation**: Direct execution (enhancement task)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Read to read skill.md
- Use Edit to add section
- Never use heredocs

**Implementation**:

Add "Cycle Breakdown Guidance" section to skill.md with:

1. **Granularity Criteria**:
   - Each cycle: 1-3 assertions
   - Clear RED failure expectation
   - Minimal GREEN implementation (no over-engineering)
   - Independent verification

2. **Numbering Scheme**:
   - X.Y format where X = feature phase, Y = increment
   - Sequential within phase (1.1 → 1.2 → 1.3)
   - Phases represent logical groupings

3. **Dependency Management**:
   - `[DEPENDS: X.Y]` for explicit dependencies
   - `[REGRESSION]` for existing behavior verification
   - No circular dependencies
   - Dependencies must reference valid cycles

4. **Stop Conditions Generation**:
   - Standard template per cycle
   - Custom conditions for complex cycles
   - Escalation triggers (RED passes unexpectedly, GREEN fails repeatedly)

5. **Common Patterns**:
   - Basic CRUD: 1 cycle per operation
   - Authentication: 1 cycle for happy path, 1 for error handling
   - Integration: 1 cycle for connection, 1 for data exchange
   - Edge cases: separate cycles for boundary conditions

**Expected Outcome**: Comprehensive cycle breakdown guidance added.

**Error Conditions**:
- Edit fails → STOP, report error

**Validation**:
- Section "Cycle Breakdown Guidance" exists in skill.md
- Contains all 5 subsections
- Examples of common patterns present

**Success Criteria**:
- Clear guidance for cycle decomposition
- Common patterns documented
- Dependency rules explicit

**Report Path**: `plans/plan-tdd-skill/reports/step-6-report.md`

---
