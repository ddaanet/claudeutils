#!/usr/bin/env python3
"""Analyze delegation overhead to answer: is orchestrator-direct cheaper than Task delegation?

Uses the delegation overhead TSV (from collect-delegation-overhead.py) to compute:
1. Fixed cost: baseline tokens for any Task call (CLAUDE.md + agent def + system prompt)
2. Variable cost: marginal tokens per tool use within the agent
3. Break-even: how many inline edits before delegation becomes cheaper

The comparison target is orchestrator-direct: the orchestrator already has CLAUDE.md
loaded, so inline edits only cost the marginal Read+Edit tokens, not the full context
reload.

Input: tmp/delegation-overhead.tsv (from collect-delegation-overhead.py)
Output: analysis to stdout
"""
import sys
from collections import defaultdict
from pathlib import Path


def percentile(values, p):
    if not values:
        return 0
    values = sorted(values)
    k = (len(values) - 1) * p / 100.0
    f = int(k)
    c = min(f + 1, len(values) - 1)
    return values[f] + (k - f) * (values[c] - values[f])


def main():
    tsv_path = Path(__file__).parent.parent.parent / "tmp" / "delegation-overhead.tsv"
    if not tsv_path.exists():
        print(f"Run collect-delegation-overhead.py first", file=sys.stderr)
        sys.exit(1)

    rows = []
    with open(tsv_path) as f:
        header = f.readline().strip().split("\t")
        for line in f:
            fields = line.strip().split("\t")
            if len(fields) < len(header):
                continue
            row = dict(zip(header, fields))
            row["total_tokens"] = int(row["total_tokens"]) if row["total_tokens"] else None
            row["tool_uses"] = int(row["tool_uses"]) if row["tool_uses"] else None
            row["prompt_chars"] = int(row["prompt_chars"]) if row["prompt_chars"] else None
            rows.append(row)

    print(f"Loaded {len(rows)} Task call records")

    # --- 1. Fixed cost: minimal-work agents ---
    # Agents with <= 3 tool uses approximate the fixed overhead
    minimal = [r for r in rows if r["tool_uses"] is not None and r["tool_uses"] <= 3 and r["total_tokens"]]
    minimal_tokens = sorted([r["total_tokens"] for r in minimal])

    print(f"\n{'='*60}")
    print("1. FIXED DELEGATION COST (agents with <= 3 tool uses)")
    print(f"{'='*60}")
    print(f"  n = {len(minimal)}")
    print(f"  p25 = {percentile(minimal_tokens, 25):,.0f} tokens")
    print(f"  p50 = {percentile(minimal_tokens, 50):,.0f} tokens")
    print(f"  p75 = {percentile(minimal_tokens, 75):,.0f} tokens")
    print(f"  p90 = {percentile(minimal_tokens, 90):,.0f} tokens")

    # --- 2. Variable cost: tokens per tool use ---
    with_both = [(r["total_tokens"], r["tool_uses"])
                 for r in rows
                 if r["total_tokens"] and r["tool_uses"] and r["tool_uses"] > 3]
    # Estimate fixed cost as p50 of minimal-work agents
    fixed_est = percentile(minimal_tokens, 50) if minimal_tokens else 35000

    print(f"\n{'='*60}")
    print("2. VARIABLE COST (marginal tokens per tool use, agents > 3 tools)")
    print(f"{'='*60}")
    if with_both:
        # Marginal = (total_tokens - fixed_est) / tool_uses
        marginals = [(tok - fixed_est) / tu for tok, tu in with_both if tu > 0]
        marginals = sorted([m for m in marginals if m > 0])
        print(f"  n = {len(marginals)}")
        print(f"  Estimated fixed cost (subtracted): {fixed_est:,.0f} tokens")
        print(f"  Marginal p25 = {percentile(marginals, 25):,.0f} tokens/tool")
        print(f"  Marginal p50 = {percentile(marginals, 50):,.0f} tokens/tool")
        print(f"  Marginal p75 = {percentile(marginals, 75):,.0f} tokens/tool")

    # --- 3. Break-even analysis ---
    print(f"\n{'='*60}")
    print("3. BREAK-EVEN: WHEN IS DELEGATION CHEAPER THAN INLINE?")
    print(f"{'='*60}")
    print(f"  Delegation fixed cost (p50): {fixed_est:,.0f} tokens")
    print(f"  This is paid once per Task call, regardless of work done.")
    print(f"")
    print(f"  For inline edits by orchestrator:")
    print(f"  - Orchestrator already has CLAUDE.md loaded (0 extra tokens)")
    print(f"  - Each edit costs ~1 Read + 1 Edit = ~2 tool uses")
    if marginals:
        marginal_p50 = percentile(marginals, 50)
        inline_cost_per_edit = marginal_p50 * 2  # Read + Edit
        break_even = fixed_est / inline_cost_per_edit if inline_cost_per_edit > 0 else float('inf')
        print(f"  - Marginal cost per tool use (p50): {marginal_p50:,.0f} tokens")
        print(f"  - Estimated cost per inline edit: ~{inline_cost_per_edit:,.0f} tokens")
        print(f"  - Break-even: ~{break_even:.0f} inline edits before delegation saves tokens")
        print(f"")
        print(f"  For typical inline phase (3-7 edits):")
        for n_edits in [3, 5, 7, 10]:
            inline_total = n_edits * inline_cost_per_edit
            delegated_total = fixed_est + n_edits * marginal_p50 * 2
            saving = delegated_total - inline_total
            print(f"    {n_edits} edits: inline={inline_total:,.0f} vs delegated={delegated_total:,.0f} (save {saving:,.0f} = {saving/delegated_total*100:.0f}%)")

    # --- 4. Context pollution concern ---
    print(f"\n{'='*60}")
    print("4. CONTEXT POLLUTION (orchestrator accumulation)")
    print(f"{'='*60}")
    # How much context does a typical orchestration session accumulate?
    # Group by session, sum total_tokens
    by_session = defaultdict(list)
    for r in rows:
        by_session[r["session"]].append(r)
    session_totals = []
    for sid, rs in by_session.items():
        n_tasks = len(rs)
        if n_tasks >= 5:  # orchestration sessions have many Task calls
            total = sum(r["total_tokens"] for r in rs if r["total_tokens"])
            session_totals.append((sid, n_tasks, total))
    session_totals.sort(key=lambda x: -x[1])
    print(f"  Sessions with >= 5 Task calls: {len(session_totals)}")
    if session_totals:
        all_totals = sorted([t for _, _, t in session_totals])
        print(f"  Session total tokens p50 = {percentile(all_totals, 50):,.0f}")
        print(f"  Session total tokens p90 = {percentile(all_totals, 90):,.0f}")
        print(f"")
        print(f"  Top 5 sessions by Task count:")
        for sid, n, total in session_totals[:5]:
            print(f"    {sid}: {n} tasks, {total:,.0f} total tokens")


if __name__ == "__main__":
    main()
