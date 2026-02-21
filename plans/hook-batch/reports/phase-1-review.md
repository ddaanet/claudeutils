# Runbook Review: Phase 1 — UserPromptSubmit Improvements

**Artifact**: `plans/hook-batch/runbook-phase-1.md`
**Date**: 2026-02-21T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (5 cycles)

## Summary

Phase 1 covers 5 TDD cycles for `userpromptsubmit-shortcuts.py`: line-based shortcut matching, COMMANDS string updates, additive directive scanning (D-7), new directives (p:/b:/q:/learn:), and pattern guards (Tier 2.5). All file references verified against disk. RED phase assertions are behaviorally specific and will fail against current implementation for the correct reasons. GREEN phases describe behavior with hints, no prescriptive code.

**Overall Assessment**: Ready

**Issues found**: 0 critical, 0 major, 1 minor
**Issues fixed**: 1
**Unfixable**: 0

## Minor Issues

### Issue 1: Deferred assertion decision in Cycle 1.3 GREEN
**Location**: Cycle 1.3, GREEN Phase, Changes section for `tests/test_userpromptsubmit_shortcuts.py`
**Problem**: Update instruction said `assert "[DISCUSS]" AND "[PENDING]" in systemMessage (or change assertion to verify both directives fired)` — the "or" alternative left the specific assertion form as a decision for the executor.
**Fix**: Resolved to: assert both `"[DISCUSS]"` AND `"[PENDING]"` appear in `output_multi["systemMessage"]` (two separate `assert ... in` statements). Removes the ambiguous alternative.
**Status**: FIXED

## File Reference Validation

All paths verified against disk:
- `agent-core/hooks/userpromptsubmit-shortcuts.py` — exists, 839 lines ✓
- `tests/test_userpromptsubmit_shortcuts.py` — exists, 282 lines ✓
- `plans/hook-batch/outline.md` — exists ✓
- `plans/hook-batch/userpromptsubmit-plan.md` — exists ✓

All line-number references verified against source:
- `if prompt in COMMANDS` at line 772 ✓
- `scan_for_directive()` at lines 156-206 ✓
- `return (directive_key, match.group(2))` at line 204 ✓
- `main()` structure at lines 765-839 ✓
- Tier 2 block at lines 784-812, early return at line 812 ✓
- `test_any_line_matching` multi-directive section at lines 222-228, assertion at line 228 ✓
- `TestTier1Commands`, `TestAdditiveDirectives`, `TestNewDirectives`, `TestPatternGuards` — all new classes (no collision) ✓

## RED Phase Verification

**Cycle 1.1:** `call_hook("s\nsome additional context")` → `"s\nsome additional context"` is not in COMMANDS → `{}` → `result["hookSpecificOutput"]` raises KeyError. Fails correctly. ✓

**Cycle 1.2:** Current `r` expansion is `'[#resume] Continue in-progress task only. Error if no in-progress task exists.'` — no "conversation context", no "session.md". Current `xc` is `'[#execute --commit] Complete task...'` — the `does NOT contain "[#execute --commit]"` assertion fails because it IS present. Fails correctly. ✓

**Cycle 1.3:** `scan_for_directive()` returns on first match (line 204). Multi-directive prompt returns only DISCUSS. PENDING assertion fails. Fails correctly. ✓

**Cycle 1.4:** Current `p:` falls to `else` branch → systemMessage = full `_PENDING_EXPANSION` (well over 60 chars). `len < 60` assertion fails. `b:`, `q:`, `learn:` not in DIRECTIVES → `call_hook` returns `{}` → KeyError. Fails correctly. ✓

**Cycle 1.5:** No `EDIT_SKILL_PATTERN`, `CCG_PATTERN` constants; no Tier 2.5 block. Pattern guard prompts return `{}`. Fails correctly. ✓

## Fixes Applied

- Cycle 1.3 GREEN, Changes section — resolved ambiguous "or" alternative in test update instruction to specify two `assert ... in` statements

## Unfixable Issues (Escalation Required)

None — all issues fixed
