# Step 4

**Context**: Read `execution-context.md` for full context before executing this step.

---

### Step 4: Design YAML Configuration Schema

**Objective**: Design the YAML configuration format for composition definitions.

**Script Evaluation**: Medium design task - prose description

**Execution Model**: Sonnet (schema design)

**Implementation**:
1. Read core module design from Step 2
2. Read CLI design from Step 3.3
3. Review existing emojipack compose.yaml for reference
4. Design YAML schema structure:
   - `sources`: Path mappings (YAML anchors for deduplication)
   - `fragments`: Ordered list of fragments to compose
   - `output`: Output file path
   - `mode`: Composition mode (agents, role, skill)
   - Optional sections (validation, decorators, etc.)
5. Define schema validation rules:
   - Required fields
   - Field types
   - Path validation (files must exist)
   - Fragment order preservation
6. Create complete examples:
   - Simple CLAUDE.md generation (agents mode)
   - Role file generation (role mode)
   - Multi-project example with anchors
7. Write to: `scratch/consolidation/design/yaml-schema.md`
8. Write execution log to: `plans/unification/reports/phase3-step4-execution.md`

**Expected Outcome**: YAML schema document with:
- Complete schema definition
- Validation rules
- Multiple complete examples
- Usage guidance

**Unexpected Result Handling**:
- If schema becomes too complex: Propose simplified version, escalate if trade-offs unclear
- If emojipack pattern conflicts with design.md: Document conflict, escalate for decision

**Error Conditions**:
- Core module or CLI design not found → Escalate (previous steps may have failed)
- Cannot determine appropriate schema structure → Document alternatives, escalate
- Validation requirements unclear → Propose basic validation, escalate for requirements

**Validation**:
- Design document exists at expected path
- Schema structure fully defined
- Validation rules specified
- At least 3 complete examples provided
- Examples cover different modes (agents, role)

**Success Criteria**:
- YAML schema design created at `scratch/consolidation/design/yaml-schema.md`
- Document includes:
  - Complete schema definition (all fields, types, structure)
  - Validation rules (required fields, types, path checks)
  - Examples (at least 3: simple, role mode, multi-project)
  - YAML anchor usage pattern (per design.md)
- Schema matches emojipack pattern from design.md
- Execution report documents schema decisions

**Report Path**: `plans/unification/reports/phase3-step-4.md`
**Artifact Path**: `scratch/consolidation/design/yaml-schema.md`

---


---

**Execution Instructions**:
1. Read execution-context.md for prerequisites, critical files, and execution notes
2. Execute this step following the actions listed above
3. Perform validation checks as specified
4. Document results in execution report
5. Stop on any unexpected results per communication rules
