# Session: Plugin Migration — Branch Separation + Runbook Assembly Blocker

**Status:** Infrastructure tasks separated to own branch. Plugin migration blocked on prepare-runbook.py phase numbering validation.

## Completed This Session

**Branch separation:**
- Created `infrastructure-improvements` branch with 4 tasks from plugin migration vetting RCAs
- Tasks: commit Gate B coverage, reflect skill output, vet-fix-agent delegation, Task tool parallelization
- Branch ready for independent merge to main
- Plugin migration continues on `wt/plugin-migration` branch

**Runbook assembly blocker discovered:**
- All 7 phase files generated and vetted (Phase 0-6, 44 issues fixed across all phases)
- `prepare-runbook.py` expects 1-based phase numbering (phases 1-N)
- Plugin migration uses 0-based numbering (Phase 0-6)
- Script validation fails: "Expected phases 1-7, got phases 0-6"
- Design intentionally uses Phase 0 for directory rename (foundational step before Phase 1)

## Pending Tasks

- [ ] **Resolve prepare-runbook.py phase numbering** — Fix validation to support 0-based or 1-based phase numbering | sonnet
  - Current: Script enforces 1-based (phases 1-N), fails on plugin migration's 0-based (Phase 0-6)
  - Options: (1) Renumber phases 0-6 → 1-7, (2) Fix script to accept 0-based, (3) Make validation flexible
  - Decision needed: User requested merge of branches but runbook assembly blocked
  - File: `agent-core/bin/prepare-runbook.py` lines 403-414
- [ ] **Merge branches after runbook assembly** — Merge infrastructure-improvements and handle submodule sync | sonnet
  - User request: "merge branches agent-core/main and claudeutils/tools-rewrite"
  - Needs clarification: agent-core is submodule, not separate branch
  - Sequence: Fix phase numbering → assemble runbook → merge infrastructure-improvements → sync submodules

## Blockers / Gotchas

**Prepare-runbook.py phase numbering mismatch:**
- Script validation at lines 410-414 expects `range(1, N+1)` (1-based)
- Plugin migration design uses Phase 0 (directory rename) as foundational step
- All phase files exist: `runbook-phase-0.md` through `runbook-phase-6.md`
- Error message: "Phase numbering gaps detected. Missing phases: []" (misleading — no gaps, just wrong base)
- Cannot proceed with runbook assembly until validation fixed

**Merge request needs clarification:**
- User said "merge branches agent-core/main and claudeutils/tools-rewrite"
- agent-core is a git submodule, not a branch in this repo
- Possible interpretations: (1) merge infrastructure-improvements to main, (2) sync submodule commits from upstream
- Need to understand: what branches to merge, what the merge accomplishes

## Reference Files

- **agent-core/bin/prepare-runbook.py** — Runbook assembly script (lines 403-414: phase numbering validation)
- **plans/plugin-migration/runbook-phase-{0-6}.md** — All phase files (vetted, ready for assembly)
- **plans/plugin-migration/reports/phase-{0-6}-review.md** — Vet reviews (44 issues fixed)
- **plans/plugin-migration/design.md** — Design with Phase 0 as foundational step (D-1 naming hierarchy)
