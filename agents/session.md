# Session Handoff: 2026-01-28

**Status:** CLAUDE.md refactoring complete, ready for pytest-md update

## Completed This Session

**Native @file discovery and initial refactoring:**
- Discovered Claude Code native support for `@file` references (recursive, 5 levels deep)
- **Phase 5-7 obsolete:** compose.py system not needed - native @file achieves goal
- Initial refactoring: 4 fragments (communication, bash-strict-mode, delegation, tool-batching)
- Updated plans/unification/STATUS.md with native @file finding
- **Commit:** c633ad8

**Additional refactoring and consolidation:**
- Created 5 new fragments in agent-core:
  - workflows-terminology.md (workflow selection + terminology)
  - token-economy.md (token economy + avoid numbered lists)
  - error-handling.md (error handling principles)
  - tmp-directory.md (project-local tmp/ usage)
  - execute-rule.md (#execute session continuation)
- Updated delegation.md: added Script-First Evaluation + Pre-Delegation Checkpoint
- Removed agent-core path rule (project renamed, no longer confusing)
- Removed Commit Agent Delegation Pattern (superseded by /commit skill improvements)
- **Commits:** 1008c47 (additional extractions), 76a3a91 (remove obsolete pattern)

**Final results:**
- CLAUDE.md: 60 lines (down from 220 - 73% reduction)
- agent-core: 16 fragments available for reuse
- agent-core submodule: updated with new fragments (commit 18a539a)

## Pending Tasks

### Combine Recent Commits
- Use `git reset --soft HEAD~2` to combine 1008c47 and 76a3a91
- Create single commit for all additional refactoring work

### Create Template CLAUDE.md
- Add template CLAUDE.md to agent-core for new projects
- Based on claudeutils structure with @file references
- Include placeholders for project-specific sections

### pytest-md Submodule Update
- Update pytest-md agent-core submodule (36 commits behind)
- Refactor pytest-md CLAUDE.md to use @file references
- Document @file pattern for future projects

## Blockers / Gotchas

**None currently.**

**Branch state:**
- Current: `skills`
- Last 3 commits: c633ad8, 1008c47, 76a3a91 (need to squash last 2)

## Next Steps

1. Squash last 2 commits into single commit
2. Add template CLAUDE.md to agent-core
3. Update pytest-md submodule
4. Refactor pytest-md CLAUDE.md

**Reference:**
- Native @file documentation: plans/unification/STATUS.md
- Current fragments: agent-core/fragments/ (16 total)
- Final CLAUDE.md: 60 lines with 10 @file references

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
