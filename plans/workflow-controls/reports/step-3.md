# Step 3 Execution Report

**Objective:** Update commit skill to replace bare "Next: task" with full STATUS format.

**Status:** COMPLETE

## Actions Taken

Edited `agent-core/skills/commit/SKILL.md` post-commit section (lines 201-216):

**Replaced:**
- Simple "Next: <first pending task description>"

**With:**
- Full STATUS display format showing:
  - Next task name
  - Command to start it (backtick-wrapped)
  - Model recommendation
  - Restart requirement
  - Remaining pending tasks

**Added graceful degradation rules:**
- Missing session.md → "No pending tasks."
- Old format tasks → defaults (sonnet, no restart)
- Missing metadata fields → appropriate defaults

## Validation

✅ STATUS format matches design specification
✅ Graceful degradation documented
✅ Model and restart fields included
✅ Pending tasks list format specified

## Outcome

Commit skill now displays full STATUS after committing, replacing the bare next-task message. Users see complete context for next action including command, model, and restart requirements.
