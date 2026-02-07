# Session: Worktree — Fix initial status in new wt

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Fix initial status in new wt reporting incorrect reset instruction** — When launching a new worktree, status incorrectly says "Note: Session says to reset session.md first (git checkout -- agents/session.md), stage all (git add -A), then /commit before executing the task." This is wrong because session.md is already pre-committed to the branch via git plumbing in the wt-new recipe.

## Context

The wt-new recipe pre-commits focused session.md to the branch before worktree creation (lines 66-75 of justfile). The focused session.md template was simplified to remove the "reset + stage + commit" bootstrap instruction. However, something is still generating this incorrect status message.

## Investigation Needed

- Find where the "Note: Session says to reset session.md first..." message is generated
- This might be in:
  - Hook scripts (UserPromptSubmit hook with #status shortcut?)
  - Session.md template still has old content?
  - Status display logic interpreting old format?

## Blockers / Gotchas

None specific to this task.

## Reference Files

- **justfile** — wt-new recipe (lines 55-87, git plumbing session pre-commit)
- **agent-core/fragments/execute-rule.md** — MODE 5 (local session.md write + recipe pre-commit flow)
- **agents/session.md** — Focused session.md template (simplified per handoff notes)
