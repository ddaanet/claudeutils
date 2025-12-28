# Phase 1: Foundation & Testing - Implementation Plan

- **Status**: Ready for execution
- **Created**: 2025-12-26
- **Executor**: Haiku (code role)
- **Context**: Module system implementation - Phase 1 of 8

---

## Prerequisites

1. Read `plans/DESIGN_MODULE_SYSTEM.md` → understand marker-based counting
2. Read `plans/opus-review-module-tiering.md` → understand tier markers
3. Read `agents/modules/src/checkpoint-obedience.semantic.md` → test module for Phase
   1.1

---

## Phase 1.1: Expansion Quality Comparison

**Objective**: Generate weak variants with Sonnet and Opus, compare quality.

**NOT TDD**: This is a comparison task, not test-driven implementation.

### Step 1: Generate with Sonnet

1. Load `agents/modules/src/checkpoint-obedience.semantic.md` → $semantic_source
2. Extract frontmatter `target_rules.weak` → $target_range (12-16)
3. Extract tier sections (Critical/Important/Preferred) → $tier_hints
4. Build prompt → $sonnet_prompt:
   ```
   Generate a weak variant for Haiku model consumption.

   Target: 12-16 rules total

   Mark each rule with tier:
   - [RULE:T1] for Critical rules (~20%)
   - [RULE:T2] for Important rules (~60%)
   - [RULE:T3] for Preferred rules (~20%)

   Source content:
   {$semantic_source}

   Requirements for weak variant:
   - Use ⚠️ markers for critical rules
   - Include "DO NOT" examples
   - Add consequence framing
   - Enumerate patterns explicitly
   - Each rule must be concrete and actionable
   ```

5. Invoke Sonnet → $sonnet_variant
6. Write `agents/modules/gen/checkpoint-obedience.weak.sonnet.md` → $sonnet_variant

### Step 2: Generate with Opus

1. Use same $semantic_source, $target_range, $tier_hints
2. Build identical prompt → $opus_prompt (same as $sonnet_prompt)
3. Invoke Opus → $opus_variant
4. Write `agents/modules/gen/checkpoint-obedience.weak.opus.md` → $opus_variant

### Step 3: Compare Variants

**Manual analysis required - STOP here, output comparison report**

Create `plans/comparison-sonnet-vs-opus.md` with:

1. **Rule Count Analysis**
   - Sonnet: Count `[RULE:T1]`, `[RULE:T2]`, `[RULE:T3]` markers → $sonnet_counts
   - Opus: Count `[RULE:T1]`, `[RULE:T2]`, `[RULE:T3]` markers → $opus_counts
   - Within target range (12-16)?
   - Total counts comparison

2. **Tier Distribution Analysis**
   - Sonnet: Calculate percentages → $sonnet_distribution
   - Opus: Calculate percentages → $opus_distribution
   - Compare to 20/60/20 target
   - Which is closer to ideal distribution?

3. **Formatting Quality**
   - Sonnet: Count ⚠️ markers, "DO NOT" examples, consequence statements
   - Opus: Count ⚠️ markers, "DO NOT" examples, consequence statements
   - Which has better weak-model formatting?

4. **Tier Assignment Quality**
   - Review each variant's T1 rules - are they truly critical?
   - Review each variant's T2 rules - are they important but not critical?
   - Review each variant's T3 rules - are they preferences?
   - Which assigns tiers more accurately?

5. **Explicitness for Haiku**
   - Sonnet: Are rules concrete and actionable?
   - Opus: Are rules concrete and actionable?
   - Which would work better for Haiku execution?

6. **Recommendation**
   - Based on analysis, which model for variant generation?
   - Is quality difference worth cost difference?

**CHECKPOINT 1**: Report comparison results → user decides Sonnet vs Opus

---

## Phase 1.2: Rule Counter Implementation

**Objective**: TDD implementation of marker-based rule counter.

**Implementation**: `src/claudeutils/module_system/rule_counter.py`

### Test Group 1: Basic Marker Counting (3 tests)

#### Test 1: Empty content returns zero

- **Given**: Empty string
- **When**: Count rules
- **Then**: Returns `{'total': 0}`

**NEW code needed**:

- `count_rules(content: str) -> dict` function stub
- Return dict with 'total' key
- Handle empty string

**Does NOT need**:

- Tier-specific counting
- Marker parsing
- Complex logic

**Test code**:

```python
def test_count_rules_empty():
    content = ""
    result = count_rules(content)
    assert result == {'total': 0}
```

---

#### Test 2: Single basic marker

- **Given**: `"[RULE] Text here"`
- **When**: Count rules
- **Then**: Returns `{'untiered': 1, 'total': 1}`

**NEW code needed**:

- Regex to find `[RULE]` markers
- Count matches
- Return 'untiered' count

**Does NOT need**:

- Tier marker parsing (T1/T2/T3)
- Multiple marker handling
- Edge cases

**Test code**:

```python
def test_count_rules_single_basic():
    content = "[RULE] Stop on unexpected results"
    result = count_rules(content)
    assert result == {'untiered': 1, 'total': 1}
```

---

#### Test 3: Multiple basic markers

**Given**:

```
[RULE] First rule
[RULE] Second rule
[RULE] Third rule
```

- **When**: Count rules
- **Then**: Returns `{'untiered': 3, 'total': 3}`

**NEW code needed**:

- Loop/iteration to count all matches
- Accurate total calculation

**Does NOT need**:

- Tier markers
- Mixed format handling

**Test code**:

```python
def test_count_rules_multiple_basic():
    content = """[RULE] First rule
[RULE] Second rule
[RULE] Third rule"""
    result = count_rules(content)
    assert result == {'untiered': 3, 'total': 3}
```

**CHECKPOINT 2**: Run
`just test tests/test_rule_counter.py::test_count_rules_empty tests/test_rule_counter.py::test_count_rules_single_basic tests/test_rule_counter.py::test_count_rules_multiple_basic`
→ awaiting approval

---

### Test Group 2: Tier Marker Parsing (3 tests)

#### Test 4: Single T1 marker

- **Given**: `"[RULE:T1] Critical rule"`
- **When**: Count rules
- **Then**: Returns `{'T1': 1, 'total': 1}`

**NEW code needed**:

- Regex to parse `[RULE:T1]` format
- Extract tier number (T1, T2, T3)
- Track tier-specific counts

**Does NOT need**:

- Multiple tier handling
- Mixed marker formats
- Distribution calculations

**Test code**:

```python
def test_count_rules_tier_t1():
    content = "[RULE:T1] ⚠️ STOP on unexpected results"
    result = count_rules(content)
    assert result == {'T1': 1, 'total': 1}
```

---

#### Test 5: Multiple markers with different tiers

**Given**:

```
[RULE:T1] Critical A
[RULE:T2] Important B
[RULE:T1] Critical C
[RULE:T3] Preferred D
```

- **When**: Count rules
- **Then**: Returns `{'T1': 2, 'T2': 1, 'T3': 1, 'total': 4}`

**NEW code needed**:

- Track counts per tier
- Accumulate across all tiers
- Accurate total calculation

**Does NOT need**:

- Mixed format (basic + tier markers)
- Distribution percentages

**Test code**:

```python
def test_count_rules_multiple_tiers():
    content = """[RULE:T1] Critical A
[RULE:T2] Important B
[RULE:T1] Critical C
[RULE:T3] Preferred D"""
    result = count_rules(content)
    assert result == {'T1': 2, 'T2': 1, 'T3': 1, 'total': 4}
```

---

#### Test 6: Mixed basic and tier markers

**Given**:

```
[RULE] Untiered rule
[RULE:T1] Tier 1 rule
[RULE:T2] Tier 2 rule
```

- **When**: Count rules
- **Then**: Returns `{'untiered': 1, 'T1': 1, 'T2': 1, 'total': 3}`

**NEW code needed**:

- Handle both marker formats in same content
- Separate counting for untiered vs tiered

**Does NOT need**:

- Distribution calculations
- Validation

**Test code**:

```python
def test_count_rules_mixed_markers():
    content = """[RULE] Untiered rule
[RULE:T1] Tier 1 rule
[RULE:T2] Tier 2 rule"""
    result = count_rules(content)
    assert result == {'untiered': 1, 'T1': 1, 'T2': 1, 'total': 3}
```

**CHECKPOINT 3**: Run `just test tests/test_rule_counter.py` (tests 1-6) → awaiting
approval

---

### Test Group 3: Tier Distribution Calculation (2 tests)

#### Test 7: Calculate distribution percentages

**Given**:

```
[RULE:T1] A
[RULE:T1] B
[RULE:T1] C
[RULE:T2] D
[RULE:T2] E
[RULE:T2] F
[RULE:T2] G
[RULE:T2] H
[RULE:T2] I
[RULE:T3] J
[RULE:T3] K
[RULE:T3] L
```

- **When**: Calculate distribution
- **Then**: Returns `{'T1': 25.0, 'T2': 50.0, 'T3': 25.0}`

**NEW code needed**:

- `calculate_distribution(counts: dict) -> dict` function
- Percentage calculation (count / total * 100)
- Handle tier counts only (ignore 'untiered')

**Does NOT need**:

- Deviation calculation
- Warning logic

**Test code**:

```python
def test_calculate_distribution():
    counts = {'T1': 3, 'T2': 6, 'T3': 3, 'total': 12}
    result = calculate_distribution(counts)
    assert result == {'T1': 25.0, 'T2': 50.0, 'T3': 25.0}
```

---

#### Test 8: Distribution with untiered rules

- **Given**: `{'untiered': 2, 'T1': 3, 'T2': 9, 'T3': 3, 'total': 17}`
- **When**: Calculate distribution
- **Then**: Returns `{'T1': 20.0, 'T2': 60.0, 'T3': 20.0}` (ignores untiered)

**NEW code needed**:

- Calculate percentages based on tiered total only
- `tiered_total = T1 + T2 + T3`

**Does NOT need**:

- Edge case handling (zero tiers)

**Test code**:

```python
def test_calculate_distribution_with_untiered():
    counts = {'untiered': 2, 'T1': 3, 'T2': 9, 'T3': 3, 'total': 17}
    result = calculate_distribution(counts)
    assert result == {'T1': 20.0, 'T2': 60.0, 'T3': 20.0}
```

**CHECKPOINT 4**: Run `just test tests/test_rule_counter.py` (tests 1-8) → awaiting
approval

---

### Test Group 4: Marker Removal (3 tests)

#### Test 9: Remove basic markers

- **Given**: `"[RULE] Text here"`
- **When**: Remove markers
- **Then**: Returns `"Text here"`

**NEW code needed**:

- `remove_markers(content: str) -> str` function
- Regex to replace `[RULE]` with empty string
- Preserve remaining text

**Does NOT need**:

- Tier marker removal
- Whitespace normalization

**Test code**:

```python
def test_remove_markers_basic():
    content = "[RULE] Text here"
    result = remove_markers(content)
    assert result == "Text here"
```

---

#### Test 10: Remove tier markers

- **Given**: `"[RULE:T1] ⚠️ Critical text\n[RULE:T2] Important text"`
- **When**: Remove markers
- **Then**: Returns `"⚠️ Critical text\nImportant text"`

**NEW code needed**:

- Regex to match `[RULE:T1]`, `[RULE:T2]`, `[RULE:T3]`
- Remove all tier variants

**Does NOT need**:

- Validation that all markers removed

**Test code**:

```python
def test_remove_markers_tiers():
    content = "[RULE:T1] ⚠️ Critical text\n[RULE:T2] Important text"
    result = remove_markers(content)
    assert result == "⚠️ Critical text\nImportant text"
```

---

#### Test 11: Remove markers in list context

**Given**:

```
- [RULE:T1] First item
- [RULE:T2] Second item
```

- **When**: Remove markers
- **Then**: Returns:

```
- First item
- Second item
```

**NEW code needed**:

- Handle markers after list symbols
- Preserve list formatting

**Does NOT need**:

- Complex markdown parsing

**Test code**:

```python
def test_remove_markers_in_lists():
    content = "- [RULE:T1] First item\n- [RULE:T2] Second item"
    result = remove_markers(content)
    assert result == "- First item\n- Second item"
```

**CHECKPOINT 5**: Run `just test tests/test_rule_counter.py` (tests 1-11) → awaiting
approval

---

### Test Group 5: Validation (2 tests)

#### Test 12: Validate no markers remain

- **Given**: `"Text with no markers"`
- **When**: Validate removal
- **Then**: Returns `True`

**NEW code needed**:

- `validate_removal(content: str) -> bool` function
- Check for presence of `[RULE` substring
- Return `False` if any markers found

**Does NOT need**:

- Complex validation
- Error messages

**Test code**:

```python
def test_validate_removal_clean():
    content = "Text with no markers"
    result = validate_removal(content)
    assert result is True
```

---

#### Test 13: Validate detects remaining markers

- **Given**: `"Text with [RULE:T1] marker still present"`
- **When**: Validate removal
- **Then**: Returns `False`

**NEW code needed**:

- Detection of incomplete removal

**Test code**:

```python
def test_validate_removal_has_markers():
    content = "Text with [RULE:T1] marker still present"
    result = validate_removal(content)
    assert result is False
```

**CHECKPOINT 6**: Run `just test tests/test_rule_counter.py` (all 13 tests) → awaiting
approval

---

### Test Group 6: Integration (1 test)

#### Test 14: Full workflow from file

**Given**: File `agents/modules/gen/checkpoint-obedience.weak.opus.md` (from Phase 1.1)
**When**:

1. Read file → $content
2. Count rules → $counts
3. Calculate distribution → $distribution
4. Remove markers → $clean_content
5. Validate removal → $is_clean

**Then**:

- $counts['total'] is 12-16
- $distribution is close to `{'T1': 20.0, 'T2': 60.0, 'T3': 20.0}`
- $is_clean is `True`

**NEW code needed**:

- Integration of all functions
- File I/O

**Test code**:

```python
def test_full_workflow():
    # Load generated variant from Phase 1.1
    with open('agents/modules/gen/checkpoint-obedience.weak.opus.md') as f:
        content = f.read()

    # Count rules
    counts = count_rules(content)
    assert 12 <= counts['total'] <= 16, f"Expected 12-16 rules, got {counts['total']}"

    # Check distribution
    distribution = calculate_distribution(counts)
    # Allow ±10 percentage points deviation
    assert 10 <= distribution['T1'] <= 30
    assert 50 <= distribution['T2'] <= 70
    assert 10 <= distribution['T3'] <= 30

    # Remove markers
    clean_content = remove_markers(content)

    # Validate
    is_clean = validate_removal(clean_content)
    assert is_clean is True
```

**CHECKPOINT 7**: Run `just test tests/test_rule_counter.py` (all 14 tests) → awaiting
approval

---

## Phase 1.3: Directory Structure

**Status**: ✅ COMPLETE - directories already exist

**Verification step**:

1. Run `ls -la agents/modules/` → verify `src/` and `gen/` exist
2. Run `ls -la agents/modules/src/` → verify 14 `.semantic.md` files exist
3. Run `ls -la agents/modules/gen/` → verify contains Sonnet and Opus variants from
   Phase 1.1

**CHECKPOINT 8**: Directory structure verified → Phase 1 complete

---

## Success Criteria - Phase 1

- [ ] Sonnet variant generated: `agents/modules/gen/checkpoint-obedience.weak.sonnet.md`
- [ ] Opus variant generated: `agents/modules/gen/checkpoint-obedience.weak.opus.md`
- [ ] Comparison report created: `plans/comparison-sonnet-vs-opus.md`
- [ ] User decision made: Sonnet or Opus for variant generation
- [ ] Rule counter implemented: `src/claudeutils/module_system/rule_counter.py`
- [ ] All 14 tests pass: `just test tests/test_rule_counter.py`
- [ ] Functions implemented:
  - `count_rules(content: str) -> dict`
  - `calculate_distribution(counts: dict) -> dict`
  - `remove_markers(content: str) -> str`
  - `validate_removal(content: str) -> bool`
- [ ] Directory structure verified: `agents/modules/src/` and `agents/modules/gen/`
      exist

---

## Execution Order

1. **Phase 1.1**: Generate variants (manual LLM invocation required - NOT test-driven)
2. **STOP**: User reviews comparison, decides on model
3. **Phase 1.2**: Implement rule counter (TDD with 14 tests, 7 checkpoints)
4. **Phase 1.3**: Verify directory structure (simple verification)

---

## Notes for Code Role Agent

- **Phase 1.1 is NOT TDD** - requires manual LLM API calls (Anthropic SDK)
- **Phase 1.2 IS TDD** - follow red-green-refactor strictly
- **Stop at every checkpoint** - wait for explicit "continue"
- **No scope creep** - implement only what each test requires
- Test order matters - each builds on previous
- Use `pytest` for all tests
- Type hints required (`mypy --strict` must pass)
- `ruff` must pass (no linting errors)

---

**END OF PLAN**
