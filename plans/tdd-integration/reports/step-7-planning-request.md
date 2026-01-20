# Planning Request: /plan-tdd Skill Implementation

**Created**: 2026-01-20
**Runbook**: `plans/tdd-integration/runbook.md`
**Step**: Step 7 of 8

---

## 1. Task Objective

Create new `/plan-tdd` skill for TDD runbook generation that converts design documents into detailed TDD execution plans with RED/GREEN/REFACTOR cycles.

The skill will be the bridge between `/design` (TDD mode) output and `/orchestrate` execution, producing runbooks with cycle definitions, stop conditions, and metadata for the weak orchestrator pattern.

---

## 2. Complexity Rationale

This task requires a separate planning session due to:

**New skill creation with substantial logic:**
- Must transform design document into structured cycle definitions
- Requires cycle breakdown logic (feature → atomic cycles)
- Must generate RED/GREEN/REFACTOR phase templates
- Needs dependency tracking between cycles
- Requires stop condition generation per cycle

**Adaptation of pytest-md reference implementation:**
- Reference implementation available at `~/code/pytest-md/.claude/skills/plan-tdd/`
- Must be adapted to agent-core runbook format and metadata requirements
- Integration with prepare-runbook.py workflow (different from pytest-md standalone execution)

**Complex TDD cycle planning logic:**
- Must decompose features into testable increments
- Requires understanding of minimal implementation approach
- Must generate expected failure messages
- Needs to identify dependencies between cycles
- Must handle `[REGRESSION]` marker logic for existing behavior verification

**Integration with prepare-runbook.py:**
- Depends on Step 6 completion (prepare-runbook.py supports TDD cycles)
- Must produce runbook format compatible with cycle file generation
- Must include metadata for weak orchestrator (runbook type, model, escalation rules)
- Common context section must be extractable for plan-specific agent generation

**Error handling and validation:**
- Must validate design document format
- Must ensure cycle IDs are valid (X.Y format)
- Must verify stop conditions are comprehensive
- Must handle edge cases (empty cycles, circular dependencies)

**Testing strategy needed:**
- How to validate generated runbooks
- How to verify integration with prepare-runbook.py
- Sample runbook creation for validation

---

## 3. Planning Requirements

Based on design document `plans/tdd-integration/design.md` section "TDD Runbook Structure":

### 3.1 Review pytest-md `/plan-design` and `/plan-tdd` Skills

**Reference material:**
- `~/code/pytest-md/.claude/skills/plan-design/SKILL.md` - Design phase planning
- `~/code/pytest-md/.claude/skills/plan-tdd/SKILL.md` - TDD cycle planning

**Adaptation needs:**
- Understand pytest-md's cycle structure and adapt to agent-core runbook format
- Identify differences between standalone pytest-md execution vs agent-core orchestration
- Extract reusable patterns for cycle breakdown logic
- Understand extraction compatibility requirements

### 3.2 Design 4-Point Planning Process for TDD Runbooks

Adapt the standard runbook prep process (Evaluate, Metadata, Review, Split) for TDD-specific needs:

**Point 1 - Evaluate:**
- Read design document (from `/design` TDD mode)
- Validate TDD-specific sections present (Spike Test, REQUIRES CONFIRMATION markers)
- Identify feature scope and decomposition strategy
- Check for unresolved `(REQUIRES CONFIRMATION)` items

**Point 2 - Metadata:**
- Generate weak orchestrator metadata (runbook type: TDD, model: haiku, escalation chain)
- Create Common Context section from design decisions
- Include file paths, conventions, framework specifics
- Add report locations path

**Point 3 - Review:**
- Validate cycle decomposition (atomic, testable increments)
- Verify dependencies are explicit and non-circular
- Check stop conditions are comprehensive
- Ensure minimal implementation guidance is clear

**Point 4 - Split:**
- Generate cycle definitions (one per increment)
- Create RED/GREEN/REFACTOR templates per cycle
- Generate stop conditions
- Output runbook file for prepare-runbook.py processing

### 3.3 Design Cycle Breakdown Logic

**Feature → Cycles decomposition:**
- Identify atomic behavioral increments from design document
- Create cycle numbering scheme (X.Y format where X = feature phase, Y = increment)
- Determine cycle dependencies (sequential vs parallel)
- Mark regression verification cycles with `[REGRESSION]`

**Cycle granularity criteria:**
- Each cycle verifies 1-3 assertions
- Each cycle has clear RED failure expectation
- Each cycle has minimal GREEN implementation
- Cycles are independently verifiable

**Dependency tracking:**
- Explicit `[DEPENDS: X.Y]` markers
- Validation of dependency graph (no cycles)
- Sequential ordering within phases

### 3.4 Design RED/GREEN/REFACTOR Phase Templates

**RED Phase template structure:**
```markdown
### RED Phase
**Test**: [Test function name] in [file path]
**Assertions**:
- [Assertion 1]
- [Assertion 2]
**Expected Failure**: [Exact error message]
```

**GREEN Phase template structure:**
```markdown
### GREEN Phase
**Implementation**: [Minimal implementation description]
**Files**: [Files to modify]
**Minimal**: [Guidance on minimal approach]
```

**REFACTOR Phase:**
- Not included in cycle definition (handled by tdd-task agent baseline protocol)
- Cycle definition focuses on RED/GREEN specifications only

### 3.5 Design Stop Condition Generation

**Standard stop conditions per cycle:**
```markdown
### Stop Conditions
- If RED passes unexpectedly: Check if [REGRESSION], else investigate
- If GREEN fails after 2 attempts: STOP, document, await guidance
```

**Customization:**
- Cycle-specific stop conditions based on complexity
- Architectural decision points requiring escalation
- Integration points with external systems

### 3.6 Design Dependency Tracking Between Cycles

**Dependency markers:**
- `[DEPENDS: X.Y]` - Explicit dependency on cycle X.Y
- `[REGRESSION]` - Verification test, expects pass in RED phase
- No marker - Can run after all dependencies satisfied

**Validation:**
- Dependency graph must be acyclic
- Dependencies must reference valid cycles
- Sequential cycles within phase (X.1 → X.2 → X.3)

### 3.7 Design Metadata Generation for TDD Runbooks

**Frontmatter:**
```yaml
---
name: feature-name
type: tdd
model: haiku
---
```

**Weak Orchestrator Metadata section:**
- Runbook Type: TDD
- Total Cycles: N
- Execution Model: Haiku (tdd-task agent)
- Step Dependencies: Sequential
- Error Escalation: Haiku → Sonnet → User
- Report Locations: plans/<name>/reports/

**Common Context section:**
- Shared knowledge for all cycles
- Design decisions and rationale
- File paths and conventions
- Framework-specific information
- Testing infrastructure details

### 3.8 Create Skill Directory Structure and Frontmatter

**Directory structure:**
```
agent-core/skills/plan-tdd/
├── skill.md          # Main skill implementation
└── (other files as needed)
```

**Skill frontmatter:**
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

### 3.9 Update Skill Documentation

**Documentation to update:**
- Skill README or index (if exists in agent-core/skills/)
- CLAUDE.md references (if skill invocation pattern changes)
- agents/tdd-workflow.md (reference to /plan-tdd skill)

---

## 4. Dependencies

**Step 6 must be complete:**
- `agent-core/bin/prepare-runbook.py` supports TDD cycles
- Script can parse `## Cycle X.Y:` headers
- Script can generate cycle files in `plans/<name>/steps/cycle-X-Y.md` format
- Script can combine tdd-task.md baseline with runbook common context

**pytest-md reference implementation available:**
- `/plan-design` skill at `~/code/pytest-md/.claude/skills/plan-design/`
- `/plan-tdd` skill at `~/code/pytest-md/.claude/skills/plan-tdd/`
- Both accessible for reading and adaptation

**Design document TDD runbook structure specification:**
- `plans/tdd-integration/design.md` section "TDD Runbook Structure"
- Defines required metadata, cycle format, and common context
- Specifies integration with prepare-runbook.py

---

## 5. Reference Material

**pytest-md skills (primary reference):**
- `~/code/pytest-md/.claude/skills/plan-design/SKILL.md`
  - Design phase planning process
  - Spike test approach
  - REQUIRES CONFIRMATION markers
  - Flag reference tables
- `~/code/pytest-md/.claude/skills/plan-tdd/SKILL.md`
  - TDD cycle structure
  - Cycle ID format (X.Y)
  - Dependency markers
  - Stop condition templates
  - Extraction compatibility requirements

**Design document:**
- `plans/tdd-integration/design.md`
  - Section: "TDD Runbook Structure" (lines 105-153)
  - Section: "TDD Task Agent" (lines 155-282)
  - Section: "prepare-runbook.py Updates" (lines 326-352)
  - Complete runbook format specification

**TDD workflow documentation:**
- `agent-core/agents/tdd-workflow.md`
  - Created in Step 2
  - TDD cycle protocol (RED/GREEN/REFACTOR)
  - Refactoring tiers
  - Commit strategy
  - Command reference
  - Stop conditions and escalation

**Existing skills for pattern reference:**
- `agent-core/skills/plan-adhoc/` (if exists) - Oneshot planning pattern
- `agent-core/skills/design/` (if exists) - Design skill structure

---

## 6. Next Action

**Requires separate planning session with Sonnet model.**

**Planning session should produce:**

1. **Detailed skill implementation specification:**
   - Input validation logic
   - Cycle breakdown algorithm
   - Template generation logic
   - Dependency tracking approach
   - Error handling strategy

2. **Skill file structure:**
   - skill.md with complete implementation
   - Frontmatter with metadata
   - Process steps clearly defined
   - Integration points documented

3. **Testing/validation approach:**
   - Sample design document for testing
   - Expected runbook output
   - Validation checklist
   - Integration test with prepare-runbook.py

4. **Implementation plan (if complex):**
   - If skill implementation is >100 lines or requires complex logic
   - Break down into implementation steps
   - Specify testing approach
   - Define success criteria

**Output from planning session:**
- Either: Direct implementation of skill (if straightforward)
- Or: Implementation runbook (if complex enough to warrant steps)

---

## Expected Success Criteria

This planning request is complete when it contains:
- ✅ All 6 required sections (1-6) present
- ✅ Comprehensive planning requirements (3.1-3.9 detailed)
- ✅ Clear dependencies and blockers identified
- ✅ Reference material paths specified
- ✅ Next action explicitly stated
- ✅ File size > 2000 bytes (comprehensive request)

**Ready for:** Delegation to separate planning session (after Step 6 complete).

---
