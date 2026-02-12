# Outline Review: worktree-update (Post-Amendment)

**Artifact**: plans/worktree-update/outline.md
**Date**: 2026-02-12T00:00:00Z
**Mode**: review + fix-all
**Context**: Third review after four amendments (TDD sequence, both-trees-clean, create-task compound, future work note)

## Summary

The amended outline maintains internal consistency and completeness. All four amendments are correctly integrated: TDD sequence explicit in implementation steps, both-trees-clean delegated to CLI command, create-task compound command designed and wired through Mode A/B, and submodule-agnostic support marked as OUT scope. The create-task design is sound (inputs/outputs/composition well-specified), scope section reflects all changes, and key decisions D7/D8 align with architecture.

**Overall Assessment**: Ready

## Amendment Integration

All four amendments verified:

| Amendment | Integration | Status |
|-----------|-------------|--------|
| TDD sequence (RED/GREEN) | Implementation Sequence lines 358-373 | Complete |
| Both-trees-clean CLI delegation | Merge Phase 1 line 118, D8 lines 335-339, justfile section lines 56-58 | Complete |
| create-task compound command | Lines 187-198 (design), D7 lines 329-333, Mode A line 212, Scope line 351, Sequence step 8 | Complete |
| Future work OUT scope | Scope OUT line 356 | Complete |

**Traceability**: All amendments traced to multiple sections (design, decisions, scope, implementation sequence, skill changes).

## Review Findings

### Critical Issues

None identified. All design elements are internally consistent.

### Major Issues

None identified. Amendments correctly integrated without introducing conflicts.

### Minor Issues

1. **Mode B create-task invocation ambiguity**
   - Location: Skill changes → Mode B → Step 4
   - Problem: Text said "Uses updated Mode A steps (focus-session, new commands)" but Mode A now uses `create-task` compound command, not individual commands. Ambiguous whether Mode B should use compound or individual.
   - Fix: Changed to "For each task in the group, invoke `claudeutils _worktree create-task "<task-name>"` (same compound command as Mode A)" for explicit clarity.
   - **Status**: FIXED

2. **Test file naming not explicit in Implementation Sequence**
   - Location: Implementation Sequence → Step 8
   - Problem: Scope line 349 lists `test_create_task.py` but step 8 just said "new test file" without naming it explicitly.
   - Fix: Added `(test_create_task.py)` to step 8 for consistency with Scope section.
   - **Status**: FIXED

3. **clean-tree classification unclear**
   - Location: Script changes → Keep as-is list
   - Problem: `clean-tree` listed as "keep as-is" alongside `ls` and `add-commit`, but it's actively used as a dependency by merge Phase 1 and justfile wt-merge. "Keep as-is" suggests passive preservation, not active dependency.
   - Fix: Split into two categories: "Keep as-is" for truly unchanged commands, and "Preserve existing (used as dependency)" for `clean-tree` with explicit note about its usage.
   - **Status**: FIXED

## Fixes Applied

- Mode B Step 4: explicit `create-task` invocation, clarifies compound command usage in parallel group
- Implementation Sequence Step 8: added `test_create_task.py` explicit filename
- Script changes section: split "Keep as-is" into two categories, clarified `clean-tree` as active dependency

## Internal Consistency Analysis

**create-task command design:**

| Aspect | Specification | Location | Consistency |
|--------|---------------|----------|-------------|
| Inputs | task name, --session-md (default agents/session.md), --base (default HEAD) | Lines 191 | ✓ |
| Process | 4 steps: derive-slug → focus-session → create-worktree → cleanup | Lines 192-196 | ✓ |
| Output | `<slug>\t<path>` tab-separated to stdout | Line 197 | ✓ |
| CLI signature | `claudeutils _worktree create-task "<task-name>" [--session-md <path>] [--base <ref>]` | Line 198 | ✓ |
| Architecture mention | Line 47 (compound command in CLI section) | Line 47 | ✓ |
| Scope IN | Line 351 (explicit inclusion) | Line 351 | ✓ |
| Implementation sequence | Step 8 (with test file) | Line 371 | ✓ |
| Key decision | D7 (lines 329-333, rationale + design) | Lines 329-333 | ✓ |
| Skill usage | Mode A Step 2 (line 212), Mode B Step 4 (line 219) | Lines 212, 219 | ✓ |

**Composition correctness:** create-task internally composes three function calls (derive-slug, focus-session, create-worktree). All three functions are defined in Architecture → Modules section. Output format (`<slug>\t<path>`) provides both identifiers needed for session.md edit (slug) and launch command (path). ✓

**Key decisions D7/D8 alignment:**

| Decision | Architecture Reference | Implementation Reference | Consistency |
|----------|------------------------|--------------------------|-------------|
| D7 (create-task compound) | Line 47 (CLI section) | Step 8 (line 371), Mode A Step 2 (line 212) | ✓ |
| D8 (justfile uses CLI clean-tree) | Line 56-58 (justfile section) | Merge Phase 1 (line 118), justfile wt-merge update (line 263) | ✓ |

**Scope section coverage:**

| Scope Item | Design Section | Implementation Step | Consistency |
|------------|----------------|---------------------|-------------|
| Python modules refactor | Architecture lines 31-41 | Step 1 (wt_path), Step 2 (add_sandbox_dir) | ✓ |
| Main CLI registration | Script changes lines 202-206 | Step 9 | ✓ |
| Skill updates | Skill changes lines 208-228 | Step 11 | ✓ |
| Execute-rule.md marker | Execute-rule section lines 230-241 | Step 12 | ✓ |
| Agent-core setup recipe | Script changes line 89 (prerequisite) | Step 9 | ✓ |
| Tests (5 files) | Test updates lines 267-297 | Steps 1-8 (interleaved) | ✓ |
| focus-session command | Script changes lines 167-185 | Step 4 | ✓ |
| create-task command | Script changes lines 187-198 | Step 8 | ✓ |
| Justfile wt-merge update | Justfile recipes line 263 | Step 10 | ✓ |

**OUT scope verification:**

- Submodule-agnostic support: Line 356 marks as future work. No implementation steps or scope items attempt this. ✓
- Settings.json user-level patterns: Line 355 clarifies only settings.local.json sandbox registration in scope. No user-level pattern work included. ✓

**Implementation Sequence coverage:**

All deliverables in Scope IN section have corresponding implementation steps:
- Steps 1-2: helper functions (wt_path, add_sandbox_dir)
- Step 3: derive-slug CLI wrapper
- Step 4: focus-session function + CLI
- Steps 5-7: update existing commands (new, rm, merge)
- Step 8: create-task compound
- Step 9: CLI registration + agent-core setup recipe
- Step 10: justfile wt-merge update
- Step 11: skill updates
- Step 12: execute-rule.md marker update

No scope items left without implementation step. ✓

**TDD sequence verification:**

Line 360 states "Each step includes tests alongside implementation (RED → GREEN → REFACTOR)."

All 12 steps mention either "tests" or "update existing tests" or "new test file":
- Steps 1-4: "+ tests" suffix
- Steps 5-6: "+ update existing tests"
- Step 7: "+ new test file"
- Step 8: "+ new test file (test_create_task.py)"
- Steps 9-12: Integration/update steps (test execution assumed)

Test-first pattern correctly integrated. ✓

## Positive Observations

- **Amendment integration quality**: All four amendments traced to multiple sections without introducing conflicts or gaps
- **create-task design completeness**: Inputs, process, outputs, CLI signature, and usage all explicitly specified
- **Internal consistency**: 9 cross-references to create-task across different sections all align
- **Scope clarity**: IN/OUT boundaries explicit, future work clearly marked as OUT
- **D7/D8 decision traceability**: Key decisions reference architecture, implementation, and rationale consistently
- **Test coverage**: Five test files with explicit coverage areas (new, rm, merge, focus-session, create-task)
- **TDD sequence**: All 12 steps include test work, RED/GREEN notation explicit
- **Dependency clarity**: clean-tree now explicitly marked as dependency, not passive "keep as-is"

## Recommendations

- **During Step 8 (create-task)**: Verify temp file cleanup happens even on error paths (context manager or try/finally)
- **During Step 11 (skill updates)**: Test Mode B with 3+ tasks to verify create-task invocation scales correctly
- **Test create-task compound**: Integration test for error propagation (if focus-session fails, does create-task return clear error?)
- **clean-tree dependency**: If clean-tree output format changes, ensure merge command and justfile remain compatible
- **Mode B efficiency**: Consider whether parallel create-task invocations would benefit from shared sandbox registration (currently each call writes settings.local.json)

---

**Ready for user presentation**: Yes
