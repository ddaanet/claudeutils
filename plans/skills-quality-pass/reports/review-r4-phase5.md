# Review R4: Phase 5 Light-Touch Edits (15 Skills)

**Date:** 2026-02-25
**Reviewer:** Opus convergence review
**Scope:** FR-1 (descriptions), FR-2 (When to Use removal), FR-6 (worktree CLI), FR-8 (redundant content), FR-9 (tail sections), NFR-6 (description format), prose quality, content preservation

## Summary

**0 Critical, 2 Major, 3 Minor**

Phase 5 executed cleanly overall. Description rewrites consistently follow NFR-6 format. FR-8 and FR-9 removals preserved essential content. Two major findings: `how` and `when` skills retain "When to Use" / "When NOT to Use" sections that should have been addressed by FR-2, and `prioritize` Step 1 still uses `list_plans(Path('plans'))` (same FR-6 class as the worktree fix).

## Batch A

### error-handling
- **FR-1 (NFR-6):** PASS. Description uses "This skill should be used when..." format. Triggers: "error handling rules for bash command execution or token-efficient bash exception patterns". Third-person, tight.
- **FR-8:** PASS. Body correctly reduced to redirect stub. Discovery-only role preserved. Fragment path referenced.
- **Prose quality:** Clean. No hedging, no preamble.

### gitmoji
- **FR-1 (NFR-6):** PASS. "This skill should be used when the user asks to..." with quoted trigger phrases. Third-person.
- **FR-2:** PASS. "When to Use" section removed.
- **FR-9:** PASS. Integration, Critical Rules, Resources sections removed. Essential constraints consolidated into a 5-bullet "Constraints" section. Index Maintenance retained (operational).
- **Prose quality:** Clean.
- **Content preservation:** Constraints section retains semantic matching rule, single-emoji rule, emoji-not-code format rule — essential content preserved.

### ground
- **FR-1 (NFR-6):** PASS. Description condensed to 2 lines with claim types and method summary. "This skill should be used when..." format.
- **FR-9:** PASS. "Integration Points" removed. References section flattened.
- **Prose quality:** Clean.

### how
- **FR-1 (NFR-6):** PASS. Single-line em-dash description. "This skill should be used when..." format.
- **FR-2:** **MAJOR.** "When to Use" (3 bullets) and "When NOT to Use" (3 bullets) sections still present at lines 32-42. The design lists `how` under FR-1 only, not FR-2. However, the `how` skill has the same "When to Use" structure as skills that ARE in the FR-2 list (e.g., `next`, `gitmoji`, `doc-writing`). The description already covers the positive triggers; the "When NOT to Use" counter-conditions (use `/when` instead, content already in context, exploring unfamiliar code) should be folded into the description per FR-2 pattern.
- **Prose quality:** Clean.

### when
- **FR-1 (NFR-6):** PASS. Single-line em-dash description matching `how` pattern.
- **FR-2:** **Same as `how` above** — "When to Use" (3 bullets) and "When NOT to Use" (3 bullets) still present at lines 32-42. Same analysis: not in the FR-2 list but structurally identical to skills that were cleaned. Counter-conditions should fold into description.
- **Prose quality:** Clean.

**Note on how/when FR-2:** The design FR-2 list (`codify, doc-writing, gitmoji, next, opus-design-question, orchestrate, reflect, release-prep, review, runbook, shelve, handoff-haiku, design`) does not include `how` or `when`. The Phase 5 agent correctly followed the specification. However, these sections are the exact pattern FR-2 targets. Marking as major because the sections remain and represent the anti-pattern, but acknowledging this is a design scope gap rather than an execution error.

### memory-index
- **FR-1 (NFR-6):** PASS. Description clarifies Bash transport purpose. "This skill should be used when..." format.
- **Prose quality:** Clean.
- **Content preservation:** Full index retained — this is the skill's operational content.

### next
- **FR-1 (NFR-6):** PASS. Description shortened, redundant triggers removed. "This skill should be used when..." format.
- **FR-2:** PASS. "When to Use" section removed. Decision logic implicit in description and body opening paragraph.
- **Prose quality:** Clean.

### prioritize
- **FR-1 (NFR-6):** PASS. Description shortened, redundant triggers trimmed. "This skill should be used when..." format.
- **FR-9:** PASS. References section flattened.
- **FR-6:** **MAJOR.** Step 1 (line 30) still contains `list_plans(Path('plans'))` — the same Python function call pattern that FR-6 fixed in the worktree skill. Should be `claudeutils _worktree ls` (which includes plan status output). The design document FR-6 only lists `worktree`, `orchestrate`, and `requirements` as correctness targets, so the agent correctly followed spec. But this is the same anti-pattern class: agents should use CLI wrappers, not internal Python functions.
- **Prose quality:** Clean.

## Batch B

### recall
- **FR-1 (NFR-6):** PASS. Description compressed to two compact sentences. "This skill should be used when..." format. Triggers: "recall", "load context", "load decisions", topic-based work.
- **Prose quality:** Clean. "Why This Exists" section is direct — no hedging.
- **Content preservation:** All modes, process, cumulative behavior retained.

### deliverable-review
- **FR-1 (NFR-6):** PASS. Description condensed, triggers retained. "This skill should be used when..." format.
- **FR-2:** PASS. "When to Use" section removed. Negative constraint implicit in "after completing plan execution".
- **Prose quality:** Clean.
- **Content preservation:** Full 4-phase process, severity classification, lifecycle entry protocol all retained.

### doc-writing
- **FR-1 (NFR-6):** PASS. Description shortened, representative triggers kept. "This skill should be used when..." format.
- **FR-2:** PASS. "When to Use" section removed.
- **Prose quality:** Clean.
- **Content preservation:** Full 5-step process, reader-test protocol, constraints section all retained.

### release-prep
- **FR-1 (NFR-6):** **MINOR.** Description does not use "This skill should be used when..." format. Current: "Validates git state, runs quality checks, updates documentation, and assesses release readiness before the human executes the release command. Invoked when the user asks to..." — this is method-first with triggers appended. NFR-6 requires "This skill should be used when..." as the opening. The description is functional and trigger-rich, but format non-compliant.
- **FR-2:** PASS. "When to Use" section removed.
- **FR-9:** PASS. "Example Interaction" section removed. Template in Step 7 already shows the format.
- **Prose quality:** Clean. D+B comments in Step 1 are good structural annotations.
- **Content preservation:** All 7 steps, post-report behavior, critical constraints retained.

### worktree
- **FR-1 (NFR-6):** PASS. Description tightened, triggers enumerated. "This skill should be used when..." format.
- **FR-6:** PASS. Mode B step 1 now uses `claudeutils _worktree ls` instead of `list_plans(Path('plans'))`.
- **Prose quality:** Clean.
- **Content preservation:** All three modes (A, B, C) with full merge ceremony retained. Usage Notes section retained (operational).

### handoff-haiku
- **FR-1 (NFR-6):** **MINOR.** Description does not use "This skill should be used when..." format. Current: "Internal skill for Haiku model orchestrators only. Not for Sonnet or Opus — use /handoff instead. Mechanical session context preservation without learnings judgment." This is a constraint statement, not a trigger statement. However, `handoff-haiku` has `user-invocable: false` — it's an internal routing target, not user-discovered. The NFR-6 format is primarily for discoverability. Low impact.
- **FR-8:** PASS. 20-line "Task metadata format" section replaced with single-line redirect to `execute-rule.md`. Merge instruction preserved inline.
- **FR-2 / tail compression:** PASS. "Key Differences from Full Handoff" condensed from 15 lines to 4 bullets. All behavioral distinctions preserved.
- **Prose quality:** Clean.
- **Content preservation:** Full merge protocol, CRITICAL preservation rule, report completion instruction all retained.

### opus-design-question
- **FR-2:** PASS. "Example Workflow" section (36 lines) removed. Step 1-4 protocol demonstrates the pattern.
- **Prose quality:** **MINOR.** Step 1 uses second-person "Recognize when you're about to..." and Step 2 uses "What are you implementing?" — this is the instruction style for the consuming agent, which is acceptable in skill procedures (agent is the audience). Not a violation per se, but inconsistent with the third-person style applied to other skills' bodies.
- **Content preservation:** 4-step protocol retained. Task tool invocation template with full prompt structure retained.

## Findings Summary

| # | Severity | Skill | Finding |
|---|----------|-------|---------|
| 1 | Major | how, when | "When to Use" / "When NOT to Use" sections retained (not in FR-2 scope, but same anti-pattern) |
| 2 | Major | prioritize | `list_plans(Path('plans'))` at Step 1 line 30 (FR-6 class — should use CLI wrapper) |
| 3 | Minor | release-prep | Description format non-compliant with NFR-6 (method-first, not "This skill should be used when...") |
| 4 | Minor | handoff-haiku | Description format non-compliant with NFR-6 (constraint statement, not trigger statement) — low impact due to `user-invocable: false` |
| 5 | Minor | opus-design-question | Second-person voice in Steps 1-2 body text (acceptable for agent-directed procedure) |

## Verdict

Phase 5 execution quality is good. The agent followed the variation table specification accurately. Both major findings stem from design scope gaps (FR-2 and FR-6 target lists missing these skills), not execution errors. All FR-8 redirect stubs and FR-9 tail removals were clean — no operational content lost.

**Recommendation:** Fix majors #1 and #2 inline (small edits). Minors are deferrable.
