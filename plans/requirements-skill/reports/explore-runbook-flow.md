# Runbook Skill Flow: Requirements and Context Collection

## Summary

The `/runbook` skill transforms design documents into execution-ready runbooks through a structured planning process. It does NOT do its own requirements gathering—instead, it receives requirements from either a `requirements.md` file or the `design.md` document produced by the `/design` skill. The skill includes a lightweight three-tier assessment that bypasses runbook creation for simple tasks (Tier 1) or lightweight delegation (Tier 2), reserving full runbook process (Tier 3) for complex multi-phase work.

## How Runbook Receives and Uses Requirements

### Entry Point: Design Document

**Usage:** `/runbook plans/<job-name>/design.md`

The skill takes a **design document** as its sole input. The design document is the authoritative source for requirements and implementation guidance.

**Design document produces:**
- Problem statement
- Functional requirements (FR-1, FR-2, etc.)
- Non-functional requirements (NFR-1, NFR-2, etc.)
- Out-of-scope items (with rationale)
- Architecture/approach decisions
- Key design decisions with rationale
- Implementation notes (affected files, testing strategy)
- Documentation Perimeter section (specifies what planner must read)

**Flowpath:** `/design` → `/runbook` → plan-reviewer → prepare-runbook.py → `/orchestrate`

### Requirements Handling in Phase 0.5

**Phase 0.5: Discover Codebase Structure** includes two requirement-related substeps:

**0. Read documentation perimeter and requirements (if present):**

Two inputs checked:

1. **Design document includes "Documentation Perimeter" section:**
   - Lists "Required reading" files planner must load
   - Notes Context7 references (may need additional queries)
   - Specifies domain-specific guidance files to load
   - Knowledge factored into step design

2. **Design document includes "Requirements" section:**
   - Functional requirements summarized
   - Non-functional requirements noted
   - Out-of-scope boundaries recorded
   - Requirements context carried into runbook Common Context

**Absolute requirement:** If `design.md` has "Requirements" section with FR/NFR mapping, the runbook **must** create a traceability mapping in Common Context linking each requirement to which implementation phase addresses it.

### Requirements in Common Context

Every assembled runbook includes a **Common Context** section extracted from the design:

```markdown
## Common Context

**Requirements (from design):**
- FR-1: [summary] — addressed by [element]

**Scope boundaries:** [in/out]

**Key Constraints:**
- [Constraint from design]

**Project Paths:**
- [Path]: [Description]
```

This ensures execution agents have:
- What requirements must be satisfied
- What's explicitly out of scope
- Architectural constraints from design
- File paths for implementation

## Does Runbook Do Its Own Requirements Gathering?

**No.** The `/runbook` skill assumes requirements are already finalized in the design document.

**Explicit constraint:** "Leaving design decisions for 'during execution'" is listed as a **Common Pitfall** to avoid. All decisions and requirements must be finalized **before** runbook creation.

**Tier assessment (Phase 0 in Tier 3) evaluates:**
- Design completeness: "Design complete (no open decisions)"
- If uncertain between tiers: "Ask user only if genuinely ambiguous"

**Anti-pattern:** Treating planning as a chance to discover requirements. The design phase is where requirements are discovered and validated. Runbook assumes they are locked.

**Escalation path if requirements change during planning:**
- Tier 2 escalation handling: "If genuinely ambiguous: Use `/opus-design-question` or ask user. Re-delegate with clarification if agent misread design."
- No auto-adjustment: design changes require going back to `/design` or explicit user direction

## Three-Tier Assessment: When Runbook is Bypassed

### Tier Assessment Structure

**Runs first in Phase 0 of Tier 3 process.** Explicitly assesses complexity before any other work.

**Assessment output format:**
```
**Tier Assessment:**
- Files affected: ~N
- Open decisions: none / [list]
- Components: N (sequential / parallel / mixed)
- Cycles/steps estimated: ~N (rough count from design)
- Model requirements: single / multiple
- Session span: single / multi

**Tier: [1/2/3] — [Direct Implementation / Lightweight Delegation / Full Runbook]**
**Rationale:** [1-2 sentences]
```

### Tier 1: Direct Implementation

**Criteria:**
- Design complete (no open decisions)
- All edits straightforward (<100 lines each)
- Total scope: <6 files
- Single session, single model
- No parallelization benefit

**When Tier 1 applies:** Runbook is **completely bypassed**.

**Sequence instead:**
1. Implement changes directly using Read/Write/Edit tools
2. Delegate to vet agent for review
3. Apply all fixes from vet review
4. Tail-call `/handoff --commit`

### Tier 2: Lightweight Delegation

**Criteria:**
- Design complete, scope moderate (6-15 files or 2-4 logical components)
- Work benefits from agent isolation but not full orchestration
- Components are sequential (no parallelization benefit)
- No model switching needed

**When Tier 2 applies:** Runbook **outline and full phase expansion bypassed**.

**For TDD work (~4-10 cycles):**
- Plan cycle descriptions (lightweight—no full runbook format)
- For each cycle: delegate via `Task(subagent_type="tdd-task", model="haiku", prompt="...")`
- Intermediate checkpoints: every 3-5 delegated cycles

**For general work (6-15 files):**
- Delegate work via `Task(subagent_type="quiet-task", model="haiku", prompt="...")`
- Single agent for cohesive work
- Include design context in prompt

**Common tail (same as Tier 1):**
- After delegation complete: delegate to vet agent
- Apply all fixes from vet review
- Tail-call `/handoff --commit`

**Key constraint:** "Design constraints are non-negotiable" — when design specifies explicit classifications (tables, rules, decision lists), include them LITERALLY in delegation prompt.

**Agent escalation handling:**
1. Verify against design source (re-read design document section)
2. If design provides explicit rules: resolve using those rules, do not accept the escalation
3. If genuinely ambiguous: use `/opus-design-question` or ask user

### Tier 3: Full Runbook

**Criteria:**
- Multiple independent steps (parallelizable)
- Steps need different models
- Long-running / multi-session execution
- Complex error recovery
- >15 files or complex coordination
- >10 TDD cycles with cross-component dependencies

**When Tier 3 applies:** Full planning process executes (Phases 0.5 through 4).

**Preference rule:** "When uncertain between tiers, prefer the lower tier (less overhead). Ask user only if genuinely ambiguous."

## Design.md Interaction Pattern

### What Design Provides to Runbook

**Design document structure delivered to runbook:**

1. **Architecture/Approach** — High-level strategy (runbook decomposes into executable steps)
2. **Key Design Decisions** — Rationale for architectural choices (embedded in runbook for execution agents)
3. **Implementation Notes** — File locations, module boundaries (referenced by runbook steps)
4. **Classification Tables** — BINDING CONSTRAINTS passed literally to execution agents
5. **Requirements Traceability** — FR/NFR mapped to design sections (reflected in runbook phases)
6. **Documentation Perimeter** — What planner must read (executed in Phase 0.5)
7. **Skill Dependencies** — For plugin work (agent, skill, hook development) — loaded by planner
8. **Out-of-Scope Boundaries** — What NOT to implement (guards against scope creep)

### Design Constraints Are Non-Negotiable

**Explicit rule:** "Classification tables are binding constraints."

When design specifies:
```markdown
### Title is semantic
- Item X: [type/behavior]
- Item Y: [type/behavior]
```

This is NOT a suggestion—it's a specification the planner must enforce during runbook creation.

**Handling design ambiguity:** If during runbook generation the planner encounters uncertainty about design intent:
1. Re-read the design document section
2. If rules provided: apply them
3. If genuinely ambiguous: escalate to `/opus-design-question` (do NOT skip design resolution)
4. Do NOT proceed without clarity

### Phase 0.5 Discovery Gating

**Critical requirement:** Before writing any runbook content:

**0. Read documentation perimeter and requirements (if present):**
- If design includes "Documentation Perimeter" section: read ALL files listed
- If design includes "Requirements" section: read and summarize
- Note Context7 references and factor knowledge into step design
- Note Skill dependencies and load before Phase 1 expansion

This gating ensures runbook generation has full context before producing outline or phases.

## How Phase Type Tagging Works

### Per-Phase Type Declaration

Each phase in outline is tagged: `type: tdd` or `type: general` (default: general)

**Format in outline:**
```markdown
### Phase 1: Core behavior (type: tdd)
- Cycle 1.1: Load configuration
- Cycle 1.2: Parse entries

### Phase 2: Skill definition updates (type: general)
- Step 2.1: Update SKILL.md frontmatter
- Step 2.2: Add new section
```

**Type determines:**
- **Expansion format:** TDD phases → RED/GREEN cycles. General phases → task steps
- **Review criteria:** TDD discipline for TDD phases, step quality for general phases
- **Orchestration:** prepare-runbook.py auto-detects via headers (`## Cycle X.Y:` vs `## Step N.M:`)

**Type does NOT affect:** Tier assessment, outline generation, consolidation gates, assembly, orchestration, checkpoints

### Binding Role of Design in Type Selection

Design document should specify which phases are behavioral (TDD) vs infrastructure (general):

**From Design Skill SKILL.md:**
> "Design should note which phases are behavioral (TDD) vs infrastructure (general) to guide per-phase type tagging during planning."

This is **guidance for designer**, not constraint on runbook—but runbook respects this guidance when present.

## Integration Points

### Runbook as Bridge Between Design and Orchestration

**Workflow:**
```
/design
  ↓ (outputs design.md + requirements.md if needed)
/runbook
  ↓ (reads design, creates runbook.md + outline + phase files)
plan-reviewer (fix-all mode)
  ↓ (reviews each phase, fixes issues)
prepare-runbook.py
  ↓ (validates, assembles, creates plan-specific agent)
/orchestrate
  ↓ (executes steps with weak orchestrator)
completion
```

### Requirements Validation During Phase 1

**Mandatory Conformance Validation:**

When design includes external reference (shell prototype, API spec) in `Reference:` field:
- Runbook MUST include validation items
- Verification items must verify implementation conforms to the reference
- Use precise descriptions with exact expected strings from reference

## Key Findings

### Requirements Flow Architecture

1. **User provides:** Job description or problem statement
2. **Design skill:** Discovers requirements, creates design.md with FR/NFR/scope
3. **Runbook skill:** Receives design.md, extracts requirements into Common Context
4. **Planner (Phase 0.5):** Reads design's "Requirements" section, embeds in outline
5. **Execution agents:** Receive requirements in Common Context of each step

### Requirements Assumed Finalized

**Critical gate:** Runbook assumes design is **complete**. No open decisions, no requirement discovery during planning.

If requirements change during runbook generation:
- Tier 1/2: stop and ask user
- Tier 3: callback mechanism stops and reports to user

### Tier Assessment as Scope Governor

**Prevents runbook overhead for small work:**
- Tier 1 (<6 files, straightforward): skip runbook entirely
- Tier 2 (6-15 files, moderate): skip outline + phase expansion, use delegated tasks instead
- Tier 3 (>15 files, complex): full runbook with outline, phases, reviews

**Assessment runs FIRST** before any planning work, as Phase 0 checkpoint.

### Design Constraints Passed Verbatim

When design includes classification tables or decision matrices, runbook does NOT reinterpret them—agents receive them as-is in step contexts or Common Context for literal application.

This pattern ensures:
- Design intent preserved in execution
- No agent "judgment" about design rules
- Binding constraints remain binding through the pipeline
