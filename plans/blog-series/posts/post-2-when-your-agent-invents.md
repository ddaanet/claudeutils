# Post 2: "When Your Agent Invents Instead of Researching"

## Opening Hook

"Establish grounded methodology to order and batch pending tasks."

The agent produced a prioritization document with subjective weights — Highest/High/Medium — and 0-3 scores without defined criteria. The scoring looked authoritative. It was structured, consistent, confident. It was entirely fabricated. No grounding in any established prioritization framework.

The user opened the output, saw the problem, and interrupted: "re-read each word of the first line of my first prompt." (Session `bcab8b4c`, Feb 16, 2026)

## Core Argument

### The Confabulation Problem

LLMs pattern-match for logically consistent language. They have no world model for true/false — they optimize for linguistic consistency. When asked to create a methodology, the model produces something that reads like a methodology: it has sections, scoring criteria, rationale. But the criteria are invented. The rationale is post-hoc. The structure is the only real thing.

The confabulated scoring wasn't a hallucination in the factual sense — it didn't cite nonexistent papers or claim false statistics. It invented a plausible-sounding evaluation framework from nothing. This is harder to catch than factual hallucination because the output looks reasonable. You have to know the domain to recognize that WSJF, RICE, and critical path analysis exist and this document references none of them.

### The Fix: Diverge-Converge

The same session that exposed the problem produced the fix. The user directed: "start in parallel brainstorm agent to identify axes to consider, and web search for existing frameworks." Two parallel agents dispatched — one for internal project-specific analysis, one for external web search. Neither contaminates the other during generation. Synthesis happens after both complete.

The external branch discovered WSJF (Weighted Shortest Job First) from SAFe, which became the project's prioritization framework. The internal branch identified project-specific evaluation axes. The resulting methodology was grounded: WSJF adapted for agent task context, with evidence-based criteria. (Commit `ab4813a4`, Feb 16, 2026)

The ground skill was created the same day (commit `cae5ef11`). 4-phase procedure: Scope → Diverge → Converge → Output. The diverge phase dispatches parallel agents — an internal brainstorm (always opus, for generative divergence) and external web search. The converge phase synthesizes with a mandatory quality label: Strong/Moderate/Thin/None grounding.

### Research Foundations

The skill's structure is grounded in established methodology — applied to itself during creation:

- **Double Diamond** (UK Design Council, 2005): diverge-converge in two diamonds
- **Rapid Review** (evidence synthesis): systematic review simplified for timeliness
- **RAG-as-Grounding** (LLM hallucination mitigation): external retrieval reduces hallucination by anchoring generation in verified sources

(Source: `plans/reports/ground-skill-research-synthesis.md`, commit `ab4813a4`)

### The Trigger Problem

During skill outline review, the user challenged the trigger wording: "'When synthesizing ungrounded methodology' is over-specific, LLM defaulting to confabulation means they cannot self-assess 'ungrounded'." (Session `dfd23c89`)

The insight: if the model could self-assess "ungrounded," it wouldn't confabulate. The trigger must fire on the *activity* — "create a scoring system," "design a methodology" — not a quality judgment the model can't make about its own output.

This connects directly to the recognition problem explored in Post 3: LLMs can't recognize their own uncertainty. The trigger for corrective action must be structural (observable activity), not metacognitive (self-assessed quality).

### Self-Application

When the ground skill was applied to the /design skill itself (commit `557c2eed`, Feb 25), it pulled in Stacey Matrix (certainty × stability), Cynefin framework (domain classification), PDR/CDR (preliminary/critical design review), and ADR (architecture decision records). Grounding report: Strong.

But applying the tool required updating the tool first (commit `f2455d9a`, Feb 24). The bootstrapping insight from an earlier session (commit `14eeed90`, Feb 15): "unimproved agents reviewing their own improvements creates a bootstrapping problem." Phase ordering must follow the tool-usage dependency graph, not logical grouping.

### Empirical Feedback Loop

Session scraper data from 8 actual /design sessions fed back into the ground skill (commit `e632470e`, Feb 26-27). The most actionable finding: the agent rationalized away the external research phase entirely. "Skipped A.3-A.4 (external research). User noticed 47 minutes later." (Session `6e808dbc`)

This drove the structural anchor requirement: a tool call proving external research was attempted, not just a procedural instruction to do it. The skill's own usage data revealed its enforcement gap.

## Evidence Chain

| Claim | Evidence |
|-------|----------|
| Confabulated scoring: subjective weights, no external anchoring | Session `bcab8b4c`, commit `ab4813a4` |
| WSJF emerged from external research branch | Commit `ab4813a4` |
| Ground skill created same day as confabulation caught | Commit `cae5ef11` (Feb 16, same day as `ab4813a4`) |
| Double Diamond / Rapid Review / RAG foundations | `plans/reports/ground-skill-research-synthesis.md` |
| LLMs can't self-assess "ungrounded" | Session `dfd23c89` (user challenge) |
| Ground applied to /design: 6 external frameworks | Commit `557c2eed` |
| Bootstrapping dependency: tool must be updated before applied | Commit `14eeed90` (learning), `f2455d9a` (update), `557c2eed` (application) |
| Agent skipped external research phase, user caught 47 min later | Session `6e808dbc` |
| Methodology spread: applied to decomposition, prioritization | Commits `ac37f7ba`, `ebf903e8` |

## Transition to Post 3

The ground skill forces external research because the agent won't do it spontaneously. But how deep does this recognition failure go? The next post measures it: across 129 opportunities, how often did an agent independently decide to consult its own reference material?
