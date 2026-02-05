# Cycle 2.1

**Plan**: `plans/statusline-parity/runbook.md`
**Execution Model**: haiku
**Phase**: 2
**Report Path**: `plans/statusline-parity/reports/cycle-2-1-notes.md`

---

## Cycle 2.1: Horizontal Token Bar Multi-Block Rendering

**Objective**: Create `horizontal_token_bar()` method with 8-level Unicode blocks for multi-block rendering

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_horizontal_token_bar` in `tests/test_statusline_display.py`

**Assertions:**
- `horizontal_token_bar(0)` returns empty string (no tokens)
- `horizontal_token_bar(25000)` returns single full block "█"
- `horizontal_token_bar(12500)` returns single half-block "▌" (8-level partials)
- `horizontal_token_bar(50000)` returns "██" (two full blocks)
- `horizontal_token_bar(37500)` returns "█▌" (one full + one half)
- `horizontal_token_bar(100000)` returns "████" (4 full blocks at 25k per block)
- `horizontal_token_bar(130625)` returns "█████▊" (5 full + 8-level partial at level 5/8)
- All blocks rendered with same color (no color progression yet - tested in 2.2)
- Format: `[{blocks}]` with square brackets

**Unicode levels reference (8-level):**
- Level 0: space " " (0/8)
- Level 1: ▏ (1/8)
- Level 2: ▎ (2/8)
- Level 3: ▍ (3/8)
- Level 4: ▌ (4/8)
- Level 5: ▋ (5/8)
- Level 6: ▊ (6/8)
- Level 7: ▉ (7/8)
- Level 8: █ (8/8 - full block)

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'horizontal_token_bar'`

**Why it fails:** Method doesn't exist yet

**Verify RED:** `pytest tests/test_statusline_display.py::test_horizontal_token_bar -v`

---

### GREEN Phase

**Implementation:** Add `horizontal_token_bar()` method to StatuslineFormatter

**Behavior:**
- Accept token_count as integer parameter
- Divide tokens into 25k chunks to determine full blocks
- Calculate remainder tokens and map to 8-level Unicode scale (0/8 through 8/8)
- Compose bar string from full block characters (█) plus one partial block if remainder exists
- Wrap result in square brackets
- Return formatted bar string

**Approach:** Direct implementation of shell algorithm (lines 169-215). Uses mathematical division/modulo to calculate blocks, maps remainder fraction to 8-level Unicode scale per D2.

**Hint:** 8-level Unicode blocks defined in RED phase Unicode reference. Map remainder as fraction of 25k, scale 0-8.

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add `horizontal_token_bar(token_count: int) -> str` method
  Location hint: After existing formatter methods

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_horizontal_token_bar -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (AttributeError), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-2-1-notes.md

---
