# Session Handoff: 2026-03-02

**Status:** Fix orch-evo findings in progress. 15/19 findings fixed, 2 test files need splitting to pass line limits. Precommit blocked.

## Completed This Session

**Orchestrate evolution — fix deliverable review findings (partial):**
- Classification: Composite task → 9 Simple, 6 Moderate, 4 no-action
- Group A (Simple batch, complete): M-2 dead code removal (`generate_agent_frontmatter`, `generate_phase_agent`, stale `crew-` fallback), m-1 "read ahead" clause, m-3 SKILL.md inline phase source, m-4 completion diff baseline, m-5 single-phase outline ref, m-6 PHASE_BOUNDARY marker, m-7 heuristic framing, m-8 refactor.md resume trigger, m-13 tester assertion tightening
- Group B (M-1, complete): Wired `phase_preambles` through `generate_default_orchestrator` — IN scope from preamble first line, OUT scope lists other phases. Added 4 tests in `TestPhaseSummariesFromPreambles`
- Group C (tests, complete): m-9 TDD corrector model frontmatter assertions, m-10 role-specific scope enforcement tests (tester, implementer, test-corrector, impl-corrector), m-12 verify-red.sh zero-argument test, m-11 verify-step.sh precommit failure test (submodule path test deferred — requires real submodule setup)
- Group D (M-3, complete): Added Section 3.6 Refactor Dispatch to SKILL.md — corrector report marker-based signaling, refactor agent dispatch protocol
- Non-actionable: m-2 (intentional simplification), m-14/m-15/m-16 (acceptable enhancements)

**Precommit blocker:** `test_prepare_runbook_orchestrator.py` (453 lines) and `test_prepare_runbook_tdd_agents.py` (442 lines) exceed 400-line limit. Need quality-first splitting per decisions.

**Discussion: lint-gated recall:**
- Existing tasks on main: Lint-gated recall (PostToolUse injection) + Lint recall gate (PreToolUse pass)
- Refinement: per-error-type gating (not just first-red-after-green). Each novel error category triggers fresh recall.
- Tuick (`~/code/tuick/`) has reusable errorformat parsing infrastructure (ErrorformatEntry, tool_registry, grouping). Only new piece: error category → recall keyword mapping table.

**Learnings appended:**
- When lint-gated recall needs error categorization

## In-tree Tasks

- [x] **Orch-evo plan format** — `/inline plans/orchestrate-evolution` | sonnet
- [x] **Orch-evo TDD agents** — `/inline plans/orchestrate-evolution` | sonnet
- [x] **Orch-evo skill rewrite** — `/inline plans/orchestrate-evolution` | opus | restart
- [x] **Orch-evo review** — `/deliverable-review plans/orchestrate-evolution` | opus | restart
- [>] **Fix orch-evo findings** — `/design plans/orchestrate-evolution/reports/deliverable-review.md` | sonnet
  - 15/19 findings fixed. Remaining: split 2 test files to pass line limits, then precommit + commit
  - Plan: orchestrate-evolution | Status: review-pending
- [ ] **Codify branch awareness** — Add feature-branch gate to `/codify` + soft-limit age calculation | sonnet

## Blockers/Gotchas

- Test file line limits: `test_prepare_runbook_orchestrator.py` (453 > 400), `test_prepare_runbook_tdd_agents.py` (442 > 400). Recall loaded: "code quality first" before splitting, check for dedup/extraction opportunities.
- Submodule changes: agent-core has 3 dirty files (prepare-runbook.py, SKILL.md, refactor.md). Parent repo sees pointer change.

## Next Steps

Resume fix task: split the two test files (quality-first per decisions), run precommit, commit. Then codify branch awareness.
