# Recall Artifact: Triage Feedback

Resolve entries via `agent-core/bin/when-resolve.py` — do not use inline summaries.

## Entry Keys

how architect feedback pipeline — three-stage collect→analyze→rules, data flow model
how define feedback type enum — StrEnum for feedback types (MESSAGE, TOOL_DENIAL, INTERRUPTION)
how categorize feedback by keywords — keyword-based category assignment with priority order
how detect noise in command output — multi-marker detection with length threshold
how validate session uuid files — regex filtering for session vs agent files
how extract session titles — handle string and array content formats in JSONL
how resolve agent ids to sessions — agent IDs become session IDs, tree recursion
how parse first line metadata — O(1) session metadata from first JSONL line
when choosing feedback output format — text vs json format for piping
when evaluating recall system effectiveness — recognition vs retrieval, forced injection bypasses recognition
when reading design classification tables — read literally, no invented heuristics
when choosing script vs agent judgment — non-cognitive deterministic → script, cognitive → agent
when designing quality gates — layered defense, multiple independent checks
when placing quality gates — gate at chokepoint, scripted mechanical enforcement
when splitting validation into mechanical and semantic — script deterministic, agent judgment advisory
when complexity assessed twice — single assessment, no redundant triage
when design ceremony continues after uncertainty resolves — two gates, mid-stream re-check
when design resolves to simple execution — execution readiness gate, coordination complexity discriminator
when temporal validation required for analysis — git history correlation for feature availability
when discovery decomposes by data point — parametrized operation, spot-check variation table
when choosing execution tier — inline/delegate/orchestrate, context window capacity
when tier thresholds are ungrounded — empirical calibration needed
when using hooks in subagents — hooks don't fire in sub-agents, write own reports
when fixing behavioral deviations identified by RCA — structural fix, not prose strengthening
