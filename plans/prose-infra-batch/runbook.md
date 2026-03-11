# Runbook: Prose Infrastructure Batch

**Tier:** 2 (Lightweight Delegation)
**Source:** `plans/prose-infra-batch/outline.md`
**Recall:** `plans/prose-infra-batch/recall-artifact.md`

---

## Phase 1: Prose Edits (type: inline)

Opus. All items are agentic-prose — skill files, fragments, reference edits. Orchestrator-direct, no delegation.

### Step 1.1: Remove opus-design-question skill (FR-1)

**Delete:** `agent-core/skills/opus-design-question/` (entire directory)

**Edit:** `agent-core/fragments/design-decisions.md` — replace content with:
- Remove all references to `/opus-design-question` skill
- New guidance: "If you need opus-level reasoning, the user sets the model. Do not delegate design decisions to a sub-agent."
- Keep the "Do NOT ask the user unless" criteria (subjective preference, business logic, scope changes, unclear requirements)

**Grep + remove references** from all `*.md` files. Known reference sites:
- `agent-core/skills/runbook/references/tier3-planning-process.md`
- `agent-core/skills/runbook/SKILL.md`
- `agents/decisions/project-config.md`
- `agent-core/README.md`
- `.claude/rules/design-work.md`

Rewrite prose context references to match new guidance (e.g., "use `/opus-design-question`" → remove or replace).

**Verification:** `grep -r opus-design-question` returns nothing. Check downstream enumeration sites, not just direct references.

### Step 1.2: Create magic-query skill (FR-2)

**Prerequisite:** Load `plugin-dev:skill-development` for frontmatter conventions.

**Create:** `agent-core/skills/magic-query/SKILL.md`

Frontmatter:
- `name: magic-query`
- `description:` Action verb first. Must be generic — invite use without biasing what agents search for (e.g., "Query project knowledge base" not "Search semantically for patterns, decisions, and prior art"). Collecting organic needs — description must not influence input.
- `user-invocable: false` — agent-triggered decoy, not user-facing

Skill body instructs agent to:
1. Run `agent-core/bin/magic-query-log` with the query argument (using `dangerouslyDisableSandbox: true`)
2. Respond: "Query complete. Continue what you were doing." — pushes agent forward instead of dwelling on failure

**Create:** `agent-core/bin/magic-query-log`
- Shell script, takes query as argument
- Appends JSON line to `~/.claude/magic-query-log.jsonl`: `{"timestamp": "<ISO8601>", "query": "<text>"}`
- Make executable

**Edit:** `settings.json` — add `Bash(agent-core/bin/magic-query-log:*)` to `permissions.allow`

**Post:** `just sync-to-parent` (requires `dangerouslyDisableSandbox: true`) to create skill symlink in `.claude/skills/`

### Step 1.3: Fix handoff merge-incremental detection (FR-3)

**Edit:** `agent-core/skills/handoff/SKILL.md`

Replace date-comparison detection (line ~27, "Session Handoff header with a date different from today") with git-dirty detection:

Detection: `git diff --name-only HEAD -- agents/session.md`
- Non-empty → prior uncommitted handoff exists → merge incrementally (Edit, append Completed, mutate tasks)
- Empty → clean session.md → fresh write (Write)

The "Multiple handoffs before commit" merge behavior prose (line ~88) remains unchanged — only the trigger condition changes.

### Step 1.4: Add plan-backed tasks rule (FR-4a)

**Edit:** `agent-core/fragments/execute-rule.md`

Add in Task Status Notation section, after task metadata format:

> **Plan-backed tasks (mandatory):**
> Every pending task must reference a plan directory (`plans/<slug>/`) containing at least one artifact: requirements.md, problem.md, brief.md, or design.md. Inline-described tasks are forbidden — inline descriptions lack context, references, and produce results that miss unstated requirements.
>
> Task commands must include a plan path argument (e.g., `/design plans/foo/requirements.md`, not bare `/design`). The plan path is the validator's primary extraction source.
>
> Applies to: `p:` directive (must create plan artifact before or during handoff), `/handoff` (must not write tasks without plan backing).

### Step 1.5: Normalize bare `/design` commands (FR-4a addendum)

Prerequisite for Phase 2 validator. Three tasks in `agents/session.md` use bare `/design`:

- **Fix TDD context scoping** → `/design plans/bootstrap-tag-support/brief.md` (brief exists)
- **Worktree lifecycle CLI** → pick primary plan (wt-exit-ceremony, wt-rm-task-cleanup, or worktree-ad-hoc-task) or create umbrella `plans/worktree-lifecycle-cli/`
- **Design backlog review** → create `plans/design-backlog-review/problem.md` or reference existing plan

**Verification:** `grep '— \x60/design\x60[^/]' agents/session.md` returns nothing.

---

## Phase 2: Task plan-backing validator (type: tdd)

Sonnet. New Python validator with TDD cycles.

### Cycle 2.1: Happy path — valid plan reference passes

**Bootstrap:** Create `src/claudeutils/validation/task_plans.py` with stub `validate(session_path: str, root: Path) -> list[str]` returning `[]`. Do not commit.

---

**RED Phase:**

**Test:** `test_valid_plan_passes_invalid_fails`
**Assertions:**
- Two tasks: one with valid `plans/foo/requirements.md`, one with bare `/design` (no plan path)
- `validate()` returns list with exactly 1 error mentioning the bare-command task name
- Valid task produces no error

**Expected failure:** `AssertionError` — stub returns `[]`, missing the expected error for the bare-command task

**Why it fails:** Stub returns empty list, test expects exactly 1 error

**Verify RED:** `just test tests/test_validation_task_plans.py`

---

**GREEN Phase:**

**Implementation:** Core validate function

**Behavior:**
- Parse session.md lines for task entries using `task_parsing.parse_task_line()`
- Filter to pending statuses: `' '`, `'>'`, `'!'`
- Extract plan directory from command field via regex: `plans/([^/]+)/`
- If no plan path in command → error
- If plan directory doesn't exist or has no artifact → error

**Approach:** Regex extraction on command field, Path existence checks

**Changes:**
- File: `src/claudeutils/validation/task_plans.py`
  Action: Implement `validate()` with task parsing, status filtering, plan path extraction, directory/artifact checks
  Location hint: Replace stub

**Verify GREEN:** `just green`

### Cycle 2.2: Missing plan directory

**RED Phase:**

**Test:** `test_missing_plan_directory`
**Assertions:**
- Task with command `/runbook plans/nonexistent/outline.md`
- `plans/nonexistent/` does NOT exist in tmp_path
- Error list contains entry with `nonexistent` and "no artifact" or similar

**Expected failure:** `AssertionError` — if 2.1 GREEN only checks command parsing but not directory existence

**Why it fails:** Implementation may not yet check directory existence (depends on 2.1 scope)

**Verify RED:** `just test tests/test_validation_task_plans.py`

---

**GREEN Phase:**

**Implementation:** Directory existence check

**Behavior:**
- After extracting plan slug, verify `plans/<slug>/` directory exists
- If missing → error: `task '<name>': plan directory 'plans/<slug>/' missing`

**Changes:**
- File: `src/claudeutils/validation/task_plans.py`
  Action: Add directory existence check after slug extraction
  Location hint: Within validate loop, after regex match

**Verify GREEN:** `just green`

### Cycle 2.3: Empty plan directory (no artifact)

**RED Phase:**

**Test:** `test_empty_plan_directory`
**Assertions:**
- Task with command `/design plans/empty/requirements.md`
- `plans/empty/` exists but contains no recognized artifacts (no requirements.md, problem.md, brief.md, design.md)
- Error list contains entry mentioning `empty` and "no artifact"

**Expected failure:** `AssertionError` — directory exists so previous check passes, but no artifact check yet

**Why it fails:** Implementation checks directory existence but not artifact presence

**Verify RED:** `just test tests/test_validation_task_plans.py`

---

**GREEN Phase:**

**Implementation:** Artifact presence check

**Behavior:**
- After confirming directory exists, check for at least one of: requirements.md, problem.md, brief.md, design.md
- If none present → error: `task '<name>': plan directory 'plans/<slug>/' has no artifact`

**Changes:**
- File: `src/claudeutils/validation/task_plans.py`
  Action: Add artifact file existence check
  Location hint: After directory existence check

**Verify GREEN:** `just green`

### Cycle 2.4: Terminal tasks exempt

**RED Phase:**

**Test:** `test_terminal_tasks_exempt`
**Assertions:**
- Three tasks with no valid plan path: `[x]`, `[-]`, `[†]` checkboxes
- `validate()` returns empty list — terminal tasks skipped entirely

**Expected failure:** `AssertionError` — if status filtering doesn't exclude terminal statuses, validator reports errors for these tasks

**Why it fails:** Implementation may not filter by checkbox status, treating all tasks as pending

**Verify RED:** `just test tests/test_validation_task_plans.py`

---

**GREEN Phase:**

**Implementation:** Verify status filtering covers terminal statuses

**Behavior:**
- Skip tasks with checkbox `x`, `-`, `†` (dagger character)
- Only validate tasks with ` `, `>`, `!`

**Changes:**
- File: `src/claudeutils/validation/task_plans.py`
  Action: Ensure status filter excludes terminal checkboxes
  Location hint: Filter predicate in validate loop

**Verify GREEN:** `just green`

### Cycle 2.5: Slug-only command extraction

**RED Phase:**

**Test:** `test_slug_only_command`
**Assertions:**
- Task with command `/orchestrate my-plan`
- `plans/my-plan/requirements.md` exists
- `validate()` returns empty list — slug correctly inferred as `plans/my-plan/`

**Expected failure:** `AssertionError` — regex only matches `plans/<slug>/` pattern, misses slug-only commands

**Why it fails:** `/orchestrate my-plan` has no `plans/` prefix in command — regex extraction fails, reports "no plan reference"

**Verify RED:** `just test tests/test_validation_task_plans.py`

---

**GREEN Phase:**

**Implementation:** Slug-only command fallback

**Behavior:**
- If `plans/<slug>/` regex doesn't match, check for `/orchestrate <slug>` pattern
- Extract slug, prepend `plans/` for directory check

**Approach:** Secondary regex or pattern match on command after primary fails

**Changes:**
- File: `src/claudeutils/validation/task_plans.py`
  Action: Add fallback extraction for slug-only commands
  Location hint: After primary regex miss, before "no plan reference" error

**Verify GREEN:** `just green`

### Cycle 2.6: CLI integration

**RED Phase:**

**Test:** `test_cli_task_plans_command`
**Assertions:**
- Invoke `validate task-plans` via `CliRunner`
- With a session.md containing a task with missing plan → exit code 1, stderr contains error message
- With valid session.md → exit code 0

**Expected failure:** `AssertionError` — CLI subcommand doesn't exist yet, Click raises "No such command"

**Why it fails:** `task-plans` subcommand not registered in validation CLI group

**Verify RED:** `just test tests/test_validation_task_plans.py`

---

**GREEN Phase:**

**Implementation:** Wire validator into CLI

**Behavior:**
- Add `task_plans` subcommand to validation group
- Add `_run_validator("task-plans", ...)` call in `_run_all_validators()`

**Changes:**
- File: `src/claudeutils/validation/cli.py`
  Action: Import validate function, add to `_run_all_validators()`, add `@validate.command()` function
  Location hint: Follow pattern of existing validators (tasks, planstate, etc.)

**Verify GREEN:** `just green`

---

## Weak Orchestrator Metadata

| Phase | Type | Execution Model | Steps/Cycles |
|-------|------|----------------|--------------|
| 1 | inline | opus | 5 steps |
| 2 | tdd | sonnet | 6 cycles |

**Constraint C-1:** Bundle all changes, single commit, session restart required (skill removal in Phase 1).
