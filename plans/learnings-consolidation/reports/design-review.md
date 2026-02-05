# Design Review: Learnings Consolidation

**Design Document**: plans/learnings-consolidation/design.md
**Review Date**: 2026-02-06
**Reviewer**: design-vet-agent (opus)

## Summary

This design automates learnings consolidation during handoff by inserting a new step 4c that conditionally delegates to a remember-task agent. The architecture is well-structured with clear separation between age calculation (script), trigger evaluation (handoff skill), and consolidation execution (agent). The design addresses all 9 functional and 3 non-functional requirements with thorough rationale for each decision.

**Overall Assessment**: Needs Minor Changes

All issues have been fixed directly in the design document.

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **D-4: Prolog pattern inconsistency and Skill tool claim**
   - Problem: D-4 opened with "prolog directive" as if it were an existing mechanism, then a note on line 150 contradicted this by saying "Claude Code does not currently have a formal 'prolog' injection mechanism." Additionally, the claim that "Sub-agents cannot invoke the Skill tool (MCP limitation)" is contradicted by existing agents (`quiet-task.md`, `tdd-plan-reviewer.md`) which list "Skill" in their tools array. The MCP limitation applies to MCP-provided tools, not necessarily the built-in Skill tool.
   - Impact: Planner would face conflicting guidance -- design says "prolog injection" but also says it doesn't exist. The incorrect Skill tool claim could lead to unnecessary workarounds.
   - Fix Applied: Rewrote D-4 as "Agent Pattern -- Embedded Skill Protocol". Removed the false claim about Skill tool unavailability. Clarified that the implementation embeds protocol sections directly in the agent definition. Added synchronization risk note and source-comment pattern for maintenance.

2. **D-6: Retry mechanism underspecified**
   - Problem: D-6 flow step 6 said "Remember-task processes remaining entries with updated targets" without explaining the mechanics. The handoff skill step 4c said "delegate to memory-refactor agent, then retry" without specifying what "retry" means -- a second remember-task invocation? With which entries?
   - Impact: Planner would have to guess the retry implementation, risking duplicate processing of already-consolidated entries.
   - Fix Applied: Expanded D-6 flow to 7 steps with explicit retry scope. Added "Retry scope" paragraph clarifying only skipped entries are retried. Updated handoff skill step 4c to match ("re-invoke remember-task with only the skipped entries").

### Minor Issues

1. **Section cross-references used non-existent names**
   - Problem: FR-* entries referenced sections like "Handoff Integration", "Age Calculation Script", "Trigger Logic", "Pre-Consolidation Checks", "Remember Task Agent", "Remember Skill Update" -- none of which match actual section headings in the design.
   - Fix Applied: Updated all FR-* cross-references to use actual section identifiers (e.g., "Implementation Component 4", "D-3", "D-5").

2. **Script output format missing line count for size trigger**
   - Problem: The handoff skill trigger logic requires the total line count of learnings.md for the size trigger (150 lines), but the script output format in D-2 didn't include it. The handoff would need to separately run `wc -l` or parse the file, defeating the purpose of having the script as the data provider.
   - Fix Applied: Added `**File lines:** 101` to the script output format example.

3. **Staleness calculation algorithm imprecise**
   - Problem: Algorithm step 4 described detecting consolidation via `git log --diff-filter=M -1 -- agents/learnings.md` "with content analysis", but `--diff-filter=M` just means "modified" which applies to almost every commit touching the file. The actual signal (H2 headers being removed) was not specified. Also the fallback "report staleness as total active days" could produce misleading numbers.
   - Fix Applied: Changed method to walk `git log -p` looking for diffs with removed H2 headers (`-## ` lines). Updated fallback to report "unknown (no prior consolidation detected)" instead of a potentially misleading number.

4. **Tool constraints update lacked current state**
   - Problem: The note about updating handoff skill allowed-tools mentioned what to add but not the current baseline, making it unclear what the resulting tools list should be.
   - Fix Applied: Added current `allowed-tools` value (`Read, Write, Edit, Bash(wc:*), Skill`) to the note so the planner knows the full before/after.

5. **Added formal Requirements Traceability table**
   - Problem: Design had FR-* identifiers in the Requirements section with prose cross-references, but no structured traceability matrix mapping each requirement to its design element.
   - Fix Applied: Added a Requirements Traceability section with table mapping all FR-1 through FR-9 and NFR-1 through NFR-3 to specific design decisions and implementation components.

## Requirements Alignment

**Requirements Source:** plans/learnings-consolidation/requirements.md

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Yes | Implementation Component 4 (Handoff Skill Modification) |
| FR-2 | Yes | Implementation Component 1 (learning-ages.py), D-2 |
| FR-3 | Yes | D-3 (Trigger Evaluation), Implementation Component 4 |
| FR-4 | Yes | D-5 (Pre-Consolidation Check Strategy) |
| FR-5 | Yes | D-5 (Pre-Consolidation Check Strategy) |
| FR-6 | Yes | D-5 (Pre-Consolidation Check Strategy) |
| FR-7 | Yes | D-6 (Memory Refactoring Trigger), Implementation Component 3 |
| FR-8 | Yes | D-4 (Embedded Skill Protocol), Implementation Component 2 |
| FR-9 | Yes | Implementation Component 5 (Remember Skill Update) |
| NFR-1 | Yes | D-7 (Failure Handling) |
| NFR-2 | Yes | Implementation Component 2 (model: sonnet) |
| NFR-3 | Yes | Implementation Component 2 (report to tmp/consolidation-report.md) |

**Gaps:** None. All requirements have corresponding design elements.

## Positive Observations

- **Two-test model is well-reasoned.** The separation of trigger (IF) and freshness (WHAT) is a clean decomposition that prevents the common anti-pattern of conflating "should we run?" with "what should we process?"
- **Git-active-day time unit is excellent.** Calendar days would create false urgency after vacations and miss burst coding sessions. Active days correctly measure "operator engagement time."
- **Threshold constraint is smart.** Staleness (14) > freshness (7) prevents the pathological case where consolidation triggers immediately after its own completion creates entries that trigger again.
- **Failure handling is appropriately conservative.** NFR-1 (consolidation failure must not block handoff) is the right default for an automation that augments a manual process.
- **Documentation Perimeter is thorough.** All 7 required-reading files verified to exist. Skill loading directives present and correct for the two plugin topics (skill-development, agent-development).
- **Pre-consolidation checks have correct bias.** Preferring escalation over silent errors matches the "false negatives are worse" principle for knowledge management.
- **D-7 failure mode table is comprehensive.** Covers script failure, no qualifying entries, batch too small, agent error, contradiction, and file limits -- good coverage of the failure space.

## Recommendations

1. **Verify Skill tool availability in sub-agents.** The design now avoids depending on it, but the underlying question remains open. A quick test (spawn a Task agent with Skill in tools, attempt to invoke a skill) would resolve the ambiguity for future designs.
2. **Consider staleness detection robustness.** The heuristic of finding removed H2 headers works for the remember workflow, but could false-positive on manual edits that rename headers. The planner should consider whether this matters in practice (likely not, given the 14-day threshold is generous).
3. **Agent synchronization maintenance.** The embedded protocol in remember-task.md will drift from the remember skill over time. Consider adding a validator check or at minimum a dated comment in the agent definition (e.g., `<!-- Synced from SKILL.md as of 2026-02-XX -->`).

## Next Steps

1. Design is ready for planning -- route to `/plan-adhoc` as specified
2. Load `plugin-dev:skill-development` and `plugin-dev:agent-development` before planning
3. All fixes have been applied to the design document
