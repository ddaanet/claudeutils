# Vet Review: Validator Consolidation Runbook

**Scope**: Full runbook review including cross-phase issues, file paths, and requirements alignment
**Date**: 2026-02-07T12:00:00Z

## Summary

The runbook is comprehensive and well-structured with clear implementation steps for consolidating 5 validator scripts from `agent-core/bin/` into the `src/claudeutils/validation/` package. The phased approach is logical (foundation → simple validators → complex validators → CLI integration). However, there are critical path issues and several major structural concerns that need addressing.

**Overall Assessment**: Needs Significant Changes

## Issues Found

### Critical Issues

1. **Missing target directory**
   - Location: Throughout runbook (Steps 1-6)
   - Problem: Target directory `src/claudeutils/validation/` does not exist yet
   - Fix: Step 1 must explicitly create the directory structure before creating files in it. Add explicit instruction: `mkdir -p src/claudeutils/validation`

2. **Incorrect source file reference**
   - Location: Step 2, line 121
   - Problem: States "Source: `agent-core/bin/validate-learnings.py` (80 lines)" but actual file is 79 lines
   - Fix: Correct to "(79 lines)" or remove line count entirely (line counts are approximate and change)

3. **Incorrect source file reference**
   - Location: Step 3, line 151
   - Problem: States "Source: `agent-core/bin/validate-jobs.py` (113 lines)" but actual file is 112 lines
   - Fix: Correct to "(112 lines)" or remove line count

4. **Incorrect source file reference**
   - Location: Step 4, line 181
   - Problem: States "Source: `agent-core/bin/validate-decision-files.py` (145 lines)" but actual file is 144 lines
   - Fix: Correct to "(144 lines)" or remove line count

5. **Incorrect source file reference**
   - Location: Step 5, line 214
   - Problem: States "Source: `agent-core/bin/validate-tasks.py` (275 lines)" but actual file is 273 lines
   - Fix: Correct to "(273 lines)" or remove line count

### Major Issues

1. **Structural prefix validation incomplete**
   - Location: Step 2, test specification line 136
   - Problem: Test "structural prefix (`.`) not treated as duplicate of non-prefixed title" is specified but no implementation guidance on how to handle this in validation logic
   - Suggestion: Add explicit note that uniqueness check should normalize by removing structural prefix before comparison, or clarify that structural and non-structural variants are allowed as separate entries

2. **Missing guidance on module splitting**
   - Location: Step 6, line 258
   - Problem: States "If module approaches 400 lines: extract `autofix_index()` and helper parsing functions to `memory_index_helpers.py`" but provides no criteria for "approaches"
   - Suggestion: Specify threshold (e.g., "If module exceeds 380 lines") and provide explicit split guidance (which functions stay, which move)

3. **Ambiguous CLI structure**
   - Location: Step 7, lines 291-296
   - Problem: Creates `src/claudeutils/validation/cli.py` with Click group, then wires into main CLI, but unclear if validators should be subcommands of `validate` (e.g., `claudeutils validate learnings`) or separate commands
   - Suggestion: Clarify command structure explicitly. Based on context "validate [targets]" implies: `claudeutils validate` (all), `claudeutils validate learnings` (specific), etc.

4. **Requirements.md mismatch on validation directory**
   - Location: Requirements D-1 vs runbook metadata line 7
   - Problem: Requirements.md D-1 states "validators live in `src/claudeutils/validation.py`" (single file) but runbook creates `src/claudeutils/validation/` (package directory)
   - Suggestion: This is actually correct (package is better), but requirements.md should be updated to reflect package structure. Note in runbook that implementation chose package over single file for modularity.

5. **Incomplete test coverage specification for memory_index**
   - Location: Step 6, test list lines 261-272
   - Problem: Lists 13 test cases but doesn't specify tests for autofix behavior with multiple issues simultaneously (e.g., entry in wrong section AND out of order)
   - Suggestion: Add test: "multiple autofix issues resolved in single pass"

6. **Checkpoint execution unclear**
   - Location: Phase 1 Checkpoint line 202, Phase 2 Checkpoint line 278
   - Problem: States "Run `pytest tests/test_validation_*.py -q`" but doesn't clarify if this should fail-fast or collect all failures
   - Suggestion: Add explicit instruction: "All tests must pass before proceeding. If any test fails, stop and escalate."

7. **Validation CLI pattern unclear**
   - Location: Step 7, line 298
   - Problem: States "Pattern: follow existing CLI subcommand structure" but doesn't specify if `validate` should be a group with subcommands or a command with arguments
   - Suggestion: Based on other CLI patterns (account, model, statusline are groups), clarify: "Create Click group `validate` with subcommands `learnings`, `memory-index`, `tasks`, `decisions`, `jobs`. Default (no subcommand) runs all."

8. **Missing error handling specification**
   - Location: Step 7, line 295
   - Problem: States "prints errors to stderr, exits 1 on failure" but doesn't specify format of error output or whether to continue after first validator failure in "all" mode
   - Suggestion: Specify behavior: "In 'all' mode, run all validators and collect errors, then exit 1 if any failed. Print errors for each validator separately with clear headers."

### Minor Issues

1. **Line count specifications brittle**
   - Location: Multiple steps (2-6)
   - Note: Including exact line counts (e.g., "80 lines") for source files is brittle — files change slightly over time
   - Suggestion: Either remove line counts entirely or use "~80 lines" to indicate approximation

2. **Redundant path specification**
   - Location: Step 1, lines 89-90
   - Note: States "Create `src/claudeutils/validation/__init__.py`: Empty initially (will be populated as validators are added)" but then Step 7 line 303 updates it
   - Suggestion: Minor optimization — could state in Step 1 "Create empty `__init__.py` (updated in Step 7)" to set expectation

3. **Test module import pattern not specified**
   - Location: Steps 2-6, test creation
   - Note: Doesn't specify import pattern for test modules (absolute imports from `src/claudeutils/validation/*` or relative imports)
   - Suggestion: Add note: "Use absolute imports: `from claudeutils.validation.learnings import validate`"

4. **Git command safety not addressed**
   - Location: Step 8, lines 343-347
   - Note: Script deletion uses `Delete` but doesn't mention verifying files are committed first
   - Suggestion: Add safety check: "Verify old scripts are committed before deletion (no uncommitted changes in agent-core/bin/validate-*.py)"

5. **Precommit recipe integration specifics missing**
   - Location: Step 8, lines 328-340
   - Note: Shows before/after for justfile but doesn't show full context (what comes before/after those lines)
   - Suggestion: Minor — could add line numbers or surrounding context for exact replacement location

6. **Module 400-line limit enforcement unclear**
   - Location: Common Context line 68
   - Note: States "Line limit: 400 lines per module" but doesn't specify how to count (include comments? docstrings? blank lines?)
   - Suggestion: Clarify: "400 non-blank lines including comments and docstrings" or specify the exact counting method

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Unified command | Satisfied | Step 7 creates `claudeutils validate [targets]` CLI |
| FR-2: Learnings validation | Satisfied | Step 2 ports all checks (title format, word count, duplicates, empty) |
| FR-3: Memory index validation | Satisfied | Step 6 ports entry existence, ambiguity, duplicates checks |
| FR-4: Task key validation | Satisfied | Step 5 ports uniqueness, history, disjointness checks |
| FR-5: Orphan detection | Satisfied | Step 6 preserves orphan detection as ERROR (line 257) |
| FR-6: Precommit integration | Satisfied | Step 8 updates justfile to call `claudeutils validate` |
| NFR-1: Test coverage | Satisfied | Each validator step includes comprehensive test creation |
| NFR-2: Clear error messages | Partial | Validators preserve error formats but Step 7 CLI error handling underspecified |
| NFR-3: Fast execution | Not Verified | No performance testing specified, but validators are simple enough |
| C-1: Merge commit handling | Satisfied | Step 5 preserves merge parent logic (line 222-223) |
| C-2: CLAUDE.md as root marker | Satisfied | Step 1 specifies `find_project_root()` uses CLAUDE.md (line 96) |

**Gaps:**
- NFR-2 partially satisfied: CLI error output format and aggregation behavior not fully specified (see Major Issue #8)
- NFR-3 not explicitly validated: No performance testing step, relying on simplicity assumption

---

## Positive Observations

- **Excellent phased structure**: Foundation → simple → complex → integration is logical and allows early validation
- **Comprehensive test specifications**: Each validator step includes detailed test cases covering edge cases
- **Checkpoint placement**: Phase boundaries align with natural verification points
- **Porting pattern consistency**: All validator steps follow the same 8-point porting pattern
- **Parallelization awareness**: Metadata correctly identifies Steps 2-6 as parallelizable within phases
- **Requirements traceability**: Clear mapping between requirements and implementation steps
- **Prerequisite verification**: Metadata section validates all dependencies upfront

## Recommendations

1. **Standardize line count references**: Either remove exact line counts or use "~" prefix to indicate approximation
2. **Enhance CLI specification**: Add explicit command structure tree diagram showing all subcommands
3. **Add integration test**: Step 8 should include end-to-end test validating all validators run correctly via CLI
4. **Consider incremental precommit**: Could wire validators into precommit as they're completed (after each phase checkpoint) rather than waiting until Step 8
5. **Document splitting decision**: Add note explaining why package structure was chosen over single-file approach (modularity, maintainability)

## Next Steps

1. **CRITICAL**: Fix all line count mismatches (Issues 2-5) or remove line counts entirely
2. **CRITICAL**: Add explicit directory creation to Step 1 (Issue 1)
3. Address structural prefix handling in Step 2 (Major Issue 1)
4. Clarify CLI command structure in Step 7 (Major Issues 3, 7)
5. Specify error handling and output format for CLI (Major Issue 8)
6. Consider adding module split threshold guidance (Major Issue 2)
7. Update requirements.md to reflect package structure decision (Major Issue 4)
