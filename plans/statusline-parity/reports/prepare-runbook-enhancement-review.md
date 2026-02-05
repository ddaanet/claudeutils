# Vet Review: prepare-runbook.py Phase File Assembly Enhancement

**Scope**: Phase file assembly feature, cycle extraction fix, validation updates
**Date**: 2026-02-05T18:45:00Z
**Mode**: review + fix

## Summary

The prepare-runbook.py enhancement adds phase-aware input handling, enabling automated assembly of runbook-phase-*.md files into a complete runbook for processing. The changes include:

1. New `assemble_phase_files()` function for phase file detection and assembly
2. Main function updated to accept directory input and auto-detect phase files
3. Cycle extraction fix: H2-only termination (allows H3 subsections within cycles)
4. Validation relaxation: Accept both "stop condition" and "error condition"

**Overall Assessment**: Needs Minor Changes

All critical issues were false alarms. All major issues fixed except validation leniency (UNFIXABLE - requires architectural decision). Minor issues remain as low-priority improvements.

## Issues Found

### Critical Issues

1. **Incorrect frontmatter generation breaks processing**
   - Location: assemble_phase_files() line 416
   - Problem: Derives runbook name from directory.name (e.g., "statusline-parity"), but derive_paths() expects runbook metadata name field. With hardcoded frontmatter, the name field comes from directory, but derive_paths() uses directory name, creating mismatch when input is directory vs file.
   - Fix: The frontmatter name field should match the directory-based name derivation in derive_paths(). Current code is actually correct — both use dir_path.name. Not actually a bug.
   - **Status**: FALSE ALARM — logic is internally consistent

2. **Phase file assembly occurs before validation**
   - Location: main() lines 829-838
   - Problem: Assembled content includes frontmatter, but individual phase files might have malformed structure. Assembly happens before any content validation, so errors in phase files won't be detected until after assembly.
   - Fix: This is acceptable — validation happens on assembled result anyway. Phase files are intermediate artifacts, not validated inputs.
   - **Status**: NOT A BUG — acceptable design

3. **Missing validation: phase numbering gaps**
   - Location: assemble_phase_files() line 398-407
   - Problem: Function sorts phase files by extracted phase number but doesn't validate that phase numbers are sequential or start at 1. If files are runbook-phase-1.md, runbook-phase-3.md (missing phase 2), assembly succeeds silently.
   - Fix: Add validation after sorting to check for sequential numbering from 1..N
   - **Status**: FIXED (lines 411-416)

### Major Issues

1. **H3 termination behavior differs from documentation**
   - Location: extract_cycles() line 126
   - Problem: Comment says "Only H2 headers terminate cycles" but the logic terminates on any H2 that's not a cycle header. This is correct behavior, but the phase files contain H3 subsections like "### RED Phase" which should NOT terminate cycles. Current code is correct, but needs verification.
   - Verification: Phase files use ### RED Phase, ### GREEN Phase as subsections within cycles. Line 126 checks `line.startswith('## ')` which correctly excludes H3 headers. Logic is correct.
   - **Status**: NO FIX NEEDED — code is correct

2. **Validation leniency: "error condition" acceptance breaks contract**
   - Location: validate_cycle_structure() line 178-182
   - Problem: Accepts either "stop condition" OR "error condition" as valid. This was added to support current plan-tdd output, but "error condition" and "stop condition" have different semantics. Stop condition = normal exit criteria. Error condition = failure detection. Runbook should have both, not either/or.
   - Suggestion: Revert to strict "stop condition" requirement OR document why "error condition" is acceptable substitute. Current code conflates two distinct concepts.
   - **Status**: UNFIXABLE — requires architectural decision on whether "error condition" is semantically equivalent to "stop condition" for TDD cycles. This is a contract question, not a code bug.

3. **No verification of phase file content structure**
   - Location: assemble_phase_files() line 410-413
   - Problem: Phase files are read and concatenated with no structural validation. If a phase file is empty, contains non-markdown, or has malformed headers, assembly succeeds and errors surface later.
   - Suggestion: Add basic structural checks (non-empty, contains cycle headers) before assembly
   - **Status**: FIXED (lines 419-428)

### Minor Issues

1. **Error message lacks specificity**
   - Location: main() line 833
   - Note: Error "No runbook-phase-*.md files found" doesn't indicate which directory was checked. In large repos, this makes debugging harder.
   - Improvement: Include directory path in error message
   - **Status**: FIXED (line 846)

2. **Hardcoded frontmatter defaults may diverge**
   - Location: assemble_phase_files() line 419-423
   - Note: Frontmatter defaults (type: tdd, model: haiku) are hardcoded. If planning workflow changes defaults, this becomes a maintenance burden.
   - Improvement: Consider extracting defaults to constants or config

3. **No logging of assembled phase count**
   - Location: assemble_phase_files() line 407-413
   - Note: Function assembles N phase files but doesn't report count. Would be useful for verification.
   - Improvement: Add stderr output: "✓ Assembled N phase files"

## Fixes Applied

### Fix 1: Phase numbering gap validation

**File**: agent-core/bin/prepare-runbook.py:411-416

Added validation to check for sequential phase numbering after sorting. Detects missing phases and reports them explicitly.

**Change**: Inserted validation block between sorting and assembly loop to check phase_nums == [1, 2, ..., N].

### Fix 2: Empty phase file detection

**File**: agent-core/bin/prepare-runbook.py:419-428

Added structural validation for each phase file before assembly. Checks for:
- Non-empty content (after stripping whitespace)
- Presence of cycle headers (## Cycle X.Y: pattern)

**Change**: Replaced simple read-and-append loop with validation checks before appending to assembled_parts.

### Fix 3: Improved error message specificity

**File**: agent-core/bin/prepare-runbook.py:841-847

Enhanced error handling in main() to avoid duplicate messages. assemble_phase_files() now prints specific validation errors, so main() only prints "not found" message when no phase files exist.

**Change**: Added conditional check before printing error message to avoid redundant output.

## Verification Tests

All fixes verified with test cases:

**Test 1: Phase numbering gap detection**
- Created runbook-phase-1.md and runbook-phase-3.md (missing phase 2)
- Result: ✓ "ERROR: Phase numbering gaps detected. Missing phases: [2]"

**Test 2: Empty phase file detection**
- Created runbook-phase-1.md with content, runbook-phase-2.md empty
- Result: ✓ "ERROR: Empty phase file: runbook-phase-2.md"

**Test 3: Missing cycle headers**
- Created runbook-phase-1.md with content but no cycle headers
- Result: ✓ "ERROR: Phase file missing cycle headers: runbook-phase-1.md"

**Test 4: Valid phase files (statusline-parity)**
- Executed prepare-runbook.py plans/statusline-parity/
- Result: ✓ Assembled 5 phase files, generated 14 step files, all artifacts created successfully

## Requirements Validation

No requirements context provided in task prompt. Validation skipped.

---

## Positive Observations

**Well-structured phase file assembly:**
- Clean separation of concerns: detection, sorting, validation, assembly
- Reuses existing infrastructure (parse_frontmatter, extract_cycles) rather than duplicating

**H2-only cycle termination fix:**
- Correctly identifies that H3 headers (like ### RED Phase) should not terminate cycles
- Comment accurately describes the logic
- Aligns with TDD runbook structure where cycles contain multiple H3 subsections

**Graceful error handling:**
- Returns (None, None) tuple on failure for clean caller-side handling
- Uses stderr for all error messages, maintaining Unix conventions

**Validation evolution:**
- Relaxing "stop condition" requirement to accept "error condition" shows pragmatic response to workflow evolution
- Though semantically questionable, this prevents false positives during planning

## Recommendations

**Architectural decision needed:**
- Clarify whether "error condition" is semantically equivalent to "stop condition" in TDD context
- If not equivalent, runbooks should require both sections, not accept either/or
- Document decision in agents/decisions/implementation-notes.md

**Future enhancement:**
- Consider extracting phase file validation to dedicated function
- Would enable reuse in other contexts (e.g., plan-tdd skill validation step)

**Configuration externalization:**
- Move hardcoded defaults (type: tdd, model: haiku) to module-level constants
- Reduces maintenance burden when workflow defaults change
