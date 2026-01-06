# Debug Scripts for Idempotency Bug Investigation

**Created:** 2026-01-06
**Context:** Investigation of `escape_inline_backticks()` idempotency failure

## Purpose

These scripts demonstrate that the `escape_inline_backticks()` function in `src/claudeutils/markdown.py` is NOT idempotent - running it multiple times on the same input produces different (corrupted) output.

## Key Scripts

### Core Problem Demonstration

- **test_idempotent.py** - Shows progressive corruption over 3 passes
- **test_better_approach.py** - Compares broken (v1) vs fixed (v2) approaches
- **test_escape_regex.py** - Tests regex behavior in isolation

### Context-Specific Tests

- **test_segments.py** - Tests segment parsing on actual file content
- **test_bare_fence.py** - Tests bare fence protection
- **test_process.py** - Full processing pipeline on real file

### Regex Analysis

- **test_fixed_regex.py** - Tests proposed regex fix (unsuccessful)
- **test_escape.py** - Additional escape pattern testing

## The Bug

**Current Regex:** `(?<!`` )(`{3,})(\w*)(?! ``)`

**Problem:** After wrapping `` `````markdown `` as `` `` `````markdown `` ``, the regex matches INSIDE the already-escaped sequence starting from the 2nd backtick.

**Evidence:**
```
Pass 1: `````markdown           → `` `````markdown ``        ✓
Pass 2: `` `````markdown ``     → `` ``` ````markdow``n ``  ❌
Pass 3: `` ``` ````markdow``n `` → (continues corruption)    ❌
```

## Running the Scripts

Most scripts can be run directly:
```bash
python3 plans/markdown/debug/test_idempotent.py
python3 plans/markdown/debug/test_better_approach.py
python3 plans/markdown/debug/test_escape_regex.py
```

Some scripts require module imports and may need adjustments to import paths.

## Solution Status

**Band-aid fix attempted:** Skip lines that already contain ```` `` `{3,} ````
**Status:** Works but unsatisfying - patches symptom, not cause
**Proper fix needed:** Redesign regex to be truly idempotent
