# Domain-Specific Validation — Design Outline

## Problem

The vet workflow routes artifacts to review agents by type (design → design-vet-agent, TDD runbooks → tdd-plan-reviewer, everything else → vet-fix-agent). There's no mechanism for domain-specific routing — a plugin skill definition gets the same generic vet-fix-agent review as a Python script, despite plugin-dev having specialized review criteria (skill structure, hook patterns, agent frontmatter).

**Current routing is artifact-type-based. It should also be domain-aware.**

## Approach: Planning-Time Domain Detection, Skill-Directed Vet

The architecture already has the pieces (rules files, skills, vet-fix-agent). What's missing:

1. **Domain-aware vet instructions in runbooks** — Planner detects domain, writes vet steps that reference domain skill files
2. **Domain validation skills** — Structured review criteria files that vet-fix-agent reads directly
3. **Plugin-dev as first implementation** — Concrete validation criteria for plugin components
4. **Optional project-level validation** — Projects can extend standard domain validation

## Key Decisions

**Encode domain concerns at planning time, not orchestration time.** The planner (opus/sonnet) detects the domain and writes runbook vet steps that include domain skill references. The weak orchestrator (haiku) executes mechanically — it doesn't need domain intelligence.

**Vet-fix-agent reads domain skill files directly.** No reprocessing by orchestrator (fidelity loss), no hub skill (unnecessary indirection), no agent proliferation (one agent per domain). The runbook step says: "vet-fix-agent: review + alignment + read and apply criteria from `path/to/domain-validation-skill.md`." Vet-fix-agent reads the file and applies criteria alongside generic quality + alignment checks.

**Autofix is the key design pattern.** Domain specialist (vet-fix-agent with domain context) applies fixes directly. If fixes were sent back to the original writer, that agent's context may have drifted and refuse to apply them. The reviewer is authoritative once delegated.

**Single agent, structured criteria.** Rather than splitting domain knowledge + alignment + generic quality across multiple agents (expensive, 2 invocations per vet), vet-fix-agent handles all three in one pass. Cognitive overload is managed by the domain skill file providing structured criteria (explicit checklists, good/bad examples) — not unbounded reasoning.

**Sub-agents don't get rules file injection.** Rules files fire in the main session only. Domain context must be carried explicitly: planner writes it into the runbook, orchestrator passes it through the task prompt, vet-fix-agent reads the skill file. No reliance on runtime injection.

**Rules files serve the planner, not the orchestrator.** Rules files remain useful for interactive sessions and for planners detecting domain context. They're a discovery mechanism for intelligent agents (planner, interactive user), not for weak orchestrators.

**Opt-in via rules files + path matching.** `.claude/rules/` path matching provides natural scoping. A project without `.claude/plugins/` files never triggers plugin-dev rules. Project-specific validation adds project-local rules files.

## Scope

**In scope:**
- Domain validation skill files (structured review criteria for vet-fix-agent)
- Planning-time domain detection pattern (planner writes domain-aware vet steps)
- Plugin-dev validation as first implementation
- Domain validation pattern documentation (template for new domains)
- Project-level validation opt-in mechanism

**Out of scope:**
- Central validation registry/framework
- New specialist review agents (no agent proliferation)
- Hub skill or routing skill (unnecessary indirection)
- Changes to vet-fix-agent itself (enriched via skill files, not code changes)
- Validation cost tracking or budgeting
- Cross-domain validation

## Implementation Details

### Domain Detection and Encoding (FR-1, FR-4)

**At planning time:** Planner detects domain via rules file context (fired in planner's session) or by recognizing artifact types in the design. Planner writes runbook vet steps with domain skill file reference.

**Runbook step example:**
```
Checkpoint: Vet skill definition
  Delegate to vet-fix-agent:
  - Standard: quality + alignment
  - Domain: read and apply criteria from `agent-core/skills/plugin-dev-validation/SKILL.md`
  - Artifact: `.claude/skills/my-skill/SKILL.md`
```

**At orchestration time:** Haiku orchestrator copies the step instructions into the Task prompt verbatim. No domain reasoning required.

**At execution time:** Vet-fix-agent (sonnet) reads the domain skill file, applies generic quality + alignment + domain criteria in one pass.

### Domain Validation Skills (FR-5)

Domain validation knowledge lives in skill files that vet-fix-agent reads directly:

**Location:** `agent-core/skills/<domain>-validation/SKILL.md` (or equivalent path)

**Content:**
- Review criteria (critical/major/minor) with explicit checklists
- Good/bad pattern examples
- Fix procedures (what's fixable vs UNFIXABLE)
- Domain-specific alignment criteria (what "correct" looks like)

**Not separate agents.** The skill file is consumed by vet-fix-agent, not by a dedicated domain agent.

### Plugin-Dev Validation (FR-3)

First implementation: validation criteria for plugin-dev component types.

**Artifact types to cover:**
- Skills (structure, progressive disclosure, triggering conditions)
- Agents (frontmatter, system prompt design, tool access)
- Hooks (event types, validation patterns, security)
- Commands (frontmatter, arguments, execution)
- Plugin structure (manifest, directory layout, discovery)

**Source material:** Existing plugin-dev skills (agent-development, skill-development, hook-development, command-development, plugin-structure) contain the domain knowledge. The validation skill extracts review criteria from these.

### Project Opt-In (FR-2, FR-6)

**Implicit opt-in:** Path matching in rules files. Project has `.claude/plugins/` → plugin-dev rules fire → planner sees domain context → writes domain-aware vet steps.

**Explicit opt-in:** Projects can add project-local rules files for additional validation beyond standard domain checks.

**Opt-out:** Remove or rename rules files (`.claude/rules/plugin-dev-validation.md.disabled`).

### Integration with Vet Workflow (FR-7)

**No changes to vet-requirement fragment or vet-fix-agent code.** Domain validation is additive:

- Vet-fix-agent already handles: quality, security, testing, alignment
- Domain skill file adds: domain-specific criteria checklist
- Vet-fix-agent reads and applies both sets in one pass

**Flow:** Create artifact → vet-fix-agent (quality + alignment + domain criteria from skill file) → escalate UNFIXABLE

### Extensibility Model (FR-8)

Template for adding new validation domains:

**Step 1:** Create domain validation skill (`agent-core/skills/<domain>-validation/SKILL.md`)
- Extract review criteria from existing domain skills/knowledge
- Structure as explicit checklists with good/bad examples
- Define fixable vs UNFIXABLE boundaries

**Step 2:** Create rules file (`.claude/rules/<domain>-validation.md`)
- Path patterns matching domain artifacts
- Reference to validation skill file (for planner discovery)

**Step 3:** Update planning skills awareness
- Planner detects domain via rules file context
- Writes runbook vet steps referencing the domain validation skill

**Pattern:** Domain = Validation skill file + Rules file + Planning awareness

## Constraints Discovered

- Sub-agents don't receive rules file injection (must use explicit context)
- Weak orchestrator (haiku) can't do domain reasoning (encode at planning time)
- Dunning-Kruger: agents can't detect their own domain knowledge gaps (plan-time detection, not runtime)
- Autofix required: writer context may drift, reviewer must apply fixes directly
- One agent per concern is expensive: structured skill files manage cognitive load in single pass

## Traceability

| Requirement | Outline Section | Coverage |
|-------------|-----------------|----------|
| FR-1: Domain-specific validation | Approach, Domain Detection | Complete — planning-time detection + skill-directed vet |
| FR-2: Optional project validation | Project Opt-In | Complete — implicit path matching + explicit rules |
| FR-3: Plugin-dev first use case | Plugin-Dev Validation | Complete — first implementation with 5 artifact types |
| FR-4: Agent discovery | Domain Detection | Complete — planner detects via rules, encodes in runbook |
| FR-5: Validation rules placement | Domain Validation Skills | Complete — skill files read by vet-fix-agent |
| FR-6: Project opt-in | Project Opt-In | Complete — path matching + opt-out mechanism |
| FR-7: Vet integration | Integration with Vet Workflow | Complete — additive, no vet-fix-agent changes |
| FR-8: Extensibility model | Extensibility Model | Complete — 3-step template |

## Open Questions

None — all design questions resolved through iterative discussion.
