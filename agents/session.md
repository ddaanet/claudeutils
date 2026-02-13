# Session Handoff: 2026-02-13

**Status:** Memory index migration attempted, blocked on design conflict — validator uses fuzzy matching but index needs exact keys. Findings documented, code changes required before migration.

## Completed This Session

**Migration investigation:**
- Wrote 152-entry heading mapping (tmp/migrate-index.py) covering all decision files
- Ran migration: renamed 152 headings with When/How to prefix, rebuilt memory-index.md
- Precommit failed: ALL 152 entries reported as orphan — fuzzy score of trigger vs "When X" heading below threshold 50.0
- User directive: exact keys in index, fuzzy matching only for resolver recovery
- Investigated three fix approaches (A: no prefix headings, B: operator-prefixed keys, C: strip prefix from heading keys)
- Wrote findings: `plans/when-recall/reports/migration-findings.md`
- Reverted all file changes, tree clean

## Pending Tasks

- [ ] **Fix validator for exact key matching** — Remove fuzzy matching from validator, update _build_heading | sonnet
  - Design conflict: entry key "writing mock tests" ≠ heading key "when writing mock tests"
  - Approach A (recommended): don't prefix headings, change `_build_heading` to not add When/How to
  - Code: resolver.py, memory_index.py, memory_index_checks.py (~40 lines)
  - Tests: test_when_resolver.py (~20 heading refs), test_validation_memory_index.py (fuzzy/collision tests)
  - Findings: `plans/when-recall/reports/migration-findings.md`

- [ ] **Migrate memory-index.md to /when format** — Depends on: validator fix | sonnet
  - 152 entries: change from `Key — description` to `/when key` or `/how key`
  - No heading renames needed if Approach A adopted (headings stay as-is)
  - Update preamble with invocation instructions
  - Migration script: `tmp/migrate-index.py` (has full 152-entry operator mapping)
  - Blocker: precommit fails until migration complete (Phase 6 validator enforces new format)

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

**Validator exact-key design conflict:** D-6 says headings get When/How to prefix, but `_extract_entry_key` strips the operator, creating key mismatch. Three approaches documented in `plans/when-recall/reports/migration-findings.md`. User chose exact keys over fuzzy bridge.

**Learnings.md over soft limit:** 319+ lines, consolidation blocked on memory redesign.

**Common context signal competition:** Structural issue in prepare-runbook.py. See `tmp/rca-common-context.md`.

## Reference Files

- `plans/when-recall/design.md` — Vetted design
- `plans/when-recall/reports/migration-findings.md` — Migration design conflict analysis
- `plans/when-recall/reports/tdd-process-review.md` — TDD process review
- `plans/when-recall/reports/checkpoint-*-vet.md` — Phase checkpoint reports (8 total)
- `tmp/migrate-index.py` — Migration script with 152-entry operator mapping
