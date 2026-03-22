# Runbook Review: Phase 1 — Plugin Manifest and Structure

**Artifact**: `plans/plugin-migration/runbook-phase-1.md`
**Date**: 2026-03-14T00:00:00Z
**Mode**: review + fix-all
**Phase types**: General (3 steps)

## Summary

Phase 1 creates the plugin manifest (`plugin.json`), rewrites hooks.json in wrapper format, and validates plugin loading via a checkpoint step. The core implementation approach is sound and aligned with the outline. Two major issues were found and fixed: a wrong settings.json path in Step 1.2 prerequisites (`.claude/settings.json` does not exist; the correct file is `.claude/settings.visible.json`), and a deferred decision in Step 1.3 ("Requires design" language left the tmux verification approach unresolved). Both were fixed inline. Two minor path-clarity issues were also corrected.

**Overall Assessment**: Ready

## Findings

### Critical Issues

None.

### Major Issues

1. **Wrong settings.json path in Step 1.2 prerequisites**
   - Location: Step 1.2, Prerequisites
   - Problem: Step says "Read `.claude/settings.json` hooks section" but `.claude/settings.json` does not exist in the project. The hooks configuration is in `.claude/settings.visible.json`. An executor following the step would fail to find the file.
   - Fix: Changed to `.claude/settings.visible.json`
   - **Status**: FIXED

2. **Deferred decision in Step 1.3 — tmux verification approach unresolved**
   - Location: Step 1.3, Implementation item 1
   - Problem: "Requires design: Programmatic Claude CLI verification via tmux. Before building custom tooling, search for existing tools/patterns..." — this leaves the implementation approach undecided, which is a planning-time gap. Executors cannot proceed without a resolved approach.
   - Fix: Replaced with concrete tmux interaction steps using `tmux new-window`, `send-keys`, `capture-pane`, and explicit verification sequence for each FR target.
   - **Status**: FIXED

### Minor Issues

3. **Ambiguous `outline.md` reference in Step 1.2**
   - Location: Step 1.2, Prerequisites and Error Conditions
   - Problem: "Read outline.md Component 2..." and "verify against outline Component 2 table" — no full path. In a multi-file plan, this is ambiguous.
   - Fix: Changed to `plans/plugin-migration/outline.md` in both locations.
   - **Status**: FIXED

4. **Subjective NFR-1 success criterion in Step 1.3**
   - Location: Step 1.3, Expected Outcome
   - Problem: "Dev mode cycle time comparable to symlink approach" is not binary-testable. An executor can't pass or fail this deterministically.
   - Fix: Replaced with concrete criterion: "edit-restart-verify cycle confirms change visible on next start."
   - **Status**: FIXED

## Fixes Applied

- Step 1.2, Prerequisites — `.claude/settings.json` → `.claude/settings.visible.json`
- Step 1.2, Prerequisites — `outline.md Component 2` → `plans/plugin-migration/outline.md` Component 2
- Step 1.2, Error Conditions — `outline Component 2 table` → `plans/plugin-migration/outline.md` Component 2 table
- Step 1.3, Implementation — replaced "Requires design" deferred block with concrete tmux interaction steps
- Step 1.3, Expected Outcome — replaced subjective NFR-1 criterion with binary-testable outcome

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes

---

*Note: A prior review from 2026-02-08 (`phase-1-review.md`) reviewed a different version of this file (referencing `edify-plugin/` paths and `.version` files). That review is superseded by this one.*
