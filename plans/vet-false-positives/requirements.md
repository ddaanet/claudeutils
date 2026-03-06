# Vet False Positive Suppression

## Requirements

### Functional Requirements

**FR-1: Proactive suppression taxonomy for corrector**
Add a "Do NOT Flag" section to `agent-core/agents/corrector.md` that enumerates categories of findings the agent should suppress before raising them as issues. Categories:

1. **Pre-existing issues** — Problems that existed before the current change. The corrector reviews a diff, not the entire codebase. If a pattern existed in the file before the change, it is not a finding.
2. **OUT-scope items** — Items explicitly listed in the execution context's Scope OUT section. Currently handled reactively (raised then classified DEFERRED/OUT-OF-SCOPE). Proactive suppression prevents the finding from being raised at all.
3. **Pattern-consistent style** — Code that follows existing project patterns, even if the pattern itself is suboptimal. If 10 functions use `snake_case` and the new function uses `snake_case`, that is not a style finding. Existing pattern check (investigation gate 3) already exists for UNFIXABLE — extend to all findings.
4. **Linter-catchable issues** — Issues that mechanical linting tools detect deterministically (formatting, import ordering, unused imports, type annotation style). These are better caught by `just lint` / `just check` than by LLM judgment. The corrector should focus on semantic issues linters cannot catch.

Acceptance: Each category has a clear definition, anti-pattern example, and "instead" guidance in the agent prompt.

**FR-2: Proactive suppression taxonomy for runbook-corrector**
Add a "Do NOT Flag" section to `agent-core/agents/runbook-corrector.md` with planning-appropriate categories:

1. **Pre-existing issues** — Defects in the outline or design that the runbook faithfully reproduces. The runbook-corrector reviews the expansion, not the design. Design defects belong to design-corrector.
2. **OUT-scope items** — Steps or features explicitly deferred in the design's Out of Scope section. Already partially addressed via UNFIXABLE investigation gates — make suppression proactive.
3. **Inherited design decisions** — Architectural choices made in the design document that the runbook implements. The runbook-corrector should not second-guess design decisions — those were reviewed by design-corrector.
4. **Expansion guidance conformance** — When the outline's Expansion Guidance section directs a specific approach, the expanded runbook following that guidance is not a finding.

Acceptance: Each category has a clear definition and example in the agent prompt.

**FR-3: Relationship to existing status taxonomy**
The "Do NOT Flag" taxonomy operates upstream of the existing Status Taxonomy (FIXED/DEFERRED/OUT-OF-SCOPE/UNFIXABLE). Findings that match a suppression category should never enter the issue list. This is proactive suppression, not reactive classification.

Document this relationship explicitly in both agent prompts: "Do NOT Flag categories prevent findings from being raised. Status Taxonomy classifies findings that were correctly raised."

Acceptance: Both agents contain clear prose distinguishing suppression (pre-finding) from classification (post-finding).

### Non-Functional Requirements

**NFR-1: Evidence-grounded categories**
Every suppression category must trace to documented evidence of false positives in `agents/decisions/` files. No invented categories — each must have a decision record showing the false positive pattern occurred.

**NFR-2: No confidence scoring**
The taxonomy is categorical (suppress/don't suppress), not scored. No numeric thresholds. Rationale: single-reviewer context (no inter-reviewer noise to score), no calibration data for thresholds, categorical matches the binary nature of the false positive evidence.

### Constraints

**C-1: Prose artifact edits**
Both corrector agent definitions are LLM-consumed prose artifacts. Wording directly determines downstream agent behavior. Changes require opus model tier per `pipeline-contracts.md` "When Selecting Model For Prose Artifact Edits."

**C-2: Additive, not restructuring**
Add "Do NOT Flag" sections to existing agents. Do not restructure Status Taxonomy, investigation gates, or review protocol. The suppression taxonomy is a new layer, not a replacement.

**C-3: Agent line budget awareness**
corrector.md is currently 527 lines. Keep additions concise — each category should be 3-5 lines (definition + anti-pattern + guidance), not exhaustive documentation.

### Out of Scope

- Confidence scoring mechanism — Deferred pending calibration data. Categorical suppression addresses the immediate false positive problem.
- design-corrector, outline-corrector, runbook-outline-corrector — Already have adequate scope controls and run at opus (fewer false positives per 2x2 experiment evidence). Extend to these agents only if evidence warrants.
- Modifying the UNFIXABLE investigation gates — Existing 4-gate protocol stays unchanged. Suppression is upstream.
- Shared fragment across correctors — Categories are agent-type-specific (code vs planning). A shared fragment would be too generic or awkwardly partitioned.

### References

- `agents/decisions/pipeline-contracts.md` — Vet escalation calibration, out-of-scope flagging, execution context
- `agents/decisions/orchestration-execution.md` — Vet flags unused code (test callers ≠ dead code)
- `agents/decisions/operational-practices.md` — Validate-runbook flags pre-existing files
- `agents/decisions/execution-strategy.md` — Corrector/lint division of responsibility (semantic vs mechanical)
- `plans/reports/anthropic-plugin-exploration.md` — code-review plugin confidence scoring (0-100, threshold ≥80)

### Skill Dependencies (for /design)

- Load `plugin-dev:agent-development` before design (agent definition edits in FR-1, FR-2)
