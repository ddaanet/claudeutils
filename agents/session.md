# Session Handoff: 2026-02-12

**Status:** Workflow pipeline unification complete. `/runbook` skill live, old skills deleted, precommit green.

## Completed This Session

### Executed: Workflow pipeline unification

Bootstrapped around broken `/plan-adhoc` — executed directly from design (Tier 2 assessment, no runbook needed for prose artifact work).

**Created:**
- `agents/decisions/pipeline-contracts.md` — centralized I/O contracts (T1-T6)
- `agent-core/skills/review-plan/SKILL.md` — unified review skill (replaced review-tdd-plan, added general + LLM failure mode criteria)
- `agent-core/agents/plan-reviewer.md` — replacement agent (replaced tdd-plan-reviewer)
- `agent-core/skills/runbook/SKILL.md` — unified planning skill (2205→810 lines, 63% reduction)
- `agent-core/skills/runbook/references/` — migrated from plan-tdd

**Modified:** design, orchestrate, vet, workflows-terminology skills + continuation-passing, execute-rule, shortcuts, plugin-dev-validation, design-vet-agent, review-tdd-process, handoff-haiku, remember consolidation-patterns

**Deleted:** plan-tdd/, plan-adhoc/, review-tdd-plan/, tdd-plan-reviewer.md

**Vetted:** Both major artifacts — no UNFIXABLE issues
- `plans/workflow-fixes/reports/review-plan-skill-vet.md`
- `plans/workflow-fixes/reports/runbook-skill-vet.md`

**Key decision:** Skill named `/runbook` not `/plan` — `/plan` conflicts with Claude Code CLI built-in (EnterPlanMode).

### Updated: Residual docs references

Updated 3 workflow documentation files to use unified naming:
- `agent-core/docs/tdd-workflow.md` — 7 replacements (plan-tdd → runbook, tdd-plan-reviewer → plan-reviewer)
- `agent-core/docs/general-workflow.md` — 11 replacements (plan-adhoc → runbook, added LLM failure mode detection)
- `agent-core/skills/handoff/examples/good-handoff.md` — 2 replacements

Commits: agent-core 042f892, main 3e417dc

### Prior session: Design (Phase A+B+C)

Design approach, decisions D1-D7, and artifacts preserved in `plans/workflow-fixes/design.md`.

## Pending Tasks

- [ ] **Fix worktree-update runbook** — Apply findings from LLM failure mode review | sonnet
  - Report: `plans/worktree-update/reports/runbook-review-llm-failure-modes.md`
  - Priority 1: Add jobs.md auto-resolve cycle
  - Priority 2: Merge vacuous cycles, density, add Phase 6 checkpoint

- [ ] **Agentic process review and prose RCA** — Analyze why deliveries are "expensive, incomplete, buggy, sloppy, overdone" | opus

- [ ] **Workflow fixes from RCA** — Implement process improvements from RCA | sonnet
  - Depends on: RCA completion

- [ ] **RCA: Vet-fix-agent UNFIXABLE labeling** — Analyze why agent labeled stylistic judgment as UNFIXABLE | sonnet

- [ ] **Consolidate learnings** — learnings.md at 361 lines (soft limit 80), 0 entries ≥7 days | sonnet

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
- 361 lines, ~57 entries — consolidation deferred until entries age (≥7 active days required)

**Restart required after this commit:**
- New agent (plan-reviewer) and skills (runbook, review-plan) created — Claude Code discovers at session start

## Reference Files

- `plans/workflow-fixes/design.md` — Unification design (vetted by opus)
- `plans/workflow-fixes/reports/review-plan-skill-vet.md` — Review-plan skill vet (clean)
- `plans/workflow-fixes/reports/runbook-skill-vet.md` — Runbook skill vet (clean)
- `agents/decisions/pipeline-contracts.md` — Pipeline I/O contracts
- `agents/decisions/runbook-review.md` — LLM failure mode methodology (four axes)
