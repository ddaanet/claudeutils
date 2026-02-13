# Session Handoff: 2026-02-13

**Status:** Phases 1-8 complete. Skill wrappers authored and verified. Precommit blocked on memory-index.md migration (Phase 9).

## Completed This Session

**Skill wrappers (Phase 8):**
- `agent-core/skills/when/SKILL.md` — behavioral knowledge recall, third-person triggers, three resolution modes
- `agent-core/skills/how/SKILL.md` — procedural knowledge recall, distinct triggers from /when
- `just sync-to-parent` — symlinks in `.claude/skills/`
- Skill-reviewer: both pass (no critical/major issues)
- Post-restart verification: skills discoverable, resolver invokes correctly (file mode returns content, trigger mode returns expected "no match" pre-migration)

## Pending Tasks

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

**Autofix functions need updating:** `autofix_index` removes all entries instead of just structural ones. Root cause: autofix logic doesn't account for operator-prefixed keys. Need to strip operator prefix when comparing against structural set, but preserve full key for header matching.

**Precommit broken:** Phase 6 validator enforces /when format but Phase 9 migration not yet executed. 152+ entries fail `check_trigger_format`. Precommit will stay broken until migration completes. Currently 20/24 validation tests pass (4 autofix tests fail).

**Operator→prefix mapping:** `/when` → "When", `/how` → "How to". Both `_extract_entry_key` and `_build_heading` must use same mapping. Test both operators in every TDD cycle.

**Learnings.md over soft limit:** 319+ lines, consolidation blocked on memory redesign.

**Common context signal competition:** Structural issue in prepare-runbook.py. See `tmp/rca-common-context.md`.

## Reference Files

- `plans/when-recall/reports/deliverable-review.md` — Findings that drove TDD cycles
- `plans/when-recall/design.md` — Vetted design (ground truth)
- `src/claudeutils/validation/memory_index_helpers.py` — Contains `_strip_operator_prefix` helper and autofix logic needing update
- `tests/test_validation_memory_index.py` — 20/24 passing, 4 autofix tests failing
