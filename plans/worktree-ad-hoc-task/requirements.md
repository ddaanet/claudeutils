# Worktree Ad-Hoc Task Creation

## Requirements

### Functional Requirements

**FR-1: Add task to session.md before worktree creation**
When the user requests a focused worktree for a task not yet present in session.md Pending Tasks, the worktree skill (Mode A) must add the task entry to Pending Tasks before invoking `claudeutils _worktree new`. The CLI requires the task to exist in session.md for both `move_task_to_worktree()` (task movement) and `focus_session()` (filtered session generation).

Acceptance criteria:
- Skill detects task absence after reading session.md in step 1
- Skill writes a minimal task entry (`- [ ] **Task Name** — command | model`) to Pending Tasks
- Subsequent `_worktree new` succeeds (task found, moved to Worktree Tasks, focused session generated)

**FR-2: Derive task metadata from user request**
When creating the ad-hoc task entry, the skill must derive reasonable metadata from the user's request context: task name, command (if determinable from plan state or conversation), and model tier.

Acceptance criteria:
- Task name derived from user's request (not verbatim — normalized to task naming conventions)
- Command derived from plan state if a plan directory exists, or from explicit user instruction
- Model defaults to sonnet if not specified

### Constraints

**C-1: Skill-layer change only**
The fix is a prose addition to the worktree SKILL.md Mode A procedure. No CLI code changes — the CLI's strict exact-match behavior is correct (prevents silent mismatches). The skill adds the missing step before the CLI call.

### Out of Scope

- CLI fuzzy matching — agent layer handles name resolution (per discussion this session)
- Automatic task discovery from plan directories — task must come from user request
- Modifying Mode B (parallel group) — that flow reads existing tasks, doesn't create new ones
