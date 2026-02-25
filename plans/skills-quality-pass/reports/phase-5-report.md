# Phase 5 Report: Light-Touch Edits (15 Skills)

**Date:** 2026-02-25

## Step 5.1: Batch A (8 skills)

### error-handling
- **FR-1:** Tightened description — removed verbose clause listing, focused on bash error handling and token-efficient exception patterns
- **FR-8:** Body was virtually identical to `agent-core/fragments/error-handling.md` (same 5 bullet points + same exception clause). Reduced body to redirect stub: "Content is in the always-loaded fragment" with discovery-only note. Skill retained for discovery layer (agents searching for error handling find the skill entry)

### gitmoji
- **FR-1:** Shortened description — removed redundant trigger variants ("find appropriate emoji for commit"), trimmed verbose tail sentence
- **FR-2:** Removed "When to Use" section (4 bullet points of trigger conditions already covered by description)
- **FR-9:** Removed "Integration" section (3 methods restating obvious workflow position), "Critical Rules" section (Do/Don't lists restating body content), and "Resources" section (file listing + limitations). Consolidated essential constraints from Critical Rules into a new "Constraints" section (5 bullets). Retained Index Maintenance as operational content

### ground
- **FR-1:** Condensed description from 4-line verbose claim-type enumeration to 2 lines. Kept claim types as compact list, added method summary
- **FR-9:** Removed "Integration Points" section (3 paragraphs restating when to use/not use — already covered by description). Renamed "Additional Resources > Reference Files" to flat "References" section

### how
- **FR-1:** Condensed description from long clause chain to single-line with em-dash structure. Removed redundant trigger examples (kept invocation hint)

### when
- **FR-1:** Condensed description matching how skill pattern — single-line with em-dash structure

### memory-index
- **FR-1:** Tightened description — clarified Bash transport purpose, removed redundant "Provides index of when/how entries"

### next
- **FR-1:** Shortened description — removed redundant trigger variants ("what should I work on?"), kept essential triggers and secondary location list
- **FR-2:** Removed "When to Use" section (4-step decision tree). The decision logic ("check context first") was already implicit in the description's "no pending work exists in already-loaded context" clause. The skill body's opening paragraph ("By the time this skill loads...") already explains the precondition

### prioritize
- **FR-1:** Shortened description — removed redundant trigger variants, trimmed verbose method description
- **FR-9:** Renamed "Additional Resources > Reference Files" to flat "References" section

## Step 5.2: Batch B (7 skills)

### recall
- **FR-1:** Shortened description — removed redundant triggers ("recall pass", "what do I need to know"), compressed behavioral summary into two compact sentences

### deliverable-review
- **FR-1:** Condensed description from 4 lines to 3 — removed redundant trigger variants, kept essential triggers and method summary
- **FR-2:** Removed "When to Use" section (3 positive triggers + 1 negative constraint). Positive triggers redundant with description; negative constraint ("Not for: in-progress work...") is implicit in "after completing plan execution" in description

### doc-writing
- **FR-1:** Shortened description — removed redundant trigger variants ("rewrite the README", "update README", "rewrite documentation", "write project docs", "improve the README"), kept representative triggers
- **FR-2:** Removed "When to Use" section (4 positive bullets + 1 negative constraint). All positive triggers covered by description; negative constraint ("Not for: API reference docs...") is implicit in "project-facing documentation"

### release-prep
- **FR-2:** Removed "When to Use" section (3 bullets restating description triggers)
- **FR-9:** Removed "Example Interaction" section (30 lines showing a complete worked example with readiness report output). The readiness report template in Step 7 already shows the format; the example was redundant demonstration

### worktree
- **FR-1:** Tightened description — removed "remove a worktree" (covered by `wt-rm` shortcut mention), compressed tail sentence
- **FR-6:** Replaced `list_plans(Path('plans'))` with `claudeutils _worktree ls` in Mode B step 1. The Python function call was incorrect for agent context — agents should use the CLI wrapper which includes plan status output

### handoff-haiku
- **FR-2:** No explicit "When to Use" section existed. Applied FR-8 instead (see below) and FR-9 equivalent tail compression
- **FR-8:** Removed 20-line "Task metadata format" section that fully restated `execute-rule.md` content (format template, 2 examples, 3 field rules, mechanical merge instruction). Replaced with single-line redirect: "Follow the format defined in `execute-rule.md` (always loaded)." The merge instruction was preserved inline
- **Tail compression:** Condensed "Key Differences from Full Handoff" (9 lines across 3 subsections) + "Principles" (6 lines across 2 subsections) into 4 bullet points under "Key Differences from Full Handoff". No content loss — all behavioral distinctions preserved

### opus-design-question
- **FR-2:** Removed "Example Workflow" section (36 lines). This was a fully worked example showing traditional vs opus-design-question approach for a CLI framework choice, including Opus response text. The Step 1-4 protocol in the body already demonstrates the pattern sufficiently; the worked example was redundant demonstration with sycophantic response modeling ("I'll help you...")
- Cleaned trailing blank lines

## Issues Encountered

None. All edits were straightforward mechanical operations matching the variation table specifications.

## Verification

All 15 files re-read after edits. Confirmed:
- No content loss (all deleted content was truly redundant with descriptions, fragments, or body content)
- All descriptions retain "This skill should be used when..." format (NFR-6)
- No structural damage to remaining skill bodies
- FR-6 worktree fix correctly replaces Python function call with CLI invocation
