# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/codify` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

## When splitting decision files with memory-index entries
- The validation script handles relocating memory-index entries to match their actual file locations. Do not manually move entries between sections during a file split — add new entries, let the validator handle section assignment.
- Evidence: Split workflow-optimization.md → workflow-execution.md, manually reorganized 14 memory-index entries between sections. User corrected: validator does this automatically.
## When companion tasks bundled into /design invocation
- Anti-pattern: Session note says "address X during /design." Agent treats companion work as exempt from design process — no recall, no skill loading, no classification gate. Rationalizes "well-specified from prior RCA" to skip all process steps.
- Correct pattern: Companion tasks get their own triage pass through the same Phase 0 gates. "Address during /design" means the /design session is the venue, not that process is optional. Each workstream needs: recall, classification, routing.
- Evidence: 4 triage fixes to design skill attempted without /recall or /skill-development loading. /reflect identified same pattern class as "Simple triage skips recall" learning.
## When recall step uses "skip if already in context" language
- Anti-pattern: "Read X (skip if already in context)" as a recall gate. Agent rationalizes the skip condition without verifying — substitutes related activity for the required Read. The escape hatch IS the failure mode.
- Correct pattern: Anchor recall with a tool call that proves work happened. `when-resolve.py` is the gate: it's a Bash call (unskippable), requires trigger knowledge (forces prior Read of memory-index), and produces output (proves resolution). One gate anchor is sufficient — passphrase/proof-of-Read mechanisms are redundant when the resolution tool already proves both.
- Evidence: /reflect Phase 4.5 skipped recall entirely. Same class as "treating recall-artifact summary as recall pass" — agent substitutes adjacent activity for the specific required action.
## When selecting model for discovery and audit tasks
- Anti-pattern: Using haiku scouts to audit prose quality or detect structural anti-patterns in LLM-consumed instruction files (skills, agents, fragments). Haiku grades generously, misses dominant failure patterns, and produces false positives that require opus validation — double work.
- Correct pattern: Sonnet minimum for any discovery/audit touching skills, agents, or fragments. These are architectural prose artifacts — assessing their quality requires the same judgment tier as editing them. The "model by complexity" rule applies to analysis, not just edits.
- Evidence: Haiku scout graded 0 skills at C (sonnet found 3), missed description anti-pattern as dominant issue (18/30), produced 15 gate findings vs sonnet's 12 (3 false positives from over-flagging steps where preceding tool output naturally feeds judgment).
## When optimizing skill prose quality
- Reference: `plans/reports/skill-optimization-grounding.md` — Segment → Attribute → Compress framework adapted from LLMLingua/ProCut. 9 content categories with compression budgets per category.
- Triggers: deslop, compression, segment, attribute, budget, skill optimization, prose quality pass
## When editing skill files
- Platform constraint: skill `description` frontmatter MUST use "This skill should be used when..." format (plugin-dev:skill-development, skill-reviewer enforce this). Improve wording within this format, do not replace the format.
- Extraction safety: every content block moved to references/ must leave a trigger condition + Read instruction in the main SKILL.md body. Verify each references/ file has a corresponding load point.
- Control flow verification: after restructuring skills with conditional branches, enumerate all execution paths and verify user-visible output on each path. Prior deslop on design skill combined two fast paths and regressed user-facing classification message.
- D+B gate additions: adding tool calls to anchor prose-only gates must not change the gate's decision outcome on existing paths. The added Read/Bash provides data for judgment — it should not introduce new content that shifts the judgment itself.
- Triggers: editing skills, skill surgery, deslop, extraction, progressive disclosure, restructuring conditional branches
