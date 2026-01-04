# Handoff Entry Point

## Current Task: Markdown Cleanup Features

- **Status:** Plans complete, ready for TDD implementation
- **Orchestrator:** Sonnet
- **Task Coders:** Haiku

---

### What's Done

- ✅ **Feature planning** - Three features designed with TDD cycles
- ✅ **User clarifications** - All edge cases and patterns validated
- ✅ **Implementation plans** - Detailed plans in `plans/markdown/`
- ✅ **Documentation plan** - Module and README updates specified

---

### What's Next

**NEXT:** Implement Feature 1 (Checklist Detection) using TDD

**Workflow:**

1. Read `plans/markdown/feature-1-checklist-detection.md`
2. Follow TDD cycles: red test → minimal code → green test
3. Use Haiku for code implementation
4. After Feature 1 complete, move to Feature 2
5. After Feature 2 complete, move to Feature 3
6. Finally, apply documentation updates

**Implementation order:**

1. Feature 1: Extend `fix_warning_lines` (6 TDD cycles)
2. Feature 2: New `fix_markdown_code_blocks` (4 TDD cycles)
3. Feature 3: New `fix_metadata_list_indentation` (6 TDD cycles)
4. Documentation updates (module docstrings, README)
5. Agent documentation (TEST_DATA.md, DESIGN_DECISIONS.md)

---

### Key Context Files

| File                                               | Purpose                              |
| -------------------------------------------------- | ------------------------------------ |
| `session.md`                                       | Current session notes and decisions  |
| `plans/markdown/overview.md`                       | Overall context and success criteria |
| `plans/markdown/feature-1-checklist-detection.md`  | Feature 1 TDD plan                   |
| `plans/markdown/feature-2-code-block-nesting.md`   | Feature 2 TDD plan                   |
| `plans/markdown/feature-3-metadata-list-indent.md` | Feature 3 TDD plan                   |
| `plans/markdown/documentation-updates.md`          | Documentation update plan            |
| `plans/markdown/agent-documentation.md`            | Agent docs update plan               |

---

### Implementation Files

- **Source:** `src/claudeutils/markdown.py`
- **Tests:** `tests/test_markdown.py`

---

### TDD Approach

**Critical:** Follow strict red-green-refactor cycle:

1. **Red:** Write ONE failing test for next increment
2. **Green:** Write MINIMAL code to pass that test
3. **Verify:** Run test, ensure it passes
4. **Iterate:** Move to next test

**Don't:**

- Write multiple tests at once
- Implement more than the current test requires
- Skip running tests after each change

**Do:**

- Keep changes minimal
- Run tests frequently (`just test tests/test_markdown.py`)
- Follow the test order in the plan

---

### Features Summary

**Feature 1: Checklist Detection**

- Extend `fix_warning_lines` to handle ANY consistent non-markup prefix
- Examples: `✅ Task`, `❌ Failed`, `[TODO] Item`
- 6 TDD cycles in plan

**Feature 2: Code Block Nesting**

- Nest `` ```markdown `` blocks containing inner `` ``` `` fences using `` ```` ``
- Error out if inner fences in non-markdown blocks
- 4 TDD cycles in plan

**Feature 3: Metadata List Indentation**

- Convert `**Label:**` + list → `- **Label:**` with 2-space indented list
- Handles both `:**` and `**:` patterns
- 6 TDD cycles in plan

---

### Success Criteria

- [ ] All new tests pass
- [ ] All existing tests pass (no regressions)
- [ ] Code follows existing patterns
- [ ] Module documentation updated (docstrings, README)
- [ ] Agent documentation updated (TEST_DATA.md, DESIGN_DECISIONS.md)
- [ ] Pipeline integration verified

---

### Commands

```bash
# Run markdown tests
just test tests/test_markdown.py

# Run specific test
just test tests/test_markdown.py::test_name

# Run all tests
just test

# Format and check
just dev
```

---

## Core Context

1. `AGENTS.md` - Project overview, user preferences, role/rule definitions
2. `agents/DESIGN_DECISIONS.md` - Architectural and implementation decisions
3. `agents/TEST_DATA.md` - Data types and sample entries

## Roles (Load at Session Start)

- `agents/role-planning.md` - Design test specifications (opus/sonnet)
- `agents/role-code.md` - TDD implementation (haiku)
- `agents/role-lint.md` - Fix lint/type errors (haiku)
- `agents/role-refactor.md` - Plan refactoring (sonnet)
- `agents/role-execute.md` - Execute planned changes (haiku)
- `agents/role-review.md` - Code review and cleanup (sonnet)
- `agents/role-remember.md` - Update agent documentation (opus)

## Rules (Load Before Action)

- `agents/rules-commit.md` - **Read before any `git commit`**
- `agents/rules-handoff.md` - Read before ending a session

## Quick Reference

See `README.md` for usage examples and development commands.

Run `just dev` to verify all tests pass.
