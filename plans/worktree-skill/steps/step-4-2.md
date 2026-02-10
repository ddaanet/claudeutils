# Cycle 4.2

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 4
**Report Path**: `plans/worktree-skill/reports/cycle-4-2-notes.md`

---

## Cycle 4.2: Mode A implementation (single-task worktree)

**RED:**
Skill contains Mode A prose that describes single-task worktree creation flow. Mode A should handle `wt <task-name>` invocation pattern. The prose should read as imperative instructions.

Test by reading the skill file. Mode A section should have numbered steps covering:
1. Read session.md to locate task
2. Derive slug from task name (lowercase, hyphens, 30 char max)
3. Generate focused session.md content (minimal scope)
4. Write focused session to `tmp/wt-<slug>-session.md`
5. Invoke CLI: `claudeutils _worktree new <slug> --session tmp/wt-<slug>-session.md`
6. Edit session.md: move task from Pending Tasks to Worktree Tasks with `→ wt/<slug>` marker
7. Print launch command for user

Each step should open with a tool mention (D+B hybrid anchor). Example: "Read `agents/session.md` to locate the task by name."

**GREEN:**
Write Mode A section with imperative prose. Begin each major step with explicit tool usage:
- "Read `agents/session.md`..." (tool anchor)
- "Derive slug..." (prose explanation of transform)
- "Generate focused session.md content..." (describe minimal format)
- "Write to `tmp/wt-<slug>-session.md`..." (tool anchor)
- "Invoke: `claudeutils _worktree new <slug> --session tmp/wt-<slug>-session.md`" (tool anchor with bash)
- "Edit `agents/session.md`..." (tool anchor)

Describe focused session.md format: minimal session scoped to single task with only relevant blockers/references. Provide template structure (4-space indented):

    # Session: Worktree — <task name>

    **Status:** Focused worktree for parallel execution.

    ## Pending Tasks

    - [ ] **<task name>** — <full metadata from original>

    ## Blockers / Gotchas

    <only blockers relevant to this task>

    ## Reference Files

    <only references relevant to this task>

For the session.md edit step, specify exact transformation: locate task in Pending Tasks section, extract full task block (including continuation lines), create Worktree Tasks section if not exists, append task with `→ wt/<slug>` marker.

End with user output: `cd wt/<slug> && claude    # <task name>`

---

**Expected Outcome**: GREEN verification, no regressions
**Stop/Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-4-2-notes.md

---
