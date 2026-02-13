# Session Handoff: 2026-02-13

**Status:** Deliverable review complete. 4 critical, 4 major findings. Code fixes scoped for TDD, then mechanical steps (bin wrapper, skills, migration). Precommit broken until migration completes.

## Completed This Session

**Deliverable review:**
- Full review per `agents/decisions/deliverable-review.md` process
- 7/12 design steps complete, 1 partial, 4 missing (phases 5, 8, 9, 10 unexecuted)
- Report: `plans/when-recall/reports/deliverable-review.md`

**Design decisions resolved:**
- Headings DO get operator prefix: `/when X` → "When X", `/how X` → "How to X" (confirms D-6)
- Approach B (not A): `_extract_entry_key` includes operator in key, maps `/how` → "how to"
- `/how` stays as operator (not `/howto` — "howto" ≠ "how to" in exact matching)

## Pending Tasks

- [ ] **Fix when-recall code findings (TDD)** — `plans/when-recall/reports/deliverable-review.md` §3 | sonnet
  - Cycle 1: `_extract_entry_key` include operator, `/how` → "how to" mapping (memory_index.py)
  - Cycle 2: Wire `operator` param through `resolve()` signature (resolver.py)
  - Cycle 3: Wire `operator` from CLI into resolver call (cli.py)
  - Cycle 4: `_resolve_section` extend to H3+ headings (resolver.py)
  - Cycle 5: Validator consistency — `check_orphan_entries`, `check_collisions` with new keys
  - Tests: test_validation_memory_index.py, test_when_resolver.py, test_when_cli.py
  - Acceptance: `just precommit` passes after migration; `/when` and `/how` produce different results

- [ ] **Create bin wrapper** — Phase 5 deliverable | haiku
  - `agent-core/bin/when-resolve.py` — thin wrapper calling `claudeutils when` CLI

- [ ] **Author skill wrappers** — Phase 8 agentic prose | opus | restart
  - `agent-core/skills/when/SKILL.md` — frontmatter in design.md, body needs authoring
  - `agent-core/skills/how/SKILL.md` — frontmatter in design.md, body needs authoring
  - Run `just sync-to-parent` after creating skills

- [ ] **Migrate memory-index.md to /when format** — Depends on: code fixes | sonnet
  - 152 entries: `Key — description` → `/when key` or `/how key`
  - Heading renames in agents/decisions/*.md: add When/How to prefix
  - Update preamble with consumption header from design spec
  - Migration script: `tmp/migrate-index.py` (has 152-entry operator mapping)
  - Atomic: entries + headings + header in single commit
  - Gate: `just precommit` must pass

- [ ] **Update remember skill** — Depends on: migration | haiku
  - Generate `/when` or `/how` entries with trigger naming guidelines
  - Design spec: §Remember Skill Update

- [ ] **Protocolize RED pass recovery** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
  - Scope: Classification taxonomy, blast radius procedure, defect impact evaluation
  - Reports: `plans/when-recall/reports/tdd-process-review.md`, `plans/orchestrate-evolution/reports/red-pass-blast-radius.md`

- [ ] **Update plan-tdd skill** — Document background phase review agent pattern | sonnet

- [ ] **Execute worktree-update runbook** — `/orchestrate worktree-update` | haiku | restart
  - Plan: plans/worktree-update
  - 40 TDD cycles, 7 phases

- [ ] **Agentic process review and prose RCA** | opus
  - Scope: worktree-skill execution process

- [ ] **Workflow fixes** — Implement process improvements from RCA | sonnet
  - Depends on: RCA completion

- [ ] **Consolidate learnings** — learnings.md at 319+ lines | sonnet
  - Blocked on: memory redesign

- [ ] **Remove duplicate memory index entries on precommit** | sonnet
  - Blocked on: memory redesign

- [ ] **Update design skill** — TDD non-code steps + Phase C density checkpoint | sonnet

- [ ] **Handoff skill memory consolidation worktree awareness** | sonnet

- [ ] **Commit skill optimizations** | sonnet
  - Blocked on: worktree-update delivery

## Blockers / Gotchas

**Precommit broken:** Phase 6 validator enforces /when format but Phase 9 migration not yet executed. 152+ entries fail `check_trigger_format`. Precommit will stay broken until migration completes.

**Operator→prefix mapping:** `/when` → "When", `/how` → "How to". Both `_extract_entry_key` and `_build_heading` must use same mapping. Test both operators in every TDD cycle.

**Learnings.md over soft limit:** 319+ lines, consolidation blocked on memory redesign.

**Common context signal competition:** Structural issue in prepare-runbook.py. See `tmp/rca-common-context.md`.

## Reference Files

- `plans/when-recall/reports/deliverable-review.md` — **Primary input for next session**
- `plans/when-recall/design.md` — Vetted design (ground truth)
- `plans/when-recall/reports/migration-findings.md` — Migration design conflict analysis (Approach A superseded by Approach B per deliverable review)
- `tmp/migrate-index.py` — Migration script with 152-entry operator mapping
