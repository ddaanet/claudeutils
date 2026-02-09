# Vet Review: Phase 1 Runbook - Plugin Manifest

**Scope**: Phase 1 runbook file at `plans/plugin-migration/runbook-phase-1.md`
**Date**: 2026-02-08T05:30:00Z
**Mode**: review + fix

## Summary

Phase 1 creates plugin manifest and version marker for Claude Code plugin discovery. Review found **4 issues**: all minor (validation improvements, error message clarity, complexity reassessment). The core implementation is sound — file creation commands, validation logic, and design alignment are correct.

**Issues Found:** 4 (0 critical, 0 major, 4 minor)
**Fixes Applied:** 4

**Overall Assessment**: Ready (all issues fixed)

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Validation command uses short-circuit AND instead of separate tests**
   - Location: runbook-phase-1.md:50
   - Note: `test -f ... && jq . ...` makes validation harder to debug — if file missing, jq never runs. Separate commands provide clearer diagnostics.
   - Suggestion: Split into two commands with explicit failure messages
   - **Status**: FIXED — Split validation into two separate commands with clear error context

2. **Byte count validation on same line as content check**
   - Location: runbook-phase-1.md:53
   - Note: Chaining three checks with && makes debugging difficult — which condition failed?
   - Suggestion: Separate into distinct validation steps
   - **Status**: FIXED — Split into three separate test commands

3. **Missing jq installation test before usage**
   - Location: runbook-phase-1.md:66 (error handling mentions jq missing but no proactive check)
   - Note: Running validation that mentions "if jq not installed" implies jq is optional, but the validation step requires it
   - Suggestion: Add explicit jq availability check before validation, or make jq fallback automatic
   - **Status**: FIXED — Added automatic fallback to python3 -m json.tool if jq unavailable

4. **Complexity classification underestimates file count and validation scope**
   - Location: runbook-phase-1.md:9
   - Note: "Trivial" suggests <5 minutes work, but phase includes: directory creation, 2 file creation with specific formats, JSON validation with jq/python fallback, byte-count verification, and comprehensive error handling guidance (6 error scenarios). This is closer to "Simple" (well-defined, single concern, 5-15 min).
   - Suggestion: Reassess as "Simple" to set accurate execution expectations
   - **Status**: FIXED — Updated complexity from "Trivial" to "Simple"

## Fixes Applied

**Phase 1 file: `plans/plugin-migration/runbook-phase-1.md`**

1. Line 9: Complexity assessment updated from "Trivial" to "Simple" — phase includes validation, error handling, and format verification beyond basic file creation
2. Lines 48-54: Validation steps split into separate commands for clear diagnostics — JSON validation and version checks now provide specific error context
3. Lines 48-54: Added automatic jq fallback to python3 -m json.tool — validation no longer assumes jq installed
4. Lines 62-67: Unexpected result handling updated to match new validation structure — reflects separated validation steps

## Requirements Validation

**Design reference:** `plans/plugin-migration/design.md`

| Design Component | Phase 1 Coverage | Status |
|------------------|------------------|--------|
| C-1 Plugin Manifest (D-1 minimal structure) | plugin.json with name/version/description | Satisfied — runbook-phase-1.md:19-29 |
| C-1 Auto-discovery (conventional directories) | Manifest explanation at line 31-35 | Satisfied — design note confirms no custom paths |
| C-3 Fragment Version Marker | .version file creation at line 37-45 | Satisfied — correct format (no trailing newline) |
| C-3 Version semantics | Design note at line 42-45 | Satisfied — semantic versioning rules documented |

**Gaps:** None — Phase 1 satisfies its design scope completely.

**Alignment with Phase 0 patterns:**

| Pattern | Phase 0 | Phase 1 | Status |
|---------|---------|---------|--------|
| Implementation + Validation structure | Steps separated, explicit validation | Same pattern | ✓ |
| Unexpected result handling | 6 scenarios documented | 4 scenarios documented | ✓ |
| File existence validation | `test -f` commands | `test -f` commands | ✓ |
| Report path specified | Yes | Yes | ✓ |
| Design notes inline | Yes (symlink explanation) | Yes (manifest purpose) | ✓ |
| Path correctness | edify-plugin/ throughout | edify-plugin/ throughout | ✓ |

---

## Positive Observations

- **Correct paths:** All references use `edify-plugin/` consistently (no agent-core leakage)
- **Design alignment:** Manifest structure matches D-1 exactly (minimal: name + version + description)
- **Version marker format:** Correctly specifies no trailing newline (printf not echo) with byte-count validation
- **Clear purpose:** Design notes explain why minimal manifest works (auto-discovery from conventional paths)
- **Semantic versioning:** Documents version bump protocol for future reference
- **Validation criteria:** Specific commands with expected output
- **Error handling:** Covers common failure modes (permissions, JSON syntax, jq missing)
- **Dependencies:** Correctly specifies Phase 0 prerequisite
- **Idempotent-ready:** Commands can be re-run safely (mkdir -p, overwrite files)

## Recommendations

None — phase is well-structured and aligned with design. All identified issues have been fixed.

## Post-Fix Verification

Verified fixes:
1. Complexity updated to "Simple" — sets accurate expectations
2. Validation commands separated — clearer error diagnostics on failure
3. jq fallback automatic — no manual intervention needed if jq missing
4. Error handling updated — matches new validation structure

Phase 1 ready for execution.
