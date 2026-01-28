# Session Handoff: 2026-01-28

**Status:** Unification Phase 4 complete, config composition pending

## Completed This Session

**Unification project Phase 4 completion:**
- Discovered unification project was incomplete (config factorization missing)
- Created agent-core/configs/ directory for base configuration files
- Moved justfile-base.just, ruff.toml, mypy.toml from fragments/ to configs/
- Renamed to *-base.* pattern (ruff-base.toml, mypy-base.toml)
- Created docformatter-base.toml (new file)
- Created configs/README.md documenting usage and pending composition work
- Updated STATUS.md to reflect accurate project state (Phase 4 complete, Phases 5-7 split)
- **Commits (agent-core):** eae879d (@file docs, code-removal fragment), b3a87b3 (configs organization)
- **Commits (claudeutils):** 089225d (remove obsolete consolidation/), d499edf (STATUS update)

**Documentation and fragments:**
- Created agent-core/docs/@file-pattern.md (comprehensive guide from claude-code-guide agent)
- Created agent-core/fragments/code-removal.md (delete obsolete code, don't archive)
- Added code-removal.md reference to claudeutils CLAUDE.md
- Removed plans/unification/consolidation/ directory (43 obsolete design files)

**Current state:**
- agent-core: configs/ directory with 4 base files + README.md
- agent-core: 18 fragments (configs moved out)
- Branch: unification (claudeutils), main (agent-core)
- Phase 4: ✅ Complete (base configs organized)
- Phases 5-7: Split status - CLAUDE.md done (@file), configs pending implementation

## Pending Tasks

**Config composition implementation (Phases 5-7 for configs):**
- Implement justfile import mechanism (projects use inline copies currently)
- Implement pyproject.toml composition (projects use inline copies currently)
- Document config composition pattern once implemented
- See: agent-core/configs/README.md, plans/unification/STATUS.md

## Blockers / Gotchas

**Config composition gap:**
- Native @file only works for markdown files
- Justfile/pyproject.toml need different import mechanism
- Base files organized but not yet consumable by projects
- Original compose.py design may still be needed for config files

## Blockers / Gotchas

**Agent-core template naming:**
- CLAUDE.md files in subdirectories auto-inject into context
- Template must be named CLAUDE.template.md to avoid this
- Copy command: `cp agent-core/templates/CLAUDE.template.md CLAUDE.md`

**Branch state:**
- claudeutils: `unification` branch (clean, 2 commits)
- agent-core: `main` branch (3 commits ahead of origin)

## Next Steps

**Option 1:** Continue with config composition implementation (justfile/pyproject.toml import mechanism)

**Option 2:** Move to next priority work from todo.md:
- Convert agent-core to Claude Code Plugin (High priority)
- Markdown Formatter Survey (High priority)

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

**Delete obsolete code, don't archive:**
- Anti-pattern: Moving obsolete code to archive/, old/, or commenting it out
- Correct pattern: Delete completely - git history is the archive
- Rationale: Dead code creates maintenance burden; git log/show retrieves anything needed
- New fragment: code-removal.md enforces this pattern
