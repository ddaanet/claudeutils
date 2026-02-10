# Cycle 2.1

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 2
**Report Path**: `plans/worktree-skill/reports/cycle-2-1-notes.md`

---

## Cycle 2.1: Session conflict resolution with task extraction

**FR-3: Extract new tasks from worktree side before applying keep-ours merge resolution.**

**RED: Test behavior**

Create test fixture with two session.md versions:
- **Ours:** Base session with tasks "Implement feature X" and "Design feature Y" in Pending Tasks
- **Theirs:** Same base plus new task "Plan feature Z TDD runbook" in Pending Tasks

Call `resolve_session_conflict(ours, theirs)` and assert:
- Result contains all three tasks in Pending Tasks section
- New task "Plan feature Z TDD runbook" includes full task block with metadata (command, model, notes)
- Order: ours tasks first, then new theirs tasks
- All other sections unchanged (Blockers, Reference Files, handoff footer)

**Expected failure:** Function doesn't exist yet, ImportError.

**GREEN: Implement behavior**

Create `src/claudeutils/worktree/conflicts.py` with `resolve_session_conflict(ours: str, theirs: str) -> str`:

**Algorithm hints:**
1. Parse task names from both versions using regex `^- \[ \] \*\*(.+?)\*\*` with `re.MULTILINE` flag
2. Compute new tasks: set difference on task names (theirs - ours)
3. For each new task name, extract full task block from theirs (task line + any indented continuation lines using multi-line regex)
4. Locate insertion point in ours: find Pending Tasks section, identify line before next `## ` heading
5. Insert new task blocks before the next section heading
6. Return merged content with ours as base, new tasks appended

**Approach notes:**
- Task block extraction must capture metadata lines (indented with spaces, containing plan/status/notes)
- Use regex lookahead to stop extraction at next non-indented line or EOF
- Preserve exact formatting (indentation, blank lines within task blocks)

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-2-1-notes.md

---
