# Vet Review: Phase 3 Hook Migration Runbook

**Scope**: plans/plugin-migration/runbook-phase-3.md
**Date**: 2026-02-07T00:00:00Z

## Summary

Phase 3 runbook provides detailed implementation steps for hook migration, including creating plugin hook configuration, deleting obsolete symlink-redirect hook, and implementing version check functionality. The runbook is well-structured with clear validation steps, error conditions, and design alignment.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Wrapper format terminology confusion**
   - Location: Step 3.1, lines 93-94, 108
   - Problem: Runbook refers to "wrapper format required by plugin hooks" but uses incorrect terminology. The format shown (with `"description"` field) is the plugin.json wrapper format. The hooks.json file itself does NOT require the wrapper — it uses direct `{"hooks": {...}}` structure
   - Evidence: Design Component 2 shows hooks.json WITHOUT description wrapper at lines 113-165. The wrapper format is only for plugin.json when hooks are inline
   - Fix: Remove "wrapper format" references in Step 3.1. The hooks.json structure shown is correct, but the terminology is misleading. Change line 24 from "Workflow infrastructure hooks for edify plugin" to match design (no description field at all per D-4)
   - Suggestion: Clarify that this is the "plugin hooks.json format" not "wrapper format"

2. **hooks.json includes description field incorrectly**
   - Location: Step 3.1, lines 23-24
   - Problem: Implementation includes `"description": "Workflow infrastructure hooks for edify plugin"` at top level of hooks.json
   - Design violation: D-4 explicitly states hooks.json is a "separate file" and design Component 2 (lines 113-165) shows hooks.json WITHOUT the description field
   - Fix: Remove lines 23-24 from the cat command. Start hooks.json with `{"hooks": {...}}` directly
   - Rationale: The wrapper format (description + hooks) is only needed when hooks are inline in plugin.json. Since D-4 chose separate hooks.json file, no wrapper is needed

3. **Missing validation for hooks.json wrapper structure**
   - Location: Step 3.1, validation section (lines 91-97)
   - Problem: Validation checks for "wrapper structure: `description` + `hooks` fields" but this should NOT exist per the design
   - Fix: Once Issue #2 is fixed, remove this validation item. Replace with validation that hooks.json contains `hooks` field at root level

### Minor Issues

1. **Inconsistent hook script count**
   - Location: Step 3.2, validation section line 136
   - Note: Lists 3 remaining hooks but should list 4 (pretooluse-block-tmp.sh, submodule-safety.py, userpromptsubmit-shortcuts.py, userpromptsubmit-version-check.py)
   - Suggestion: Update to include version-check script: "Remaining hooks present: `pretooluse-block-tmp.sh`, `submodule-safety.py`, `userpromptsubmit-shortcuts.py`, `userpromptsubmit-version-check.py`"

2. **Temp file path uses project-local tmp/ but rationale could be clearer**
   - Location: Step 3.3, line 242
   - Note: Correctly uses `$CLAUDE_PROJECT_DIR/tmp/` but the parenthetical reason is incomplete
   - Suggestion: Expand rationale to: "follows project tmp/ convention per CLAUDE.md, not system `/tmp/`; also avoids conflict with pretooluse-block-tmp.sh hook which blocks /tmp writes"

3. **Manual test section could reference hook testing patterns**
   - Location: Phase checkpoint, lines 290-300
   - Note: Manual test procedure is comprehensive but doesn't reference existing hook testing documentation
   - Suggestion: Add reference to claude-config-layout.md hook testing section if it exists, or note this is the canonical test procedure

4. **Python compilation validation missing for existing hooks**
   - Location: Phase checkpoint, line 287
   - Note: Python syntax validation only checks new version-check hook, not existing Python hooks
   - Suggestion: Add syntax validation for submodule-safety.py and userpromptsubmit-shortcuts.py to ensure no accidental corruption during this phase

5. **jq installation note placement**
   - Location: Step 3.1, error conditions line 102
   - Note: While helpful, placing brew install command in error conditions is unusual — most runbooks assume tooling is available
   - Suggestion: Move to prerequisites section of overall runbook, or keep as-is if brew is standard for this project

## Requirements Validation

**Requirements context provided in design.md:**

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-9 (hooks migrate to plugin, settings.json emptied) | Satisfied | Step 3.1 creates hooks.json with all hooks configured |
| D-4 (hooks.json separate file) | Partial | File is separate, but includes wrapper format incorrectly (Major Issue #2) |
| Component 2 (hook migration with correct paths) | Satisfied | All hook scripts use $CLAUDE_PLUGIN_ROOT correctly |
| Component 7 (version check hook) | Satisfied | Step 3.3 implements version check with once-per-session gating |

**Gaps:** hooks.json format deviates from design (includes description field when it shouldn't per D-4)

---

## Positive Observations

- **Comprehensive validation**: Each step includes multiple validation methods (file existence, JSON syntax, executable bit, Python compilation)
- **Error condition coverage**: Anticipates common failure modes with specific remediation steps
- **Design alignment**: Correctly identifies all design references and maps them to implementation details
- **Path resolution clarity**: Excellent explanation of $CLAUDE_PLUGIN_ROOT usage and dev vs consumer mode differences
- **Script behavior documentation**: Version check hook behavior is thoroughly documented with clear step-by-step logic
- **Idempotency consideration**: Step 3.2 error conditions note that deletion is idempotent
- **Checkpoint verification**: Phase checkpoint includes both automated commands AND manual restart testing

## Recommendations

1. **Reconcile hooks.json format with design**: Remove description field to match D-4 decision for separate file approach
2. **Add upstream validation**: Consider adding a step to verify all hook scripts exist BEFORE creating hooks.json (fail-fast if prerequisites missing)
3. **Document hook timeout values**: The implementation adds timeout values (5s, 10s) but design doesn't specify these — consider adding rationale or moving to a constants section
4. **Consider hooks.json schema validation**: If Claude Code provides a schema for hooks.json, reference it in validation steps

## Next Steps

1. Fix hooks.json format (remove description field wrapper)
2. Update validation to match corrected format
3. Correct remaining hook count in Step 3.2 validation
4. Execute Phase 3 steps with corrected runbook
5. Run checkpoint validation before proceeding to Phase 4
