# Statusline Visual Parity - Runbook Outline

## Requirements Mapping

| Requirement | Description | Implementation Phase/Cycle |
|-------------|-------------|---------------------------|
| R1 | Model display with emoji/color/thinking indicator | Phase 1: Cycles 1.1-1.3 |
| R2 | Directory display with 📁 prefix and color | Phase 1: Cycle 1.4 |
| R3 | Git status with ✅/🟡 emoji and color | Phase 1: Cycle 1.5 |
| R4 | Cost display with 💰 prefix | Phase 1: Cycle 1.6 |
| R5 | Context display with 🧠 prefix, color, horizontal token bar | Phase 2: Cycles 2.1-2.2 |
| R6 | Mode line with 🎫/💳 emoji and color | Phase 1: Cycle 1.7 |
| R7 | Python environment indicator with 🐍 prefix | Phase 3: Cycle 3.1 |
| TTL | Update UsageCache TTL from 30s to 10s | Phase 4: Cycle 4.1 |

## Phase Structure

### Phase 1: Display Formatting (6 cycles)

**Objective:** Implement emoji and color formatting methods in StatuslineFormatter

**Cycles:**
- **1.1 (RED):** `_extract_model_tier()` helper - Test tier extraction from display_name
- **1.1 (GREEN):** `_extract_model_tier()` implementation
- **1.2 (RED):** `format_model()` - Test medal emoji, color, abbreviated name
- **1.2 (GREEN):** `format_model()` implementation with emoji mappings
- **1.3 (RED):** `format_model()` thinking indicator - Test 😶 when disabled
- **1.3 (GREEN):** Extend `format_model()` with thinking state
- **1.4 (RED):** `format_directory()` - Test 📁 emoji and CYAN color
- **1.4 (GREEN):** `format_directory()` implementation
- **1.5 (RED):** `format_git_status()` - Test ✅/🟡 emoji and branch color
- **1.5 (GREEN):** `format_git_status()` implementation
- **1.6 (RED):** `format_cost()` - Test 💰 emoji prefix
- **1.6 (GREEN):** `format_cost()` implementation

**Complexity:** 6 cycles (RED/GREEN pairs), straightforward pattern replication

**Model:** Haiku (execution-focused formatting)

---

### Phase 1 (continued): Format Mode (1 cycle)

**Cycles:**
- **1.7 (RED):** `format_mode()` - Test 🎫/💳 emoji and color based on account mode
- **1.7 (GREEN):** `format_mode()` implementation

---

### Phase 2: Token Bar and Context (3 cycles)

**Objective:** Implement horizontal multi-block token bar and context formatting

**Cycles:**
- **2.1 (RED):** `horizontal_token_bar()` - Test multi-block rendering with 8-level Unicode
- **2.1 (GREEN):** `horizontal_token_bar()` implementation
- **2.2 (RED):** `horizontal_token_bar()` color - Test progressive color per block
- **2.2 (GREEN):** Extend `horizontal_token_bar()` with threshold-based color
- **2.3 (RED):** `format_context()` - Test 🧠 prefix, colored tokens, horizontal bar
- **2.3 (GREEN):** `format_context()` implementation integrating `horizontal_token_bar()`

**Complexity:** 3 cycles (RED/GREEN pairs), moderate algorithm complexity

**Model:** Haiku (pattern established, clear shell reference)

---

### Phase 3: CLI Integration and Validation (4 cycles)

**Objective:** Add Python environment detection, integrate formatter methods into CLI, and validate visual parity

**Cycles:**
- **3.1 (RED):** `get_python_env()` and `PythonEnv` model - Test VIRTUAL_ENV/CONDA_DEFAULT_ENV detection
- **3.1 (GREEN):** Implementation in context.py and models.py
- **3.2 (RED):** CLI Line 1 composition - Test integrated format methods (model, directory, git, cost, context)
- **3.2 (GREEN):** Replace string concatenation with formatter method calls in cli.py
- **3.3 (RED):** CLI Line 2 composition - Test mode line with format_mode() and usage data
- **3.3 (GREEN):** Integrate format_mode() into Line 2 composition
- **3.4 (RED):** Integration validation - Test end-to-end visual parity against shell output
- **3.4 (GREEN):** Fix any presentation gaps, verify all requirements met

**Complexity:** 4 cycles (RED/GREEN pairs), environment detection + composition and validation

**Model:** Haiku (integration and testing)

**Checkpoint:** Full (end of Phase 3)

---

### Phase 4: TTL Update (1 cycle)

**Objective:** Update UsageCache TTL to match design spec

**Cycles:**
- **4.1 (RED):** Test UsageCache TTL is 10 seconds
- **4.1 (GREEN):** Update TTL constant from 30s to 10s in usage.py

**Complexity:** 1 cycle (RED/GREEN pair), single constant change

**Model:** Haiku (trivial update)

---

## Key Design Decisions Reference

- **D1:** Extend StatuslineFormatter for emoji/color methods (display.py)
- **D2:** Horizontal token bar with multi-block rendering (shell lines 169-215)
- **D3:** CLI composition calls formatter methods (cli.py)
- **D4:** Model tier extraction via substring matching (display.py helper)
- **D5:** Add bright colors (brgreen, brred) and BLINK constant
- **D6:** Python environment detection in context.py
- **D7:** TTL adjustment from 30s to 10s (non-critical)

## Complexity Per Phase

| Phase | Cycles | Estimated Complexity | Model |
|-------|--------|---------------------|-------|
| Phase 1 | 7 | Low (pattern replication) | Haiku |
| Phase 2 | 3 | Medium (token bar algorithm) | Haiku |
| Phase 3 | 1 | Low (environment check) | Haiku |
| Phase 4 | 3 | Medium (integration testing) | Haiku |
| Phase 5 | 1 | Low (constant update) | Haiku |
| **Total** | **15** | **Moderate** | **Haiku** |

**Note:** Each cycle represents a RED/GREEN pair. Total cycle count matches design estimate (12-15 cycles → 15 cycles).

## Success Criteria

1. ✓ Visual parity with shell output (emoji, colors, bars)
2. ✓ All tests pass (existing + new formatting tests)
3. ✓ No functional regressions (data gathering unchanged)
4. ✓ TTL conformance (10 seconds per R4)

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Cycle expansion:**
- Expand RED phase descriptions with specific test cases (e.g., "Test `_extract_model_tier('Claude Sonnet 4')` returns 'sonnet'")
- Add specific shell line number references in cycle notes for algorithm verification (already in design, propagate to cycles)
- Expand cycle 4.3 with explicit edge cases (missing data, unknown model names, terminal width constraints)
- Include visual inspection step in cycle 4.3 to verify ANSI codes render correctly
- Note opportunities for test fixture reuse across similar format methods (cycles 1.2-1.7)

**Checkpoint guidance:**
- Phase 4 checkpoint should include visual diff against shell output with identical input data
- Consider adding intermediate checkpoint after Phase 2 (token bar complete) for early algorithm validation
- Final checkpoint (end of Phase 4) should validate against conformance report criteria

**References to include:**
- Shell implementation: `scratch/home/claude/statusline-command.sh` (lines 416-441 for model, 169-215 for token bar)
- Conformance report: `plans/statusline-wiring/reports/conformance-validation.md`
