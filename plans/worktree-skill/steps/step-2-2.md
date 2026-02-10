# Cycle 2.2

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 2
**Report Path**: `plans/worktree-skill/reports/cycle-2-2-notes.md`

---

## Cycle 2.2: Session conflict removes merged worktree entry

**FR-3: Remove worktree task entry from Worktree Tasks section after extracting it.**

**RED: Test behavior**

Create test fixture where theirs has a Worktree Tasks section:
- **Ours:** Pending Tasks only (no Worktree Tasks section)
- **Theirs:** Same Pending Tasks plus Worktree Tasks section with entry `- [ ] **Execute plugin migration** → wt/plugin-migration`

Call `resolve_session_conflict(ours, theirs, slug="plugin-migration")` and assert:
- Result has no Worktree Tasks section
- Pending Tasks section includes "Execute plugin migration" task (extracted and moved)
- No reference to `wt/plugin-migration` remains

**Expected failure:** Function signature doesn't accept `slug` parameter, worktree entry not removed.

**GREEN: Implement behavior**

Update `resolve_session_conflict` signature to accept optional `slug: str | None = None`:

**Algorithm hints:**
1. After extracting new tasks from theirs, scan theirs for Worktree Tasks section
2. If `slug` provided: match line containing `→ wt/{slug}` pattern using regex
3. Extract task name from matched worktree entry (same task name regex as Pending Tasks)
4. If task name matches one of the newly extracted tasks, include it in new tasks list
5. Do NOT include Worktree Tasks section in final result (section is omitted entirely)
6. Return merged content with new tasks in Pending Tasks, no Worktree Tasks

**Approach notes:**
- Worktree entry removal happens automatically by taking ours as base (which lacks the section)
- Task name from worktree entry must match against extracted new tasks
- Edge case: if worktree task name doesn't match any new task, it's not critical (merge can proceed)

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-2-2-notes.md

---
