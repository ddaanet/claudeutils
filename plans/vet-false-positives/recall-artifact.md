# Recall Artifact: Vet False Positives

Resolve entries via `claudeutils _recall resolve` — do not use inline summaries.

## Entry Keys

when vet escalation calibration — over-UNFIXABLE pattern, agents treat uncertainty as escalation
when vet flags out-of-scope items — DEFERRED vs UNFIXABLE distinction, scope OUT matching
when vet receives execution context — filesystem vs execution-time state, explicit context required
when vet flags unused code — test callers mistaken for dead code, design-intent infrastructure
when validate-runbook flags pre-existing files — lifecycle false positive for modify-before-create
when requiring per-artifact vet coverage — batch momentum skip prevention
when scoping vet for cross-cutting invariants — verification scope beyond changed-files
when adding verification scope to vet context — cross-cutting invariant indicators
when outline review produces ungrounded corrections — confabulated operation sequences, model tier
when running multi-reviewer diagnostics — parallel independent cross-reference false positive
