# Update Grounding Skill: Outline

## Approach

Three changes:
1. Both diverge branches run as parallel Task agents writing exploration artifacts to `plans/reports/` for audit
2. Unify "brainstorm"/"explore" into a single **explore** mode with a scope parameter (codebase vs conceptual)
3. Remove conditional delete/promote logic — all branch artifacts retained

## Key Decisions

1. **Unified internal branch mode:** Replace brainstorm/explore distinction with `explore(scope=codebase)` and `explore(scope=conceptual)`. Both are exploration — they differ in what's explored and model tier, not in kind.
   - `scope=codebase`: Surface existing patterns, conventions, prior decisions. Scout agent, sonnet.
   - `scope=conceptual`: Generate project-specific dimensions, constraints, evaluation axes from project context. General-purpose agent, opus (generative divergence still requires opus).
2. **External branch agent type:** general-purpose — needs WebSearch/WebFetch (unavailable in scout). Skill prompt controls behavior.
3. **Artifact paths:** All branches write directly to `plans/reports/<topic>-{internal-codebase|internal-conceptual|external-research}.md`. No tmp/ staging.
4. **Retention:** All branch artifacts retained unconditionally as audit evidence. Grounding report references them.
5. **Model for external agent:** sonnet — search + synthesis, not generative divergence.

## Changes

### SKILL.md

**Phase 1 (Scope) — parameter selection:**
- Replace "Internal branch type: brainstorm / explore" with "Internal scope: codebase / conceptual"
- Update selection criteria: codebase = "what patterns exist for X", conceptual = "what dimensions/constraints apply to X"
- Model tier follows scope: codebase → sonnet (scout), conceptual → opus (general-purpose)

**Phase 2, Branch A (Internal):**
- Rewrite as unified explore with scope parameter
- `scope=codebase`: Scout agent, writes `plans/reports/<topic>-internal-codebase.md`
- `scope=conceptual`: General-purpose/opus, writes `plans/reports/<topic>-internal-conceptual.md`
- Both: agent writes report, returns filepath (quiet execution pattern)

**Phase 2, Branch B (External):**
- Change from inline execution to Task agent delegation
- Agent: general-purpose, model: sonnet
- Prompt includes: topic, search query templates (from grounding-criteria.md), evaluation criteria, output format contract
- Output: `plans/reports/<topic>-external-research.md`
- Agent writes report, returns filepath (quiet execution pattern)

**Phase 2 dispatch:**
- Explicit instruction: launch both Task calls in a single message for parallel execution

**Phase 4 (Output):**
- Remove "Branch file retention" section (conditional move/delete)
- Replace with: "Branch artifacts in `plans/reports/` are retained as audit evidence. The grounding report references both."
- Remove all tmp/ file references

### grounding-criteria.md

**Parameterization guide:**
- Replace "Internal branch: brainstorm / explore" row with "Internal scope: codebase / conceptual"
- Update selection criteria text
- Update model tier row to reference scope not branch type

**Convergence template:**
- Update references from tmp paths to plans/reports/ paths
- Add: "Both branch artifacts are inputs to convergence — read them from plans/reports/"

### workflow-optimization.md

**"When Writing Methodology" entry:**
- Update "brainstorm" references to "conceptual explore" or equivalent
- Update "When Brainstorming" entry if it references ground skill specifically

## Scope

**IN:**
- `agent-core/skills/ground/SKILL.md` — Phases 1, 2, 4
- `agent-core/skills/ground/references/grounding-criteria.md` — parameterization + convergence template
- `agents/decisions/workflow-optimization.md` — terminology alignment

**OUT:**
- New agent definitions (general-purpose + scout are sufficient)
- Scout agent changes (already correct for codebase scope)
- Phase 3 (Converge) logic — synthesis process unchanged, just reads from new paths
