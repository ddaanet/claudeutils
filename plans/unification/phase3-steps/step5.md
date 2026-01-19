# Step 5

**Context**: Read `execution-context.md` for full context before executing this step.

---

### Step 5: Synthesize Unified Design Document

**Objective**: Combine all design sections into the final compose-api.md deliverable.

**Script Evaluation**: Medium task (assembly and coherence checking) - prose description

**Execution Model**: Sonnet (synthesis and coherence validation)

**Implementation**:
1. Read all design artifacts from Steps 1-4:
   - feature-extraction.md
   - core-module-design.md
   - cli-design.md
   - yaml-schema.md
2. Create unified document structure following phase3.md template:
   - Section 3.1: Core Composition Module (from step 2)
   - Section 3.2: CLI Entry Point (from step 3)
   - Section 3.3: YAML Schema (from step 4)
   - Additional sections: Integration notes, examples, implementation notes
3. Ensure coherence across sections:
   - CLI arguments match core module API
   - YAML schema supports all CLI modes
   - Examples use consistent patterns
   - No conflicting specifications
4. Add integration guidance:
   - How components work together
   - Data flow (YAML → parser → composition → output)
   - Error handling across layers
5. Add implementation notes:
   - Key decisions from feature extraction
   - Dependencies (libraries needed)
   - Testing approach
6. Write to: `scratch/consolidation/design/compose-api.md`
7. Write execution log to: `plans/unification/reports/phase3-step5-execution.md`

**Expected Outcome**: Unified design document ready for Phase 4 implementation.

**Unexpected Result Handling**:
- If design sections have inconsistencies: Document conflicts, propose resolutions, escalate if unclear
- If additional design decisions needed: Document gaps, escalate for decisions

**Error Conditions**:
- Design artifacts from previous steps not found → Escalate (steps may have failed)
- Cannot reconcile conflicting specifications → Document conflicts, escalate for architectural decision
- Design completeness unclear → Document gaps, escalate for requirements

**Validation**:
- Final design document exists at expected path
- All three main sections present and complete
- Cross-section coherence verified (no conflicts)
- Examples provided for each component
- Implementation notes sufficient for Phase 4

**Success Criteria**:
- Unified design created at `scratch/consolidation/design/compose-api.md`
- Document includes all sections from phase3.md:
  - 3.1 Core Composition Module (API, algorithm, examples)
  - 3.2 CLI Entry Point (subcommands, arguments, usage)
  - 3.3 YAML Schema (structure, validation, examples)
  - Integration notes (component interaction)
  - Implementation notes (dependencies, testing)
- Design is coherent (no conflicting specifications)
- Design is complete (sufficient for implementation)
- Execution report confirms synthesis and validation

**Report Path**: `plans/unification/reports/phase3-step-5.md`
**Artifact Path**: `scratch/consolidation/design/compose-api.md` (final deliverable)

---

## Design Decisions

### Sequential Execution Rationale

All steps must execute sequentially because:
- Step 2 depends on feature extraction from 1
- Step 3 depends on core module design from 2
- Step 4 depends on both core module and CLI from 2-3
- Step 5 depends on all previous design artifacts

No parallel execution possible.

### All-Sonnet Execution Model

All steps assigned to Sonnet (not Haiku) because:
- Design tasks require architectural judgment
- Semantic analysis needed for feature extraction
- API design requires understanding of trade-offs
- Schema design requires understanding of use cases
- Synthesis requires coherence validation across sections

This is not simple file manipulation - it's architectural design work.

### Artifact-per-Step Pattern

Each step produces its own design artifact rather than building one document incrementally because:
- Enables review of each design decision independently
- Supports revision of individual sections without rewriting entire document
- Provides audit trail of design evolution
- Allows parallel review by human (if desired)
- Final synthesis step ensures coherence

### Validation Strategy

Each step has explicit validation criteria focused on:
- Artifact existence at expected path
- Content completeness (required sections present)
- Actionability (sufficient detail for next step or implementation)
- Examples provided (demonstrates understanding)

No separate validation step needed - validation embedded in each step's success criteria.

---

## Context for Execution

**Plan-specific agents should receive**:
1. This execution plan (all decisions documented)
2. Step reference (which step to execute)
3. Instruction to write detailed output to report path AND artifact path
4. Instruction to return only: `done: <brief summary>` or `error: <description>`

**Example task prompt for Step 1**:
```
Execute Phase 3 Step 1 from the plan.

Plan: plans/unification/phase3-execution-plan.md
Step: 1 - Research Existing Composition Implementations

Write execution log to: plans/unification/reports/phase3-step-1.md
Write feature extraction to: scratch/consolidation/design/feature-extraction.md
Return only: "done: <summary>" or "error: <description>"
```

---

## Dependencies

**Before Phase 3**:
- Phase 2 analysis complete (provides context for design)
- Source files accessible:
  - tuick/agents/build.py (73 lines)
  - emojipack/agents/compose.sh
  - emojipack/agents/compose.yaml
- design.md decisions understood (composition model, directory structure)

**After Phase 3**:
- Phase 4 uses design document for implementation:
  - src/claudeutils/compose.py implementation
  - src/claudeutils/cli_compose.py implementation
  - YAML schema validation logic
- Design provides implementation specification
- All architectural decisions documented

---

## Notes

**Phase 3 is pure design** - no code implementation happens here.

**Design completeness critical** - Phase 4 implementation should not require additional design decisions.

**Sequential dependencies** - Orchestrator must execute steps in order (3.1 → 3.2 → 3.3 → 3.4 → 3.5).

**All-sonnet execution** - Every step requires design judgment, no simple file operations.

**Multiple artifacts** - Each step produces both execution log (reports/) and design artifact (design/), final step synthesizes into compose-api.md.


---

**Execution Instructions**:
1. Read execution-context.md for prerequisites, critical files, and execution notes
2. Execute this step following the actions listed above
3. Perform validation checks as specified
4. Document results in execution report
5. Stop on any unexpected results per communication rules
