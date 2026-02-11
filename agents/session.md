# Session Handoff: 2026-02-11

**Status:** Phase 4C complete. T5 test implementation blocked by production bug in apply_theirs_resolution.

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

**Phase 4B (Minor Tests):** Refactored test organization, consolidated boilerplate (T1, T8, T10, T11, T12)
- 4038815: Replaced subprocess.run → run_git() helper in 2 test files
- 4038815: Extracted _get_mode5_section() helper to eliminate duplication
- 4038815: Consolidated 10 YAML schema tests → 3 grouped tests
- 4038815: Deleted redundant test_resolve_source_conflicts_returns_list_of_resolved_files
- Step 4.4 (T5) skipped — requires reading merge_phases.py before test design (added as pending task)
- Net: -137 lines (231 deleted, 94 added)

**Phase 4C (Minor Docs):** Updated Usage Notes and slug derivation clarity (A3, A4)
- 108a498: Fixed Usage Notes to reflect Mode C auto-cleanup behavior — Mode A/B require separate cleanup, Mode C includes it automatically
- 108a498: Clarified slug derivation special character handling — replaced vague "special characters" with explicit `[a-z0-9]` pattern
- Vet review: No issues, documentation accurate and clear

### Production Bug Discovered in T5 Implementation

Attempted to implement T5 e2e test for precommit fallback flow. Test correctly identified bug in production code:

**Bug location**: `src/claudeutils/worktree/merge_phases.py:244`
**Issue**: `apply_theirs_resolution()` called after merge commit exists, MERGE_HEAD consumed, `git checkout --theirs` cannot work

**Expected flow**: Commit with ours → precommit fails → reset HEAD~1 → apply theirs (requires MERGE_HEAD) → commit → retry precommit
**Actual flow**: Commit with ours → precommit fails → apply theirs WITHOUT reset (MERGE_HEAD gone) → `git checkout --theirs` fails silently → retry precommit with same ours content → fails

**Evidence**: Lines 232-256 show reset only on unparseable output (line 241) or after apply_theirs fails (line 255), NOT before calling apply_theirs (line 244)

**Report**: `plans/worktree-skill-fixes/reports/t5-production-bug.md`

### Added Investigation Prerequisite Rule to Planning Skills

RCA on Step 4.4 failure: executor in throughput mode treated creation step as mechanical recipe, attempted test 3× without reading production code.

Fix: Step classification rule added to both planning skills:
- `agent-core/skills/plan-tdd/SKILL.md` — Phase 3.1-3.6 step 4 (before dependency assignment)
- `agent-core/skills/plan-adhoc/SKILL.md` — Point 1 (before medium task criteria)

Rule: **Transformation** steps (delete/move/rename) = self-contained recipe. **Creation** steps (new test/integration) = MUST include `**Prerequisite:** Read [file:lines] — understand [behavior]`.

## Pending Tasks

- [ ] **Fix apply_theirs_resolution bug** — Add reset HEAD~1 before calling apply_theirs | opus
  - Bug: `merge_phases.py:244` calls apply_theirs after commit (MERGE_HEAD gone, checkout --theirs fails)
  - Fix: Insert `run_git(["reset", "HEAD~1"], check=False)` between line 243 and 244
  - After fix: complete T5 test implementation (test currently blocked by this bug)
  - Report: `plans/worktree-skill-fixes/reports/t5-production-bug.md`

- [ ] **Review investigation prerequisite rule** — `Task(subagent_type="plugin-dev:skill-reviewer")` | sonnet
  - Prompt: Review the "step type classification" additions to two planning skills. Read `agent-core/skills/plan-tdd/SKILL.md:530-546` and `agent-core/skills/plan-adhoc/SKILL.md:377-385`. Context: An executor attempted to write an e2e test (Step 4.4 in `plans/worktree-skill-fixes/runbook-outline.md:238-248`) three times without reading the production code it was testing (`src/claudeutils/worktree/merge_phases.py:220-260`). Each attempt failed because the executor was in throughput mode — 5 prior mechanical steps succeeded as recipes, so the 6th (a creation step requiring system understanding) was treated the same way. The new rule classifies steps as transformation (recipe sufficient) vs creation (investigation prerequisite required), so planners encode the investigation the executor would skip. Review for: triggering effectiveness (will planners notice this during step generation?), clarity of transformation/creation distinction, placement relative to surrounding guidance, interaction with existing prerequisite/dependency mechanisms in both skills.

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
- 782/784 tests passing (1 pre-existing failure, 1 xfail)

**T5 test blocked by production bug:**
- Cannot implement e2e test for precommit fallback until apply_theirs_resolution bug is fixed
- Bug discovered during test implementation — test correctly identified the issue
- Fix required before test can pass

## Reference Files

- `plans/worktree-skill-fixes/runbook-outline.md` — Runbook outline (25 steps, 7 phases)
- `plans/worktree-skill-fixes/reports/t5-production-bug.md` — Production bug blocking T5 test
- `plans/worktree-skill-fixes/reports/phase-4c-vet.md` — Phase 4C vet review (no issues)
- `plans/worktree-skill-fixes/reports/opus-outline-review.md` — Opus review (12 issues, all resolved)
- `plans/worktree-skill/reports/deliverable-review.md` — Review findings (27 items)
- `agents/decisions/deliverable-review.md` — Review methodology
