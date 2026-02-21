# Runbook Review: hook-batch Phase 3

**Artifact**: `plans/hook-batch/runbook-phase-3.md`
**Date**: 2026-02-21T00:00:00Z
**Mode**: review + fix-all
**Phase types**: General (2 steps)

## Summary

Phase 3 is a focused general phase: one creation step (Step 3.1) and one validation step (Step 3.2). Both steps are well-structured with Objective, Implementation, Expected Outcome, and Error Conditions. Two issues found — one critical (non-existent file reference) and one major (ambiguous error-handling instruction) — both fixed.

**Overall Assessment**: Ready

## Findings

### Critical Issues

1. **Non-existent file reference in Step 3.1 Test 4**
   - Location: Step 3.1, Validation block, Test 4
   - Problem: `agent-core/hooks/pretooluse-recipe-redirect.py` does not exist. No hook file by that name exists in `agent-core/hooks/`. Executor would receive a JSON payload pointing to a missing file, making the test meaningless.
   - Fix: Replaced with `agent-core/hooks/userpromptsubmit-shortcuts.py` — an existing Python hook in the same directory that is ruff-formattable.
   - **Status**: FIXED

### Major Issues

1. **Ambiguous error-handling instruction in Step 3.1 item 8**
   - Location: Step 3.1, Implementation, item 8
   - Problem: "wrap ruff calls in `|| true` equivalent using `2>&1` redirect or explicit error capture" conflates three distinct mechanisms: `|| true` (exit code suppression), `2>&1` (stderr→stdout redirect), and error capture (subshell). An executor following this literally could wrap ruff in `|| true`, silencing real ruff failures (malformed Python, file-not-found). This contradicts the Error Conditions clause "ruff not available → log to stderr, exit 0" — the `command -v ruff` guard at the start handles unavailability; the ruff calls themselves should propagate errors. Only docformatter (explicitly optional) needs `|| true`.
   - Fix: Replaced with explicit split: ruff calls run normally under `set -euo pipefail`; docformatter call uses `|| true` because it is optional.
   - **Status**: FIXED

### Minor Issues

None.

## Fixes Applied

- Step 3.1 Test 4: `pretooluse-recipe-redirect.py` → `userpromptsubmit-shortcuts.py` (file exists)
- Step 3.1 item 8: Replaced ambiguous `|| true` equivalence language with explicit per-call guidance (ruff normal, docformatter `|| true`)

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
