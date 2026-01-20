# Planning Request: prepare-runbook.py TDD Cycle Support

**Created:** 2026-01-19
**Runbook:** plans/tdd-integration/runbook.md
**Step:** 6 of 8

---

## 1. Task Objective

Add TDD cycle format support to `prepare-runbook.py` to enable detection, parsing, and processing of TDD runbooks with RED/GREEN/REFACTOR cycle structure.

The script must:
- Detect TDD runbooks via frontmatter metadata (`type: tdd`)
- Parse cycle sections instead of step sections (`## Cycle X.Y:` headers)
- Use `tdd-task.md` baseline instead of `quiet-task.md` for TDD runbooks
- Generate cycle files (`cycle-X-Y.md`) instead of step files
- Generate appropriate orchestrator plan for TDD execution
- Maintain backward compatibility with general (non-TDD) runbook processing

---

## 2. Complexity Rationale

This task requires separate planning session because:

### Script Size
- Current `prepare-runbook.py` is ~290 lines
- TDD support requires modifications exceeding 100 lines
- New functions needed: cycle detection, cycle parsing, TDD validation
- Multiple code paths diverge based on runbook type

### Parsing Complexity
- Cycle detection requires regex pattern matching (`## Cycle X.Y:` format)
- Must handle cycle numbering (X.Y where X = major, Y = minor)
- Must extract RED/GREEN/REFACTOR subsections from cycle content
- Must validate cycle structure (mandatory phases, stop conditions)
- Error handling for malformed cycle definitions

### Conditional Logic
- Baseline selection: `tdd-task.md` vs `quiet-task.md` based on runbook type
- File generation: `cycle-X-Y.md` vs `step-X-Y.md` naming
- Section extraction: cycles vs steps
- Orchestrator plan: TDD-specific vs general instructions

### Integration Points
- Must not break existing general runbook processing
- Must maintain same CLI interface
- Must preserve existing path derivation logic
- Must maintain same output structure (agents/, steps/, orchestrator-plan.md)

---

## 3. Planning Requirements

### 3.1 Analyze Current Implementation

Review `agent-core/bin/prepare-runbook.py` to understand:
- Current frontmatter parsing (`parse_frontmatter()`)
- Current section extraction (`extract_sections()`)
- Step pattern matching (`step_pattern = r'^## Step\s+([\d.]+):\s*(.*)'`)
- Baseline agent selection (`read_baseline_agent()`)
- File generation logic (`generate_step_file()`, `generate_agent_frontmatter()`)
- Path derivation (`derive_paths()`)
- Validation logic (`validate_and_create()`)

### 3.2 Design Cycle Detection Logic

Create regex pattern for cycle headers:
- Pattern: `## Cycle X.Y:` where X and Y are integers
- Example: `## Cycle 1.1: User can authenticate`
- Regex should capture: cycle number (X.Y), cycle name
- Must differentiate from step pattern (`## Step N:`)

Design conditional section extraction:
- If `type: tdd` in frontmatter → extract cycles
- If `type: general` or no type → extract steps
- Share common logic where possible

### 3.3 Design TDD Metadata Detection

Frontmatter parsing already exists; extend for type detection:
- Key: `type`
- Valid values: `tdd`, `general` (or absent)
- Default behavior if absent: treat as general runbook

Example frontmatter:
```yaml
---
name: feature-auth
type: tdd
model: haiku
---
```

### 3.4 Design Baseline Selection Logic

Conditional baseline loading:
- TDD runbooks → `agent-core/agents/tdd-task.md`
- General runbooks → `agent-core/agents/quiet-task.md`

Update `read_baseline_agent()`:
- Add `runbook_type` parameter
- Load appropriate baseline
- Handle missing baseline file errors

### 3.5 Design Cycle File Generation

Create new function `generate_cycle_file()` similar to `generate_step_file()`:

**File naming:**
- Pattern: `cycle-X-Y.md` (e.g., `cycle-1-1.md`, `cycle-2-3.md`)
- Location: `plans/<runbook-name>/steps/` (same directory as step files)

**File structure:**
```markdown
# Cycle X.Y

**Plan**: `plans/<runbook-name>/runbook.md`
**Common Context**: See plan file for context

---

## Cycle X.Y: [name]

[cycle content including RED/GREEN/REFACTOR sections]
```

**Cycle content extraction:**
- Extract full cycle section from runbook
- Include all subsections (RED phase, GREEN phase, Stop Conditions)
- Preserve markdown structure

### 3.6 Design Validation for Cycle Format

Add validation checks for TDD runbooks:

**Cycle numbering:**
- Sequential major numbers (1, 2, 3...)
- Sequential minor numbers within major (1.1, 1.2, 1.3...)
- No gaps allowed
- No duplicate cycle numbers

**Cycle structure:**
- Each cycle must have subsections (validate presence)
- RED phase, GREEN phase are mandatory
- Stop conditions section is mandatory
- Warn if dependencies section missing

**Error messages:**
- "ERROR: Duplicate cycle number: X.Y"
- "ERROR: Non-sequential cycle numbering"
- "ERROR: Missing required section in Cycle X.Y: [section]"
- "WARNING: Cycle X.Y missing dependencies section"

### 3.7 Update Help Text and Error Messages

Update `main()` help text:
```
Transforms runbook markdown into execution artifacts:
  - Plan-specific agent (.claude/agents/<runbook-name>-task.md)
  - Step/Cycle files (plans/<runbook-name>/steps/)
  - Orchestrator plan (plans/<runbook-name>/orchestrator-plan.md)

Supports:
  - General runbooks (## Step N:)
  - TDD runbooks (## Cycle X.Y:, requires type: tdd in frontmatter)
```

Update error messages:
- "ERROR: TDD runbook missing type: tdd in frontmatter"
- "ERROR: No cycles found in TDD runbook"
- "ERROR: No steps found in general runbook"
- "ERROR: Baseline agent not found: [path]"

### 3.8 Add Unit Tests or Validation Scripts

Create validation strategy:

**Option 1: Unit tests**
- Test cycle regex pattern matching
- Test frontmatter type detection
- Test baseline selection logic
- Test cycle file generation

**Option 2: Integration test**
- Use existing TDD runbook: `plans/tdd-integration/runbook.md`
- Run `prepare-runbook.py` on it
- Verify outputs:
  - Agent uses `tdd-task.md` baseline
  - Cycle files created (not step files)
  - Orchestrator plan appropriate for TDD

**Recommendation:** Start with Option 2 (integration test on real runbook), add unit tests if time permits.

---

## 4. Dependencies

### Completed Prerequisites
- **Step 3 complete:** `tdd-task.md` baseline exists at `agent-core/agents/tdd-task.md`
- **Current implementation:** `agent-core/bin/prepare-runbook.py` functional for general runbooks

### Required Understanding
- Current `prepare-runbook.py` structure and functions
- TDD runbook format specification (see design.md § TDD Runbook Structure)
- Baseline template pattern (baseline + common context → plan-specific agent)

### External Dependencies
- Python 3.x environment
- Runbook in `plans/*/runbook.md` format
- Baseline agents in `agent-core/agents/`

---

## 5. Reference Material

### Design Document
**Path:** `plans/tdd-integration/design.md`

**Key sections:**
- § TDD Runbook Structure (lines 105-153)
  - Shows frontmatter format with `type: tdd`
  - Shows cycle header format: `## Cycle X.Y: [name]`
  - Shows cycle subsections: RED/GREEN/Stop Conditions

- § prepare-runbook.py Updates (lines 326-352)
  - Cycle detection requirements
  - TDD runbook processing steps
  - Key difference: `tdd-task.md` vs `quiet-task.md` baseline

### Current Implementation
**Path:** `agent-core/bin/prepare-runbook.py`

**Key functions to review:**
- `parse_frontmatter()` (lines 27-49) - Already handles metadata parsing
- `extract_sections()` (lines 52-125) - Needs cycle detection variant
- `read_baseline_agent()` (lines 148-157) - Needs type parameter
- `generate_step_file()` (lines 172-182) - Template for cycle file generation
- `validate_and_create()` (lines 195-250) - Main orchestration logic

### Baseline Template
**Path:** `agent-core/agents/tdd-task.md`

**Usage:**
- Provides TDD cycle execution protocol
- Combined with runbook common context
- Used instead of `quiet-task.md` for TDD runbooks

### Example TDD Runbook
**Path:** `plans/tdd-integration/runbook.md`

**Purpose:**
- Real TDD runbook for testing
- Contains actual cycle definitions
- Can be used for integration validation

---

## 6. Next Action

This planning request documents a complex implementation task that requires:
- Code analysis and design decisions
- Multiple new functions and conditional logic paths
- Validation strategy and error handling
- Backward compatibility preservation

**Recommended approach:**
1. Read all reference materials (prepare-runbook.py, design.md, tdd-task.md)
2. Design the changes (new functions, modified functions, integration points)
3. Create implementation runbook with discrete steps
4. Execute via /orchestrate with appropriate model (sonnet for implementation)

**Model recommendation:** Sonnet for planning session (complexity warrants detailed design but not architectural decisions).

**Expected planning output:**
- Implementation runbook with 8-12 steps
- Each step focused on discrete change (add function, modify function, update validation)
- Testing/validation as final step
- Clear acceptance criteria per step

---

## Summary

This planning request captures a >100 line modification to `prepare-runbook.py` with:
- Cycle detection regex and parsing
- Conditional baseline selection
- Cycle file generation
- TDD-specific validation
- Backward compatibility maintenance

The complexity justifies separate planning session to ensure correct implementation without multiple revision cycles.
