# Validator Consolidation — Runbook Outline

**Source:** `plans/validator-consolidation/requirements.md`
**Tier:** 3 — Full Runbook

## Requirements Mapping

| Requirement | Phase | Steps | Notes |
|-------------|-------|-------|-------|
| FR-1: Unified command (`claudeutils validate`) | 3 | 3.7 | Click subcommand group |
| FR-2: Learnings validation | 1 | 1.2 | Title format, word count, duplicates |
| FR-3: Memory index validation | 2 | 2.6 | Entry existence, ambiguity, duplicates |
| FR-4: Task key validation | 2 | 2.5 | Uniqueness within session, git history |
| FR-5: Orphan detection | 2 | 2.6 | Semantic headers not in index |
| FR-6: Precommit integration | 3 | 3.8 | Single `just precommit` call |
| NFR-1: Test coverage | All | 1.1-3.7 | Full test suite per validator |
| NFR-2: Clear error messages | All | 1.1-2.6 | Line numbers, file paths, descriptions |
| NFR-3: Fast execution | All | All | <1s for typical project |
| C-1: Merge commit handling | 2 | 2.5 | Check all parents after first |
| C-2: CLAUDE.md as root marker | 1 | 1.1 | Root discovery in common.py |
| D-1: Validators in claudeutils | 1-2 | 1.1-2.6 | src/claudeutils/validation/ |
| D-2: Shared patterns extracted | 1 | 1.1 | common.py utilities |
| D-3: Test suite required | All | 1.1-3.7 | Post-hoc tests for ported logic |
| D-4: Entry point → Option A | 3 | 3.7 | `claudeutils validate [targets]` |

## Key Decisions

- **D-4 resolved:** Option A — `claudeutils validate [targets]` using Click subcommand group, consistent with existing CLI pattern (`claudeutils feedback`, `claudeutils token`)
- **Root discovery:** Each validator function takes `root: Path` parameter (not `find_project_root()` internally). CLI resolves root once and passes it down. Tests pass `tmp_path`.
- **Module structure:** `src/claudeutils/validation/` package with one module per validator + `common.py` for shared utilities
- **Autofix preservation:** memory_index autofix behavior preserved (autofixes placement/ordering/structural, only non-autofixable issues are errors)

## Phase Structure

### Phase 1: Foundation + Simple Validators (Steps 1-4)

Estimated scope: ~400 lines new code, ~300 lines tests. Model: haiku.

- **Step 1:** Create validation package + common utilities + tests (C-2, D-2)
  - `src/claudeutils/validation/__init__.py` — expose public API
  - `src/claudeutils/validation/common.py` — `find_project_root()` (C-2: uses CLAUDE.md as root marker), error formatting utilities
  - `tests/test_validation_common.py` — root finding, error formatting tests
  - Success criteria: Root discovery works in projects with CLAUDE.md, error messages include line numbers and file paths

- **Step 2:** Port learnings validator + tests (FR-2)
  - Source: `agent-core/bin/validate-learnings.py` (80 lines)
  - Target: `src/claudeutils/validation/learnings.py`
  - `tests/test_validation_learnings.py` — title format (## Title), word count (5 max), duplicates, empty titles
  - Success criteria: All FR-2 checks pass, existing validation behavior preserved

- **Step 3:** Port jobs validator + tests
  - Source: `agent-core/bin/validate-jobs.py` (113 lines)
  - Target: `src/claudeutils/validation/jobs.py`
  - `tests/test_validation_jobs.py` — table parsing, directory scanning, missing/extra plans
  - Success criteria: Jobs table validates against plans/ directory structure

- **Step 4:** Port decision_files validator + tests
  - Source: `agent-core/bin/validate-decision-files.py` (145 lines)
  - Target: `src/claudeutils/validation/decision_files.py`
  - `tests/test_validation_decision_files.py` — structural detection, content threshold, nesting
  - Success criteria: Decision files validate structural headers correctly

**Phase 1 Checkpoint:** Run `pytest tests/test_validation_*.py -k "common or learnings or jobs or decision"` to verify foundation validators work correctly before proceeding to complex validators.

### Phase 2: Complex Validators (Steps 5-6)

Estimated scope: ~750 lines new code, ~500 lines tests. Model: haiku.

**Note:** Step 6 memory_index autofix logic is being ported (not designed from scratch), so haiku is sufficient for translation work.

- **Step 5:** Port tasks validator + tests (FR-4, C-1)
  - Source: `agent-core/bin/validate-tasks.py` (275 lines)
  - Target: `src/claudeutils/validation/tasks.py`
  - `tests/test_validation_tasks.py` — task extraction, learning key disjointness, git history (mocked subprocess), **merge commit handling** (C-1: check all parents after first)
  - Key: subprocess calls for git operations need careful mocking
  - Success criteria: Task key uniqueness validated across session.md/todo.md/shelved + git history, handles merge commits correctly

- **Step 6:** Port memory_index validator + tests (FR-3, FR-5)
  - Source: `agent-core/bin/validate-memory-index.py` (480 lines)
  - Target: `src/claudeutils/validation/memory_index.py`
  - `tests/test_validation_memory_index.py` — header collection, entry parsing, **orphan detection** (FR-5: semantic headers not in index = error), duplicate detection, word count, autofix behavior, section placement
  - Largest validator — may approach 400-line limit, consider splitting parsing/autofix helpers
  - Success criteria: All existing memory_index validation behavior preserved, including autofix for placement/ordering/structural issues

**Phase 2 Checkpoint:** Run full test suite (`pytest tests/test_validation_*.py`) and verify all validators work correctly before integrating into CLI.

### Phase 3: CLI + Integration (Steps 7-8)

Estimated scope: ~150 lines CLI code, ~200 lines tests, justfile update. Model: haiku.

- **Step 7:** Create validation CLI subcommand + tests (FR-1, D-4)
  - `src/claudeutils/validation/cli.py` — Click group with subcommands (learnings, memory-index, tasks, decisions, jobs, all)
  - Wire into `src/claudeutils/cli.py` via `cli.add_command(validate)`
  - `tests/test_validation_cli.py` — subcommand routing, all-targets mode, error exit codes
  - Success criteria: `claudeutils validate [targets]` works for all validators, proper exit codes on validation failure

- **Step 8:** Update justfile + remove old scripts + e2e verify (FR-6)
  - Update `justfile` precommit recipe: replace 5 script calls with `claudeutils validate`
  - Remove `agent-core/bin/validate-{learnings,memory-index,decision-files,tasks,jobs}.py`
  - Run `just precommit` to verify end-to-end
  - Success criteria: `just precommit` runs all validators via single `claudeutils validate` call, old scripts deleted

**Phase 3 Checkpoint:** Run `just precommit` on clean working tree to verify complete integration. Test should pass without any validation errors.

## Complexity Per Phase

| Phase | Steps | Lines (est.) | Model | Parallelizable |
|-------|-------|-------------|-------|----------------|
| 1: Foundation + Simple | 4 | ~700 | haiku | Steps 2-4 independent after Step 1 |
| 2: Complex Validators | 2 | ~1250 | haiku | Steps 5-6 independent |
| 3: CLI + Integration | 2 | ~350 | haiku | Sequential |

## Dependencies

- Step 1 (common) must complete before Steps 2-6
- Steps 2-6 are independent of each other
- Step 7 depends on all validators (Steps 2-6) existing
- Step 8 depends on Step 7 (CLI must be wired before justfile update)

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Test patterns to include:**
- For common.py: Test `find_project_root()` with missing CLAUDE.md (should raise error), nested directories (should find root correctly), and error formatting with various inputs
- For each validator: Include at least one test for each validation rule (e.g., learnings needs 5 tests minimum: format, word count, duplicates, empty, structural prefix)
- For tasks validator: Mock `subprocess.run()` carefully — provide sample git log output for history checks, test merge commit parent iteration logic explicitly
- For memory_index: Test autofix behavior separately from validation — verify autofixes don't trigger errors, only non-autofixable issues error

**Module boundary guidance:**
- Keep validator functions pure: take `root: Path` parameter, return validation results (not exit codes)
- CLI layer handles exit codes and user-facing output formatting
- Common utilities should include: `find_project_root()`, `format_error(file, line, msg)`, potentially `extract_headers(file)` if shared across validators

**Checkpoint validation steps:**
- Phase 1 checkpoint: Verify common.py works with actual project structure before porting validators
- Phase 2 checkpoint: Run validators against actual project files (agents/learnings.md, agents/memory-index.md, agents/session.md) to catch edge cases
- Phase 3 checkpoint: Test `just precommit` in clean state AND with intentional validation errors (to verify error propagation)

**References to source scripts:**
- When porting, preserve exact validation logic — line numbers from source scripts in requirements.md (80, 113, 145, 275, 480 lines) indicate scope, not prescriptive structure
- memory_index.py autofix logic (Step 6) is the most complex — consider extracting `apply_autofixes()` helper if main function approaches 250 lines
- tasks.py git operations (Step 5) should use same subprocess patterns as original for consistency

**CLI structure:**
- Subcommands: `validate learnings`, `validate memory-index`, `validate tasks`, `validate decision-files`, `validate jobs`, `validate all`
- `validate all` runs all validators, aggregates errors, exits non-zero if any fail
- Each subcommand should support `--fix` flag for validators with autofix capability (currently only memory-index)
