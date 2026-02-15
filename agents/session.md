# Session Handoff: 2026-02-15

**Status:** Runbook outline generated and reviewed for workflow-rca-fixes. Ready for interactive outline review before runbook promotion.

## Completed This Session

**Runbook Planning (workflow-rca-fixes):**
- Tier 3 assessment: 23 files, 6 phases, multi-session, mixed models → Full Runbook
- Phase 0.5: Read full documentation perimeter (14+ files), verified all target files exist
- Loaded plugin-dev:skill-development + plugin-dev:agent-development prerequisites
- Phase 0.75: Generated outline — 16 steps, 6 phases, 20 FRs mapped
- Runbook skill updated: commit-before-review rule at Phase 0.75 + Phase 1
- Outline review (runbook-outline-review-agent): Ready, 6 fixes applied
  - Critical: vet-fix-agent.md at 436 lines, +150 → 586 → split taxonomy to `vet-taxonomy.md`
  - Major: Phase 5 restart must include workflows-terminology.md (fragment loaded via CLAUDE.md)
  - 4 minor: bootstrap notes, step dependency, growth projection, Phase 4 density justification
- Phase 0.85: No consolidation candidates
- Phase 0.9: 16 items, no callbacks
- Phase 0.95: Sufficiency check passed — outline detailed enough for promotion

**Prior Session (Design):**
- Design complete: `plans/workflow-rca-fixes/design.md` (6 phases, 20 FRs)
- Diagnostic review complete: 3 major findings fixed (C-1, F-1, CL-1)
- Early bootstrap: project-conventions skill, design-vet-agent + outline-review-agent updated
- Reports: `plans/workflow-rca-fixes/reports/` (7 exploration + review reports)

## Pending Tasks

- [ ] **Workflow RCA fixes** — Interactive outline review then promote to runbook | opus
  - Outline: `plans/workflow-rca-fixes/runbook-outline.md` (16 steps, reviewed Ready)
  - Outline review: `plans/workflow-rca-fixes/reports/runbook-outline-review.md`
  - Design: `plans/workflow-rca-fixes/design.md` (20 FRs, 6 phases)
  - Requirements: `plans/workflow-rca-fixes/requirements.md`
  - Next: interactive opus review of outline, then promote to runbook.md, then Phase 4 (prepare-runbook.py)
  - Key review finding: vet-fix-agent.md needs taxonomy split (436 + 150 = 586 lines)
- [ ] **Diagnostic opus review methodology** — New task from design discussion | `/requirements` | opus
  - Interactive post-vet RCA using domain-specific methodology + iterative deepening
  - Extends /reflect skill with proactive invocation, two-model separation, feedback loops
  - Needs: review methodology documents (design-review, agent-review), integration into workflow
  - Research: MAR, Flow-of-Action, Reflexion, Five Whys, TAMO, AgentErrorTaxonomy
  - Design review methodology conversation: `tmp/design-review-methodology-synthesis.md`, `tmp/design-review-methodology-critique.md`
  - Taxonomy (6 categories): completeness, consistency, feasibility, clarity, traceability, coupling
  - Two-tier context augmentation: always-inject (skills prolog) vs index-and-recall (on-demand). Haiku paradox resolved: discovery stays with capable agents, haiku gets pre-assembled context
  - Methodology as skill referenced in design-vet-agent + outline-review-agent `skills:` frontmatter
- [ ] **Workflow improvements** — Remaining sub-items not captured in workflow-rca-fixes | sonnet
  - Orchestrate evolution — designed, stale Feb 10, refresh after RCA
  - Fragments cleanup — remove fragments duplicating skills/workflow
  - Reflect skill output — RCA should produce pending tasks, not inline fixes
  - Tool-batching.md — add Task tool parallelization guidance with examples
  - Orchestrator delegate resume — resume delegates with incomplete work
  - Agent output optimization — remove summarize/report language from agents
  - Investigation prerequisite rule review
  - Commit skill optimizations — remove handoff gate, Gate B coverage ratio, branching after precommit
- [ ] **Commit CLI tool** — CLI for precommit/stage/commit across both modules | `/design` | sonnet
  - Modeled on worktree CLI pattern (mechanical ops in CLI, judgment in skill)
  - Single command: precommit → stage → commit in main + agent-core submodule
  - Override flag for precommit skip
  - Combined status output after commit
- [ ] **Workflow formal analysis** — Formal verification of agent workflow | `/requirements` then `/design` | opus
  - Candidates: TLA+ (temporal), Alloy (structural), Petri nets (visual flow)
  - Separate requirements artifact needed
- [ ] **Build pushback into conversation process** → `wt/pushback` — `/design plans/pushback/requirements.md` | opus
- [ ] **Codebase quality sweep** — Tests, deslop, factorization, dead code | sonnet
- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
- [ ] **Design workwoods** — `/design plans/workwoods/requirements.md` | opus
- [ ] **Error handling framework design** → `wt/error-handling` — Resume `/design` Phase B | opus
- [ ] **Execute plugin migration** — Refresh outline then orchestrate | sonnet
- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
- [ ] **Handoff skill memory consolidation worktree awareness** — Only consolidate in main repo or dedicated worktree | sonnet
- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet
- [ ] **Learning ages computation after consolidation** — Verify age calculation correct when learnings consolidated/rewritten | sonnet
- [ ] **Model tier awareness hook** — Hook injecting "Response by Opus/Sonnet/Haiku" into context | sonnet | restart
- [ ] **Precommit validation improvements** — Expand precommit checks | sonnet
- [ ] **Protocolize RED pass recovery** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
- [ ] **Upstream plugin-dev: document skills frontmatter** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` field | sonnet

## Worktree Tasks

- [ ] **Build pushback into conversation process** → `wt/pushback` — `/design plans/pushback/requirements.md` | opus
- [ ] **Error handling framework design** → `wt/error-handling` — Resume `/design` Phase B | opus
- [ ] **Workflow improvements** → `workflow-improvements` — Process fixes from RCA + skill/fragment/orchestration cleanup | sonnet
- [ ] **Worktree fixes** → `worktree-fixes` — `/design plans/worktree-fixes/` | opus

## Blockers / Gotchas

**Execution feedback gap connects to error-handling:**
- FR-17 documents requirement, implementation in `wt/error-handling`
- RCA data (when-recall test plan redesign incident) provides grounding for error-handling design
- All 5 RCAs provide grounding material for error classification taxonomy

**Diagnostic review methodology converging:**
- Taxonomy, iteration protocol, priming template designed in conversation
- Opus critique validated approach, identified haiku paradox (resolved: discovery at capable tier, pre-assembled context for haiku)
- Methodology skill + design-vet-agent integration planned as follow-on task
- Synthesis and critique in tmp/ (ephemeral — capture in requirements before cleanup)

## Next Steps

Interactive opus review of `plans/workflow-rca-fixes/runbook-outline.md` — then promote to runbook.md and run prepare-runbook.py.

---
*Handoff by Sonnet. Outline reviewed Ready, planning paused for interactive review.*
