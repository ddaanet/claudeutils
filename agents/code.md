---
name: code
description: TDD implementation and code quality
---

# Coding Skill

**Agent:** Weak models (haiku). Strong models use `planning.md` instead.

---

## Plan Adherence (Critical)

Follow the plan in `agents/PLAN.md` exactly. Do not improvise your own approach, create alternative task breakdowns, or reorder features. The plan specifies implementation order, test specifications, and fixture data - execute it as written.

---

## BEFORE STARTING (Mandatory)

**If not already loaded, read these files using the Read tool:**
1. `START.md` - Current task and status
2. `AGENTS.md` - Project overview and user preferences
3. `agents/TEST_DATA.md` - Data types and sample entries
4. `agents/PLAN.md` - Test specifications and implementation order

⚠️ **Do not proceed until these files are in context.**

## TIER 1: Critical Rules (Must Always Follow)

### Red-Green-Refactor Cycle (MANDATORY)

**Critical:** Always follow Red-Green-Refactor cycle. The RED phase is mandatory and must not be skipped.

#### Each Test-Implement Cycle (must follow exactly):

1. **Write ONE test** - Add exactly one new test case
2. **Run test and VERIFY it FAILS (Red)** - This step is MANDATORY
   - Run `just test` or the specific test
   - Confirm the test fails for the EXPECTED reason (assertion fails, not import/syntax error)
   - If test passes unexpectedly, the test may be wrong or implementation already exists
3. **Write minimal code to make it PASS (Green)**
   - Only add code needed to pass THIS test
   - Do not anticipate future tests
   - If Test 1 requires finding items and Test 2 requires filtering, Test 1's implementation should NOT include filtering
4. **Run test again and confirm it PASSES**
5. **Refactor if needed** (optional)
6. **Repeat** with next test until reaching a validation checkpoint

### Why the RED Phase Matters

Skipping the RED phase defeats the purpose of TDD:
- It verifies your test is actually testing something
- It confirms the test fails for the right reason
- It proves your implementation caused the test to pass

**Unexpected success is an error.** If a new test passes without writing new code, you have over-implemented. This means:
- You wrote more than the minimal code needed for the previous test
- The test may not be testing what you think it's testing
- You've lost the feedback loop that TDD provides

### When Test Passes Unexpectedly

**STOP immediately:**
1. Do NOT proceed to the next test
2. Report the violation to the user
3. Wait for user guidance on how to proceed

### TDD Anti-Patterns - Never Do These

🚫 **DON'T:**
- Write all tests upfront then implement
- Skip running the test before implementing
- Implement before seeing the test fail
- Fix lint or type errors (`just check`) - a separate agent handles this at checkpoints

✅ **DO:**
- Run each test immediately after writing it
- Verify failure message matches expectations
- Stop at validation checkpoints defined in the plan

### File Size Limits (Enforced)

Source files that exceed these limits block forward progress:

- **SHOULD NOT** exceed 300 lines per file
- **MUST NOT** exceed 400 lines per file

When a file approaches 300 lines, proactively plan to split it before continuing implementation.

---

## TIER 2: Important Rules (Follow in Most Cases)

### Type Safety (Non-negotiable)

- Full mypy strict mode required
- All parameters and return types must have type annotations
- No `Any` type unless justified with comment
- Use specific mypy error codes (e.g., `# type: ignore[arg-type]`) not blanket ignores

### Linting & Style

See `agents/lint.md` for detailed linting rules.

### Testing Standards

- All tests in `tests/` directory
- Use proper pytest parametrization for similar test cases
- Test names should clearly describe what they verify
- **Compare objects directly:** Prefer `assert result == expected_obj` over individual members
- **Factor common code:** Extract repeated test setup into plain helper functions (not fixtures)
- **Keep tests concise:** Pytest expands assert values; use natural loops with one assert
- **Fixture return types:** Use direct tuple, not Generator

---

## Tooling

### Dependency Management

- **Always use `uv`** for all package operations
- Add dependencies: `uv add package-name`
- Sync environment: `uv sync`
- Run commands: `uv run command`

### Task Runner

Use `justfile` for common tasks:
```bash
just test      # Run pytest
just check     # Run ruff + mypy
just format    # Auto-format with ruff
just dev       # Run all (format, check, test)
```

### File Organization

- Implementation: `src/claudeutils/`
- Tests: `tests/`
- Configuration: `pyproject.toml`
- Plan: `agents/PLAN.md`
