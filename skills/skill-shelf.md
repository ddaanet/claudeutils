---
name: shelf
description: Archive current context to todo list
trigger: /shelf
---

# Shelf Skill

**Purpose:** Preserve current work context for later continuation by moving it to the todo list.

---

## When to Use

- Before starting unrelated work in the same session
- When pausing work on current feature
- To preserve context without committing or closing session

---

## Workflow

1. **Read** `agents/session.md` (current context)
2. **Read** `agents/todo.md` (existing todo items, create if missing)
3. **Prepend** current context to `agents/todo.md`:
   - Add dated separator: `## Shelved: YYYY-MM-DD - <topic>`
   - Insert full context content below separator
   - Preserve existing todo.md content below
4. **Reset** `agents/session.md` to empty template
5. **Report** completion: "Shelved context: <topic>"

---

## Todo.md Format

```markdown
# Todo

Deferred work items and shelved context.

---

## Shelved: 2026-01-13 - Markdown Formatter Migration

<full context content here>

---

## Shelved: 2026-01-12 - Previous Topic

<previous shelved content>

---

## Backlog

- [ ] Item 1
- [ ] Item 2
```

---

## Empty Context Template

After shelving, reset `agents/session.md` to:

```markdown
# Session Handoff: YYYY-MM-DD

**Status:** Ready for new work

## Completed This Session

(Empty - will be filled with next session's work)

## Pending Tasks

**None.**

## Blockers / Gotchas

**None currently.**

## Next Steps

Ready for new work.

## Recent Learnings

(Empty - will be filled as patterns emerge)

---

## Recent Decisions

<decisions>

---

## Blockers

**None currently.**
```

---

## Constraints

- **Do NOT** modify archived session.md content
- **Do NOT** remove existing todo.md content (prepend only)
- **Create** todo.md if it doesn't exist
