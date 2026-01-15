# Out-of-Tree Agent Consolidation Plan

**Goal**: Bring out-of-tree changes from emojipack, tuick, and pytest-md into claudeutils scratch/ directory, consolidate generation tooling, and establish unified composition system.

**Status**: Planning complete, ready for execution
**Date**: 2026-01-15

---

## Context

Three projects have agent-related infrastructure that needs consolidation:
- **emojipack**: Shell-based composition (compose.sh/compose.yaml)
- **tuick**: Python-based composition (build.py + Makefile)
- **pytest-md**: Manual AGENTS.md, 7 reusable skills

Per design document (plans/unification/design.md):
- Shared content goes in agent-core (git submodule)
- Generation tooling goes in claudeutils (Python module)
- Projects consume via dev dependency

---

## Architecture Decision

**Generation tooling location**: `claudeutils` as Python module (not shell scripts in agent-core)

**Rationale**:
- tuick's build.py has proven features (header manipulation, decorators)
- Python enables extensibility (YAML parsing, validation, templating)
- Fits claudeutils pattern: dev dependency with CLI entry points
- Client projects use: `claudeutils compose <config>`

---


---

## Common Context

This file contains shared context for all execution steps.
Each step file references this context and should be executed with both files in context.

---

## Critical Files

**Design Reference**:
- plans/unification/design.md - Architecture decisions (already read)

**Source Files for Extraction**:
- /Users/david/code/tuick/agents/build.py - Composition logic (73 lines)
- /Users/david/code/emojipack/agents/compose.yaml - YAML config pattern
- /Users/david/code/pytest-md/AGENTS.md - Content to fragment (153 lines)
- /Users/david/code/pytest-md/.claude/skills/ - 7 skills to integrate

**Target Files for Updates**:
- agent-core/skills/ - NEW directory
- agent-core/configs/ - NEW directory
- agent-core/fragments/ - Expand with new fragments
- src/claudeutils/compose.py - NEW composition engine
- src/claudeutils/cli.py - Add compose subcommand

---

## Open Questions Resolved

1. **pytest-md skills**: Integrate reusable skills into agent-core/skills/ ✓
2. **Config files**: Centralize in agent-core/configs/ (justfile, ruff, mypy) ✓
3. **Naming**: Use `claudeutils compose` (subcommand) ✓
4. **Makefile support**: Provide example, defer full integration ✓
5. **YAML templating**: Defer to v2 ✓
6. **Validation**: Basic validation only (valid markdown, files exist) ✓
7. **pytest-md fragmentation**: Section-level split per analysis above ✓

---

## Success Criteria

- [ ] All files copied to scratch/consolidation/
- [ ] diff/patch analysis complete in scratch/consolidation/analysis/
- [ ] Composition API designed in scratch/consolidation/design/
- [ ] agent-core updated with skills/, configs/, new fragments
- [ ] claudeutils compose module implemented and working
- [ ] All three projects validated with unified tooling
- [ ] Generated AGENTS.md matches expected output for each project

---

## Execution Notes

**Orchestration pattern** (per design doc):
- Use haiku agents for file copying and diff operations
- Use sonnet for composition API implementation
- Terse returns: `done: <summary>` or `blocked: <reason>`
- Reports to files, not orchestrator context
- Final validation by diff-based review

**Sandbox considerations**:
- Work happens in scratch/ within claudeutils (sandbox-safe)
- Out-of-tree reads are read-only (no modifications to sibling projects)
- Git operations only in claudeutils and agent-core repos

