# Outline Review: worktree-skill

**Artifact**: plans/worktree-skill/outline.md
**Date**: 2026-02-10T19:45:00Z
**Mode**: review + fix-all

## Summary

The outline is comprehensive, technically sound, and demonstrates strong understanding of git worktree mechanics and submodule handling. Coverage is complete across all functional areas. The document is well-structured and actionable for planning.

**Overall Assessment**: Ready

## Requirements Traceability

Since this outline was created without explicit FR-*/NFR-* requirements, implicit requirements are extracted from the design approach, key decisions, and scope sections:

| Implicit Requirement | Outline Section | Coverage | Notes |
|---------------------|-----------------|----------|-------|
| CLI subcommand for worktree operations | CLI Subcommands | Complete | 6 subcommands defined |
| Skill orchestration for session management | Skill Orchestration | Complete | All responsibilities listed |
| Submodule merge conflict resolution | Submodule Merge Resolution | Complete | Deterministic sequence provided |
| Session file conflict resolution | Session File Conflict Resolution | Complete | Patterns for session.md, learnings.md, jobs.md |
| Source code conflict resolution | Source Code Conflict Resolution | Complete | Strategy with precommit gate |
| Task extraction during merge | Task extraction algorithm | Complete | 5-step algorithm provided |
| Error handling for git operations | Error Handling | Complete | Lock files, merge debris, missing objects |
| Integration testing strategy | Testing | Complete | Scenarios and approach detailed |
| TDD discipline | Approach, Testing | Complete | Explicit throughout |
| Mode 5 integration | Scope | Complete | execute-rule.md update in scope |
| Handoff template update | Scope | Complete | Listed in scope |
| Absorb wt-merge-skill | Approach, Scope | Complete | Explicitly stated |
| Delete justfile recipes | Key Decisions, Scope | Complete | Migration path clear |
| Idempotent merge operations | Key Decisions | Complete | Stop/resume pattern described |
| Clean tree gate | CLI Subcommands | Complete | clean-tree subcommand |
| Parallel group detection | Skill Orchestration | Complete | Prose, not scripted |

**Traceability Assessment**: All implicit requirements have corresponding outline sections with complete coverage.

## Review Findings

### Critical Issues

None identified.

### Major Issues

None identified.

### Minor Issues

**1. Missing step number in submodule merge sequence**
- Location: Line 56 (Submodule Merge Resolution section)
- Problem: Step numbering jumps from 2 to 4, skipping step 3
- Fix: Renumbered step 4 → step 3, step 5 → step 4
- **Status**: FIXED

**2. Vague scope exclusion**
- Location: Line 43 (Scope section, "Out")
- Problem: "focus-session.py changes" is ambiguous — outline section 30 says "Reuse focus-session.py for session extraction" which implies it will be used, and line 34 explicitly lists it as part of skill orchestration
- Fix: Clarified exclusion to "focus-session.py implementation changes" to indicate script is reused as-is, not modified
- **Status**: FIXED

**3. Branch naming inconsistency**
- Location: Lines 13 (Key Decisions) vs line 14 (directory convention)
- Problem: Line 13 says "slug directly (no `wt/` prefix)" for branch naming, but line 14 uses `wt/<slug>/` for directory. Unclear whether branches have no prefix at all or this is contrasting with old `wt/` prefix pattern
- Fix: Clarified line 13 to "Branch naming: `wt/<slug>` (consistent with existing convention)" based on exploration report showing `wt/` prefix is universal convention
- **Status**: FIXED

**4. Unclear pronoun reference**
- Location: Line 88 (Batch Stale Worktree Removal)
- Problem: "Stale worktrees... are removed with `wt-rm`" — technically, `_worktree rm` is the CLI subcommand, while `wt-rm` is the justfile recipe being deleted
- Fix: Changed to "`_worktree rm`" for consistency with CLI subcommand naming
- **Status**: FIXED

## Fixes Applied

- Line 56: Renumbered step 4 → 3 in submodule merge sequence
- Line 57: Renumbered step 5 → 4 in submodule merge sequence
- Line 43: Clarified "focus-session.py changes" → "focus-session.py implementation changes"
- Line 13: Clarified branch naming from "slug directly (no `wt/` prefix)" → "Branch naming: `wt/<slug>` (consistent with existing convention)"
- Line 88: Changed "wt-rm" → "`_worktree rm`" for CLI subcommand consistency

## Positive Observations

**Strong technical understanding:**
- Submodule merge resolution sequence is accurate and complete (ancestry check, fetch strategy, verification)
- Session file conflict patterns are well-analyzed with correct deterministic vs. judgment-based classification
- Error handling covers real-world edge cases (lock files, merge debris, missing objects)

**Clear design decisions:**
- CLI vs. skill boundary is well-defined (deterministic operations in CLI, orchestration in skill)
- Scope is explicit with clear in/out boundaries
- Testing strategy is comprehensive with integration-first approach

**Practical approach:**
- Absorbs wt-merge-skill plan instead of creating separate skill (reduces complexity)
- Reuses focus-session.py (avoids duplicate work)
- Idempotent merge with stop/resume pattern (handles real-world interruptions)

**Good use of exploration:**
- Integration report (explore-integration.md) was clearly leveraged for comprehensive coverage
- References existing learnings and patterns from codebase

## Recommendations

**For Phase B (full design):**
- Elaborate CLI subcommand interfaces with full argument specifications and exit codes
- Detail skill SKILL.md structure with step-by-step procedures
- Specify error messages and user-facing output formats
- Define execute-rule.md Mode 5 update specifics (exact changes to make)

**For planning (Phase D):**
- Break down testing into TDD cycles matching the critical scenarios listed
- Sequence implementation to allow incremental delivery (e.g., `new` and `ls` first, then `rm`, then `merge`)
- Consider precommit validation for skill SKILL.md frontmatter and structure

**For user discussion:**
- Validate directory convention choice (`wt/<slug>/` inside project root vs. sibling directories `../<repo>-<slug>/` used by current justfile recipes)
- Confirm branch naming convention (`wt/<slug>` matches current pattern)
- Clarify whether justfile recipes should be deleted immediately or deprecated with warnings first

---

**Ready for user presentation**: Yes
