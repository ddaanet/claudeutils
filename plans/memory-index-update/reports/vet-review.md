# Vet Review: Memory Index Update Implementation

**Scope**: Uncommitted changes to learnings.md, memory-index.md, and agent-core submodule validators
**Date**: 2026-02-03T14:30:00-08:00

## Summary

The implementation completed format migrations successfully (bare lines in index, `## Title` headers in learnings, validator regex updates) but **failed to execute the recovery plan's core requirement**: adding index entries for all semantic headers. The index has ~145 entries but most are existing entries from before this work. Per the recovery plan, the index should grow from ~24 to ~140-150 entries by adding all semantic headers from `agents/decisions/*.md`. This did not happen.

**Overall Assessment**: Needs Significant Changes

## Issues Found

### Critical Issues

1. **Index expansion not executed**
   - Location: agents/memory-index.md
   - Problem: Recovery plan Step 4 requires "add bare line entry to memory-index.md for each semantic header" with scope of ~100-120 semantic headers to add. The index only grew by ~10-15 entries in the "Learnings from Sessions" section (copying learnings.md titles). All semantic headers from agents/decisions/architecture.md and agents/decisions/workflows.md are missing from the index.
   - Fix: Execute recovery plan Step 2 (collect all semantic headers from indexed files) and Step 4 (add index entries for each). Examples of missing entries: "Minimal `__init__.py`", "Private helpers stay with callers", "Path encoding algorithm", "Oneshot workflow pattern", "TDD workflow integration", etc. — dozens of semantic headers with zero index entries.

2. **Structural markers not applied**
   - Location: agents/decisions/*.md files
   - Problem: Recovery plan Step 3 requires marking genuinely structural headers with `.` prefix. No changes to decision docs visible in diff. Headers like "Files Modified", "Implementation", metadata tables should be marked as `.` structural per recovery plan judgment criteria.
   - Fix: Read agents/decisions/architecture.md and agents/decisions/workflows.md, identify genuinely structural headers (TOCs, revision history, "Files Modified" sections, navigation headers), add `.` prefix to those headers only.

3. **Validator logic error in orphan detection direction**
   - Location: agent-core/bin/validate-memory-index.py:110-124
   - Problem: Orphan check logic reversed. Lines 110-116 report "orphan semantic header" for headers without index entries (correct direction), but lines 118-124 report "orphan index entry" for entries without matching headers. This is backwards — design D-5 says orphan semantic headers block commit, not orphan index entries. Index entries can reference content without headers (prose in semantic sections).
   - Fix: Remove lines 118-124 (orphan index entry check). Only check headers → index direction (lines 110-116 are correct). Index entries don't need matching headers — they can reference prose content within semantic sections.

4. **Remember skill not updated**
   - Location: agent-core/skills/remember/ (not found in diff)
   - Problem: Recovery plan Step 5 specifies updating remember skill template. The diff shows handoff skill updated but no changes to remember skill. The remember skill is what agents use to consolidate learnings into permanent docs — it needs the `## Title` format template.
   - Fix: Update agent-core/skills/remember/SKILL.md template to use `## Title` format for new learning entries, matching the handoff skill change.

### Major Issues

1. **Bare line format inconsistent with design example**
   - Location: agents/memory-index.md:13-159
   - Problem: Design D-3 example shows entries like "Tool batching unsolved — docs unreliable, hookify bloats context" (keyword phrase after em-dash). Current index has many entries without em-dash descriptions: "Tool batching unsolved" (line 13), "Delegation with context" (line 14), etc. The em-dash description provides keyword richness for discovery.
   - Suggestion: Add em-dash descriptions to bare entries. Example: "Tool batching unsolved — documentation unreliable, hookify bloats, pending exploration" or "Delegation with context — don't delegate when context loaded".

2. **Document intro exemption not validated**
   - Location: agent-core/bin/validate-memory-index.py:54-71
   - Problem: Design D-2 says "content between # title and first ## is document intro — exempt from orphan check". Validator code lines 54-71 tracks `in_doc_intro` state but only uses it to skip content lines, not to validate the exemption. No test verifies that prose between `# Title` and first `##` doesn't trigger orphan errors.
   - Suggestion: Add test case with prose in document intro section to verify exemption works. Current validator logic looks correct but untested.

3. **Validator pattern allows false positives**
   - Location: agent-core/bin/validate-memory-index.py:36-50
   - Problem: Index entry extraction (lines 36-50) uses bare line detection: any non-header, non-bold, non-empty line in a section is treated as index entry. This will match accidental prose like "Prefer retrieval-led reasoning over pre-training knowledge." (line 3 of memory-index.md). That line is in the preamble, not in a section, so current logic skips it, but if it appeared in a section it would be treated as an index entry.
   - Suggestion: Add validation that index entries either have em-dash separator OR are short (≤8 words). Long prose sentences are likely not index entries.

4. **Learnings validator skips preamble incorrectly**
   - Location: agent-core/bin/validate-learnings.py:22-25
   - Problem: Hard-coded "skip first 10 lines" to avoid preamble. Fragile — if preamble grows to 11 lines, first learning gets skipped. The old pattern used title format heuristic which was self-documenting. New pattern needs content-aware skip (e.g., skip until first `## ` header).
   - Suggestion: Change line 22-25 from `if i <= 10: continue` to `if not seen_first_header: [detect ## header, set flag, continue]`. More robust than line number counting.

### Minor Issues

1. **Index entry word count exceeds soft limit**
   - Location: agents/memory-index.md:60-62
   - Problem: "Problem", "Solution", "Design decisions" (lines 60-62) are 1-2 word entries, not 8-12 word keyword phrases. These look like orphan headers or structural section markers that shouldn't be in the index.
   - Note: Verify these are intentional entries. If they reference headers in architecture.md subsections, they're correct but too terse for keyword matching. Add context: "Problem — markdown cleanup Claude output", "Solution — preprocessor before dprint".

2. **Retrieval directive placement**
   - Location: agents/memory-index.md:3
   - Problem: Design D-3 pending item says "Move retrieval directive to .claude/rules/memory-index.md". It's currently in the index file header (line 3). This is a design decision to defer, not an implementation issue, but worth noting.
   - Note: Current placement is acceptable per design D-3 ("Retrieval directive stays in index header"). No action needed unless design changes.

3. **Handoff template missing blank line guidance**
   - Location: agent-core/skills/handoff/SKILL.md:105
   - Problem: Template note says "No blank line after ## Title header" but doesn't explain why (preserves line count for 80-line soft limit). Without rationale, agents might ignore it as arbitrary formatting.
   - Suggestion: Extend note to "No blank line after ## Title header (preserves line count for 80-line soft limit)."

4. **Submodule dirty state**
   - Location: agent-core submodule (git diff shows -dirty suffix)
   - Problem: Submodule has uncommitted changes. This is normal during development but should be cleaned up before final commit.
   - Note: Standard workflow — commit submodule first, then commit parent with pointer update. Not an implementation issue but a commit-time consideration.

## Positive Observations

- **Format migration executed correctly**: Bare line format (no list markers) consistently applied in memory-index.md, all 24 learnings converted to `## Title` format without blank lines
- **Validator regex patterns correct**: `SEMANTIC_HEADER = re.compile(r'^(##+) ([^.].+)$')` correctly matches ##+ followed by non-dot character, `STRUCTURAL_HEADER` correctly detects `.` prefix
- **Token economy preserved**: Bare lines save 14% tokens vs list markers, `## Title` format more efficient than `**Title:**` format
- **Handoff skill template updated**: Learning format template changed from `**[Learning title]:**` to `## [Learning title]` with rationale note
- **Document intro exemption implemented**: Validator tracks `in_doc_intro` state correctly (lines 54-71), skips content between `# Title` and first `##`
- **Clean validator output**: Both validators run without errors on current state (0 errors reported), indicating format migrations are syntactically valid even though index expansion is incomplete

## Recommendations

1. **Execute recovery plan in full**: The implementation completed Steps 1 (format changes), 6 (validate), and partial Step 5 (remember skill). Still missing: Step 2 (collect semantic headers), Step 3 (apply structural markers), Step 4 (add index entries), complete Step 5 (remember skill). The core value of this work — extensive index for ambient awareness — is missing until Step 4 completes.

2. **Fix validator orphan direction**: Remove orphan index entry check (lines 118-124 of validate-memory-index.py). Only semantic headers without index entries should block commit, not vice versa. Index entries can reference prose content.

3. **Add em-dash descriptions to bare entries**: Many index entries lack the keyword-rich description that design D-3 specifies. Review all bare entries and add em-dash descriptions to improve discovery surface.

4. **Validate structural header judgment**: When applying `.` prefix to genuinely structural headers (Step 3), document judgment criteria in commit message. Examples: "Files Modified" sections are structural (meta-info), "Pydantic for validation" subsections are semantic (knowledge content).

## Next Steps

1. **Collect all semantic headers** from agents/decisions/architecture.md and agents/decisions/workflows.md (recovery plan Step 2)
2. **Apply structural markers** to genuinely structural headers using recovery plan judgment criteria (Step 3)
3. **Add index entries** for all collected semantic headers with em-dash descriptions (Step 4)
4. **Update remember skill** template to use `## Title` format (complete Step 5)
5. **Fix validator logic** to remove orphan index entry check (critical issue #3)
6. **Run validation** with `just precommit` to verify all semantic headers indexed
7. **Commit submodule** changes first, then commit parent with pointer update
