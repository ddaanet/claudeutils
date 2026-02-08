# Outline: Parity Test Quality — Remaining Gap Fixes

**Source:** `rca.md` (5 gaps), `rca-review.md` (D+B impact), `rca-review-critique.md` (Opus corrections)

## Approach

Address 4 remaining gaps + 3 Opus-identified concerns through guidance updates, mechanical fixes, and tooling. Group by implementation complexity.

**Gap 3 status clarification (Opus Finding 1):** The D+B hybrid fix (merging prose gates into action steps + anchoring with tool calls) substantially mitigates prose gate skipping for the two modified skills (commit, orchestrate) but does not eliminate the class of failure. Gap 3 is mitigated in known instances with residual regression risk addressed by N1 (convention enforcement lint, experimental).

## Gap Prioritization (revised per Opus critique)

| Gap | Impact | Fix type | Complexity | Addresses |
|-----|--------|----------|------------|-----------|
| 1: No conformance validation | High (iterations 0-2) | Conformance tests + vet alignment | Moderate — planning guidance + vet enhancement | RCA Gap 1, RC1 |
| 4: Test description imprecision | High (enables Gap 1, iteration 1) | Guidance + convention | Low — decision doc + plan-tdd update | RCA Gap 4, RC5, Opus Finding 6 |
| 5: `--test`/`--lint` bypass paths | Medium (iteration 3) | Restrict to WIP commits | Low — commit skill clarification | RCA Gap 5, RC3, Opus Finding 2 |
| 2: No pre-write file size check | Low-medium (iterations 3-4) | Planning-time awareness | Low — runbook convention | RCA Gap 2, RC4, Opus Finding 3 |
| N1: Convention enforcement | Medium (regression risk) | Lint script (deferred — audit first) | Low — parse skill .md files | Opus Finding 7 |
| N2: Vet scope for conformance | Medium (RC2, iteration 1) | Vet alignment enhancement | Low — extend design anchoring | RCA RC2, Opus Finding 6 |
| N3: Empirical validation of D+B fix | Low (confidence check) | Test execution | Trivial — run commit skill, verify gates | Opus Finding 8 |

**Dependencies (Opus interaction analysis):**
- Gap 4 must be resolved before Gap 1 is effective — test descriptions must be precise enough for conformance tests to validate against
- Gap 3 + Gap 5 interaction — D+B ensures precommit runs at final commit; `--test`/`--lint` only apply to WIP commits where final precommit catches violations
- Gap 2 benefits from Gap 3 fix — D+B ensures commit-time file size check actually runs

## Resolved Decisions

**D1: Conformance validation mechanism (Gap 1, RC1, RC2)**

**Key concept:** Tests are executable contracts. Expected behavior is baked into test assertions at authoring time. The external reference (shell prototype, API spec, mockup) is consumed during test writing, not kept as a runtime dependency.

**Approach — two layers:**
- **Conformance tests (primary)** — Planner MUST include conformance test cycles when design has external reference. Tests capture exact expected strings/behavior derived from the reference. Reference is consumed at authoring time, not preserved as test artifact.
- **Vet alignment review (secondary)** — Vet-fix-agent includes alignment checking as standard practice (extension of existing design anchoring). Catches drift between implementation and specification through frequent fixing and re-alignment. Not conditional on a special field — alignment is always essential.

**Why not script-based diff:** One-off validation, not reproducible. Tests are permanent, in CI, and serve as living documentation of expected behavior.

**D2: Where does conformance validation trigger?**

**Decision:** Planner responsibility (mandatory). No orchestrator judgment required.

- Planner MUST include conformance test cycles when design has `Reference:` field or external spec
- Tests execute through normal TDD cycle infrastructure (no orchestration changes)
- Vet alignment review happens at standard checkpoints (no new trigger points)
- Orchestrator remains mechanical — no conformance-specific logic

**D3: Convention enforcement lint (N1) — deferred until validated**

- Scope: Skills only (agent-core/skills/*/SKILL.md). Not agents, not hooks.
- Check: Each `### N.` step heading must have a tool call within first 5 lines after the heading.
- **Warnings do not work** (learnings: "hard limits vs soft limits" — either fail build or don't check).
- Concerns: False positives on legitimate steps. Agent circumvention by adding meaningless tool calls to satisfy linter.
- **Approach:** Manual audit of existing skills first (Tier 2). If audit shows the convention holds with few exceptions, ship as hard fail with exemption marker (e.g., `<!-- no-tool-call-check -->`) for documented exceptions. If audit reveals many exceptions or the check is easily gamed, don't ship — the convention remains guidance only.

**Q1: `--test`/`--lint` bypass paths (Gap 5)**

**Decision:** Precommit is the right gate. D+B already ensures it runs at final commit.

- `--test` and `--lint` modes are for WIP commits only (TDD GREEN phase, lint-fix iterations)
- Final commits always use full `just precommit` which includes line limits
- No need to add line limits to `just test` or `just lint` — they serve different purposes
- Clarify in commit skill: `--test`/`--lint` are WIP-only, never for final commits

**Q2: Conformance cycles** — Mandatory when design has external reference. Not guidance.

**Q3: Skill step lint** — Deferred. Manual audit first. Ship as hard fail or don't ship. No warning mode.

**Q4: Vet alignment** — Always-on, not conditional. Prevents drift through frequent fixing and re-alignment. Extension of existing design anchoring, not a separate mode.

**Q5: Defense-in-depth documentation** — New file `agents/decisions/defense-in-depth.md`. Pattern applies broadly.

## Changes by File

| File | Change | Gap |
|------|--------|-----|
| `agents/decisions/testing.md` | Expand "Conformance Validation for Migrations" — tests as executable contracts, expected strings baked in, reference consumed at authoring time | Gap 4 |
| `agent-core/skills/plan-tdd/SKILL.md` | Mandatory conformance test cycles when design has external reference | Gap 1, 4 |
| `agent-core/skills/plan-adhoc/SKILL.md` | Same conformance guidance | Gap 1, 4 |
| `agent-core/agents/vet-fix-agent.md` | Extend design anchoring to include alignment checking as standard practice | N2, Gap 1 |
| `agent-core/skills/commit/SKILL.md` | Clarify `--test`/`--lint` are WIP-only, final commits always use full precommit | Gap 5 |
| `scripts/check_skill_steps.py` (new) | Lint: verify tool-call-first convention in skill steps (experimental) | N1 |
| `justfile` | Add skill step validation to precommit (hard fail, only if audit supports it) | N1 |
| `agents/decisions/workflow-advanced.md` | Update "Prose Test Descriptions Save Tokens" with conformance exception | Gap 4 |
| `agents/decisions/defense-in-depth.md` (new) | Document layered mitigation pattern, Gap 3+5 interaction | Q5 |
| `plans/reflect-rca-prose-gates/` | Add D+B empirical validation procedure | N3 |

## What This Doesn't Do

- No orchestration pipeline changes — conformance triggers through existing TDD cycles and vet checkpoints, not new orchestrator logic
- No persistent test artifacts from references — expected behavior baked into tests, reference consumed at authoring time
- No retroactive fix of existing plans — conventions apply going forward
- No pre-write hooks for file size (Gap 2 addressed through planning awareness + D+B-ensured commit-time check)
- No changes to D+B hybrid implementation (convention lint is complementary)
- No solution to concurrent pipeline evolution (scheduling concern, not quality gate)

## Concurrent Evolution Factor

The RCA raised whether iterations were inflated by pipeline changes happening in parallel (rca.md:253-265). This outline does NOT attempt to solve that — it's a scheduling/workflow concern, not a quality gate concern.

**Note:** Unresolved from original RCA. If it becomes a priority, it belongs in a separate job focused on workflow scheduling and plan lifecycle management.

## Implementation Tiers

**Tier 1 (trivial, immediate):**
- Gap 5: Clarify `--test`/`--lint` as WIP-only in commit skill (prose edit)
- N3: Document D+B empirical validation procedure

**Tier 2 (low complexity, single session):**
- Gap 4: Update testing.md and workflow-advanced.md with conformance precision guidance
- Gap 2: Add planning-time file size awareness to plan-tdd/plan-adhoc conventions
- Q5: Create defense-in-depth.md
- N1: Manual audit of existing skills for tool-call-first convention. Decision: hard fail lint or guidance only.

**Tier 3 (moderate, depends on Gap 4):**
- Gap 1: Mandatory conformance test cycles in plan-tdd/plan-adhoc
- N2: Extend vet-fix-agent alignment checking

**Sequencing:** Tier 1 → Tier 2 (parallel) → Tier 3 (after Gap 4 landed)
