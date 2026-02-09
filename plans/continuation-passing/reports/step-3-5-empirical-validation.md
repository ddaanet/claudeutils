# Step 3.5: Empirical Validation Report

**Date:** 2026-02-09
**Objective:** Validate continuation parser accuracy against real session corpus (FR-5, D-7)

## Methodology

**Corpus:** `~/.claude/projects/*/` session transcripts (2791 files)

**Sample:**
- Extracted 2814 unique user prompts containing `/`
- Analyzed sample of 200 prompts
- Ran parser with 3-skill registry (commit, handoff, orchestrate)

**Classification:**
- **TRUE POSITIVE (TP):** Skill reference correctly identified as invocation/continuation
- **FALSE POSITIVE (FP):** Skill mentioned but not as invocation (meta-discussion, paths, output)
- **FALSE NEGATIVE (FN):** Explicit skill invocation missed by parser

## Results

### Detection Metrics

| Metric | Count | Rate |
|--------|-------|------|
| Total sample | 200 | 100% |
| Detections | 30 | 15% |
| True Positive | 1 | 3.3% of detections |
| False Positive | 26 | 86.7% of detections |
| Needs Review | 3 | 10% of detections |
| False Negative | 0 | 0% (no missed invocations found) |

### False Positive Analysis

**Critical Finding:** Parser triggers on skill references in contexts where continuation should NOT apply.

**False Positive Categories:**

1. **Meta-discussion (8 cases, 31%):**
   - "Remember to use the /commit skill"
   - "update CLAUDE.md: directive to use /commit skill"
   - "Execute step from: plans/.../step-X.md" (instructional context)

2. **File paths (11 cases, 42%):**
   - Prompts containing `plans/`, `steps/`, `.md` with skill references
   - Example: "Review the memory index update implementation" (mentions /commit in file content)

3. **Command output (7 cases, 27%):**
   - `<command-message>commit</command-message>` (XML/structured output)
   - `<bash-stdout>` containing skill names
   - `<local-command-stdout>` with context markers

### False Negative Analysis

**Finding:** No false negatives detected in sample.

- Scanned 170 non-detections for skill-like patterns
- No prompts starting with `/design`, `/plan`, `/commit`, `/handoff`, or `/orchestrate` were missed
- Parser correctly identifies direct skill invocations

## Compliance Assessment

**Target Metrics (from requirements):**

| Requirement | Target | Actual | Status |
|-------------|--------|--------|--------|
| False Positive Rate | 0% (critical) | **86.7%** | ❌ **FAILED** |
| False Negative Rate | <5% (acceptable) | 0% | ✅ **PASSED** |

### Failure Analysis

**Root Cause:** Parser uses simple `/\w+` regex pattern to detect skill references without context awareness.

**Impact:**
- **Critical:** False positives corrupt skill args (FR-5 violation)
- When user discusses skills in prose, parser injects continuation into args
- Example: "Remember to use /commit skill" → detected as invocation → wrong continuation appended

**Why False Negatives Are Acceptable:**
- 0% FN rate: Parser catches all actual invocations
- Missing edge cases: User can retype (low cost)
- Asymmetric risk: FP corrupts execution, FN just requires retry

## Recommendations

### Immediate Fixes Required

1. **Context-Aware Detection:**
   - Exclude skill references inside meta-markers: `<command-`, `<bash-`, `<local-`
   - Exclude prose contexts: "use /skill", "Remember to /skill", "directive to /skill"
   - Exclude file paths: prompts containing `plans/`, `steps/`, `.md` before skill reference

2. **Invocation Heuristics:**
   - TRUE: Prompt starts with `/skill` (direct invocation)
   - TRUE: Contains ` and /skill` or `and\n- /skill` (continuation syntax)
   - FALSE: Skill reference not at prompt start and no continuation markers
   - FALSE: Skill reference in quoted/escaped context

3. **Conservative Approach:**
   - Only detect continuations in unambiguous invocation contexts
   - When in doubt, pass through (no detection)
   - Prefer FN over FP (user retypes vs. corrupted execution)

### Test Coverage Gaps

**Current unit tests (from Step 3.2) are insufficient:**
- Focus on happy path continuation syntax
- Missing negative test cases for:
  - Meta-discussion contexts
  - File paths with skill names
  - Command output containing skills
  - Prose mentions of skills

**Required test additions:**
```python
# Negative cases: should return None (no continuation)
assert parse_continuation("Remember to use /commit skill", registry) is None
assert parse_continuation("Execute step from: plans/.../step.md", registry) is None
assert parse_continuation("<command-name>/commit</command-name>", registry) is None
assert parse_continuation("Review /path/to/commit.md", registry) is None
```

## Conclusion

**Status:** ❌ **FAILED empirical validation**

**Critical Issue:** 86.7% false positive rate violates FR-5 requirement (prose-to-explicit translation must be accurate).

**Blocker:** Parser implementation (Step 1.3) requires fixes before proceeding to Phase 2 (skill integration).

**Next Steps:**
1. Fix parser to exclude false positive contexts (enhance Step 1.3 implementation)
2. Add negative test cases (enhance Step 3.2 tests)
3. Re-run empirical validation (repeat Step 3.5)
4. Proceed to Phase 2 only after FP rate < 5%

---

**Execution Model:** Sonnet
**Phase:** 1 - Hook Implementation
