# Outline Review: handoff-cli-tool (post-/proof)

**Artifact**: plans/handoff-cli-tool/outline.md
**Date**: 2026-03-13T19:06:45Z
**Mode**: review + fix-all
**Context**: /proof changes applied — flat CLI, flat package layout, `_git changes`, completed entries as `### `, H-3 learnings token weight, `no-edit` option, strip git `hint:` lines, C-1 agent-core scripts, C-4 amend removed from table, C-5 amend validation state, Stop hook `systemMessage`, ANSI colors, suppress redundant Next, ST-1 ordering/cap/first-group, ST-2 no backward compat, Decision References killed, Phase Notes kept.

## Summary

All /proof changes are correctly reflected in the outline. Found two major issues not introduced by /proof: (1) `_git changes` CLI registration was omitted from S-1's registration note, leaving implementers without a structural home for the command; (2) the `_status` output section omitted the session continuation header ("Session: uncommitted changes") required by execute-rule.md MODE 1 format. Found two minor issues: H-3's diagnostics table conflated the failure-path and success-path output, and the learnings age condition was inconsistent between the pipeline step 5 and H-3 table. All issues fixed.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements derived from brief.md, prior review rounds, execute-rule.md MODE 1, and task prompt. No requirements.md exists; this is the established approach for this plan.

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: `_handoff`, `_commit`, `_status` top-level commands (flat) | Approach, S-1 | Complete | Flat CLI confirmed; `_session` group rejected |
| FR-2: Structured markdown I/O (stdin/stdout, no stderr) | S-3, Input/Output sections | Complete | S-3 convention applied uniformly |
| FR-3: Session.md mechanical writes (handoff) | H-1, H-2, Pipeline | Complete | Domain boundaries explicit |
| FR-4: State caching for retry (handoff) | H-4, Pipeline step 2 | Complete | Cache before first mutation |
| FR-5: Sole commit path with vet check | C-1, C-4, Pipeline | Complete | Vet check covers agent-core scripts |
| FR-6: Submodule coordination | C-2, C-5 | Complete | 4-case truth table + amend propagation |
| FR-7: Commit ID in output | Output examples, Output principle | Complete | Short hash in git passthrough line |
| FR-8: STATUS rendering (pure data transformation) | Status Pipeline, Output | Complete | No mutations, no stdin |
| FR-9: `→ wt` worktree-destined tasks | S-4, ST-0, H-1, Status Output | Complete | Parser, rendering, domain ownership addressed |
| FR-10: Parallel detection | ST-1 | Complete | Consecutive-task ordering, cap 5, first eligible group |
| FR-11: Missing session.md = fatal error | ST-2 | Complete | Exit 2 (input validation) |
| FR-12: `_git()` extraction to shared module | S-2 | Complete | Move from worktree/utils.py |
| FR-13: `--amend` option | C-5, C-4, Input example | Complete | Orthogonal with validation levels, no inherited validation state |
| FR-14: Git CLI output passthrough | Output section, Output principle | Complete | Raw git output on success, strip hint: lines |
| FR-15: Submodule output labeling | Output examples | Complete | `<path>:` prefix distinguishes repos |
| FR-16: `_git changes` unified view | S-5, Scope | Complete | CLI registration now specified in S-1 (fixed) |
| FR-17: Session continuation header in STATUS | Status Output | Complete | Added via fix — conditional on dirty tree |
| FR-18: `no-edit` option for amend | C-5, Options section | Complete | `## Message` omitted when `amend + no-edit` |
| FR-19: Completed entries as `### ` headings | Input section | Complete | Explicitly stated |
| FR-20: Learnings token weight diagnostic | H-3 | Complete | Severity warning above 5k tokens |
| FR-21: Stop hook integration via systemMessage | Status Output | Complete | Zero agent token waste path documented |
| FR-22: ANSI colors in status output | Status Output | Complete | Line 311 |
| FR-23: ST-2 old format = fatal error (no backward compat) | ST-2 | Complete | Missing metadata is exit 2 |

**Traceability Assessment**: All requirements covered.

## Scope-to-Component Traceability

| Scope IN Item | Component | Notes |
|---------------|-----------|-------|
| `_handoff` command | H-1 through H-4 + Pipeline | Direct match |
| `_commit` command | C-1 through C-5 + Input/Output | Direct match |
| `_status` command | ST-0 through ST-2 + Pipeline/Output | Direct match |
| Shared session.md parser | S-4 | Direct match |
| `_git()` extraction to `claudeutils/git.py` | S-2 | Direct match |
| Git changes utility (`_git changes`) | S-5, S-1 (registration fixed) | Registration added |
| Tests (CliRunner + real git repos) | Phase Notes (phases 1-7 all TDD) | Direct match |
| Registration in main `cli.py` | S-1 | Direct match |

**Scope Assessment**: All items assigned. No orphans.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **`_git changes` CLI registration missing from S-1**
   - Location: S-1 Registration note (line 26 in original)
   - Problem: S-5 defines `claudeutils _git changes` as a top-level CLI command consumed by skills and the handoff CLI, but S-1's registration note only listed `_handoff`, `_commit`, `_status`. Implementers reading S-1 would not know where to register the `_git changes` command — it would likely be orphaned or incorrectly implemented as a standalone script.
   - Fix: Extended S-1 registration note to specify `_git changes` as a sub-command of a `_git` Click group, also registered in main `cli.py`.
   - **Status**: FIXED

2. **Status output missing session continuation header**
   - Location: `_status` Output section
   - Problem: The execute-rule.md MODE 1 STATUS format includes a conditional "Session: uncommitted changes — `/handoff`, `/commit`" header (shown when git tree is dirty, with `review-pending` extension). The `_status` output section and example omitted this entirely — no mention of the condition, format, or `review-pending` extension. Since `_status` is designed to fully replace agent-generated STATUS output (Stop hook path), the omission would produce incomplete output compared to the spec.
   - Fix: Added session continuation header documentation in the output improvements list and added the header line to the output example.
   - **Status**: FIXED

### Minor Issues

1. **H-3 table conflated failure-path and success-path output**
   - Location: H-3 (Diagnostic output)
   - Problem: The table was labeled "Diagnostic output" (implying step 6 post-success), but "Precommit result: Always" implied it covered both paths. This conflation made it hard to reason about which output appears in which pipeline path. Additionally, step 5 failure emits "precommit result + learnings age" unconditionally, but H-3 listed learnings age as conditional on "≥7 active days" — consistent only for the success path.
   - Fix: Added a preamble distinguishing failure path (step 5) and success path (step 6). Expanded table with Path column. Clarified that learnings age is emitted always on failure, conditionally on success.
   - **Status**: FIXED

### Observations

The /proof review changes are all correctly reflected. Specific checks:
- `_session` group references removed; flat commands throughout
- `no-edit` option present in Options section and C-5
- `## Message` optional with `amend + no-edit` explicit at line 165
- git `hint:` stripping at line 236
- C-1 agent-core script patterns at lines 254-255
- C-4 table has no amend rows; orthogonality stated
- C-5 "inherits no validation state" explicit
- `systemMessage` in status output section
- ANSI colors noted
- Next section suppression documented
- ST-1 consecutive ordering, cap 5, first eligible group
- ST-2 fatal errors for both missing file and old format
- Decision References section absent
- Phase Notes present

## Fixes Applied

- S-1 registration note — Added `_git changes` as sub-command of `_git` Click group in main `cli.py`
- Status Output section — Added session continuation header documentation and example line
- H-3 table — Added Path column, preamble distinguishing failure/success paths, corrected learnings age condition per path

## Positive Observations

- The C-5 amend validation amendment check uses the correct `git diff-tree --no-commit-id --name-only HEAD` command (fixed in round 6). No regression here.
- ST-1 ordering constraint ("only consecutive independent tasks form a group") is a meaningful and precise spec — avoids implementation ambiguity about which tasks qualify.
- The "report deviations only" output principle applied consistently across all failure/success examples in `_commit`.
- Phase Notes phasing is well-matched to dependency order: shared infrastructure (1) → status pure function (2) → handoff mutations (3) → commit parsing (4-5) → commit pipeline (6) → integration (7).

## Recommendations

- The `_git` Click group name could conflict with the `_git()` Python function name. Implementers should be aware of the distinction — `_git` as a CLI command group (user-facing underscore convention) vs `_git()` as an internal subprocess helper function. No outline change needed (both names are established), but worth noting.
- S-4 parser ordering decision (brief.md: regex-first vs AST-first) is deferred. The outline correctly reflects regex-first per current plan. If the markdown-ast-parser plan ships before S-4 implementation begins, brief.md should be updated.

---

**Ready for user presentation**: Yes
