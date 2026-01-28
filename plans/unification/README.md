# Rules Unification Project

## Overview

Consolidate agent infrastructure from emojipack, tuick, and pytest-md into unified composition system.

## Key Documents

**Design:**
- `design.md` - Architecture decisions, repository model, composition patterns

**Plans:**
- `consolidation-plan.md` - Master plan (7 phases)
- `phases/` - Split plan for delegation (context + phase files)
- `phases/consolidation-context.md` - Common context for all execution steps

**Execution Plans:**
- `phase1-execution-plan.md` - Phase 1: Extract fragments to agent-core
- `phase2-execution-plan.md` - Phase 2: Analysis (compose scripts, config files)
- `phase3-execution-plan.md` - Phase 3: Design unified composition API

**Reports:**
- `reports/` - Execution reports and summaries from all phases

**Design Deliverables (Phase 3):**
- `consolidation/design/feature-extraction.md` - Features from tuick and emojipack
- `consolidation/design/core-module-design.md` - Core composition module
- `consolidation/design/cli-design.md` - CLI interface design
- `consolidation/design/yaml-schema.md` - YAML configuration schema
- `consolidation/design/compose-api.md` - Integrated design document (34K, ready for Phase 4)

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

## Status

**See:** `STATUS.md` for comprehensive current state assessment

**Summary:**
- agent-core operational with 16 production skills
- Both claudeutils and pytest-md use agent-core as submodule
- Composition tooling (Phase 5-7) not implemented—projects use manual CLAUDE.md
- pytest-md submodule is 36 commits behind claudeutils

**Decision Point:** Complete composition system vs. defer for future
