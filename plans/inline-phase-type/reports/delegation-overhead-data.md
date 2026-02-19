# Phase 0: Delegation Overhead Data

## Data Sources

- 758 sessions scanned across 63 claudeutils projects
- 709 Task calls with `total_tokens`, `tool_uses`, `duration_ms` (from `<usage>` metadata)
- 205 sessions with per-turn cache breakdown (main session only)
- Sub-agent per-turn cache breakdown unavailable (not in session JSONL)

Collection scripts: `plans/prototypes/collect-delegation-overhead.py`, `analyze-delegation-overhead.py`, `analyze-cache-impact.py`

## Measurement 1: Fixed Delegation Cost

Minimal-work agents (≤3 tool uses, n=52) approximate the fixed overhead of any Task call — CLAUDE.md injection + agent definition + system prompt + round-trip:

| Metric | p25 | p50 | p75 | p90 |
|--------|-----|-----|-----|-----|
| total_tokens | 30,104 | 35,688 | 41,030 | 55,619 |
| prompt_chars | 429 | 686 | 1,162 | 1,755 |

All agents (n=709):

| Metric | p25 | p50 | p75 | p90 |
|--------|-----|-----|-----|-----|
| total_tokens | 40,719 | 50,461 | 61,706 | 75,005 |

No significant difference across model tiers (haiku/sonnet/opus all ~50K p50).

## Measurement 2: Marginal Cost Per Tool Use

Agents with >3 tool uses, subtracting fixed overhead estimate:

| Metric | p25 | p50 | p75 |
|--------|-----|-----|-----|
| tokens/tool_use | 507 | 799 | 1,212 |

## Measurement 3: Prompt Caching Behavior

Main session per-turn data (n=205 sessions):
- System prompt size: p50 = 43,384 tokens (from first-turn `cache_creation_input_tokens`)
- Cache hit rate after warmup: 94-100% (`cache_read / total` on turns 3+)
- Fresh input per turn: 3-10 tokens (just conversation delta)

**Sub-agent caching:** Cannot directly measure. The `total_tokens` in `<usage>` tags doesn't decompose into cache read vs. fresh. Repeated same-agent-type calls show median tokens-per-tool-use ratio of 1.09 (rest/first) — no evidence of cross-call caching benefit in token count, but this doesn't tell us about $ cost since cache reads count the same as fresh in the total.

## Measurement 4: Cross-Call Caching Effect

60 consecutive same-agent sequences (≥3 calls each):
- Tokens-per-tool-use ratio (subsequent/first): median = 1.09, mean = 1.49
- No evidence that repeated calls to the same agent type reduce token volume
- Slight increase likely from conversation context growth within agent

## Analysis: Break-Even

**Token count break-even** (treating all tokens equally):
- Delegation fixed cost: ~35.7K tokens
- Inline edit cost: ~1.6K tokens (2 tool calls × 799 tokens/tool)
- Break-even: ~22 edits

**$ cost break-even** (accounting for caching):
- Cannot precisely compute without sub-agent cache breakdown
- Lower bound: if all 35K fixed tokens are cache reads at 0.1x, fixed $ cost drops 10x → break-even ~99 edits
- Upper bound: if no caching, break-even stays at ~22 edits
- Both well above typical inline phase (3-7 edits)

**Latency overhead** (not token-dependent):
- Agent startup + report cycle: p50 = 50s, p90 = 150s per Task call
- Inline edit: near-zero incremental latency

## Conclusion for D-3

**Orchestrator-direct confirmed for all inline phases.** Batching deferred permanently — no threshold needed.

Evidence:
- Token break-even (22-99 edits) far exceeds any single inline phase (3-7 edits)
- Latency overhead of delegation dominates for small edit counts
- For all-inline runbooks: no coordination context to protect from pollution, so context isolation (delegation's other benefit) provides no value
- For mixed runbooks: 7 inline edits add ~11K tokens to orchestrator context — 5.5% of 200K window, negligible

**Remaining gap:** Per-request $ cost with cache breakdown. LiteLLM proxy configured with SQLite spend logging (`~/.local/share/litellm/spend.db`) — future sessions will capture this. Not blocking for the D-3 decision.
