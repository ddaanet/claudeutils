---
name: handoff
description: Ending a session (any role can load)
---

# Handoff Skill

This skill can be loaded by any agent role when ending a session.

**Session start** is handled by loading `CLAUDE.md` and `agents/session.md`.

---

## What to Do Before Ending

1. **Update completion file** - Add notes to `agents/STEP#_COMPLETION.md`
2. **Document blockers** - Note any issues or decisions needed
3. **Reference specific locations** - File paths, line numbers, function names
4. **Leave clear next steps** - What the next agent should do

### Completion File Structure

Each `STEP#_COMPLETION.md` serves dual purpose:

- **Completion notes:** What was implemented, test results, design decisions
- **Handoff info:** Current status, next steps, file locations, blockers

**Single file, not separate handoff file.**

---

## Key Principle

**Documentation should not duplicate dynamic state.**

Instead of maintaining counts in markdown:

- Run `just test` to see current test status
- Use git commands to check file modifications
- Let tools provide live information

What to document:

- Design decisions and rationale
- User feedback and preferences
- Blockers or questions for next session
- References to specific code locations

What NOT to document:

- Test counts (use `just test`)
- File lists (use `ls` or `git status`)
- Implementation details visible in code
