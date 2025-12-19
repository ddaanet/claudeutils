# Handoff Entry Point

## Core Context (Read First)

1. `AGENTS.md` - Project overview, user preferences, skill references
2. `agents/DESIGN_DECISIONS.md` - Architectural and implementation decisions
3. `agents/TEST_DATA.md` - Data types and sample entries

## Skills (Read Before Action)

- `agents/code.md` - Read before implementing code
- `agents/planning.md` - Read before designing test specifications
- `agents/commit.md` - **Read before any `git commit`**
- `agents/remember.md` - Read before updating documentation
- `agents/handoff.md` - Read before ending a session

## Current Task

**Next:** Execute CLI refactoring from `agents/REFACTOR_PLAN.md`

### Immediate Priority

Fix complexity violations in `src/claudeutils/cli.py:54` (main function):
- C901: Complexity 22 > 10
- PLR0912: Branches 28 > 12
- PLR0915: Statements 93 > 50

**Approach:** Extract 5 command handlers (`list`, `extract`, `collect`, `analyze`, `rules`) into dedicated functions. Plan ready for Haiku execution in `agents/REFACTOR_PLAN.md`.

### After Refactoring

Resume implementing feedback processing pipeline. **Note:** Features 2-4 already implemented but pending complexity fix before commit.

See `agents/PLAN.md` for original feature specifications.

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
