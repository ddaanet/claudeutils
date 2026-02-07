# Session: Plugin Migration — Runbook Planning (Partial)

**Status:** Runbook outline reviewed, Phase 0 drafted and reviewed. Planning paused for commit.

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

**Phase 0 Drafted and Vetted:**
- Created runbook-phase-0.md with directory rename implementation
- vet-agent found 13 issues (5 critical, 5 major, 3 minor) including:
  - Missing .claude/rules/*.md path updates
  - Missing 6 plan-specific agent files
  - Missing 41 references in plans/ directories
  - Makefile target rename needed
  - Incomplete grep pattern (excluded critical directories)
- Vet report: plans/plugin-migration/reports/phase-0-review.md

## Pending Tasks

- [ ] **Apply Phase 0 vet fixes and continue phase expansion** — Load vet report, apply all fixes to Phase 0, then expand Phases 1-6 | sonnet
  - Phase 0 needs: .claude/rules/ updates, plan-specific agents, Makefile changes, comprehensive symlink validation
  - After Phase 0 complete: expand and review Phases 1-6 (each phase → vet → fix → next)
  - Each phase review should use vet-agent (review-only mode)
  - Final step: prepare-runbook.py → handoff → commit

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
