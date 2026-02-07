# Session: Plugin Migration — Runbook Complete

**Status:** All 7 phases expanded and path-corrected. Ready for prepare-runbook.py assembly.

## Completed This Session

**Tier 3 Assessment (Full Runbook):**
- 50+ files affected (7 create, 8 modify, 30+ delete, 1 directory rename)
- 8 sequential components with dependencies
- Multiple models needed (haiku for operations, sonnet for skills/validation)
- Multi-session execution with restart requirements
- Point of no return at Component 6 (symlink cleanup)

**Runbook Outline Created and Reviewed:**
- Created comprehensive outline with 7 phases, 17 steps total
- Added Phase 0: Directory Rename (agent-core → edify-plugin) — critical missing step from prior plan
- Mapped all FR-* and NFR-* requirements to phases/steps
- All 8 design decisions (D-1 through D-8) reflected in phase structure
- hooks.json format corrected: direct format `{"PreToolUse": [...]}` not wrapper
- runbook-outline-review-agent found and fixed critical gap: directory rename must be explicit step
- Review report: plans/plugin-migration/reports/outline-review-2.md

**Phase 0 Fixed (13 Issues from Vet):**
- Applied all vet fixes: .claude/rules/ updates, plan-specific agents, Makefile, cache rename timing
- Added 6 file categories: core config, rules, agents, session, cache, historical docs
- Expanded from 9 steps to 16 steps with comprehensive validation
- Baseline grep → rename → categorical updates → post-grep comparison
- All 31 symlinks validated (not just one sample)
- Complexity upgraded from Trivial to Moderate

**Phases 1-6 Expanded:**
- Phase 1: Plugin manifest + version marker (consolidated to single step)
- Phase 2: Skills/agents verification + /edify:init + /edify:update creation
- Phase 3: hooks.json (direct format per D-4) + version-check hook + delete symlink-redirect
- Phase 4: portable.just extraction + root justfile import
- Phase 5: Symlink cleanup + config/doc updates + comprehensive validation (NFR-1, NFR-2)
- Phase 6: Cache regeneration (both root and edify-plugin)
- All phases updated: agent-core → edify-plugin throughout

## Pending Tasks

- [ ] **Run prepare-runbook.py and review** — Assemble phases into runbook.md, validate cycle numbering, review metadata | haiku
  - Command: `edify-plugin/bin/prepare-runbook.py plans/plugin-migration/runbook-outline.md` (requires `dangerouslyDisableSandbox: true`)
  - Review output for errors, check metadata calculation
  - Handoff and commit after successful assembly

## Blockers / Gotchas

**Phase 0 complexity underestimated:**
- Initial assessment: "trivial git mv + path updates"
- Reality: 13 issues found including multiple file categories missed (rules, agents, plans, Makefile)
- Suggests remaining phases will also need careful attention to detail

**Incomplete file discovery:**
- Grep pattern `--exclude-dir=edify-plugin` prevents finding self-references inside renamed directory
- Need two-phase grep: before git mv (find all) and after (verify updates)
- .claude/rules/ files contain agent-core references in YAML frontmatter (not caught by basic grep)

**Historical plan documentation:**
- 41 references in plans/ subdirectories (reflect-rca-prose-gates, validator-consolidation, etc.)
- Decision needed: update historical docs vs accept staleness
- Not breaking (just confusing) but should be addressed

**Phase-by-phase review pattern:**
- Each phase requires: draft → vet-agent review → apply fixes → proceed
- Cannot batch all 7 phases then review — issues compound
- Token implications: ~50K per phase (draft + review + fixes)

## Reference Files

- **plans/plugin-migration/design.md** — Design with 8 components, 8 decisions (D-1 through D-8)
- **plans/plugin-migration/runbook-outline.md** — Complete outline (7 phases, 17 steps)
- **plans/plugin-migration/runbook-phase-0.md** — Phase 0 draft (needs fixes from vet report)
- **plans/plugin-migration/reports/outline-review-2.md** — Outline review with all fixes applied
- **plans/plugin-migration/reports/phase-0-review.md** — Phase 0 vet review (13 issues identified)
