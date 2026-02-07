# Domain-Specific Validation — Design

## Problem

Vet-fix-agent reviews all non-design, non-TDD artifacts with generic quality + alignment criteria. A plugin skill definition gets the same review as a Python script — no domain-specific checks for skill structure, progressive disclosure, triggering conditions, frontmatter correctness, etc.

Domain knowledge exists in plugin-dev skills (agent-development, skill-development, hook-development, command-development, plugin-structure) but isn't surfaced to vet-fix-agent during review.

## Requirements

**Source:** `agents/session.md` (design questions) + iterative discussion

**Functional:**
- FR-1: Domain-specific validation — Validation criteria for specific work types → addressed by domain validation skill files
- FR-2: Optional project-specific validation — Projects opt in/out → addressed by rules files + path matching
- FR-3: Plugin-dev as first use case → addressed by plugin-dev-validation skill
- FR-4: Agent discovery of applicable validations → addressed by planning-time detection
- FR-5: Validation rules placement → addressed by skill files read by vet-fix-agent
- FR-6: Project opt-in mechanism → addressed by implicit path matching + explicit rules
- FR-7: Integration with vet/review workflows → addressed by additive criteria, no vet-fix-agent changes
- FR-8: Extensibility model for new domains → addressed by 3-step template

**Non-functional:**
- NFR-1: Weak orchestrator compatible — Haiku orchestrator executes mechanically, no domain reasoning
- NFR-2: No agent proliferation — One vet-fix-agent, enriched via skill files
- NFR-3: No fidelity loss — Vet-fix-agent reads skill files directly, no orchestrator reprocessing
- NFR-4: Autofix — Domain reviewer applies fixes directly (writer context may drift)

**Out of scope:**
- Central validation registry/framework
- New specialist review agents per domain
- Hub/routing skills
- Changes to vet-fix-agent agent definition
- Cross-domain validation
- Validation cost tracking

## Architecture

### Core Concept: Skill-Directed Vet

Domain validation knowledge is encoded in **domain validation skill files** — structured review criteria documents that vet-fix-agent reads during review. The skill file is referenced in runbook vet steps, written by the planner at planning time.

```
Planning time (sonnet/opus):
  Planner detects domain → writes runbook vet step with skill file reference

Orchestration time (haiku):
  Copies step instructions into Task prompt verbatim

Execution time (sonnet vet-fix-agent):
  Reads domain skill file → applies generic + alignment + domain criteria → fixes all → reports
```

### Why This Architecture

**Constraint: Sub-agents don't receive rules file injection.** Rules files fire in the main session only. Vet-fix-agent spawned via Task tool doesn't see them. Domain context must be explicitly provided.

**Constraint: Weak orchestrator can't reason about domains.** Haiku orchestrator executes runbook steps mechanically. Domain detection requires intelligence — it belongs at planning time (sonnet/opus).

**Constraint: Dunning-Kruger.** A generic agent can't reliably detect its own domain knowledge gaps. Runtime escalation to specialists fails because the agent doesn't know what it doesn't know. Planning-time detection by an intelligent planner avoids this.

**Constraint: Cost.** One agent per concern (quality agent + alignment agent + domain agent) means 2-3 invocations per vet. Structured skill files provide explicit checklists that manage cognitive load in a single pass.

**Constraint: Autofix trust.** Domain fixes must be applied directly by the reviewer. Sending fixes back to the original writer risks refusal due to context drift (observed in practice).

### Information Flow

```
                    PLANNING TIME                    EXECUTION TIME
                    ─────────────                    ──────────────
Rules files ─┐
             ├→ Planner ─→ Runbook step ─→ Haiku ─→ vet-fix-agent
Design doc ──┘              (with skill            (reads skill file,
                             file ref)              applies all criteria,
                                                    fixes directly)
```

**Rules files serve the planner.** They provide domain context to the intelligent agent (planner) that writes the runbook. The weak orchestrator and sub-agents never see rules files — they work from explicit instructions.

## Key Design Decisions

### D-1: Domain Validation Skill File Format

Domain validation skills follow the existing skill file pattern but are structured specifically for vet-fix-agent consumption.

**Location:** `agent-core/skills/plugin-dev-validation/SKILL.md`

**Structure:**

```markdown
# Plugin Development Validation

## Scope
Artifact types this skill covers, with path patterns.

## Review Criteria by Artifact Type

### Skills
**Critical:**
- [criterion with rationale]

**Major:**
- [criterion with rationale]

**Minor:**
- [criterion with rationale]

**Good/Bad Examples:**
- ✅ [correct pattern]
- ❌ [incorrect pattern with explanation]

### Agents
[same structure]

### Hooks
[same structure]

...

## Alignment Criteria
What "correct" means for each artifact type in this domain.
How to verify the artifact serves its intended purpose.

## Fix Procedures
What's fixable (with instructions) vs UNFIXABLE (escalate).
```

**Rationale:** Explicit checklists with examples provide structured criteria that vet-fix-agent can apply mechanically. This manages cognitive load without requiring separate agents.

**Not user-invocable.** This skill is consumed by vet-fix-agent via file read, not invoked interactively. It may have frontmatter `user-invocable: false` if that field exists, otherwise the filename/location makes its role clear.

### D-2: Planning-Time Domain Detection

**How the planner detects domain:**

1. **Rules file context** — If planner's session has rules files matching artifact paths, the rules file content is already in context. Rules file references the domain validation skill.
2. **Design document** — Design may explicitly mention plugin components (hooks, agents, skills). The design skill's A.0 already scans for skill dependencies.
3. **Artifact path patterns** — Planner recognizes `.claude/plugins/`, `.claude/skills/`, `.claude/agents/`, `.claude/hooks/` as plugin-dev domain.

**How the planner encodes it in the runbook:**

The vet checkpoint step includes an additional instruction:

```markdown
### Step N: Checkpoint — Vet [artifact description]

Delegate to vet-fix-agent:
- Review all changes for quality, security, and alignment
- **Domain validation:** Read and apply criteria from
  `agent-core/skills/plugin-dev-validation/SKILL.md`
  for artifact type: [skills|agents|hooks|commands|plugin-structure]
- Write report to `plans/<job>/reports/vet-step-N.md`
```

**Planner awareness update:** Plan skills (`/plan-adhoc`, `/plan-tdd`) should document that when writing vet checkpoint steps, the planner should check if domain validation skills exist for the artifact types being reviewed.

### D-3: Rules File for Planner Discovery

**File:** `.claude/rules/plugin-dev-validation.md`

```yaml
---
paths:
  - ".claude/plugins/**/*"
  - ".claude/skills/**/*"
  - ".claude/agents/**/*"
  - ".claude/hooks/**/*"
  - "agent-core/skills/**/*"
  - "agent-core/agents/**/*"
---

# Plugin Development Validation

When planning work that creates or modifies plugin components (skills, agents, hooks, commands, plugin structure), include domain-specific validation in vet checkpoint steps.

**Domain validation skill:** `agent-core/skills/plugin-dev-validation/SKILL.md`

Include in vet-fix-agent delegation:
- Read and apply criteria from the domain validation skill
- Specify artifact type being reviewed (skills, agents, hooks, commands, plugin-structure)
```

**Purpose:** Surfaces domain context to the planner. The planner sees this when working with matching file paths and includes domain validation references in runbook vet steps.

**No orchestrator logic.** The rules file doesn't instruct the orchestrator — it informs the planner during runbook generation.

### D-4: Plugin-Dev Validation Criteria

Criteria extracted from existing plugin-dev skills. The validation skill consolidates review-relevant criteria from:

| Source Skill | Artifact Type | Key Validation Points |
|---|---|---|
| `plugin-dev:skill-development` | Skills | Progressive disclosure, triggering conditions, frontmatter fields, content structure |
| `plugin-dev:agent-development` | Agents | Frontmatter (name 3-50 chars, description with examples, model, color, tools), system prompt design, triggering examples |
| `plugin-dev:hook-development` | Hooks | Event types, matcher patterns, security (exact match not startswith), output format |
| `plugin-dev:command-development` | Commands | YAML frontmatter, argument structure, execution patterns |
| `plugin-dev:plugin-structure` | Plugin manifest | Directory layout, plugin.json structure, auto-discovery |

**The validation skill is NOT a copy of these skills.** It extracts review-relevant criteria (what to check, good/bad examples, severity levels) into a format optimized for vet-fix-agent consumption.

### D-5: Existing Plugin-Dev Review Agents

Plugin-dev already has review agents (skill-reviewer, plugin-validator). These continue to exist for **interactive use** — user directly invokes them for focused review. They're not part of the standard vet workflow.

**Relationship:**
- **Standard vet workflow:** vet-fix-agent + domain validation skill file (one agent, one pass)
- **Interactive review:** Existing plugin-dev review agents (user-initiated, focused domain review)

No changes to existing plugin-dev review agents.

### D-6: Project-Level Opt-In/Out

**Implicit opt-in:** Rules files with path patterns. If project has files matching `.claude/plugins/**/*` etc., the rules file activates for the planner.

**Opt-out:** Rename rules file (`.claude/rules/plugin-dev-validation.md` → `.claude/rules/plugin-dev-validation.md.disabled`). Rules files with non-`.md` extension aren't loaded.

**Project-specific extensions:** Projects can add their own rules files with additional path patterns and references to project-specific validation skills.

**No feature flags.** Path matching provides natural scoping. Projects without matching artifacts never trigger domain validation.

### D-7: Extensibility Template

Adding a new validation domain:

**Step 1: Create domain validation skill**
- Location: `agent-core/skills/<domain>-validation/SKILL.md`
- Content: Review criteria by artifact type, severity levels, good/bad examples, fix procedures, alignment criteria
- Consumed by: vet-fix-agent (reads file directly)

**Step 2: Create rules file**
- Location: `.claude/rules/<domain>-validation.md`
- Content: Path patterns + reference to validation skill
- Consumed by: Planner (domain detection at planning time)

**Step 3: Ensure planner awareness**
- Plan skills should document: "check for domain validation skills when writing vet steps"
- The rules file content in planner's context provides the domain reference

**That's it.** No new agents, no code changes, no framework. Domain = validation skill file + rules file.

## Implementation Notes

### Affected Files

**New files:**
- `agent-core/skills/plugin-dev-validation/SKILL.md` — Domain validation criteria for plugin components
- `.claude/rules/plugin-dev-validation.md` — Rules file for planner discovery

**Modified files:**
- Plan skills (`agent-core/skills/plan-adhoc/`, `agent-core/skills/plan-tdd/`) — Add awareness that domain validation skills exist and should be referenced in vet checkpoint steps
- `agents/decisions/workflow-core.md` or `agents/decisions/workflow-advanced.md` — Document domain validation pattern

**Unchanged files:**
- `agent-core/agents/vet-fix-agent.md` — No changes (reads domain skill files naturally)
- `agent-core/fragments/vet-requirement.md` — No changes (domain validation is additive)
- Existing plugin-dev review agents — Remain for interactive use

### Testing Strategy

- **Manual validation:** Create a plugin skill, run vet with domain criteria reference, verify domain-specific issues are caught
- **Comparison test:** Review same artifact with and without domain criteria — domain version should catch additional issues
- **Planner integration:** Verify planner includes domain skill reference in runbook vet steps when rules file is active

### Risk Assessment

| Risk | Impact | Mitigation |
|---|---|---|
| Vet-fix-agent ignores domain skill file | Domain criteria not applied | Explicit instruction in task prompt: "Read and apply criteria from..." |
| Domain skill too large for context | Token budget exceeded | Keep criteria concise — checklists + examples, not full skill docs |
| Planner forgets domain reference | Generic vet only | Rules file reminder in planner's context; document in plan skills |
| Criteria extraction loses nuance | False positives/negatives in review | Start with clear-cut criteria, iterate based on review results |

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agent-core/fragments/vet-requirement.md` — Current vet workflow
- `agent-core/agents/vet-fix-agent.md` — Vet-fix-agent protocol (how it processes instructions)
- `plans/domain-validation/reports/explore-review-agents.md` — Review agent ecosystem
- `plans/domain-validation/reports/explore-validation-patterns.md` — Validation patterns and context delivery

**Plugin-dev skills (source material for validation criteria):**
- Load `plugin-dev:skill-development` — Skill review criteria
- Load `plugin-dev:agent-development` — Agent review criteria
- Load `plugin-dev:hook-development` — Hook review criteria
- Load `plugin-dev:command-development` — Command review criteria
- Load `plugin-dev:plugin-structure` — Plugin structure review criteria

**Additional research allowed:** Planner may explore existing plugin-dev review agents (skill-reviewer, plugin-validator) for additional criteria patterns.

## Next Steps

- Route to `/plan-adhoc` for runbook generation (general workflow — not TDD, infrastructure/documentation work)
- Load `plugin-dev:skill-development` before planning (validation skill is itself a skill artifact)
- Execution model: sonnet for skill file creation, sonnet for rules file, sonnet for plan skill updates
