# Cycle 5.2

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 5
**Report Path**: `plans/worktree-skill/reports/cycle-5-2-notes.md`

---

## Cycle 5.2: execute-rule.md Mode 5 Update

**RED — Specify the behavior to verify:**

The `agent-core/fragments/execute-rule.md` file still contains inline prose for Mode 5 (worktree setup) behavior. It should instead reference the `/worktree` skill as the canonical implementation.

**Test expectations:**
- Mode 5 section header remains: "### MODE 5: WORKTREE SETUP"
- Triggers section references `wt` commands
- Body text directs reader to `/worktree` skill documentation
- No inline implementation prose (slug derivation, session generation, merge ceremony)

**GREEN — Implement to make tests pass:**

Replace the inline worktree implementation prose with a reference to the `/worktree` skill. Preserve the trigger documentation (`wt` and `wt <task-name>`) but delegate behavior description to the skill.

**Approach:**
- Edit `agent-core/fragments/execute-rule.md` Mode 5 section
- Remove detailed implementation steps (slug derivation, focused session generation, worktree creation flow)
- Add: "See `agent-core/skills/worktree/SKILL.md` for implementation details"
- Keep trigger documentation intact for reference

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-5-2-notes.md

---
