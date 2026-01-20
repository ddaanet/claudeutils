---
name: plan-tdd-skill
type: general
model: sonnet
---

# /plan-tdd Skill Implementation Runbook

**Context**: Implement /plan-tdd skill for TDD runbook generation that converts design documents into detailed TDD execution plans with RED/GREEN/REFACTOR cycles.

**Source**: `plans/tdd-integration/reports/step-7-planning-request.md`
**Design**: `plans/tdd-integration/design.md` (sections: TDD Runbook Structure, TDD Task Agent)

**Status**: Draft
**Created**: 2026-01-20

---

## Weak Orchestrator Metadata

**Total Steps**: 9

**Execution Model**:
- Steps 1-3: Sonnet (research, analysis, design)
- Steps 4-7: Sonnet (skill implementation)
- Step 8: Sonnet (documentation updates)
- Step 9: Haiku (validation testing)

**Step Dependencies**: Sequential

**Error Escalation**:
- Sonnet → User: Missing reference files, validation failures, unclear design decisions

**Report Locations**: `plans/plan-tdd-skill/reports/`

**Success Criteria**:
- /plan-tdd skill created at `agent-core/skills/plan-tdd/skill.md`
- Skill can parse design documents and generate TDD runbooks
- Generated runbooks compatible with prepare-runbook.py (type: tdd, Cycle X.Y format)
- Documentation updated (tdd-workflow.md references skill)
- Validation test produces valid TDD runbook

**Prerequisites**:
- Step 6 complete: prepare-runbook.py supports TDD cycles (✓ per session.md)
- pytest-md backup available: `/Users/david/code/pytest-md/.backup/skills/plan-tdd/` (✓ verified)
- Design document: `plans/tdd-integration/design.md` (✓ verified)
- TDD workflow doc: `agent-core/agents/tdd-workflow.md` (created in Step 2)

---

## Common Context

**Key Design Decisions:**

1. **TDD Runbook Format** (from design doc):
   - YAML frontmatter: `type: tdd`, `model: haiku`
   - Common Context section: design decisions, file paths, conventions
   - Cycles: `## Cycle X.Y:` headings (not `## Step`)
   - Cycle structure: RED Phase, GREEN Phase, Stop Conditions
   - Dependencies: `[DEPENDS: X.Y]` or `[REGRESSION]` markers

2. **Cycle Breakdown Principles**:
   - Each cycle verifies 1-3 assertions
   - Clear RED failure expectation
   - Minimal GREEN implementation
   - Sequential ordering within phases (X.1 → X.2 → X.3)

3. **Integration with prepare-runbook.py**:
   - Script already supports TDD cycles (Step 6 complete)
   - Parses `## Cycle X.Y:` headers
   - Generates cycle files: `plans/<name>/steps/cycle-X-Y.md`
   - Combines tdd-task.md baseline with runbook common context

**Project Paths**:
- Skill location: `agent-core/skills/plan-tdd/skill.md`
- TDD workflow doc: `agent-core/agents/tdd-workflow.md`
- Reference implementation: `/Users/david/code/pytest-md/.backup/skills/plan-tdd/SKILL.md`
- Design spec: `plans/tdd-integration/design.md`

**Conventions**:
- Use Read tool for file operations, not cat/head/tail
- Use Write for new files, Edit for modifications
- Use Grep for searching, not bash grep
- Report files in `plans/plan-tdd-skill/reports/`

---

## Step 1: Review pytest-md Reference Implementation

**Objective**: Understand pytest-md /plan-tdd skill structure and extract reusable patterns.

**Script Evaluation**: Direct execution (research task)

**Execution Model**: Sonnet

**Implementation**:

Read and analyze:
1. `/Users/david/code/pytest-md/.backup/skills/plan-tdd/SKILL.md`
2. `/Users/david/code/pytest-md/.backup/skills/plan-design/SKILL.md`

Extract:
- Cycle structure and numbering (X.Y format)
- Dependency markers (`[DEPENDS: X.Y]`, `[REGRESSION]`)
- RED/GREEN specification format
- Stop condition templates
- Extraction compatibility requirements

Document findings in `plans/plan-tdd-skill/reports/step-1-analysis.md`:
- Reusable patterns for agent-core
- Differences between pytest-md standalone vs agent-core orchestration
- Adaptation requirements

**Expected Outcome**: Analysis report documenting reusable patterns and adaptation needs.

**Error Conditions**:
- Reference files missing → STOP, report to user

**Validation**:
- Report exists at specified path
- Report contains sections: Reusable Patterns, Differences, Adaptation Requirements
- Report size > 1000 bytes

**Success Criteria**:
- Clear understanding of pytest-md cycle structure
- Identified patterns applicable to agent-core
- Documented differences requiring adaptation

**Report Path**: `plans/plan-tdd-skill/reports/step-1-analysis.md`

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

## Step 3: Design Skill Process Flow

**Objective**: Design the skill's execution flow from design doc input to runbook output.

**Script Evaluation**: Prose description (design task)

**Execution Model**: Sonnet

**Implementation**:

Design skill process with these phases:

**Phase 1: Intake**
- Read design document path (from user or default location)
- Read CLAUDE.md if exists (project conventions)
- Validate design document format

**Phase 2: Analysis**
- Extract feature name and goals
- Identify design decisions and constraints
- Check for unresolved confirmations
- Determine cycle decomposition strategy

**Phase 3: Cycle Planning**
- Apply cycle breakdown algorithm (from Step 2)
- Generate cycle definitions with RED/GREEN specs
- Assign dependencies and mark regressions
- Generate stop conditions per cycle

**Phase 4: Runbook Generation**
- Create YAML frontmatter (type: tdd, model: haiku)
- Generate Weak Orchestrator Metadata section
- Generate Common Context from design decisions
- Output cycle definitions
- Write to `plans/<feature-name>/runbook.md`

**Phase 5: Validation**
- Verify runbook format
- Check prepare-runbook.py compatibility
- Report success with next action guidance

Document process flow in `plans/plan-tdd-skill/reports/step-3-process-flow.md`:
- Phase breakdown with inputs/outputs
- Error handling per phase
- User interaction points (confirmations)
- Integration with prepare-runbook.py

**Expected Outcome**: Complete skill process flow specification.

**Error Conditions**:
- Process flow has gaps → STOP, clarify design

**Validation**:
- Process flow document exists
- All 5 phases documented
- Error handling specified

**Success Criteria**:
- Clear end-to-end process from design doc to runbook
- User interaction points identified
- prepare-runbook.py integration specified

**Report Path**: `plans/plan-tdd-skill/reports/step-3-process-flow.md`

---

## Step 4: Create Skill Directory and Frontmatter

**Objective**: Create skill directory structure with metadata frontmatter.

**Script Evaluation**: Small script

**Execution Model**: Sonnet

**Tool Usage**:
- Use Bash for mkdir
- Use Write for file creation
- Never use heredocs

**Implementation**:

```bash
mkdir -p agent-core/skills/plan-tdd
```

Create `agent-core/skills/plan-tdd/skill.md` with frontmatter:

```yaml
---
name: plan-tdd
description: Create TDD runbook with RED/GREEN/REFACTOR cycles from design document
model: sonnet
requires:
  - Design document from /design (TDD mode)
  - CLAUDE.md for project conventions (if exists)
outputs:
  - TDD runbook at plans/<feature-name>/runbook.md
  - Ready for prepare-runbook.py processing
---
```

**Expected Outcome**: Skill directory created with frontmatter-only file.

**Error Conditions**:
- Directory creation fails → STOP, report permissions issue
- Write fails → STOP, report error

**Validation**:
- Directory exists: `agent-core/skills/plan-tdd/`
- File exists: `agent-core/skills/plan-tdd/skill.md`
- File contains valid YAML frontmatter

**Success Criteria**:
- Skill directory structure ready
- Frontmatter metadata correct

**Report Path**: `plans/plan-tdd-skill/reports/step-4-report.md`

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

## Step 7: Add Error Handling and Edge Cases

**Objective**: Add error handling and edge case guidance to skill.md.

**Script Evaluation**: Direct execution (enhancement task)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Read to read skill.md
- Use Edit to add section
- Never use heredocs

**Implementation**:

Add "Error Handling and Edge Cases" section to skill.md with:

1. **Input Validation Errors**:
   - Design document not found → Report path, stop
   - Missing TDD sections → Report missing sections, ask if general runbook instead
   - Unresolved `(REQUIRES CONFIRMATION)` → List items, stop for user input

2. **Cycle Generation Errors**:
   - Empty cycle (no assertions) → Report warning, skip cycle
   - Circular dependencies detected → Report cycles involved, stop
   - Invalid cycle ID format → Report invalid IDs, stop
   - Duplicate cycle IDs → Report duplicates, stop

3. **Integration Errors**:
   - Cannot write runbook file → Report path and permissions, stop
   - prepare-runbook.py not available → Report path, stop

4. **Edge Cases**:
   - Single-cycle feature → Valid, generate single cycle
   - No dependencies between cycles → Valid, mark all as parallel-safe
   - All cycles are regressions → Valid, entire test suite verification
   - Cycle depends on future cycle → Invalid, report ordering issue

5. **Recovery Protocols**:
   - Validation failure → Report specific issue, provide fix guidance
   - Partial runbook generation → Clean up partial files, report error
   - User intervention needed → Save state, clear next action

**Expected Outcome**: Comprehensive error handling guidance added.

**Error Conditions**:
- Edit fails → STOP, report error

**Validation**:
- Section "Error Handling and Edge Cases" exists
- All 5 subsections present
- Recovery protocols documented

**Success Criteria**:
- All error conditions documented
- Edge cases handled gracefully
- Recovery protocols clear

**Report Path**: `plans/plan-tdd-skill/reports/step-7-report.md`

---

## Step 8: Update Documentation

**Objective**: Update tdd-workflow.md to reference /plan-tdd skill.

**Script Evaluation**: Direct execution (documentation task)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Read to read tdd-workflow.md
- Use Edit to add reference
- Use Grep to find insertion point

**Implementation**:

Update `agent-core/agents/tdd-workflow.md`:

1. Find workflow entry point section (should mention /design)
2. Add reference to /plan-tdd skill after /design:
   - "After /design (TDD mode), use /plan-tdd to generate TDD runbook"
   - Include link: `agent-core/skills/plan-tdd/skill.md`
3. Add note about prepare-runbook.py step:
   - "After /plan-tdd, run prepare-runbook.py to create execution artifacts"

**Expected Outcome**: tdd-workflow.md updated with /plan-tdd reference.

**Unexpected Result Handling**:
- If tdd-workflow.md doesn't exist → STOP, report (should exist from Step 2)
- If workflow entry point unclear → STOP, ask for guidance on insertion location

**Error Conditions**:
- Read fails → STOP, report file not found
- Edit fails → STOP, report error

**Validation**:
- Grep for "/plan-tdd" in tdd-workflow.md returns match
- Reference includes link to skill.md
- prepare-runbook.py step mentioned

**Success Criteria**:
- tdd-workflow.md references /plan-tdd skill
- Workflow integration documented
- prepare-runbook.py step clear

**Report Path**: `plans/plan-tdd-skill/reports/step-8-report.md`

---

## Step 9: Validation Test

**Objective**: Test /plan-tdd skill with sample design document.

**Script Evaluation**: Medium task (test execution)

**Execution Model**: Haiku

**Tool Usage**:
- Use Write to create sample design doc
- Invoke /plan-tdd skill
- Use Read to verify generated runbook
- Use Bash to run prepare-runbook.py on output

**Implementation**:

1. Create minimal sample design document at `plans/plan-tdd-skill/test-design.md`:
   - Goal: Simple authentication feature
   - 2-3 design decisions
   - 2 behavioral increments (2 cycles expected)

2. Invoke /plan-tdd skill with sample design doc:
   - Should generate runbook at `plans/test-auth/runbook.md`
   - Verify file created

3. Validate runbook format:
   - Has YAML frontmatter with `type: tdd`
   - Has Weak Orchestrator Metadata section
   - Has Common Context section
   - Has 2 Cycle sections (`## Cycle 1.1:`, `## Cycle 1.2:`)
   - Each cycle has RED Phase, GREEN Phase, Stop Conditions

4. Test prepare-runbook.py compatibility:
   ```bash
   python3 agent-core/bin/prepare-runbook.py plans/test-auth/runbook.md
   ```
   - Should create `.claude/agents/test-auth-task.md`
   - Should create `plans/test-auth/steps/cycle-1-1.md` and `cycle-1-2.md`
   - Should create `plans/test-auth/orchestrator-plan.md`

5. Document results in `plans/plan-tdd-skill/reports/step-9-validation.md`:
   - Test design doc used
   - Generated runbook format validation
   - prepare-runbook.py output
   - Any issues found

**Expected Outcome**: Successful test with valid TDD runbook generation and prepare-runbook.py processing.

**Unexpected Result Handling**:
- If /plan-tdd skill invocation fails → Document error, STOP
- If runbook format invalid → Document specific issue, STOP
- If prepare-runbook.py fails → Document error, STOP

**Error Conditions**:
- Sample design doc creation fails → STOP, report error
- Skill invocation error → STOP, report error details
- Validation failures → STOP, report specific validation issues

**Validation**:
- Generated runbook exists
- Runbook has correct format (type: tdd, cycles, sections)
- prepare-runbook.py completes successfully
- All expected artifacts created

**Success Criteria**:
- /plan-tdd skill successfully generates valid TDD runbook
- Runbook compatible with prepare-runbook.py
- All execution artifacts created correctly
- No errors during test execution

**Report Path**: `plans/plan-tdd-skill/reports/step-9-validation.md`

---

## Design Decisions

**Decision 1: Skill Model Selection**
- **Choice**: Sonnet
- **Rationale**: Planning task requires semantic analysis and judgment. Haiku insufficient for design document interpretation and cycle breakdown logic. Opus unnecessary as task follows established patterns.

**Decision 2: Cycle Granularity**
- **Choice**: 1-3 assertions per cycle
- **Rationale**: Balances atomic verification with practical execution speed. Single assertion too granular, >3 assertions risks multiple failure points per cycle.

**Decision 3: Dependency Validation**
- **Choice**: Validate dependency graph for cycles during runbook generation
- **Rationale**: Early detection prevents execution failures. Cheaper to validate during planning than debug during execution.

**Decision 4: Error Handling Strategy**
- **Choice**: Fail fast with clear error messages
- **Rationale**: TDD runbooks critical for execution. Better to stop planning with clear error than generate invalid runbook.

---

## Dependencies

**Before This Runbook**:
- Step 6 complete: prepare-runbook.py supports TDD cycles
- pytest-md reference implementation available (backup)
- Design document with TDD runbook specification

**After This Runbook**:
- /plan-tdd skill ready for use
- Can generate TDD runbooks from design documents
- Integration with /orchestrate for TDD execution
- pytest-md can consume via agent-core submodule

---

## Notes

**Adaptation from pytest-md**:
- pytest-md used standalone execution (no weak orchestrator)
- agent-core uses plan-specific agents with context isolation
- Runbook format differs (YAML frontmatter, Weak Orchestrator Metadata)
- prepare-runbook.py integration required

**Testing Strategy**:
- Step 9 provides basic validation
- Full validation requires real feature implementation (future)
- Can use pytest-md feature as comprehensive test case

**Future Enhancements**:
- Automatic test command detection from project
- Integration with /design for seamless workflow
- Cycle complexity analysis (warn on overly complex cycles)
