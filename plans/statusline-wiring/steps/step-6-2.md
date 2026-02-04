# Cycle 6.2

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-6-2-notes.md`

---

## Cycle 6.2: Replace limit_display with format_plan_limits

**Objective**: StatuslineFormatter.format_plan_limits() creates compact format for both 5h and 7d limits on one line
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_display.py tests format_plan_limits(PlanUsageData(hour5_pct=87, hour5_reset="14:23", day7_pct=42)) returns string with "87%", "42%", "14:23", and vertical bars

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'format_plan_limits'
```

**Why it fails:** format_plan_limits() method doesn't exist yet

**Verify RED:** pytest tests/test_statusline_display.py::test_format_plan_limits -xvs
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add format_plan_limits(data: PlanUsageData) → str method, delete limit_display() method (dead code)

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add format_plan_limits() method that formats "5h {pct}% {bar} {reset} / 7d {pct}% {bar}", use vertical_bar() for bars
- File: src/claudeutils/statusline/display.py
  Action: Delete limit_display() method (no longer used)

**Verify GREEN:** pytest tests/test_statusline_display.py::test_format_plan_limits -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass (update/remove tests for old limit_display if any)

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-6-2-notes.md

---

**Full Checkpoint** (end of Phase 6 - final phase)
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review all changes for quality, clarity, design alignment. Apply high/medium fixes. Commit.
3. Functional: Review all implementations against design. Check for stubs.

---
