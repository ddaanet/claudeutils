# Agent Instructions

**Role-specific instructions:** See `agents/role-*.md` for specialized behaviors.
**Current work state:** Read `agents/context.md` for active tasks and decisions.
**Architecture decisions:** See `agents/design-decisions.md` for technical rationale.

---

## Communication Rules

1. **Stop on unexpected results** - If something fails OR succeeds unexpectedly, describe expected vs observed, then STOP and wait for guidance
2. **Wait for explicit instruction** - Do NOT proceed with a plan or TodoWrite list unless user explicitly says "continue" or equivalent
3. **Request validation every 3 cycles** - After every three test-implement cycles, stop and request confirmation
4. **Be explicit** - Ask clarifying questions if requirements unclear
5. **Stop at boundaries** - Complete assigned task then stop (no scope creep)

---

## Tool Batching

**Planning phase (before tool calls):**
1. Identify ALL changes needed for current task
2. Group by file: same-file edits sequential, different-file edits parallel
3. For multi-edit files: list insertion points, plan bottom-to-top order (avoids line shifts)

**Execution phase:**
4. **Batch reads:** Read multiple files in one message when needed soon
5. **Different files:** Edit in parallel when independent
6. **Same file:** Edit sequentially, bottom-to-top when inserting
7. **Refresh context:** If you plan to modify a file again in next iteration, Read it in the batch

---

## Roles and Rules

**Roles** define agent behavior modes. **Rules** apply during specific actions.

### Roles

| Role     | File                      | Purpose                    |
| -------- | ------------------------- | -------------------------- |
| planning | `agents/role-planning.md` | Design test specifications |
| code     | `agents/role-code.md`     | TDD implementation         |
| lint     | `agents/role-lint.md`     | Fix lint/type errors       |
| refactor | `agents/role-refactor.md` | Plan refactoring changes   |
| execute  | `agents/role-execute.md`  | Execute planned changes    |
| review   | `agents/role-review.md`   | Code review and cleanup    |
| remember | `agents/role-remember.md` | Update agent documentation |

### Rules (Action-Triggered)

| Rule    | File                      | Trigger                 |
| ------- | ------------------------- | ----------------------- |
| commit  | `agents/rules-commit.md`  | Before any `git commit` |
| handoff | `agents/rules-handoff.md` | Before ending a session |

**Loading:** Read the role file at session start. Read rule files before the triggering action.
