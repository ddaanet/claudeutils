# Problem: Cycle Numbering Churn in TDD Runbooks

## Problem Statement

Current TDD runbook system uses sequential numeric identifiers (0.1, 1.1, 1.2, 2.1, etc.) for cycles. When phases are added/removed during runbook creation, all downstream cycle numbers must be renumbered, causing maintenance churn.

## Example

**Original design phases**: R0, R1, R2, R3, R4

**Runbook omits R3** (implementation integrated into R1/R2 GREEN phases):
- Created with phases: R0, R1, R2, R4
- prepare-runbook.py validation fails: "Gap in major cycle numbers: 2 -> 4"
- Must renumber R4 → R3
- Must update all cycle numbers: 4.1 → 3.1, 4.2 → 3.2, 4.3 → 3.3
- Must update all report paths: cycle-4-1-notes.md → cycle-3-1-notes.md
- Must update cross-references to cycles

**Result**: 10+ edits to fix numbering that adds no semantic value.

## Root Cause

**Sequential numbering assumption**:
- prepare-runbook.py enforces sequential major cycle numbers (no gaps)
- Cycle numbers treated as sequence indicators, not stable identifiers
- Validation rejects gaps even though document order defines execution sequence

**Parallel issue in CLAUDE.md**:
> "Avoid numbered lists - Use bullets unless sequencing/ordering matters. Numbered lists cause renumbering churn when edited"

Same principle applies here: ordering DOES matter (dependencies), but NUMBERS don't matter (only document order matters).

## Current Workflow

1. Design specifies phases (may use non-sequential: R0, R1, R2, R4)
2. Runbook generation follows design phase numbering
3. prepare-runbook.py validation fails on gaps
4. Manual renumbering required:
   - Cycle headers
   - Report paths
   - Cross-references
   - Common Context notes
5. Re-run prepare-runbook.py

## Impact

**Maintenance cost**:
- 10-15 edits per phase gap (replace_all operations)
- Easy to miss cross-references
- Interrupts flow during runbook creation

**No semantic benefit**:
- Numbers don't convey meaning (unlike semantic names)
- Document order already defines execution sequence
- prepare-runbook.py extracts cycles top-to-bottom regardless of numbers

**Violates token economy**:
- Multiple edits for no information gain
- Churn in git commits
- Cognitive load tracking renumbering

## Constraints

**Must preserve**:
- Execution order (sequential within phases)
- Unique cycle identifiers (for step file names, reports, cross-references)
- Orchestrator plan structure (phase grouping)

**Can change**:
- Identifier format (numbers vs semantic names)
- Validation rules (allow gaps, semantic IDs, etc.)
- Step file naming convention

## Success Criteria

Solution eliminates renumbering churn while preserving:
- Clear execution order
- Unique cycle identification
- Orchestrator plan compatibility
- Cross-reference capability

## Potential Solutions

**Option 1: Semantic identifiers** (skill-style)
- Phase: "strengthen-providers"
- Cycles: "anthropic-keystore-mock", "openrouter-credentials", "litellm-localhost-url"
- No renumbering needed
- More descriptive
- Longer identifiers

**Option 2: Relax validation** (allow gaps)
- Accept R0, R1, R2, R4 as valid
- Extract cycles in document order
- Numbers become stable identifiers, not sequence
- Minimal change to existing format

**Option 3: Hierarchical semantic** (hybrid)
- Phase: "strengthen-providers"
- Cycles: "strengthen-providers/anthropic", "strengthen-providers/openrouter"
- Filesystem-friendly
- Clear phase grouping

**Option 4: Auto-numbering** (remove from source)
- Cycles have no numbers in runbook.md
- prepare-runbook.py assigns sequential numbers during extraction
- Source file has semantic names or bullets
- Generated artifacts have numbers

## Out of Scope

- Changing orchestrator execution model
- Removing phase concept
- Backward compatibility with existing runbooks (one-time migration acceptable)

## Questions

1. Should identifiers be optimized for humans (semantic) or tooling (short numbers)?
2. How important is step file name readability? (step-0-1.md vs step-cleanup-vacuous.md)
3. Should runbook source format differ from generated artifacts format?
4. Does orchestrator plan need cycle numbers or just stable IDs?

## Related Files

- `agent-core/bin/prepare-runbook.py` - validation logic (line ~80: gap detection)
- `agent-core/skills/plan-tdd/SKILL.md` - cycle numbering guidance
- `agent-core/skills/plan-adhoc/SKILL.md` - adhoc numbering
- `plans/claude-tools-recovery/runbook.md` - recent example of renumbering churn

## Timeline

- **Discovered**: 2026-01-31 during recovery runbook generation
- **Impact**: Immediate (affects all future TDD runbooks)
- **Priority**: Medium (workaround exists: manual renumbering)
