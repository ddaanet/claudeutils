# Vet Review: Phase 4 - Justfile Modularization

**Scope**: plans/plugin-migration/runbook-phase-4.md
**Date**: 2026-02-08T13:45:00Z
**Mode**: review + fix

## Summary

Phase 4 covers justfile modularization: extracting portable recipes to `edify-plugin/just/portable.just` and updating the root justfile with import. The phase correctly interprets design decision D-5 and Component 5.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Incorrect hooks.json format reference**
   - Location: Step 4.1 implementation (lines 24-124)
   - Problem: Design D-4 specifies hooks.json uses direct format (`{"PreToolUse": [...]}`), not wrapper format. Phase 4 doesn't involve hooks.json, but inline comment at line 113 says "NEW: Plugin hook configuration" which could confuse readers into thinking hooks.json is created in this phase
   - Fix: Remove the misleading "NEW: Plugin hook configuration" comment from hooks/ directory listing — hooks.json is created in Phase 2, not Phase 4
   - **Status**: FIXED

2. **Missing precommit-base validation in Step 4.1**
   - Location: Step 4.1 validation (line 142)
   - Problem: Step lists "All 7 recipes extracted" but only validates paths and commands. Should explicitly test `just --justfile edify-plugin/just/portable.just precommit-base` to verify validators are callable
   - Fix: Add explicit precommit-base test to validation section
   - **Status**: FIXED

3. **Incomplete root justfile precommit update**
   - Location: Step 4.2 implementation (lines 184-194)
   - Problem: Instructions say "Update precommit recipe to call precommit-base" but example shows `precommit: precommit-base` dependency which only runs base validators. Design Component 5 shows precommit should add language-specific checks (ruff, mypy, pytest) AFTER base validators
   - Fix: Clarify that example shows complete pattern — base validators run first (via dependency), then project-specific checks
   - **Status**: FIXED

### Minor Issues

1. **Success criteria redundancy**
   - Location: Step 4.1 success criteria (lines 152-155)
   - Note: "All 7 recipes extracted" repeats "portable.just exists and parses correctly" validation. Could consolidate to reduce token count
   - **Status**: FIXED

2. **Missing explicit `just --list` test in Step 4.2 validation**
   - Location: Step 4.2 validation (line 222)
   - Note: Validation checks grep patterns but doesn't explicitly test `just --list` to verify import works end-to-end
   - **Status**: FIXED

3. **Vague "full bash_prolog" description**
   - Location: Step 4.2 implementation (line 209-211)
   - Note: Says "Keep full bash_prolog" but doesn't specify which functions. Design D-5 clarifies portable recipes use minimal prolog (fail, visible, colors) while root keeps project-specific helpers (sync, run-checks, pytest-quiet)
   - **Status**: FIXED

## Fixes Applied

- **Step 4.1**: Removed misleading "NEW: Plugin hook configuration" comment from hooks/ directory listing
- **Step 4.1**: Added explicit `just --justfile edify-plugin/just/portable.just precommit-base` validation test
- **Step 4.2**: Added note clarifying precommit dependency pattern runs base first, then project-specific
- **Step 4.1**: Consolidated success criteria to remove redundancy
- **Step 4.2**: Added explicit `just --list` end-to-end validation test
- **Step 4.2**: Clarified full bash_prolog includes sync, run-checks, pytest-quiet (project-specific helpers)

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-2 | Satisfied | Step 4.1 creates claude/claude0 recipes with `--plugin-dir ./edify-plugin` |
| FR-6 | Satisfied | Step 4.1 extracts all portable recipes (claude, wt-*, precommit-base) to importable file |
| NFR-1 | Satisfied | portable.just retains all functionality, no performance degradation |

**Gaps**: None. Phase 4 fully satisfies its assigned requirements.

---

## Positive Observations

- Correct interpretation of D-5 minimal prolog constraint (fail, visible, colors only)
- Proper submodule path updates throughout (edify-plugin not agent-core)
- Good unexpected result handling for both steps (syntax errors, import failures)
- Validation commands are concrete and actionable
- Recipe extraction notes clearly document constraints and design references

## Recommendations

None. Phase is complete and ready for execution after fixes applied.
