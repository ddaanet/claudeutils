# Handoff Entry Point

## Core Context (Read First)

1. `AGENTS.md` - Project overview, user preferences, skill references
2. `agents/PLAN.md` - Full implementation plan and data model

## Skills (Read Before Action)

- `agents/code.md` - Read before implementing code
- `agents/planning.md` - Read before designing test specifications
- `agents/commit.md` - **Read before any `git commit`**
- `agents/remember.md` - Read before updating documentation
- `agents/handoff.md` - Read before ending a session

## Current Task

**⚠️ BLOCKER: File Size Limit Violations** (🔴 MUST FIX FIRST)

- `src/claudeutils/main.py`: 417 lines (exceeds 400-line limit by 17)
- `tests/test_main.py`: 866 lines (exceeds 400-line limit by 466)
- **Plan exists:** `/Users/david/.claude/plans/misty-zooming-thunder.md`
  - Split main.py into 6 modules (models, paths, parsing, discovery, extraction, cli)
  - Split test_main.py into 5 test modules
  - All import paths will change (breaking change, approved by user)
  - Verification: `just dev` (includes new line-limits check)
- **Next action:** Execute the plan to split files before implementing Step 5

**Step 5: CLI Subcommands** (⏳ AFTER FILE SPLIT)

- Task spec: `agents/STEP5_TESTS.md` ✅
- `list [--project PATH]` - Show top-level sessions
- `extract SESSION_PREFIX [--project PATH] [--output FILE]` - Extract feedback recursively
- 18 tests: CLI argument parsing, output formatting, session matching, JSON serialization

**Completed:**

- Step 1: Path encoding & session discovery
- Step 2: Trivial message filter
- Step 3: Message parsing (completion notes: `agents/STEP3_COMPLETION.md`)
- Step 4: Recursive sub-agent processing (completion notes: `agents/STEP4_COMPLETION.md`)

## Quick Commands

```bash
just dev         # Format, check, test (full cycle)
just test ...    # Run pytest, arguments are passed to pytest
just check       # Run ruff + mypy
```

## Status Check

Run `just test` to see current test status and progress.
