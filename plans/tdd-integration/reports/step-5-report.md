# Step 5 Report: Update /oneshot skill for methodology detection

**Step**: `plans/tdd-integration/steps/step-5.md`
**Date**: 2026-01-19
**Status**: ✅ Complete

---

## Actions Taken

Modified `agent-core/skills/oneshot/skill.md` to add TDD methodology detection and workflow routing logic.

### 1. Added Methodology Detection Section
- Inserted after "Applicability" section (line 26)
- Documents TDD vs General methodology signals
- Lists workflow routing paths for each methodology

### 2. Added Workflow Selection Section
- Describes TDD workflow characteristics (spike tests, TDD cycles, tdd-task agent)
- Describes General workflow characteristics (implementation details, sequential steps, quiet-task agent)

### 3. Added Workflow Documentation References
- Links to `agent-core/agents/tdd-workflow.md`
- Links to `agent-core/agents/oneshot-workflow.md`

---

## Validation Results

✅ "Methodology Detection" section present (line 26)
✅ "TDD Methodology Signals" documented (line 30)
✅ "Workflow Routing" documented (line 42)
✅ "Workflow Documentation" references added (line 62)
✅ TDD workflow documentation reference present (line 64)

**File size**: 9,391 bytes (added ~1,400 bytes of content)

---

## Key Changes

**TDD Methodology Signals:**
- Project has test-first culture
- User mentions "test", "TDD", "red/green"
- Feature requires behavioral verification
- Project is pytest-md or similar

**General Methodology Signals:**
- Infrastructure/migration work
- Refactoring without behavior change
- Prototype/exploration
- Default if TDD signals absent

**Workflow Routing:**
- TDD path: `/design` (TDD mode) → `/plan-tdd` → `/orchestrate` → `/vet` → `/review-analysis`
- General path: `/design` → `/plan-adhoc` → `/orchestrate` → `/vet`

---

## Success Criteria Met

✅ skill.md contains methodology detection
✅ Workflow routing documented
✅ References to workflow docs added
✅ No syntax errors
✅ File structure preserved

---

## Notes

- File size increased by approximately 1,400 bytes (more than the expected 300-500 due to comprehensive documentation)
- All three required sections successfully added in logical order
- Integration points with existing skill structure maintained
- No conflicts with existing content
