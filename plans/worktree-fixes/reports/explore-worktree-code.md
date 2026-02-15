# Worktree Code Exploration Report

## Summary

The worktree skill is a comprehensive git worktree management system with CLI commands for creating, merging, and removing parallel worktrees. The codebase is split between `src/claudeutils/worktree/` for core logic and `src/claudeutils/validation/` for session file validation. Task name handling currently lacks format constraints and full session block preservation during merges. The merge commit decision logic has a subtle bug where empty diffs skip commit creation, orphaning branches.

---

## Key Findings

### 1. **`src/claudeutils/worktree/cli.py`** — Main CLI Implementation

**File location:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/cli.py` (357 lines)

#### `derive_slug()` Function (Lines 17–23)

```python
def derive_slug(task_name: str, max_length: int = 30) -> str:
    """Task name to slug."""
    if not task_name or not task_name.strip():
        msg = "task_name must not be empty"
        raise ValueError(msg)
    slug = re.sub(r"[^a-z0-9]+", "-", task_name.lower()).strip("-")[:max_length]
    return slug.rstrip("-")
```

**Current behavior:**
- Accepts any characters, strips non-alphanumeric to hyphens
- Truncates at `max_length=30` (lossy)
- No validation of input format

**FR-1 constraint:** Needs to require `[a-zA-Z0-9 .\-]` input and remove `max_length` parameter entirely for lossless transformation.

#### `focus_session()` Function (Lines 50–68)

```python
def focus_session(task_name: str, session_md_path: str | Path) -> str:
    """Filter session.md to task_name with relevant context sections."""
    content = Path(session_md_path).read_text()
    pattern = rf"- \[ \] \*\*{re.escape(task_name)}\*\* (.+?)(?=\n-|\n## |\Z)"
    if not (match := re.search(pattern, content, re.DOTALL)):
        msg = f"Task '{task_name}' not found in session.md"
        raise ValueError(msg)

    metadata = match.group(1).rstrip()
    plan_dir = m.group(1) if (m := re.search(r"[Pp]lan:\s*(\S+)", metadata)) else None
    result = (
        f"# Session: Worktree — {task_name}\n\n"
        f"**Status:** Focused worktree for parallel execution.\n\n"
        f"## Pending Tasks\n\n- [ ] **{task_name}** {metadata}\n"
    )
    for section in ["Blockers / Gotchas", "Reference Files"]:
        if filtered := _filter_section(content, section, task_name, plan_dir):
            result += f"\n{filtered}"
    return result
```

**Current behavior:**
- Extracts task line and inline metadata
- Uses `re.escape()` for pattern safety (good)
- Matches single-line task entries only (continuation lines lost)

**Issue:** Only captures the first line of a task. If a task has continuation lines (indented metadata), they're dropped. FR-4 requires full block extraction.

**`_filter_section()` Helper (Lines 26–47):**
Filters Blockers/Gotchas/Reference Files sections by task name or plan directory match. Reconstructs section with matching entries only.

#### `new` Command (Lines 248–274)

```python
@worktree.command()
@click.argument("slug", required=False)
@click.option("--base", default="HEAD")
@click.option("--session", default="")
@click.option("--task", default="")
@click.option("--session-md", default="agents/session.md")
def new(slug: str | None, base: str, session: str, task: str, session_md: str) -> None:
    """Create worktree in sibling container."""
    if task and slug:
        raise click.UsageError("slug and --task are mutually exclusive")
    if not task and not slug:
        raise click.UsageError("either slug or --task is required")
    temp_session_file = None
    try:
        if task:
            slug = derive_slug(task)
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
                f.write(focus_session(task, session_md))
                temp_session_file = session = f.name
        assert slug is not None
        if (path := wt_path(slug, create_container=True)).exists():
            click.echo(f"Error: existing directory {path}", err=True)
            raise SystemExit(1)
        _setup_worktree(path, slug, base, session, task)
    finally:
        if temp_session_file:
            Path(temp_session_file).unlink(missing_ok=True)
```

**Current behavior:**
- `--task` mode: derive slug from task, focus session, create temp file, pass to setup
- `--slug` mode: direct slug usage
- Session file created in temp directory, never edited in main repo

**FR-6 requirement:** This command should move the task from Pending Tasks → Worktree Tasks with `→ <slug>` marker in the main repo's session.md.

#### `rm` Command (Lines 318–356)

```python
@worktree.command()
@click.argument("slug")
def rm(slug: str) -> None:
    """Remove worktree and its branch."""
    worktree_path = wt_path(slug)
    parent_reg, submodule_reg = _probe_registrations(worktree_path)

    if worktree_path.exists():
        status = _git("-C", str(worktree_path), "status", "--porcelain", check=False)
        if status:
            count = len(status.strip().split("\n"))
            click.echo(f"Warning: worktree has {count} uncommitted files")

    if parent_reg or submodule_reg:
        _remove_worktrees(worktree_path, parent_reg, submodule_reg)
    else:
        _git("worktree", "prune")

    r = subprocess.run(
        ["git", "branch", "-d", slug], capture_output=True, text=True, check=False
    )
    if r.returncode != 0 and "not found" not in r.stderr.lower():
        click.echo(f"Branch {slug} has unmerged changes — use: git branch -D {slug}")

    if worktree_path.exists():
        shutil.rmtree(worktree_path)

    container = worktree_path.parent
    if container.exists() and not list(container.iterdir()):
        container.rmdir()

    click.echo(f"Removed worktree {slug}")
```

**Current behavior:**
- Probes worktree registration
- Removes submodule worktree first (order is important for git), then parent
- Attempts branch deletion
- Clean up container directory if empty

**FR-6 requirement:** After merge, this command should remove the task from Worktree Tasks section (if task was completed/deleted in merged content) or keep it (if still pending).

#### `_create_parent_worktree()` (Lines 165–184)

Creates git worktree with optional focused session commit:
- If session file provided, creates a commit with just `agents/session.md` and branches from it
- Otherwise creates branch from base or reuses existing branch
- Uses custom git index to create the session commit

#### `_create_submodule_worktree()` (Lines 187–208)

Creates agent-core submodule worktree (shared object store via `git worktree`, not `--reference` clone):
- Probes if branch exists in agent-core
- Creates worktree in `<worktree_path>/agent-core/`
- Creates branch if doesn't exist

---

### 2. **`src/claudeutils/worktree/merge.py`** — Merge Operations

**File location:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/merge.py` (287 lines)

#### `_resolve_session_md_conflict()` (Lines 57–104)

```python
def _resolve_session_md_conflict(conflicts: list[str]) -> list[str]:
    """Resolve agents/session.md conflict.

    Keep ours and extract new tasks from theirs. Returns updated conflict list
    with session.md removed if present.
    """
    if "agents/session.md" not in conflicts:
        return conflicts

    ours_content = _git("show", ":2:agents/session.md", check=False)
    theirs_content = _git("show", ":3:agents/session.md", check=False)

    ours_tasks = {
        line
        for line in ours_content.split("\n")
        if line.strip().startswith("- [ ] **") and "**" in line
    }
    theirs_tasks = {
        line
        for line in theirs_content.split("\n")
        if line.strip().startswith("- [ ] **") and "**" in line
    }

    new_tasks = theirs_tasks - ours_tasks

    if new_tasks:
        ours_lines = ours_content.split("\n")
        pending_idx = next(
            (i for i, line in enumerate(ours_lines) if "## Pending Tasks" in line), None
        )
        if pending_idx is not None:
            next_section_idx = next(
                (
                    i
                    for i in range(pending_idx + 1, len(ours_lines))
                    if ours_lines[i].startswith("## ")
                ),
                len(ours_lines),
            )
            ours_lines[next_section_idx:next_section_idx] = ["", *sorted(new_tasks)]
        else:
            ours_lines.extend(["", "## Pending Tasks", "", *sorted(new_tasks)])
        ours_content = "\n".join(ours_lines)

    Path("agents/session.md").write_text(ours_content)
    _git("add", "agents/session.md")

    return [c for c in conflicts if c != "agents/session.md"]
```

**Current behavior:**
- Extracts single-line tasks only (lines matching `- [ ] **`)
- Uses set diff on full lines → loses multi-line task blocks
- Extracts "new" tasks as set difference
- Inserts before next `##` section header

**FR-4 bug:** A task with continuation lines merges as 1 line:
```
# Original (ours)
- [ ] **Task A** — plan

# Original (theirs)
- [ ] **Task B** — plan
  - Constraint: X
  - Constraint: Y

# Merged result (WRONG)
- [ ] **Task B** — plan
```

**Fix required:** Extract full task blocks (task line + all indented continuation lines), not just the task line.

#### `_phase4_merge_commit_and_precommit()` (Lines 252–279)

```python
def _phase4_merge_commit_and_precommit(slug: str) -> None:
    """Phase 4: Commit merge and run precommit validation.

    If staged changes exist after merge, commit with message "🔀 Merge <slug>".
    Then run `just precommit` and handle exit code appropriately.
    """
    staged_check = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        check=False,
    )

    if staged_check.returncode != 0:
        _git("commit", "-m", f"🔀 Merge {slug}")

    precommit_result = subprocess.run(
        ["just", "precommit"],
        capture_output=True,
        text=True,
        check=False,
    )

    if precommit_result.returncode == 0:
        click.echo("Precommit passed")
    else:
        click.echo("Precommit failed after merge")
        click.echo(precommit_result.stderr)
        raise SystemExit(1)
```

**Current behavior:**
- Checks if staged changes exist with `git diff --cached --quiet`
- Only commits if return code != 0 (changes exist)
- Skips commit if return code == 0 (no changes)

**FR-5 bug:** When session.md conflict resolves to no net changes, `git diff --cached --quiet` returns 0 → commit skipped → branch never becomes ancestor of HEAD → `git branch -d` correctly fails with "not fully merged" → orphan branch.

**Fix:** Always create merge commit when merge was initiated (Phase 3), even if staged changes are empty:
```python
# After _phase3_merge_parent completes successfully
_git("commit", "-m", f"🔀 Merge {slug}")  # Always commit
```

#### `_phase3_merge_parent()` (Lines 221–249)

Initiates merge with `--no-commit --no-ff` flag to avoid auto-committing, then auto-resolves known conflicts (agent-core, session.md, learnings.md, jobs.md). If unresolved conflicts remain, aborts merge.

#### `_phase1_validate_clean_trees()` (Lines 150–174)

Validates both main repo and worktree have clean trees (except exempt files: session.md, jobs.md, learnings.md, agent-core).

#### `_phase2_resolve_submodule()` (Lines 177–218)

Merges agent-core submodule commits if worktree version differs from local. Handles cases where commits aren't reachable (fetches from worktree submodule).

---

### 3. **`src/claudeutils/validation/`** — Validation Modules

**Directory:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/validation/`

#### Structure

- **`cli.py`** — CLI entry point with `validate` command group
- **`tasks.py`** — Task name validation (uniqueness, disjointness, history check)
- **`learnings.py`** — Learnings file validation
- **`memory_index.py`** — Memory index validation
- **`decision_files.py`** — Decision file structure validation
- **`jobs.py`** — Jobs.md validation
- **`common.py`** — Shared utilities

#### `tasks.py` (Lines 1–310)

Validates task names in session.md:

**Key functions:**

1. **`extract_task_names()` (Lines 21–35)**
   ```python
   TASK_PATTERN = re.compile(r"^- \[[ x>]\] \*\*(.+?)\*\* —")

   def extract_task_names(lines: list[str]) -> list[tuple[int, str]]:
       """Extract (line_number, task_name) pairs from task lines."""
       tasks = []
       for i, line in enumerate(lines, 1):
           m = TASK_PATTERN.match(line.strip())
           if m:
               tasks.append((i, m.group(1)))
       return tasks
   ```
   - Uses regex to match task pattern
   - Returns (line_number, task_name) tuples
   - Supports `[ ]`, `[x]`, `[>]` states

2. **`validate()` (Lines 246–309)**
   ```python
   def validate(session_path: str, learnings_path: str, root: Path) -> list[str]:
       """Validate task names. Returns list of error strings."""
       # Checks:
       # 1. Uniqueness within session.md (case-insensitive)
       # 2. Disjointness with learning keys
       # 3. Git history check for new tasks (git log -S)
       # 4. Merge commit handling (compares against all parents)
   ```

**Current checks:**
- Uniqueness across session.md (case-insensitive key)
- No collision with learning keys
- New tasks not present in git history
- Merge commit constraint: task is "new" only if absent from ALL parents (C-1)

**No format validation yet.** FR-2 requires adding character constraint checking (`[a-zA-Z0-9 .\-]` only, max 25 chars).

---

### 4. **`src/claudeutils/worktree/utils.py`** — Shared Utilities

**File location:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/utils.py` (39 lines)

#### `_git()` Helper (Lines 7–21)

```python
def _git(
    *args: str,
    check: bool = True,
    env: dict[str, str] | None = None,
    input_data: str | None = None,
) -> str:
    r = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=check,
        env=env,
        input=input_data,
    )
    return r.stdout.strip()
```

Convenience wrapper for git commands. Returns stdout stripped. Handles check flag and custom env.

#### `wt_path()` (Lines 24–38)

```python
def wt_path(slug: str, create_container: bool = False) -> Path:
    """Worktree path in sibling -wt container."""
    if not slug or not slug.strip():
        msg = "slug must not be empty or whitespace"
        raise ValueError(msg)
    current_path = Path.cwd()
    parent_name = current_path.parent.name
    container_path = (
        current_path.parent
        if parent_name.endswith("-wt")
        else current_path.parent / f"{current_path.name}-wt"
    )
    if create_container and not parent_name.endswith("-wt"):
        container_path.mkdir(parents=True, exist_ok=True)
    return container_path / slug
```

**Logic:**
- Checks if parent directory already ends with `-wt` (sibling container)
- If yes, use it directly (already in a -wt container)
- If no, create `<current_dir_name>-wt` sibling
- Returns `<container>/<slug>` path
- Optionally creates container directory

**Example paths:**
- Main repo: `/path/to/myproject` → worktree: `/path/to/myproject-wt/slug`
- Already in container: `/path/to/myproject-wt` → worktree: `/path/to/myproject-wt/slug`

---

### 5. **Precommit Validation** — Integration Points

**Location:** `/Users/david/code/claudeutils-wt/worktree-fixes/justfile` (603 lines)

#### `precommit` Recipe (Lines 22–33)

```bash
[no-exit-message]
precommit:
    #!{{ bash_prolog }}
    sync
    claudeutils validate
    gmake --no-print-directory -C agent-core check
    run-checks
    pytest_output=$(safe pytest -q 2>&1)
    echo "$pytest_output"
    if echo "$pytest_output" | grep -q "skipped"; then fail "Tests skipped — all tests must run"; fi
    run-line-limits
    report-end-safe "Precommit"
```

**Calls `claudeutils validate`** which runs all validators via `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/validation/cli.py`.

**FR-2 requirement:** Add task name format validator (character constraints, length) that runs here.

#### Worktree Merge Integration (Lines 201–331)

The `wt-merge` recipe includes precommit validation:
```bash
# Post-merge precommit gate
echo ""
echo "Running precommit validation..."
if ! just precommit >/dev/null 2>&1; then
    echo "${RED}Precommit failed after merge${NORMAL}" >&2
    ...
fi
```

---

### 6. **Test Structure** — Testing Patterns

**Location:** `/Users/david/code/claudeutils-wt/worktree-fixes/tests/`

#### Test Files

12 worktree test modules:
- `test_worktree_commands.py` — CLI commands (ls, new, merge, rm)
- `test_worktree_merge_conflicts.py` — Conflict auto-resolution
- `test_worktree_merge_submodule.py` — Submodule merge
- `test_worktree_merge_parent.py` — Parent merge
- `test_worktree_merge_jobs_conflict.py` — Jobs.md conflict
- `test_worktree_new_creation.py` — Worktree creation
- `test_worktree_new_config.py` — Config setup
- `test_worktree_clean_tree.py` — Clean tree validation
- `test_worktree_merge_validation.py` — Merge validation
- `test_worktree_rm.py` — Worktree removal
- `test_worktree_submodule.py` — Submodule operations
- `test_worktree_utils.py` — Utility functions

#### Fixtures (`tests/fixtures_worktree.py`)

```python
@pytest.fixture
def init_repo() -> Callable[[Path], None]:
    """Initialize git repo with config and commit."""
    # Creates git repo with user config and README.md

@pytest.fixture
def repo_with_submodule(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create git repo with submodule and session files."""
    # Sets up repo with agent-core submodule + agents/session.md, jobs.md, learnings.md

@pytest.fixture
def mock_precommit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock subprocess.run for 'just precommit' to return success."""
    # Prevents actual precommit execution in tests
```

#### Test Pattern Example

```python
def test_merge_conflict_session_md(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Auto-resolve session.md conflict by extracting new tasks from worktree."""
    monkeypatch.chdir(repo_with_submodule)

    # 1. Create worktree
    result = CliRunner().invoke(worktree, ["new", "test-merge"])
    assert result.exit_code == 0

    # 2. Make changes on worktree
    commit_file(worktree_path, "file.txt", "content\n", "message")

    # 3. Make conflicting change on main
    subprocess.run(["git", "checkout", "main"], cwd=repo_with_submodule, check=True)
    commit_file(repo_with_submodule, "other.txt", "content\n", "message")

    # 4. Merge and verify
    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0
```

**E2E approach:** Uses real git repos with tmp_path fixtures. Tests complete workflow start-to-finish.

---

### 7. **Justfile Worktree Recipes** — Implementation Comparison

**Location:** `/Users/david/code/claudeutils-wt/worktree-fixes/justfile` (lines 60–200)

The justfile contains parallel implementations:
- `wt-new` (bash recipe)
- `wt-task` (bash recipe)
- `wt-ls` (bash recipe)
- `wt-rm` (bash recipe)
- `wt-merge` (bash recipe)

**Status:** These are **legacy implementations** being replaced by Python CLI commands. The CLI versions are the current implementation.

Key difference: Bash `wt-merge` includes session.md conflict resolution inline, while Python version delegates to `merge.py` functions.

---

## Architectural Patterns

### 1. **Separation of Concerns**

- **CLI layer** (`cli.py`) — User interaction, argument parsing, worktree setup
- **Merge layer** (`merge.py`) — Complex conflict resolution logic (4 phases)
- **Utilities** (`utils.py`) — Git wrapper, path resolution
- **Validation** (`validation/`) — Modular validators for different file types

### 2. **Worktree Lifecycle**

1. **CREATE:** `new` command → derive slug → focus session → create worktrees (parent + submodule)
2. **WORK:** Agent edits files in worktree
3. **MERGE:** `merge` command → 4 phases (validate, submodule, parent merge, commit + precommit)
4. **REMOVE:** `rm` command → unregister worktrees → delete directory → cleanup container

### 3. **Container Directory Strategy**

Worktrees created in sibling `-wt` container to avoid parent CLAUDE.md injection:
- Main: `/path/to/myproject/`
- Container: `/path/to/myproject-wt/`
- Worktrees: `/path/to/myproject-wt/{slug}/`

Each worktree gets its own `.claude/settings.local.json` for sandbox isolation.

### 4. **Merge Conflict Resolution**

**Auto-resolved conflicts:**
- `agent-core` — Keep ours (already merged in Phase 2)
- `agents/session.md` — Keep ours + extract new tasks from theirs
- `agents/learnings.md` — Keep ours + append theirs-only lines
- `agents/jobs.md` — Keep ours (local plan status is authoritative)

**Unresolved conflicts** → abort merge + clean up → user fixes manually

---

## Gaps and Open Questions

### 1. **Task Name Format Validation (FR-1, FR-2)**

**Gap:** No format constraints on task names. Currently accepts any characters that `derive_slug()` can process.

**Requirements:**
- Constrain to `[a-zA-Z0-9 .\-]` (alphanumeric, space, period, hyphen)
- Max 25 characters
- Remove `max_length` parameter from `derive_slug()` (no truncation)
- Add validator function for format checking
- Integrate into precommit validation

### 2. **Session Merge Multi-line Task Blocks (FR-4)**

**Gap:** `_resolve_session_md_conflict()` extracts single-line tasks only. Multi-line task blocks lose their continuation lines.

**Fix needed:**
- Extract full task blocks (task line + all indented continuation lines)
- Update pattern matching to identify block boundaries
- Preserve indentation when inserting

### 3. **Merge Commit Creation Bug (FR-5)**

**Gap:** `_phase4_merge_commit_and_precommit()` checks `git diff --cached --quiet` → if empty, skips commit → orphans branch.

**Fix:** Always create merge commit after Phase 3 initiates merge, regardless of staged changes.

### 4. **Automated Task Movement (FR-6)**

**Gap:** No automation for moving tasks between Pending Tasks ↔ Worktree Tasks sections.

**Required:**
- `new --task` moves task to Worktree Tasks with `→ <slug>` marker
- `rm` removes task from Worktree Tasks (if completed) or moves back to Pending (if still active)
- Both operations edit main repo's session.md

### 5. **Session File Extraction in focus_session()**

**Issue:** `focus_session()` only captures first line of task. Continuation lines (indented metadata) are lost.

**Related to FR-4:** Fix together when implementing multi-line block extraction.

### 6. **Q-1: Validation Placement**

**Open question from requirements:** Should `derive_slug()` validate task name format and reject invalid names, or should that be precommit's job only?

**Trade-off:**
- **Fail-fast at creation** — Catch issues early, but adds validation logic to every slug derivation
- **Catch at precommit** — Deferred validation, cleaner separation of concerns, but users create worktrees with invalid names first

**Recommendation:** Validate in precommit only. `derive_slug()` is internal utility; task names are validated at boundaries (new command input, session.md parsing).

---

## File Locations Summary

| Component | File | Lines | Purpose |
|-----------|------|-------|---------|
| CLI | `src/claudeutils/worktree/cli.py` | 357 | Commands: new, rm, merge, ls; slug derivation; session focusing |
| Merge logic | `src/claudeutils/worktree/merge.py` | 287 | 4-phase merge: validate, submodule, parent, commit |
| Utilities | `src/claudeutils/worktree/utils.py` | 39 | Git wrapper, worktree path resolution |
| Validation | `src/claudeutils/validation/tasks.py` | 310 | Task name uniqueness, history, format |
| Validation | `src/claudeutils/validation/cli.py` | 145 | Validator entry point, runs all checks |
| Tests | `tests/test_worktree_*.py` | 12 files | E2E tests with real git repos |
| Build | `justfile` | 603 | Precommit recipe, legacy bash worktree commands |

---

## Code Snippets for Design Reference

### Current Task Pattern Matching

```python
# From tasks.py line 16
TASK_PATTERN = re.compile(r"^- \[[ x>]\] \*\*(.+?)\*\* —")
```

Matches: `- [ ] **Task Name** — description`

### Current Session Merge Logic (Simplified)

```python
# From merge.py lines 69-78
ours_tasks = {
    line
    for line in ours_content.split("\n")
    if line.strip().startswith("- [ ] **") and "**" in line
}
theirs_tasks = {
    line
    for line in theirs_content.split("\n")
    if line.strip().startswith("- [ ] **") and "**" in line
}

new_tasks = theirs_tasks - ours_tasks
```

**Issue:** Set diff on full lines loses continuation lines.

### Current Merge Commit Decision (Problematic)

```python
# From merge.py lines 258-260
staged_check = subprocess.run(
    ["git", "diff", "--cached", "--quiet"],
    check=False,
)

if staged_check.returncode != 0:  # Only commits if changes exist
    _git("commit", "-m", f"🔀 Merge {slug}")
```

**Bug:** Skips commit if diff is empty, orphaning branch.

---

## Notes for Design Implementation

1. **Test-First Approach:** Write tests for format validation before implementing. Use parametrized fixtures for valid/invalid task names.

2. **Regex Complexity:** Pattern matching for multi-line task blocks will need multiline mode (`re.DOTALL`) and boundary detection (look for next `##` or end of section).

3. **Backward Compatibility:** Existing task names with underscores, colons, etc. will fail validation. May need migration plan or soft enforcement (warning vs error).

4. **Session File Editing:** Both `new --task` and `rm` will edit the main repo's session.md. Need atomic operations to avoid conflicts (use git staging).

5. **Merge Phase Logic:** The 4-phase structure is solid. Keep the separation and make minimal changes to Phase 4 (always commit) and Phase 3 (improve session extraction).

