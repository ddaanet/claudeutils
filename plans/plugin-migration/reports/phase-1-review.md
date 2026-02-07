# Vet Review: Phase 1 Runbook

**Scope**: plans/plugin-migration/runbook-phase-1.md
**Date**: 2026-02-07T00:00:00Z

## Summary

Phase 1 runbook defines creation of plugin manifest and version marker files. Both steps are straightforward file creation tasks. Runbook structure is clear with explicit validation commands and success criteria. Design alignment is strong with correct references to D-1 and Component 1.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Missing .version content specification**
   - Location: runbook-phase-1.md:67
   - Problem: Design Component 3 states "plain text, single line, no trailing newline" but step 1.2 says "(Plain text, single line, no trailing newline)" in parentheses as if optional or clarifying
   - Suggestion: Be explicit in Implementation section: "Create file with content `1.0.0` using `printf` to avoid trailing newline: `printf '1.0.0' > agent-core/.version`"

2. **Weak validation for .version content**
   - Location: runbook-phase-1.md:87
   - Problem: `cat agent-core/.version` outputs the content but doesn't verify absence of trailing newline or extra whitespace
   - Suggestion: Add validation command that checks exact byte content: `[ "$(cat agent-core/.version | wc -c)" -eq 5 ]` (5 bytes = "1.0.0" with no newline)

3. **Report Path marked N/A inconsistently**
   - Location: runbook-phase-1.md:49, 89
   - Problem: Both steps say "N/A (trivial step, no report needed)" but this violates quiet execution pattern for delegated tasks
   - Suggestion: Either specify report path (e.g., `plans/plugin-migration/reports/phase-1-execution.md`) or clarify that these steps are executed inline (not delegated) and therefore don't need report paths

4. **Missing plugin-dev skill load checkpoint**
   - Location: runbook-phase-1.md (beginning)
   - Problem: Design "Documentation Perimeter" specifies loading `plugin-dev:plugin-structure` and `plugin-dev:hook-development` skills before planning, but Phase 1 doesn't verify these are loaded
   - Suggestion: Add prerequisite check at start of Phase 1: verify skills loaded OR load them explicitly

### Minor Issues

1. **Inconsistent heading case**
   - Location: runbook-phase-1.md:11, 53
   - Note: Step headings use "Create plugin.json" vs "Create .version marker" — first is file-focused, second is artifact-focused
   - Suggestion: Standardize to artifact-focused: "1.1: Create plugin manifest" and "1.2: Create fragment version marker"

2. **Missing jq installation check**
   - Location: runbook-phase-1.md:35
   - Note: Validation requires `jq` but doesn't check if it's installed
   - Suggestion: Add to error conditions: "jq not installed → Install with brew/apt/package manager"

3. **Checkpoint success criteria duplicates step validation**
   - Location: runbook-phase-1.md:93-109
   - Note: Phase 1 Checkpoint verification commands are identical to step 1.1 and 1.2 validation commands
   - Suggestion: Checkpoint could reference step validation instead of duplicating: "Verify both Step 1.1 and Step 1.2 validation commands pass"

4. **No directory creation guidance**
   - Location: runbook-phase-1.md:19
   - Note: Step 1.1 creates `agent-core/.claude-plugin/plugin.json` but doesn't explicitly state to create `.claude-plugin/` directory first
   - Suggestion: Add to Implementation: "Create directory `agent-core/.claude-plugin/` if it doesn't exist"

5. **Error condition too vague**
   - Location: runbook-phase-1.md:42
   - Note: "Directory creation fails → Check permissions" doesn't specify which directory
   - Suggestion: "`.claude-plugin/` directory creation fails → Check permissions on agent-core/ directory"

## Requirements Validation

**Outline Review Status**: Present at `plans/plugin-migration/reports/runbook-outline-review.md`

**Requirements Coverage**:

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1 (plugin auto-discovery) | Partial | plugin.json enables discovery, but Phase 1 only creates manifest (hooks/skills in later phases) |
| D-1 (plugin name = edify) | Satisfied | runbook-phase-1.md:30 references D-1, plugin.json uses name "edify" |
| Component 1 (minimal manifest) | Satisfied | runbook-phase-1.md:31 references Component 1, manifest has only name/version/description |
| Component 3 (versioning) | Satisfied | .version marker created per Component 3 spec |

**Gaps**: None for Phase 1 scope. FR-1 full satisfaction requires later phases.

## Outline Validation

**Outline Review Status**: Present at `plans/plugin-migration/reports/runbook-outline-review.md`

**Requirements Coverage** (from `plans/plugin-migration/runbook-outline.md`):

Phase 1 maps to outline Section 1.1 (plugin.json) and Section 1.2 (.version marker). Both requirements covered.

**Coverage notes**:
- Outline Section 1.1 mapped to FR-1 + D-1 + Component 1 — runbook satisfies
- Outline Section 1.2 mapped to Component 3 — runbook satisfies
- No missing coverage identified

---

## Positive Observations

- **Clear validation commands** — Each step includes executable bash commands for verification, not prose descriptions
- **Explicit design references** — D-1 and Component 1 cited with rationale, making design traceability easy
- **Idempotent validation** — All validation commands can be re-run safely (`test -f`, `jq .`, content checks)
- **Simple scope** — Phase 1 appropriately limited to two trivial file creation tasks
- **Checkpoint structure** — Phase boundary checkpoint clearly separates Phase 1 from Phase 2
- **Error conditions specified** — Each step includes error conditions and remediation guidance

## Recommendations

1. **Standardize report path handling** — Decide if Phase 1 steps are inline execution (no delegation, no report) or quiet execution (delegated, report to file). If inline, remove "Report Path: N/A" sections entirely (not needed for inline work). If delegated, specify actual report path.

2. **Add prerequisite validation** — Include skill load check at start: verify `plugin-dev:plugin-structure` and `plugin-dev:hook-development` are loaded per design "Documentation Perimeter" requirements.

3. **Strengthen .version validation** — Use byte-count check (`wc -c`) to verify no trailing newline, not just visual inspection via `cat`.

4. **Clarify directory creation** — Make explicit that `.claude-plugin/` directory must be created (or use `mkdir -p` pattern in implementation guidance).

## Next Steps

1. **Fix major issue #1** — Add explicit `printf` command to Step 1.2 Implementation to ensure no trailing newline
2. **Fix major issue #2** — Add byte-count validation to Step 1.2 Validation section
3. **Fix major issue #3** — Clarify report path handling (inline vs delegated execution model)
4. **Fix major issue #4** — Add prerequisite validation checkpoint at start of Phase 1
5. **Address minor issues** — Standardize heading case, add jq check, make directory creation explicit
6. **Re-run validation** — After fixes, verify all validation commands execute cleanly
