# Outline Review: worktree-cli-default

**Artifact**: plans/worktree-cli-default/outline.md
**Date**: 2026-02-22
**Mode**: review + fix-all

## Summary

Outline is sound and well-scoped. Three major issues fixed: vacuous cycle removed, missing sandbox removal requirement added, absorbed-scope contradiction resolved. Five minor issues fixed: structural improvements to assertions, regression notes, and section organization.

**Overall Assessment**: Ready

## Requirements Traceability

No formal FR-* requirements exist. Traceability is against session.md task notes and absorbed scope items.

| Absorbed Item | Outline Coverage | Status |
|---------------|-----------------|--------|
| positional = task name | Cycles 1.1-1.3 | Complete |
| `--branch` for bare slug | Cycle 1.1 | Complete |
| `--slug` override | Cycle 1.3 | Complete |
| pre-merge untracked file fix | Cycle 1.5 | Complete |
| worktree skill adhoc mode | Cycle 1.1 (note) | Complete |
| sandbox removal | Cycle 1.1 | Complete (was Missing) |
| `rm --confirm` gate fix | — | Separated — orthogonal to CLI args |

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Cycle 1.5 vacuous — `--task` removal**
   - Location: Phase 1, Cycle 1.5
   - Problem: `--task` option is removed as part of Cycle 1.1's argument rewiring. Click rejects unknown options by default. RED test for `--task` would pass immediately without any implementation beyond what Cycle 1.1 already requires.
   - Fix: Removed Cycle 1.5. Added explanatory note after Phase 1 cycles.
   - **Status**: FIXED

2. **Missing absorbed requirement: sandbox removal**
   - Location: Scope, Affected Files, Phase 1
   - Problem: Session.md explicitly states "Remove sandbox configuration from `_worktree new` — no more `additionalDirectories` in settings.local.json." Code at `_create_parent_worktree` lines 128-132 has 3 `add_sandbox_dir` calls. Not mentioned in outline.
   - Fix: Added sandbox removal to Goal, Before/After, Affected Files, Cycle 1.1 assertions, Scope. Folded into Cycle 1.1 rather than separate cycle (deletion, not new behavior — same function, same test).
   - **Status**: FIXED

3. **`rm --confirm` gate fix contradiction**
   - Location: Scope vs session.md absorbed list
   - Problem: Session.md lists `rm --confirm gate fix` as absorbed into this task. Outline Scope explicitly excludes `rm` subcommand. Contradiction.
   - Fix: Added SEPARATE TASK note in Scope section. `rm --confirm` is orthogonal to CLI argument changes and belongs in its own task.
   - **Status**: FIXED

### Minor Issues

1. **Phase 1 addendum section → inline**
   - Location: "Phase 1 addendum: Absorbed scope" section
   - Problem: Cycle 1.6 was in a separate addendum section outside Phase 1. Confusing for execution — appears to be a different phase.
   - Fix: Moved to Phase 1 as Cycle 1.5 (after vacuous cycle removal). Removed addendum heading.
   - **Status**: FIXED

2. **Cycle 1.1 missing negative assertion**
   - Location: Phase 1, Cycle 1.1
   - Problem: Only checked exit 0 + worktree exists. Didn't verify session.md was NOT modified (important to distinguish bare slug from task mode).
   - Fix: Added "session.md NOT modified" and "no `.claude/settings.local.json` written" to RED assertions.
   - **Status**: FIXED

3. **Cycle 1.2 "session.md updated" vague**
   - Location: Phase 1, Cycle 1.2
   - Problem: "session.md updated" doesn't specify what update. Could mean file exists, contains content, or move_task_to_worktree was called.
   - Fix: Changed to "`move_task_to_worktree` called with task name and derived slug" and added "session.md gets inline worktree marker" to Verifies.
   - **Status**: FIXED

4. **Phase 2 missing regression note**
   - Location: Phase 2 heading
   - Problem: Phase 1 changes the CLI signature, breaking existing tests. No note that Phase 2 specifically addresses this expected breakage.
   - Fix: Added regression note after Phase 2 heading.
   - **Status**: FIXED

5. **Step 2.2 sandbox test needs deletion, not rename**
   - Location: Phase 2, Step 2.2
   - Problem: Listed `test_new_sandbox_registration` as slug-to-branch rename. With sandbox removal, this test should be removed entirely.
   - Fix: Changed to "remove" with explanation.
   - **Status**: FIXED

## Fixes Applied

- Goal — added "Remove sandbox registration from `new`"
- Before/After — added sandbox registration state change
- Affected Files — added `add_sandbox_dir` removal, corrected `test_new_sandbox_registration` action
- Cycle 1.1 — added negative assertions (no session.md, no settings.local.json), added sandbox to Verifies
- Cycle 1.2 — specified `move_task_to_worktree` call and inline marker
- Cycle 1.3 — specified `move_task_to_worktree` call with custom slug
- Cycle 1.4 — clarified "at least one of positional or `--branch`"
- Removed old Cycle 1.5 (`--task` removal — vacuous), added explanatory note
- Moved old Cycle 1.6 → Cycle 1.5 (inline in Phase 1)
- Phase 2 heading — added regression note
- Step 2.2 — changed `test_new_sandbox_registration` from rename to removal
- Scope — added sandbox removal to IN, `add_sandbox_dir` function to OUT, `rm --confirm` to SEPARATE TASK

## Positive Observations

- Clear Before/After state table makes the change immediately understandable
- Scope boundaries are explicit and reasonable
- Phase typing (TDD vs general) is appropriate — new behavior gets TDD, mechanical updates get general
- Cycle 1.3 addresses the real-world 29-char slug problem with concrete example
- Adhoc mode coverage via note avoids a vacuous cycle

## Recommendations

- Session.md should be updated to remove `rm --confirm gate fix` from the absorbed list (or create a separate task for it)
- Consider whether `add_sandbox_dir` function itself should be deleted (if no other callers) — currently marked OUT of scope

---

**Ready for expansion**: Yes
