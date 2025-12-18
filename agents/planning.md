---
name: planning
description: Test-first design for TDD execution
---

# Planning Skill

**Goal:** Produce plans ready for TDD execution by low-reasoning agents (haiku).

## Test-First Design Methodology

Always specify tests before implementation. The output of planning must be actionable test specifications that a low-reasoning agent can execute using TDD.

## Requirements for Test Specifications

### 1. Detailed Natural-Language Tests

Each test specification must describe:
- **What** function/behavior is being tested
- **Input** values (specific examples)
- **Expected output** (exact values or patterns)
- **Edge cases** and error conditions

### 2. High-Level Implementation Guidance Only

- Provide approach and architecture, not detailed code
- Suggest patterns and algorithms conceptually
- Reference existing code patterns when applicable
- Let the implementation agent make detailed coding decisions

### 3. Use STEP*_TESTS.md Format

Follow the existing pattern from `STEP1_TESTS.md`, `STEP2_TESTS.md`, etc.:

```markdown
## Group Name

### Test: Description of what is being tested

**Input:**
- Parameter 1: value
- Parameter 2: value

**Expected:**
- Return value or behavior

**Edge cases:**
- Case 1: expected behavior
- Case 2: expected behavior
```

## Example Test Specification

```
### Test: encode_project_path handles absolute paths with slashes

**Input:**
- path: "/Users/david/code/project"

**Expected:**
- Return: "Users-david-code-project"

**Edge cases:**
- Leading slash should be stripped
- Multiple consecutive slashes treated as single separator
- Empty path raises ValueError
```

## Implementation Steps Reference

Reference the current implementation plan structure:
- Step 1: Path encoding & session discovery (✅ COMPLETE)
- Step 2: Trivial message filter (✅ COMPLETE)
- Step 3: Message parsing (✅ COMPLETE)
- Step 4: Recursive sub-agent processing (⏳ NEXT)
- Step 5: CLI subcommands (📋 PLANNED)

Each step has:
- Test specifications: `agents/STEP#_TESTS.md`
- Completion notes: `agents/STEP#_COMPLETION.md`
