# Session Handoff: 2026-01-28

**Status:** Skill improvements complete

## Completed This Session

**Plan-TDD skill: Presentation test guidance and checkpoint system:**
- Opus designed solution in plan mode with iterative refinement
- Added "What NOT to Test" section to SKILL.md:
  - Table showing presentation vs behavior test boundaries
  - Heuristic: "If users see output directly, don't test exact phrasing"
  - Valid exceptions for regulatory/generated content
- Added "Checkpoints" section to SKILL.md:
  - Two-step process: Fix (just dev → sonnet quiet-task → commit), then Vet (quality review → commit)
  - Placement guidelines: natural boundaries, not every cycle, not all at end
  - Example showing checkpoint between cycles
- Added presentation test anti-pattern to references/anti-patterns.md
- Files modified:
  - agent-core/skills/plan-tdd/SKILL.md (lines 399-459)
  - agent-core/skills/plan-tdd/references/anti-patterns.md (line 14)

**Remember skill: Made project-independent:**
- Removed hardcoded path /Users/david/code/claudeutils/CLAUDE.md
- Removed obsolete agents/learnings/pending.md processing pattern
- Generalized File Selection to reference agents/decisions/README.md
- Updated consolidation-patterns.md to use project-level routing
- Added routing-template.md showing projects how to configure domain routing
- Files modified:
  - agent-core/skills/remember/SKILL.md (commit f97157f)
  - agent-core/skills/remember/references/consolidation-patterns.md
  - agent-core/skills/remember/references/routing-template.md (new)

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
