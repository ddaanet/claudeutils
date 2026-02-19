# Worktree CLI Pattern Analysis

## Summary

The worktree CLI implements a clear separation: mechanical operations live in the CLI layer, while judgment and workflow orchestration stay in the agent-facing skill. The pattern uses Click command groups, subprocess wrappers with systematic error handling, and git state interrogation to power a tool that the `/worktree` skill invokes for focused task management. The handoff CLI should follow this same architecture.

## Architecture Overview

### Entry Point and Command Structure

**Location:** `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/cli.py`

- Single entry point: `claudeutils` command (via `project.scripts` in pyproject.toml)
- CLI uses Click framework with command groups
- Worktree exposed as subcommand: `claudeutils _worktree <command>`
- Underscore prefix (`_worktree`) signals internal tool, not user-facing command

**Command group structure** (`worktree/cli.py`):
```python
@click.group(name="_worktree")
def worktree() -> None:
    """Worktree commands."""

@worktree.command()
def ls(...) -> None: ...  # List worktrees

@worktree.command()
def new(...) -> None: ...  # Create worktree

@worktree.command()
def merge(...) -> None: ...  # Merge worktree back

@worktree.command()
def rm(...) -> None: ...  # Remove worktree

@worktree.command(name="clean-tree")
def clean_tree() -> None: ...  # Verify clean state
```

### CLI vs Agent Responsibility Split

**CLI layer (mechanical, stateless):**
- Parse command arguments and options
- Execute git/subprocess operations in deterministic order
- Report raw output (tab-separated for machine consumption, formatted for human)
- Detect merge conflicts, precommit failures, git errors
- Exit with semantic exit codes (0=success, 1=error, 2=config/guard issue, 3=conflict)
- NO session.md manipulation (except write temp files)
- NO judgment about whether to proceed

**Skill/Agent layer (judgment, workflow):**
- Read session.md to extract task context
- Decide which tasks can run in parallel
- Determine when to create vs merge vs remove worktrees
- Handle human interaction (user confirms merge conflicts, edits)
- Update session.md task status (move pending → worktree tasks)
- Interpret exit codes and route to recovery/escalation

**Example:** `claudeutils _worktree new --task "Task Name"`:
1. **CLI does:** Derive slug, create worktree, register sandbox, emit `slug\tpath`
2. **Skill does:** Parse output, read session.md, move task to worktree section, print launch command

### Key CLI Commands

#### `ls` (List Worktrees)

```
claudeutils _worktree ls [--porcelain]
```

- Reads git worktree list (porcelain format)
- Parses into slug, branch, path tuples
- Output modes:
  - Default: Rich-formatted table with status indicators
  - `--porcelain`: Tab-separated (slug, branch, path) for scripting

**Mechanical role:** Format git worktree state for consumption

#### `new` (Create Worktree)

```
claudeutils _worktree new [--base HEAD] [--session FILE] [--task NAME] [--session-md PATH] [slug]
```

**Options:**
- `slug`: Git branch/worktree identifier (mutually exclusive with `--task`)
- `--task NAME`: Derive slug from task name, create focused session
- `--base`: Commit to branch from (default HEAD)
- `--session`: Path to session.md file to commit into branch
- `--session-md`: Path to session.md for task extraction (default agents/session.md)

**Flow:**
1. Validate exclusive (slug XOR task)
2. If task: derive slug via `derive_slug()`, focus session.md via `focus_session(task)`
3. Create git worktree: run git commands in sequence
4. Register worktree container in `.claude/settings.local.json` (sandbox allowlist)
5. Initialize environment: run `just setup` if available
6. Output: `slug\tpath` (tab-separated, parsed by skill)

**Mechanical operations:**
- `git branch <slug> <commit>` (if session provided, use custom session commit)
- `git worktree add <path> <slug>`
- Create agent-core submodule worktree if exists
- JSON config write to `.claude/settings.local.json`
- Subprocess call to `just setup` for environment init

**NOT handled by CLI:** Moving task from Pending Tasks → Worktree Tasks (skill does this)

#### `merge` (Merge Worktree Branch)

```
claudeutils _worktree merge <slug>
```

**Exit codes:**
- 0: Success
- 1: Git error or precommit failure
- 2: Validation error (branch not found, merge state corruption)
- 3: Merge conflicts detected

**Merge phases (deterministic, resumable):**

1. **Phase 1: Validate clean trees** — Ensure parent and submodule are clean for merge
2. **Phase 2: Merge submodule** (if agent-core worktree exists)
3. **Phase 3: Merge parent repo** — Run git merge, detect conflicts
4. **Phase 4: Resolve conflicts + commit** — Auto-resolve known files (session.md, learnings.md), create merge commit, run precommit
5. **Phase 5: Validate merge result** — Verify branch is fully merged

**State detection** (`merge_state.py`):
- Checks MERGE_HEAD presence to detect in-progress merge
- Classifies into 5 states: merged, clean, parent_resolved, parent_conflicts, submodule_conflicts
- Resumes from appropriate phase on re-invocation

**Mechanical output:**
- Success: Silent (exit 0)
- Conflicts (exit 3): Formatted conflict report with file list, diff stats, hint command
- Error (exit 1): Git error message + stderr
- Validation failure (exit 2): Error description + stderr

**NOT handled by CLI:** Session.md amendment (skill wraps and does this)

#### `rm` (Remove Worktree)

```
claudeutils _worktree rm <slug> [--confirm] [--force]
```

**Guards (unless `--force`):**
- Require `--confirm` to prevent accidental removal (skill enforces this)
- Check parent repo is clean (uncommitted changes would be lost)
- Check submodule is clean
- Check branch is either merged or a focused session commit

**Mechanical operations:**
- Warn if worktree has uncommitted files
- Update session.md: remove task from Worktree Tasks (via `remove_worktree_task()`)
- Delete git worktree: `git worktree remove`, `git worktree prune`
- Delete branch: `git branch -d` (or `-D` for focused sessions)
- Clean up empty container directory
- Output: Summary message

#### `clean-tree` (Verify Clean Tree)

```
claudeutils _worktree clean-tree
```

- Check parent and submodule status
- Exempt session.md and learnings.md (can be staged during handoff)
- Exit code 1 if dirty (prints dirty files)

**Used by:** Merge command to validate preconditions

### Core Utilities and Abstractions

#### `_git()` subprocess wrapper

```python
def _git(*args: str, check: bool = True, env: dict[str, str] | None = None,
         input_data: str | None = None) -> str:
```

- Single-responsibility wrapper: execute git, capture stdout, return stripped
- `check=True` raises `CalledProcessError` on non-zero exit (default behavior)
- `check=False` swallows exit code, returns output
- Supports environment variable override (for custom GIT_INDEX_FILE)
- Supports stdin input (for `git hash-object`)

**Error handling pattern:** Caller decides whether to check exit code
- `_git("command", check=True)` → raise on failure
- `_git("command", check=False)` → return output, let caller check returncode

#### `wt_path()` — Worktree path derivation

```python
def wt_path(slug: str, create_container: bool = False) -> Path:
```

- Maps slug to sibling container structure
- Example: cwd `/Users/user/project` → worktree `/Users/user/project-wt/slug`
- Creates container on demand (idempotent)
- Raises ValueError if slug empty

**Why sibling container:** Allows multiple worktrees in one `-wt` directory, simplifies sandbox config

#### `derive_slug()` — Task name to git branch name

```python
def derive_slug(task_name: str) -> str:
```

- Validate task name via `validate_task_name_format()`
- Convert to lowercase alphanumeric + hyphens
- Deterministic (same task name → same slug every time)
- Example: "Implement ambient awareness" → "implement-ambient-awareness"

#### Session management (`session.py`)

- `extract_task_blocks()` — Parse task items from session.md markdown
- `focus_session()` — Create filtered session.md for worktree (just this task + context)
- `move_task_to_worktree()` — Update session.md: move task from Pending Tasks to Worktree Tasks with `→ \`slug\`` marker
- `remove_worktree_task()` — Remove task from Worktree Tasks section

**Constraint:** These are called by CLI during creation, NOT during merge/removal. Task movement is state change that lives in git commit history.

#### Merge state detection (`merge_state.py`)

- `_detect_merge_state()` — Classify current merge progress (5 states)
- `_recover_untracked_file_collision()` — Handle git merge edge case where incoming branch has untracked file that conflicts

### Error Handling Patterns

#### Exit Codes as Semantic Signal

| Code | Meaning | Operator Action |
|------|---------|-----------------|
| 0 | Success | Proceed |
| 1 | Non-recoverable error (git failure, precommit failure) | Show error, stop |
| 2 | Validation/guard failure (branch not found, dirty tree, no confirm flag) | Address precondition, retry |
| 3 | Merge conflict detected | Edit files, re-invoke merge |

#### Error Output Style

```python
# Write to stderr, exit with code
click.echo(f"Error message", err=True)
raise SystemExit(exit_code)

# Example from merge.py
if not _is_branch_merged(slug):
    click.echo("Error: branch not fully merged")
    raise SystemExit(2)
```

**Pattern:** Errors go to stderr (not stdout), exit code carries semantic meaning. No exceptions leak to user (caught at command boundary).

#### Guard Functions

Guards check preconditions and exit early if unmet:

```python
def _check_confirm(slug: str, confirm: bool) -> None:
    if not confirm:
        click.echo(f"Use worktree skill... Pass --confirm to invoke directly.", err=True)
        raise SystemExit(2)

def _guard_branch_removal(slug: str) -> tuple[bool, str | None]:
    # Returns (branch_exists, removal_type) or exits with code 2
```

**Use case:** Prevent accidental operations (skill enforces confirm flag, CLI validates it)

### State Management and Idempotence

#### Git State as Source of Truth

- No separate state file in `.claude/` for worktree tracking
- State lives entirely in: git worktree list, git branches, MERGE_HEAD file
- `claudeutils _worktree ls` queries this state on demand
- Session.md tracks task assignments, not git state

#### Idempotent Merge

The merge command can be safely re-invoked after fixing conflicts:

```python
def _detect_merge_state(slug: str) -> str:
    # Checks MERGE_HEAD to resume from current phase
    if _is_branch_merged(slug):
        return "merged"
    if merge_head exists:
        if conflicts: return "parent_conflicts"
        else: return "parent_resolved"
    return "clean"
```

**Use case:** User edits conflicted files, runs `claudeutils _worktree merge <slug>` again. CLI detects "parent_conflicts" state and resumes from conflict resolution phase.

#### Clean Tree Invariant

Every command validates clean tree (except direct modifiers that require `--confirm`):

```python
# merge.py
_check_clean_for_merge(path, exempt_paths, label)  # Exit 1 if dirty

# rm command
if _is_parent_dirty():
    click.echo("Parent repo has uncommitted changes...")
    raise SystemExit(2)
```

**Rationale:** Uncommitted state would be lost in merge/checkout. Git operations require baseline.

### Integration Points with Skill

#### Skill invocation pattern

The `/worktree` skill in `agent-core/skills/worktree/SKILL.md` invokes CLI with `dangerouslyDisableSandbox: true`:

```
Invoke: `claudeutils _worktree new --task "<task name>"`
Parse output to extract slug and path
```

#### Tab-separated output protocol

When CLI needs to return structured data for script parsing:

```python
# new command
click.echo(f"{slug}\t{worktree_path}" if task else str(worktree_path))

# ls command (porcelain mode)
for slug, branch, path in _parse_worktree_list(porcelain_output, main_path):
    click.echo(f"{slug}\t{branch}\t{path}")
```

**Convention:** Tab-separated with natural order (most useful first). Skill parses with `split("\t")`

#### Sandbox management

CLI writes to `.claude/settings.local.json` to register worktree containers:

```python
def add_sandbox_dir(container: str, settings_path: str | Path) -> None:
    # Read existing settings, append to additionalDirectories
    settings = json.loads(path.read_text())
    dirs = settings.setdefault("permissions", {}).setdefault("additionalDirectories", [])
    if container not in dirs:
        dirs.append(container)
    path.write_text(json.dumps(settings, indent=2))
```

**Why:** Worktree lives outside project root (sibling -wt container). Sandbox rules block all out-of-tree operations. CLI must update allowlist before worktree is usable.

## Package Structure

```
src/claudeutils/
├── cli.py                          # Main entry point, command routing
├── worktree/
│   ├── __init__.py                 # (empty, module marker)
│   ├── cli.py                      # Worktree commands (350 lines)
│   ├── merge.py                    # Merge orchestration (360 lines)
│   ├── merge_state.py              # State detection + recovery (~140 lines)
│   ├── resolve.py                  # Conflict resolution for session.md, learnings.md
│   ├── session.py                  # Session.md parsing + editing
│   ├── utils.py                    # Shared utilities (git wrapper, path, branch checks)
│   └── display.py                  # Rich formatting for `ls` output
```

### Imports and Dependencies

**Click:** CLI framework
- Commands, groups, options, arguments
- `CliRunner` for testing
- `click.echo()` for output, `click.get_text_stream()` for stdin

**Subprocess:** Spawning git, precommit, just commands
- `check=True/False` to control exception vs. return code
- `capture_output=True` for stdout/stderr capture

**Pathlib:** File path operations
- `Path.exists()`, `Path.read_text()`, `Path.write_text()`
- Container creation: `Path.mkdir(parents=True, exist_ok=True)`

**stdlib:** tempfile, json, re, shutil, os

### Testing Strategy

28 worktree-specific test files (15K+ LOC):

- **Fixtures** (`fixtures_worktree.py`): Git repo setup, cleanup, helpers
- **Command tests** (`test_worktree_commands.py`): Command group structure, invocation
- **Creation tests** (`test_worktree_new_*.py`): Session commit, config, focused branches
- **Merge tests** (`test_worktree_merge_*.py`): Phase progression, conflict handling, submodules, exit codes
- **Removal tests** (`test_worktree_rm_*.py`): Guard checks, session.md updates, cleanup
- **State tests** (`test_worktree_merge_state*.py`, `test_worktree_merge_validation.py`): Detection, error conditions
- **Session automation** (`test_worktree_session_*.py`): Task parsing, section updates
- **Submodule tests** (`test_worktree_submodule.py`): Agent-core worktree creation/merge

**Testing pattern:**
```python
def test_example(tmp_path: Path, monkeypatch, init_repo: Callable):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)  # Simulate working in repo
    init_repo(repo_path)           # Set up git repo

    runner = CliRunner()
    result = runner.invoke(worktree, ["command", "args"])

    assert result.exit_code == expected
    assert "expected output" in result.output
```

Uses Click's `CliRunner` for in-process invocation (not subprocess), enabling isolation and fixture control.

## Design Patterns Applied

### Mechanical vs. Judgment Split

**CLI (mechanical, deterministic):**
- Task: Input → Output via subprocess calls
- No state side effects (except git working tree)
- Failures map to exit codes
- Idempotent (re-invocation works)
- No human interaction

**Skill (judgment, interactive):**
- Reads CLI output + project state
- Makes routing decisions
- Handles conflicts via human editor
- Updates persistent state (session.md)
- Provides user feedback

**Benefit:** CLI is testable, composable, reproducible. Skill handles workflow complexity without burdening CLI.

### Subprocess Reliability

```python
def _git(*args: str, check: bool = True, ...) -> str:
    r = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=check,
        ...
    )
    return r.stdout.strip()
```

**Pattern:**
- Always capture stdout/stderr (`capture_output=True`)
- Always use text mode (`text=True`)
- Always strip whitespace (`strip()`)
- Let caller decide error handling (`check` parameter)

**Why:** Prevents accidental output leakage, enables testing, allows flexible error routing.

### Layered Validation

Example: merge command validates in sequence, exits on first failure:

```python
_check_clean_for_merge()      # Exit 1 if dirty
_detect_merge_state()         # Classify
if state == "merged":
    return                    # Success
elif state == "clean":
    _phase2_merge_submodule() # May exit 1 or 3
    _phase3_merge_parent()
    # ...
```

**Pattern:** Fail fast, validate preconditions first, communicate via exit code.

## Key Learnings for Handoff CLI

1. **Tab-separated output for scripting** — Skill parses output, use clear protocol
2. **Exit codes encode semantics** — 0=success, 1=error, 2=guard, 3=conflict
3. **Idempotence via state detection** — Use git/filesystem state, not metadata files
4. **Guards prevent misuse** — `--confirm` flag enforced by skill, CLI validates
5. **Clean tree invariant** — Commands fail if tree is dirty (data loss protection)
6. **Subprocess isolation** — Each command runs in deterministic subprocess, no shared state
7. **Sandbox configuration** — CLI must update `.claude/settings.local.json` if creating out-of-tree directories
8. **Session.md is skill domain** — CLI creates temp files, skill applies persistent changes
9. **Testing via CliRunner** — Use Click's runner, not subprocess, for isolation
10. **Error messages to stderr** — Separate diagnostic output from machine-consumable output

## File Locations (Absolute Paths)

- CLI entry point: `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/cli.py`
- Worktree CLI: `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/worktree/cli.py`
- Worktree merge: `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/worktree/merge.py`
- Worktree session: `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/worktree/session.py`
- Worktree utils: `/Users/david/code/claudeutils-wt/handoff-cli-tool/src/claudeutils/worktree/utils.py`
- Worktree skill: `/Users/david/code/claudeutils-wt/handoff-cli-tool/agent-core/skills/worktree/SKILL.md`
- Project config: `/Users/david/code/claudeutils-wt/handoff-cli-tool/pyproject.toml`
- Tests: `/Users/david/code/claudeutils-wt/handoff-cli-tool/tests/test_worktree_*.py`
