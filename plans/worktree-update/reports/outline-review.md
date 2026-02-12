# Outline Review: worktree-update

**Artifact**: plans/worktree-update/outline.md
**Date**: 2026-02-11T19:45:00Z
**Mode**: review + fix-all

## Summary

The outline describes porting justfile worktree prototype behavior into the Python CLI. The original outline was structurally sound but lacked implementation specificity — high-level bullet points without sufficient detail for direct implementation. All issues have been fixed with detailed specifications, algorithms, and sequencing.

**Overall Assessment**: Ready

## Requirements Traceability

No formal requirements.md file exists. Requirements extracted from task prompt context:

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| Sibling directory paths (`<repo>-wt/<slug>`) | Script changes → new command | Complete | Path computation algorithm specified |
| Worktree-based submodule (not --reference) | Script changes → new command | Complete | git worktree add approach documented |
| Skill updated to use scripts | Skill changes | Complete | Invocation patterns and frontmatter updated |
| Merge ceremony implementation | Script changes → merge command | Complete | 4-phase algorithm with exit codes |
| Submodule removal ordering | Script changes → rm command | Complete | Critical ordering documented |
| Sandbox registration | Script changes → new command | Complete | settings.local.json modification specified |

**Traceability Assessment**: All requirements covered with implementation details.

## Review Findings

### Critical Issues

**C1. Missing implementation algorithms**
- Location: Script changes section (all three commands)
- Problem: High-level bullets without detailed algorithms — implementer would need to reverse-engineer from justfile
- Fix: Added detailed step-by-step algorithms with git commands, exit code handling, and error conditions for `new`, `rm`, and `merge` commands
- **Status**: FIXED

**C2. Merge command completely underspecified**
- Location: "Add merge command" bullet
- Problem: Listed 3 phases and exit codes without any implementation detail — merge is the most complex operation (180+ lines in justfile)
- Fix: Expanded to 4 phases with detailed git commands, conflict resolution strategies, and control flow for each phase
- **Status**: FIXED

**C3. Missing CLI registration decision**
- Location: Key Decisions section
- Problem: Outline silent on whether to keep `_worktree` prefix or register as main command group — affects skill invocation
- Fix: Added D6 decision to remove underscore and register as `claudeutils worktree`, updated skill changes accordingly
- **Status**: FIXED

### Major Issues

**M1. Path computation not described**
- Location: "Update new command" section
- Problem: "port wt-path() logic" without explaining what that logic is
- Fix: Added container detection algorithm, sibling path construction rules, and directory creation logic
- **Status**: FIXED

**M2. Submodule worktree approach underspecified**
- Location: "Update new command" → Submodule bullet
- Problem: Single line mentioning worktree add without branch handling logic
- Fix: Added branch existence detection, conditional `-b` flag usage, and removal of `--reference` logic
- **Status**: FIXED

**M3. Sandbox registration missing implementation**
- Location: "Update new command" → Sandbox bullet
- Problem: "port add-sandbox-dir()" without specifying JSON structure or file locations
- Fix: Added JSON read/write logic, `additionalDirectories` array handling, dual file locations (main + worktree)
- **Status**: FIXED

**M4. Removal ordering not emphasized as critical**
- Location: "Update rm command" section
- Problem: Listed removal steps but didn't call out that ordering is git constraint (not preference)
- Fix: Added "(critical)" marker, explicit rationale, and submodule-first emphasis
- **Status**: FIXED

**M5. Conflict resolution strategies missing**
- Location: "Add merge command" → Phase 3
- Problem: "conflict auto-resolution" without specifying which files get which strategy
- Fix: Added per-file-type strategies (agent-core ours, session.md extract+warn, source files ours) with git commands
- **Status**: FIXED

**M6. Environment init ambiguous**
- Location: "Update new command" → Environment init
- Problem: Listed fallback commands but not the detection logic
- Fix: Added `just --summary | grep -qx setup` check with subprocess cwd parameter
- **Status**: FIXED

**M7. Test coverage vague**
- Location: Test updates section
- Problem: "verify X" without listing specific test cases or assertions
- Fix: Expanded to specific assertions for each test file (path checks, ordering mocks, exit codes, idempotency)
- **Status**: FIXED

**M8. Missing helper function scope**
- Location: Implementation Sequence section (added during fix)
- Problem: Outline didn't identify reusable helpers needed across commands
- Fix: Added Steps 1-2 for `wt_path()` and `add_sandbox_dir()` helper functions
- **Status**: FIXED

**M9. Skill changes underspecified**
- Location: Skill changes section
- Problem: "Update path references" and "Update allowed-tools" without showing what changes to
- Fix: Added specific frontmatter changes, per-mode invocation updates, and path handling notes
- **Status**: FIXED

**M10. Justfile decision missing rationale**
- Location: Justfile simplification section
- Problem: "Design decision needed" without analysis
- Fix: Made decision (keep bash implementation), added rationale (colored output, user convenience, parallel implementations)
- **Status**: FIXED

### Minor Issues

**N1. Existing branch support mentioned twice**
- Location: "Update new command" bullets
- Problem: Listed as separate bullet without integration into branch creation flow
- Fix: Consolidated into single branch detection section with conditional logic
- **Status**: FIXED

**N2. Exit code semantics unclear**
- Location: "Add merge command" → Exit codes
- Problem: Listed codes without explaining when each occurs
- Fix: Added semantic descriptions (0=success, 1=conflicts/precommit, 2=fatal) and caller implications
- **Status**: FIXED

**N3. Scope missing implementation sequence**
- Location: Scope section
- Problem: Listed IN/OUT items but no guidance on implementation ordering
- Fix: Added 9-step implementation sequence showing helper functions first, then commands, then tests
- **Status**: FIXED

**N4. Key Decisions incomplete**
- Location: Key Decisions section
- Problem: Only 5 decisions listed, missing CLI registration and slug derivation reconciliation
- Fix: Expanded to 6 decisions with full rationale for each
- **Status**: FIXED

**N5. Missing session file handling in new command**
- Location: "Update new command" section
- Problem: Existing branch reuse mentioned but not what happens to --session flag when branch exists
- Fix: Added warning and ignore logic for session file when branch exists
- **Status**: FIXED

**N6. Container cleanup not specified in rm**
- Location: "Update rm command" section
- Problem: "Empty container directory cleanup" without implementation
- Fix: Added `os.listdir()` empty check and `os.rmdir()` call
- **Status**: FIXED

**N7. Precommit validation missing details**
- Location: "Add merge command" → Phase 4
- Problem: "precommit validation gate" without command or error handling
- Fix: Added `just precommit` command, exit code capture, and exit 1 on failure with message
- **Status**: FIXED

**N8. Test file organization unclear**
- Location: Test updates section
- Problem: "Update X" vs "Add X" without file structure context
- Fix: Added "(new file)" marker for test_worktree_merge.py, clarified updates to existing files
- **Status**: FIXED

## Fixes Applied

**Problem section (lines 3-14):**
- Expanded stale behavior list to enumerate all gaps between Python CLI and justfile
- Added correct behavior section with rationale for each feature

**Script changes → new command (lines 20-28):**
- Expanded path computation to full algorithm (container detection, sibling construction)
- Added existing branch detection with conditional flow
- Expanded submodule section to branch handling and --reference removal
- Detailed sandbox registration with JSON operations
- Added environment init detection logic with cwd parameter

**Script changes → rm command (lines 30-38):**
- Added path resolution reference
- Added uncommitted changes warning check
- Added registration probing for both parent and submodule
- Emphasized removal ordering as critical with rationale
- Detailed directory and container cleanup
- Changed branch deletion from -D to -d with fallback warning

**Script changes → merge command (lines 40-58):**
- Expanded from 3 bullets to 4 phases with full algorithms
- Phase 1: Clean tree checks with exempt files and exit codes
- Phase 2: Submodule resolution with ancestry check and conditional merge
- Phase 3: Parent merge with per-file-type conflict resolution strategies
- Phase 4: Precommit validation with exit code handling
- Added exit code semantics and caller implications

**Skill changes (lines 60-75):**
- Per-mode invocation updates with step references
- Frontmatter change from `_worktree` to `worktree`
- Path handling note about symbolic vs actual paths

**Justfile simplification (lines 77-85):**
- Made design decision (keep bash implementation)
- Added rationale (colored output, user convenience, parallel implementations)

**Test updates (lines 87-105):**
- Expanded to specific assertions per test file
- Added test cases for edge conditions (existing branch, empty container, idempotency)

**Key Decisions (lines 107-131):**
- Expanded from 5 to 6 decisions
- Added implementation details for each decision
- Added D6 for CLI registration approach

**Scope (lines 133-164):**
- Added implementation sequence with 9 steps
- Ordered helpers before commands before tests
- Clarified IN vs OUT items

## Positive Observations

**Clear problem statement:** Outline correctly identified the gap between justfile prototype and Python CLI.

**Correct technical approach:** Worktree-based submodule approach is superior to --reference clone (shared object store, bidirectional visibility).

**Sound architectural decisions:** Keeping justfile and Python CLI as parallel implementations serves both user (interactive) and programmatic (skill) use cases.

**Proper scoping:** Correctly excluded focus-session.py and execute-rule.md conventions as separate concerns.

**Justfile as specification:** Using working justfile recipes as reference implementation reduces design risk.

## Recommendations

**Implementation priority:** Start with helper functions (`wt_path()`, `add_sandbox_dir()`) before commands — reduces duplication and ensures consistency.

**Merge command complexity:** This is the highest-risk implementation (4 phases, conflict resolution, idempotency). Consider TDD approach with phase-by-phase test coverage.

**Existing branch handling:** Test both creation paths (new branch vs existing branch) to validate conditional logic.

**Container isolation verification:** After implementation, test that worktree Claude sessions don't inherit parent CLAUDE.md (primary motivation for sibling paths).

**Settings.local.json handling:** Consider atomic write pattern (write to temp, rename) to avoid partial updates on crash.

---

**Ready for user presentation**: Yes — all critical, major, and minor issues fixed. Outline now provides sufficient implementation detail for direct execution.
