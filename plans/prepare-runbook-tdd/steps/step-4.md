# Step 4

**Plan**: `plans/prepare-runbook-tdd/runbook.md`
**Common Context**: See plan file for context

---

## Step 4: Implement TDD Metadata Detection

**Objective**: Extend frontmatter parsing to detect `type: tdd` field and set runbook type flag.

**Script Evaluation**: Prose description (20-30 line modification)

**Execution Model**: Sonnet

**Implementation**:

1. Review existing `parse_frontmatter()` function
2. Add `type` field extraction from frontmatter:
   - Default value: `general` (if absent)
   - Valid values: `tdd`, `general`
   - Store in frontmatter dictionary
3. Add validation for type field:
   - Warn if unknown type value
   - Default to `general` for unknown values
4. Pass runbook type to downstream functions:
   - Modify function signatures if needed
   - Propagate type through call chain
5. Add error message for TDD runbook without type field:
   - "WARNING: TDD runbook detected (cycle headers) but missing 'type: tdd' in frontmatter"

**Expected Outcome**: Frontmatter parsing detects and validates runbook type.

**Unexpected Result Handling**:
- If frontmatter structure differs from expected → report and STOP

**Error Conditions**:
- Invalid YAML syntax → Report clear error
- Unknown type value → Warn and default to general

**Validation**:
- Type field extracted correctly
- Default behavior preserves backward compatibility
- Warning issued for missing type in TDD runbook

**Success Criteria**:
- `parse_frontmatter()` returns type field
- Type validation implemented
- Backward compatibility maintained (no type field → general)
- Changes tested with sample frontmatter (documented in report)

**Report Path**: `plans/prepare-runbook-tdd/reports/step-4-report.md`

---
