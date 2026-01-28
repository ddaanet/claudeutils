# Session Handoff: 2026-01-28

**Status:** /next skill improvements complete

## Completed This Session

**Updated /next skill invocation logic:**
- First commit (2b1fedc): Fixed stop-early logic (was stopping on empty states like "None")
- Second update: Changed skill to only load when context is empty
- Modified description: "ONLY when... NO pending work in already-loaded context"
- Added "When NOT to Use" section: Don't load if work visible in session.md
- Restructured flow: Context check happens BEFORE skill invocation (not inside skill)
- Renumbered steps: Removed "Check Initial Context" as step 1 (now prerequisite)
- Pattern: Most efficient path is checking loaded context first, only load skill if truly empty

## Pending Tasks

**None.**

## Blockers / Gotchas

**None currently.**

## Next Steps

Ready for new work.

## Recent Learnings

**Checkpoint process for runbooks:**
- Anti-pattern: All-at-once vetting after full runbook execution OR vetting every single step
- Correct pattern: Two-step checkpoints at natural boundaries (Fix: just dev → quiet-task → commit; Vet: quality review → commit)
- Rationale: Balances early issue detection with cost efficiency; creates logical commit points

**Presentation vs behavior in TDD:**
- Anti-pattern: Writing RED-GREEN cycles for help text wording, error message phrasing, log formatting
- Correct pattern: Test behavior (command works, error raised, data logged), defer presentation quality to vet checkpoints
- Rationale: Presentation tests are brittle (break on improvements) and self-evident (users see quality directly)

**Agent-core project-independence pattern:**
- Anti-pattern: Hardcode project-specific paths or file structures in agent-core skills
- Correct pattern: Delegate project-specific routing to project-level config files (e.g., agents/decisions/README.md)
- Rationale: Skills should be opinionated about patterns but flexible about project structure; allows reuse across projects
