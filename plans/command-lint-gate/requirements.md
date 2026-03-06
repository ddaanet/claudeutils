# Command Lint Gate

## Requirements

### Functional Requirements

**FR-1: Validate pending tasks have commands**
Pending (`[ ]`) and in-progress (`[>]`) tasks must have a backtick-wrapped command. Missing command on these task types is a precommit error. Completed (`[x]`), blocked (`[!]`), failed (`[†]`), and canceled (`[-]`) tasks are exempt.

Acceptance criteria:
- `- [ ] **Task Name** — description | sonnet` → error (no backtick command)
- `- [ ] **Task Name** — `/design plans/foo/` | sonnet` → pass
- `- [x] **Done Task** — description` → pass (completed, exempt)

**FR-2: Validate skill command names against allowlist**
The `/skill-name` prefix in backtick commands must be in the workflow skill allowlist. Unknown skill names are errors. Allowlist: `/requirements`, `/design`, `/runbook`, `/orchestrate`, `/deliverable-review`, `/inline`, `/ground`.

Acceptance criteria:
- `` `/design plans/foo/` `` → pass (in allowlist)
- `` `/frobnicate plans/foo/` `` → error (not in allowlist)
- Non-skill commands (no `/` prefix) are not validated by this check

**FR-3: Integrate into precommit pipeline**
The new validation runs as part of `claudeutils validate tasks` (or `session-structure`), which is already called by `just precommit`. No new CLI subcommand needed — extend the existing validator.

Acceptance criteria:
- `just precommit` catches command lint errors
- Errors include line number, task name, and specific violation

**FR-4: Validate commands at worktree creation**
`_worktree new --task` validates the task's command before creating the worktree. Uses the same validation logic as FR-1/FR-2. Invalid commands fail early, before expensive git/submodule/setup operations.

Acceptance criteria:
- `claudeutils _worktree new "Task Name"` fails with clear error if task has no command or invalid skill name
- Validation runs after task extraction, before `_setup_worktree_safe()`

### Constraints

**C-1: Extend existing infrastructure**
Build on `task_parsing.py` (already extracts `command` field via `COMMAND_PATTERN`), `session_commands.py` (already validates command anti-patterns), and the `session_structure.py` orchestration. Do not create a parallel validation pipeline.

**C-2: Explicit workflow skill allowlist**
The known skill list is a hardcoded allowlist of workflow skills that legitimately appear in task commands, not filesystem-derived. Rationale: filesystem discovery would auto-accept skills that shouldn't be task commands (`/recall`, `/handoff`, `/commit`). The allowlist forces an explicit decision when a new skill is added. Empirical basis: git history shows 18 distinct skill commands in task entries; after filtering retired, in-session, and deprecated skills, 7 remain.

**C-3: Deterministic validation only**
This is a mechanical lint gate — no agent judgment. Per "when choosing script vs agent judgment" decision: if the solution is non-cognitive, script it.

### Out of Scope

- Path argument validation — already handled by `session_paths.py`
- Command anti-pattern checking — already handled by `session_commands.py`
- Validating command arguments beyond the skill name (argument semantics are skill-specific)
- Validating commands in completed/blocked/failed/canceled tasks

### Dependencies

- `task_parsing.py` `ParsedTask.command` field — source of command text
- `session_commands.py` `check_command_semantics()` — integration point (extend or sibling function)
- `session_structure.py` — orchestration point that calls command validators
- `worktree/cli.py` `new` command — FR-4 integration point (validation before `_setup_worktree_safe()`)

### References

- `src/claudeutils/validation/task_parsing.py` — `COMMAND_PATTERN`, `parse_task_line()`
- `src/claudeutils/validation/session_commands.py` — existing command validation
- `src/claudeutils/validation/session_paths.py` — path validation (adjacent, not overlapping)
- `src/claudeutils/validation/session_structure.py` — orchestration, calls `check_command_semantics`
- `src/claudeutils/worktree/cli.py` — worktree creation, FR-4 call site
