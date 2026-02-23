# Orchestrator Plan: remember-skill-update

Execute steps sequentially using remember-skill-update-task agent.

Stop on error and escalate to sonnet for diagnostic/fix.

## Step Execution Order

## step-1-1 (Cycle 1.1)
Execution: steps/step-1-1.md

## step-1-2 (Cycle 1.2)
Execution: steps/step-1-2.md

## step-1-3 (Cycle 1.3) — PHASE_BOUNDARY
Execution: steps/step-1-3.md
[Last item of phase 1. Insert functional review checkpoint before Phase 2.]

## step-2-1 (Step 2.1)
Execution: steps/step-2-1.md

## step-2-2 (Step 2.2)
Execution: steps/step-2-2.md

## step-2-3 (Step 2.3)
Execution: steps/step-2-3.md

## step-2-4 (Step 2.4)
Execution: steps/step-2-4.md

## step-2-5 (Step 2.5) — PHASE_BOUNDARY
Execution: steps/step-2-5.md
[Last item of phase 2. Insert functional review checkpoint before Phase 3.]

## step-3-1 (Step 3.1) — PHASE_BOUNDARY
Execution: steps/step-3-1.md
[Last item of phase 3. Insert functional review checkpoint before Phase 4.]

## step-4-1 (Cycle 4.1)
Execution: steps/step-4-1.md

## step-4-2 (Cycle 4.2)
Execution: steps/step-4-2.md

## step-4-3 (Cycle 4.3) — PHASE_BOUNDARY
Execution: steps/step-4-3.md
[Last item of phase 4. Insert functional review checkpoint before Phase 5.]

## step-6-1 (Step 6.1)
Execution: steps/step-6-1.md

## step-6-2 (Step 6.2) — PHASE_BOUNDARY
Execution: steps/step-6-2.md
[Last item of phase 6. Insert functional review checkpoint before Phase 7.]


## Phase Models

- Phase 1: sonnet
- Phase 2: opus
- Phase 3: opus
- Phase 4: sonnet
- Phase 6: sonnet
