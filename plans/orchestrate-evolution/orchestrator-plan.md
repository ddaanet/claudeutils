# Orchestrator Plan: orchestrate-evolution

Execute steps using per-phase agents.

Stop on error and escalate to sonnet for diagnostic/fix.

## Phase-Agent Mapping

| Phase | Agent | Type |
| --- | --- | --- |
| 1 | crew-orchestrate-evolution-p1 | tdd |
| 2 | crew-orchestrate-evolution-p2 | tdd |
| 3 | crew-orchestrate-evolution-p3 | tdd |
| 4 | crew-orchestrate-evolution-p4 | general |


## Step Execution Order

## step-1-1 (Cycle 1.1)
Agent: crew-orchestrate-evolution-p1
Execution: steps/step-1-1.md

## step-1-2 (Cycle 1.2)
Agent: crew-orchestrate-evolution-p1
Execution: steps/step-1-2.md

## step-1-3 (Cycle 1.3)
Agent: crew-orchestrate-evolution-p1
Execution: steps/step-1-3.md

## step-1-4 (Cycle 1.4) — PHASE_BOUNDARY
Agent: crew-orchestrate-evolution-p1
Execution: steps/step-1-4.md
Phase file: plans/orchestrate-evolution/runbook-phase-1.md
[Last item of phase 1. Insert functional review checkpoint before Phase 2.]

## step-2-1 (Cycle 2.1)
Agent: crew-orchestrate-evolution-p2
Execution: steps/step-2-1.md

## step-2-2 (Cycle 2.2)
Agent: crew-orchestrate-evolution-p2
Execution: steps/step-2-2.md

## step-2-3 (Cycle 2.3)
Agent: crew-orchestrate-evolution-p2
Execution: steps/step-2-3.md

## step-2-4 (Cycle 2.4) — PHASE_BOUNDARY
Agent: crew-orchestrate-evolution-p2
Execution: steps/step-2-4.md
Phase file: plans/orchestrate-evolution/runbook-phase-2.md
[Last item of phase 2. Insert functional review checkpoint before Phase 3.]

## step-3-1 (Cycle 3.1)
Agent: crew-orchestrate-evolution-p3
Execution: steps/step-3-1.md

## step-3-2 (Cycle 3.2)
Agent: crew-orchestrate-evolution-p3
Execution: steps/step-3-2.md

## step-3-3 (Cycle 3.3)
Agent: crew-orchestrate-evolution-p3
Execution: steps/step-3-3.md

## step-3-4 (Cycle 3.4) — PHASE_BOUNDARY
Agent: crew-orchestrate-evolution-p3
Execution: steps/step-3-4.md
Phase file: plans/orchestrate-evolution/runbook-phase-3.md
[Last item of phase 3. Insert functional review checkpoint before Phase 4.]

## step-4-1 (Step 4.1)
Agent: crew-orchestrate-evolution-p4
Execution: steps/step-4-1.md

## step-4-2 (Step 4.2) — PHASE_BOUNDARY
Agent: crew-orchestrate-evolution-p4
Execution: steps/step-4-2.md
Phase file: plans/orchestrate-evolution/runbook-phase-4.md
[Last item of phase 4. Insert functional review checkpoint before Phase 5.]


## Phase Models

- Phase 1: sonnet
- Phase 2: sonnet
- Phase 3: sonnet
- Phase 4: opus
