# Phase 3 Execution Plan - Design Unified Composition API

**Context**: This plan expands Phase 3 with all design decisions documented for weak orchestrator execution.

**Source**: `plans/unification/phases/phase3.md`
**Design**: `plans/unification/design.md`
**Common Context**: `plans/unification/phases/consolidation-context.md`

**Status**: Ready
**Created**: 2026-01-19
**Reviewed**: 2026-01-19 (Sonnet, READY)

---

## Weak Orchestrator Metadata

**Total Steps**: 5

**Execution Model**:
- Steps 1-4: Sonnet (design and semantic analysis tasks)
- Step 5: Sonnet (document synthesis and coherence checking)

**Step Dependencies**: Sequential (1 → 2 → 3 → 4 → 5)
- Each step builds on outputs from previous steps
- No parallel execution possible

**Error Escalation**:
- Sonnet → User: Design decisions unclear, conflicting requirements found, architectural choices needed
- Sonnet → User: Source files missing or significantly different than expected

**Report Locations**:
- Execution logs: `plans/unification/reports/phase3-step{N}-execution.md`
- Design artifacts: `scratch/consolidation/design/` (created by Step 3.1)
- Final deliverable: `scratch/consolidation/design/compose-api.md`

**Success Criteria**:
- Complete design document created at `scratch/consolidation/design/compose-api.md`
- All three sections documented (Core Module, CLI, YAML Schema)
- Design includes: API surface, module structure, usage patterns, examples
- Design is actionable (sufficient detail for Phase 4 implementation)
- No unresolved design questions

**Prerequisites**:
- Source files exist and readable:
  - /Users/david/code/tuick/agents/build.py (✓ 73 lines per context)
  - /Users/david/code/emojipack/agents/compose.sh
  - /Users/david/code/emojipack/agents/compose.yaml
- Phase 2 analysis complete (provides context for design decisions):
  - `scratch/consolidation/analysis/pytest-md-fragmentation.md`
  - `scratch/consolidation/analysis/justfile-*.patch`
- scratch/consolidation/design/ directory will be created by Step 1

---

### Step 1: Research Existing Composition Implementations

**Objective**: Extract features and patterns from existing composition implementations to inform API design.

**Script Evaluation**: Medium task (analysis requiring semantic understanding) - prose description

**Execution Model**: Sonnet (semantic analysis of code patterns)

**Implementation**:
1. Read and analyze tuick/agents/build.py:
   - Extract composition algorithm (fragment concatenation)
   - Extract header manipulation logic (increase_header_levels function)
   - Extract decorator injection patterns (title + separators)
   - Identify YAML config parsing approach
   - Document output modes (agents mode, role mode)
2. Read and analyze emojipack composition pattern:
   - Read compose.sh for shell-based approach
   - Read compose.yaml for configuration structure
   - Identify similarities/differences with tuick approach
3. Create feature extraction report:
   - List all features found in existing implementations
   - Categorize by: core composition, text manipulation, configuration, CLI
   - Note which features are essential vs optional
   - Identify patterns to preserve vs improve
4. Create design directory: `mkdir -p scratch/consolidation/design`
5. Write findings to: `scratch/consolidation/design/feature-extraction.md`
6. Write execution log to: `plans/unification/reports/phase3-step1-execution.md`

**Expected Outcome**: Feature extraction document with:
- Complete feature list from tuick/build.py
- Comparison with emojipack approach
- Categorized features (essential/optional)
- Recommendations for API design

**Unexpected Result Handling**:
- If tuick/build.py is significantly larger than 73 lines: Document actual size, analyze anyway
- If emojipack uses different composition approach than expected: Document approach, compare trade-offs
- If critical features are missing: Note gaps, recommend additions

**Error Conditions**:
- Source file not found → Verify paths, escalate to user if files moved
- Source file unreadable → Report permissions issue, escalate
- Conflicting patterns between implementations → Document conflict, escalate for architectural decision

**Validation**:
- Feature extraction document exists at expected path
- All source files analyzed (tuick build.py, emojipack compose.sh/yaml)
- Features categorized by type
- Recommendations provided for API design

**Success Criteria**:
- Feature extraction document created at `scratch/consolidation/design/feature-extraction.md`
- Document includes:
  - Complete feature list (at least 5-7 features from tuick)
  - Pattern comparison (tuick vs emojipack)
  - Feature categorization (core/manipulation/config/CLI)
  - Design recommendations
- Execution report documents analysis process

**Report Path**: `plans/unification/reports/phase3-step-1.md`
**Artifact Path**: `scratch/consolidation/design/feature-extraction.md`

---

### Step 2: Design Core Composition Module

**Objective**: Design the composition engine module (src/claudeutils/compose.py) based on extracted features.

**Script Evaluation**: Large design task - prose description

**Execution Model**: Sonnet (architectural design)

**Implementation**:
1. Read feature extraction from Step 1
2. Design module structure:
   - Define main composition function signature
   - Define helper functions (header manipulation, decorator injection, etc.)
   - Define data structures for configuration
   - Define error handling approach
3. Design composition algorithm:
   - Fragment loading (from file paths)
   - Fragment concatenation (order preservation)
   - Header level adjustment (increase_header_levels)
   - Decorator injection (title, separators)
   - Output generation
4. Design text manipulation utilities:
   - Header level detection and manipulation
   - Markdown structure preservation
   - Whitespace handling
5. Create design document section:
   - Module overview (purpose, scope)
   - API surface (public functions and signatures)
   - Algorithm description (step-by-step composition process)
   - Examples (code usage examples)
6. Write to: `scratch/consolidation/design/core-module-design.md`
7. Write execution log to: `plans/unification/reports/phase3-step2-execution.md`

**Expected Outcome**: Core module design document with:
- Clear module structure (functions, classes if needed)
- Detailed composition algorithm
- API signatures with type hints
- Usage examples

**Unexpected Result Handling**:
- If feature extraction reveals conflicting requirements: Propose resolution, escalate if unclear
- If complexity exceeds single-module scope: Propose multi-module structure, escalate for approval

**Error Conditions**:
- Feature extraction not found → Escalate (Step 1 may have failed)
- Design decisions unclear → Document alternatives, escalate for architectural choice
- Cannot reconcile tuick vs emojipack approaches → Document trade-offs, escalate for decision

**Validation**:
- Design document exists at expected path
- Module structure clearly defined
- API signatures specified
- Composition algorithm documented
- At least 2 usage examples provided

**Success Criteria**:
- Core module design created at `scratch/consolidation/design/core-module-design.md`
- Document includes:
  - Module structure (functions, parameters, return types)
  - Composition algorithm (detailed steps)
  - Text manipulation utilities (header levels, decorators)
  - API examples (at least 2)
- Design is implementable (sufficient detail for coding)
- Execution report documents design decisions

**Report Path**: `plans/unification/reports/phase3-step-2.md`
**Artifact Path**: `scratch/consolidation/design/core-module-design.md`

---

### Step 3: Design CLI Entry Point

**Objective**: Design the CLI interface for composition commands (claudeutils compose).

**Script Evaluation**: Medium design task - prose description

**Execution Model**: Sonnet (interface design)

**Implementation**:
1. Read core module design from Step 2
2. Design CLI subcommand structure:
   - `claudeutils compose <config-file>` for CLAUDE.md generation
   - `claudeutils compose role` for role file generation (tuick pattern)
   - Future extensibility for other modes
3. Design command-line arguments:
   - Config file path (required)
   - Output path (optional, default from config)
   - Verbosity flags (optional)
   - Validation flags (optional)
4. Design pyproject.toml integration:
   - Entry point definition
   - Subcommand routing
5. Create usage pattern examples:
   - Simple CLAUDE.md generation
   - Role file generation with arguments
   - Integration with justfile/Makefile
6. Write to: `scratch/consolidation/design/cli-design.md`
7. Write execution log to: `plans/unification/reports/phase3-step3-execution.md`

**Expected Outcome**: CLI design document with:
- Complete subcommand structure
- Argument specifications
- Usage examples
- Integration patterns

**Unexpected Result Handling**:
- If role mode requires significantly different CLI pattern: Propose alternatives, escalate if unclear
- If argument combinations create complexity: Simplify or propose phased approach

**Error Conditions**:
- Core module design not found → Escalate (Step 2 may have failed)
- Cannot determine appropriate CLI pattern → Document options, escalate for decision
- pyproject.toml integration unclear → Research existing patterns, escalate if needed

**Validation**:
- Design document exists at expected path
- Subcommand structure defined
- Arguments specified with types
- At least 3 usage examples provided
- pyproject.toml integration documented

**Success Criteria**:
- CLI design created at `scratch/consolidation/design/cli-design.md`
- Document includes:
  - Subcommand structure (compose, compose role, future modes)
  - Argument specifications (required/optional, types, defaults)
  - Usage examples (at least 3 complete examples)
  - pyproject.toml entry point definition
- Design matches patterns in design.md
- Execution report documents CLI decisions

**Report Path**: `plans/unification/reports/phase3-step-3.md`
**Artifact Path**: `scratch/consolidation/design/cli-design.md`

---

### Step 4: Design YAML Configuration Schema

**Objective**: Design the YAML configuration format for composition definitions.

**Script Evaluation**: Medium design task - prose description

**Execution Model**: Sonnet (schema design)

**Implementation**:
1. Read core module design from Step 2
2. Read CLI design from Step 3.3
3. Review existing emojipack compose.yaml for reference
4. Design YAML schema structure:
   - `sources`: Path mappings (YAML anchors for deduplication)
   - `fragments`: Ordered list of fragments to compose
   - `output`: Output file path
   - `mode`: Composition mode (agents, role, skill)
   - Optional sections (validation, decorators, etc.)
5. Define schema validation rules:
   - Required fields
   - Field types
   - Path validation (files must exist)
   - Fragment order preservation
6. Create complete examples:
   - Simple CLAUDE.md generation (agents mode)
   - Role file generation (role mode)
   - Multi-project example with anchors
7. Write to: `scratch/consolidation/design/yaml-schema.md`
8. Write execution log to: `plans/unification/reports/phase3-step4-execution.md`

**Expected Outcome**: YAML schema document with:
- Complete schema definition
- Validation rules
- Multiple complete examples
- Usage guidance

**Unexpected Result Handling**:
- If schema becomes too complex: Propose simplified version, escalate if trade-offs unclear
- If emojipack pattern conflicts with design.md: Document conflict, escalate for decision

**Error Conditions**:
- Core module or CLI design not found → Escalate (previous steps may have failed)
- Cannot determine appropriate schema structure → Document alternatives, escalate
- Validation requirements unclear → Propose basic validation, escalate for requirements

**Validation**:
- Design document exists at expected path
- Schema structure fully defined
- Validation rules specified
- At least 3 complete examples provided
- Examples cover different modes (agents, role)

**Success Criteria**:
- YAML schema design created at `scratch/consolidation/design/yaml-schema.md`
- Document includes:
  - Complete schema definition (all fields, types, structure)
  - Validation rules (required fields, types, path checks)
  - Examples (at least 3: simple, role mode, multi-project)
  - YAML anchor usage pattern (per design.md)
- Schema matches emojipack pattern from design.md
- Execution report documents schema decisions

**Report Path**: `plans/unification/reports/phase3-step-4.md`
**Artifact Path**: `scratch/consolidation/design/yaml-schema.md`

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
