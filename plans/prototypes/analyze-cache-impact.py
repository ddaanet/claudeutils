"""Analyze delegation overhead accounting for prompt caching.

Key finding from session data: API input_tokens excludes cached tokens.
They report separately as cache_creation_input_tokens and cache_read_input_tokens.
The CLI's total_tokens in <usage> tags sums ALL token types including cache.

So when we see total_tokens=50K for a sub-agent:
- System prompt (~40K) is cache_read on turns 2+ (0.1x price)
- Fresh input (~few hundred per turn) is input_tokens (1.0x price)
- First turn pays cache_creation (1.25x price) for the system prompt

This script models the actual $ cost under this understanding.
"""

# Sonnet pricing (per 1M tokens)
INPUT_PRICE = 3.00
CACHE_WRITE_PRICE = 3.75  # 1.25x
CACHE_READ_PRICE = 0.30   # 0.1x
OUTPUT_PRICE = 15.00

# Measured values
SYSTEM_PROMPT_TOKENS = 43_384   # p50 of main session first-turn cache_creation
MINIMAL_AGENT_TOTAL = 35_688    # p50 total_tokens for <=3 tool use agents
TYPICAL_AGENT_TOTAL = 50_461    # p50 total_tokens for all agents
TYPICAL_TOOL_USES = 16          # p50 tool_uses for all agents


def cost_per_1m(tokens, price):
    return tokens * price / 1_000_000


def main():
    print("="*70)
    print("DELEGATION COST MODEL (cache-aware)")
    print("="*70)
    print()

    # --- Sub-agent: model one Task call ---
    # A typical agent: ~16 tool uses = ~17 API turns
    # Turn 1: cache_creation for system prompt
    # Turns 2-17: cache_read for system prompt
    # Fresh input per turn: conversation context delta (tool results, new prompts)
    #
    # total_tokens = sum across turns of (input + cache_create + cache_read + output)
    # For typical agent: 50,461 total
    # System prompt contributes: 43,384 × 17 turns... but wait, that's 737K
    # which >> 50K. So total_tokens must NOT sum across turns.
    #
    # Hypothesis: total_tokens is from the LAST turn only (snapshot, not cumulative)
    # Or: CLI sums just input_tokens + output_tokens (non-cache) across all turns

    turns = TYPICAL_TOOL_USES + 1  # tool uses + initial turn

    # If total_tokens excludes cache (= sum of input + output across turns):
    fresh_per_turn = TYPICAL_AGENT_TOTAL / turns
    cache_cost_turn1 = cost_per_1m(SYSTEM_PROMPT_TOKENS, CACHE_WRITE_PRICE)
    cache_cost_rest = cost_per_1m(SYSTEM_PROMPT_TOKENS, CACHE_READ_PRICE) * (turns - 1)
    fresh_cost = cost_per_1m(TYPICAL_AGENT_TOTAL, INPUT_PRICE)  # simplify: treat all fresh as input
    total_delegated = cache_cost_turn1 + cache_cost_rest + fresh_cost

    print(f"Hypothesis A: total_tokens = sum(input + output), excludes cache")
    print(f"  Turns: {turns}")
    print(f"  Fresh tokens (all turns): {TYPICAL_AGENT_TOTAL:,} (at ${INPUT_PRICE}/M)")
    print(f"  Cache write (turn 1): {SYSTEM_PROMPT_TOKENS:,} (at ${CACHE_WRITE_PRICE}/M)")
    print(f"  Cache reads (turns 2-{turns}): {SYSTEM_PROMPT_TOKENS:,} × {turns-1} (at ${CACHE_READ_PRICE}/M)")
    print(f"  Fresh cost: ${fresh_cost:.4f}")
    print(f"  Cache write: ${cache_cost_turn1:.4f}")
    print(f"  Cache reads: ${cache_cost_rest:.4f}")
    print(f"  TOTAL: ${total_delegated:.4f}")
    print()

    # If total_tokens includes cache (= sum of all token types, last turn):
    # Then for the last turn: input + cache_read + output = total
    # cache_read ≈ system_prompt, so fresh = total - system_prompt
    fresh_last_turn = max(TYPICAL_AGENT_TOTAL - SYSTEM_PROMPT_TOKENS, 0)
    # But this is just the last turn. Previous turns had less context.
    # Estimate: fresh input grows linearly from ~500 to fresh_last_turn
    avg_fresh_per_turn = fresh_last_turn / 2  # rough average
    total_fresh_all_turns = avg_fresh_per_turn * turns
    cache_cost_turn1_b = cost_per_1m(SYSTEM_PROMPT_TOKENS, CACHE_WRITE_PRICE)
    cache_cost_rest_b = cost_per_1m(SYSTEM_PROMPT_TOKENS, CACHE_READ_PRICE) * (turns - 1)
    fresh_cost_b = cost_per_1m(total_fresh_all_turns, INPUT_PRICE)
    total_delegated_b = cache_cost_turn1_b + cache_cost_rest_b + fresh_cost_b

    print(f"Hypothesis B: total_tokens = last turn (input + cache_read + output)")
    print(f"  Fresh tokens (last turn only): {fresh_last_turn:,}")
    print(f"  Estimated fresh all turns: {total_fresh_all_turns:,.0f}")
    print(f"  Cache write: ${cache_cost_turn1_b:.4f}")
    print(f"  Cache reads: ${cache_cost_rest_b:.4f}")
    print(f"  Fresh cost: ${fresh_cost_b:.4f}")
    print(f"  TOTAL: ${total_delegated_b:.4f}")
    print()

    # --- Inline by orchestrator ---
    # System prompt already loaded and cached. Each edit = Read + Edit.
    # Read: returns file content (~2-5K tokens). Edit: sends old+new (~0.5-2K).
    # Marginal cost per edit: ~3K fresh tokens + same system prompt cache_read
    # But orchestrator's cache_read is already happening on every turn regardless.
    # So incremental cost of an inline edit = just the fresh tokens.

    FRESH_PER_INLINE_EDIT = 3_000  # Read result + Edit inputs (conservative)
    inline_cost_per_edit = cost_per_1m(FRESH_PER_INLINE_EDIT, INPUT_PRICE)

    print(f"Inline edit by orchestrator:")
    print(f"  Fresh tokens per edit: ~{FRESH_PER_INLINE_EDIT:,}")
    print(f"  Cost per edit: ${inline_cost_per_edit:.6f}")
    print(f"  (system prompt cache_read happens anyway, not incremental)")
    print()

    # --- Comparison ---
    print("="*70)
    print("COMPARISON: 7 prose edits (typical error-handling phase)")
    print("="*70)
    n = 7
    inline_total = n * inline_cost_per_edit

    print(f"  Inline ({n} edits): ${inline_total:.4f}")
    print(f"  Delegated (hyp A): ${total_delegated:.4f}  ({total_delegated/inline_total:.1f}x)")
    print(f"  Delegated (hyp B): ${total_delegated_b:.4f}  ({total_delegated_b/inline_total:.1f}x)")
    print()

    # The dominant cost in delegation is the cache reads across all turns
    # Even at 0.1x, 43K tokens × 16 turns × $0.30/M = $0.21
    print(f"  Delegation cache reads alone: ${cache_cost_rest:.4f}")
    print(f"  That's {cache_cost_rest/inline_total:.1f}x the total inline cost")
    print()

    # --- Context window impact ---
    print("="*70)
    print("CONTEXT WINDOW IMPACT")
    print("="*70)
    print(f"  7 inline edits add ~{n * FRESH_PER_INLINE_EDIT:,} tokens to orchestrator history")
    print(f"  Orchestrator 200K context limit: {n * FRESH_PER_INLINE_EDIT / 200_000 * 100:.1f}% consumed")
    print(f"  1 Task delegation adds ~500 tokens (brief result) to orchestrator history")
    print()

    # --- Break-even ---
    print("="*70)
    print("BREAK-EVEN")
    print("="*70)
    if inline_cost_per_edit > 0:
        be_a = total_delegated / inline_cost_per_edit
        be_b = total_delegated_b / inline_cost_per_edit
        print(f"  Hypothesis A: {be_a:.0f} edits")
        print(f"  Hypothesis B: {be_b:.0f} edits")
    print()
    print("  Both hypotheses: delegation never saves $ for typical inline phases.")
    print("  Delegation's value is context isolation, not token cost.")


if __name__ == "__main__":
    main()
