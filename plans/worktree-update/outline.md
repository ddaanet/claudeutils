# Worktree Update: Outline

## Problem

The worktree skill references `claudeutils _worktree` Python CLI commands that are stale relative to the justfile prototype:

**Stale Python CLI behavior:**
- `new` uses `wt/<slug>` paths (inside repo) instead of sibling `<repo>-wt/<slug>`
- `new` uses `--reference` submodule clone instead of worktree-based submodule
- `new` missing sandbox permission registration for container directory
- `new` missing existing branch reuse support
- `merge` command doesn't exist at all (entire 3-phase ceremony missing)
- `rm` uses `-D` (force delete) instead of `-d` with fallback warning
- `rm` doesn't handle submodule worktree removal ordering
- No `focus-session` command — skill generates session content inline (cognitive work that should be scripted)

**Correct behavior (justfile prototype):**
- Sibling directory paths: `<repo>-wt/<slug>` (Claude Code isolation from parent CLAUDE.md)
- Worktree-based submodule: `git -C agent-core worktree add` (shared object store, bidirectional visibility)
- Sandbox permission registration: container added to settings.local.json
- Submodule removal ordering: submodule worktree removed first (git refuses parent removal while submodule exists)
- Existing branch reuse: `git worktree add <path> <branch>` if branch exists
- Graceful branch deletion: `-d` with fallback to warning if unmerged

## Approach

Refactor Python worktree modules into functions that serve the skill. The skill is the primary interface; justfile recipes are fallback for interactive use.

### Architecture

**Modules** (`src/claudeutils/worktree/`): Pure functions implementing worktree logic.
- `wt_path(slug)` → path computation (sibling container detection)
- `add_sandbox_dir(container, settings_path)` → sandbox permission registration
- `create_worktree(slug, base, session_path)` → full creation (branch, submodule worktree, sandbox, env init)
- `remove_worktree(slug)` → full removal (submodule-first ordering, container cleanup, branch)
- `merge_worktree(slug)` → 4-phase merge ceremony
- `focus_session(task_name, session_md_path)` → generate focused session content (reads file, returns string)
- `derive_slug(task_name)` → slug derivation (single implementation, no duplication)
- `list_worktrees()` → list active worktrees

Note: Most functions already exist in cli.py but need refactoring: extract logic into functions, leave CLI commands as thin wrappers.

**CLI** (`src/claudeutils/worktree/cli.py`): Click group `_worktree` wrapping the functions.
- `_` prefix → hidden from `claudeutils --help`
- Used by: skill (primary), justfile recipes (may call for shared operations like `ls`)
- Already partially exists, needs major updates and registration in main `cli.py`

**Skill** (`agent-core/skills/worktree/SKILL.md`): Primary user interface.
- Invokes `claudeutils _worktree` commands
- Handles cognitive work: task identification, session context filtering, conflict resolution decisions
- allowed-tools: `Bash(claudeutils _worktree:*)`

**Justfile recipes**: Interactive fallback.
- Bash implementation with colored output, `visible()` helpers
- Recipes may call `claudeutils _worktree` for shared operations (e.g., `wt-ls` already does)
- Not modified in this plan — just kept working as-is

### Script changes (Python CLI)

**Update `new` command:**
- **Path computation:** Port `wt-path()` bash function logic:
  - Parent directory detection: `Path.cwd().parent.name.endswith('-wt')`
  - If in `-wt` container: sibling path `parent/<slug>`
  - If NOT in container: create container `<repo-name>-wt/` and use `<container>/<slug>`
  - Container creation: `mkdir -p` for container directory
  - Extract repo name: `Path.cwd().name` for container naming
- **Existing branch detection:** Check `git rev-parse --verify <slug>` before creating branch
  - If branch exists: `git worktree add <path> <branch>` (no `-b` flag)
  - If branch doesn't exist: existing behavior with `-b` flag (or session commit flow)
  - Session file handling: warn and ignore `--session` if branch exists (branch reuse means session already committed)
- **Submodule worktree creation:** Replace `submodule update --init --reference` with worktree-based approach:
  - Check if submodule exists in parent: `Path('agent-core/.git').exists()`
  - Check if submodule branch exists: `git -C agent-core rev-parse --verify <slug>`
  - If submodule branch exists: `git -C agent-core worktree add <path>/agent-core <slug>` (no `-b`)
  - If submodule branch doesn't exist: `git -C agent-core worktree add <path>/agent-core -b <slug>`
  - Remove `--reference` logic entirely (worktree shares object store inherently)
  - Remove `checkout -B <slug>` step (worktree add already checks out the branch)
- **Sandbox registration:** Port `add-sandbox-dir()` function:
  - Determine container directory (absolute path to `<repo-name>-wt/`)
  - Read `.claude/settings.local.json` (create if missing with `{}`)
  - Add container path to `permissions.additionalDirectories` array (create key if missing, dedup if already present)
  - Write both main and worktree settings files: `.claude/settings.local.json` and `<wt-path>/.claude/settings.local.json`
  - JSON parsing: use `json.load()` / `json.dump()` with indent=2 for readability
- **Environment initialization:** Run `just setup` in worktree after creation.
  - Check for just availability: `subprocess.run(['just', '--version'], ...)` first
  - If `just setup` unavailable: print warning, do NOT fall back to manual commands
  - Prerequisite: add `setup` recipe to agent-core justfile (currently only in parent)
  - All commands run with `cwd=<wt-path>` subprocess parameter
- **Output:** Print actual worktree path (absolute) for caller to capture

**Update `rm` command:**
- **Path resolution:** Use same `wt_path()` logic as `new` to find worktree path from slug
- **Uncommitted changes warning:** Check `git -C <wt-path> status --porcelain` before removal (if path exists), print warning if dirty
- **Worktree registration probing:**
  - Parse `git worktree list --porcelain` to check if `<wt-path>` is registered
  - Parse `git -C agent-core worktree list --porcelain` to check if `<wt-path>/agent-core` is registered
  - Use path matching, not grep (more reliable parsing)
- **Removal ordering (critical):**
  1. Remove submodule worktree FIRST: `git -C agent-core worktree remove --force <path>/agent-core` (if registered)
  2. Remove parent worktree SECOND: `git worktree remove --force <path>` (if registered)
  3. Rationale: git refuses parent removal while submodule worktree exists
- **Directory cleanup:** If `<wt-path>` still exists after git commands (orphaned), use `shutil.rmtree()`
- **Container cleanup:** Check if container directory is empty (`os.listdir()` returns empty list), remove with `os.rmdir()`
- **Branch deletion:** Use `-d` flag (safe delete, checks merge status):
  - Command: `git branch -d <slug>`
  - If fails with unmerged status: print warning "Branch <slug> has unmerged changes. Use: git branch -D <slug>"
  - Do NOT auto-force-delete with `-D`
- **Graceful degradation:** Handle case where worktree directory doesn't exist but branch does (prune stale registration, then delete branch)

**Add `merge` command (new):**

Implement 4-phase merge ceremony from justfile:

**Phase 1: Pre-checks**
- Clean tree validation (exempt session files):
  - Use `claudeutils _worktree clean-tree` command (already implements exemption logic)
  - Exit 1 if dirty with message: "Clean tree required for merge"
- Branch existence: verify `git rev-parse --verify <slug>` succeeds, exit 2 if not found
- Worktree directory check: warn if `<wt-path>` doesn't exist but continue (branch-only merge valid)

**Phase 2: Submodule Resolution**
- Extract worktree's submodule commit: `git ls-tree <branch> -- agent-core | awk '{print $3}'`
- Compare to local: `git -C agent-core rev-parse HEAD`
- If commits differ:
  - Check ancestry: `git -C agent-core merge-base --is-ancestor <wt-commit> <local-commit>`
  - If not ancestor (need merge):
    - Fetch if unreachable: `git -C agent-core cat-file -e <wt-commit>` → if fails, `git -C agent-core fetch <wt-path>/agent-core HEAD`
    - Merge: `git -C agent-core merge --no-edit <wt-commit>`
    - Stage: `git add agent-core`
    - Commit: `git commit -m "🔀 Merge agent-core from <slug>"` (only if staged changes exist)

**Phase 3: Parent Merge with Auto-Resolution**
- Initiate merge: `git merge --no-commit --no-ff <branch>` (capture both stdout and stderr)
- If conflicts occur (exit code ≠ 0):
  - Get conflict list: `git diff --name-only --diff-filter=U`
  - **agent-core conflict:** `git checkout --ours agent-core && git add agent-core` (already merged in Phase 2)
  - **agents/session.md conflict:**
    - Extract new tasks from theirs: parse for `- [ ] **<name>**` patterns in `:3:agents/session.md`
    - Keep ours: `git checkout --ours agents/session.md && git add agents/session.md`
    - Print warning with new task list for manual extraction (manual work, cognitive decision)
  - **agents/learnings.md conflict:** Keep both — append theirs-only content to ours:
    - Extract ours content: `git show :2:agents/learnings.md`
    - Extract theirs content: `git show :3:agents/learnings.md`
    - Find theirs-only lines (lines in :3 not in :2), append to ours
    - Write merged result, `git add agents/learnings.md`
  - **agents/jobs.md conflict:** Keep ours with warning: `git checkout --ours agents/jobs.md && git add agents/jobs.md`
  - **Source file conflicts:** Abort merge. Exit 1 with conflict list. Skill handles resolution manually.
    - Do NOT auto-resolve source files with take-ours
    - Print conflicted file list for skill/agent to resolve
    - Abort: `git merge --abort`, clean debris: `git clean -fd`
  - Verify all resolved: check `git diff --name-only --diff-filter=U` is empty
  - If conflicts remain (shouldn't happen after auto-resolution): `git merge --abort`, `git clean -fd`, exit 1 with message
- Commit merge: `git commit -m "🔀 Merge <slug>"` (only if staged changes exist)

**Phase 4: Precommit Validation**
- Run: `just precommit` (capture exit code and output)
- If fails (exit ≠ 0): exit 1 with message "Precommit failed after merge" + stderr
- Success message if passes

**Exit codes:**
- 0: Success (all phases complete, precommit passed)
- 1: Conflicts unresolved OR precommit failure (caller must fix and retry)
- 2: Fatal error (branch not found, submodule failure)

**Add `focus-session` command (new):**

Generate focused session.md content for a worktree. Replaces the inline generation currently done by the skill (Mode A steps 3-4) and the justfile `wt-task` recipe.

- **Input:** task name + path to source session.md
- **Output:** Focused session content to stdout
- **Logic:**
  - Parse session.md to extract:
    - Task block matching task name (full metadata, continuation lines)
    - Blockers/Gotchas section entries mentioning the task or its plan directory
    - Reference Files entries relevant to the task
  - Generate focused session with:
    - H1: "Session: Worktree — <task name>"
    - Status: "Focused worktree for parallel execution."
    - Pending Tasks: single extracted task
    - Blockers/Gotchas: relevant entries only
    - Reference Files: relevant entries only
- **Relation to wt-task recipe:** The recipe currently does simple `grep -A5` extraction. `focus-session` replaces this with proper parsing (relevant blockers, references). Recipe can be updated to call this command.
- **CLI signature:** `claudeutils _worktree focus-session "<task-name>" <session-md-path>` with output to stdout

**Keep as-is:** `ls`, `clean-tree`, `add-commit`

**Register CLI:** Add `_worktree` group to main `cli.py`.
- Import: `from claudeutils.worktree.cli import worktree`
- Registration: `cli.add_command(worktree)` in main CLI group
- `_` prefix means hidden from `claudeutils --help` output
- Agent implementation detail, not user-facing

### Skill changes

**Mode A (Single Task) updates:**
- **Step 2 (slug):** Remove inline derivation logic. Call `claudeutils _worktree derive-slug "<task name>"` — single implementation, no duplication.
- **Steps 3-4 (session generation):** Replace inline generation with `claudeutils _worktree focus-session "<task name>" agents/session.md > tmp/wt-<slug>-session.md`
- **Step 5 (creation):** Invoke `claudeutils _worktree new <slug> --session tmp/wt-<slug>-session.md`. CLI now outputs actual sibling path. Capture output to variable for next step.
- **Step 6 (session.md marker):** Update from `→ wt/<slug>` to `→ <slug>`. The slug is the stable identifier; actual path discoverable via `claudeutils _worktree ls`.
- **Step 7 (launch command):** Use actual path from `new` command output: `cd <actual-sibling-path> && claude    # <task-name>` (with comment for clarity)

**Mode B (Parallel Group) updates:**
- **Step 4:** Uses updated Mode A steps (focus-session, new commands) for each task in the group
- **Step 5:** Launch commands use actual sibling paths from `new` output, print consolidated list with instructions

**Mode C (Merge Ceremony) updates:**
- **Step 2:** Invoke `claudeutils _worktree merge <slug>` (command now exists)
- **Step 3 cleanup:** Invoke `claudeutils _worktree rm <slug>` (now uses improved removal logic)
- **Step 4 (source conflicts):** Merge exits 1 with conflict list. Skill resolves source conflicts manually (cognitive work), then re-runs merge.

**Frontmatter updates:**
- `allowed-tools`: Keep `Bash(claudeutils _worktree:*)` (underscore prefix preserved)

### Execute-rule.md marker convention

**IN scope.** The Worktree Tasks section format changes:

Before: `- [ ] **Task Name** → `wt/<slug>` — metadata`
After: `- [ ] **Task Name** → `<slug>` — metadata`

The slug is the stable key for all operations (`merge <slug>`, `rm <slug>`). The actual filesystem path is a sibling directory discoverable via `claudeutils _worktree ls`. No need to embed the path in session.md.

Update in `agent-core/fragments/execute-rule.md`:
- Worktree Tasks section format (remove `wt/` prefix in marker)
- Status display (#status command) to show slug only, not full path

### Settings.json permission patterns

**IN scope** (already part of sandbox registration in `new` command). Clarification:

- `add_sandbox_dir()` writes to `.claude/settings.local.json` (gitignored, per-machine)
- Registers container directory in `permissions.additionalDirectories`
- Written to both main repo and worktree settings files
- `rm` does NOT clean up sandbox entries (harmless stale entries, no cleanup needed)

### Justfile recipes

**Kept as fallback.** Recipes remain working bash implementations for interactive use.

**Rationale:**
- Colored output (`visible()`, `fail()`, `show()`) for terminal UX
- User can invoke directly when skill unavailable (no Claude session)
- Independent implementation — no coupling to Python CLI
- Skill is the primary interface; recipes are the escape hatch

**No changes to justfile** in this plan except: add `setup` recipe to agent-core justfile.

### Test updates

**Update `test_worktree_new.py`:**
- Verify sibling path creation: assert worktree at `<container>/<slug>` not `wt/<slug>`
- Verify container directory created if not in `-wt` parent
- Verify worktree-based submodule: check `git -C agent-core worktree list` includes new path
- Verify sandbox registration: assert `settings.local.json` contains container in `additionalDirectories`
- Verify existing branch reuse: create branch first, assert no error, worktree uses existing branch
- Verify env init: assert `just setup` invoked with `cwd=<wt-path>`, warning if missing

**Update `test_worktree_rm.py`:**
- Verify removal ordering: assert submodule worktree removed before parent
- Verify container cleanup: assert empty container directory removed
- Verify branch deletion: assert `git branch -d` (not `-D`), capture warning for unmerged
- Verify graceful degradation: removal when only branch exists (no directory)

**Add `test_worktree_merge.py` (new file):**
- Phase 1: Clean tree enforcement (uses clean-tree command, exempt session files, fail on dirty source)
- Phase 2: Submodule resolution (ancestry check, merge when needed, skip when ancestor)
- Phase 3: Conflict handling — session files auto-resolve, source files exit 1
- Phase 3 learnings: verify theirs-only content appended to ours
- Phase 4: Precommit validation gate (exit 1 on failure, guidance printed)
- Exit codes: 0 (success), 1 (conflicts/precommit), 2 (fatal)
- Idempotency: re-running after manual fix resumes correctly
- Source file conflict abort: verify merge aborted and working tree cleaned

**Add `test_focus_session.py` (new file):**
- Task extraction from session.md
- Relevant blockers filtering
- Relevant reference files filtering
- Missing task error handling

## Key Decisions

**D1. Path computation:** Port `wt-path()` to Python `wt_path(slug)` function.
- Container detection: `Path.cwd().parent.name.endswith('-wt')`
- Sibling path construction: `parent/<slug>` or `<repo-name>-wt/<slug>`
- Shared across `new`, `rm`, `merge` commands

**D2. Submodule approach:** Worktree-based (not `--reference` clone).
- `git -C agent-core worktree add` shares object store inherently
- Bidirectional commit visibility (no fetch needed in most merges)
- Removal requires submodule-first ordering

**D3. Skill is primary, recipes are fallback.**
- Skill invokes Python CLI (`claudeutils _worktree`) — primary interface
- Justfile recipes — independent bash implementation for interactive fallback
- Not parallel implementations serving different audiences; skill is the designed workflow

**D4. Single implementation for shared logic.**
- Slug derivation: `derive_slug()` in Python, skill calls CLI — no inline duplication
- Session generation: `focus_session()` in Python, skill calls CLI — no inline steps 3-4
- Path computation: `wt_path()` in Python — single source of truth

**D5. Environment init: warn only.**
- Run `just setup` in worktree. If recipe missing: warn, do not fall back.
- Prerequisite: add `setup` recipe to agent-core justfile.

**D6. CLI hidden from user help.**
- `_worktree` prefix → not shown in `claudeutils --help`
- Agent implementation detail, invoked by skill and recipes
- Register in main `cli.py` for discoverability by code (import path works)

## Scope

**IN:**
- Python modules: `src/claudeutils/worktree/` (refactor into functions + CLI wrapper)
- Main CLI registration: `src/claudeutils/cli.py` (add `_worktree` group)
- Skill: `agent-core/skills/worktree/SKILL.md` (invocations, frontmatter, remove inline logic)
- Execute-rule: `agent-core/fragments/execute-rule.md` (Worktree Tasks marker format)
- Agent-core setup: add `setup` recipe to `agent-core/justfile`
- Tests: `test_worktree_new.py`, `test_worktree_rm.py`, `test_worktree_merge.py` (new), `test_focus_session.py` (new)
- `focus-session` command: focused session generation for worktree creation

**OUT:**
- Justfile recipe changes (kept as-is, independent fallback)
- Settings.json user-level patterns (only settings.local.json sandbox registration, already in scope)

## Implementation Sequence

1. Refactor existing CLI: extract logic from commands into helper functions (`wt_path()`, etc.)
2. Add `add_sandbox_dir()` helper function (new)
3. Add `focus_session()` function + `focus-session` CLI command + `derive-slug` CLI command
4. Update `new` command (sibling paths, worktree submodule, sandbox, env init, branch reuse)
5. Update `rm` command (submodule-first ordering, container cleanup, `-d`, graceful degradation)
6. Add `merge` command (4-phase ceremony, auto-resolution, exit codes)
7. Register `_worktree` group in main CLI (`src/claudeutils/cli.py`)
8. Add `setup` recipe to agent-core justfile
9. Update skill (remove inline logic, call CLI commands, update markers, update launch commands)
10. Update execute-rule.md marker convention (slug-only format)
11. Update existing tests (`test_worktree_new.py`, `test_worktree_rm.py`)
12. Add new test files (`test_worktree_merge.py`, `test_focus_session.py`)
