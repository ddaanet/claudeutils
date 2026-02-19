# Backlog

Deferred tasks. Pull into session.md Pending Tasks when capacity opens.

## Worktree

- [ ] **Worktree skill** — Full CLI + skill TDD | `/runbook plans/worktree-skill/design.md` | sonnet
- [ ] **Worktree merge from main** — `/design plans/worktree-merge-from-main/` | sonnet
- [ ] **Worktree merge data loss** — `/orchestrate worktree-merge-data-loss` | sonnet
- [ ] **Cross-tree requirements transport** — `/requirements` skill writes to main from worktree | sonnet
- [ ] **Handoff wt awareness** — Only consolidate memory in main repo | sonnet
- [ ] **Parallel orchestration** — Parallel dispatch via worktree isolation | sonnet
  - Plan: parallel-orchestration | Blocked on: worktree-skill + orchestrate-evolution

## Pipeline & Orchestration

- [ ] **Model directive pipeline** — Model guidance design → runbook → execution | opus
- [ ] **RED pass protocol** — Formalize orchestrator RED pass handling | sonnet
- [ ] **Runbook evolution** — Prose atomicity, self-modification, testing diamond | sonnet
  - Plan: runbook-evolution
- [ ] **Remaining workflow items** — /reflect output, tool-batching, agent output optimization | sonnet
  - Plan: remaining-workflow-items (FR-1, FR-2, FR-4 — FR-3/FR-5 absorbed)

## Memory & Learning

- [ ] **Remember skill update** — Resume `/design` Phase B | opus
  - Plan: remember-skill-update | Absorbs: memory-index auto-sync, learning ages consol
- [ ] **Merge learnings delta** — Reconcile learnings.md after diverged merge | sonnet
  - Plan: merge-learnings-delta
- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet

## Quality & Testing

- [ ] **Execute plugin migration** — Refresh outline then orchestrate | opus
  - Plan: plugin-migration | Status: ready (stale — Feb 9)
- [ ] **Migrate test suite to diamond** — Needs scoping | depends on runbook evolution
- [ ] **Test diagnostic helper** — Replace subprocess.run check=True with stderr surfacing | sonnet
- [ ] **Session.md validator** — Scripted precommit check | sonnet
  - Plan: session-validator | FR-2/FR-4 depend on worktree-cli-default

## Agents & Rules

- [ ] **Agent rule injection** — Distill sub-agent rules into agent templates | sonnet
- [ ] **Task agent guardrails** — Tool-call limits, regression detection, model escalation | sonnet
- [ ] **Pretool hook cd pattern** — Allow `cd <root> && <cmd>` in PreToolUse | sonnet
  - Plan: pretool-hook-cd-pattern
- [ ] **Handoff insertion policy** — Insert at priority position instead of append | sonnet

## Design (opus)

- [ ] **Behavioral design** — Nuanced conversational pattern intervention | opus
- [ ] **Diagnostic opus review** — Post-vet RCA methodology | opus
- [ ] **Safety review expansion** — Pipeline changes from grounding research | opus
  - Depends on: Explore Anthropic plugins
- [ ] **Ground state-machine review criteria** — State coverage validation research | opus
- [ ] **Workflow formal analysis** — Formal verification of agent workflow | opus
- [ ] **Design-to-deliverable** — tmux-like session automation | opus | restart

## Prototypes & Exploration

- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
- [ ] **Cache expiration prototype** — Debug log token metrics, measure TTL | sonnet
- [ ] **Explore Anthropic plugins** — Install all 28 official plugins | sonnet | restart
- [ ] **Tweakcc** — Remove redundant builtin prompts, inject custom | sonnet
  - Plan: tweakcc
- [ ] **TDD cycle test optimization** — Selective test rerun via dependency analysis | sonnet

## Small Fixes

- [ ] **Simplify when-resolve CLI** — Single argument with when/how prefix | sonnet
- [ ] **Fix task-context.sh task list bloat** — Filter/trim output | sonnet
- [ ] **Upstream skills field** — PR/issue for missing skills frontmatter | sonnet
- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet
