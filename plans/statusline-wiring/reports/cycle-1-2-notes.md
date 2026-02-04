# Cycle 1.2: Handle current_usage as optional (null case)

**Status:** REGRESSION - Feature already implemented

**Test command:** `pytest tests/test_statusline_models.py::test_parse_null_current_usage -xvs`

**RED result:** PASS (unexpected - expected FAIL with ValidationError)

**Expected failure:** ValidationError: current_usage field required

**Actual result:** Test passes without error

**Analysis:**
- Models.py already has: `current_usage: ContextUsage | None = None` (line 22 of models.py)
- Field is marked as Optional with default value None
- Pydantic accepts null values without validation error
- Feature already implemented during cycle 1.1 or earlier

**Regression check:** N/A (feature already present)

**Files modified:** tests/test_statusline_models.py (added test_parse_null_current_usage)

**Decision made:**
Per cycle spec: "If passes, STOP - field may already be optional"
- Wrote test to verify current_usage=null handling
- Test passes, confirming feature is already implemented
- No implementation changes needed
- Test added for regression coverage in future cycles

**Next action:** Continue to cycle 1.3 (no blocking issues)
