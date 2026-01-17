# Context: Rules Unification Project

<!--
Purpose: Task-related, relatively stable, cross-session context
- Key documents and their locations
- Architecture decisions and references
- Source/target repository locations
- NOT for: Active tasks, current state, session progress (use session.md instead)
-->

## Key Documents

**Design:**
- `plans/unification/design.md` - Architecture decisions, repository model, composition patterns

**Plans:**
- `plans/unification/consolidation-plan.md` - Master plan (7 phases, 410 lines)
- `plans/unification/phases/` - Split plan for delegation (context + phase files)

**Reports:**
- `plans/unification/reports/` - Execution reports and summaries

## Architecture

**Separation model:**
- `agent-core` - Shared fragments (consumed as git submodule)
- `claudeutils` - Generation tooling (Python module, dev dependency)
- Client projects consume via: `claudeutils compose <config>`

**agent-core structure:**
```
agent-core/
  fragments/     # Shared rule fragments (communication, delegation, etc)
  configs/       # Shared tool configs (justfile, ruff, mypy)
  skills/        # Reusable skills
  composer/      # Generation scripts (future)
```

## Source Projects

- `/Users/david/code/tuick` - Python composition (build.py)
- `/Users/david/code/emojipack` - Shell composition (compose.sh)
- `/Users/david/code/pytest-md` - Skills and CLAUDE.md fragments

## Target Repositories

- `claudeutils` - `/Users/david/code/claudeutils`
- `agent-core` - `/Users/david/code/agent-core`
