# Design Review: Continuation Passing

**Design Document**: `plans/continuation-passing/design.md`
**Review Date**: 2026-02-09
**Reviewer**: design-vet-agent (opus)

## Summary

Well-structured design for replacing hardcoded skill tail-calls with a hook-based continuation passing system. The three-component architecture (hook parser, cooperative skill protocol, frontmatter declarations) is clean and achieves backward compatibility. All core requirements (FR-1 through FR-7, NFR-1 through NFR-3, C-1, C-2) are addressed with clear design decisions and rationale.

**Overall Assessment**: Needs Minor Changes

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **Inaccurate `/orchestrate` tail-call claim**
   - Problem: Component 3 (line 379 original) stated `/orchestrate` has "End of execution tail-call" as its current location. The actual orchestrate skill has no hardcoded Skill tail-call -- Section 6 "Completion" suggests next actions in prose but never invokes `/handoff --commit` via Skill tool. `/orchestrate` also lacks `Skill` in its `allowed-tools`.
   - Impact: Planner would look for a tail-call section to remove in `/orchestrate` and find nothing, causing confusion or incorrect edits. Missing `Skill` tool would block tail-call execution at runtime.
   - Fix Applied: Updated affected skills list to accurately describe each skill's current state. `/orchestrate` entry now notes "suggests next action but has no hardcoded Skill tail-call; refactoring adds continuation protocol without removing existing tail-call." Added note in Component 3 that `/orchestrate` has no hardcoded tail-call to remove.

2. **`Skill` tool missing from `allowed-tools` not explicitly called out**
   - Problem: Component 2 said "Add `Skill` to `allowed-tools` if not present" without identifying which skills need it. `/design` (`allowed-tools: Task, Read, Write, Bash, Grep, Glob, WebSearch, WebFetch`) and `/orchestrate` (`allowed-tools: Task, Read, Write, Bash(git:*)`) both lack `Skill`. The remaining 4 cooperative skills already have it.
   - Impact: Planner might miss adding `Skill` to these two skills, causing runtime failures when attempting tail-calls.
   - Fix Applied: Added explicit enumeration of which skills need `Skill` tool addition and which already have it.

### Minor Issues

1. **FR-4 simplification not noted in Requirements mapping**
   - Problem: Requirements section listed FR-4 as "addressed by `and\n- /skill` list marker detection" without noting this is a simplification from the requirements' `then:`/`finally:` marker format with per-skill context.
   - Fix Applied: Added parenthetical noting simplification from requirements' format and deferral of cross-session capabilities to orchestrate-evolution.

2. **Missing `systemMessage` design note**
   - Problem: The existing hook (Tier 1/2) emits both `additionalContext` and `systemMessage` in its output. The Tier 3 continuation format only uses `additionalContext`. The design didn't document this deliberate difference.
   - Fix Applied: Added note explaining that Tier 3 omits `systemMessage` because continuation metadata is internal to Claude's processing and should not appear in user UI.

3. **Imprecise tail-call location references**
   - Problem: Several entries in "Affected skills and their current tail-call locations" used vague descriptions (`plan-adhoc`: "Tier 1/2/3 tail-call instructions", `plan-tdd`: "Phase 5 tail-call instructions"). Actual section names are more specific.
   - Fix Applied: Updated to match actual section names (`plan-adhoc`: Step 3 "Tail-call `/handoff --commit`", `plan-tdd`: Step 6 "Tail-call `/handoff --commit`"). Added parenthetical descriptions of what each tail-call does.

## Requirements Alignment

**Requirements Source:** `plans/continuation-passing/requirements.md`

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Yes | D-6 parsing strategy (Mode 2 inline prose) |
| FR-2 | Yes | Architecture (peel-first-pass-remainder) |
| FR-3 | Yes | Cooperative Skill Protocol (consumption protocol) |
| FR-4 | Yes (simplified) | D-6 parsing strategy (Mode 3 multi-line list) |
| FR-5 | Yes | D-7 prose-to-explicit translation + empirical validation |
| FR-6 | Yes | D-5 sub-agent isolation by convention |
| FR-7 | Yes | Cooperative Skill Protocol + frontmatter schema |
| FR-8 | Out of scope | Explicitly deferred (optional in requirements) |
| NFR-1 | Yes | Protocol size (~5-8 lines), no downstream coupling |
| NFR-2 | Yes | Cooperative Skill Registry (3-source discovery) |
| NFR-3 | Yes | D-4 ephemeral continuation lifecycle |
| C-1 | Yes | D-5 + consumption protocol CRITICAL note |
| C-2 | Yes | Empty continuation = terminal |

**Gaps:**
- FR-4 is simplified from the requirements' structured format (`then:`, `finally:` with per-skill context) to list markers (`and\n- /skill`). Design documents this as intentional, deferring cross-session capabilities. Acceptable scope reduction.
- Requirements OQ-3 (error mid-chain) addressed as deferred to error handling framework. Design notes chain terminates on error (C-2 compliance).

## Positive Observations

- **Backward compatibility is thoroughly analyzed.** The default-exit appending mechanism means solo skill invocations behave identically to current hardcoded tail-calls. Migration is zero-risk for existing workflows.
- **Rollback strategy is clean.** Removing Tier 3 from hook makes the entire system inert -- frontmatter is ignored, continuation protocol sections become no-ops.
- **Three-source registry discovery is well-researched.** The plugin scope filtering (user vs. project, enabled/disabled) shows awareness of the real-world complexity. Session history confirms this was validated through 3 rounds of user feedback.
- **Edge cases are enumerated.** Path disambiguation, connecting words in args, terminal detection, and unknown skills in chains are all addressed.
- **Transport format is pragmatic.** `[CONTINUATION: ...]` bracket-delimited suffix in args avoids JSON parsing complexity while being unambiguous.
- **Empirical validation protocol (FR-5)** with explicit false-positive/false-negative targets and session corpus testing shows rigor.

## Recommendations

1. **Consider testing `/orchestrate` continuation flow.** Since `/orchestrate` differs from other skills (no existing tail-call, adding continuation from scratch), an integration test specifically covering the orchestrate link in a chain would catch protocol misunderstanding.

2. **Module extraction threshold.** Design suggests extracting to `continuation_parser.py` "if complexity warrants" for Component 1 (hook modification adding ~120-150 lines to ~100-line script). Given the script more than doubles in size, extraction is likely warranted. Planner should plan for the extracted module from the start rather than treating it as optional.

3. **`/handoff` flag-dependent default exit.** The special case where `/handoff` with vs. without `--commit` has different default exits adds parsing complexity. Consider whether frontmatter can express this (e.g., `default-exit-conditional`) rather than hardcoding the flag check in the hook. This would keep the hook generic and make the behavior discoverable from frontmatter alone.

## Next Steps

1. Route to `/plan-adhoc` for runbook creation as specified in design's Next Steps
2. Load `plugin-dev:skill-development` before planning (skill frontmatter modifications)
3. All fixes applied -- no blocking issues remain
