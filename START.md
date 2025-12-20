# Handoff Entry Point

## Core Context (Read First)

1. `AGENTS.md` - Project overview, user preferences, role/rule definitions
2. `agents/DESIGN_DECISIONS.md` - Architectural and implementation decisions
3. `agents/TEST_DATA.md` - Data types and sample entries

## Roles (Load at Session Start)

- `agents/role-planning.md` - Design test specifications (opus/sonnet)
- `agents/role-code.md` - TDD implementation (haiku)
- `agents/role-lint.md` - Fix lint/type errors (haiku)
- `agents/role-refactor.md` - Plan refactoring (sonnet)
- `agents/role-execute.md` - Execute planned changes (haiku)
- `agents/role-remember.md` - Update agent documentation (opus)

## Rules (Load Before Action)

- `agents/rules-commit.md` - **Read before any `git commit`**
- `agents/rules-handoff.md` - Read before ending a session

## Current Task

**Status:** Ready for new feature work

**Note:** Agent reorganization complete. System uses role-based architecture. All tests passing (97 tests).

### Recently Completed

- ✅ **File Cleanup** - Agent reorganization complete (files renamed/deleted, references verified)
- ✅ **CLI Inline Help** - Enhanced argparse help text (5 tests, all passing)
- ✅ **Agent Reorganization** - Created role/rules structure (6 roles, 2 rules, justfile recipes)
- ✅ **Compliance Fix** - Added Plan Conflicts/Bugs detection to role-code.md
- ✅ README.md updated with pipeline documentation (collect → analyze → rules)
- ✅ CLI refactoring (handler extraction, complexity reduction)

---

**Previously Completed:**

- **Step 5: CLI Subcommands** ✅ - `list`, `extract` commands
- **Step 4: Recursive sub-agent processing** ✅
- **Step 3: Message parsing** ✅
- **Step 2: Trivial message filter** ✅
- **Step 1: Path encoding & session discovery** ✅
- **File Split Refactoring** ✅ - All files under 400-line limit

## Quick Reference

See `README.md` for usage examples and development commands.

Run `just test` to verify all tests pass.
