# b: Directive Brainstorm

## Framing

The directive set {b, d, p, q} shapes how the agent processes a message. Each directive is a behavioral mode — not a command (Tier 1) or a skill invocation, but a lens applied to the user's text.

Current coverage:
- **d:** Critical evaluation without execution (analysis mode)
- **p:** Deferred capture without execution (scheduling mode)
- **q:** Minimal-ceremony response (compression mode)

What mode is missing?

## Evaluation of Prior Candidates

### brainstorm

**Semantics:** Generate options without converging. Diverge first — list alternatives, explore variations, don't evaluate or recommend.

**Strengths:**
- Fills a genuine gap. `d:` evaluates (converge); brainstorm generates (diverge). These are complementary cognitive operations. Currently there's no way to say "give me options" without the agent also ranking them and recommending one.
- Natural language fit. "b: approaches for session persistence" reads well.
- The expansion string is clean and enforceable — "do not converge" is a verifiable behavioral constraint.

**Weaknesses:**
- Proximity to `d:` — both are "think about this" modes. The distinction (diverge vs converge) is real but requires the user to internalize which is which.
- Frequency question: how often does a user want options without any evaluation? In practice, the user often wants "give me options AND tell me which one" — which is `d:` territory.

**Draft expansion:**
```
[BRAINSTORM] Generate options, do not converge.

Explore possibilities. List alternatives without evaluating or ranking.
No recommendations. No "best option." Diverge — convergence is a separate step.
```

**Verdict:** Viable. The diverge/converge split is a real workflow distinction.

### bookmark

**Semantics:** Save a reference point — mark something for later recall.

**Strengths:**
- Captures intent to persist without scheduling execution (unlike `p:` which creates a task).

**Weaknesses:**
- Overlaps `p:` heavily. Both say "remember this, don't act now." The distinction (reference vs task) is too subtle for a single-letter shortcut.
- What does the agent actually DO? `p:` has a clear output format (task name + model + restart). Bookmark would need its own artifact — a "bookmarks" section in session.md? A separate file? The storage mechanism doesn't exist and would need design.
- `learn:` already covers the "persist knowledge" use case for learnings. Bookmark would be a third "save this" mechanism alongside `p:` and `learn:`.

**Verdict:** Rejected. Overlaps `p:` and `learn:` without a clear distinct behavior.

### batch

**Semantics:** Group multiple items together.

**Strengths:**
- None that are directive-shaped. Batching is a structural property of commands, not a behavioral mode for processing text.

**Weaknesses:**
- "batch: X, Y, Z" — then what? Execute all? Capture all as pending? The directive doesn't specify a behavior; it specifies a quantity modifier on some other behavior.
- Would need to compose with another mode: "batch-execute," "batch-capture." Composition breaks the single-letter-prefix model.
- The existing workflow handles batching via other means (parallel task detection in `#status`, `wt` for worktree setup).

**Verdict:** Rejected. Not a behavioral mode — it's a modifier that lacks standalone semantics.

## Additional Candidates

### brief (b: as brief)

**Semantics:** Summarize or condense. Give the essential points of a topic, decision, or artifact — compress without losing signal.

**Strengths:**
- Distinct from all three existing directives. `q:` is about response ceremony (terse), not about content density. `b: the orchestration design` asks the agent to distill understanding of something complex. `q: what does orchestrate do` asks for a quick answer.
- The `/brief` skill already exists in this project for writing cross-tree briefs. `b:` as "brief me on X" is a reading mode (consume and compress), while `/brief` is a writing mode (produce a brief artifact). Different enough, but the name collision could confuse.
- High utility in a workflow with dense artifacts (designs, runbooks, session histories). "Brief me" is a common need.

**Draft expansion:**
```
[BRIEF] Summarize the essentials.

Distill to key points. What matters, what changed, what depends on what.
No background the reader already has. No exhaustive enumeration.
Prioritize: decisions > context > detail.
```

**Weaknesses:**
- Name collision with `/brief` skill. The user types `b: the design` meaning "summarize this for me" and the hook fires, but the `/brief` skill also exists for writing brief.md artifacts. Distinct behaviors, confusable triggers.
- Proximity to `q:`. Both compress output. The distinction: `q:` compresses ceremony (answer directly), `b:` compresses content (distill a complex topic). Real distinction, but users may not maintain it.

**Verdict:** Viable but weakened by `/brief` skill collision.

### background (b: as background)

**Semantics:** Provide context and background on a topic. Explain the situation, history, and relevant decisions — orient the reader.

**Strengths:**
- Opposite of `q:`. Where `q:` says "skip context, just answer," `b:` says "give me the context I need to understand this."
- Useful when picking up unfamiliar parts of the codebase or returning to stale topics.

**Draft expansion:**
```
[BACKGROUND] Provide context and orientation.

Explain the situation: what exists, why it exists, what decisions led here.
Include relevant history and dependencies. Assume the reader is approaching
this topic fresh and needs grounding before making decisions.
```

**Weaknesses:**
- Low frequency. The user can just ask "explain X" without a directive. The directive doesn't change behavior enough — the agent already provides context when asked.
- Doesn't shape behavior as distinctly as d/p/q. Those three each have a clear behavioral constraint (evaluate-don't-execute, capture-don't-execute, compress-don't-elaborate). "Provide background" is closer to the agent's default behavior than to a distinct mode.

**Verdict:** Rejected. Insufficient behavioral distinctness — too close to default agent behavior.

### breakout (b: as breakout)

**Semantics:** Decompose something into constituent parts. Break down a problem, decision, or artifact into structured components.

**Strengths:**
- Useful for complexity management — "b: the session CLI task" → agent breaks it into sub-problems, dependencies, decision points.
- Distinct from `d:` (which evaluates) and from brainstorm (which generates alternatives). Breakout is structural analysis.

**Draft expansion:**
```
[BREAKOUT] Decompose into parts.

Break this down: components, dependencies, decision points, unknowns.
Structure the complexity. Don't solve — map.
```

**Weaknesses:**
- "breakout" is not a standard term. "Break down" is more natural, but "bd:" is two letters. The single-letter mapping `b: = breakout` requires learning.
- Overlaps with early-stage design work. `/design` already decomposes problems. As a directive, it's a lighter-weight version of the same cognitive operation — but the user could also just say "break this down for me."

**Verdict:** Marginal. The decomposition mode is useful but the name is a stretch and the overlap with design-phase work is real.

## Comparison Matrix

| Candidate | Distinct from d/p/q? | Clear behavioral constraint? | Frequency of use? | Name fit? |
|-----------|----------------------|------------------------------|--------------------|-----------|
| brainstorm | Yes (diverge vs converge) | Yes (no ranking, no recommendation) | Medium | Strong |
| bookmark | No (overlaps p: and learn:) | Weak (unclear artifact) | Low | Moderate |
| batch | No (modifier, not mode) | No (needs composition) | N/A | Weak |
| brief | Yes (compress content) | Moderate (near q:) | High | Collision with /brief |
| background | No (near default behavior) | Weak | Low | Moderate |
| breakout | Partial (near design) | Moderate | Medium | Weak |

## Recommendation: brainstorm

**Winner: `b:` = brainstorm**

Reasoning:

1. **Strongest behavioral distinctness.** The diverge/converge axis is the clearest separation from `d:`. Every other candidate either overlaps an existing directive or fails to define a distinct mode.

2. **Enforceable constraint.** "Do not converge" is a testable property of the output. You can verify the agent didn't rank options or recommend one. Compare to "brief" where the boundary with `q:` is fuzzy, or "background" where the behavior is barely different from default.

3. **Genuine workflow gap.** The current set has no divergent-thinking mode. `d:` forces convergence (verdict required). `q:` forces compression. `p:` forces deferral. None says "explore without deciding." In a workflow that produces designs and makes architectural decisions, the ability to separate option generation from option evaluation is valuable.

4. **Natural composition with `d:`.** The workflow becomes: `b: approaches for X` (generate options) → `d: option 3 from above` (evaluate the promising one). Two-step deliberation with clear phase separation.

5. **Name fit.** "brainstorm" maps naturally to "b:" and the word is universally understood. No collision with existing skills or commands.

**Recommended expansion:**

```python
_BRAINSTORM_EXPANSION = (
    '[BRAINSTORM] Generate options, do not converge.\n'
    '\n'
    'Explore possibilities. List alternatives without evaluating or ranking.\n'
    'No recommendations. No "best option." Diverge — convergence is a separate step.'
)
```

**Dual output (matching d:/p:/q: pattern):**
- systemMessage: `'[BRAINSTORM] Generate options, do not converge.'`
- additionalContext: Full `_BRAINSTORM_EXPANSION`

**The final directive set:**

| Directive | Mode | Behavioral constraint |
|-----------|------|----------------------|
| `b:` | Brainstorm | Diverge — no evaluation, no ranking |
| `d:` | Discussion | Converge — evaluate, stress-test, state verdict |
| `p:` | Pending | Defer — capture task, don't execute |
| `q:` | Quick | Compress — terse, no ceremony |
