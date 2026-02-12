# Cycle 4.1

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Cycle 4.1: Task extraction by name — with metadata and formatting

**Objective:** Extract task block from session.md by matching task name.

**Prerequisite:** Read `agents/session.md` lines 1-100 — understand task block format with metadata (task name, command, model, restart flag) and continuation lines.

**RED Phase:**

**Test:** `test_focus_session_task_extraction`
**Assertions:**
- Given session.md with task `- [ ] **Implement feature X** — \`/plan-adhoc\` | sonnet`
- `focus_session("Implement feature X", session_path)` returns string containing task line
- Returned string includes task metadata (command, model)
- Returned string includes H1 header: `# Session: Worktree — Implement feature X`
- Returned string includes status line: `**Status:** Focused worktree for parallel execution.`
- Returned string has Pending Tasks section with single extracted task
- Task checkbox preserved: `- [ ]` format maintained

**Expected failure:** NameError: function `focus_session` not defined

**Why it fails:** Function doesn't exist yet

**Verify RED:** `pytest tests/test_worktree_cli.py::test_focus_session_task_extraction -v`

---

**GREEN Phase:**

**Implementation:** Create function to parse session.md and extract matching task

**Behavior:**
- Read session.md file content
- Parse to find task by matching `**<task-name>**` pattern
- Extract full task line (including metadata after task name)
- Generate focused session with:
  - H1: `# Session: Worktree — <task-name>`
  - Status: `**Status:** Focused worktree for parallel execution.`
  - Pending Tasks section with single extracted task
- Return formatted string (not write to file)

**Approach:** Regex to find task line, string formatting to build focused session structure

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add new function `focus_session(task_name: str, session_md_path: str | Path) -> str` at module level
  Location hint: After `derive_slug()` function, before command definitions
- File: `src/claudeutils/worktree/cli.py`
  Action: Implement task extraction — read file, regex match for `- [ ] **<task-name>**`, extract line
  Location hint: Function body uses `Path.read_text()`, `re.search()` or `re.findall()`, string formatting for output

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_focus_session_task_extraction -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 3 tests still pass

---
