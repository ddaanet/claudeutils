# Brief: Discuss Protocol Redesign

## Context

Current discuss protocol (`d:` directive) has structural problems identified through session mining and usage experience:

- **Stress-test is dead weight:** Zero perspective changes across 9 mined sessions. Agent controls both sides — defense always wins. Originally fixed contrarianism (AGAINST-first), became entrenchment mechanism.
- **Brainstorm step causes change resistance:** Mandatory divergence slows response time, not always needed. Straightforward-looking tasks benefit most from divergence, but those are least likely to trigger it.
- **Verbosity:** Five output sections, verdict buried. Heavy ceremony for interactive discussion.
- **Grounding is reactive only:** Checks user's referenced artifacts but agent's own ungrounded claims pass unchallenged.

## Proposed Direction

Replace current protocol with lighter three-step core:

1. **Grounding** — recall-explore-recall variant (mechanism TBD), can include web search, git history, session scraping in explore phase
2. **State position** — agent commits to a position informed by grounding evidence
3. **Claim validation** — enumerate claims, trace each to source, flag ungrounded. Not metacognitive introspection ("flag uncertainty") but mechanical text operation ("cite source or write 'ungrounded'")

Optional prefix: `bd:` for divergence before discussion (user-triggered broadening, not mandatory).

## Key Design Insight

Claim validation may work where metacognitive instructions fail because it's pattern matching (claim → source lookup), not confidence monitoring. Same reasoning as why structural enforcement works and "LLM Limitation Awareness" doesn't. The 0% spontaneous recall finding is the same phenomenon — agents don't self-initiate metacognitive tasks but can execute constrained lookup operations.

## Adversarial Framing

"Poke holes in logic, explain why status quo is better" — single data point but produced good outcome. Concrete adversarial instruction outperforms vague "be critical." Status quo defense forces a specific position rather than open-ended evaluation.

## Evidence Base

- `plans/reports/discuss-protocol-mining.md` (commit `1857b6899233`) — 9 perspective-change sessions mined; stress-test produces 0 changes; three categories of actual mind-change (new facts, reframing, research gaps)
- `plans/reports/how-verb-form-ab-methodology.md` (commit `1857b6899233`) — forced selection methodology, paired design, McNemar's test — transferable testing pattern
- A/B test infrastructure (commit `6876de6ad8ea`) — prototype scripts for variant generation, task selection, forced selection harness, analysis
- Retrospective topic-2 pushback report — full arc from "proceed autonomously" through proto-pushback to structural enforcement
- 0% spontaneous recall measurement (`plans/measure-agent-recall/report.md`) — agents never self-initiate metacognitive tasks

## Open Questions

- **Grounding mechanism specifics:** "Recall-explore-recall variant" — what does the explore phase include? How heavy?
- **Claim validation timing:** After grounding+position (creates research agenda for targeted follow-up) vs end of turn (mirrors current interactive pattern). Discussion leaned toward after-position.
- **`bd:` divergence scope:** What replaces current brainstorm procedure (3+ framings, one must reframe problem)? How much structure?
- **Agreement momentum:** 3+ consecutive agreements — undecided from mining report
- **Testing methodology:** Ground truth annotation is the blocking human step. Forced selection design available but needs task curation and annotation.
- **Existing artifact disposition:** Current discuss skill files, fragments — what gets removed vs refactored?

## 2026-03-13: Discussion conclusions from retrospective review session

**LLM reasoning framing:** User frames LLM capability as "approximation of reasoning via language pattern fitting" — not actual reasoning. Metacognitive instructions ("flag uncertainty", "LLM Limitation Awareness") are wishful thinking because they ask the model to do something it structurally can't (monitor confidence). Claim validation works because it's a text operation (trace claim to source), not introspection.

**Grounding sequence decided:** Grounding before position statement. Agent needs context before forming a position worth validating. Without it, initial position is based on incomplete context. Sequence: trigger → grounding → state position → enumerate claims → flag ungrounded → (optional: targeted research on ungrounded claims) → restate.

**Two grounding passes, different purposes:** First pass is broad context gathering. Second pass (if needed) is surgical — only targeting specific ungrounded claims identified by validation step. First pass may eliminate need for second.

**Testing methodology constraints:** Behavioral variation measurement requires careful context preparation — not improvisable by replaying old prompts in different git context. Agent behavior depends on loaded context (CLAUDE.md, session.md, skills), not just prompt. Proper test needs: fixed context, fixed prompt, varied treatment, evaluation criteria defined before running. Ground truth annotation is the blocking human step.

**Longitudinal observation alternative:** Mine sessions for defined markers (perspective changes, ungrounded claims flagged) rather than controlled A/B testing. Same methodology as discuss-protocol-mining.md — search for "I was wrong" / "revised position" signals.

**Brief skill trigger gap identified:** `/brief` in mid-sentence not recognized as skill invocation. Separate `p:` task to update skill description — lead with general mechanism ("capture conversation context into brief.md"), not specific use case ("cross-worktree transfer"). Opus (agentic prose).
