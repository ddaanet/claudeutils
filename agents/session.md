# Session Handoff: 2026-02-04

**Status:** Status skill and jobs.md workflow updated. Unified plans listing, nested pending task format, precommit validation.

## Completed This Session

**Status display format changes (execute-rule.md):**
- Pending list: nested format with plan directory, status, notes
- Jobs section → "Unscheduled Plans" (only plans without associated pending tasks)
- Removed directory-based status detection fallback (jobs.md is authoritative)

**jobs.md unified format:**
- Single "Plans" table with all plans (including one-off documents)
- Removed separate "One-off documents" section
- Added Notes column for context
- Complete (Archived) section unchanged

**New validation script (agent-core/bin/validate-jobs.py):**
- Cross-checks jobs.md Plans table against plans/ directory
- Plans in directory must exist in jobs.md
- Non-complete plans in jobs.md must exist in directory
- Special handling for plans/claude/ subdirectory
- Added to precommit recipe

**Files modified:**
- agent-core/fragments/execute-rule.md (STATUS format, removed fallback)
- agents/jobs.md (unified format)
- agent-core/bin/validate-jobs.py (new)
- justfile (added validate-jobs.py to precommit)

## Pending Tasks

- [ ] **Plan statusline wiring** — `/plan-tdd plans/statusline-wiring/design.md`
  - Plan: statusline-wiring | Status: designed
- [ ] **Fix prepare-runbook.py artifact hygiene** — Clean steps/ directory before writing
- [ ] **Update plan-tdd/plan-adhoc skills** — Auto-run prepare-runbook.py with sandbox bypass, handoff, commit
- [ ] **Continuation passing design-review** — validate outline against requirements | opus
  - Plan: continuation-passing | Status: requirements
- [ ] **Validator consolidation** — move validators to claudeutils package with tests
  - Plan: validator-consolidation | Status: requirements
- [ ] **Handoff validation design** — complete design, requires continuation-passing | opus
  - Plan: handoff-validation | Status: requirements
- [ ] **Add execution metadata to step files** — Step files declare dependencies and execution mode
- [ ] **Orchestrator scope consolidation** — delegate checkpoint phases instead of manual invocation
- [ ] **Session-log capture research** — extract explore/websearch/context7 results from transcripts | opus
- [ ] **Run /remember** — Process learnings (learnings.md at 35 lines)

## Blockers / Gotchas

**jobs.md is now authoritative for plan status:**
- No directory-based status inference
- All plans must be listed in jobs.md Plans table
- validate-jobs.py enforces this in precommit

## Reference Files

- **agent-core/fragments/execute-rule.md** — Updated STATUS format documentation
- **agent-core/bin/validate-jobs.py** — New validation script
- **agents/jobs.md** — Unified plans table

## Next Steps

- Plan statusline wiring TDD runbook
- Execute statusline runbook with TDD discipline
- Run /remember to consolidate learnings.md

---
*Handoff by Sonnet. Status workflow updated: unified jobs.md, nested pending format, precommit validation.*
