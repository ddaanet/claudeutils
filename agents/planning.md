---
name: planning
description: Test-first design for TDD execution
---

# Planning Skill

> **Context:** Load `@START.md` for current task, `@AGENTS.md` for project overview, and `@agents/PLAN.md` for data model and step details.

**Goal:** Produce plans ready for TDD execution by low-reasoning agents (haiku).

## Test-First Design Methodology

Always specify tests before implementation. The output of planning must be actionable test specifications that a low-reasoning agent can execute using TDD.

---

## Critical Rule: Incremental Test Ordering

**Each test must require writing NEW code.** If implementing test N also makes test N+1 pass, the test sequence is wrong.

### Test Ordering Principles

1. **Start with the simplest case** - Often an empty input or error case
2. **Add one capability per test** - Each test should require exactly one new piece of functionality
3. **Build complexity gradually** - Simple → filtering → multiple items → edge cases → error handling
4. **Delay complex features** - Don't test recursion before testing the base case

### Example: Good vs Bad Test Ordering

**Bad ordering (allows batch implementation):**
1. Find 2 matching items ← Requires full implementation
2. Filter out non-matching items ← Already works from test 1
3. Empty directory returns empty ← Already works from test 1

**Good ordering (forces incremental implementation):**
1. Empty directory returns `[]` ← Just return empty list
2. One item, wrong ID → `[]` ← Add file reading + ID check
3. One item, correct ID → `[path]` ← Add collection logic
4. Multiple items with filtering ← Add loop

---

## Requirements for Test Specifications

### 1. Implementation Scope Per Test

Each test MUST include an **Implementation scope** section stating:
- What NEW code this test requires
- What existing code it builds upon
- What it explicitly does NOT require yet

```markdown
#### Test 3: `test_find_single_match`
**Given:** One file referencing target session
**When:** `find_items("target-123", dir)` is called
**Then:** Returns list containing one Path

**Implementation scope:**
- When ID matches, add file path to results list
- Return list of matching Paths
- Does NOT require: filtering, error handling, recursion
```

### 2. Detailed Natural-Language Tests

Each test specification must describe:
- **What** function/behavior is being tested
- **Given/When/Then** format for clarity
- **Fixture data** with exact JSON/values
- **Expected output** (exact values or patterns)

### 3. Group Tests by Capability

Organize tests into logical groups that build on each other:

```markdown
### Group A: Basic Discovery (Tests 1-3)
### Group B: Filtering (Tests 4-5)
### Group C: Error Handling (Tests 6-7)
### Group D: Recursion (Tests 8-10)
```

### 4. Include Fixture Data Inline

Provide exact test data so agents don't have to invent it:

```markdown
**Fixture data:**
```python
# agent-a1.jsonl
{"type":"user","sessionId":"main-123","message":{"content":"test"}}
```
```

---

## Test Specification Template

Use this format for each test:

```markdown
#### Test N: `test_function_name_behavior`
**Given:** [Preconditions - what exists before the test]
**When:** `function_call(args)` is called
**Then:** [Expected result]

**Implementation scope:**
- [New code required for this test]
- [Does NOT require: features tested later]

**Fixture data:**
```python
# filename.ext
{exact data}
```
```

---

## Common Planning Mistakes

### ❌ Tests that pass without new code
If test 2 passes after implementing test 1, restructure the tests.

### ❌ Missing implementation scope
Without explicit scope, agents implement entire functions at once.

### ❌ Testing complex before simple
Always test base cases and error cases before happy paths.

### ❌ Vague test descriptions
"Test filtering works" → "Test: returns only files matching session ID"

### ❌ Missing fixture data
Agents waste time inventing test data. Provide it explicitly.

---

## Checklist Before Finalizing Plan

- [ ] First test is the simplest possible case
- [ ] Each test adds exactly one new capability
- [ ] Implementation scope is explicit for each test
- [ ] Fixture data is provided inline
- [ ] Tests are grouped by capability
- [ ] No test would pass from a previous test's implementation
- [ ] Error cases come before complex happy paths
- [ ] Recursion/complexity tests come last

---

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
