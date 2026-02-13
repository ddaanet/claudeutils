# Requirements Patterns Exploration

## Summary

Requirements.md files follow a structured format with functional/non-functional requirements (FR/NFR), constraints, and open questions. Four active plans use requirements files (handoff-validation, orchestrate-evolution, requirements-skill, tweakcc), each documenting specific skills or features. Requirements are referenced throughout the workflow via design documents (requirements checkpoint in A.0) and plan outlines (requirements mapping tables), creating an explicit traceability chain that persists into execution artifacts.

## Key Findings

### 1. Requirements File Locations and Structure

**Active requirements.md files:**
- `/Users/david/code/claudeutils-wt/requirements-skill/plans/handoff-validation/requirements.md` — 127 lines
- `/Users/david/code/claudeutils-wt/requirements-skill/plans/orchestrate-evolution/requirements.md` — 10 lines (skeletal)
- `/Users/david/code/claudeutils-wt/requirements-skill/plans/requirements-skill/requirements.md` — 65 lines
- `/Users/david/code/claudeutils-wt/requirements-skill/plans/tweakcc/requirements.md` — 76 lines

**Canonical structure (from handoff-validation and tweakcc):**

```markdown
# [Skill/Feature Name]

## Requirements

### Functional Requirements
**FR-1: [requirement description]**
[Details, rationale, acceptance criteria]

**FR-2: [requirement description]**
...

### Non-Functional Requirements
**NFR-1: [requirement description]**
...

### Constraints
**C-1: [constraint]**
...

---

## [Additional sections: Design Outline, Analysis, Recommendation, Research, Open Questions]
```

**Format patterns:**
- Numbered identifiers (FR-1, NFR-1, C-1) for traceability
- Narrative descriptions with context (not bare statements)
- Tables for comparing options or validation scopes
- Scope IN/OUT boundaries explicitly stated
- Token cost estimates included (tweet-cost awareness)

### 2. Requirements Reference in Workflow

**Workflow Integration Points:**

**A.0 Requirements Checkpoint (Design Skill, line 43-67):**
```
If `requirements.md` exists in job directory:
  - Read and summarize functional/non-functional requirements
  - Note scope boundaries (in/out of scope)
  - Carry requirements context into outline and design
  - Scan for skill dependencies → load plugins if mentioned
```

**Why this matters:** Early discovery prevents design from inadvertently creating agents/skills without proper guidance.

**Design Document Requirements Section (line 202-223):**

When requirements.md exists, design includes explicit traceability mapping:

```markdown
## Requirements

**Source:** `plans/<job-name>/requirements.md`

**Functional:**
- FR-1: [requirement] — addressed by [design decision/section]
- FR-2: [requirement] — addressed by [design decision/section]

**Out of scope:**
- [item] — rationale
```

Each requirement maps to a design element, creating bidirectional traceability.

**Plan Outline Requirements Mapping:**

Outline-review-agent checks "Requirements Traceability Assessment" — all requirements must map to phases with explicit cycle references. Evidence from plan reports:

```
plans/worktree-update/reports/outline-review-2.md:
"Coverage Assessment: All requirements covered with explicit cycle references"

plans/plugin-migration/reports/runbook-outline-review.md:
"Requirements Mapping table provides complete FR → Phase → Cycles mapping"
```

### 3. Requirements Format Variations by Plan Type

**Functional/NFR Plans (handoff-validation, tweakcc):**
- Structured requirements with acceptance criteria
- Design outline section ("Design Outline from discussion")
- Analysis section with hypothesis and fallback options
- Token cost estimates for cost-benefit analysis
- Open questions section for design decisions

**Skeletal/Research Plans (orchestrate-evolution, requirements-skill):**
- Minimal FR/NFR (3 open questions instead of detailed requirements)
- Focus on research gaps and recommendation
- Intent to defer full specification until research completes
- Example: orchestrate-evolution (10 lines) vs handoff-validation (127 lines)

**No requirements.md plans:**
- Tasks with clear requirements from conversation extract them during design
- Outline-review identifies "requirements extracted from task prompt"
- Example: worktree-update (task prompt had 9 requirements documented in outline review)

### 4. Skill Dependencies Embedded in Requirements

**Scanning Pattern (Design Skill A.0, line 55-63):**

Requirements files signal which plugins/skills are needed:

```
"sub-agent" → load plugin-dev:agent-development
"skill" → load plugin-dev:skill-development
"hook" → load plugin-dev:hook-development
"plugin" → load plugin-dev:plugin-structure, plugin-dev:mcp-integration
```

**Example from tweakcc/requirements.md:**
- FR-1, FR-2 establish npm project structure and tweakcc patches
- Implicit requirement for understanding npm postinstall hooks
- Design loading `plugin-dev:hook-development` ensures hook configuration guidance is available

**Impact:** Prevents designers from working in a vacuum; required domain context loads before outline generation.

### 5. Requirements Validation and Evolution

**Timeline Evolution (from reports):**

1. **Skeletal requirements** → Open questions guide design research
2. **Design creates inline requirements** → Supersedes skeletal file if more specific
3. **Design-vet-agent checks traceability** → Each design element maps to requirement
4. **Outline-review-agent validates coverage** → All requirements have phase/cycle assignments
5. **Runbook-outline-review validates traceability** → Requirements mapping explicit in outline

**Evidence from orchestrate-evolution (design-review.md):**
```
Problem: Design has inline requirements that supersede skeletal requirements.md
Fix Applied: Added note that inline requirements supersede the skeletal requirements.md
Result: "Requirements Source: Inline (design lines 9-41), superseding plans/orchestrate-evolution/requirements.md"
```

**Scope mutability rule (workflow-advanced.md line 51-63):**
```
"Requirements MUST NOT be updated if task execution made them outdated;
updating requires explicit user confirmation."
```

This is a deliberate constraint — requirements are the specification at planning time, not adaptive to discovered implementation constraints.

### 6. Requirements in Non-Functional Context

**Token Economy Awareness:**

Token cost estimates appear in requirements (tweakcc line 44, handoff-validation line 122-126):
```
**Token cost:**
- Inline: ~500 tokens added to /handoff
- Agent: ~2000-4000 tokens for Sonnet delegation
```

**Requirements as Design Inputs:**

handoff-validation explicitly names requirements sections that design consumes:
```
FR-6: Validation must compare handoff against requirements captured since conversation start
```

Implies requirements document serves as a scoreboard for downstream validation (vet-handoff agent references requirements to check alignment).

### 7. Cross-Artifact Requirements References

**From Grep results (16 files match "requirements"):**

Requirements are referenced in:
- Design skill (A.0 checkpoint)
- Plan outline reviews (requirements mapping sections)
- Vet reports (traceability assessment)
- Execution reports (success criteria validation)

**Pattern: Requirements → Design → Outline → Execution:**

Each stage carries forward and validates against requirements:
- Design: "FR-X addressed by Section Y"
- Outline: "FR-X implemented by Phase N, Cycles M.P through M.Q"
- Execution: "All FR tests passed, NFR token budget met"

### 8. Alternative to Formal Requirements

**Plans without requirements.md:**
- Task prompt provides implicit requirements
- Designer documents discovery in design.md inline
- Outline-review notes "No formal requirements.md, extracted from task prompt"
- Pattern: `plans/worktree-update/reports/outline-review-2.md` shows 9 requirements extracted from task

**Recommendation from requirements-skill requirements.md (line 63-64):**
```
"Defer implementation until design/plan skill requirements sections are working.
Evaluate whether separate /requirements skill provides value beyond in-skill requirements capture."
```

This suggests formal requirements.md files are optional for simple tasks but valuable for complex ones that span multiple phases or require external coordination.

### 9. Requirements Metadata Patterns

**Constraint classification:**

Requirements use constraint shorthand:
- **C-1** for architectural constraints (e.g., "Requires continuation passing")
- **FR** for functional (behavior, output, acceptance)
- **NFR** for non-functional (performance, cost, model tier)

Example from handoff-validation:
```
C-1: Requires continuation passing
C-2: Tally persistence (tally stored in session.md or dedicated file)
```

These constraints appear in design decisions and runbook instructions.

### 10. Design Binding from Requirements

**Design Skill output expectations (line 184-186):**
```
"Classification tables are binding: they are LITERAL constraints for downstream
planners/agents, not interpretable guidelines."
```

This principle flows from requirements → design → runbook:

When requirements establish a constraint (e.g., "must use sonnet for validation"), designers embed it in classification tables, and planners pass it through verbatim to orchestration.

## Patterns

### Pattern 1: Early Requirement Discovery

**When:** Design Phase A.0
**Action:** Check for requirements.md, read it, scan for skill dependencies
**Benefit:** Prevents working without domain context, loads plugins early

### Pattern 2: Explicit Traceability Chain

**When:** Design → Outline → Execution
**Structure:** Each stage maps requirements to artifacts (design sections → outline phases → execution cycles)
**Benefit:** Requirements stay visible throughout execution, enabling validation at each stage

### Pattern 3: Scope Boundaries in Requirements

**Format:** Functional (FR), Non-Functional (NFR), Constraints (C), Out of Scope
**Purpose:** Prevent scope creep during execution
**Evidence:** Every requirements file separates in/out of scope explicitly

### Pattern 4: Skeletal vs Complete Requirements

**Skeletal:** Research-phase plans use 3-10 open questions to guide exploration
**Complete:** Implementation-phase plans detail all FR/NFR with acceptance criteria
**Transition:** Designer synthesizes discoveries into complete requirements during design

### Pattern 5: Token Awareness in Requirements

**Inclusion:** Cost estimates for delegation options
**Purpose:** Allow users to make informed decisions (inline vs agent validation)
**Example:** handoff-validation estimates ~500t inline vs ~2000-4000t agent

### Pattern 6: Requirements Checkpoint in Design Workflow

**Placement:** Phase A.0 (first thing, before A.1 documentation checkpoint)
**Triggers:** Skill loading if requirements mention agents/skills/hooks
**Scope:** Inform outline generation and design decisions

### Pattern 7: Supersession Rule

**When:** Design creates inline requirements that contradict requirements.md
**Action:** Design-vet-agent detects and adds clarifying note
**Effect:** Inline requirements take precedence, with explicit rationale

### Pattern 8: No Mid-Execution Updates

**Rule:** Requirements immutable during execution (workflow-advanced.md)
**Exception:** Requires explicit user confirmation if execution discovers they're outdated
**Rationale:** Preserves planning intent; execution must work within specified constraints

## Gaps

### Gap 1: No Formal Requirements Generation Skill

Requirements-skill plan exists but is not implemented. Current pattern:
- Complex tasks: Designer creates requirements.md during design (optional)
- Simple tasks: Requirements extracted from task prompt inline in design.md
- No dedicated `/requirements` skill to guide elicitation upfront

**Impact:** Requirements discovery is ad-hoc; early planning relies on user clarity.

### Gap 2: No Requirements Validation Against Design

While design validates traceability, no automated check that:
- All requirements are addressed by design (false negatives possible)
- Design doesn't exceed requirements scope (scope creep)
- NFR constraints are feasible given approach

**Current:** Manual review by design-vet-agent; no structured validation rule.

### Gap 3: Incomplete Guidance on Requirements Scope

Design skill A.0 says "Read and summarize functional/non-functional requirements" but provides no structured checklist or template for what complete requirements should contain.

**Current:** Templates exist for design.md, but not requirements.md.

### Gap 4: No Requirements-to-Code Traceability

Requirements map to design sections, design maps to outline phases, but no mechanism to trace from execution tests back to original requirement.

**Current:** Manual correlation required; no artifact linking test code to FR-X.

### Gap 5: Skeletal Requirements Lack Specificity

orchestrate-evolution requirements.md has 3 open questions and says "Blocked on continuation-passing." No concrete FR/NFR to guide subsequent phases.

**Risk:** Designer has to invent requirements during design, potentially diverging from user intent.

## Unresolved Questions

1. **When should requirements.md exist?**
   - Always (formal discipline)?
   - For complex tasks (>15 files, >20 cycles)?
   - Only when external stakeholders need them?

2. **Should requirements be updated if design contradicts them?**
   - Current rule: No, unless user explicitly approves
   - Exception: Can design-vet-agent suggest updates as non-blocking recommendations?

3. **How to handle requirements discovered during design?**
   - Inline in design.md (current pattern)
   - Extracted to separate requirements.md after design completes?
   - Both (design.md carries inline, prepared for extraction)?

4. **Should skeleton requirements force specific structure?**
   - Current: Each plan chooses (FR/NFR vs open questions vs minimal outline)
   - Alternative: Standardize on FR/NFR even for skeletal (clearer graduation path)

5. **How deep should A.0 requirement scans go?**
   - Current: Check for agent/skill/hook keywords
   - Future: Scan requirements for design patterns (event-driven, state machine, etc.)?

## Recommendations for requirements-skill Design

Based on patterns observed:

1. **Positioning:** `/requirements` skill sits between task clarification and `/design`
   - User → `/requirements` (conversational requirements elicitation) → `/design` (architecture)
   - Output: Structured requirements.md with FR/NFR/Constraints/Out-of-Scope

2. **Scope:** Minimal exploration (unlike `/design` which does full research)
   - Collect user intent
   - Ask clarifying questions about scope boundaries
   - Document constraints discovered from conversation
   - DO NOT duplicate design's exploration phase

3. **Output:** requirements.md ready for design.md A.0 checkpoint
   - FR/NFR/Constraints enumerated
   - Out-of-scope section explicit
   - Skill dependencies identified (if any)
   - Open questions documented for design research

4. **Workflow:** Optional for simple tasks (auto-skip via tier assessment), recommended for complex tasks
   - Tier 1: No /requirements needed (requirements trivial from task)
   - Tier 2+: /requirements valuable (explicit scope prevents planning surprises)

5. **Integration:** Design skill A.0 already consumes it (no workflow changes needed)
   - Just needs implementation and user guidance on when to invoke
