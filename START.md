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

**Status:** Ready for implementation

### Next Task: CLI Inline Help Enhancement

**Plan:** `agents/PLAN_INLINE_HELP.md`

Enhance argparse help text so agents can use CLI without README:
- 5 tests in 2 groups (A: descriptions, B: pipeline context)
- All changes in `src/claudeutils/cli.py`
- Test file: `tests/test_cli_help.py`

### Recently Completed

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
