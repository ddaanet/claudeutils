# Cycle 4.4

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 4
**Report Path**: `plans/worktree-skill/reports/cycle-4-4-notes.md`

---

## Cycle 4.4: Mode C implementation (merge ceremony)

**RED:**
Skill contains Mode C prose for merge ceremony orchestration. Mode C handles `wt merge <slug>` invocation pattern. The section describes handoff → commit → merge → cleanup flow with error handling.

Test by reading the skill file. Mode C section should have steps covering:
1. Invoke `/handoff --commit` (ceremony before merge)
2. Wait for commit completion, stop if handoff/commit fails
3. Invoke CLI merge: `claudeutils _worktree merge <slug>`
4. Handle merge exit codes (0 success, 1 conflicts/precommit failure, 2 error)
5. On success: edit session.md to remove task from Worktree Tasks
6. On success: invoke cleanup `claudeutils _worktree rm <slug>`
7. On failure: report error with resolution guidance

**GREEN:**
Write Mode C section with skill invocation anchor:
- "Invoke `/handoff --commit` to ensure clean tree and session context committed." (tool anchor: Skill tool)

Explain the ceremony requirement: merge needs clean tree, handoff ensures session.md reflects current state, commit creates sync point.

After handoff+commit: "If handoff or commit fails, STOP. Merge requires clean tree. Resolve handoff/commit issues before retrying merge."

Invoke merge with bash anchor:
- "Invoke: `claudeutils _worktree merge <slug>`" (tool anchor)

Parse exit code and handle three cases:

**Exit 0 (success):**
- "Edit `agents/session.md`: Remove task from Worktree Tasks section (match on `→ wt/<slug>` marker)." (tool anchor)
- "Invoke: `claudeutils _worktree rm <slug>`" (tool anchor)
- Output: "Merged and cleaned up wt/<slug>. Task complete."

**Exit 1 (conflicts or precommit failure):**
Read stderr from merge command. Parse for conflict indicators or precommit failure messages.

If conflicts: list conflicted files and provide resolution guidance:
- Note session files should auto-resolve (report as bug if conflicted)
- For source files: resolve manually, stage with `git add`, then re-run `wt merge <slug>` (idempotent)

If precommit failure: show which checks failed and explain resolution:
- Merge commit already exists (don't re-merge)
- Fix reported issues, stage fixes
- Amend merge commit: `git commit --amend --no-edit`
- Verify with `just precommit`
- After passing, re-run `wt merge <slug>` to continue cleanup

**Exit 2 (error):**
Report stderr as-is. Generic error handling: "Merge command error. Review output above and resolve before retrying."

---

**Expected Outcome**: GREEN verification, no regressions
**Stop/Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-4-4-notes.md

---
