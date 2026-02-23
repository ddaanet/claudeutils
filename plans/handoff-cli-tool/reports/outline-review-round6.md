# Outline Review: handoff-cli-tool (Round 6)

**Artifact**: plans/handoff-cli-tool/outline.md
**Date**: 2026-02-23
**Mode**: review + fix-all

## Summary

Focused review on newly added content: `amend` option (C-5), git CLI output passthrough, submodule output labeling (`agent-core:` prefix), "report deviations only" output principle, and Decision References section. Found 1 major issue (C-5 amend validation logic referenced wrong git command for HEAD commit membership), 2 minor issues (S-3 output format description inconsistent with commit passthrough, Decision References attribution inaccurate for git passthrough entry), and 1 minor completeness gap (C-4 table didn't document amend option orthogonality). All fixed. Existing outline sections from rounds 1-5 remain sound.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements derived from session.md task description and prior round context (no requirements.md). Updated to reflect round 6 changes.

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: `_session` command group (handoff, commit, status) | Approach, S-1 | Complete | Three subcommands with shared infrastructure |
| FR-2: Structured markdown I/O (stdin/stdout, no stderr) | S-3, Input/Output sections | Complete | S-3 convention applied uniformly |
| FR-3: Session.md mechanical writes (handoff) | H-1, H-2, Pipeline | Complete | Domain boundaries explicit |
| FR-4: State caching for retry (handoff) | H-4, Pipeline step 2 | Complete | Cache before first mutation |
| FR-5: Sole commit path with vet check | C-1, C-4, Pipeline | Complete | Terminology consistent |
| FR-6: Submodule coordination | C-2, C-5 | Complete | 4-case truth table + amend propagation rules |
| FR-7: Commit ID in output | Output examples, Output principle | Complete | Short hash in git passthrough `[branch hash]` line; agent extracts |
| FR-8: STATUS rendering (pure data transformation) | Status Pipeline, Output | Complete | No mutations, no stdin |
| FR-9: `-> wt` worktree-destined tasks | S-4, ST-0, H-1, Status Output | Complete | Parser, rendering, domain ownership all addressed |
| FR-10: Parallel detection without model/restart constraints | ST-1 | Complete | Rationale: worktree parallelism eliminates both |
| FR-11: Missing session.md = fatal error | ST-2 | Complete | Exit 2 (input validation) |
| FR-12: `_git()` extraction to shared module | S-2 | Complete | Move from worktree/utils.py |
| FR-13: `--amend` option for commit | C-5, C-4, Input example | Complete | Orthogonal with validation levels, propagation rules documented |
| FR-14: Git CLI output passthrough | Output section, Output principle | Complete | Raw git output on success, no CLI-side parsing |
| FR-15: Submodule output labeling | Output examples, line 194 | Complete | `agent-core:` prefix distinguishes repos |

**Traceability Assessment**: All requirements covered.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **C-5 amend validation uses wrong git command for HEAD commit membership**
   - Location: C-5 (line 291)
   - Problem: Original text said "Validation checks `git status --porcelain` OR `git diff HEAD -- <file>` shows the file in the amended commit." The `git diff HEAD -- <file>` command compares working tree against HEAD — for a file already committed in HEAD with no further changes, this produces empty output (no diff). The intent is to check whether a file is part of the HEAD commit, which requires `git diff-tree --no-commit-id --name-only HEAD` (lists files in the HEAD commit).
   - Fix: Changed to `git diff-tree --no-commit-id --name-only HEAD` with clarified description: "file is part of HEAD commit."
   - **Status**: FIXED

### Minor Issues

1. **S-3 output format description inconsistent with commit passthrough**
   - Location: S-3 (line 49)
   - Problem: S-3 stated "Error output uses `**Header:** content` format (same as success)" — the "(same as success)" parenthetical was incorrect after the output redesign. Commit success output is now raw git passthrough, not `**Header:** content` format. Only error/warning output uses the `**Header:** content` format.
   - Fix: Changed to "Error and warning output uses `**Header:** content` format" and added "Success output varies by subcommand (commit: raw git passthrough; handoff/status: structured markdown)."
   - **Status**: FIXED

2. **C-4 table omitted amend option combinations**
   - Location: C-4 (lines 283-286)
   - Problem: Table listed `amend` and `just-lint + amend` as separate rows but omitted `no-vet + amend` and `just-lint + no-vet + amend`. Since options are orthogonal, enumerating incomplete combinations is misleading.
   - Fix: Removed amend-specific rows from the table. Added prose statement: "Options are orthogonal: `amend` combines with any validation level above" with explicit examples of all valid combinations.
   - **Status**: FIXED

3. **Decision References attribution inaccurate for git passthrough**
   - Location: Decision References, LLM-caller design subsection (line 394)
   - Problem: "Git output passthrough" was listed under `agents/learnings.md` but there is no learnings entry for this concept. It's a design decision made in this outline. The other two entries in the subsection correctly reference real learnings entries but used paraphrased text instead of the actual learning titles.
   - Fix: Added actual learning heading references for the first two entries (`When designing CLI tools for LLM callers`, `When CLI outputs errors consumed by LLM agents`). Changed git passthrough attribution to "design decision, this outline."
   - **Status**: FIXED

## Fixes Applied

- C-5 line 291 — `git diff HEAD -- <file>` changed to `git diff-tree --no-commit-id --name-only HEAD` with clarified description
- S-3 line 49 — Removed "(same as success)" from error format description; added per-subcommand success format note
- C-4 lines 283-286 — Replaced amend-specific table rows with orthogonality statement and examples
- Decision References line 392-394 — Added actual learning heading names; corrected git passthrough attribution

## Positive Observations

- The "report deviations only" output principle (line 176, 241) is well-articulated and consistently applied across all output examples. Success shows only git output; failure shows only the relevant diagnostic. No redundant confirmation.
- Amend propagation rules (C-5) correctly identify the directional dependency: submodule amend forces parent amend (pointer hash changes), but not vice versa. This is a non-obvious interaction documented with precision.
- The `agent-core:` labeling convention is minimal and unambiguous. Placing it before the submodule output block (not inline per-line) keeps the git output intact for agent parsing.
- C-5's message requirement ("Required even with `amend`") prevents `--no-edit` implicit behavior, keeping the LLM caller explicitly in control of the message content.
- Decision References section provides useful implementation guidance without expanding the outline's scope. The `/when` cross-references give implementers a direct lookup path.
- The input example (lines 144-164) now shows `amend` in context, making the combined `no-vet + amend` pattern visible to implementers.

## Recommendations

- The amend success output example (lines 197-202) shows parent-only amend. A submodule+parent amend example could be added for completeness, but the two patterns (submodule labeling, amend output) are independently documented and compose predictably. Not blocking.
- Phase 6 description (line 377) now includes "amend" and "git passthrough" — both new concepts are accounted for in phase planning.

---

**Ready for user presentation**: Yes
