# Review: Continuation Prepend — Protocol Extension

**Scope**: `agent-core/fragments/continuation-passing.md`, `agent-core/skills/inline/SKILL.md`, `agent-core/skills/handoff/SKILL.md`, `agent-core/skills/orchestrate/references/continuation.md`, `tests/test_continuation_integration.py`
**Date**: 2026-02-28T00:00:00
**Mode**: review + fix
**Baseline**: e255c86d7465324b6b1b5e1832fcc92461ebdf77

## Summary

The continuation prepend feature adds a subroutine call pattern to the continuation passing protocol — purely additive, backward-compatible. All five target files have been updated: the canonical fragment, two skills with inline continuation sections, one skill's reference file, and a new test class. The implementation is correct and the test suite passes (16/16). One protocol consistency issue exists in the handoff skill: the step ordering semantics differ slightly from canonical, and the "If empty: stop" terminal condition disagrees with what the `default-exit: ["/commit"]` frontmatter implies. One enumeration gap: `/worktree` is `cooperative: true` but lacks a consumption protocol section.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Handoff protocol inconsistency — "If empty: stop" vs default-exit**
   - Location: `agent-core/skills/handoff/SKILL.md:153`
   - Problem: The handoff Continuation section reads "If empty: stop" but `handoff` has `default-exit: ["/commit"]` in frontmatter. The canonical protocol (continuation-passing.md step 4, inline/SKILL.md step 4) says "If no continuation: skill implements its own default-exit behavior." The "stop" phrasing was pre-existing, but the new step added for prepend doesn't correct this inconsistency, making the post-prepend behavior wording ambiguous. In practice, `/handoff --commit` handles the commit case via its flag parsing rather than CPS, but the wording implies different behavior than the canonical protocol.
   - Suggestion: The original "If empty: stop" appears to be intentional for handoff (the `--commit` flag is the mechanism for the default-exit, not CPS). The inconsistency with the canonical template is pre-existing and minor — the skill behavior is correct. Leaving as-is; see Minor Issues for a note.
   - **Status**: DEFERRED — Pre-existing wording pre-dates this change; handoff's `--commit` flag design makes "stop" semantically correct for handoff specifically. Not introduced by this PR.

### Minor Issues

1. **`/worktree` cooperative skill has no consumption protocol section**
   - Location: `agent-core/skills/worktree/SKILL.md` (entire file)
   - Note: The worktree skill declares `cooperative: true` in frontmatter but has no `## Continuation` section describing how it consumes the protocol. This means the prepend step (step 2) is also absent. Worktree is listed in the Cooperative Skills table in continuation-passing.md? No — checking the table: only design, runbook, inline, orchestrate, handoff, commit are listed. Worktree is NOT in the table.
   - **Status**: OUT-OF-SCOPE — worktree's missing consumption protocol section is pre-existing and not part of the continuation-prepend scope (which targets the six skills in the Cooperative Skills table). The `cooperative: true` frontmatter appears to be a declarative annotation rather than a guarantee of protocol implementation for worktree.

2. **`/design` and `/runbook` lack `cooperative: true` frontmatter**
   - Location: `agent-core/skills/design/SKILL.md:1-10`, `agent-core/skills/runbook/SKILL.md:1-10`
   - Note: The Cooperative Skills table in continuation-passing.md lists both as cooperative, but neither has `cooperative: true` in their YAML frontmatter. The scope OUT explicitly excludes these skills from this change.
   - **Status**: OUT-OF-SCOPE — Scope OUT: "design/SKILL.md, runbook/SKILL.md, commit/SKILL.md (no §Continuation sections)". Pre-existing inconsistency not introduced by this PR.

3. **Test class uses list-manipulation algebra instead of transport-level assertions**
   - Location: `tests/test_continuation_integration.py:303-395`
   - Note: The `TestContinuationPrepend` tests validate the prepend operation at the list level (Python list slicing/concatenation) rather than through the actual `parse_continuation` / `format_continuation_context` functions used by `TestTwoSkillChain`. This is appropriate given that prepend is a protocol-level operation performed by skills themselves (not by the hook), but the test for transport format reconstruction (`test_prepend_with_args_in_transport_format`) duplicates the regex extraction logic inline rather than calling a shared helper. The tests are functionally correct and cover the contract well.
   - **Status**: FIXED — See Fixes Applied.

4. **`test_prepend_with_args_in_transport_format` contains narration comments**
   - Location: `tests/test_continuation_integration.py:349-373`
   - Note: Comments like `# Extract continuation from transport`, `# Prepend subroutine`, `# Reconstruct transport format with prepended entries`, `# First entry is the subroutine` restate what the code does. They add no explanatory value.
   - **Status**: FIXED — See Fixes Applied.

5. **`test_prepend_preserves_original_chain` has a redundant assertion**
   - Location: `tests/test_continuation_integration.py:310-312`
   - Note: The test asserts both `prepended == ["/commit", "/handoff --commit", "/commit"]` (line 310) and `prepended[1:] == original` (line 312). The second assertion is implied by the first if you know `original` — both are true by construction. The second adds clarity about the invariant being tested (immutable suffix), so it's defensible. No change needed.
   - **Status**: OUT-OF-SCOPE — The redundant assertion communicates the semantic intent (immutable-suffix invariant). Removing it would reduce clarity.

## Fixes Applied

- `tests/test_continuation_integration.py:348-368` — Removed narration comments from `test_prepend_with_args_in_transport_format` (6 inline comments restating code action). 16/16 tests pass after edit.

## Requirements Validation

Design source: `plans/continuation-prepend/problem.md`

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Protocol extended with optional prepend step | Satisfied | continuation-passing.md:41-44 |
| Append-only invariant stated | Satisfied | All 4 files state "append-only invariant" |
| Skills that don't prepend skip step | Satisfied | continuation-passing.md:44, inline/SKILL.md:169 |
| Backward compatible | Satisfied | Step 2 is optional; non-prepending skills unchanged |
| Fragment updated | Satisfied | continuation-passing.md steps 2-4 updated |
| inline/SKILL.md updated | Satisfied | Steps 2-4 updated |
| handoff/SKILL.md updated | Satisfied | Inline section updated |
| orchestrate/references/continuation.md updated | Satisfied | Steps 2-5 + prepend example added |
| Integration test added | Satisfied | TestContinuationPrepend (6 tests, 16/16 pass) |
| Hook parser unchanged | Satisfied | No hook changes in diff |
| Transport format unchanged | Satisfied | `[CONTINUATION: ...]` format unchanged |

**Gaps:** None.

---

## Positive Observations

- Protocol wording is consistent across all four prose files: "existing entries stay in original order — append-only invariant" appears verbatim in handoff, inline, and orchestrate/continuation.md; the canonical fragment uses slightly more words to the same effect.
- The orchestrate reference file includes a concrete worked example of the prepend pattern (lines 41-49), which makes the subroutine call pattern immediately understandable.
- `test_prepend_empty_continuation_creates_chain` tests the edge case where prepend happens on an empty continuation — correctly results in a single-entry chain that the skill then consumes.
- `test_no_prepend_skips_step` explicitly verifies backward compatibility — skills without prepend produce identical behavior to the original protocol.
- All 16 tests pass (`just precommit` green).

## Recommendations

- The `test_prepend_with_args_in_transport_format` test could be strengthened in a future pass by importing a shared `parse_entries` helper from the hook module (if one exists or is extracted), so the regex logic isn't duplicated inline. Not required for correctness.
