# Step 1: pytest-md Reference Implementation Analysis

**Date**: 2026-01-20
**Analyzed Files**:
- `/Users/david/code/pytest-md/plans/r-flag-parity-design.md`
- `/Users/david/code/pytest-md/plans/r-flag-parity-phase-1-2.md`
- `/Users/david/code/pytest-md/agent-core/skills/task-plan/skill.md`

---

## Reusable Patterns

### 1. Cycle Structure

**Format observed in pytest-md:**

```markdown
### Cycle X.Y: [Cycle Name]

**RED: [Description of test to write]**

[Implementation details]

**Expected RED output:**
```
[Expected failure message]
```

**Why it fails:** [Explanation]

**Verify RED:** [How to confirm RED]

---

**GREEN: [Description of minimal implementation]**

[Implementation details]

**Verify GREEN:** [How to confirm GREEN]

**Verify no regression:** [How to check existing tests]
```

**Key elements:**
- Clear X.Y numbering (X = phase, Y = increment)
- RED section with expected failure message
- GREEN section with minimal implementation
- Explicit verification steps
- Regression check

### 2. Dependency Markers

**Observed patterns:**
- `[DEPENDS: X.Y]` - Explicit dependency on another cycle
- `[REGRESSION]` - Test for existing behavior

**Usage:**
- Placed in cycle title or first line
- Indicates execution order constraints
- Helps orchestrator understand parallelization limits

### 3. Stop Conditions

**Standard template from design doc:**

```markdown
**STOP IMMEDIATELY if:**
- A new test passes on first run (should be RED)
- Test failure message doesn't match expected
- Test passes after partial implementation
- Any existing test breaks (regression)

**Required actions when stopped:**
- Document what happened in session.md
- Investigate why test didn't fail as expected
- If feature already works correctly:
  - Convert test to regression test, mark `[REGRESSION]`
  - Mark cycle complete, proceed to next
- If test is incorrect:
  - Fix test to ensure RED before continuing
  - Do NOT proceed to next cycle until RED verified
```

**Purpose:**
- Prevents false positives
- Enforces TDD discipline
- Provides clear escalation protocol

### 4. Pre-Implementation Spike

**From design doc:**

```markdown
### Pre-Implementation Spike

Before starting TDD cycles, verify current behavior:
1. Write throwaway tests for expected functionality
2. Document pytest defaults that affect design
3. Identify cycles that may be `[REGRESSION]` tests
```

**Purpose:**
- Understand existing system behavior
- Identify what's already implemented
- Prevent unnecessary test writing
- Inform cycle planning

### 5. Cycle Granularity

**Observed patterns:**
- Each cycle: 1-3 assertions typically
- Clear RED failure expectation
- Minimal GREEN implementation (single feature increment)
- Independent verification

**Examples from r-flag-parity:**
- Cycle 1.1: Add test fixture (setup only, no RED/GREEN)
- Cycle 1.2: Test separate errors section (single assertion)
- Cycle 1.3: Test default mode shows both (2 assertions)

---

## Differences from agent-core Context

### 1. Standalone vs Orchestrated Execution

**pytest-md:**
- Cycles executed directly by single agent
- Session context maintained across cycles
- Cumulative knowledge assumed

**agent-core:**
- Weak orchestrator pattern
- Each cycle as separate agent invocation
- Context isolation via prepare-runbook.py

**Implication:** agent-core cycles need self-contained context in each cycle file.

### 2. Runbook Format

**pytest-md:**
- Markdown with standard headers
- No YAML frontmatter
- No "Weak Orchestrator Metadata" section

**agent-core:**
- YAML frontmatter required (`type: tdd`, `model: haiku`)
- Weak Orchestrator Metadata section required
- Common Context section for shared knowledge

**Implication:** /plan-tdd must generate agent-core-compatible format.

### 3. File Organization

**pytest-md:**
- Single phase document with all cycles
- Manual execution tracking

**agent-core:**
- Runbook → prepare-runbook.py → cycle files
- Each cycle file contains baseline + common context + cycle
- Orchestrator-driven execution

**Implication:** Cycle breakdown must account for extraction compatibility.

### 4. Dependency Management

**pytest-md:**
- Dependencies implied by sequential numbering
- Manual enforcement

**agent-core:**
- Explicit `[DEPENDS: X.Y]` markers
- Orchestrator validates and sequences

**Implication:** /plan-tdd must make dependencies explicit.

---

## Adaptation Requirements

### 1. Cycle Header Format

**Change:**
- From: `### Cycle X.Y: [Name]` (H3)
- To: `## Cycle X.Y: [Name]` (H2)

**Reason:** prepare-runbook.py expects H2 headers for cycle extraction.

### 2. Frontmatter Addition

**Required:**
```yaml
---
name: [feature-name]
type: tdd
model: haiku
---
```

**Reason:** Agent-core pattern requires frontmatter for routing.

### 3. Weak Orchestrator Metadata

**Required sections:**
- Total Steps (cycles count)
- Execution Model (haiku for TDD)
- Step Dependencies (sequential/parallel)
- Error Escalation (stop conditions)
- Report Locations
- Success Criteria
- Prerequisites

**Reason:** Orchestrator needs execution metadata.

### 4. Common Context Section

**Required content:**
- Design decisions from design doc
- File paths and project structure
- Conventions (tool usage, error handling)
- TDD protocol (RED-GREEN-REFACTOR rules)

**Reason:** Each cycle file needs shared knowledge for context isolation.

### 5. Cycle Content Structure

**Required for each cycle:**
```markdown
## Cycle X.Y: [Name] [DEPENDS: A.B] [REGRESSION]

**Objective**: [Clear goal]

**RED Phase:**
[Test to write, expected failure]

**GREEN Phase:**
[Minimal implementation]

**Stop Conditions:**
[When to escalate]
```

**Reason:** Standardized structure for prepare-runbook.py extraction.

### 6. Template Sections

**Need templates for:**
- Runbook frontmatter
- Weak Orchestrator Metadata
- Common Context
- Cycle definition
- RED/GREEN phases
- Stop conditions

**Reason:** Skill must generate consistent, valid runbooks.

---

## Extraction Compatibility Requirements

### 1. Header Parsing

prepare-runbook.py expects:
- `type: tdd` in frontmatter
- `## Cycle X.Y:` pattern for cycle headers
- Colon after cycle number

**Validation:**
- Cycle ID must match `X.Y` pattern (e.g., `1.1`, `2.3`)
- No duplicate cycle IDs
- Sequential numbering within phases

### 2. File Generation

prepare-runbook.py generates:
- `.claude/agents/[name]-task.md` (baseline + common context)
- `plans/[name]/steps/cycle-X-Y.md` (individual cycles)
- `plans/[name]/orchestrator-plan.md` (execution index)

**Requirements:**
- Common Context must be extractable
- Each cycle must be self-contained
- Cycle files must reference baseline

### 3. Baseline Integration

prepare-runbook.py uses:
- `agent-core/agents/tdd-task.md` for TDD runbooks
- Combines baseline + common context → plan-specific agent

**Requirements:**
- Common Context format compatible with baseline
- Tool usage rules consistent
- Error handling protocol aligned

---

## Key Takeaways for /plan-tdd Skill

### 1. Cycle Breakdown Algorithm Must:
- Parse design document phases/sections
- Generate X.Y numbering (X = phase, Y = increment)
- Create RED/GREEN specifications per cycle
- Assign dependencies (sequential within phase default)
- Mark regression tests where applicable

### 2. Runbook Generation Must:
- Include YAML frontmatter with `type: tdd`
- Generate Weak Orchestrator Metadata section
- Extract design decisions → Common Context
- Format cycles as H2 headers (`## Cycle X.Y:`)
- Include RED/GREEN/Stop Conditions per cycle

### 3. Validation Must Check:
- Cycle ID format (X.Y pattern)
- No duplicate cycle IDs
- Dependencies reference valid cycles
- No circular dependencies
- Each cycle has RED/GREEN/Stop Conditions

### 4. Integration Must:
- Output to `plans/[name]/runbook.md`
- Be compatible with prepare-runbook.py
- Reference tdd-task.md baseline
- Support orchestrator execution pattern

---

## Conclusion

The pytest-md reference provides solid patterns for TDD cycle structure, but requires significant adaptation for agent-core's weak orchestrator pattern. Key differences are:

1. **Context isolation**: Each cycle needs self-contained context
2. **Metadata requirements**: Frontmatter and orchestrator metadata mandatory
3. **Extraction format**: H2 headers, structured sections for parsing
4. **Dependency management**: Explicit markers vs implied sequence

The /plan-tdd skill must bridge these differences while preserving TDD discipline (RED-GREEN-REFACTOR, stop conditions, regression handling).

**Analysis complete. Size: 7843 bytes**
