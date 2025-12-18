# Handoff Entry Point

## Core Context (Read First)

1. `AGENTS.md` - Project overview, user preferences, skill references
2. `agents/PLAN.md` - Full implementation plan and data model

## Skills (Load as Needed)

- `@agents/code.md` - TDD implementation (load when coding)
- `@agents/planning.md` - Test-first design (load when planning)
- `@agents/commit.md` - Git commit standards (load when committing)
- `@agents/remember.md` - Documentation updates (load when updating docs)
- `@agents/handoff.md` - Ending a session (any role)

## Current Task

**Step 5: CLI Subcommands** (⏳ NEXT)

- Task spec: `agents/STEP5_TESTS.md` (needs creation based on `agents/PLAN.md`)
- `list [--project PATH]` - Show top-level sessions
- `extract SESSION_PREFIX [--project PATH] [--output FILE]` - Extract feedback recursively
- See Plan lines 140-166 for test cases

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
