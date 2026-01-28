# Session Handoff: 2026-01-28

**Status:** CLAUDE.md refactoring and template creation complete across all projects

## Completed This Session

**Template creation and commit discipline fixes (agent-core):**
- Created CLAUDE.template.md in agent-core/templates/ for new projects
- Renamed to CLAUDE.template.md to avoid auto-injection in subdirectories
- Fixed over-committing pattern in /commit and /commit-context skills
  - Added interactive vs automated session distinction
  - Interactive: batch changes, commit on user request or natural breakpoints
  - Automated: auto-commit after each logical unit per runbook
- Created 2 new shared fragments:
  - commit-skill-usage.md (mentions gitmoji is included)
  - no-estimates.md (no predictions unless requested)
- **Commits:** 51831e8 (template), 7545d60 (commit discipline), e1385c0 (fragments)

**pytest-md CLAUDE.md migration:**
- Updated agent-core submodule from 7321a80 to e1385c0 (5 new fragments)
- Created CLAUDE.md using @file references (103 lines)
- Restored missing project-specific sections:
  - Context Management (session.md discipline, handoff protocol)
  - Opus Orchestration (model selection, sub-agent usage)
- Removed AGENTS.md (superseded by CLAUDE.md)
- Sonnet review validated correctness and completeness
- **Commit:** f82e7a2 (CLAUDE.md + AGENTS.md removal, amended)

**claudeutils fragment adoption:**
- Replaced inline commit/estimate rules with @file references
- Updated agent-core submodule to e1385c0
- **Commit:** ddc7401

**Current state:**
- agent-core: 18 fragments (up from 11)
- claudeutils CLAUDE.md: 56 lines with 12 @file references
- pytest-md CLAUDE.md: 103 lines with 10 @file references
- Template ready for future projects

## Pending Tasks

**None - all workflow tasks complete.**

## Blockers / Gotchas

**Agent-core template naming:**
- CLAUDE.md files in subdirectories auto-inject into context
- Template must be named CLAUDE.template.md to avoid this
- Copy command: `cp agent-core/templates/CLAUDE.template.md CLAUDE.md`

**Branch state:**
- claudeutils: `skills` branch
- pytest-md: `dev` branch
- agent-core: `main` branch (pushed to origin)

## Next Steps

**Start fresh session for new work.**

All CLAUDE.md refactoring complete. Template established for future projects.

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

**Native @file obsoletes custom composition tooling:**
- Discovery: Claude Code natively supports `@path/to/file.md` references with recursive inclusion (5 levels)
- Impact: Custom compose.py system (34K design, Phases 5-7) not needed for modular CLAUDE.md
- Pattern: Use @file for shared fragments, keep project-specific content inline
- Rationale: Native feature achieves goal (avoid copy-paste, reuse fragments) without tooling overhead

**Handoff discipline with multi-commit work:**
- Anti-pattern: Skipping handoff updates between commits during extended work sessions
- Correct pattern: Update session.md before each commit, or immediately after realizing omission
- Rationale: Preserves context for next agent, avoids information loss, maintains workflow continuity

**Interactive vs automated commit patterns:**
- Anti-pattern: Auto-committing after each small change in interactive sessions (file edit, template creation)
- Correct pattern: Distinguish session types - interactive sessions batch related changes and commit on user request; automated workflows commit after each logical unit
- Rationale: Prevents commit spam in interactive work while maintaining checkpoint discipline in runbook execution
