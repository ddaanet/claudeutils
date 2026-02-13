# Worktree Fixes — Design

## Problem

Five worktree bugs/gaps: lossy slug derivation, no task name format validation, single-line session merge losing continuation lines, orphaned branches from skipped merge commits, and manual session.md task movement that should be automated.

## Requirements

**Source:** `plans/worktree-fixes/requirements.md`

- FR-1: Task name constraints (`[a-zA-Z0-9 .\-]`, max 25 chars, lossless slugs) — addressed by validation function + derive_slug changes
- FR-2: Precommit task name validation — addressed by format check in existing validator
- FR-4: Session merge preserves full task blocks — addressed by shared task-block parser
- FR-5: Merge commit always created — addressed by MERGE_HEAD detection
- FR-6: Automate session.md task movement — addressed by CLI automation in new/rm commands

**Out of scope:** Mode B parallel group changes, learnings.md/jobs.md merge changes, slug format changes, task autocomplete.

## Architecture

### New Module: `src/claudeutils/worktree/session.py`

Central infrastructure shared by FR-4 (merge) and FR-6 (automation). All session.md parsing and editing lives here.

**Data model:**

```python
@dataclass
class TaskBlock:
    name: str          # "Fix session merge"
    lines: list[str]   # all lines (task line + continuation)
    section: str       # "Pending Tasks" | "Worktree Tasks"
```

**Functions:**

`extract_task_blocks(content: str, section: str | None = None) -> list[TaskBlock]`
- Parse content into TaskBlock instances
- Task line: matches `^- \[[ x>]\] \*\*(.+?)\*\*`
- Continuation lines: immediately following lines with leading whitespace (spaces or tabs)
- Block boundary: next task line, next `## ` header, or EOF
- Optional section filter restricts to named section only

`find_section_bounds(content: str, header: str) -> tuple[int, int] | None`
- Returns (start_line, end_line) for section with given `## header`
- end_line is the line before next `## ` header or EOF
- Returns None if section not found

`move_task_to_worktree(session_path: Path, task_name: str, slug: str) -> None`
- Extract task block from Pending Tasks by name
- Append `→ \`{slug}\`` to first line of block
- Insert into Worktree Tasks section (create section if missing, after Pending Tasks)
- Remove original block from Pending Tasks
- Write back atomically

`remove_worktree_task(session_path: Path, slug: str, worktree_branch: str) -> None`
- Find task in Worktree Tasks by `→ \`{slug}\`` marker
- Extract task name from that entry
- Check worktree branch state: `git show {worktree_branch}:agents/session.md`
- If task name NOT in worktree branch's Pending Tasks → task was completed → remove entry from Worktree Tasks
- If task name still in worktree branch's Pending Tasks → keep entry (task incomplete)
- Idempotent: no-op if slug not found in Worktree Tasks

**Why check branch, not merged result:** After merge, the main session.md has Worktree Tasks from "ours" side (unchanged). The worktree branch still exists at `rm` time (deleted later). Reading the branch's session.md gives ground truth about whether the agent completed the task.

**Sequence constraint for `rm`:** Check worktree branch state BEFORE `git branch -d`. Current `rm` deletes branch early — reorder to: check → edit session.md → delete branch → cleanup.

### Changes to Existing Modules

#### `src/claudeutils/worktree/cli.py`

**`derive_slug(task_name: str) -> str`** (was `derive_slug(task_name, max_length=30)`)
- Remove `max_length` parameter
- Call `validate_task_name_format(task_name)` before transformation (fail-fast, raises ValueError if invalid)
- Transformation: `task_name.lower()` then `re.sub(r"[^a-z0-9]+", "-", ...).strip("-")`
- No truncation — constrained names produce short slugs
- Lossless: spaces/dots/sequences become single hyphens, but names are short enough that this is unambiguous

**`new` command:**
- After `_setup_worktree()` succeeds, call `move_task_to_worktree(session_md_path, task_name, slug)`
- `session_md_path` is the main repo's session.md (not worktree copy)
- Only when `--task` flag is provided (slug-only mode doesn't touch session.md)

**`rm` command:**
- Reorder operations: probe registrations → check worktree task state → edit session.md → remove worktrees → delete branch → cleanup
- Call `remove_worktree_task(session_md_path, slug, slug)` (branch name = slug)
- Must happen before `git branch -d` (needs branch to exist for `git show`)

**`focus_session()` (Phase 1 — uses `extract_task_blocks()` from session.py):**
- Replace single-line regex with `extract_task_blocks()` from session.py
- Reconstruct focused session with full task block (all continuation lines)
- Constrained task names simplify pattern matching (no complex escaping needed)

#### `src/claudeutils/worktree/merge.py`

**`_resolve_session_md_conflict()`:**
- Replace single-line set diff with `extract_task_blocks()`
- Use `find_section_bounds()` to locate insertion point for new blocks
- Compare by task name (not full line text)
- Insert full blocks (all lines) for new tasks from worktree side
- Blank line separation before next section header

Current (buggy):
```python
ours_tasks = {line for line in content.split("\n") if line.startswith("- [ ] **")}
new_tasks = theirs_tasks - ours_tasks  # loses continuation lines
```

Fixed:
```python
ours_blocks = extract_task_blocks(ours_content, section="Pending Tasks")
theirs_blocks = extract_task_blocks(theirs_content, section="Pending Tasks")
ours_names = {b.name for b in ours_blocks}
new_blocks = [b for b in theirs_blocks if b.name not in ours_names]
# Insert full blocks (all lines) before next section
```

**`_phase4_merge_commit_and_precommit(slug)`:**
- Replace `git diff --cached --quiet` check with MERGE_HEAD detection
- `git rev-parse --verify MERGE_HEAD` (exit 0 = merge in progress)
- When MERGE_HEAD present: always commit with `--allow-empty` flag
- When no MERGE_HEAD: existing behavior (only commit if staged changes)
- `--allow-empty` handles the case where conflict resolution nullifies all changes

```python
merge_in_progress = subprocess.run(
    ["git", "rev-parse", "--verify", "MERGE_HEAD"],
    capture_output=True, check=False,
).returncode == 0

if merge_in_progress:
    _git("commit", "--allow-empty", "-m", f"🔀 Merge {slug}")
elif subprocess.run(["git", "diff", "--cached", "--quiet"], check=False).returncode != 0:
    _git("commit", "-m", f"🔀 Merge {slug}")
```

#### `src/claudeutils/validation/tasks.py`

**Add `validate_task_name_format(name: str) -> list[str]`:**
- Check character set: `re.fullmatch(r"[a-zA-Z0-9 .\-]+", name)` — reject if no match
- Check length: `len(name) <= 25`
- Check not empty/whitespace-only
- Returns list of error strings (empty = valid)

**Integrate into existing `validate()` function:**
- After extracting task names, call `validate_task_name_format()` on each
- Format errors reported with line number and offending character
- Runs alongside existing uniqueness/disjointness checks

**Error message format:** `"Task '{name}' (line {n}): contains forbidden character '{char}'"` or `"Task '{name}' (line {n}): exceeds 25 character limit ({len} chars)"`

### Key Design Decisions

**1. TaskBlock as lines, not parsed fields.**
Task blocks contain arbitrary metadata in continuation lines. Parsing them into structured fields adds complexity with no benefit — merge and movement just need to copy blocks intact. Only the task name is extracted for matching.

**2. Section-aware extraction.**
`extract_task_blocks()` accepts an optional section filter because the same task name can appear in both Pending Tasks and Worktree Tasks (during transitions). Callers specify which section they're operating on.

**3. Branch check for rm, not merge-result check.**
At `rm` time, the merged session.md has Worktree Tasks from "ours" side (unchanged by merge resolution). Checking the worktree branch (`git show branch:agents/session.md`) gives the actual worktree state. This avoids coupling `rm` behavior to merge resolution internals.

**4. `--allow-empty` for merge commits.**
Standard git behavior: `git merge --no-commit --no-ff` sets MERGE_HEAD but may result in no staged changes after conflict resolution. `git commit --allow-empty` creates the merge commit regardless, making the branch an ancestor of HEAD so `git branch -d` succeeds.

**5. Validation in derive_slug AND precommit.**
`derive_slug()` is called at worktree creation time — fail-fast catches bad names before creating git branches. Precommit catches names written directly to session.md by agents (manual edits bypass derive_slug). Defense in depth.

**6. Shared `validate_task_name_format()` function.**
Both `derive_slug()` (fail-fast) and precommit validator call the same function. Single source of truth for format rules.

## Phase Structure

| Phase | FRs | Type | Files Changed |
|-------|-----|------|---------------|
| 0: Task name constraints | FR-1, FR-2 | TDD | `cli.py`, `validation/tasks.py`, tests |
| 1: Merge fixes | FR-4, FR-5 | TDD | `merge.py`, `cli.py` (focus_session), NEW `session.py`, tests |
| 2: Session automation | FR-6 | TDD | `cli.py`, `session.py`, tests |
| 3: Skill update | — | General | `SKILL.md` |

**Phase 0** establishes validation infrastructure. `derive_slug()` becomes lossless with format validation. Precommit gains format checking.

**Phase 1** creates shared `session.py` module with `extract_task_blocks()` and `find_section_bounds()`. Fixes `_resolve_session_md_conflict()` to use full blocks (uses `find_section_bounds()` for insertion point). Fixes `_phase4` with MERGE_HEAD detection. Updates `focus_session()` to use `extract_task_blocks()`.

**Phase 2** adds `move_task_to_worktree()` and `remove_worktree_task()` to session.py. Wires into `new --task` and `rm` commands. Reorders `rm` to check branch before deletion.

**Phase 3** updates SKILL.md: removes session.md editing from Mode A step 4 and Mode B step 4 (now automated by `new --task`). Simplifies Mode C step 3 to remove manual session.md editing (now automated by `rm`). Documents that CLI handles task movement automatically.

## Testing Strategy

All TDD phases use E2E tests with real git repos via `tmp_path` fixtures, matching existing test patterns.

**Phase 0 tests (`test_validation_tasks.py`, `test_worktree_cli.py`):**
- Parametrized valid/invalid task names for `validate_task_name_format()`
- `derive_slug()` lossless round-trip: valid names → slug → verify no truncation
- `derive_slug()` rejects invalid names (ValueError)
- Precommit integration: session.md with invalid names → validation errors

**Phase 1 tests (`test_worktree_session.py`, `test_worktree_merge_conflicts.py`, `test_worktree_merge_parent.py`):**
- `extract_task_blocks()`: single-line tasks, multi-line tasks, mixed sections (in `test_worktree_session.py`)
- `_resolve_session_md_conflict()`: merge with multi-line task blocks preserved (in `test_worktree_merge_conflicts.py`)
- `_phase4`: empty-diff merge still creates commit (MERGE_HEAD detection) (in `test_worktree_merge_parent.py`)
- `git branch -d` succeeds after empty-diff merge

**Phase 2 tests (`test_worktree_session.py`, `test_worktree_cli.py`):**
- `move_task_to_worktree()`: moves block, creates section if missing, idempotent
- `remove_worktree_task()`: removes when task completed, keeps when still pending
- `new --task` E2E: session.md updated after worktree creation
- `rm` E2E: session.md updated conditionally after merge

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agents/decisions/testing.md` — TDD patterns, E2E approach
- `plans/worktree-fixes/reports/explore-worktree-code.md` — Current code structure, function signatures, test patterns

**No plugin-dev skills needed.** This design modifies only Python code and one skill file (prose edit in Phase 3).

**No external library research needed.** All changes use standard library (re, pathlib, subprocess, dataclasses).

## Next Steps

1. `/runbook plans/worktree-fixes/design.md` — generate execution runbook
2. Execution model: sonnet for all phases (no architectural decisions remaining)
