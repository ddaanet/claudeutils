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

**Next:** Implement feedback processing pipeline from `agents/PLAN.md`

### Implementation Order

1. **Feature 2: Filtering Module** - Foundation for analyze and rules
2. **Feature 1: `collect` Subcommand** - Batch extract from all sessions
3. **Feature 3: `analyze` Subcommand** - Statistical summary with categories
4. **Feature 4: `rules` Subcommand** - Deduplicated rule-worthy items

See `agents/PLAN.md` for full test specifications (24 tests total).

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
