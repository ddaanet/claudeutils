# Recall Gate Improvement

## Context

RCA from problem-md-migration execution: /runbook's mandatory recall gate (D+B anchor) was skipped when chained from /design. Three layers identified:

1. **Gate compliance** — tool call not made, violating D+B anchor requirement
2. **Scope conflation** — agent treated /design's triage-scoped recall as satisfying /runbook's implementation-scoped recall. Different phases need different trigger selection.
3. **Artifact-existence branching creates skip rationalization** — gate's two-path structure (artifact exists / fallback) makes the primary path for moderate tasks (no artifact) feel like a skippable fallback, especially when upstream recall entries are already in context.

## Problem

The recall gate in /runbook and /inline has identical structure:
- **Path A:** recall-artifact.md exists → resolve from it
- **Path B (fallback):** no artifact → read memory-index, identify entries, resolve

For moderate tasks (most common /runbook entry), Path A is structurally unreachable — recall artifacts are produced during /design's complex path (Phase A.1 → write-outline.md). Path B is the actual primary path but is framed as a fallback, inviting skip rationalization when recall entries are already in context from upstream skills.

Additionally: the gate doesn't distinguish triage-scoped recall (loaded by /design) from implementation-scoped recall (needed by /runbook). The agent conflates "recall entries are in context" with "implementation-relevant recall has been done."

## Scope

Affected skills: /runbook (Tier 1 and Tier 2 recall gates), /inline (Phase 2.3 recall gate).

Changes:
- Reframe gate so memory-index scan is the constant action, artifact is an optimization (pre-curated list), not a branching condition
- Add implementation-scope signal: gate should select triggers relevant to implementation domain, not reuse triage triggers
- Preserve D+B anchor (tool call as structural proof)

## Evidence

- RCA session: problem-md-migration execution skipped /runbook recall gate
- "When anchoring gates with tool calls" (defense-in-depth.md): escape hatch IS the failure mode
- "When recall-artifact is absent during review" (pipeline-review.md): "proceed without" early exit = no recall at all
- "When step file inventory misses codebase references" (workflow-planning.md): relevant entry that implementation-scoped recall would have surfaced
