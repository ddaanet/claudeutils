# Session Handoff: 2026-02-15

**Status:** Runbook promoted to full format (runbook.md). Ready for interactive opus review before prepare-runbook.py.

## Completed This Session

**Runbook Promotion (workflow-rca-fixes):**
- Loaded plugin-dev:skill-development + plugin-dev:agent-development (prerequisites for Phase 1)
- Promoted outline → runbook.md following Phase 0.95 sufficiency path
- Runbook structure: 16 steps across 6 phases, all general type
- Frontmatter: name (workflow-rca-fixes), model (sonnet)
- Common Context: requirements summary, scope boundaries, key decisions, project structure
- All steps formatted: Objective, Prerequisites, Implementation, Expected Outcome, Error Conditions, Validation
- Phase checkpoints: restart requirements and diagnostic review guidance documented
- Final validation checklist included
- File: `plans/workflow-rca-fixes/runbook.md`

**Prior Sessions:**
- Outline generated and reviewed (runbook-outline-review-agent): 16 steps, 6 phases, 20 FRs mapped
- Interactive opus review: 3 fixes applied, deliverable-level traceability added to Phase 4
- Design complete: `plans/workflow-rca-fixes/design.md` (6 phases, 20 FRs)
- Reports: `plans/workflow-rca-fixes/reports/` (exploration + review artifacts)

## Pending Tasks

- [>] **Workflow RCA fixes** — Interactive opus review of runbook, then prepare-runbook | opus then sonnet
  - Runbook: `plans/workflow-rca-fixes/runbook.md` (16 steps, 6 phases, promoted from outline)
  - Outline: `plans/workflow-rca-fixes/runbook-outline.md` (outline-review complete)
  - Design: `plans/workflow-rca-fixes/design.md` (20 FRs, 6 phases)
  - Requirements: `plans/workflow-rca-fixes/requirements.md`
  - Next: Switch to opus, review runbook.md for quality, alignment, completeness
  - After opus review: run prepare-runbook.py, restart, `/orchestrate workflow-rca-fixes`
  - Key review finding: vet-fix-agent.md needs taxonomy split (Step 3.1 creates vet-taxonomy.md)
- [ ] **RCA failures to load skills during /runbook** — Investigate why plugin-dev skills required explicit invocation | sonnet
  - Context: /runbook skill documentation perimeter says "Load plugin-dev:skill-development before planning"
  - Expected: Auto-load or clearer failure message when missing
  - Actual: User had to manually invoke skills before runbook promotion could proceed
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

1. Switch to opus model for interactive runbook review
2. Review `plans/workflow-rca-fixes/runbook.md` for quality, alignment with design, completeness
3. After review fixes: sonnet session runs `agent-core/bin/prepare-runbook.py plans/workflow-rca-fixes/runbook.md`
4. Restart session, paste `/orchestrate workflow-rca-fixes`

---
*Handoff by Sonnet. Runbook promoted to full format, ready for opus review.*
