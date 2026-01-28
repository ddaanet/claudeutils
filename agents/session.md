# Session Handoff: 2026-01-28

**Status:** Native @file pattern adopted, additional refactoring in progress

## Completed This Session

**Native @file discovery and refactoring:**
- Discovered Claude Code native support for `@file` references (recursive, 5 levels deep)
- **Phase 5-7 obsolete:** compose.py system not needed - native @file achieves goal
- Refactored CLAUDE.md to use @file references (proof of concept)
  - 4 fragments extracted: communication.md, bash-strict-mode.md, delegation.md, tool-batching.md
  - Added section headings before @file references for proper hierarchy
  - Review confirmed: structure correct, wording quality preserved
- Updated plans/unification/STATUS.md with native @file finding
  - Documented capabilities: recursive inclusion, circular detection, code block protection
  - Marked Phase 5-7 as "Superseded by Native Feature"
  - Updated recommendations: adopt native @file pattern

## Pending Tasks

### Additional CLAUDE.md Refactoring
**User request:** Further extract reusable rules to agent-core fragments

**Planned extractions:**
1. **Workflow + terminology fragment** - Workflow Selection and Terminology sections relate to agent-core skills
2. **Token economy fragment** - Token economy + avoid numbered lists rules
3. **Reusable rules to extract:**
   - Error handling (generic pattern)
   - Project tmp/ rule (filesystem constraint)
   - Execute rule (session management)
4. **Remove agent-core path rule** - Project was renamed to avoid confusion
5. **Orchestration fragment consolidation:**
   - Add Script-First Evaluation to orchestration/delegation fragment
   - Add Pre-Delegation Checkpoint
6. **Commit agent delegation pattern:**
   - Mostly superseded by improvements in /commit and /commit-context skills
   - Consider improving commit skills with tee/filter scripts to match delegation pattern
   - Not clear if worthwhile - needs evaluation

**After refactoring:** Commit changes

### pytest-md Submodule Update
- Update pytest-md agent-core submodule (36 commits behind)
- Refactor pytest-md CLAUDE.md to use @file references
- Document @file pattern for future projects

## Blockers / Gotchas

**None currently.**

**Branch state:**
- Current: `skills`
- Working tree: CLAUDE.md and STATUS.md have uncommitted changes

## Next Steps

1. Complete additional CLAUDE.md refactoring per user request
2. Commit refactoring changes
3. Update pytest-md submodule
4. Refactor pytest-md CLAUDE.md

**Reference:**
- Native @file documentation: plans/unification/STATUS.md (Native @file Feature Discovery section)
- Current fragments: agent-core/fragments/

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
