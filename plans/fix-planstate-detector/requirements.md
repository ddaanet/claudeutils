# Fix Planstate Detector

## Requirements

### Functional Requirements

**FR-1: Add `outlined` status to planstate inference**
When a plan directory contains `outline.md` but not `design.md`, infer status as `outlined` (not `requirements`). This distinguishes plans that have completed design outline + review from plans still at the requirements stage.

Acceptance criteria:
- `outline.md` present, no `design.md` → status `outlined`
- `outline.md` + `design.md` both present → status `designed` (design.md takes priority, existing behavior)
- `requirements.md` only → status `requirements` (unchanged)
- `outline.md` + `requirements.md`, no `design.md` → status `outlined`

**FR-2: Derive next action for `outlined` status**
Map `outlined` to the appropriate next action command: `/runbook plans/{name}/outline.md`. The outline serves as the design artifact when the design sufficiency gate passes (outline is concrete enough to skip full design).

Acceptance criteria:
- `outlined` status → next action `/runbook plans/{name}/outline.md`
- Existing status→action mappings unchanged

**FR-3: Update downstream enumeration sites**
All locations that enumerate planstate status values must include `outlined`. Per "when adding a new variant to an enumerated system": grep all affected files for existing variant names and update every enumeration site.

Acceptance criteria:
- `agent-core/fragments/execute-rule.md` status values list includes `outlined`
- `agent-core/skills/handoff/SKILL.md` command derivation table includes `outlined` → `/runbook plans/{name}/outline.md`
- Tests cover the new status

### Constraints

**C-1: Priority chain ordering**
`outlined` slots between `designed` and `requirements` in the priority chain: `lifecycle > ready > planned > designed > outlined > requirements`. A plan with both `design.md` and `outline.md` is `designed` (design.md is the higher artifact).

### Out of Scope

- Adding new lifecycle.md states — `outlined` is a pre-ready artifact-detection state, not a post-ready lifecycle state
- Changing vet chain (source→report) mappings — `outline.md → reports/outline-review.md` already exists in `vet.py`
- Planstate validation changes — validation module checks artifact consistency, new status doesn't change validation rules

### Dependencies

- `src/claudeutils/planstate/inference.py` — authoritative status detection
- `src/claudeutils/planstate/models.py` — data model (no changes needed, status is a string)
- `tests/test_planstate_inference.py` — test coverage
- `agent-core/fragments/execute-rule.md` — status enumeration in STATUS display rules
- `agent-core/skills/handoff/SKILL.md` — command derivation table

### References

- Observed during `/handoff` STATUS display: `userpromptsubmit-topic` plan shows `[requirements]` despite having reviewed `outline.md`
- `/when adding a new variant to an enumerated system` — grep downstream enumeration sites
