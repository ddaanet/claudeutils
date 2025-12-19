---
name: code
description: TDD implementation and code quality
---

# Coding Skill

## BEFORE STARTING (Mandatory)

**If not already loaded, read these files using the Read tool:**
1. `START.md` - Current task and status
2. `AGENTS.md` - Project overview and user preferences
3. `agents/TEST_DATA.md` - Data types and sample entries
4. The relevant `agents/STEP*_TESTS.md` for your current task

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
6. **Repeat** with next test
7. **After every THREE cycles, request user validation before continuing**

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
- Proceed with the next cycle without explicit user instruction

✅ **DO:**
- Run each test immediately after writing it
- Verify failure message matches expectations
- Request confirmation after every THREE test-implement cycles
- WAIT for user to say "continue" before proceeding after validation checkpoints

---

## TIER 2: Important Rules (Follow in Most Cases)

### Type Safety (Non-negotiable)

- Full mypy strict mode required
- All parameters and return types must have type annotations
- No `Any` type unless justified with comment
- If using `type: ignore`, include line comment explaining why

### Linting & Style

See `agents/lint.md` for detailed linting rules.

- Docstrings in imperative mood ("Extract content" not "Extracts content")
- Docstrings wrap at column 80 (docformatter enforces this via `just format`)

### Testing Standards

- All tests in `tests/` directory
- Use proper pytest parametrization for similar test cases
- Test names should clearly describe what they verify
- **Compare complex objects directly** for better error messages:
  - Prefer `assert result == expected_obj` over comparing individual members
- **Fixture return types:** Use direct tuple, not Generator
- **Long JSON strings:** Use implicit concatenation across lines

### Code Quality Anti-Patterns

See `agents/lint.md` for linting anti-patterns and when ignores are acceptable.

### File Size Limits

Keep source files small to avoid loading unneeded context:

- **SHOULD NOT** exceed 300 lines per file
- **MUST NOT** exceed 400 lines per file
- When files grow larger, split them into focused modules

---

## TIER 3: Optional Style Rules

### Type Annotations

- Use specific type annotations (`list[str]`, not bare `list`)
- Prefer built-in generic types over `typing` module where possible (Python 3.9+)

---

## Sub-Agent Usage

Use sub-agents for batched operations like lint fixing:

- **Prefer architectural fixes** over `# noqa` suppressions
- **Explain strategy** before launching sub-agent
- **Transcripts location:** `~/.claude/projects/[ENCODED-PATH]/agent-*.jsonl`

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

- Implementation: `src/claudeutils/main.py`
- Tests: `tests/test_main.py`
- Configuration: `pyproject.toml`
- Plans: `agents/PLAN.md` and `agents/STEP*_TESTS.md`
