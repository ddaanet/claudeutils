# TDD Cycle Module

---
author_model: claude-opus-4-5-20251101
semantic_type: workflow
expansion_sensitivity: high
target_rules:
  strong: 5-7
  standard: 12-16
  weak: 18-24
weak_expansion_notes: |
  - Enumerate each phase with explicit steps
  - List acceptable vs unacceptable failure types
  - Provide examples of correct red-green transitions
  - Add visual markers for critical steps
---

## Semantic Intent

Agent implements code using strict Test-Driven Development. Write one test, see it
fail with the RIGHT kind of failure, write minimal code to pass, repeat. The red phase
validates the test actually tests something; the green phase adds only what's needed.

---

## Critical (Tier 1)

### One Test at a Time

Write exactly ONE new test case. Run it. See it fail. Then implement. Never write
multiple tests before implementing. Never implement before seeing failure.

### Verify Correct Failure Type

The red phase must produce an ASSERTION failure, not an infrastructure error.

Acceptable failures (test is running correctly):
- AssertionError - assertion failed as expected
- AttributeError on missing method - method not yet implemented

Unacceptable failures (test not actually running):
- ImportError - module structure broken
- SyntaxError - code doesn't parse
- NameError - undefined reference

If failure is wrong type: fix the infrastructure error first, then re-run to see
actual assertion failure.

### Minimal Implementation

Write ONLY the code needed to pass THIS test. Do not anticipate future tests. Do not
add features not tested. If you're writing code not required by the current failing
test, stop.

---

## Important (Tier 2)

### Tool Batching for TDD

Each TDD iteration completes in 2 tool batches:
- Red phase (batch 1): Write test + run test (chained)
- Green phase (batch 2): Write impl + run test (chained)

Bugfixes and refactoring: 1 batch (write + verify).

### Unexpected Pass = Problem

If a test passes when you expected it to fail, something is wrong. Either:
- Implementation already exists (check the code)
- Test is not testing what you think (check assertions)
- Wrong test file being run (check command)

Do not proceed. Investigate.

### Refactor Phase Optional

After green, refactoring is optional. Only refactor if there's clear duplication or
the code is genuinely hard to read. Don't refactor speculatively.

---

## Preferred (Tier 3)

### Test Naming

Test names should describe the behavior being verified, not the implementation.
Good: `test_returns_empty_list_when_no_matches`
Bad: `test_filter_function`

### Assertion Style

Compare objects directly when possible: `assert result == expected_obj`
Avoid testing individual attributes when object equality works.
