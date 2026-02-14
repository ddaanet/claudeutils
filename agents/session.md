# Session Handoff: 2026-02-14

**Status:** Design Phase B complete for workflow-rca-fixes (18 FRs). Outline reviewed, validated, ready for Phase C (design document).

## Completed This Session

**FR-18 Added:**
- Added FR-18 (review-fix integration rule) to `plans/workflow-rca-fixes/requirements.md`
- Updated FR-1 with behavioral vacuity detection requirement

**Design Phase A (Research + Outline):**
- Three parallel explorations: target files structure, skills frontmatter behavior, review-plan skill
- Q-1 resolved: `skills:` injects full SKILL.md (all-or-nothing, no section selection)
- Q-2 resolved: ~300-400 tokens per small skill, ~1200 for large, 2-3 skills per agent manageable
- Q-3 resolved: conformance gate = outline-review-agent (FR-11), scaffolding detection = Section 11.1 (FR-2)
- CC system prompt gap analysis: sub-agents receive minimal prompt — no prose quality, no token economy, no tmp-directory. Gap analysis report: `plans/workflow-rca-fixes/reports/explore-agent-knowledge-gaps.md`
- Revised FR-12: bundle deslop + token-economy + tmp-directory into `project-conventions` skill (~400 tokens). Drop code-removal (CC covers "delete unused"). Keep error-handling separate (~100 tokens) for bash-heavy agents.
- Outline produced, reviewed by outline-review-agent (7 fixes applied, assessment: Ready)

**Design Phase B (Iterative Discussion) — Key Decisions:**
- Reflexive bootstrapping: reordered phases by tool-usage dependency (composition → runbook review → vet → outline review → skills → cleanup). Each improvement applied before downstream agent uses it.
- Review-after-edit rule: skill-reviewer for skills, agent-creator (plugin-dev, has Write) for agents, vet-fix-agent for decisions/fragments
- Diagnostic opus review: interactive RCA after reviewer pass (Phases 1-4 only). Session stops primed with methodology + prompts, user switches to opus. NOT delegated — opus needs full conversation context.
- Restart rule: after every agent/fragment edit. Skill content resolves at spawn time (no restart for content-only).
- Plugin-dev prerequisites: load skill-development + agent-development before Phase 1. Read continuation passing design + existing non-invocable skill patterns.

**Research Grounding:**
- Anthropic context engineering: focused task context over comprehensive information
- ACE framework (arXiv 2510.04618): 10.6% performance gain from strategic knowledge injection
- MAR (Multi-Agent Reflexion): multi-agent reflection breaks "degeneration of thought"
- Flow-of-Action: SOP-constrained RCA reduces hallucinations
- Reflexion (NeurIPS 2023): verbal reinforcement learning without weight updates

**Exploration Reports:**
- `plans/workflow-rca-fixes/reports/explore-target-files.md` — 7 target files structure
- `plans/workflow-rca-fixes/reports/explore-skills-frontmatter.md` — Skills injection mechanism + Q-1/Q-2
- `plans/workflow-rca-fixes/reports/explore-review-plan-skill.md` — Review-plan Section 11 analysis
- `plans/workflow-rca-fixes/reports/explore-agent-knowledge-gaps.md` — CC system prompt gap analysis
- `plans/workflow-rca-fixes/reports/outline-review.md` — Outline review (Ready)
- `plans/reports/rca-runbook-outline-review.md` — RCA from worktree-fixes (3 patterns, FR-18 source)

## Pending Tasks

- [>] **Workflow RCA fixes** — Resume `/design plans/workflow-rca-fixes/` Phase C | sonnet
  - Requirements: `plans/workflow-rca-fixes/requirements.md` (18 FRs)
  - Outline: `plans/workflow-rca-fixes/outline.md` (reviewed, Ready)
  - Open questions: all resolved (Q-1, Q-2, Q-3)
  - Phase C: generate design.md, checkpoint commit, design-vet-agent review, handoff+commit
  - Prerequisite for Phase C: check Anthropic official skills repo for RCA patterns to integrate into diagnostic review methodology
- [ ] **Diagnostic opus review methodology** — New task from design discussion | `/requirements` | opus
  - Interactive post-vet RCA using domain-specific methodology + iterative deepening
  - Extends /reflect skill with proactive invocation, two-model separation, feedback loops
  - Needs: review methodology documents (design-review, agent-review), integration into workflow
  - Research: MAR, Flow-of-Action, Reflexion, Five Whys, TAMO, AgentErrorTaxonomy
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

**Diagnostic review methodology gap:**
- No formal design-review-methodology.md or agent-review-methodology.md exists
- For workflow-rca-fixes, use pipeline-contracts + plugin-dev patterns as interim
- Formal methodology documents are follow-on work (diagnostic opus review methodology task)

## Next Steps

Resume `/design plans/workflow-rca-fixes/` Phase C — generate design.md from outline.

---
*Handoff by Sonnet. Design Phase B complete, outline validated.*
