# Workflow Optimization Patterns

Patterns for efficient workflow execution, delegation, and resource usage.

## .Handoff Workflow

### How to End Workflow With Handoff And Commit

**Handoff tail-call:**

**Decision Date:** 2026-02-01

**Decision:** All tiers (1/2/3) must end with `/handoff --commit`, never bare `/commit`.

**Anti-pattern:** Tier 1/2 skip handoff because "no session restart needed"

**Correct pattern:** Always tail-call `/handoff --commit` — handoff captures session context and learnings regardless of tier

**Rationale:** Handoff is about context preservation, not just session restart. Even direct implementations produce learnings and update pending task state.

**Impact:** Consistent workflow termination across all tier levels.

### When Handoff Includes Commit Flag

**Handoff commit assumption:**

**Decision Date:** 2026-02-01

**Decision:** session.md reflects post-commit state when `--commit` flag is used.

**Anti-pattern:** Writing "Ready to commit" in Status or "pending commit" in footer when `--commit` flag is active

**Correct pattern:** Write status reflecting post-commit state — the tail-call makes commit atomic with handoff

**Rationale:** Next session reads session.md post-commit. Stale commit-pending language causes agents to re-attempt already-completed commits. The rule against commit tasks in Pending/Next Steps must extend to ALL sections.

**Generalization:** Next Steps must contain only actions performable from the current context. Cross-context actions (commit when `--commit` active, merge-to-main from source worktree) create false affordances that agents promote into STATUS task slots. Same principle, different venues.

**Impact:** Prevents duplicate commit attempts and cross-context action leakage in subsequent sessions.

## .Workflow Efficiency

### When Context Already Loaded For Delegation

**Delegation with context:**

**Decision Date:** 2026-02-01

**Decision:** Don't delegate when context is already loaded.

**Anti-pattern:** Reading files, gathering context, then delegating to another agent (which re-reads everything)

**Correct pattern:** If you already have files in context, execute directly — delegation adds re-reading overhead

**Rationale:** Token economy. Agent overhead (context setup + re-reading) exceeds cost of continuing in current model.

**Corollary:** Delegate when task requires *new* exploration you haven't done yet.

**Impact:** Reduces token waste from redundant context loading.

### When Complexity Assessed Twice

**Single-layer complexity:**

**Decision Date:** 2026-02-01

**Decision:** Single-layer complexity assessment, not double assessment.

**Anti-pattern:** Entry point skill assesses complexity, then routes to planning skill which re-assesses complexity (tier assessment)

**Correct pattern:** Single entry point with triage that routes directly to the appropriate depth — no intermediate routing layer

**Rationale:** Each assessment reads files, analyzes scope, produces output. Two assessments for the same purpose is pure waste.

**Example:** Oneshot assessed simple/moderate/complex, then /plan-adhoc re-assessed Tier 1/2/3 — same function, different labels.

**Impact:** Eliminates redundant analysis overhead.

### When Reusing Review Agent Context

**Decision Date:** 2026-02-01

**Decision:** Leverage review agent context for fixes instead of launching new agents.

**Anti-pattern:** When removal agent makes mistakes and review catches them, launching a new fix agent (which re-reads everything)

**Correct pattern:** If review agent has context of what's wrong, leverage it. If caller also has context (from reading review report), apply fixes directly.

**Rationale:** Tier 1/2 pattern — caller reads report, applies fixes with full context. No need for another agent round-trip.

**Impact:** Faster fix cycles without redundant context loading.

### When Delegating Well-Specified Prose Edits

**Decision Date:** 2026-02-24

**Anti-pattern:** Applying "opus for prose artifacts" model rule to justify delegation when the cognitive work (designing what to add) was already done at opus during design. Launches N agents for N independent file edits, each re-reading files already in planner context.

**Correct pattern:** The "opus for prose artifacts" rule targets cases where design decisions happen during editing. When an outline pre-resolves all decisions and specifies exact insertion points, execution is mechanical. The "design resolves to simple execution" decision applies: delegation ceremony exceeds edit cost for all-prose work.

**Evidence:** 4 opus artisan agents launched for 47 lines of prose insertions across 4 skill files.

### When Designing Context Preloading Mechanisms

**Decision Date:** 2026-02-24

**Anti-pattern:** Injecting content via @ref expansion in session.md, then having workflow skills Read the same files. @ref expansion puts content in system prompt; Read puts content in conversation messages. Both are cumulative — content appears twice, doubling token cost.

**Correct pattern:** Use explicit skill invocation instead of implicit session.md injection. Skill Reads content into conversation once. No system-prompt duplication. Infrastructure to automate preloading exceeds the cost of explicit skill call.

**Evidence:** 8-round design discussion explored @ref preload → SessionStart hook → scripted gate → all dropped. Final: `/prime` skill chain-calls `/recall`.

## .Design Process Gates

### When Design Ceremony Continues After Uncertainty Resolves

**Decision Date:** 2026-02-18

**Anti-pattern:** One-shot complexity triage at `/design` entry, no re-assessment when outline resolves architectural uncertainty. Process continues at "complex" even when outline reveals 2-file prose edits.

**Correct pattern:** Two gates. Entry gate reads plan directory artifacts (existing outline can skip ceremony). Mid-stream gate re-checks complexity after outline production. Both internal to `/design` — preserves single entry point.

**Evidence:** outline-corrector + design.md + design-corrector cost ~112K tokens for work that could have been done inline. Findings would have surfaced during editing.

### When Design Resolves To Simple Execution

**Decision Date:** 2026-02-18 (updated 2026-02-19: replaced ≤3 files heuristic with coordination complexity discriminator)

**Anti-pattern:** Always routing from `/design` to `/runbook` after sufficiency gate, regardless of execution complexity. Complex design classification persists through the pipeline even when design resolves the uncertainty.

**Correct pattern:** Execution readiness gate at sufficiency gate using coordination complexity discriminator. All of: decisions pre-resolved, changes additive, cross-file deps phase-ordered, content derivable from architecture section → design is execution-ready, skip `/runbook`.

File count is a proxy — 7 files with independent additive changes can be simpler than 2 files with interleaving structural changes. The underlying property is "no implementation loops across any phase."

**Rationale:** Design can resolve complexity. A job correctly classified as Complex for design may produce Simple execution. The gate is subtractive (creates exit ramp), not additive (more ceremony).

**Strongest signal:** All-prose phases with no feedback loop — execute inline from design outline. Delegation ceremony (agent startup, file re-reads, report write/read) exceeds edit cost. Evidence: error-handling runbook used 11 opus agents for ~250 lines of prose; runbook-corrector caught a regression *introduced* by the generation process.

## .Research and Methodology

### When Writing Methodology

**Decision Date:** 2026-02-18 (updated 2026-02-21: added general-first framing rule)

**Anti-pattern:** Producing scoring frameworks, evaluation axes, or "best practice" documents from internal reasoning alone — yields confabulated methodologies with subjective weights and ungrounded criteria. Also: framing grounded output as project-specific problems validated by external research (inverted framing).

**Correct pattern:** Invoke `/ground` skill. Diverge-converge with parallel branches: internal explore (codebase or conceptual scope for project-specific dimensions) + external research (web search for established frameworks). Both run as parallel Task agents writing to `plans/reports/`. Synthesize by mapping internal dimensions onto external skeleton.

**Framing rule — general first:** State each principle as the general insight derived from external research. Project-specific implementation is an instance that validates the principle. The internal branch confirms applicability; it does not define the principle. Inverted framing (project-specific → external validation) produces entries that read as local fixes rather than transferable knowledge.

**Evidence:** First prioritization attempt produced subjective weights ("Highest/High/Medium") and 0-3 scores without defined criteria. After grounding in WSJF research, methodology used Fibonacci scoring with observable evidence sources. Code-density grounding produced project-specific entries ("Git state queries return booleans — `_git_ok()`") that should have been general principles with project instances.


