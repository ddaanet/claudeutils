# Unification Project Status

**Last Updated:** 2026-01-28

## Executive Summary

**agent-core is operational** with 16 actively-developed skills and shared fragments. Both claudeutils and pytest-md use it as a submodule. The composition tooling (Phase 5-7) remains unimplemented—projects still use manual CLAUDE.md files rather than compose.yaml + generation.

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

### ❌ Not Completed

**Composition tooling (Phase 5-7):**
- No `src/claudeutils/compose.py` module
- No `claudeutils compose` CLI command
- No compose.yaml files in projects
- No YAML-driven CLAUDE.md generation
- Projects use manual CLAUDE.md maintenance

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

### What Was Planned

The original plan envisioned:

```yaml
# agents/compose.yaml (doesn't exist yet)
sources:
  core: &core agent-core/fragments

fragments:
  - *core/communication.md
  - *core/delegation.md
  - local/project-rules.md

output: CLAUDE.md
```

Then run: `claudeutils compose agents/compose.yaml`

## Phase Mapping

| Phase | Goal | Status | Notes |
|-------|------|--------|-------|
| 1 | Extract fragments to agent-core | ✅ Done | Files copied to scratch, fragmented |
| 2 | Analysis (compose scripts, configs) | ✅ Done | Reports in consolidation/analysis/ |
| 3 | Design unified composition API | ✅ Done | compose-api.md (34K) ready |
| 4 | Integrate content into agent-core | ⚠️  Partial | Skills done, configs should move |
| 5 | Build composition tooling | ❌ Blocked | Needs compose.py implementation |
| 6 | Deploy compose.yaml to projects | ❌ Blocked | Depends on Phase 5 |
| 7 | Validation and testing | ❌ Blocked | Depends on Phase 5-6 |

## Next Actions

### Option A: Complete Composition System (Original Plan)
1. Move configs from fragments/ to configs/ directory in agent-core
2. Implement src/claudeutils/compose.py per design doc
3. Add `claudeutils compose` CLI command
4. Create compose.yaml files in both projects
5. Generate CLAUDE.md files from composition
6. Update pytest-md agent-core submodule to latest

### Option B: Defer Composition System (Pragmatic)
1. Accept current manual CLAUDE.md maintenance
2. Focus on skill development and improvement
3. Update pytest-md agent-core submodule to latest
4. Document composition system as future enhancement
5. Keep design docs for when it's needed

### Option C: Simplify Composition System
1. Skip full YAML composition tooling
2. Create simple bash script for fragment concatenation
3. Update pytest-md submodule
4. Ship lightweight solution now, full system later

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

## Risk Assessment

**Low Risk:**
- agent-core is stable and actively maintained
- Skills are production-tested in claudeutils
- Submodule pattern works well

**Medium Risk:**
- pytest-md falling behind on skill improvements
- Manual CLAUDE.md maintenance in multiple projects
- Config files in wrong directory (minor)

**High Risk:**
- None currently

## Recommendation

**Short term:** Option A partial (update pytest-md submodule, document deferral)
**Long term:** Revisit composition system when multi-project management becomes painful

The composition tooling design is solid, but there's no urgency. Current manual approach works and agent-core delivers value through skills and fragments.
