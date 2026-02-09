# Vet Review: Phase 6 — Cache Regeneration

**Scope**: `plans/plugin-migration/runbook-phase-6.md`
**Date**: 2026-02-08
**Mode**: review + fix

## Summary

**Overall Assessment**: Needs Minor Changes

Phase 6 addresses cache regeneration after justfile changes in Phase 4 and Phase 5. Review found 3 issues:
- 1 Critical: Incorrect cache filename reference
- 1 Major: Missing cache filename update in documentation
- 1 Minor: grep command pattern could be clearer

## Issues Found

### Critical Issues

1. **Wrong cache filename in documentation**
   - Location: phase-6.md:26 (in Implementation section)
   - Problem: References `.cache/just-help-edify-plugin.txt` but current filename is `.cache/just-help-agent-core.txt`
   - Fix: Update filename to match current state (agent-core → edify-plugin rename happens in Phase 0)
   - **Status**: FIXED

### Major Issues

1. **Cache filename inconsistency in Expected Outcome**
   - Location: phase-6.md:51
   - Problem: References `.cache/just-help-edify-plugin.txt` while line 26 references same cache with wrong name
   - Suggestion: Ensure consistent naming after critical issue fixed
   - **Status**: FIXED

### Minor Issues

1. **grep pattern could be more explicit**
   - Location: phase-6.md:37
   - Note: Pattern `grep -E "(claude|wt-new|wt-ls|wt-rm|wt-merge|precommit-base)"` could explicitly anchor to line starts to avoid false matches in recipe descriptions
   - **Status**: FIXED

## Fixes Applied

- phase-6.md:15 — Changed `.cache/just-help-edify-plugin.txt` to `.cache/just-help-agent-core.txt` in Objective
- phase-6.md:26 — Changed `.cache/just-help-edify-plugin.txt` to `.cache/just-help-agent-core.txt` (current filename)
- phase-6.md:44 — Changed `.cache/just-help-edify-plugin.txt` to `.cache/just-help-agent-core.txt` in validation command
- phase-6.md:51 — Changed `.cache/just-help-edify-plugin.txt` to `.cache/just-help-agent-core.txt` for consistency
- phase-6.md:61 — Changed `.cache/just-help-edify-plugin.txt` to `.cache/just-help-agent-core.txt` for consistency
- phase-6.md:78 — Changed `.cache/just-help-edify-plugin.txt` to `.cache/just-help-agent-core.txt` in Affected Files
- phase-6.md:37 — Changed grep pattern to anchor to line start: `grep -E "^[[:space:]]+(claude|wt-new|wt-ls|wt-rm|wt-merge|precommit-base)"`

## Requirements Validation

**Design alignment:**

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Cache regeneration after justfile changes | Satisfied | Step 6.1 uses `just cache` command |
| Root cache includes imported recipes | Satisfied | Validation checks for imported recipe names |
| Edify-plugin cache excludes sync-to-parent | Satisfied | Validation checks sync-to-parent NOT present |
| CLAUDE.md @ references remain valid | Satisfied | Success criteria includes "CLAUDE.md @ references resolve" |

**Dependencies:**
- Phase 4 prerequisite correctly identified (justfile import changes output)
- Phase 5 prerequisite correctly identified (sync-to-parent removal)

**Validation strategy:**
- Cache content verification with grep checks (imported recipes present, sync-to-parent absent)
- Timestamp verification (files updated after command)
- @ reference integrity check

**Gaps:** None identified.

---

## Positive Observations

- Comprehensive validation strategy covering both cache files
- Clear explanation of `just cache` behavior (calls Makefile target)
- Proper prerequisite identification (Phases 4 and 5)
- Unexpected result handling addresses common failure scenarios
- Success criteria explicitly includes CLAUDE.md @ reference integrity

## Recommendations

None. Phase 6 is well-structured and complete after fixes applied.
