# Cycle 6.1

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-6-1-notes.md`

---

## Cycle 6.1: Add format_tokens helper for humanized token display

**Objective**: StatuslineFormatter.format_tokens() converts token counts to human-readable strings (1234 → "1k", 150000 → "150k")
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_display.py tests format_tokens(1234) == "1k", format_tokens(150000) == "150k", format_tokens(1500000) == "1.5M"

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'format_tokens'
```

**Why it fails:** format_tokens() method doesn't exist yet

**Verify RED:** pytest tests/test_statusline_display.py::test_format_tokens -xvs
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add format_tokens(tokens: int) → str method to StatuslineFormatter class

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add format_tokens() method that checks ranges: <1000 → str(n), <1000000 → "Nk", ≥1000000 → "N.NM"

**Verify GREEN:** pytest tests/test_statusline_display.py::test_format_tokens -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-6-1-notes.md

---
