# Session Handoff: 2026-01-28

**Status:** /next skill logic fix complete

## Completed This Session

**Fixed /next skill stop-early logic:**
- Updated .claude/skills/next/skill.md to clarify pending work detection
- Bug: Skill was stopping when seeing "None" or "Ready for new work" in session.md
- Fix: Added explicit definition of what qualifies as pending work (specific tasks/items, NOT empty states)
- Updated all 4 check steps to distinguish between "actual pending work" vs "no pending work"
- Updated Important Notes section with clarification
- Pattern: "Stop early" means stop when work IS found, not when checking reveals emptiness

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
