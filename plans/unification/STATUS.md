# Unification Project Status

**Last Updated:** 2026-01-28

## Executive Summary

**⚠️  PHASE 4 COMPLETE, CONFIG COMPOSITION PENDING**

agent-core is operational with 16 actively-developed skills, shared fragments, and base config files. Both claudeutils and pytest-md use it as a submodule with native `@file` references for modular CLAUDE.md organization.

**Composition status:**
- ✅ CLAUDE.md: Native `@file` support makes custom tooling unnecessary
- ⚠️  Config files (justfile/pyproject.toml): Base files organized, but project composition not yet implemented

## Current State

### ✅ Completed

**agent-core infrastructure:**
- Repository structure established
- 16 production skills in `skills/` directory:
  - commit, commit-context, design, gitmoji, handoff, handoff-lite
  - next, oneshot, orchestrate, plan-adhoc, plan-tdd
  - remember, review-tdd-plan, shelve, token-efficient-bash, vet
- Shared fragments in `fragments/` directory (18 files, excludes configs)
- Base config files in `configs/` directory (4 files):
  - justfile-base.just, ruff-base.toml, mypy-base.toml, docformatter-base.toml
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

### ⚠️  Partially Complete

**Composition status split by file type:**

**CLAUDE.md composition (Phase 5-7 obsolete):**
- Native `@file` references provide all needed functionality
- No custom tooling required
- Obsolete design artifacts removed (consolidation/ directory)
- Documentation: `agent-core/docs/@file-pattern.md`

**Config file composition (Phase 5-7 still needed):**
- Base files organized in `agent-core/configs/`
- Projects still use inline copies (not imports)
- Need implementation: justfile import mechanism, pyproject.toml composition
- Documentation: `agent-core/configs/README.md` describes current state

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
├── configs/                            # ✅ Base config files (4 files)
│   ├── justfile-base.just              # Common recipes
│   ├── ruff-base.toml                  # Ruff base config
│   ├── mypy-base.toml                  # Mypy base config
│   ├── docformatter-base.toml          # Docformatter base config
│   └── README.md                       # Usage documentation
├── fragments/                          # ✅ Shared content (18 files)
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
| 4 | Integrate content into agent-core | ✅ Done | Skills, fragments, configs organized |
| 5 | Build composition tooling | ⚠️  Split | @file for CLAUDE.md (done), configs pending |
| 6 | Deploy to projects | ⚠️  Split | CLAUDE.md done, configs pending |
| 7 | Validation and testing | ⚠️  Split | CLAUDE.md done, configs pending |

## Current Status

**Completed:**
1. ✅ agent-core repository with shared skills/fragments/configs/docs
2. ✅ Both projects (claudeutils, pytest-md) using agent-core submodule
3. ✅ Both projects using native @file references in CLAUDE.md
4. ✅ @file pattern documented in agent-core/docs/@file-pattern.md
5. ✅ Base config files organized in agent-core/configs/
6. ✅ Config usage documented in agent-core/configs/README.md
7. ✅ Obsolete design artifacts removed per code-removal.md
8. ✅ New fragment: code-removal.md (delete, don't archive)

**Pending:**
1. ⚠️  Implement justfile import mechanism (projects currently use inline copies)
2. ⚠️  Implement pyproject.toml composition (projects currently use inline copies)
3. ⚠️  Document config composition pattern once implemented

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
