# Session Handoff: 2026-02-12

**Status:** Runbook review methodology created and integrated into planning infrastructure. runbook-review.md move resolved (keep in place).

## Completed This Session

### LLM Failure Mode Review Methodology

Web research on LLM code generation failure modes in TDD contexts, then applied to worktree-update outline.

**Research grounding:** 3 papers (Jiang 2024, WebApp1K 2025, Mathews & Nagappan ASE 2024). Research provided citations and mechanism explanations but the detection axes came from manual analysis. One genuinely new axis (checkpoint spacing) from WebApp1K instruction-loss finding.

**Methodology document:** `agents/decisions/runbook-review.md` — 4 review axes:
- **Vacuity:** Cycles/steps that don't constrain implementation (scaffold-only, wiring, presentation)
- **Dependency ordering:** Intra-phase forward dependencies (dedup before container creation)
- **Cycle density:** Collapsible edge-case clusters, trivial phases
- **Checkpoint spacing:** Gaps >10 cycles or >2 phases without quality gate

**Applied to worktree-update outline:** `plans/worktree-update/reports/outline-review-4-llm-failure-modes.md`
- 5 vacuous cycles (0.1, 5.1, 5.6, 5.9, 6.1)
- 1 critical ordering issue (Phase 2: dedup before nested key creation)
- ~7 collapsible cycles (48 → ~41)
- Checkpoint gaps (only Phase 7 has explicit checkpoint)

### Planning Infrastructure Improvements

Integrated the 4 review axes into planning workflow at two levels:

**Review agent (detective):** `agent-core/agents/runbook-outline-review-agent.md` — added vacuity, intra-phase ordering, step/cycle density, checkpoint spacing criteria. Shared by both plan-tdd and plan-adhoc.

**Generation rules (preventive):**
- `agent-core/skills/plan-tdd/SKILL.md` — Phase 1.5 outline quality + Phase 3.1 cycle ordering: branch-point requirement, foundation-first ordering, edge-case collapse
- `agent-core/skills/plan-adhoc/SKILL.md` — Point 0.75 outline quality: functional outcome requirement, foundation-first ordering, collapsible step detection

### runbook-review.md move — resolved as no-op

Analyzed whether `agents/decisions/runbook-review.md` should move into agent-core. Conclusion: low value, moderate cost. Content already inlined in consumers (`runbook-outline-review-agent.md` has criteria baked in, `(ref: ...)` markers were attribution only). Removed 4 attribution markers from review agent. Dropped pending task.

## Pending Tasks

- [ ] **Plan worktree-update (Phase 3-5)** — Continue phase-by-phase cycle expansion | sonnet
  - Plan: plans/worktree-update
  - Phase 0-1.5 complete (outline validated)
  - Next: Phase 3 (phase-by-phase expansion), then Phase 4 (assembly), Phase 5 (final review)
  - Command: Resume /plan-tdd from Phase 3 (already past intake and outline)

- [ ] **Agentic process review and prose RCA** — Analyze why deliveries are "expensive, incomplete, buggy, sloppy, overdone" | opus
  - Scope: worktree-skill execution process, not deliverables
  - Signals: plan specified opus but session showed haiku, vacuous tests passed vet, vet checked presence not correctness
  - Evidence now available: worktree-skill-fixes complete

- [ ] **Workflow fixes** — Implement process improvements from RCA | sonnet
  - Depends on: RCA completion

- [ ] **RCA: Vet-fix-agent UNFIXABLE labeling** — Analyze why agent labeled stylistic judgment as UNFIXABLE | sonnet

- [ ] **Consolidate learnings** — learnings.md at 320 lines (soft limit 80), 0 entries ≥7 days | sonnet
  - Run `/remember` when entries age sufficiently

- [ ] **Remove duplicate memory index entries on precommit** — Autofix or fail on duplicate index entries | sonnet

- [ ] **Update design skill** — Two refinements: (1) TDD non-code steps: non-code artifacts (skill, docs, justfile) explicitly marked non-TDD; (2) Phase C density checkpoint: if outline already has architecture+decisions+scope+impl sequence, promote to design.md (add Doc Perimeter) instead of full opus expansion | sonnet

- [ ] **Handoff skill memory consolidation worktree awareness** — Only consolidate memory in main repo or dedicated consolidation worktree | sonnet
  - Add worktree detection: skip consolidation if `git rev-parse --show-toplevel` appears in `git worktree list` output
  - Rationale: Consolidation modifies shared docs (learnings.md, decisions/, fragments) — parallel worktree modifications cause merge conflicts

## Blockers / Gotchas

**Two methodology documents exist:**
- `agents/decisions/review-methodology.md` — sonnet-generated, user distrusts, do NOT use
- `agents/decisions/deliverable-review.md` — ISO-grounded, use this one
- Cleanup: delete review-methodology.md (fixes confirmed it's fully superseded)

**Learnings.md over soft limit:**
- 320 lines, 54 entries, 0 entries ≥7 days — consolidation deferred until entries age

**Justfile wt-merge gap:**
- Currently only checks OURS side for clean tree — THEIRS check needed (step 8 scope)

## Reference Files

- `plans/worktree-update/design.md` — Worktree update design (9 steps: 7 TDD + non-code + refactor)
- `plans/worktree-update/runbook-outline.md` — Validated runbook outline (48 TDD cycles, 9 phases)
- `plans/worktree-update/reports/outline-review-1.md` — Outline review report with expansion guidance
- `plans/worktree-update/reports/vet-review-2.md` — Design review report
- `plans/worktree-skill/outline.md` — Ground truth design spec (worktree-skill)
- `agents/decisions/deliverable-review.md` — Post-execution review methodology
- `agents/decisions/runbook-review.md` — Pre-execution runbook review methodology (LLM failure modes)
- `plans/worktree-update/reports/outline-review-4-llm-failure-modes.md` — Applied review findings
