# Opus Outline Review

**Date:** 2026-02-11
**Artifact:** plans/worktree-skill-fixes/runbook-outline.md
**Reviewer model:** Opus

## Summary

The outline is well-structured with clear finding-to-step mapping and appropriate phase ordering. However, several steps have ambiguity or missing context that would cause an executing LLM agent to produce wrong output, and there are two requirements coverage gaps and three ordering dependencies that need explicit declaration.

## Issues Found

### OOR-1: Step 0.1 merge abort fix lacks branch state awareness
- **Axis:** Missing context that causes hallucination
- **Severity:** Critical
- **Location:** Step 0.1
- **Problem:** The fix says "Replace `merge --abort` with `git reset HEAD~1` when merge commit exists" and uses ORIG_HEAD vs HEAD comparison. But this ignores the case where the merge commit is not the most recent commit -- if additional commits happened between the merge and the precommit failure check (unlikely in current code but the fix should be robust). More critically, the step references lines 238, 242, 255 but doesn't specify the control flow: there are THREE separate `merge --abort` calls in `merge_phase_3_commit_and_precommit()`. An executing agent needs to know which ones to change and which to leave. If the merge hasn't been committed yet (earlier failure paths), `merge --abort` IS correct. The step must distinguish: abort calls BEFORE line 217 (commit) keep `merge --abort`; abort calls AFTER line 217 use `reset HEAD~1`.
- **Recommendation:** Add explicit decision tree: "Lines before the `git commit` call at ~217: keep `merge --abort`. Lines after the commit call (238, 242, 255): replace with `git reset HEAD~1`. The detection `git rev-parse ORIG_HEAD` succeeds only after a commit, so use that as the discriminator in code."

### OOR-2: Step 1.3 git_utils extraction has no import ordering guidance
- **Axis:** Ambiguity that causes wrong action
- **Severity:** Major
- **Location:** Step 1.3
- **Problem:** The step says "Create new module with both functions" and "Update imports in commands.py" and "Update imports in merge_helpers.py." But both source files have slightly different implementations (the review notes merge_helpers.py has a comment about circular import avoidance). The agent must choose WHICH implementation to keep. Additionally, there's no guidance on whether `run_git()` should also move to git_utils.py (it's used by both files and is thematically a git utility). Without this, the agent may make inconsistent choices about what belongs in the new module.
- **Recommendation:** Specify: "Use the commands.py implementation as canonical (it lacks the workaround comment). Move `get_dirty_files()` and `check_clean_tree()` only -- `run_git()` stays in its current location(s) for this step. Step 1.4 will add retry logic to git_utils.py alongside these functions."

### OOR-3: Step 1.4 lock retry has conflicting scope guidance
- **Axis:** Scope creep opportunities
- **Severity:** Major
- **Location:** Step 1.4
- **Problem:** The step says "Apply to all `run_git()` invocations in merge_phases.py, commands.py, conflicts.py" but the Expansion Guidance section says "wrapper for explicit control flow." If the agent creates a wrapper function, it needs to know whether to (a) modify `run_git()` itself to include retry, (b) create a separate `run_git_with_retry()` that wraps `run_git()`, or (c) wrap each call site. Option (a) changes behavior globally; option (b) requires updating all call sites; option (c) is most surgical but tedious. The outline doesn't resolve this, leaving the agent to choose -- and different choices have different test implications.
- **Recommendation:** Resolve the implementation choice in the outline: "Add retry logic inside `run_git()` in git_utils.py (option a), detecting lock file errors in stderr and retrying. This makes retry automatic for all callers. Place `run_git()` in git_utils.py alongside the other extracted functions."

### OOR-4: Step 1.3 and Step 1.4 have an undeclared ordering dependency
- **Axis:** Ordering risks
- **Severity:** Major
- **Location:** Steps 1.3 and 1.4
- **Problem:** Step 1.4 says "Implementation location: git_utils.py (alongside git helpers)" -- but git_utils.py only exists if Step 1.3 has completed. The outline's Rationale section mentions "C3 creates module dependency used by C7" but this dependency isn't declared in the step definitions themselves. An agent or orchestrator treating Phase 1 steps as parallelizable would fail.
- **Recommendation:** Add explicit dependency declaration to Step 1.4: "Depends on: Step 1.3 (git_utils.py must exist)." Better: if OOR-3 is adopted (moving `run_git()` into git_utils.py), declare that Step 1.4 ALSO depends on knowing where `run_git()` lives after 1.3.

### OOR-5: Step 3.4/3.5 fixture consolidation target is ambiguous
- **Axis:** Ambiguity that causes wrong action
- **Severity:** Major
- **Location:** Steps 3.4, 3.5
- **Problem:** Step 3.4 says "Choose canonical implementation (conftest.py fixture or create new shared fixture)" and Step 3.5 similarly says "Choose canonical implementation (likely conftest.py `repo_with_submodule` fixture)." This defers a design decision to the executing agent. The Expansion Guidance section adds more options (conftest_fixtures.py if size exceeds 400 lines). An executing agent will spend tokens reasoning about this choice instead of executing. Worse, if 3.4 picks conftest.py and 3.5 later finds it too large, the agent may need to undo 3.4's work.
- **Recommendation:** Make the decision now. Read conftest.py's current size. If it's under 300 lines, consolidate into conftest.py for both steps. If over, create conftest_git.py from the start. Specify the exact target file in both steps.

### OOR-6: Step 4.3 T1 rename has undeclared dependency on Steps 3.4/3.5
- **Axis:** Ordering risks
- **Severity:** Major
- **Location:** Step 4.3
- **Problem:** Step 4.3 renames test_merge_helpers.py to conftest_merge.py (or merges into conftest.py). But Steps 3.4 and 3.5 already consolidate fixtures FROM test_merge_helpers.py into conftest.py. After 3.4/3.5, test_merge_helpers.py may have fewer functions (or be empty). The rename decision depends on what's left after Phase 3 consolidation. If most helpers moved to conftest.py in Phase 3, the rename may become a deletion instead.
- **Recommendation:** Re-sequence: either move 4.3 into Phase 3 (before or after 3.4/3.5, with explicit awareness of what remains), or change 4.3's description to "evaluate what remains in test_merge_helpers.py after Phase 3 consolidation and either delete the file or rename what's left."

### OOR-7: Step 4.5 T8 references deleted file
- **Axis:** Missing context that causes hallucination
- **Severity:** Minor
- **Location:** Step 4.5
- **Problem:** The step says "(other files already deleted in T2)" acknowledging test_worktree_merge_verification.py is gone. But it lists test_worktree_source_conflicts.py and test_worktree_new.py as targets. After Step 3.1 deletes test_worktree_merge_verification.py, some imports or helpers that test_worktree_source_conflicts.py uses from test_merge_helpers.py may have changed location (due to Steps 3.4/3.5/4.3). The agent needs to know the post-Phase-3 state of imports, not the current state.
- **Recommendation:** Add: "After Phase 3 consolidation, the `run_git()` helper will be in conftest.py (or conftest_merge.py). Update subprocess calls in test_worktree_source_conflicts.py and test_worktree_new.py to use the consolidated helper from its new location."

### OOR-8: Phase 4 has 10 steps with no internal checkpoint
- **Axis:** Checkpoint adequacy
- **Severity:** Major
- **Location:** Phase 4
- **Problem:** Phase 4 has 10 steps spanning code fixes (4.1-4.2), test restructuring (4.3-4.8), and documentation (4.9-4.10). The Expansion Guidance says "Run full test suite (final validation)" only after ALL Phase 4 steps. If step 4.1 (import changes) breaks tests, the agent won't discover this until after 9 more steps of changes, making diagnosis difficult. The Expansion Guidance notes Phase 4 "could be split" but doesn't commit to it.
- **Recommendation:** Split Phase 4 into two sub-phases with a checkpoint between: Phase 4A (code: steps 4.1, 4.2, 4.5) and Phase 4B (tests: 4.3, 4.4, 4.6, 4.7, 4.8) and Phase 4C (docs: 4.9, 4.10). Run test suite after 4A and after 4B. Alternatively, at minimum add a checkpoint after 4.2 (code changes that affect imports).

### OOR-9: Step 3.2 test deletion list may be wrong
- **Axis:** Missing context that causes hallucination
- **Severity:** Minor
- **Location:** Step 3.2
- **Problem:** The step lists 6 test names to delete using wildcard notation (`test_*_no_slug_derivation_prose`, etc.) but these are paraphrased, not exact function names. The deliverable review (T3) lists the same paraphrased names. An executing agent that greps for these exact strings may not find them if the actual function names differ slightly (e.g., `test_mode5_no_slug_derivation_prose` vs `test_execute_rule_mode5_no_slug_derivation_prose`). The step says "Keep: 2 behavioral tests" but doesn't name them.
- **Recommendation:** During expansion, require the agent to read the file first and enumerate exact function names. Add to the step: "Read test_execute_rule_mode5_refactor.py first. Identify exact function names matching the absence pattern. List the 2 behavioral tests to keep by name before deleting anything."

### OOR-10: Cross-cutting X2 not fully resolved by Step 1.3
- **Axis:** Requirements coverage
- **Severity:** Minor
- **Location:** Step 1.3 vs X2
- **Problem:** Cross-cutting issue X2 notes "The module boundary between commands.py and merge_helpers.py is unclear." Step 1.3 only extracts `get_dirty_files` and `check_clean_tree` to git_utils.py. This resolves the duplication but doesn't clarify the module boundary itself. The `__all__` re-exports (C4, Step 4.1) are a symptom of the same unclear boundary. The outline doesn't acknowledge that X2 is only partially addressed.
- **Recommendation:** Add a note to the Requirements Mapping that X2 is partially addressed by Steps 1.3 and 4.1 but the module boundary question (what belongs in commands.py vs merge_helpers.py) is explicitly out of scope for this fix runbook. This prevents an agent from attempting a larger refactor.

### OOR-11: G2 severity mismatch between deliverable review and runbook
- **Axis:** Requirements coverage
- **Severity:** Minor
- **Location:** Requirements Mapping table, G2 row
- **Problem:** The deliverable review lists G2 as both Major (in Findings by Severity) and Minor (also listed under Minor). The runbook Requirements Mapping places G2 in Phase 1 (Major Code Fixes). The deliverable review text itself says "Severity: Minor" in the G2 finding body. The runbook's Phase 1 placement treats it as Major, which is inconsistent with the source.
- **Recommendation:** Move G2 from Phase 1 to Phase 4 (Minor Fixes) to match the source finding's severity. It's a simple deletion -- appropriate for Phase 4 complexity.

### OOR-12: Step 4.4 test scenario assumes precommit failure simulation
- **Axis:** Ambiguity that causes wrong action
- **Severity:** Minor
- **Location:** Step 4.4
- **Problem:** The test scenario says "Simulate precommit failure" at step 4. The codebase follows "E2E over mocked subprocess" (learning). Simulating a precommit failure in an e2e test requires either (a) creating actual precommit violations, (b) mocking the precommit subprocess call, or (c) patching the precommit check function. The outline doesn't specify which approach, and the learning says "mocking only for error injection" which could be interpreted either way for precommit simulation.
- **Recommendation:** Specify: "Create a real precommit violation (e.g., introduce a lint error in the merged file) rather than mocking the precommit check. This aligns with the e2e testing principle."

## Requirements Coverage Assessment

All 27 findings from the deliverable review are mapped to runbook steps. T9 is correctly noted as addressed by T2 deletion. The mapping is complete.

Two gaps worth noting:

- **X1 (path inconsistency):** Addressed across Steps 0.2, 0.3, and 1.6 -- but the outline doesn't call out the cross-cutting nature. An agent fixing 0.2 might not realize it should check for the same wrong path in other files beyond those listed.

- **X2 (API contract gap):** Only partially addressed (see OOR-10). The outline should explicitly scope-bound this to prevent agent scope creep.

## Recommendations

Ordered by impact on execution correctness:

1. **OOR-1 (Critical):** Add control flow decision tree to Step 0.1 distinguishing pre-commit vs post-commit abort calls
2. **OOR-4 + OOR-3 (Major):** Resolve Step 1.4 implementation choice and declare Step 1.3 dependency
3. **OOR-5 (Major):** Decide fixture consolidation target now instead of deferring to the executing agent
4. **OOR-6 (Major):** Re-sequence Step 4.3 relative to Phase 3 consolidation steps, or update description to account for Phase 3 output
5. **OOR-8 (Major):** Split Phase 4 into sub-phases with intermediate checkpoint after code changes
6. **OOR-2 (Major):** Specify which implementation is canonical for git_utils.py extraction and what moves vs stays
7. **OOR-9 (Minor):** Add "read file first, enumerate exact names" instruction to Step 3.2
8. **OOR-10 (Minor):** Explicitly scope-bound X2 to prevent agent overreach
9. **OOR-11 (Minor):** Move G2 to Phase 4 to match source severity
10. **OOR-7 (Minor):** Update Step 4.5 to reference post-Phase-3 import locations
11. **OOR-12 (Minor):** Specify e2e precommit failure approach for Step 4.4
