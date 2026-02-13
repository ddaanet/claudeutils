# Worktree CLI Implementation Exploration

## Summary

The worktree CLI implementation spans four Python modules: `cli.py` (core commands and utilities), `merge.py` (merge operations), and `utils.py` (helpers). Current implementation supports worktree creation, removal, listing, and merge with session.md conflict resolution. Key functions relevant to the 6 FRs include `derive_slug()` (truncating to 30 chars), `focus_session()` (task filtering), `_resolve_session_md_conflict()` (single-line task extraction), and `_phase4_merge_commit_and_precommit()` (conditional commit). Session.md task movement between Pending and Worktree Tasks sections is not yet automated.

## Key Findings

### 1. `derive_slug()` — Slug Derivation

**File:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/cli.py`
**Lines:** 17–23

```python
def derive_slug(task_name: str, max_length: int = 30) -> str:
    """Task name to slug."""
    if not task_name or not task_name.strip():
        msg = "task_name must not be empty"
        raise ValueError(msg)
    slug = re.sub(r"[^a-z0-9]+", "-", task_name.lower()).strip("-")[:max_length]
    return slug.rstrip("-")
```

**Current Behavior:**
- Converts task name to lowercase
- Replaces any sequence of non-alphanumeric chars with single hyphen
- Truncates to `max_length` (default 30 chars)
- Strips trailing hyphens
- Examples from tests:
  - `"Implement ambient awareness"` → `"implement-ambient-awareness"`
  - `"Review agent-core orphaned revisions"` → `"review-agent-core-orphaned-rev"` (truncated at 30 chars)
  - `"Special!@#$%chars"` → `"special-chars"` (punctuation stripped)
  - `"feat: add login"` → `"feat-add-login"` (colon becomes hyphen)

**Relevance to FR-1:** The function currently accepts any characters in input (via `re.sub` matching `[^a-z0-9]+`) and truncates output. Per FR-1, task names should be constrained to `[a-zA-Z0-9 ]` (letters, digits, spaces only), eliminating need for truncation and making slug derivation near-identity (lowercase + spaces→hyphens).

### 2. `focus_session()` — Task Filtering for Focused Worktrees

**File:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/cli.py`
**Lines:** 50–68

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

**Helper Function:** `_filter_section()` (lines 26–47)
```python
def _filter_section(
    content: str, section_name: str, task_name: str, plan_dir: str | None
) -> str:
    """Filter section entries by task_name or plan_dir match."""
    pattern = rf"## {re.escape(section_name)}\n\n(.*?)(?=\n## |\Z)"
    if not (match := re.search(pattern, content, re.DOTALL)):
        return ""

    def is_relevant(entry: str) -> bool:
        lo = entry.lower()
        return task_name.lower() in lo or bool(plan_dir and plan_dir.lower() in lo)

    lines = []
    include = False
    for line in match.group(1).split("\n"):
        if line.startswith("- "):
            include = is_relevant(line[2:].strip())
            if include:
                lines.append(line)
        elif include and line.strip():
            lines.append(line)
    return f"## {section_name}\n\n" + "\n".join(lines) + "\n" if lines else ""
```

**Current Behavior:**
- Uses `re.escape(task_name)` in regex pattern — handles special characters safely
- Matches task name with `- [ ] **{task_name}** ` prefix
- Extracts plan directory from task metadata (e.g., `Plan: plans/foo/`)
- Filters Blockers/Gotchas and Reference Files sections to only relevant entries
- Returns markdown-formatted focused session

**Relevance to FR-1:** With task name constraints to `[a-zA-Z0-9 ]`, the `re.escape()` call becomes less critical (no special chars to escape), but remains safe. The regex pattern with `**` markers and space-only constraints becomes simpler and more robust.

**Relevance to FR-6:** `focus_session()` is called from the `new` command (line 265) when `--task` flag is used, but does not modify session.md in the main repo—it only generates focused session content for the worktree.

### 3. `_resolve_session_md_conflict()` — Session.md Conflict Resolution

**File:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/merge.py`
**Lines:** 57–104

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

**Current Behavior (Bug):**
- Extracts task lines matching `- [ ] **` pattern (single-line extraction)
- Uses set difference to find new tasks in worktree side
- Problem: Set contains only the main task line, not continuation lines (metadata sub-bullets)
- When new tasks have indented continuation lines (Plan, Status, Notes), those lines are lost
- Inserts only the sorted main lines before next section header

**Example Bug Scenario:**
Worktree task:
```
- [ ] **Task Name** — `/runbook` | sonnet
  - Plan: plans/task/
  - Status: in-progress
```
After merge, becomes (continuation lines lost):
```
- [ ] **Task Name** — `/runbook` | sonnet
```

**Relevance to FR-4:** This is the core issue to fix. Must extract full task blocks (task line + all indented continuation lines) instead of single lines.

### 4. `_phase3_merge_parent()` — Merge Initiation

**File:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/merge.py`
**Lines:** 221–249

```python
def _phase3_merge_parent(slug: str) -> None:
    """Phase 3: Initiate parent merge and auto-resolve known conflicts."""
    result = subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", slug],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return

    conflicts = _git("diff", "--name-only", "--diff-filter=U", check=False).split("\n")
    conflicts = [c for c in conflicts if c.strip()]

    if "agent-core" in conflicts:
        _git("checkout", "--ours", "agent-core")
        _git("add", "agent-core")
        conflicts = [c for c in conflicts if c != "agent-core"]

    conflicts = _resolve_session_md_conflict(conflicts)
    conflicts = _resolve_learnings_md_conflict(conflicts)
    conflicts = _resolve_jobs_md_conflict(conflicts)

    if conflicts:
        _git("merge", "--abort")
        _git("clean", "-fd")
        conflict_list = ", ".join(conflicts)
        click.echo(f"Merge aborted: conflicts in {conflict_list}")
        raise SystemExit(1)
```

**Current Behavior:**
- Initiates merge with `--no-commit --no-ff` flags (does not commit; forces merge commit even if FF possible)
- Catches merge conflicts and runs auto-resolution functions
- If any conflicts remain after auto-resolution, aborts merge and exits with error
- Returns early if merge succeeds without conflicts (merge is staged, not committed)

**Relevance to FR-5:** This function initiates the merge but does not create the commit. See Phase 4 below.

### 5. `_phase4_merge_commit_and_precommit()` — Merge Commit Creation

**File:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/merge.py`
**Lines:** 252–278

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

**Current Behavior (Bug):**
- Checks `git diff --cached --quiet` (exit code 0 = no staged changes, nonzero = staged changes)
- Only commits if `staged_check.returncode != 0` (i.e., if there ARE changes)
- Problem: When session.md conflict resolves to no net changes (or any merge that nullifies diff), staged check returns 0 and commit is skipped
- Result: Merge initiated but not committed → branch remains unmerged → `git branch -d` rejects branch as "not fully merged"

**Relevance to FR-5:** This is the core bug. When merge is initiated with `--no-commit`, the merge must always be committed, even if diff is empty. Current code skips commit on empty diff, orphaning the branch.

### 6. `new` Command — Worktree Creation

**File:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/cli.py`
**Lines:** 248–274

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
        raise click.UsageError("slug and --task are mutually exclusive")  # noqa: TRY003
    if not task and not slug:
        raise click.UsageError("either slug or --task is required")  # noqa: TRY003
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

**Signature and Options:**
- `slug` (optional positional): Branch/worktree name. If not provided, `--task` must be used
- `--base` (default="HEAD"): Base commit for new branch
- `--session` (default=""): Path to session.md file to commit on new branch
- `--task` (default=""): Task name from session.md; slug derived from name
- `--session-md` (default="agents/session.md"): Path to source session.md for task extraction

**Current Behavior:**
- If `--task`: derives slug, generates focused session, creates worktree
- If explicit slug: uses provided slug, creates worktree
- Does not modify session.md in main repo to move task to Worktree Tasks section

**Relevance to FR-6:** The command creates the worktree but does not move the task from Pending Tasks to Worktree Tasks. This is currently manual work in the skill (worktree/SKILL.md Mode A step 4, Mode C step 3).

### 7. `rm` Command — Worktree Removal

**File:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/cli.py`
**Lines:** 325–356

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

**Current Behavior:**
- Probes worktree registration status
- Removes worktrees (submodule first if registered, then parent)
- Attempts safe branch deletion with `git branch -d`
- Cleans up worktree and empty container directories
- Does not modify session.md to remove task from Worktree Tasks section

**Relevance to FR-6:** The command removes worktrees but does not remove the corresponding task entry from session.md Worktree Tasks section. This is currently manual work in the skill.

### 8. Session.md Task Movement Functions

**Not Yet Implemented:**

The codebase lacks functions to:
1. Move tasks from "Pending Tasks" to "Worktree Tasks" section with `→ <slug>` marker
2. Remove tasks from "Worktree Tasks" section

These would be needed for FR-6 automation. Current code pattern (from `_resolve_session_md_conflict`) shows how to parse sections and manipulate task entries, but dedicated functions don't exist.

### 9. Helper Functions

**`_git()` — Git command wrapper**
- **File:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/utils.py` (lines 7–21)
- Runs git commands, captures output, strips whitespace
- Accepts optional `check`, `env`, `input_data` parameters
- Used throughout for all git operations

**`wt_path()` — Worktree path resolution**
- **File:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/utils.py` (lines 24–38)
- Returns worktree path in sibling `-wt` container
- Detects if already in container (parent name ends with `-wt`)
- Optionally creates container directory
- Raises ValueError for empty/whitespace slugs

**`_setup_worktree()` — Worktree setup orchestration**
- **File:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/cli.py` (lines 211–224)
- Creates parent and submodule worktrees
- Registers container in sandbox settings
- Initializes environment (runs `just setup` if available)

**`_create_parent_worktree()` — Parent worktree creation**
- **File:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/cli.py` (lines 165–184)
- Creates or reuses branch
- Optionally commits focused session as first commit
- Uses `-b` flag for new branches, reuses existing if branch exists

**`_create_submodule_worktree()` — Submodule worktree creation**
- **File:** `/Users/david/code/claudeutils-wt/worktree-fixes/src/claudeutils/worktree/cli.py` (lines 187–208)
- Creates worktree in agent-core submodule
- Checks for branch existence, uses `-b` flag if branch doesn't exist
- Silently skips if agent-core is not a git repo

### 10. Conflict Resolution Helpers

**`_resolve_learnings_md_conflict()`** (lines 107–131 in merge.py)
- Keeps ours, appends theirs-only content
- Set-based diff of lines

**`_resolve_jobs_md_conflict()`** (lines 134–147 in merge.py)
- Keeps ours (local plan status is authoritative)
- Uses `git checkout --ours`

**`_check_clean_for_merge()`** (lines 11–54 in merge.py)
- Validates clean tree for merge operations
- Accepts exempt paths for session/jobs/learnings files
- Checks parent and submodule separately

## Patterns and Conventions

### Task Name Pattern Matching
- Format: `- [ ] **{task_name}** {metadata}`
- Matched by functions using `re.escape(task_name)` for safety
- Continuation lines: indented (start with spaces), not bullet points

### Merge Phase Architecture
- Phase 1: Validate clean trees
- Phase 2: Resolve submodule (already merged by this point)
- Phase 3: Initiate parent merge, auto-resolve known conflicts
- Phase 4: Create merge commit, run precommit

### Git Configuration Modes
- Worktrees created in sibling `-wt` container (e.g., `my-repo-wt/feature-branch/`)
- Sandbox registration in both main and worktree `.claude/settings.local.json`
- Submodule worktrees share object store (not separate clones with `--reference`)

## Current Gaps vs. FR Requirements

| FR | Status | Gap |
|----|--------|-----|
| FR-1 | Partial | `derive_slug()` has `max_length` parameter, accepts any chars. Need: remove truncation, validate input. |
| FR-2 | Not implemented | Precommit validation for task name format not in codebase. |
| FR-3 | Not implemented | Migration script not present. |
| FR-4 | Buggy | `_resolve_session_md_conflict()` extracts single lines, loses continuation lines. Need: extract full task blocks. |
| FR-5 | Buggy | `_phase4_merge_commit_and_precommit()` skips commit on empty diff. Need: always commit after merge initiated. |
| FR-6 | Not implemented | No functions to move tasks between sections or edit session.md. `new` and `rm` don't modify main repo session.md. |

## Test Coverage

The project has comprehensive tests for:
- `derive_slug()` with various inputs and edge cases (test_worktree_utils.py:14–32)
- `focus_session()` task extraction and section filtering (test_worktree_utils.py:163–220)
- `_resolve_session_md_conflict()` with single-line tasks (test_worktree_merge_conflicts.py:132–259)
- `_phase4_merge_commit_and_precommit()` merge validation (test_worktree_merge_validation.py)
- Worktree creation, listing, and removal (test_worktree_commands.py)

Tests currently validate *existing behavior*, which contains the bugs noted above. Tests would need updates when FRs are implemented to validate corrected behavior (e.g., full task block extraction for FR-4, unconditional commit for FR-5).
