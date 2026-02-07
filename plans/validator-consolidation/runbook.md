---
model: haiku
---

# Validator Consolidation

**Context**: Consolidate 5 validator scripts from `agent-core/bin/` into `src/claudeutils/validation/` package with unified CLI entry point and full test coverage.

**Source**: `plans/validator-consolidation/requirements.md`

---

## Weak Orchestrator Metadata

**Total Steps**: 8

**Execution Model**:
- Steps 1-8: Haiku (all steps are porting existing logic, no architectural judgment needed)

**Step Dependencies**:
- Step 1 must complete before Steps 2-6
- Steps 2-6 are independent (parallelizable)
- Step 7 depends on Steps 2-6
- Step 8 depends on Step 7

**Error Escalation**:
- Haiku → Sonnet: If validator logic needs restructuring beyond simple porting (e.g., memory_index exceeds 400-line limit and needs module split)
- Sonnet → User: If existing validator behavior is ambiguous or contradictory

**Report Locations**: `plans/validator-consolidation/reports/step-N.md`

**Success Criteria**: `just precommit` passes with all validators running via `claudeutils validate`, old scripts removed, full test suite green.

**Prerequisites**:
- Source validators exist at `agent-core/bin/validate-{learnings,memory-index,decision-files,tasks,jobs}.py` (verified)
- Package structure at `src/claudeutils/` (verified)
- CLI entry point at `src/claudeutils/cli.py` using Click (verified)
- Test suite at `tests/test_*.py` using pytest (verified)

---

## Common Context

**Design Decisions (binding):**
- D-1: Validators live in `src/claudeutils/validation/` package (requirements.md says `validation.py` single file — package chosen for modularity with one module per validator)
- D-2: Shared patterns in `common.py` (currently only `find_project_root()`)
- D-3: Full test suite required for each validator
- D-4: Option A — `claudeutils validate [targets]` Click subcommand

**Constraints (binding):**
- C-1: Task key uniqueness must check all merge parents, not just HEAD~1
- C-2: `find_project_root()` uses CLAUDE.md as root marker (not agents/ directory)

**Porting Pattern (all validator steps follow this):**
1. Read source script at `agent-core/bin/validate-*.py`
2. Create target module at `src/claudeutils/validation/*.py`
3. Adapt `validate()` function to take `root: Path` parameter (remove internal root discovery)
4. Remove `main()` and `if __name__` block (CLI handles invocation)
5. Keep all validation logic identical to original
6. Add type annotations (strict mypy), docstrings
7. Create test file at `tests/test_validation_*.py`
8. Run `pytest tests/test_validation_*.py -q` to verify

**Project Conventions:**
- Type annotations: full, strict mypy mode
- Imports: prefer explicit from specific modules
- `__init__.py`: minimal, expose public API only
- Line limit: 400 lines per module
- Test pattern: `tmp_path` fixture for temporary directories, `monkeypatch` for mocking
- Path handling: `Path.cwd()` not `os.getcwd()`
- Errors to stderr, exit 1 on failure

**Tool usage:** Use Read/Write/Edit/Glob/Grep — not Bash equivalents (cat, echo, grep, find).

**Checkpoint behavior:** At phase boundaries (after Steps 4, 6, 8), run full test suite: `pytest tests/test_validation_*.py -q`. All tests must pass before proceeding. If any test fails, stop and escalate — do not continue to next phase.

---

### Phase 1: Foundation + Simple Validators

## Step 1: Create Validation Package + Common Utilities + Tests

**Objective**: Create package structure and shared `find_project_root()` utility.

**Execution Model**: Haiku

**Implementation**:

1. Create package directory: `src/claudeutils/validation/`

2. Create `src/claudeutils/validation/__init__.py`:
   - Empty initially (updated in Step 7 with public API exports)

3. Create `src/claudeutils/validation/common.py`:
   - Port `find_project_root()` from any existing validator (they all have it)
   - Function signature: `find_project_root(start: Path | None = None) -> Path`
   - If `start` is None, use `Path.cwd()`
   - Walk up directory tree looking for `CLAUDE.md` (C-2)
   - Raise `FileNotFoundError` if root not found (don't silently fall back to cwd)

4. Create `tests/test_validation_common.py`:
   - Test: finds root when CLAUDE.md exists in parent
   - Test: finds root when CLAUDE.md exists in current dir
   - Test: raises FileNotFoundError when CLAUDE.md not found
   - Test: works from nested subdirectory
   - Test: custom start path parameter

**Expected Outcome**: Package importable, `find_project_root()` works correctly.

**Success Criteria**:
- `from claudeutils.validation.common import find_project_root` works
- All tests pass: `pytest tests/test_validation_common.py -q`
- `mypy src/claudeutils/validation/` clean

---

## Step 2: Port Learnings Validator + Tests

**Objective**: Port learnings validation (FR-2: title format, word count, duplicates, empty).

**Execution Model**: Haiku

**Source**: `agent-core/bin/validate-learnings.py` (~80 lines)

**Implementation**:

1. Create `src/claudeutils/validation/learnings.py`:
   - Port `extract_titles()` and `validate()` functions
   - `validate(path: Path, root: Path, max_words: int = 5) -> list[str]`
   - Keep `TITLE_PATTERN`, `MAX_WORDS` constants
   - Keep preamble skip logic (first 10 lines)
   - Use absolute imports: `from claudeutils.validation.common import find_project_root`

2. Create `tests/test_validation_learnings.py`:
   - Test: valid learnings file returns no errors
   - Test: title exceeding max word count returns error
   - Test: duplicate titles detected (case-insensitive)
   - Test: preamble (first 10 lines) skipped
   - Test: empty file returns no errors
   - Import: `from claudeutils.validation.learnings import validate`

**Expected Outcome**: Learnings validator produces identical results to original script.

**Success Criteria**: `pytest tests/test_validation_learnings.py -q` passes, validates FR-2 checks.

---

## Step 3: Port Jobs Validator + Tests

**Objective**: Port jobs.md validation against plans/ directory structure.

**Execution Model**: Haiku

**Source**: `agent-core/bin/validate-jobs.py` (~110 lines)

**Implementation**:

1. Create `src/claudeutils/validation/jobs.py`:
   - Port `parse_jobs_md()` and `get_plans_directories()` functions
   - Main function: `validate(root: Path) -> list[str]`
   - Preserve: skip `.`-prefixed entries, skip `plans/claude/`, skip `README.md`, skip complete plans when checking missing directories

2. Create `tests/test_validation_jobs.py`:
   - Test: valid jobs.md with matching plans/ returns no errors
   - Test: plan in directory but not in jobs.md → error
   - Test: plan in jobs.md but not in directory (non-complete) → error
   - Test: complete plans exempt from directory check
   - Test: table parsing handles standard format
   - Test: missing jobs.md → error

**Expected Outcome**: Jobs validator identical behavior to original.

**Success Criteria**: `pytest tests/test_validation_jobs.py -q` passes.

---

## Step 4: Port Decision Files Validator + Tests

**Objective**: Port decision file structural validation (organizational sections must be marked structural).

**Execution Model**: Haiku

**Source**: `agent-core/bin/validate-decision-files.py` (~145 lines)

**Implementation**:

1. Create `src/claudeutils/validation/decision_files.py`:
   - Port `parse_heading()`, `analyze_file()`, `validate()` functions
   - `validate(root: Path) -> list[str]`
   - Keep `CONTENT_THRESHOLD = 2`, `DECISION_GLOBS` patterns
   - Preserve action message format (A: mark structural, B: add content)

2. Create `tests/test_validation_decision_files.py`:
   - Test: section with content before sub-headings → no violation
   - Test: section with only sub-headings → violation (needs structural marker)
   - Test: structural marker (`.` prefix) → no violation
   - Test: content threshold (≤2 substantive lines before sub-heading → violation)
   - Test: nested heading levels handled correctly
   - Test: no decision files → no errors

**Expected Outcome**: Decision files validator identical behavior to original.

**Success Criteria**: `pytest tests/test_validation_decision_files.py -q` passes.

**Phase 1 Checkpoint**: Run `pytest tests/test_validation_common.py tests/test_validation_learnings.py tests/test_validation_jobs.py tests/test_validation_decision_files.py -q` and `mypy src/claudeutils/validation/`. All must pass before proceeding.

---

### Phase 2: Complex Validators

## Step 5: Port Tasks Validator + Tests

**Objective**: Port task key validation (FR-4: uniqueness, disjointness with learning keys, git history; C-1: merge commit handling).

**Execution Model**: Haiku

**Source**: `agent-core/bin/validate-tasks.py` (~275 lines)

**Implementation**:

1. Create `src/claudeutils/validation/tasks.py`:
   - Port all functions: `extract_task_names()`, `extract_learning_keys()`, `get_session_from_commit()`, `get_merge_parents()`, `get_staged_session()`, `get_new_tasks()`, `check_history()`, `validate()`
   - `validate(session_path: str, learnings_path: str, root: Path) -> list[str]`
   - Keep subprocess calls for git operations (git show, git rev-parse, git log -S)
   - Preserve merge commit logic (C-1): check all parents, task is "new" only if absent from ALL parents
   - Preserve octopus merge detection and error

2. Create `tests/test_validation_tasks.py`:
   - Test: task name extraction from session.md format
   - Test: duplicate task names within session.md → error
   - Test: task name conflicts with learning key → error
   - Test: new task found in git history → error
   - Test: merge commit checks all parents (mock both git rev-parse and git show)
   - Test: no session.md → no errors
   - Test: no learnings.md → still validates tasks
   - Mock `subprocess.run` for all git operations. Use `monkeypatch.setattr` or `unittest.mock.patch`.

**Expected Outcome**: Tasks validator identical behavior including merge commit handling.

**Success Criteria**: `pytest tests/test_validation_tasks.py -q` passes, C-1 merge logic tested.

---

## Step 6: Port Memory Index Validator + Tests

**Objective**: Port memory index validation (FR-3: entry existence/ambiguity/duplicates; FR-5: orphan detection as errors) with autofix.

**Execution Model**: Haiku

**Source**: `agent-core/bin/validate-memory-index.py` (~480 lines)

**Implementation**:

1. Create `src/claudeutils/validation/memory_index.py`:
   - Port all functions: `collect_structural_headers()`, `collect_semantic_headers()`, `extract_index_entries()`, `extract_index_structure()`, `validate()`, `autofix_index()`
   - `validate(index_path: str, root: Path, autofix: bool = True) -> list[str]`
   - Keep all regex patterns: `SEMANTIC_HEADER`, `STRUCTURAL_HEADER`, `DOC_TITLE`, `FILE_SECTION`
   - Keep `INDEXED_GLOBS`, `EXEMPT_SECTIONS` constants
   - Preserve autofix behavior: fix placement/ordering/structural issues silently, report only non-autofixable errors
   - Preserve orphan detection (FR-5): semantic headers without index entries → ERROR
   - If module exceeds 350 lines: extract `autofix_index()` and collection functions (`collect_structural_headers`, `collect_semantic_headers`) to `memory_index_helpers.py`. Main module keeps `validate()`, `extract_index_entries()`, `extract_index_structure()`.

2. Create `tests/test_validation_memory_index.py`:
   - Test: valid index with matching headers → no errors
   - Test: orphan semantic header (not in index) → error (FR-5)
   - Test: orphan index entry (no matching header) → error
   - Test: duplicate index entries → error
   - Test: word count violation (outside 8-15 range) → error
   - Test: missing em-dash separator → error
   - Test: entry in wrong section → autofixed (no error if autofix=True)
   - Test: entries out of order → autofixed
   - Test: structural header entries → removed by autofix
   - Test: exempt sections preserved as-is
   - Test: autofix=False reports all issues as errors
   - Test: duplicate headers across files → error
   - Test: multiple autofix issues resolved in single pass (wrong section + out of order)

**Expected Outcome**: Memory index validator identical behavior including autofix.

**Success Criteria**: `pytest tests/test_validation_memory_index.py -q` passes, FR-3 and FR-5 verified.

**Phase 2 Checkpoint**: Run `pytest tests/test_validation_*.py -q` and `mypy src/claudeutils/validation/`. All must pass before proceeding.

---

### Phase 3: CLI + Integration

## Step 7: Create Validation CLI + Tests

**Objective**: Create unified `claudeutils validate [targets]` command (FR-1, D-4).

**Execution Model**: Haiku

**Implementation**:

1. Create `src/claudeutils/validation/cli.py`:
   - Click group `validate` with invoke_without_command=True (bare `claudeutils validate` runs all)
   - Subcommands: `learnings`, `memory-index`, `tasks`, `decisions`, `jobs`
   - Command tree:
     ```
     claudeutils validate              → runs all validators
     claudeutils validate learnings    → runs learnings only
     claudeutils validate memory-index → runs memory-index only
     claudeutils validate tasks        → runs tasks only
     claudeutils validate decisions    → runs decisions only
     claudeutils validate jobs         → runs jobs only
     ```
   - Each subcommand: resolves `root` via `find_project_root()`, calls validator, prints errors to stderr, exits 1 on failure
   - "All" mode: runs every validator, collects all errors, prints errors per-validator with headers, exits 1 if ANY failed (don't short-circuit on first failure)
   - Pattern: follow existing Click group structure (see `account`, `model`, `statusline` in `src/claudeutils/cli.py`)

2. Wire into main CLI:
   - Add `from claudeutils.validation.cli import validate` to `src/claudeutils/cli.py`
   - Add `cli.add_command(validate)` alongside existing command registrations

3. Update `src/claudeutils/validation/__init__.py`:
   - Export key functions for programmatic use: `validate_learnings`, `validate_jobs`, etc.

4. Create `tests/test_validation_cli.py`:
   - Test: `claudeutils validate` runs all validators (mock each validator function)
   - Test: `claudeutils validate learnings` runs only learnings validator
   - Test: exit code 1 when validation fails
   - Test: exit code 0 when validation passes
   - Test: error output goes to stderr
   - Use Click's `CliRunner` for testing (see existing test patterns in `tests/test_cli_*.py`)

**Expected Outcome**: `claudeutils validate` runs all validators, individual targets selectable.

**Success Criteria**: `pytest tests/test_validation_cli.py -q` passes, `claudeutils validate` works from command line.

---

## Step 8: Update Justfile + Remove Old Scripts + E2E Verify

**Objective**: Wire precommit integration (FR-6) and clean up old scripts.

**Execution Model**: Haiku

**Implementation**:

1. Update `justfile` precommit recipe:
   - Replace:
     ```
     agent-core/bin/validate-tasks.py agents/session.md agents/learnings.md
     agent-core/bin/validate-learnings.py agents/learnings.md
     agent-core/bin/validate-decision-files.py
     agent-core/bin/validate-memory-index.py agents/memory-index.md
     agent-core/bin/validate-jobs.py
     ```
   - With:
     ```
     claudeutils validate
     ```

2. Remove old scripts:
   - Delete `agent-core/bin/validate-learnings.py`
   - Delete `agent-core/bin/validate-memory-index.py`
   - Delete `agent-core/bin/validate-decision-files.py`
   - Delete `agent-core/bin/validate-tasks.py`
   - Delete `agent-core/bin/validate-jobs.py`

3. Verify existing test for learning-ages still imports correctly:
   - Check `tests/test_learning_ages.py` — it imports from `agent-core/bin/learning-ages.py` (NOT a validator being removed), so should be unaffected
   - Run `pytest tests/test_learning_ages.py -q` to confirm

4. Run full verification:
   - `pytest -q` (entire test suite)
   - `just precommit` (end-to-end with new `claudeutils validate`)
   - `mypy src/claudeutils/validation/`

**Expected Outcome**: Precommit uses unified validator, old scripts gone, all tests green.

**Success Criteria**: `just precommit` passes in clean working tree, no old validate-*.py scripts remain in agent-core/bin/.

**Phase 3 Checkpoint**: `just precommit` on clean working tree passes. Full test suite green. Old scripts deleted.

---

## Orchestrator Instructions

Execute steps sequentially using validator-consolidation-task agent. Phase boundaries (after Steps 4, 6, 8) are checkpoints — run test suite and escalate if failures. Steps 2-4 and Steps 5-6 could be parallelized within their phases if orchestrator supports it, but sequential execution is acceptable.

---

## Dependencies

**Before This Runbook**:
- Source validators exist in `agent-core/bin/` (verified)
- claudeutils package structure exists (verified)
- Click CLI infrastructure exists (verified)

**After This Runbook**:
- Validators consolidated in `src/claudeutils/validation/`
- `claudeutils validate` is the single entry point
- Old scripts removed from `agent-core/bin/`
- Full test coverage for all validators
