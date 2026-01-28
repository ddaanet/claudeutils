# Unification Project Status

**Last Updated:** 2026-01-28

## Executive Summary

**✅ PROJECT COMPLETE**

agent-core is operational with 16 actively-developed skills and shared fragments. Both claudeutils and pytest-md use it as a submodule with native `@file` references for modular CLAUDE.md organization.

**Composition tooling (Phase 5-7) obsolete:** Native Claude Code `@file` support makes custom composition tooling unnecessary. Design artifacts removed per code-removal.md fragment.

## Current State

### ✅ Completed

**agent-core infrastructure:**
- Repository structure established
- 16 production skills in `skills/` directory:
  - commit, commit-context, design, gitmoji, handoff, handoff-lite
  - next, oneshot, orchestrate, plan-adhoc, plan-tdd
  - remember, review-tdd-plan, shelve, token-efficient-bash, vet
- Shared fragments in `fragments/` directory (14 fragments including configs)
- Baseline agents in `agents/` directory (quiet-task, tdd-task)
- Workflow documentation in `docs/` directory
- Runbook preparation tooling in `bin/` directory

**Project integration:**
- claudeutils: agent-core submodule (latest), CLAUDE.md uses @file references
- pytest-md: agent-core submodule (latest), CLAUDE.md uses @file references
- Both use `just sync-to-parent` to symlink skills into `.claude/`

**@file pattern documentation:**
- Complete documentation: `agent-core/docs/@file-pattern.md`
- Covers syntax, recursion depth, circular references, best practices
- Real-world multi-project examples included

### ⚠️  Superseded by Native Feature

**Composition tooling (Phase 5-7) - obsolete due to native @file support:**
- Native `@file` references provide all needed functionality
- No custom tooling required (compose.py, CLI, YAML configs)
- Obsolete design artifacts removed (consolidation/ directory)
- Documentation available in `agent-core/docs/@file-pattern.md`

## Architecture Reality vs Plan

### What Exists

```
agent-core/
├── .claude/
│   └── skills/ -> ../skills/           # Symlink for Claude Code discovery
├── agents/                             # ✅ Baseline agent templates
│   ├── quiet-task.md
│   └── tdd-task.md
├── bin/                                # ✅ Runbook tooling
│   └── prepare-runbook.py
├── docs/                               # ✅ Workflow docs
│   ├── oneshot-workflow.md
│   └── tdd-workflow.md
├── fragments/                          # ✅ Shared content (14 files)
│   ├── communication.md                #    Including configs (should move)
│   ├── justfile-base.just              # ⚠️  Should be in configs/
│   ├── ruff.toml                       # ⚠️  Should be in configs/
│   └── mypy.toml                       # ⚠️  Should be in configs/
├── skills/                             # ✅ Production skills (16)
│   ├── commit/
│   ├── design/
│   └── ...
└── README.md

claudeutils/
├── agent-core/                         # ✅ Submodule (latest)
├── .claude/
│   ├── agents/ -> ../agent-core/agents/
│   └── skills/ -> ../agent-core/skills/
├── agents/
│   ├── session.md                      # ✅ Manual maintenance
│   └── decisions/                      # ✅ Project-specific docs
├── src/claudeutils/
│   └── compose.py                      # ❌ Not implemented
└── CLAUDE.md                           # ⚠️  Manual (should be generated)

pytest-md/
├── agent-core/                         # ⚠️  Submodule (36 commits behind)
├── .claude/                            # ✅ Symlinks via sync-to-parent
└── CLAUDE.md                           # ⚠️  Manual (should be generated)
```

### What Was Planned vs Native Solution

**Original plan (YAML composition):**
```yaml
# agents/compose.yaml (obsolete)
sources:
  core: &core agent-core/fragments

fragments:
  - *core/communication.md
  - *core/delegation.md
  - local/project-rules.md

output: CLAUDE.md
```

**Native solution (no tooling needed):**
```markdown
# CLAUDE.md (uses native @file references)
@agent-core/fragments/communication.md
@agent-core/fragments/delegation.md
@agents/decisions/project-rules.md
```

Recursive inclusion supported up to 5 levels. References resolved at session startup.

## Phase Mapping

| Phase | Goal | Status | Notes |
|-------|------|--------|-------|
| 1 | Extract fragments to agent-core | ✅ Done | Files copied to scratch, fragmented |
| 2 | Analysis (compose scripts, configs) | ✅ Done | Reports in consolidation/analysis/ |
| 3 | Design unified composition API | ✅ Done | Obsolete artifacts removed |
| 4 | Integrate content into agent-core | ✅ Done | Skills integrated, fragments ready |
| 5 | Build composition tooling | ✅ Skipped | Native @file support sufficient |
| 6 | Deploy compose.yaml to projects | ✅ Done | Using native @file references |
| 7 | Validation and testing | ✅ Done | Both projects using @file successfully |

## Project Complete

All planned work is complete:
1. ✅ agent-core repository with shared skills/fragments/docs
2. ✅ Both projects (claudeutils, pytest-md) using agent-core submodule
3. ✅ Both projects using native @file references in CLAUDE.md
4. ✅ @file pattern documented in agent-core/docs/@file-pattern.md
5. ✅ Obsolete design artifacts removed per code-removal.md
6. ✅ New fragment created: code-removal.md (delete, don't archive)

## New Fragments Created

**code-removal.md:**
- Delete obsolete code, don't archive it
- Git history is the archive
- Clean codebase is easier to navigate
- Rationale: Dead code creates maintenance burden

This fragment prevents future accumulation of `archive/`, `old/`, or commented-out dead code.

## Next Work

The unification project is complete. Next potential work (from todo.md):

1. **Convert agent-core to Claude Code Plugin** (High priority)
   - Replace git submodule with plugin for auto-discovery
   - Benefits: No manual sync, works across all projects
   - Current blocker: None (unification complete)

2. **Markdown Formatter Survey** (High priority)
   - Find dprint replacement (has serious markdown handling issues)
   - Evaluate: prettier, markdownlint-cli2, remark-cli
