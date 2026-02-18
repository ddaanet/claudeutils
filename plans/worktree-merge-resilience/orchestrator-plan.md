# Orchestrator Plan: worktree-merge-resilience

Execute steps sequentially using worktree-merge-resilience-task agent.

Stop on error and escalate to sonnet for diagnostic/fix.

## Model Directives

Step execution: per step metadata.
Vet-fix:
  Opus for Phase 1 (state machine routing, D-5 compliance).
  Opus for Step 5.3 (prose artifact, LLM-consumed).
  Sonnet for Phases 2–4 and Steps 5.1, 5.2.
Refactor: sonnet.

Principle: match review model to the correctness property, not the author's model.

## Step Execution Order

## step-1-1 (Cycle 1.1)

## step-1-2 (Cycle 1.2)

## step-1-3 (Cycle 1.3)

## step-1-4 (Cycle 1.4)

## step-1-5 (Cycle 1.5) — PHASE_BOUNDARY
[Last item of phase 1. Insert functional review checkpoint before Phase 2.]

## step-2-1 (Cycle 2.1)

## step-2-2 (Cycle 2.2) — PHASE_BOUNDARY
[Last item of phase 2. Insert functional review checkpoint before Phase 3.]

## step-3-1 (Cycle 3.1)

## step-3-2 (Cycle 3.2) — PHASE_BOUNDARY
[Last item of phase 3. Insert functional review checkpoint before Phase 4.]

## step-4-1 (Cycle 4.1) — PHASE_BOUNDARY
[Last item of phase 4. Insert functional review checkpoint before Phase 5.]

## step-5-1 (Step 5.1)

## step-5-2 (Step 5.2)

## step-5-3 (Step 5.3) — PHASE_BOUNDARY
[Last item of phase 5. Insert functional review checkpoint before Phase 6.]

