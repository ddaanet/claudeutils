# Worktree-Skill Deliverable Review Fixes — Runbook Outline

**Source:** `plans/worktree-skill/reports/deliverable-review.md`
**Requirements:** 27 findings (3 critical, 12 major, 12 minor) organized by severity and file

## Requirements Mapping

| Finding | Severity | Phase | Steps | Notes |
|---------|----------|-------|-------|-------|
| C6: merge --abort after committed merge | Critical | 0 | 0.1 | Fix error handling logic |
| A1: Wrong path in SKILL.md launch commands | Critical | 0 | 0.2 | Path correction: `../<repo>-<slug>` → `wt/<slug>` |
| D1: Wrong directory convention in sandbox-exemptions.md | Critical | 0 | 0.3 | Path correction: `worktrees/<slug>` → `wt/<slug>` |
| C1: Dead derive_slug() | Major | 1 | 1.1 | Remove unused function |
| C2: No slug format validation | Major | 1 | 1.2 | Add validation at CLI entry point |
| C3: Duplicate get_dirty_files/check_clean_tree | Major | 1 | 1.3 | Extract to git_utils.py module |
| C7: Missing lock file retry | Major | 1 | 1.4 | Implement retry wrapper for run_git() |
| G1: Missing /wt/ in .gitignore | Major | 1 | 1.5 | Add directory pattern to project .gitignore |
| G2: Dead wt-path() in justfile | Major | 1 | 1.6 | Remove obsolete helper function |
| A2: Lock file removal instruction | Major | 2 | 2.1 | Remove agent-initiated removal guidance |
| T2: Tests verify git concepts, not production code | Major | 3 | 3.1 | Delete test_worktree_merge_verification.py |
| T3: Mode 5 tests verify absence, not correctness | Major | 3 | 3.2 | Remove 6 absence tests, keep 2 behavioral |
| T4: Merge debris cleanup not tested | Major | 3 | 3.3 | Add e2e test exercising cleanup path |
| T6: Git init boilerplate defined 5 times | Major | 3 | 3.4 | Consolidate to conftest fixture |
| T7: Submodule setup defined 3 times | Major | 3 | 3.5 | Consolidate to conftest fixture |
| C4: __all__ re-exports from wrong module | Minor | 4 | 4.1 | Update test imports to source module |
| C5: Inconsistent subprocess.run vs run_git | Minor | 4 | 4.2 | Replace raw subprocess with helper |
| T1: test_merge_helpers.py is utility module | Minor | 4 | 4.3 | Rename to conftest_merge.py |
| T5: Source conflict flow partially tested | Minor | 4 | 4.4 | Add e2e test for full flow |
| T8: Raw subprocess boilerplate | Minor | 4 | 4.5 | Refactor to use run_git helper |
| T9: test_worktree_merge_verification.py 90% setup | Minor | — | — | Already addressed by T2 deletion |
| T10: Mode 5 section extraction copy-pasted | Minor | 4 | 4.6 | Extract helper, parametrize tests |
| T11: 10 micro-tests for YAML schema | Minor | 4 | 4.7 | Consolidate to 2-3 grouped tests |
| T12: Near-duplicate test adds no value | Minor | 4 | 4.8 | Delete redundant test |
| A3: Usage Notes contradict Mode C | Minor | 4 | 4.9 | Update prose to match implementation |
| A4: Vague "special characters" in slug derivation | Minor | 4 | 4.10 | Clarify regex pattern in prose |

## Phase Structure

### Phase 0: Critical Fixes (3 fixes)

**Complexity:** Medium
**Model:** Sonnet
**Deliverables:** Fixed code and documentation with functional correctness

**Step 0.1: Fix C6 — merge --abort after committed merge**
- Target: `src/claudeutils/worktree/merge_phases.py:238, 242, 255`
- Problem: `git merge --abort` called after merge commit already created — MERGE_HEAD consumed, abort silently fails
- Fix: Replace `merge --abort` with `git reset HEAD~1` when merge commit exists
- Detection: Check if merge commit was created (ORIG_HEAD vs HEAD)
- Error message: Update to mention `git reset HEAD~1` for manual recovery

**Step 0.2: Fix A1 — Wrong path in SKILL.md launch commands**
- Target: `agent-core/skills/worktree/SKILL.md:68, 95-96`
- Problem: Launch command says `cd ../<repo>-<slug>` — should be `cd wt/<slug>`
- Fix: Replace `../<repo>-<slug>` with `wt/<slug>` in Mode A step 7 and Mode B step 5

**Step 0.3: Fix D1 — Wrong directory convention in sandbox-exemptions.md**
- Target: `agent-core/fragments/sandbox-exemptions.md:40`
- Problem: Documentation says `worktrees/<slug>/` — should be `wt/<slug>/`
- Fix: Replace `worktrees/<slug>/` with `wt/<slug>/` in Worktree Operations section

**Rationale:** Functional correctness issues that break existing features or provide wrong guidance. C6 is a silent failure causing merge state corruption. A1 and D1 give wrong paths preventing successful worktree launch.

### Phase 1: Major Code Fixes (6 fixes)

**Complexity:** Medium
**Model:** Sonnet
**Deliverables:** Cleaned code, new module, spec compliance

**Step 1.1: Fix C1 — Remove dead derive_slug() function**
- Target: `src/claudeutils/worktree/cli.py:17-31`
- Problem: Function defined but never called by production code; slug is CLI argument, agent derives in SKILL.md
- Fix: Delete function and related tests (if they exist in test_worktree_cli.py)
- Verify: Grep for `derive_slug` usage across codebase

**Step 1.2: Fix C2 — Add slug format validation to cmd_new()**
- Target: `src/claudeutils/worktree/cli.py:60` (in `cmd_new`)
- Problem: No validation of slug input — accepts empty string, path traversal, special chars
- Fix: Add validation before worktree creation
  - Check: non-empty, no path traversal (`..`), safe chars only (alphanumeric + hyphen)
  - Pattern: `^[a-z0-9]([a-z0-9-]*[a-z0-9])?$` (start/end alphanumeric, hyphen in middle)
  - Error: Exit 1 with "Invalid slug" message to stderr
- Test: Add test cases for invalid inputs (empty, `..`, `/foo`, special chars)

**Step 1.3: Fix C3 — Extract git_utils.py module**
- Target: Create `src/claudeutils/worktree/git_utils.py`
- Problem: `get_dirty_files()` and `check_clean_tree()` duplicated in commands.py:38-72 and merge_helpers.py:82-116
- Fix:
  1. Create new module with both functions
  2. Update imports in commands.py (remove definitions, import from git_utils)
  3. Update imports in merge_helpers.py (remove definitions, import from git_utils)
  4. Update test imports if tests reference these functions
- Verify: Both modules import from git_utils, no duplication remains

**Step 1.4: Fix C7 — Implement lock file retry logic**
- Target: Wrap `run_git()` calls with retry logic
- Problem: Outline specifies "wait-1s-and-retry (2 retries max)" but not implemented
- Fix: Create retry decorator/wrapper
  - Detect lock file errors (exit code, stderr message "index.lock")
  - Retry up to 2 times with 1s delay
  - Apply to all `run_git()` invocations in merge_phases.py, commands.py, conflicts.py
- Implementation location: git_utils.py (alongside git helpers)
- Test: Mock lock file error, verify retry behavior

**Step 1.5: Fix G1 — Add /wt/ to .gitignore**
- Target: `.gitignore` (project root)
- Problem: Worktree directories appear as untracked without this entry
- Fix: Add `/wt/` line to .gitignore (slash prefix = root-level only)
- Verify: Test fixtures already add this (test_worktree_new.py:111, test_merge_helpers.py:61) — confirms requirement

**Step 1.6: Fix G2 — Remove dead wt-path() from justfile**
- Target: `justfile:252-260`
- Problem: Old helper function uses `../<parent>-wt/` convention (wrong), all recipes deleted but helper remains
- Fix: Delete the `wt-path()` function definition
- Verify: Grep justfile for `wt-path` — should have zero references after deletion

**Rationale:** Code quality, missing spec'd behavior, dead code removal. C3 creates module dependency used by C7. G1/G2 are quick config cleanups.

### Phase 2: Major Documentation Fix (1 fix)

**Complexity:** Low
**Model:** Sonnet
**Deliverables:** Corrected agent guidance

**Step 2.1: Fix A2 — Remove lock file removal instruction**
- Target: `agent-core/skills/worktree/SKILL.md:129` (Mode C step 5)
- Problem: Instructs agent to `rm .git/index.lock` — contradicts "Never agent-initiate lock file removal" learning and behavioral rule
- Current text: "Run `git status` to inspect tree, check for stale locks (`rm .git/index.lock` if present)"
- Fix: Replace with: "Run `git status` to inspect tree. If lock file errors occur, stop and report to user."
- Verify: No other lock file removal instructions in SKILL.md

**Rationale:** Contradicts established behavioral rule. Agents must stop on unexpected lock errors, not auto-remove locks (could corrupt active git operations).

### Phase 3: Major Test Fixes (5 fixes)

**Complexity:** High
**Model:** Sonnet
**Deliverables:** Cleaned test suite, shared fixtures, improved coverage

**Step 3.1: Fix T2 — Delete test_worktree_merge_verification.py**
- Target: `tests/test_worktree_merge_verification.py` (341 lines)
- Problem: Tests manually reproduce git merge ops, prove `merge-base --is-ancestor` works — don't exercise production code
- Fix: Delete entire file
- Coverage preservation: test_merge_phase_2.py already covers same scenarios through actual merge commands
- Verify: Run test suite, confirm no coverage loss

**Step 3.2: Fix T3 — Refactor test_execute_rule_mode5_refactor.py**
- Target: `tests/test_execute_rule_mode5_refactor.py:49-139` (6 of 8 tests)
- Problem: Tests verify old content was removed (absence tests) — no ongoing regression value
- Fix: Delete 6 tests: `test_*_no_slug_derivation_prose`, `test_*_no_single_task_flow_steps`, `test_*_no_parallel_group_flow_steps`, `test_*_no_focused_session_template`, `test_*_no_output_format_section`, `test_*_no_worktree_tasks_section_description`
- Keep: 2 behavioral tests that verify current content correctness
- Verify: Remaining tests still cover Mode 5 presence and structure

**Step 3.3: Fix T4 — Add test for merge debris cleanup**
- Target: Create new test in `tests/test_merge_phase_3_*.py` (or new file)
- Problem: `clean_merge_debris()` has no dedicated test coverage
- Behavior: After `git merge --abort`, untracked files materialized during merge are removed
- Test scenario:
  1. Create merge conflict where source branch adds new file
  2. Trigger merge conflict
  3. Call merge cleanup (or cmd_merge which triggers it)
  4. Assert: New file from source branch no longer exists as untracked
- Implementation: Use existing test fixtures, add assertions for debris cleanup

**Step 3.4: Fix T6 — Consolidate git init boilerplate**
- Target: 5 implementations across test files
- Problem: `_init_repo()` / `_init_git_repo()` defined in test_worktree_cli.py:12, test_worktree_rm.py:13, test_worktree_new.py:12, test_merge_helpers.py:20, conftest.py:284
- Fix:
  1. Choose canonical implementation (conftest.py fixture or create new shared fixture)
  2. Remove local implementations from 4 test files
  3. Update test imports to use shared fixture
- Result: Single source of truth for git repo initialization

**Step 3.5: Fix T7 — Consolidate submodule setup**
- Target: 3 implementations across test files
- Problem: test_worktree_new.py:33 (40 lines), test_merge_helpers.py:27 (38 lines), conftest.py:271 (70 lines)
- Fix:
  1. Choose canonical implementation (likely conftest.py `repo_with_submodule` fixture)
  2. Remove duplicate implementations from test_worktree_new.py and test_merge_helpers.py
  3. Update test imports to use shared fixture
- Verify: All tests using submodule setup still pass

**Rationale:** Test quality improvements — delete redundant/vacuous tests (T2, T3), add missing coverage (T4), reduce duplication (T6, T7). High complexity due to test refactoring requiring understanding of test intent and fixture dependencies.

### Phase 4: Minor Fixes (12 items)

**Complexity:** Low-Medium
**Model:** Sonnet

**Deliverables:** Fixed test modules, updated documentation

**Step 4.1: Fix C4 — Clean up __all__ re-exports**
- Target: `src/claudeutils/worktree/commands.py:23-35`
- Problem: `apply_theirs_resolution`, `capture_untracked_files`, `parse_precommit_failures` re-exported from commands.py but defined in merge_helpers.py
- Fix: Update test imports to import from merge_helpers.py (the defining module)
- Files to update: Tests that `import from claudeutils.worktree.commands`
- Verify: Tests still pass after import changes

**Step 4.2: Fix C5 — Use run_git helper consistently**
- Target: `src/claudeutils/worktree/conflicts.py:244-252`
- Problem: `resolve_source_conflicts()` uses raw `subprocess.run(["git", ...])` — inconsistent with codebase
- Fix: Replace with `run_git()` helper call
- Verify: Function behavior unchanged, just uses consistent helper

**Step 4.3: Fix T1 — Rename test_merge_helpers.py**
- Target: `tests/test_merge_helpers.py`
- Problem: File contains only utility functions (`run_git`, `init_repo`, `setup_repo_with_submodule`) — no test assertions
- Fix: Rename to `conftest_merge.py` or move helpers to main conftest.py
- Decision: If helpers are merge-specific, use conftest_merge.py; if general, merge into conftest.py
- Update imports in test files that use these helpers

**Step 4.4: Fix T5 — Add e2e test for source conflict full flow**
- Target: Create test in `tests/test_merge_phase_3_precommit.py`
- Problem: Partial coverage — apply_theirs_resolution tested in isolation, but full flow (take-ours → precommit fails → fallback to theirs → re-check) not tested e2e
- Test scenario:
  1. Create conflicting change in source and main
  2. Trigger merge with conflict
  3. Apply take-ours resolution
  4. Simulate precommit failure
  5. Verify fallback to theirs
  6. Verify precommit re-runs and passes
- Implementation: Extend existing test_merge_phase_3_precommit.py

**Step 4.5: Fix T8 — Refactor subprocess boilerplate**
- Target: `tests/test_worktree_source_conflicts.py`, `tests/test_worktree_new.py` (other files already deleted in T2)
- Problem: Raw `subprocess.run(["git", ...], cwd=..., check=True, capture_output=True)` repeated
- Fix: Replace with `run_git()` helper from test_merge_helpers.py (or conftest after T1 fix)
- Verify: Tests still pass with helper

**Step 4.6: Fix T10 — Extract section extraction helper**
- Target: `tests/test_execute_rule_mode5_refactor.py`
- Problem: 8 tests copy-paste same 7-line section extraction pattern
- Fix: Create `_get_mode5_section()` helper function, use parametrize for multiple tests
- Result: Reduce 139 lines to ~30-40 lines
- Verify: All remaining tests still pass

**Step 4.7: Fix T11 — Consolidate YAML schema tests**
- Target: `tests/test_worktree_skill_frontmatter.py`
- Problem: 10 micro-tests for YAML schema — excessive granularity
- Fix: Consolidate to 2-3 grouped tests:
  1. Test basic schema (description, continuation fields)
  2. Test nested structure (default_exit, cooperative)
  3. Test validation (missing required fields)
- Verify: Same coverage, fewer test functions

**Step 4.8: Fix T12 — Delete redundant test**
- Target: `tests/test_worktree_source_conflicts.py:201-222`
- Problem: `test_resolve_source_conflicts_returns_list_of_resolved_files` checks `isinstance`, `len > 0`, `"app.py" in resolved` — all implied by preceding test
- Fix: Delete the test function
- Verify: Preceding test already covers same assertions

**Step 4.9: Fix A3 — Update Usage Notes to match Mode C**
- Target: `agent-core/skills/worktree/SKILL.md:140-141`
- Problem: "Merge and cleanup are separate user actions" but Mode C step 3 explicitly invokes cleanup command
- Current text: "The worktree merge ceremony does not automatically delete branches or cleanup"
- Fix: Update to: "Mode A and Mode B require separate cleanup. Mode C includes cleanup automatically after successful merge."
- Verify: Prose matches Mode C implementation

**Step 4.10: Fix A4 — Clarify special characters definition**
- Target: `agent-core/skills/worktree/SKILL.md:33`
- Problem: "remove special characters" is vague — which characters?
- Current text: (vague prose about special characters)
- Fix: Replace with: "Remove any characters not matching `[a-z0-9]` (replace with hyphen)"
- Verify: Matches actual implementation pattern

**Rationale:** Minor issues that improve code quality and consistency but don't affect functional behavior.

## Key Decisions

**Phase ordering:** Critical → Major Code → Major Docs → Major Tests → Minor
- Critical fixes first (broken functionality)
- Major code fixes before tests (tests may depend on code changes)
- Minor fixes last (low risk, can be batched)

**Test consolidation strategy:**
- Extract shared fixtures to conftest.py (T6, T7)
- Delete redundant tests that don't exercise production code (T2, T12)
- Refactor absence tests to behavior tests (T3)
- Add missing coverage for untested code paths (T4, T5, T19)

**Module extraction (C3):**
- Create src/claudeutils/worktree/git_utils.py
- Move get_dirty_files() and check_clean_tree() from both files
- Update imports in commands.py and merge_helpers.py
- Update tests to import from new module

**Lock file retry (C7):**
- Wrap run_git() in retry logic (2 retries, 1s delay)
- Apply to all git operations that may encounter .git/index.lock
- Matches outline specification: "wait-1s-and-retry (2 retries max)"

## Consolidation Gate Assessment

**Trivial phases:** None. All phases have substantial work (3-6 steps, medium complexity).

**Phase merge candidates:** None. Phases are logically distinct (critical/major/minor) and merging would exceed 10 steps.

**Proceed with current structure.**

## Expansion Complexity Check

**Total steps:** 26 (including skip for T9)
**Pattern-based steps:** None (each fix is unique)
**Algorithmic steps:** Most steps are straightforward edits/deletions
**Token cost:** Moderate (each step ~200 lines of context + implementation guidance)

**Assessment:** Expansion feasible. Proceed with phase-by-phase generation.

**Fast-path opportunities:** None identified. Each fix requires specific guidance.

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Consolidation candidates:**
- No trivial phases identified — all phases have substantial work (3-6+ steps)
- Phase 4 (10 steps) could be split into Phase 4A (code) and Phase 4B (tests/docs) if individual steps prove complex during expansion, but initial assessment suggests batching is appropriate

**Step expansion priorities:**

**Step 0.1 (merge --abort fix):**
- Include detection logic: compare `git log -1 --format=%H` against ORIG_HEAD to determine if commit exists
- Decision tree: if commit exists → `git reset HEAD~1`, else → `git merge --abort`
- Error message updates: mention both recovery paths to user

**Step 1.2 (slug validation):**
- Decide validation location: CLI layer (fail fast) vs `cmd_new()` function (defense-in-depth)
- Recommend CLI layer for this fix — function-level can be future enhancement
- Test cases must cover: empty string, `..`, `/foo`, special chars, valid edge cases (single char, max length)

**Step 1.3 (git_utils extraction):**
- Verify circular dependency resolution after extraction
- Document import chain: commands.py → git_utils.py, merge_helpers.py → git_utils.py (no cycle)
- Consider future: if git_utils grows beyond 2 functions, may need further splitting

**Step 1.4 (lock retry logic):**
- Implementation choice: decorator vs wrapper function
- Recommend wrapper for explicit control flow and error handling clarity
- Detection pattern: check stderr for "index.lock" string, not just exit code
- Test strategy: mock subprocess to inject lock errors, verify retry count and delays

**Phase 3 fixture consolidation (Steps 3.4, 3.5):**
- Monitor conftest.py size — consolidating 8 implementations may create 500+ line file
- Alternative structure: `conftest_fixtures.py` for git-specific fixtures, keep conftest.py for pytest config
- Recommend: consolidate to conftest.py first, extract to conftest_fixtures.py if size exceeds 400 lines

**Step 4.6 (section extraction parametrize):**
- Parametrize IDs must include section name for failure debuggability
- Example: `@pytest.mark.parametrize("section", ["MODE 5", "other"], ids=["mode5", "other"])`
- Balance: reduce code duplication without sacrificing failure localization

**Step 4.7 (YAML test consolidation):**
- Target: 2-3 grouped tests (not 1 monolithic test)
- Group 1: Basic schema (description, continuation)
- Group 2: Nested structure (default_exit, cooperative)
- Group 3: Error cases (missing fields, invalid values)
- Maintain assertion granularity — consolidated ≠ less thorough

**Checkpoint guidance:**

**After Phase 0:**
- Run precommit validation (critical fixes may affect linting/complexity)
- Run full test suite (merge --abort fix affects core merge logic)
- Vet review: focus on error handling correctness and path accuracy

**After Phase 1:**
- Run precommit validation (new module, validation logic)
- Run full test suite (git_utils refactor and lock retry affect many operations)
- Vet review: focus on module boundaries and retry robustness

**After Phase 2:**
- No precommit needed (documentation only)
- Vet review: verify prose no longer contradicts behavioral rule

**After Phase 3:**
- Run full test suite (test infrastructure changes)
- Verify test count reduction: expect ~400 lines removed, 1-2 new tests added
- Vet review: check for test vacuity, fixture clarity, coverage preservation

**After Phase 4:**
- Run full test suite (final validation)
- Run precommit validation (if any code changes in C4/C5)
- Vet review: comprehensive check across all changes

**References to include:**

**Deliverable review report:**
- `plans/worktree-skill/reports/deliverable-review.md` — source of all 27 findings
- Reference specific finding codes (C6, A1, T2, etc.) in commit messages

**Original outline:**
- `plans/worktree-skill/outline.md` §Error Handling — lock file retry specification
- §Testing — merge debris cleanup behavior specification

**Behavioral rules:**
- learnings.md: "Never agent-initiate lock file removal" — context for A2 fix
- learnings.md: "E2E over mocked subprocess" — context for test strategy

**Test quality axes:**
- `agents/decisions/deliverable-review.md` — test evaluation criteria (vacuity, expressiveness, pertinence)
- Apply during Phase 3-4 vet reviews to prevent reintroducing test slop
