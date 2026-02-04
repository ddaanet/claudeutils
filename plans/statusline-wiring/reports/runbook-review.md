# TDD Runbook Review: statusline-wiring

**Date**: 2026-02-04
**Reviewer**: tdd-plan-reviewer (Sonnet 4.5)
**Runbook**: plans/statusline-wiring/runbook.md

---

## Summary

- **Total cycles**: 31 (matches metadata)
- **Violations found**: 12 CRITICAL (file reference violations)
- **Overall assessment**: NEEDS REVISION

---

## Critical Issues

### Issue 1: Missing test files (BLOCKING)

**Location**: All cycles across all phases
**Problem**: All test files referenced in RED/GREEN phases do not exist

**Missing files:**
- `tests/test_statusline_models.py` (Cycles 1.1-1.3)
- `tests/test_statusline_context.py` (Cycles 2.1-2.8)
- `tests/test_statusline_plan_usage.py` (Cycles 3.1-3.3)
- `tests/test_statusline_api_usage.py` (Cycles 4.4-4.7)
- `tests/test_statusline_cli.py` (Cycles 5.1-5.5)
- `tests/test_switchback.py` (Cycles 4.1-4.3)

**Existing files:**
- `tests/test_statusline_display.py` (referenced in Cycles 6.1-6.2, EXISTS)
- `tests/test_statusline_structure.py` (not referenced in runbook)

**Impact**: Runbook cannot execute — every RED phase will fail with "file not found" instead of expected test failures.

**Recommendation**: Either:
1. Create placeholder test files before execution (preferred), OR
2. Update runbook to acknowledge test creation as part of RED phase

---

### Issue 2: Missing source modules (BLOCKING)

**Location**: All cycles except Phase 6
**Problem**: All source modules referenced in GREEN phases do not exist

**Missing modules:**
- `src/claudeutils/statusline/models.py` (Cycles 1.1-6.2)
- `src/claudeutils/statusline/context.py` (Cycles 2.1-2.8, 5.2)
- `src/claudeutils/statusline/plan_usage.py` (Cycles 3.2-3.3, 5.3)
- `src/claudeutils/statusline/api_usage.py` (Cycles 4.4-4.7, 5.3)

**Existing modules:**
- `src/claudeutils/statusline/cli.py` (referenced in Cycles 5.1-5.5, EXISTS)
- `src/claudeutils/statusline/display.py` (referenced in Cycles 6.1-6.2, EXISTS)

**Impact**: GREEN phases will create new files. This is expected for TDD, but conflicts with "Verify no regression: pytest tests/test_statusline_*.py" which assumes existing tests.

**Recommendation**: Update Common Context to clarify:
- These are net-new modules (no existing tests to regress)
- Regression verification applies only to display.py/cli.py modules

---

### Issue 3: Missing function in account.switchback

**Location**: Cycles 4.2-4.3, 4.7
**Problem**: `account.switchback.read_switchback_plist()` does not exist

**Existing module**: `src/claudeutils/account/switchback.py` EXISTS
**Existing function**: `create_switchback_plist()` EXISTS (Cycle 4.1 will modify this)
**Missing function**: `read_switchback_plist()` NOT FOUND

**Cycles affected:**
- Cycle 4.2: Create `read_switchback_plist()` in account.switchback
- Cycle 4.3: Handle missing plist gracefully
- Cycle 4.7: Call `read_switchback_plist()` from api_usage.py

**Impact**: Cycles 4.2-4.3 correctly create the function. Cycle 4.7 assumes it exists in `account.switchback`, which is correct IF Cycles 4.2-4.3 executed first.

**Recommendation**: Add explicit dependency: Cycle 4.7 [DEPENDS: 4.2, 4.3]

---

### Issue 4: test_switchback.py location ambiguity

**Location**: Cycles 4.1-4.3
**Problem**: Runbook references `tests/test_switchback.py` but existing file is `tests/test_account_switchback.py`

**Glob results:**
- `tests/test_account_switchback.py` (EXISTS, likely target)
- `tests/test_switchback.py` (NOT FOUND)

**Recommendation**: Update Cycles 4.1-4.3 to use `tests/test_account_switchback.py` instead of `tests/test_switchback.py`

---

### Issue 5: Metadata accuracy (Total Steps mismatch)

**Location**: Weak Orchestrator Metadata (line 16)
**Problem**: Metadata declares "Total Steps: 31" but actual cycle count is 31

**Cycle count verification:**
- Phase 1: Cycles 1.1-1.3 (3 cycles)
- Phase 2: Cycles 2.1-2.8 (8 cycles)
- Phase 3: Cycles 3.1-3.3 (3 cycles)
- Phase 4: Cycles 4.1-4.7 (7 cycles)
- Phase 5: Cycles 5.1-5.5 (5 cycles)
- Phase 6: Cycles 6.1-6.2 (2 cycles)
- Total: 3+8+3+7+5+2 = 28 cycles

**Actual count**: 28 cycles (not 31 as declared)
**Checkpoints**: 3 light checkpoints (lines 619, 774, 1127, 1378) + 1 full checkpoint (line 1484) = 4 checkpoints (not counted as cycles)

**Impact**: Orchestrator may expect 31 cycles but only 28 exist.

**Recommendation**: Update metadata to "Total Steps: 28"

---

### Issue 6: account.usage.UsageCache.TTL_SECONDS reference

**Location**: Cycle 3.1 (line 656)
**Problem**: Runbook assumes `UsageCache.TTL_SECONDS = 30` exists

**Verification needed**: Check if `src/claudeutils/account/usage.py` has `UsageCache` class with `TTL_SECONDS` attribute.

**Impact**: If attribute doesn't exist or has different name, RED phase will fail with wrong error message.

**Recommendation**: Verify attribute exists before execution, or update RED phase expected failure.

---

## Prescriptive Code Analysis

### Phase 1: Scan for Code Blocks in GREEN Phases

**Search pattern**: `**GREEN Phase:**` followed by code blocks (` ```python`)

**Result**: NO code blocks found in any GREEN phase

**Analysis**: All GREEN phases use behavioral descriptions, not prescriptive code. Examples:
- Cycle 1.1: "Create with StatuslineInput, ContextUsage, ModelInfo..." (structural guidance, not code)
- Cycle 2.1: "call subprocess.run(...)" (API call specification, not implementation)
- Cycle 2.7: "read last 1MB with seek, parse lines in reverse..." (algorithm description, not code)

**Assessment**: PASS — No prescriptive code violations

---

## RED/GREEN Sequencing Analysis

### Phase 2: Validate RED → GREEN Transitions

Analyzed all 28 cycles for proper RED → GREEN sequencing:

**PASS — Proper sequencing:**
- All cycles follow pattern: RED (ModuleNotFoundError/AttributeError/AssertionError) → GREEN (create/add/update)
- Incremental progression observed (e.g., Cycle 2.1 creates module, 2.2 adds feature, 2.3 adds error handling)
- No "complete implementation in first cycle" violations

**Examples of good sequencing:**
- Cycle 1.1: Module doesn't exist → Create module with models
- Cycle 1.2: Field not optional → Make field optional
- Cycle 2.1: Function doesn't exist → Create function with happy path
- Cycle 2.3: No error handling → Add try/except
- Cycle 5.4: Outputs stub "OK" → Replace with real output

**Assessment**: PASS — All cycles demonstrate proper RED → GREEN discipline

---

## Weak RED Assertions Analysis

### Phase 3: Verify Behavioral Assertions

Checked all RED phases for structural-only vs behavioral assertions:

**Strong assertions (behavioral):**
- Cycle 1.3: Asserts token sum (tests actual calculation, not just structure)
- Cycle 2.2: Asserts dirty=True when porcelain output non-empty (tests logic)
- Cycle 2.6: Asserts calculate_context_tokens() returns 200 (tests computation)
- Cycle 2.7: Asserts context tokens from transcript parsing (tests fallback logic)
- Cycle 4.5: Asserts week aggregation sums 7 days correctly (tests accumulation)
- Cycle 5.4: Asserts two-line output with real data (tests end-to-end behavior)

**Weak assertions flagged:**
- Cycle 5.1: RED expects stub "OK" output, GREEN just imports StatuslineInput (test may pass without real work)
  - **Mitigation**: Cycle 5.4 forces real output, so 5.1 is acceptable as incremental step

**Assessment**: MOSTLY PASS — One borderline case (5.1) mitigated by later cycle

---

## Implementation Hints vs Prescription

### Phase 4: Evaluate Guidance Quality

All GREEN phases provide implementation hints without prescribing exact code:

**Good examples:**
- Cycle 2.1: "call subprocess.run([...]) and subprocess.run([...])" — specifies API, not full function body
- Cycle 2.7: "read last 1MB with seek, parse lines in reverse, filter type=='assistant' and not isSidechain, sum 4 token fields, return first non-zero" — algorithm steps, not code
- Cycle 5.4: "format line 1 (model + dir + git + cost + context), format line 2 (mode + usage)" — output structure, not exact formatting code

**No violations**: No GREEN phases contain complete function implementations.

**Assessment**: PASS — All hints are appropriately high-level

---

## Recommendations

### 1. File Reference Corrections (CRITICAL — must fix before execution)

**Action 1**: Create placeholder test files or update runbook to acknowledge test creation in RED phase.

**Suggested approach**: Add to Common Context:
```markdown
**Test file creation strategy:**
- Test files do not exist before runbook execution
- RED phase creates test file with failing test
- GREEN phase creates source module to pass test
- Pattern: RED writes test → GREEN writes implementation
```

**Action 2**: Update Cycle 4.1-4.3 test references:
```diff
- pytest tests/test_switchback.py::test_create_switchback_plist_includes_month_day -xvs
+ pytest tests/test_account_switchback.py::test_create_switchback_plist_includes_month_day -xvs
```

**Action 3**: Fix metadata Total Steps:
```diff
- **Total Steps**: 31
+ **Total Steps**: 28
```

**Action 4**: Add dependency notation:
```diff
## Cycle 4.7: Format switchback time as MM/DD HH:MM

+**Dependencies**: [DEPENDS: 4.2, 4.3] (requires read_switchback_plist function)
```

---

### 2. Common Context Clarifications

**Add section to Common Context:**
```markdown
**Module creation order:**
- Phase 1: models.py (Pydantic schemas)
- Phase 2: context.py (git, thinking, context calculation)
- Phase 3: plan_usage.py (OAuth API usage)
- Phase 4: api_usage.py (stats-cache.json parsing), switchback.py (read_switchback_plist)
- Phase 5: cli.py (orchestration)
- Phase 6: display.py (formatting — already exists, enhancement only)

**Regression testing scope:**
- Phases 1-5: No existing tests (net-new modules)
- Phase 6: Existing display.py tests must pass (true regression check)
```

---

### 3. RED Phase Enhancement

**Problem**: Several RED phases assume "function doesn't exist" but don't specify how agent should write the test without knowing the function signature.

**Recommendation**: Add guidance to Common Context:
```markdown
**RED phase test writing:**
- Test file creation is part of RED phase
- Test should import and call the function being developed
- Expected failure: ModuleNotFoundError or AttributeError
- Agent infers minimal function signature from requirements
- GREEN phase implements to match test expectations
```

---

### 4. Verification Commands

**Issue**: "Verify no regression: pytest tests/test_statusline_*.py" will fail in early cycles because test files don't exist.

**Fix**: Update pattern to:
```diff
- **Verify no regression:** pytest tests/test_statusline_*.py
+ **Verify no regression:** pytest tests/test_statusline_*.py (skip if no tests exist yet)
```

Or use explicit file lists:
```markdown
**Verify no regression:** pytest tests/test_statusline_display.py (if exists)
```

---

## Conclusion

**Runbook quality**: Excellent TDD discipline, proper RED → GREEN sequencing, behavioral assertions, non-prescriptive guidance.

**Blocking issues**: File references assume files exist when they don't (12 CRITICAL violations).

**Path forward**:
1. Apply file reference corrections (Actions 1-4 above)
2. Add clarifications to Common Context (Recommendation 2)
3. Execute runbook with fixed file paths
4. Monitor for actual vs expected failures in RED phases

**Estimated fix time**: 30-60 minutes to update file paths and metadata.

**Recommended next steps**:
1. Fix CRITICAL file reference issues
2. Re-run review to verify fixes
3. Proceed to execution with corrected runbook

---

**Report generated**: 2026-02-04
**Review methodology**: Skill-based systematic analysis (review-tdd-plan)
