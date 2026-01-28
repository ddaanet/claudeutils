# Unification Project Status

**Last Updated:** 2026-01-28

## Executive Summary

**agent-core is operational** with 16 actively-developed skills and shared fragments. Both claudeutils and pytest-md use it as a submodule.

**Composition tooling (Phase 5-7) is now obsolete:** Native Claude Code supports `@file` references for recursive file inclusion (max depth: 5 levels). This provides modular organization without custom tooling. The compose.py system design remains available if programmatic generation becomes needed in the future.

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
- claudeutils: agent-core submodule at commit a3f49e5 (latest, 2026-01-28)
- pytest-md: agent-core submodule at commit 903c129 (36 commits behind)
- Both use `just sync-to-parent` to symlink skills into `.claude/`

**Phase 3 deliverables (design):**
- Feature extraction: `consolidation/design/feature-extraction.md`
- Core module design: `consolidation/design/core-module-design.md`
- CLI design: `consolidation/design/cli-design.md`
- YAML schema: `consolidation/design/yaml-schema.md`
- **Final design:** `consolidation/design/compose-api.md` (34K, comprehensive)

### ⚠️  Superseded by Native Feature

**Composition tooling (Phase 5-7) - obsolete due to native @file support:**
- No `src/claudeutils/compose.py` module (not needed)
- No `claudeutils compose` CLI command (not needed)
- No compose.yaml files in projects (not needed)
- **Native solution:** Claude Code supports `@path/to/file.md` references in CLAUDE.md
  - Recursive inclusion up to 5 levels deep
  - Relative, absolute, and home directory paths supported
  - Circular reference detection built-in
  - Code block protection (won't expand inside backticks)
- Projects now use @file references for modular organization

**Infrastructure gaps:**
- Configs mixed in `fragments/` directory (should be `configs/`)
- pytest-md agent-core submodule is stale (36 commits behind)

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
| 3 | Design unified composition API | ✅ Done | compose-api.md (34K) ready |
| 4 | Integrate content into agent-core | ✅ Done | Skills integrated, fragments ready |
| 5 | Build composition tooling | ⚠️  Obsolete | Native @file support makes this redundant |
| 6 | Deploy compose.yaml to projects | ⚠️  Obsolete | Native @file references used instead |
| 7 | Validation and testing | ⚠️  Obsolete | Native feature already tested by Claude Code |

## Next Actions

### Recommended: Adopt Native @file Pattern
1. ✅ Refactor CLAUDE.md to use @file references (proof of concept complete in claudeutils)
2. Update pytest-md agent-core submodule (36 commits behind)
3. Refactor pytest-md CLAUDE.md to use @file references
4. Document @file pattern in agent-core/docs/ for future projects
5. Archive compose.yaml design as "superseded by native feature"

### If Programmatic Generation Needed Later
The compose.py design (compose-api.md) remains available if future needs require:
- Template rendering or conditional inclusion
- Programmatic header level adjustment
- Metadata/frontmatter processing
- Validation or linting of composed output
- Batch generation for multiple projects

Current assessment: Native @file sufficient for modular organization.

## Dependencies

**pytest-md submodule update:**
```bash
cd /Users/david/code/pytest-md/agent-core
git pull origin main
cd ..
git add agent-core
git commit -m "Update agent-core submodule (36 commits, latest skills)"
```

**Skills requiring sync:**
- commit-context, handoff-lite, next, review-tdd-plan, token-efficient-bash

## Native @file Feature Discovery

**Date:** 2026-01-28

**Finding:** Claude Code natively supports `@file` references in CLAUDE.md for recursive file inclusion.

**Capabilities:**
- Syntax: `@path/to/file.md` (relative, absolute, or home directory paths)
- Recursive inclusion up to 5 levels deep
- Circular reference detection
- Code block protection (won't expand inside backticks)
- Resolution timing: Session startup

**Impact on Phases 5-7:**
- compose.py implementation: Not needed
- YAML configuration: Not needed
- CLI commands: Not needed
- **Native solution achieves original goal:** Modular fragment organization without copy-paste

**Proof of concept:** claudeutils CLAUDE.md refactored to use @file references (2026-01-28)

**Design preservation:** compose-api.md (34K design doc) archived for potential future needs if programmatic generation becomes necessary.

## Risk Assessment

**Low Risk:**
- agent-core is stable and actively maintained
- Skills are production-tested in claudeutils
- Submodule pattern works well
- Native @file feature is officially supported

**Medium Risk:**
- pytest-md falling behind on skill improvements (36 commits)

**High Risk:**
- None currently

## Recommendation

**Adopt native @file pattern for modular CLAUDE.md organization.** The original composition system goal (avoid copy-paste, reuse fragments) is fully achieved by native Claude Code features. Programmatic tooling can be implemented later if specific needs arise (templating, validation, conditional inclusion).
