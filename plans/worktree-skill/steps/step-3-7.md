# Cycle 3.7

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 3
**Report Path**: `plans/worktree-skill/reports/cycle-3-7-notes.md`

---

## Cycle 3.7: Phase 3 parent merge - session conflicts

**RED — Behavioral Verification:**

Verify deterministic session file conflict resolution. Create worktree with new task in session.md Pending Tasks, make conflicting edit to same section in parent, invoke merge, assert session.md conflict detected and resolved via conflicts.py logic (new task extracted and appended). Verify learnings.md and jobs.md conflicts also resolved deterministically. Assert agent-core submodule conflict resolved via `--ours` (Phase 2 already merged). Check no unresolved conflicts remain after automatic resolution.

Expected: Session conflicts resolved without manual intervention, new task preserved, agent-core taken from ours, merge proceeds to commit.

**GREEN — Behavioral Description:**

Implement conflict detection and resolution for session context files. After merge command, detect conflicts: `git diff --name-only --diff-filter=U` (U = unmerged). For each conflict file, route to appropriate resolver: agent-core → `git checkout --ours agent-core && git add agent-core` (already merged in Phase 2), session.md → apply `resolve_session_conflict()`, learnings.md → `resolve_learnings_conflict()`, jobs.md → `resolve_jobs_conflict()`. Extract conflict sides via `git show :2:<path>` (ours) and `git show :3:<path>` (theirs), pass to resolver, write result to working tree, stage with `git add <path>`. Check remaining conflicts after resolution — if any remain, proceed to abort flow (cycle 3.10).

Design decisions: D-6 (extract before resolve), NFR-2 (deterministic session resolution). Approach: conflict file routing table, git show for conflict extraction, conflicts.py provides resolution functions.

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-3-7-notes.md

---
