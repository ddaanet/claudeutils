# Session Handoff: 2026-02-12

**Status:** Workflow pipeline redesign outline complete (Phase A+B). Supersedes previous 10-artifact patch approach. 7 structural gaps identified, 3 open questions await user input before Phase C (full design).

## Completed This Session

### Design: Workflow pipeline redesign (Phase A+B, second iteration)

**Scope expansion:** User requested complete dataflow/control flow audit of /design, /plan-tdd, /plan-adhoc, /orchestrate — not just 10 artifact patches. Previous outline superseded.

**Analysis performed:**
- Read all 4 core skill files (plan-adhoc 1136 lines, plan-tdd 1052 lines, orchestrate 475 lines, design loaded via /design invocation)
- Read all 4 review agent definitions (tdd-plan-reviewer, vet-fix-agent, vet-agent, runbook-outline-review-agent)
- Read review-tdd-plan skill (456 lines)
- Mapped pipeline as 6 transformations (T1-T6) with defect types and review gates

**Key finding:** T3 (outline → phase expansion) is the critical gap. All 4 LLM failure modes can be re-introduced during expansion, but the review gate either checks wrong criteria (TDD: prescriptive code only) or routes to wrong agent (adhoc: vet-fix-agent rejects planning artifacts).

**7 gaps identified:**
- G1: Adhoc phase review routes to vet-fix-agent which rejects planning artifacts
- G2: Autofix contradiction (agent fixes, then planner re-fixes)
- G3: No LLM failure mode re-validation after expansion
- G4: Report recommendations not consumed downstream (only Expansion Guidance works)
- G5: Agent name ambiguity ("vet agent" unspecified)
- G6: Missing scope IN/OUT context in review delegations
- G7: Orchestrate general completion doesn't actually vet

**Research grounding:** Four axes from `agents/decisions/runbook-review.md` (Jiang 2024, Fan 2025, Mathews 2024, Microsoft 2025) connect to G3 — vacuity, ordering, density, checkpoints.

**Outline written:** `plans/workflow-fixes/outline.md` — reviewed by outline-review-agent (Ready, 2 major + 4 minor fixed)

### Prior work preserved

- LLM failure mode integration into tdd-plan-reviewer (implemented via this design)
- Manual runbook review findings (report at `plans/worktree-update/reports/runbook-review-llm-failure-modes.md`)
- Exploration reports still valid for reference

## Pending Tasks

- [ ] **Complete workflow pipeline redesign** — Answer 3 open questions, then Phase C (full design) → `/plan-adhoc` | opus
  - Outline: `plans/workflow-fixes/outline.md`
  - Open Q1: Agent rename (tdd-plan-reviewer → plan-reviewer) — acceptable churn or keep name?
  - Open Q2: Edit precision for plan-adhoc (exact locations or semantic descriptions)?
  - Open Q3: I/O contracts location (embedded in skills or central decision doc)?
  - After design: `/plan-adhoc` → execute with opus for skill/agent edits

- [ ] **Fix worktree-update runbook** — Apply findings from LLM failure mode review | sonnet
  - Report: `plans/worktree-update/reports/runbook-review-llm-failure-modes.md`
  - Priority 1: Add jobs.md auto-resolve cycle
  - Priority 2: Merge vacuous cycles, density, add Phase 6 checkpoint

- [ ] **Agentic process review and prose RCA** — Analyze why deliveries are "expensive, incomplete, buggy, sloppy, overdone" | opus

- [ ] **Workflow fixes from RCA** — Implement process improvements from RCA | sonnet
  - Depends on: RCA completion

- [ ] **RCA: Vet-fix-agent UNFIXABLE labeling** — Analyze why agent labeled stylistic judgment as UNFIXABLE | sonnet

- [ ] **Consolidate learnings** — learnings.md at 319+ lines (soft limit 80), 0 entries ≥7 days | sonnet

- [ ] **Remove duplicate memory index entries on precommit** — Autofix or fail on duplicate index entries | sonnet

- [ ] **Update design skill** — Two refinements: (1) TDD non-code steps marked non-TDD; (2) Phase C density checkpoint | sonnet

- [ ] **Handoff skill memory consolidation worktree awareness** — Only consolidate memory in main repo or dedicated consolidation worktree | sonnet

- [ ] **Fix skill-based agents not using skills prolog section** — Agents duplicate content instead of referencing skills via `skills:` frontmatter | sonnet

- [ ] **Upstream plugin-dev: document `skills:` frontmatter** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` field | sonnet

## Blockers / Gotchas

**Two methodology documents exist:**
- `agents/decisions/review-methodology.md` — sonnet-generated, user distrusts, do NOT use
- `agents/decisions/deliverable-review.md` — ISO-grounded, use this one

**Learnings.md over soft limit:**
- 319+ lines, 54 entries, 0 entries ≥7 days — consolidation deferred until entries age

**Exploration agents can produce false findings:**
- quiet-explore reported plan-tdd reference files as "not found" when they exist
- Always verify file existence claims from exploration reports

## Reference Files

- `plans/workflow-fixes/outline.md` — Pipeline redesign outline (7 gaps, 3 decisions, transformation table)
- `plans/workflow-fixes/reports/outline-review.md` — Outline review (Ready, 2 major + 4 minor fixed)
- `plans/workflow-fixes/reports/explore-target-artifacts.md` — Artifact exploration (10 issues, prior iteration)
- `plans/workflow-fixes/reports/explore-audit-overlap.md` — Workflow-skills-audit overlap
- `plans/worktree-update/reports/runbook-review-llm-failure-modes.md` — LLM failure mode review (8 findings)
- `agents/decisions/runbook-review.md` — LLM failure mode methodology (four axes, research citations)
