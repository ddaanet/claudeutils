# Step 5

**Plan**: `plans/plan-tdd-skill/runbook.md`
**Common Context**: See plan file for context

---

## Step 5: Implement Skill Core Logic

**Objective**: Write skill process implementation in skill.md.

**Script Evaluation**: Prose description (implementation task)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Read to read existing skill.md
- Use Edit to add content after frontmatter
- Never use heredocs

**Implementation**:

Implement the 5-phase process (from Step 3) in skill.md:

1. **Add Introduction Section**:
   - Skill purpose and workflow context
   - When to use vs when not to use
   - Integration with /design and /orchestrate

2. **Add Process Sections** (Phases 1-5):
   - Phase 1: Intake (read design doc, validate format)
   - Phase 2: Analysis (extract goals, check confirmations)
   - Phase 3: Cycle Planning (apply algorithm, generate cycles)
   - Phase 4: Runbook Generation (create runbook file)
   - Phase 5: Validation (verify format, report success)

3. **Add Templates Section**:
   - Runbook frontmatter template
   - Weak Orchestrator Metadata template
   - Cycle definition template (RED/GREEN/Stop Conditions)
   - Common Context template

4. **Add Examples Section**:
   - Sample design document snippet
   - Sample generated cycle
   - Sample complete runbook structure

5. **Add Constraints Section**:
   - Tool usage rules (Read/Write/Edit/Grep, no Bash file ops)
   - Cycle granularity criteria
   - Dependency validation rules
   - Error handling protocol

**Expected Outcome**: Complete skill implementation with all sections.

**Error Conditions**:
- Cannot read skill.md → STOP, report error
- Edit fails → STOP, report error

**Validation**:
- Skill file contains all 5 process phases
- Templates section present
- Examples section present
- File size > 3000 bytes (comprehensive implementation)

**Success Criteria**:
- Complete skill implementation
- All phases documented with clear instructions
- Templates ready for use

**Report Path**: `plans/plan-tdd-skill/reports/step-5-report.md`

---
