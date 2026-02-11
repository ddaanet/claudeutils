# Session Handoff: 2026-02-11

**Status:** OOR fixes applied, plan-adhoc sufficiency check added. Ready for Tier 2 execution of outline.

## Completed This Session

### Applied 12 OOR Fixes to Runbook Outline

All issues from `plans/worktree-skill-fixes/reports/opus-outline-review.md` resolved:
- **OOR-1 (Critical):** Decision tree for three merge abort calls — pre-commit keeps `merge --abort`, post-commit uses `reset HEAD~1`
- **OOR-2/3/4 (Major):** git_utils.py extraction fully specified — canonical source (commands.py), run_git() moves to git_utils.py with retry, Step 1.3→1.4 dependency declared
- **OOR-5 (Major):** Fixture consolidation target decided — `tests/conftest_git.py` (conftest.py at 353 lines, would exceed 400-line limit)
- **OOR-6 (Major):** Step 4.3 updated to evaluate test_merge_helpers.py post-Phase-3 instead of assuming pre-consolidation state
- **OOR-8 (Major):** Phase 4 split into 4A (code, 3 steps), 4B (tests, 6 steps), 4C (docs, 2 steps) with intermediate checkpoints
- **OOR-9/10/11/12 (Minor):** Exact test names for Step 3.2, X2 scope bound, G2 moved to Phase 4A (corrected severity), e2e precommit approach specified

**Design decision:** Fix existing outline rather than regenerate. Rationale: regeneration validates checklist against its training data — real validation is next novel plan.

### Added Outline Sufficiency Check to plan-adhoc

Point 0.95 in `agent-core/skills/plan-adhoc/SKILL.md` — when outline steps already have targets, concrete actions, and verification, skip expansion (Points 1-3) and promote outline directly to runbook format for prepare-runbook.py. Prevents wasted planning cycle on detailed outlines.

### Executed worktree-skill-fixes Phases 0-2

**Phase 0 (Critical):** Fixed merge --abort after committed merge (C6), corrected paths in documentation (A1, D1)
- d51c3cb: Replaced `git merge --abort` with `git reset HEAD~1` after commit (3 locations in merge_phases.py)
- 2fb64bd: Fixed SKILL.md launch commands (`../<repo>-<slug>` → `wt/<slug>`)
- 2fb64bd: Fixed sandbox-exemptions.md directory convention (`worktrees/` → `wt/`)
- Vet review: No UNFIXABLE issues

**Phase 1 (Major Code):** Removed dead code, added validation, extracted git_utils module, implemented retry logic, updated .gitignore (C1, C2, C3, C7, G1)
- 8276e0c: Removed derive_slug() function and test
- 8276e0c: Added slug format validation with 11 test cases (pattern: `^[a-z0-9]([a-z0-9-]*[a-z0-9])?$`)
- 8276e0c: Extracted get_dirty_files() and check_clean_tree() to git_utils.py
- 8276e0c: Moved run_git() to git_utils.py with lock file retry (2 retries, 1s delay, detects "index.lock" and "Unable to create" errors)
- 8276e0c: Added /wt/ to .gitignore
- Resolved circular import by centralizing git operations in git_utils module
- Test note: Leading hyphen test case uses exit code 2 (Click option parsing layer) vs 1 (validation layer)
- Validated: Using `--` separator allows testing validation directly — `worktree new -- -foo` correctly rejects with exit code 1 (validation layer catches it)
- Defense-in-depth working: Both Click (exit 2) and validation regex (exit 1) reject leading hyphens
- Vet review: No UNFIXABLE issues, 795/797 tests passing

**Phase 2 (Major Docs):** Removed lock file removal instruction (A2)
- cab2340: Updated SKILL.md Mode C error handling — replaced "rm .git/index.lock if present" with "stop and report to user"
- Aligns with "Never agent-initiate lock file removal" behavioral rule

**Phase 3 (Major Tests):** Deleted redundant tests, consolidated fixtures, added missing coverage (T2-T7)
- 6c629a4: Deleted test_worktree_merge_verification.py (341 lines, tested git not production code)
- 6c629a4: Removed 5 absence tests from test_execute_rule_mode5_refactor.py
- 6c629a4: Added test_merge_debris_cleanup_before_merge (exercises clean_merge_debris before merge)
- 6c629a4: Consolidated 5 git init implementations → conftest_git.py
- 6c629a4: Consolidated 3 submodule setups → conftest_git.py
- Vet improved fixture API: init_repo() with optional with_commit parameter
- Net: -434 lines (646 deleted, 212 added)
- Vet review: No UNFIXABLE issues, critical vacuity issue fixed (test now exercises production code)

**Phase 4A (Minor Code):** Fixed import sources, subprocess consistency, dead code (C4, C5, G2)
- 860764e: Updated test_merge_phase_3_precommit imports to use merge_helpers (defining module)
- 860764e: Replaced raw subprocess calls with run_git() in conflicts.py (using -C for cwd)
- 860764e: Removed dead wt-path() function from justfile (wrong path convention)

**Progress:** 4/7 phases complete (Phase 0, 1, 2, 3, 4A). Remaining: Phase 4B (6 test steps), Phase 4C (2 doc steps).

### Consolidated 13 Learnings into Permanent Documentation

- 5e7b174: Consolidated into workflow-advanced.md (2 decisions), vet-requirement.md (2 rules), design skill (1 rule), memory-index.md (5 entries)
- Removed 2 duplicate memory-index entries, trimmed workflow-advanced.md 405→399 lines
- Net -79 lines from learnings.md

## Pending Tasks

- [>] **Execute worktree-skill-fixes** — Continue Phase 4B (minor test fixes) | sonnet
  - Progress: 4/7 phases complete (Phases 0, 1, 2, 3, 4A committed)
  - Next: Phase 4B — 6 minor test fixes (T1, T5, T8, T10, T11, T12)
  - Guide: `plans/worktree-skill-fixes/runbook-outline.md`
  - Note: Checkpoint commits per phase

- [ ] **Remove deprecated code** — Delete init_repo_with_commit() wrapper from conftest_git.py | sonnet
  - Added by vet for backward compat, can be cleaned up after confirming no external dependencies
  - File: tests/conftest_git.py:37-39

- [ ] **Agentic process review and prose RCA** — Analyze why deliveries are "expensive, incomplete, buggy, sloppy, overdone" | opus
  - Scope: worktree-skill execution process, not deliverables
  - Signals: plan specified opus but session showed haiku, vacuous tests passed vet, vet checked presence not correctness
  - Do NOT start until review+fixes complete (needs evidence)

- [ ] **Workflow fixes** — Implement process improvements from RCA | sonnet
  - Depends on: RCA completion

- [ ] **RCA: Vet-fix-agent UNFIXABLE labeling** — Analyze why agent labeled stylistic judgment as UNFIXABLE | sonnet

- [ ] **Consolidate learnings** — learnings.md at 404 lines (soft limit 80), 14 entries ≥7 days | sonnet
  - Run `/remember` to consolidate into permanent documentation

- [ ] **Remove duplicate memory index entries on precommit** — Autofix or fail on duplicate index entries | sonnet

## Blockers / Gotchas

**Two methodology documents exist:**
- `agents/decisions/review-methodology.md` — sonnet-generated, user distrusts, do NOT use
- `agents/decisions/deliverable-review.md` — ISO-grounded, use this one
- Cleanup: delete review-methodology.md after fixes confirm it's fully superseded

**Learnings.md over soft limit:**
- 325 lines after partial consolidation (13 entries consolidated this session) — further consolidation needed

**Review methodology gap:**
- "Excess" axis needs explicit density sub-criteria for test files

**Pre-existing test failure:**
- `test_merge_phase_2_diverged_commits` fails with "Error: failed to fetch from worktree submodule"
- Not related to fix phases, present before fixes started
- 774/791 tests passing (1 pre-existing failure, 1 xfail, 16 skipped without remark-cli)

## Reference Files

- `plans/worktree-skill-fixes/runbook-outline.md` — Runbook outline (25 steps, 7 phases/sub-phases)
- `plans/worktree-skill-fixes/reports/phase-0-vet.md` — Phase 0 vet review (no issues)
- `plans/worktree-skill-fixes/reports/phase-1-vet.md` — Phase 1 vet review (no issues)
- `plans/worktree-skill-fixes/reports/phase-3-vet.md` — Phase 3 vet review (critical vacuity issue fixed)
- `plans/worktree-skill-fixes/reports/opus-outline-review.md` — Opus review (12 issues, all resolved)
- `plans/worktree-skill/reports/deliverable-review.md` — Review findings (27 items)
- `agents/decisions/deliverable-review.md` — Review methodology
- `plans/worktree-skill/outline.md` — Ground truth design spec
