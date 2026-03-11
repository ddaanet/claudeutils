# Prose Infrastructure Batch — Outline

## Phase 1: Prose Edits (general)

Four items, all agentic-prose. No behavioral code, no TDD.

### FR-1: Remove opus-design-question skill

**Delete:**
- `agent-core/skills/opus-design-question/` (entire directory)

**Edit:**
- `agent-core/fragments/design-decisions.md` — replace entire content. New guidance: "If you need opus-level reasoning, the user sets the model. Do not delegate design decisions to a sub-agent." Keep the "Do NOT ask the user unless" criteria (subjective preference, business logic, scope changes, unclear requirements) — those are still valid routing guidance.

**Grep + remove references:**
- Known references (from grep): `agent-core/skills/runbook/references/tier3-planning-process.md`, `agent-core/skills/runbook/SKILL.md`, `agents/decisions/project-config.md`, `agent-core/README.md`, `.claude/rules/design-work.md`
- Grep all `*.md` for `opus-design-question` — remove each reference
- Some references may be in prose context (e.g., "use `/opus-design-question`") — rewrite to match new guidance

**Verification:** `grep -r opus-design-question` returns nothing. Per "when adding a new variant to an enumerated system" — grep all downstream enumeration sites, not just direct references.

### FR-2: Magic-query skill

**Prerequisite:** Load `plugin-dev:skill-development` for frontmatter conventions before writing.

**Create:** `agent-core/skills/magic-query/SKILL.md`

Skill frontmatter:
- `name: magic-query`
- `description:` Lead with action verb per skill-development guide. Must be generic — invite use without biasing what agents search for (e.g., "Query project knowledge base" not "Search semantically for patterns, decisions, and prior art")
- `user-invocable: false` — agent-triggered decoy, not user-facing. Agents discover it via description matching when they want to "search" or "query" project knowledge.

The skill is not user-invocable because it's a decoy for agents — the description is what triggers agent selection. No `/magic-query` slash command exposed. The skill's value is capturing what agents try to search for, not serving the user directly.

Behavior:
- Log query to `~/.claude/magic-query-log.jsonl` — outside project tree for persistence across worktrees and sessions. JSON object per line: `{"timestamp": "<ISO8601>", "query": "<text>"}`
- Return: "Query complete. Continue what you were doing." — pushes agent forward instead of dwelling on failure
- **Logging script:** `agent-core/bin/magic-query-log` — takes query as argument, appends JSON line to `~/.claude/magic-query-log.jsonl`
- **Sandbox bypass:** Add `Bash(agent-core/bin/magic-query-log:*)` to `permissions.allow` in settings.json. Skill instructs agent to call with `dangerouslyDisableSandbox: true` — permission auto-approved, no visible prompt, decoy preserved.
- Skill body invokes the script, then responds with neutral message

### FR-3: Handoff merge-incremental fix

**Edit:** `agent-core/skills/handoff/SKILL.md`

Current detection (line ~27): checks `# Session Handoff:` header date vs today.

Replace with git-dirty detection:
```
git diff --name-only HEAD -- agents/session.md
```
- Non-empty output → prior uncommitted handoff exists → merge incrementally
- Empty output → clean session.md → fresh write

The "Multiple handoffs before commit" prose (line ~88) remains valid — it describes the merge behavior. Only the detection trigger changes.

### FR-4a: Forbid undocumented tasks rule

**Edit:** `agent-core/fragments/execute-rule.md`

Add rule in the Task Status Notation section (after task metadata format):

```markdown
**Plan-backed tasks (mandatory):**
Every pending task must reference a plan directory (`plans/<slug>/`) containing at least one artifact: requirements.md, problem.md, brief.md, or design.md. Inline-described tasks are forbidden — inline descriptions lack context, references, and produce results that miss unstated requirements.

Task commands must include a plan path argument (e.g., `/design plans/foo/requirements.md`, not bare `/design`). The plan path is the validator's primary extraction source.

Applies to: `p:` directive (must create plan artifact before or during handoff), `/handoff` (must not write tasks without plan backing).
```

### FR-4a addendum: Normalize existing bare commands

Three tasks in session.md use bare `/design` without a plan path:
- **Fix TDD context scoping** — needs plan path (has brief at `plans/bootstrap-tag-support/brief.md`)
- **Worktree lifecycle CLI** — needs plan path (has multiple plans: wt-exit-ceremony, wt-rm-task-cleanup, worktree-ad-hoc-task)
- **Design backlog review** — meta-task, needs a plan artifact created or existing plan referenced

Normalize these during Phase 1 so the validator passes on current session.md. Prerequisite for Phase 2.

---

## Phase 2: Task plan-backing validator (TDD)

### Scope

New validator: `src/claudeutils/validation/task_plans.py`

**Function:** `validate(session_path: str, root: Path) -> list[str]`

**Logic:**
1. Parse tasks from session.md using `task_parsing.parse_task_line()`
2. Filter to pending statuses only: `' '`, `'>'`, `'!'` (per C-2)
3. For each pending task, extract plan directory from command field:
   - Explicit path: `/runbook plans/foo/outline.md` → `plans/foo/`, `/design plans/bar/requirements.md` → `plans/bar/`
   - Slug-only commands: `/orchestrate foo` → `plans/foo/`
4. If no plan directory extractable from command → error: `task '<name>' has no plan reference`
6. If plan directory extractable but `plans/<slug>/` doesn't exist or contains none of {requirements.md, problem.md, brief.md, design.md} → error: `task '<name>': plan directory 'plans/<slug>/' has no artifact`
7. Terminal tasks (`x`, `-`, `†`) exempt — skip entirely

**Integration:**
- Add to `cli.py`: import + `_run_validator("task-plans", validate_task_plans, ...)` in `_run_all_validators()`
- Add CLI subcommand `task_plans` to validation group
- Per "when adding a new variant to an enumerated system" — grep `cli.py` and any downstream consumers that enumerate validators to ensure all sites updated

**Edge cases:**
- Tasks with no command field → error (no plan reference)
- Command without `plans/` path → error (no plan reference)
- Command with `plans/` path → extract slug, check directory + artifact

### Test plan

Tests in `tests/validation/test_task_plans.py`. Use Click `CliRunner` for integration test (per "when testing CLI tools").

**Cycles:**
1. **Happy path:** Task with valid plan directory + artifact → passes
2. **Missing plan directory:** Task with command referencing nonexistent `plans/foo/` → error
3. **Empty plan directory:** `plans/foo/` exists but no artifact files → error
4. **No plan reference:** Task with no command or command without plans/ path → error
5. **Terminal tasks exempt:** `[x]`, `[-]`, `[†]` tasks without plans → no error
6. **Command variants:** explicit path (`/design plans/foo/requirements.md`), slug-only (`/orchestrate foo`) — both extract correctly
7. **Integration:** CLI wiring — `claudeutils validate task-plans` invoked via `CliRunner`, runs the validator

---

## Decisions

- **D-1: Plan reference extraction** — parse from command field only (`plans/<slug>/` in backtick command). No fallback to task notes. Path argument is required — no bare `/design` without a plan path.
- **D-2: Validator scope** — pending tasks only (C-2). Terminal tasks exempt because their plans may have been cleaned up or archived.
- **D-3: Existing infra reuse** — extends `task_parsing.parse_task_line()` for parsing, follows `tasks.py` pattern for validator structure, plugs into `cli.py` like all other validators.
- **D-4: Mechanical validation** — plan-backing check is deterministic (path extraction + file existence). No agent judgment needed. Per "when splitting validation into mechanical and semantic" — scripted, blocking, zero false positives.
- **D-5: FR-3 ↔ FR-4b dependency** — handoff produces session.md consumed by this validator. FR-4b test fixtures should cover the merge-incremental path (two uncommitted handoffs producing valid session.md that passes validation).

## Scope

**IN:** FR-1 (remove skill), FR-2 (create skill), FR-3 (handoff fix), FR-4a (rule), FR-4b (validator + tests + CLI integration)

**OUT:** Migrating existing tasks (already done), validating plan content quality (UNREVIEWED marker concern), changing /design skill
