# Design Review: Design Workflow Enhancement (Rev 2)

**Design Document**: plans/design-workflow-enhancement/design.md
**Review Date**: 2026-02-04
**Reviewer**: design-vet-agent (opus)

## Summary

This design specifies a three-phase workflow for the design skill (Research+Outline → Iterative Discussion → Generate Design), introduces a documentation checkpoint hierarchy, creates a quiet-explore agent for persistent exploration results, and extends the workflow with requirements validation across design, planning, and vet stages. The design is well-structured with clear rationale for decisions and addresses a real problem of wasted opus tokens from single-pass design generation.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Design document already updated in design skill**
   - Note: The current `agent-core/skills/design/SKILL.md` already incorporates the three-phase workflow, documentation checkpoint, documentation perimeter, and quiet-explore delegation from this design. The skill was likely updated in earlier planning steps. The design document's "Affected files" list should acknowledge that partial implementation exists.

2. **Extension section missing from Affected Files (Extension) table**
   - Note: The Affected Files (Extension) table references `agent-core/agents/design-vet-agent.md` for requirements alignment checks, but the current design-vet-agent.md does not include requirements alignment protocol. The table is correct about what needs to change; this is just a status observation.

3. **Vet agents currently lack requirements validation section**
   - Note: The extension specifies adding requirements validation to vet-agent.md and vet-fix-agent.md, but these agents currently have no such section. This is expected (the design describes what to add), but runbook steps should verify existing vet agent structure before extending.

4. **design-vet-agent vs general-purpose opus inconsistency**
   - Note: Design Decision 7 says "Design review stays general-purpose(opus), not vet-agent(sonnet)" but the current design skill (C.3) uses `design-vet-agent` (opus). This is actually correct — the design-vet-agent IS the opus agent for design review. The decision text is slightly misleading but the implementation is correct.

## Positive Observations

- **Clear three-phase structure**: Phases A, B, C are well-defined with explicit objectives and actions
- **Strong rationale for all decisions**: Each of the 12 design decisions includes trade-off analysis and alternatives considered
- **Documentation checkpoint hierarchy**: Five-level fallback system is practical and domain-aware
- **Extension is internally consistent**: Requirements Alignment Validation flows naturally from Phase A.0 through design generation, review, and vet agents
- **Backward compatibility considered**: Documentation perimeter is additive (older designs work unchanged), vet requirements validation is conditional (triggers only when context provided)
- **Runbook guidance section**: Explicitly corrects issues from previous runbook attempts (agent creation pattern, symlink management, step count target)
- **Requirements traceability pattern**: FR-N → design section → runbook context → vet validation is complete and verifiable
- **Plugin-topic detection**: Outline includes skill-loading directive detection for downstream planners

## Validation: Extension Requirements

### 1. Internal Consistency with Original Design

**Verified**: The extension builds on the original design without contradicting it:
- Phase A.0 (requirements checkpoint) slots before A.1 (documentation checkpoint) logically
- Phase C.1 additions (requirements section) extend existing content guidance
- Phase C.3 extension (requirements alignment review) adds checks to existing review protocol
- Affected files lists are complementary (original + extension = complete scope)

### 2. Requirements Validation Flow Completeness

**Verified**: The flow is complete:
- **Design phase**: A.0 loads requirements → C.1 includes Requirements section with traceability → C.3 reviews alignment
- **Plan phase**: Reads requirements from design → includes in Common Context → vet prompt includes requirements
- **Vet phase**: Conditional validation section triggered by requirements context in task prompt

### 3. Gaps Between Original and Extension

**Verified**: No gaps found:
- Extension explicitly references original sections it extends (Phase A, C.1, C.3)
- Affected files are additive (no files modified by original are forgotten in extension)
- Design decisions 9-12 complement decisions 1-8 without overlap

### 4. Affected Files Completeness

**Verified**: All affected files are listed:

| File | Original | Extension | Notes |
|------|----------|-----------|-------|
| `agent-core/skills/design/SKILL.md` | Yes | Yes | Phase A-C + A.0, C.1, C.3 extensions |
| `agent-core/agents/quiet-explore.md` | Yes (create) | No | New agent, no extension changes |
| `agent-core/skills/plan-adhoc/SKILL.md` | Yes | Yes | Read perimeter + requirements passthrough |
| `agent-core/skills/plan-tdd/SKILL.md` | Yes | Yes | Read perimeter + requirements passthrough |
| `agent-core/agents/design-vet-agent.md` | No | Yes | Requirements alignment checks |
| `agent-core/agents/vet-agent.md` | No | Yes | Conditional requirements validation |
| `agent-core/agents/vet-fix-agent.md` | No | Yes | Same as vet-agent |

All files accounted for.

### 5. Design Decisions 9-12 Rationale Adequacy

**Decision 9 (Requirements checkpoint before outline)**:
- Rationale: Clear — requirements inform outline decisions
- Trade-off: Acknowledged (adds step, minimal overhead)
- **Adequate**

**Decision 10 (Traceability in design document)**:
- Rationale: Clear — explicit mapping enables validation
- Alternative considered: Implicit traceability (rejected with reason)
- **Adequate**

**Decision 11 (Conditional requirements validation in vet agents)**:
- Rationale: Clear — backward compatibility
- Trigger mechanism: Defined (task prompt includes requirements)
- **Adequate**

**Decision 12 (Requirements in runbook Common Context)**:
- Rationale: Clear — step agents need context
- Alternative considered: Per-step passing (rejected with reason)
- **Adequate**

## Recommendations

1. **Verify quiet-explore agent exists**: Glob confirms `agent-core/agents/quiet-explore.md` exists. Runbook steps 4-7 (pending) can reference it.

2. **Clarify Decision 7 wording**: Consider updating "Design review stays general-purpose(opus)" to "Design review uses design-vet-agent (opus)" for consistency with current implementation.

3. **Order extension implementation after core**: The extension changes (vet agents, plan skills requirements passthrough) depend on the core design skill changes being complete. Steps 4-7 should sequence correctly.

## Next Steps

1. Proceed to runbook steps 4-7 (remaining implementation)
2. Steps should verify which original design changes are already in design skill before duplicating effort
3. Extension changes (vet agents, plan skills) are net-new and ready for implementation

---

**File paths verified via Glob:**
- `agent-core/skills/design/SKILL.md` — exists (255 lines)
- `agent-core/agents/quiet-explore.md` — exists
- `agent-core/skills/plan-adhoc/SKILL.md` — exists (702 lines)
- `agent-core/skills/plan-tdd/SKILL.md` — exists
- `agent-core/agents/design-vet-agent.md` — exists (259 lines)
- `agent-core/agents/vet-agent.md` — exists (295 lines)
- `agent-core/agents/vet-fix-agent.md` — exists
