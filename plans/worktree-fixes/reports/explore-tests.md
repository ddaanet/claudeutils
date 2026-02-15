# Worktree Test Infrastructure Exploration

## Summary

The worktree test infrastructure in this project consists of 12 dedicated test modules (2,646 lines total) spanning creation, merging, submodule handling, and conflict resolution. Tests use real git operations with `tmp_path` fixtures rather than mocks, establishing patterns for git repo creation, worktree setup, and session.md fixture generation. The fixture architecture separates cross-cutting concerns (conftest.py) from worktree-specific helpers (fixtures_worktree.py).

## Key Findings

### Test File Organization

**Location:** `/Users/david/code/claudeutils-wt/worktree-fixes/tests/`

Worktree tests are organized by functional area:

| File | Lines | Focus |
|------|-------|-------|
| `test_worktree_commands.py` | 399 | CLI commands, ls, session precommit, task mode |
| `test_worktree_merge_conflicts.py` | 392 | Conflict auto-resolution (agent-core, session.md, learnings.md) |
| `test_worktree_clean_tree.py` | 264 | Tree validation, staged changes detection |
| `test_worktree_merge_parent.py` | 248 | Parent merge initiation and precommit validation |
| `test_worktree_merge_submodule.py` | 281 | Submodule conflict resolution during merge |
| `test_worktree_new_config.py` | 219 | Sandbox registration, environment init, branch naming |
| `test_worktree_utils.py` | 220 | Slug derivation, path calculation (wt_path) |
| `test_worktree_merge_validation.py` | 194 | Merge validation and exit codes |
| `test_worktree_submodule.py` | 160 | Submodule initialization and fetch operations |
| `test_worktree_new_creation.py` | 128 | Branch creation, collision detection |
| `test_worktree_merge_jobs_conflict.py` | 138 | jobs.md conflict resolution |
| `test_worktree_rm.py` | 101 | Worktree cleanup operations |

**Total coverage:** 2,646 lines across 12 modules + 267 lines of fixtures.

### Fixture Pattern: Real Git Repos with tmp_path

**Principle:** Tests use real git operations on temporary filesystems rather than mocks. This enables e2e testing of git workflows including merge conflicts and submodule handling.

**Core fixture locations:**
- `/Users/david/code/claudeutils-wt/worktree-fixes/tests/conftest.py` — Global fixtures (267 lines)
- `/Users/david/code/claudeutils-wt/worktree-fixes/tests/fixtures_worktree.py` — Worktree-specific (267 lines)
- `/Users/david/code/claudeutils-wt/worktree-fixes/tests/pytest_helpers.py` — Helper functions (69 lines)

### Git Repo Fixtures

**init_repo** - Factory fixture creating initialized git repo

```python
@pytest.fixture
def init_repo() -> Callable[[Path], None]:
    """Return function to initialize git repo with config and commit."""
    def _init_repo(repo_path: Path) -> None:
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], ...)
        subprocess.run(["git", "config", "user.name", "Test User"], ...)
        (repo_path / "README.md").write_text("test")
        subprocess.run(["git", "add", "README.md"], ...)
        subprocess.run(["git", "commit", "-m", "Initial commit"], ...)
    return _init_repo
```

**Pattern:** Returns a callable that accepts `Path`, performs git init, config, and initial commit in one operation. Used across all creation tests.

**repo_with_submodule** - Complete repo fixture for merge testing

Located in `/Users/david/code/claudeutils-wt/worktree-fixes/tests/fixtures_worktree.py` (lines 72-154):

```python
@pytest.fixture
def repo_with_submodule(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create git repo with submodule and session files."""
```

Creates:
1. Main repo with README.md and initial commit
2. `agent-core` submodule (nested git repo)
3. Session files: `agents/session.md`, `agents/jobs.md`, `agents/learnings.md`
4. `.gitmodules` configuration
5. `.gitignore` for `wt/` directory

Returns path to main repo. Submodule created using actual `git submodule add` (not plumbing commands).

**setup_repo_with_submodule** - Lower-level fixture using git plumbing

Uses `git update-index --add --cacheinfo` to create gitlink entries directly (lines 175-266). This provides fine-grained control for specialized conflict testing where merge state matters.

### Helper Functions for Tests

**commit_file** - Atomic file creation + staging + commit

```python
@pytest.fixture
def commit_file() -> Callable[[Path, str, str, str], None]:
    """Return function to create, stage, and commit a file."""
    def _commit_file(path: Path, filename: str, content: str, message: str) -> None:
        (path / filename).write_text(content)
        subprocess.run(["git", "add", filename], cwd=path, ...)
        subprocess.run(["git", "commit", "-m", message], cwd=path, ...)
    return _commit_file
```

**Usage pattern:** Repeated throughout tests to build test scenarios:
```python
commit_file(repo_path, "file.txt", "content\n", "Commit message")
commit_file(worktree_path, "branch-file.txt", "branch content\n", "Branch change")
```

**mock_precommit** - Mocks `just precommit` validation

```python
@pytest.fixture
def mock_precommit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock subprocess.run for 'just precommit' to return success."""
    # Intercepts calls matching ["just", "precommit"] and returns success mock
    # Allows merge tests to skip actual precommit validation
```

**pytest_helpers.py utilities:**
- `make_mock_history_dir()` — Factory for mocking history directory lookups
- `setup_cli_mocks()` — Configures sys.argv, cwd, history_dir for CLI tests
- `assert_json_output()` — Validates and extracts JSON from captured output

Test constants defined:
- `SESSION_ID_MAIN = "e12d203f-ca65-44f0-9976-cb10b74514c1"`
- `TS_BASE`, `TS_EARLY`, `TS_MID`, `TS_LATE` — Timestamps for ordering tests

### Session.md Fixture Creation

**Pattern: focus_session() function**

Located in `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/cli.py` (lines 50-68):

```python
def focus_session(task_name: str, session_md_path: str | Path) -> str:
    """Filter session.md to task_name with relevant context sections."""
    content = Path(session_md_path).read_text()
    # Extracts task by name: `- [ ] **{task_name}** ...`
    # Returns focused session with:
    # - Header: "# Session: Worktree — {task_name}"
    # - Pending Tasks section: single task entry
    # - Filtered "Blockers / Gotchas" and "Reference Files" sections
```

**Usage in test_worktree_commands.py (line 79-113):**

```python
def test_session_precommit(...) -> None:
    """Session file committed to worktree branch before worktree creation."""
    session_file = tmp_path / "test-session.md"
    session_file.write_text("# Focused Session\n\nTask content")

    result = CliRunner().invoke(
        worktree, ["new", "test-feature", "--session", str(session_file)]
    )
    assert result.exit_code == 0

    session_md_path = tmp_path / "repo-wt" / "test-feature" / "agents" / "session.md"
    assert session_md_path.read_text() == "# Focused Session\n\nTask content"
```

**Session.md created by worktree new command:**
- Command accepts `--session` flag with external session file path
- File is copied/filtered into worktree at `agents/session.md`
- Committed as "Focused session for {task-name}" on branch before worktree creation

**Test file creation pattern in tests/test_worktree_merge_conflicts.py (line 156-175):**

```python
# Main side: Create session.md with initial task
(repo_with_submodule / "agents").mkdir(exist_ok=True)
(repo_with_submodule / "agents" / "session.md").write_text(
    "# Session\n\n- [ ] **Task A** — `/design` | sonnet\n"
)
subprocess.run(["git", "add", "agents/session.md"], cwd=repo_with_submodule, ...)
subprocess.run(["git", "commit", "-m", "Add session.md"], cwd=repo_with_submodule, ...)
```

**Conflict resolution testing (line 220-235):**

Session.md conflicts are tested by:
1. Creating different versions on main and worktree branches
2. Running `merge` command which auto-resolves via `--ours` strategy + task extraction
3. Verifying new tasks from worktree are extracted and appended

### Test Organization Patterns

**Fixture injection hierarchy:**

```
conftest.py (global)
├── clear_api_key (autouse)
├── temp_project_dir
├── mock_anthropic_client (factory)
└── pytest_plugins = ["tests.fixtures_worktree"]

fixtures_worktree.py (worktree-specific)
├── init_repo (factory)
├── repo_with_submodule
├── commit_file (factory)
├── mock_precommit
└── setup_repo_with_submodule (factory)
```

**Test patterns by type:**

1. **Creation tests** (`test_worktree_new_*.py`)
   - Use `init_repo` to set up base repo
   - Invoke `CliRunner().invoke(worktree, ["new", "task-name"])`
   - Verify worktree directory exists at `repo-wt/task-name/`
   - Check branch created: `git branch --list | grep task-name`

2. **Merge tests** (`test_worktree_merge_*.py`)
   - Use `repo_with_submodule` for complete setup
   - Create commits on worktree branch and main
   - Invoke merge command
   - Verify conflicts auto-resolved or merge completes cleanly
   - Check MERGE_HEAD nonexistent: `git rev-parse MERGE_HEAD` should fail

3. **Utility tests** (`test_worktree_utils.py`)
   - Test slug derivation: `derive_slug("Task name")` → `"task-name"`
   - Test path calculation: `wt_path("slug")` respects `-wt` container location
   - Use `init_repo` for minimal setup

4. **Config tests** (`test_worktree_new_config.py`)
   - Verify `.claude/settings.local.json` updates
   - Check sandbox `additionalDirectories` registration
   - Use `json.load()` to parse and validate config

### E2E Testing via Subprocess

No mocking of git operations. Tests invoke actual git commands:

```python
subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
subprocess.run(["git", "branch", "test-merge"], cwd=repo_path, ...)
subprocess.run(["git", "worktree", "add", str(worktree_path), "task-a"], ...)
```

**Rationale:**
- E2E: Catches real git state transitions
- Integration: Validates worktree skill against real git workflows
- Conflict testing: Merge conflicts must be actual git conflicts, not simulated

**Subprocess pattern constants:**
- `check=True` — Fail test on non-zero exit
- `capture_output=True` — Suppress noise, capture for debugging
- `text=True` — Parse stdout as string for assertions

### File Growth Profile

12 worktree test modules with clear separation of concerns:
- Largest: `test_worktree_commands.py` (399 lines) — CLI entry points
- Merge tests split across 4 files (392+281+248+138 = 1,059 lines)
- Focused: `test_worktree_rm.py` (101 lines) — Minimal focused scope

## Patterns

### Fixture Lifecycle

1. **Session-scoped:** Markdown fixtures directory created once per session
2. **Function-scoped:** All git repos created fresh per test via `tmp_path` (default)
3. **Factory pattern:** `init_repo`, `commit_file`, `mock_precommit` return callables for reuse

### Git Workflow Testing

- No git mocks — all tests use real `subprocess.run(["git", ...])`
- Fixtures create minimal necessary state (README.md, config, initial commit)
- Submodule tests use actual `git submodule add` and plumbing for advanced scenarios
- Merge conflict tests build state by creating commits on separate branches

### Session.md Conventions

- Format: `# Session\n\n- [ ] **Task Name** — metadata\n`
- Location in tests: `agents/session.md` under repo root
- Creation: Either via fixture, test file write, or `focus_session()` filtering
- Conflict resolution: Auto-resolved by merge command (task extraction + append pattern)

### Error Testing

Tests verify both success paths and error cases:
- Branch collision detection (`test_new_directory_collision`)
- Exit codes checked: `assert result.exit_code == 0/1`
- Error messages validated: `assert "error" in result.output.lower()`
- Git state verified after failures (branch not created, etc.)

## Gaps

1. **Session file conflict resolution not directly tested** — learnings.md and jobs.md auto-resolution tested, but session.md extraction logic (parsing task names) only tested in `test_merge_conflict_session_md` without edge cases (malformed task names, missing sections)

2. **Focus_session() function not directly unit-tested** — Only tested via CLI integration in `test_session_precommit`. Direct unit tests for edge cases (nonexistent task, malformed session.md, missing sections) would improve confidence.

3. **Worktree submodule cleanup not comprehensive** — `test_worktree_rm.py` is minimal (101 lines). No tests for cleanup when submodule worktree exists or stale worktrees in container.

4. **Path handling edge cases** — `wt_path()` tested for basic cases but not for nested repo situations or unusual directory names with special characters.

5. **Precommit failure handling** — `mock_precommit` always succeeds. No tests for scenarios where precommit validation fails and merge must abort.

6. **Settings.json validation** — `test_new_sandbox_registration` validates JSON structure but doesn't verify the settings actually prevent sandbox errors when accessed.

## Verification Commands

Test execution:
```bash
# All worktree tests
pytest tests/test_worktree*.py -v

# Specific module
pytest tests/test_worktree_merge_conflicts.py -v

# Single test
pytest tests/test_worktree_commands.py::test_session_precommit -v

# With coverage
pytest tests/test_worktree*.py --cov=claudeutils.worktree
```

Fixture discovery:
```bash
pytest --fixtures tests/conftest.py | grep -A 10 "init_repo\|repo_with_submodule"
```

File locations for reference:
- Test modules: `/Users/david/code/claudeutils-wt/worktree-fixes/tests/test_worktree*.py`
- Fixtures: `/Users/david/code/claudeutils-wt/worktree-fixes/tests/fixtures_worktree.py`
- Helpers: `/Users/david/code/claudeutils-wt/worktree-fixes/tests/pytest_helpers.py`
- Global: `/Users/david/code/claudeutils-wt/worktree-fixes/tests/conftest.py`
- Worktree CLI: `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/cli.py`
