# Step 3.7: Update Workflow Optimization Decisions

**Status:** Complete

## Deliverable

Added to `agents/decisions/workflow-optimization.md` under new `.Continuation Passing` section:

### Continuation Passing Pattern
- Summary of D-1 through D-7 decisions
- Anti-pattern: hardcoded tail-calls
- Correct pattern: peel-first-pass-remainder with default-exit fallback
- Cross-references to fragment and design.md

### Hook-Based Parsing Rationale
- Why hook over fragment-only approach
- Deterministic regex + registry lookup
- Context-aware filtering (whitespace, paths, note: prefix)
- Empirical validation results: 0% FP rate

## Index

Added 2 entries to `agents/memory-index.md` under existing `agents/decisions/workflow-optimization.md` section:
- Continuation passing pattern
- Hook-based parsing rationale
