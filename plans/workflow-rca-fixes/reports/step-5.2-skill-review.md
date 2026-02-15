# Step 5.2 Self-Review: Design Skill Phase C Additions

**File:** `agent-core/skills/design/SKILL.md`
**FRs:** FR-14 (density checkpoint), FR-15 (repetition helper), FR-19 (agent-name validation, late-addition check)

## Changes Applied

### Density checkpoint (FR-14) -- ENHANCED
- Added concrete thresholds: >8 items/phase, <20 LOC delta for adjacent items
- Added coarseness criterion: >3 unrelated concerns per item
- Added heuristic formula: items x avg-LOC in 100-300 range with interpretation guidance
- Prior version had only qualitative "too granular"/"too coarse" without numeric thresholds

### Repetition helper prescription (FR-15) -- ENHANCED
- Added explicit 5+ threshold (was "more than 5" -- now "5+")
- Added dual justification: token cost (expansion + execution budget per repetition) AND error rate (drift between repetitions)
- Added concrete example: "update field X in files A, B, C, D, E, F"
- Threshold justified by extraction overhead vs repetition cost tradeoff

### Agent-name validation (FR-19) -- NEW
- Specifies Glob tool on two directories: `agent-core/agents/*.md` and `.claude/agents/*.md`
- Failure action: flag as design error (not deferred to implementation)
- Grounded in specific example: `outline-review-agent` vs `runbook-outline-review-agent` mismatch

### Late-addition completeness check (FR-19) -- NEW
- Two re-validation criteria: traceability (maps to outline item) and mechanism (concrete approach)
- Triggers on requirements added after Phase B (outline review)
- Grounded in specific incident: FR-18 bypassed outline-level validation
- Clear failure action: flag for completion before proceeding

## Verification

- All four additions placed in Phase C section (C.1), after content principles and before classification tables
- Density checkpoint has 3 concrete heuristics (not qualitative descriptions)
- Repetition helper justifies threshold with token cost + error rate rationale
- Agent-name validation specifies Glob directories and failure action
- Late-addition check grounded in specific session finding with clear re-validation criteria
- No UNFIXABLE issues identified

## Status: PASS
