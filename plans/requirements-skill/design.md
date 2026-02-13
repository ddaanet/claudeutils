# Requirements Skill: Design

## Problem

Two gaps in the current workflow:
1. **Mid-conversation capture:** After ad-hoc discussions, requirements live only in conversation context — lost or degraded on session end.
2. **Cold-start elicitation:** No structured step guides requirements gathering before `/design`.

Both result in `/design` Phase A.0 re-discovering intent from scratch or working from vague input.

## Requirements

**Source:** `plans/requirements-skill/requirements.md`

**Functional:**
- FR-1: Conversational collection — skill guides user through structured elicitation → addressed by Elicit mode
- FR-2: Flexible follow-up — can be followed by /handoff, /design, /runbook → addressed by Workflow Positioning
- FR-3: Requirements artifact — produces requirements.md that downstream skills consume → addressed by Standard Artifact Format

**Non-functional:**
- NFR-1: Lightweight — should not duplicate exploration/doc-search phases → addressed by Lightweight Discovery (capped scope)
- NFR-2: Standalone value — useful without proceeding to design/plan immediately → addressed by standalone workflow path

**Out of scope:**
- Automated requirements validation
- Requirements-to-code traceability
- Changes to `/design` or `/runbook` skills
- Deep exploration (quiet-explore agents, Context7, web research)

## Architecture

### Dual-Mode Operation

`/requirements <job>` detects conversation state and operates in the appropriate mode:

**Extract mode** — conversation contains substantive discussion about a feature/task:
1. Scan conversation context for requirements signals (feature descriptions, constraints mentioned, scope discussions)
2. Lightweight codebase discovery
3. Structure extracted requirements into standard format
4. Gap detection: identify empty critical sections
5. Present draft to user for validation
6. Ask targeted questions only for empty critical sections
7. Write `plans/<job>/requirements.md`

**Elicit mode** — fresh conversation or minimal prior context:
1. Ask semi-structured questions using standard sections as framework
2. Adapt follow-up questions based on responses (not rigid template-fill)
3. Lightweight codebase discovery (after initial scope is understood)
4. Structure responses into standard format
5. Present draft to user for validation
6. Write `plans/<job>/requirements.md`

**Mode detection heuristic:** If conversation before `/requirements` invocation contains feature/task discussion (descriptions of desired behavior, constraints, scope mentions) → extract mode. Otherwise → elicit mode. No explicit mode flag needed — the skill infers from context.

### Lightweight Codebase Discovery

Quick scan to ground requirements in reality. Runs after initial requirements are understood (either extracted or elicited) so the scan is targeted.

**Discovery actions:**
- `Glob` for `plans/*/requirements.md` and `plans/*/design.md` — find related work, avoid duplication
- `Grep` for key terms from the requirements in source files — check what exists in the relevant area
- `Read` existing patterns in the area — inform constraints

**Discovery boundaries:**
- Direct tool use only (Glob, Grep, Read) — no agent delegation
- Capped at ~5 tool calls — enough to ground, not enough to explore
- No Context7, no web research, no quiet-explore agents

**Rationale:** Satisfies NFR-1. Prevents naive requirements (e.g., "add feature X" when X already exists). Costs ~30 seconds, saves design-time re-discovery.

### Standard Artifact Format

```markdown
# <Job Name>

## Requirements

### Functional Requirements
**FR-1: <requirement title>**
<description, acceptance criteria>

### Non-Functional Requirements
**NFR-1: <requirement title>**
<description>

### Constraints
**C-1: <constraint title>**
<rationale>

### Out of Scope
- <item> — <rationale>

### Dependencies
- <dependency> — <impact on implementation>

### Open Questions
- Q-1: <unresolved item — what needs investigation>
```

**Section rules:**
- Omit empty sections entirely (don't write "### Constraints" with nothing under it)
- Number identifiers sequentially within each section (FR-1, FR-2, ... not FR-1, FR-3)
- Open Questions section captures items the conversation didn't resolve — these become Design Phase A research targets
- Dependencies section flags blocking work, prerequisite plans, or external dependencies

### Skill Dependency Scanning

After writing the artifact, scan the requirements text for skill dependency indicators:

| Indicator | Skill to flag |
|-----------|---------------|
| "sub-agent", "delegate to agent", "agent definition" | `plugin-dev:agent-development` |
| "skill", "invoke skill", "skill preloaded" | `plugin-dev:skill-development` |
| "hook", "PreToolUse", "PostToolUse" | `plugin-dev:hook-development` |
| "plugin", "MCP server" | `plugin-dev:plugin-structure` |

If indicators found, append a note to the artifact:

```markdown
### Skill Dependencies (for /design)
- Load `plugin-dev:hook-development` before design (hooks mentioned in FR-2)
```

Design A.0 already scans for these, but flagging in the artifact makes it explicit.

### Gap Detection

After extraction (extract mode) or initial structuring (elicit mode), check for empty critical sections:

**Critical sections** (ask if empty):
- Functional Requirements — "What should the system do?"
- Out of Scope — "What should it NOT do?"

**Non-critical sections** (note absence, don't ask):
- NFRs, Constraints, Dependencies — many tasks genuinely have none

**Question budget:** Maximum 3 gap-fill questions per invocation. The skill captures what the conversation provided; it doesn't interrogate.

### Workflow Positioning

```
/requirements <job> → /design plans/<job>/ (seeds A.0)
/requirements <job> → /handoff (document intent for later)
/requirements <job> → /runbook plans/<job>/design.md (direct to planning, if clear)
/requirements <job> (standalone — capture intent, no follow-up)
```

No changes needed to `/design` or `/runbook` — Design A.0 already consumes `requirements.md` from the job directory.

**Default exit:** Present the artifact path and suggest next step based on completeness:
- Few open questions, clear scope → suggest `/design`
- Many open questions, unclear scope → suggest standalone (revisit later)
- User explicitly stated intent → suggest that path

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Dual-mode (extract/elicit) | Covers both mid-conversation capture and cold-start; same output format |
| Opus model tier | Extract mode requires synthesizing nuanced conversation; sonnet misses implicit requirements |
| Semi-structured elicitation | Research validates: predetermined framework + adaptive follow-ups most effective |
| Lightweight discovery (capped) | Grounds requirements without duplicating design exploration (NFR-1) |
| Gap-fill, not interrogation | Max 3 questions; captures conversation, doesn't replace it |
| Extract from conversation, don't infer | Hallucination risk: ground in what was said, flag unknowns as Open Questions |
| Omit empty sections | Clean artifacts; don't scaffold structure nobody will fill |

## Empirical Grounding

Design informed by requirements engineering research (details in `references/empirical-grounding.md`):

- **HAIC pattern** (58% industry adoption) — extract + human validation, not autonomous generation
- **Semi-structured interviews** — most effective technique; standard sections as framework with adaptive follow-ups
- **AI excels at structuring** — extract mode is the validated value proposition
- **Hallucination risk** — extract from conversation (grounded), capture unknowns as Open Questions rather than inventing requirements
- **81% human review** — gap-fill presents draft for user validation before writing

## Implementation Notes

### Skill Structure

```
agent-core/skills/requirements/
├── SKILL.md              — Dual-mode procedure, format spec, discovery rules
└── references/
    └── empirical-grounding.md  — Research findings informing the design
```

### SKILL.md Content Outline

1. **Frontmatter** — name, description with trigger phrases
2. **Mode Detection** — how to determine extract vs elicit
3. **Extract Mode Procedure** — scan conversation, structure, gap-fill
4. **Elicit Mode Procedure** — semi-structured questions by section
5. **Lightweight Discovery** — what to scan, boundaries
6. **Standard Format** — artifact template
7. **Skill Dependency Scanning** — indicator table
8. **Default Exit** — suggest next step

### Integration Points

- **Design A.0** already consumes `requirements.md` — no changes needed
- **Session.md tasks** can reference `/requirements` as the entry command
- **Jobs.md** status `requirements` already exists for plans with requirements.md

### Phase Typing

- All general (no TDD) — this is a procedural skill, not code

### Affected Files

- `agent-core/skills/requirements/SKILL.md` (new)
- `agent-core/skills/requirements/references/empirical-grounding.md` (new)
- `agent-core/fragments/workflows-terminology.md` — add `/requirements` to workflow entry points
- `.claude/skills/requirements` — symlink via `just sync-to-parent`

### Testing Strategy

Manual validation: invoke `/requirements` in both modes, verify artifact format and discovery behavior. No automated tests (procedural skill, no code).

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agent-core/skills/design/SKILL.md` — Phase A.0 requirements checkpoint (integration point)
- `plugin-dev:skill-development` — skill structure and best practices
- `plans/requirements-skill/reports/research-empirical.md` — empirical grounding for reference file

## Next Steps

1. Implement SKILL.md with dual-mode procedure
2. Create references/empirical-grounding.md from research report
3. Update workflows-terminology.md entry point
4. Sync symlinks via `just sync-to-parent`
5. Manual test in both modes
