# Session Handoff: 2026-02-12

**Status:** Workflow pipeline unification design complete. Ready for planning: `/plan-adhoc plans/workflow-fixes/design.md`

## Completed This Session

### Design: Workflow pipeline unification (Phase A+B+C complete)

**Scope evolution across sessions:**
1. Prior session: 10-artifact patch approach → superseded by pipeline analysis (G1-G7)
2. This session: G1-G7 gap patches → superseded by unification after user identified root cause

**Root cause insight:** The bifurcation (/plan-tdd vs /plan-adhoc) forces a binary choice on mixed work. 75% of skill content is identical. Most gaps (G1-G5, G7) trace to having two parallel paths with inconsistent review gates.

**Design approach:** Unified `/plan` skill with per-phase type tagging. Each phase tagged `type: tdd` or `type: general`. Mixed runbooks supported — behavioral phases get RED/GREEN cycles, infrastructure phases get task steps.

**Key decisions:**
- D1: Per-phase granularity (not per-runbook or per-step)
- D2: Clean rename tdd-plan-reviewer → plan-reviewer (v0.0, no aliases)
- D3: Fix-all pattern eliminates recommendation dead-ends
- D4: Centralized pipeline contracts in `agents/decisions/pipeline-contracts.md`
- D5: LLM failure mode criteria in review-plan skill (four axes, all phase types)
- D6: Outline sufficiency for TDD (<3 phases AND <10 cycles)
- D7: Orchestrate completion unified (both types vet, resolves G7)

**Artifacts:**
- Design: `plans/workflow-fixes/design.md` — vetted by opus (3 major + 4 minor, all fixed)
- Outline: `plans/workflow-fixes/outline.md` — reviewed (Ready)
- Exploration: `plans/workflow-fixes/reports/explore-plan-unification.md` — 75% structural overlap evidence

### Prior work preserved

- Pipeline analysis (T1-T6 transformations, G1-G7 gaps) — incorporated into design rationale
- LLM failure mode methodology from `agents/decisions/runbook-review.md` — integrated into review-plan skill spec

## Pending Tasks

- [ ] **Execute workflow pipeline unification** — `/plan-adhoc plans/workflow-fixes/design.md` (last adhoc before unification) | opus
  - Design: `plans/workflow-fixes/design.md`
  - Build order: pipeline-contracts → review-plan skill → plan-reviewer agent → unified /plan skill → update design/orchestrate/terminology → reference sweep → sync-to-parent → delete deprecated
  - Execution model: opus for architectural artifacts (skill/agent definitions)

- [ ] **Fix worktree-update runbook** — Apply findings from LLM failure mode review | sonnet
  - Report: `plans/worktree-update/reports/runbook-review-llm-failure-modes.md`
  - Priority 1: Add jobs.md auto-resolve cycle
  - Priority 2: Merge vacuous cycles, density, add Phase 6 checkpoint

- [ ] **Agentic process review and prose RCA** — Analyze why deliveries are "expensive, incomplete, buggy, sloppy, overdone" | opus

- [ ] **Workflow fixes from RCA** — Implement process improvements from RCA | sonnet
  - Depends on: RCA completion

- [ ] **RCA: Vet-fix-agent UNFIXABLE labeling** — Analyze why agent labeled stylistic judgment as UNFIXABLE | sonnet

- [ ] **Consolidate learnings** — learnings.md at 350 lines (soft limit 80) | sonnet

- [ ] **Remove duplicate memory index entries on precommit** — Autofix or fail on duplicate index entries | sonnet

- [ ] **Update design skill** — Phase C density checkpoint (TDD non-code marking now handled by per-phase typing) | sonnet

- [ ] **Handoff skill memory consolidation worktree awareness** — Only consolidate memory in main repo or dedicated consolidation worktree | sonnet

- [ ] **Fix skill-based agents not using skills prolog section** — Agents duplicate content instead of referencing skills via `skills:` frontmatter | sonnet

- [ ] **Upstream plugin-dev: document `skills:` frontmatter** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` field | sonnet

## Blockers / Gotchas

**Two methodology documents exist:**
- `agents/decisions/review-methodology.md` — sonnet-generated, user distrusts, do NOT use
- `agents/decisions/deliverable-review.md` — ISO-grounded, use this one

**Learnings.md over soft limit:**
- 350 lines, ~55 entries — consolidation deferred until entries age (≥7 active days required)

**Design skill "Update design skill" task note:**
- The TDD non-code steps refinement is now addressed by per-phase typing. Only Phase C density checkpoint remains.

## Reference Files

- `plans/workflow-fixes/design.md` — Unification design (vetted by opus)
- `plans/workflow-fixes/outline.md` — Unification outline (reviewed, all questions resolved)
- `plans/workflow-fixes/reports/design-review.md` — Opus design review (3 major + 4 minor, all fixed)
- `plans/workflow-fixes/reports/outline-review-v2.md` — Outline review v2 (Ready)
- `plans/workflow-fixes/reports/explore-plan-unification.md` — Structural overlap analysis (75% shared)
- `plans/worktree-update/reports/runbook-review-llm-failure-modes.md` — LLM failure mode review
- `agents/decisions/runbook-review.md` — LLM failure mode methodology (four axes)
