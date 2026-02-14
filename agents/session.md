# Session Handoff: 2026-02-14

**Status:** RCA analysis complete, requirements artifact written for workflow-rca-fixes (17 FRs).

## Completed This Session

**RCA Analysis:**
- Collected and summarized all 5 in-tree RCA reports (general-step detection, file growth, vet over-escalation, UNFIXABLE evidence, process review)
- Mapped RCA fixes to existing Workflow improvements sub-items — identified 13 uncaptured fixes
- Clustered into 5 editing sessions: runbook-review overhaul, vet agent overhaul, outline review agent, runbook skill cleanup, process RCA gaps

**Requirements Capture:**
- Wrote `plans/workflow-rca-fixes/requirements.md` — 17 FRs, research-grounded
- Research grounding: van der Aalst workflow net soundness, IBM ODC defect taxonomy, Microsoft agent orchestration patterns, DyFlow replanning framework
- FR-1 through FR-11: Direct RCA fixes (prose edits to existing files)
- FR-12/13: Agent composition infrastructure (skills frontmatter injection, memory index for sub-agents)
- FR-14/15: Design skill fixes (Phase C density, repetition helper prescription)
- FR-16: Deliverable review as post-orchestration workflow step
- FR-17: Execution-to-planning feedback requirement (deferred to error-handling framework)

**Design Discussion Outcomes:**
- Agent composition mechanism: `skills:` YAML frontmatter injects prompt content — native, no build step
- Memory index for sub-agents: index injected via `skills:`, recall via Bash (`when-resolve.py`)
- Deliverable review placement: post-orchestration, requires opus session
- Execution feedback: local replanning (refactor) vs global replanning (escalate) gap identified
- Commit CLI tool: branched to pending task, not on this worktree

## Pending Tasks

- [ ] **Workflow RCA fixes** — `/design plans/workflow-rca-fixes/` | sonnet
  - Requirements complete: `plans/workflow-rca-fixes/requirements.md` (17 FRs)
  - Open questions: Q-1 (skills injection scope), Q-2 (token cost), Q-3 (conformance gate placement)
  - Dependency: skill-reviewer verdict on fragment-as-skill viability (FR-12)
  - 5 clusters: runbook-review, vet agent, outline review, runbook skill, design skill
  - RCA source reports: `plans/reports/rca-*-opus.md`, `plans/process-review/rca.md`
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

**Skills frontmatter behavior unknown:**
- Q-1: Does `skills:` inject full SKILL.md or specific sections? Affects fragment skill design
- Q-2: Token cost per injection — crowding risk with multiple skills
- Test with plan-reviewer (only current user of `skills:`) to answer empirically

**Execution feedback gap connects to error-handling:**
- FR-17 documents requirement, implementation in `wt/error-handling`
- RCA data (when-recall test plan redesign incident) provides grounding for error-handling design
- All 5 RCAs provide grounding material for error classification taxonomy

## Next Steps

Start `/design plans/workflow-rca-fixes/` to resolve open questions and produce design for the 17 FRs.

---
*Handoff by Sonnet. Requirements captured, ready for design.*
