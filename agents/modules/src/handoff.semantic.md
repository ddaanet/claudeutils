# Handoff Skill Module

---
author_model: claude-opus-4-5-20251101
semantic_type: skill
expansion_sensitivity: explicit
target_rules:
  weak: 8-12
note: Skills only generate weak variant (loaded on-demand at session end)
---

## Semantic Intent

Session handoffs should leave clear state for the next agent. Document blockers,
decisions, and next steps. Reference specific code locations. Don't duplicate
information available from tools.

---

## Critical (Tier 1)

### Update Completion File

Before ending, add notes to the relevant completion file (e.g., `STEP#_COMPLETION.md`).
This serves as both completion notes and handoff information.

### Reference Specific Locations

Include file paths, line numbers, function names. Vague references waste the next
agent's time searching.

---

## Important (Tier 2)

### What to Document

Document:

- Design decisions and rationale
- User feedback and preferences
- Blockers or questions for next agent (document in agents/session.md#Blockers)
- Current status and next steps

Do NOT document:

- Test counts (use `just test` for live info)
- File lists (use `ls` or `git status`)
- Implementation details visible in code

### Key Principle

Documentation should not duplicate dynamic state. Let tools provide live information.
Document decisions and context that tools can't provide.

---

## Preferred (Tier 3)

### Completion File Structure

Single file serves dual purpose:

- Completion notes: what was implemented, test results, decisions
- Handoff info: status, next steps, blockers

No separate handoff file needed.
