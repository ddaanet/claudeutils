# Runbook Outline Review: LLM Failure Mode Analysis

**Target:** `plans/worktree-update/runbook-outline.md`
**Review type:** LLM execution failure mode analysis, grounded in research
**Model:** haiku (48 TDD cycles)

---

## Review Methodology

Three review axes derived from empirical research on LLM code generation in TDD contexts.

### Axis 1: Vacuous Cycles

**Grounding:** [Where Do Large Language Models Fail When Generating Code?](https://arxiv.org/html/2406.08731v1) identifies "meaningless code snippet" as a distinct failure type — code that is "syntactically correct but irrelevant to the assigned task." In TDD runbooks, this manifests as cycles where the RED test verifies only scaffolding (import exists, function callable) and the GREEN implementation adds no behavioral substance. LLMs, especially smaller models, produce more meaningless code (13.6–31.7% "wrong logical direction" rate).

**Detection pattern:** A cycle is vacuous when:
- RED can be satisfied by `import X; assert callable(X)` or similar structural assertion
- GREEN adds ≤3 lines of non-branching code (no conditional logic, no state transformation)
- The cycle tests integration wiring (A calls B) rather than behavior (given X, observe Y)
- The cycle tests presentation format (output shape) rather than semantic correctness

**Risk:** Vacuous cycles don't constrain haiku's implementation. Without meaningful RED assertions, GREEN can pass with degenerate implementations. The cycle consumes budget without reducing defect space.

### Axis 2: Dependency Ordering

**Grounding:** [Tests as Prompt (WebApp1K, 2025)](https://arxiv.org/html/2505.09027v1) identifies dependency ordering as a critical failure mode. When cycles reference structures that don't exist yet, the executing model must either (a) create them ad-hoc (scope creep) or (b) mock them (implementation coupling). Both produce fragile GREEN implementations that break in later cycles.

Additional grounding from the WebApp1K error taxonomy: "API Call Mismatch" (Type C) and "Scope Violation" (Type F) are direct consequences of executing against structures that don't match the expected state.

**Detection pattern:** A dependency ordering problem exists when:
- Cycle N tests behavior that depends on structure created in cycle N+k (k>0)
- Cycle N's GREEN must assume a data shape that a later cycle establishes
- Refactoring in a later cycle invalidates GREEN from an earlier cycle

**Risk:** Haiku implements against the wrong structural assumption, then later cycles require rewriting earlier implementations. Wasted tokens and potential regression introduction.

### Axis 3: Cycle Density (Collapsibility)

**Grounding:** [Tests as Prompt (WebApp1K, 2025)](https://arxiv.org/html/2505.09027v1) demonstrates "instruction loss in long prompts" — as context grows, later instructions lose fidelity. 48 TDD cycles is substantial context accumulation for haiku. Each unnecessary cycle adds prompt length pressure during expansion AND execution.

Additionally, [TDD for Code Generation (Mathews & Nagappan, 2024)](https://arxiv.org/abs/2402.13521) shows that TDD remediation loops improve results (5.26% MBPP improvement), but only when tests encode meaningful requirements. Trivial tests don't contribute to the remediation signal.

**Detection pattern:** Cycles should collapse when:
- Two adjacent cycles test the same function with <1 branch point difference
- A cycle tests a single edge case that could be a parametrized test row in the prior cycle
- A cycle exists solely for a formatting/presentation concern separable from behavior

**Risk:** Bloated runbooks dilute the expansion agent's attention budget. Each unnecessary cycle means one fewer cycle where haiku gets high-quality RED/GREEN guidance.

---

## Findings

### F1: Vacuous Cycles (5 identified)

| Cycle | Issue | Evidence |
|-------|-------|----------|
| **0.1** | Import and register CLI group | RED: `from claudeutils.worktree.cli import worktree; assert worktree`. GREEN: one-line `cli.add_command(worktree)`. No behavior tested. |
| **5.1** | Use `wt_path()` for sibling paths | Tests that `new` calls `wt_path()` — integration wiring, not behavior. `wt_path()` already tested in Phase 1. |
| **5.6** | Environment initialization | Tests that `just setup` is called with `cwd`. Subprocess call verification, not behavioral outcome. |
| **5.9** | Tab-separated output format | Presentation format, not semantics. Project testing decisions: "test behavior, defer presentation to vet." |
| **6.1** | Use `wt_path()` for path resolution | Same as 5.1 — integration wiring for a function tested in Phase 1. |

**Impact:** 5 cycles (~10% of 48) that don't constrain implementation. Haiku can pass these with degenerate GREEN.

### F2: Dependency Ordering (1 critical)

**Phase 2 cycles 2.2 ↔ 2.4:**
- Cycle 2.2: Deduplication logic (avoid adding existing paths)
- Cycle 2.4: Nested key creation (`permissions.additionalDirectories`)

Dedup in 2.2 checks whether a path already exists in an array. But the array lives at `permissions.additionalDirectories` — a nested key path that cycle 2.4 creates. Cycle 2.2's GREEN must either:
- Assume flat structure → breaks when 2.4 changes to nested (regression)
- Pre-assume nested structure → testing behavior that 2.4 establishes (forward dependency)

**Recommended reorder:** Foundation-first:
1. 2.1: Basic read/write with nested key path (happy path, keys exist)
2. Missing file handling (create from nothing)
3. Nested key creation (handle partial JSON — keys absent)
4. Dedup (refinement on working function)

Each cycle's GREEN builds on the last without forward references.

### F3: Collapsible Cycles (4 groups, ~7 cycles reducible)

**Group A: Phase 0 → Phase 1 prefix (save 1 cycle)**

Phase 0 has 2 cycles for CLI registration. Cycle 0.1 is vacuous (F1). Cycle 0.2 ("verify hidden from help") is a single assertion. Merge 0.2 into Phase 1 cycle 1.1 as a pre-check: "register CLI group, verify hidden, then test `wt_path()` basic construction."

The outline's own expansion guidance already suggests this: "Phase 0 cycles could merge with Phase 1 start."

**Group B: Phase 3 entire phase (save 2 cycles)**

Phase 3 is "Fix edge cases in existing `derive_slug()` function" — 3 cycles for edge-case fixes on a 6-line function that already exists (`cli.py:12-26`). Each cycle's RED/GREEN is a single assertion + single `re.sub` or `.rstrip()` tweak.

Collapse to 1 cycle: "derive_slug edge cases (special chars, truncation, empty input)." Better yet, merge with cycle 5.8 (slug derivation in task mode) for integration coverage — again, the outline's own guidance suggests this.

**Group C: Phase 4 cycle 4.5 (save 1 cycle)**

"Output formatting (H1, status, sections)" — presentation, not behavior. The function's output format is part of cycle 4.1's contract (task extraction returns structured content). Merge formatting assertions into 4.1–4.3 as part of the behavioral assertions.

**Group D: Phase 5 + Phase 6 presentation/cleanup (save 2-3 cycles)**
- 5.9 (tab output) → merge into 5.8 (task mode). Tab format is the output contract of task mode, not a separate behavior.
- 6.5 (directory cleanup) + 6.6 (container cleanup) → collapse to 1 cycle "post-removal cleanup." Same concept (cleanup orphaned resources), same function, same test fixture.

**Net impact:** 48 → ~41 cycles. Tighter runbook, each remaining cycle has meaningful RED constraints.

### F4: Checkpoint Spacing

Phase 7 is the only phase with an explicit checkpoint. With 48 cycles (or ~41 after trimming), that's one quality gate for the entire runbook.

Research context:
- [WebApp1K](https://arxiv.org/html/2505.09027v1): "non-reasoning models understand semantics and write functioning code, but fail expectations" — pretraining bias overrides spec
- [Mathews 2024](https://arxiv.org/abs/2402.13521): remediation loops only work when tests encode meaningful requirements

Consider intermediate checkpoints after Phase 2 (JSON manipulation is error-prone for haiku) and Phase 5 (largest single phase, integration point for Phases 1-4).

---

## Summary

| Axis | Count | Severity | Recommendation |
|------|-------|----------|----------------|
| Vacuous cycles | 5 | Medium | Eliminate or merge into behavioral cycles |
| Dependency ordering | 1 | High | Reorder Phase 2: foundation → behavior → refinement |
| Collapsible cycles | 4 groups (~7 cycles) | Medium | 48 → ~41 cycles, tighter RED constraints |
| Checkpoint gaps | — | Low | Add checkpoints after Phase 2 and Phase 5 |

The Phase 2 ordering issue (F2) is the highest-risk finding — it will cause either regression or forward-dependency in haiku's GREEN implementations. The vacuous cycles (F1) and collapsible cycles (F3) compound with haiku's instruction-loss vulnerability at scale.

---

## Sources

- [Where Do Large Language Models Fail When Generating Code?](https://arxiv.org/html/2406.08731v1) — Error taxonomy, "meaningless code snippet" failure type, wrong-logical-direction rates by model size
- [Tests as Prompt: A TDD Benchmark for LLM Code Generation (WebApp1K)](https://arxiv.org/html/2505.09027v1) — Instruction loss in long prompts, pretraining bias overriding specs, error types A-G, dependency ordering
- [TDD for Code Generation (Mathews & Nagappan, ASE 2024)](https://arxiv.org/abs/2402.13521) — TDD effectiveness (+12.78%), remediation loop value (+5.26%), edge-case failure persistence
- [Microsoft: Taxonomy of Failure Modes in Agentic AI Systems](https://www.microsoft.com/en-us/security/blog/2025/04/24/new-whitepaper-outlines-the-taxonomy-of-failure-modes-in-ai-agents/) — Task decomposition and sequencing failures in agentic systems
- [Automated Test Generation Using LLMs](https://www.mdpi.com/2306-5729/10/10/156) — Test homogenization trap, silent correctness failures
- [AI-Generated Code Is Not Reproducible (Yet)](https://arxiv.org/pdf/2512.22387) — Data transcription failures, silent validation issues
