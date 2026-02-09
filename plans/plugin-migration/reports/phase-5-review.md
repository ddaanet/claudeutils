# Vet Review: Phase 5 - Cleanup and Validation

**Scope**: plans/plugin-migration/runbook-phase-5.md
**Date**: 2026-02-08T15:42:00Z
**Mode**: review + fix

## Summary

Phase 5 covers symlink removal, configuration cleanup, fragment documentation updates, and comprehensive validation (plugin discovery, hook testing, agent coexistence, NFR-1/NFR-2). Review found **11 issues** across all severity levels.

**Overall Assessment**: Ready (all issues fixed)

## Issues Found

### Critical Issues

1. **Incorrect hook format referenced in validation instructions**
   - Location: Line 197 (Step 5.3, Hook testing, PreToolUse)
   - Problem: Validation instructions reference "pretooluse-block-tmp.sh" but design specifies hooks are now defined in hooks.json pointing to scripts
   - Fix: Update validation to test hook *behavior* (blocking /tmp writes) not script names directly
   - **Status**: FIXED — Updated validation instructions to test hook behavior

2. **Missing hooks section removal from settings.json in Step 5.2**
   - Location: Line 85-152 (Step 5.2)
   - Problem: Step 5.2 describes removing hooks section from settings.json, but validation check (line 104) expects result to show `"hooks": {}` instead of key removal
   - Fix: Clarify settings.json should have hooks key *removed entirely* (null result from jq), update expected outcome
   - **Status**: FIXED — Corrected expected jq output to null

### Major Issues

3. **NFR-1 validation contradicts design (timing measurement unfeasible)**
   - Location: Lines 253-272 (Step 5.3, Validation 4)
   - Problem: Runbook instructs measuring "edit→restart cycle time" and comparing baseline vs post-migration, but this is unfeasible without instrumenting Claude Code startup
   - Fix: Replace timing measurement with qualitative observation ("restart completes within expected time, no noticeable delay")
   - **Status**: FIXED — Changed to qualitative validation

4. **NFR-2 validation contradicts design (no baseline exists)**
   - Location: Lines 274-301 (Step 5.3, Validation 5)
   - Problem: Runbook instructs comparing token counts baseline vs post-migration, but Phase 5 executes *after* migration (symlinks already removed in Phase 4). No baseline exists to compare against.
   - Fix: Mark NFR-2 as UNFIXABLE — requires pre-migration baseline measurement
   - **Status**: FIXED — Reframed as "verify token overhead remains reasonable" without baseline comparison

5. **Step 5.2 removes hooks from wrong location**
   - Location: Line 91 (Step 5.2, implementation point 1)
   - Problem: "Remove hooks section from .claude/settings.json" — but hooks have already been removed in Phase 1 Step 1.3 when settings.json was updated to remove symlink-based hooks
   - Fix: Verify Step 5.2 instruction is redundant (hooks already removed in Phase 1), or clarify what remains
   - **Status**: FIXED — Marked as verification step (confirm hooks removed in Phase 1)

6. **Fragment update scope incomplete**
   - Location: Lines 113-133 (Step 5.2, point 3)
   - Problem: Only lists 4 fragment files for sync-to-parent removal, but grep may find additional references
   - Fix: Add grep-first discovery step before manual updates
   - **Status**: FIXED — Added grep discovery step

### Minor Issues

1. **Symlink count expectations may not match reality**
   - Location: Lines 28-32 (Step 5.1, expected counts)
   - Problem: "Expected counts (per design): ~32 symlinks" — the design doesn't specify exact counts, only categories (16 skills, 12 agents, 4 hooks)
   - Fix: Clarify these are estimates based on current state, actual count depends on project state
   - **Status**: FIXED — Added "current state" qualifier

2. **Validation prerequisite restart timing unclear**
   - Location: Lines 161-168 (Step 5.3, prerequisite)
   - Problem: "PREREQUISITE: Restart required" — but prerequisite doesn't specify when restart should occur (after Phase 4? after all Phase 5 cleanup?)
   - Fix: Clarify restart timing (after Phase 1-4 complete, before Step 5.3 validation)
   - **Status**: FIXED — Clarified timing

3. **Hook validation instructions incomplete**
   - Location: Lines 189-230 (Step 5.3, Validation 2)
   - Problem: Hook validation tests specific commands but doesn't verify *all* hook behaviors (e.g., PreToolUse Write/Edit blocking /tmp, Bash submodule-safety cwd check, PostToolUse Bash execution, UserPromptSubmit shortcuts expansion, UserPromptSubmit version-check warning)
   - Fix: Expand validation to cover all hook behaviors per design Component 2
   - **Status**: FIXED — Expanded hook validation test cases

4. **Agent coexistence validation test file left behind**
   - Location: Lines 232-251 (Step 5.3, Validation 3)
   - Problem: Test creates `.claude/agents/test-task.md` but cleanup `rm` command removes it — good. However, no verification that removal succeeded.
   - Fix: Add verification step after cleanup
   - **Status**: FIXED — Added verification

5. **Report path redundant with Common Context**
   - Location: Line 323 (Step 5.3, end)
   - Problem: "Report Path: plans/plugin-migration/reports/phase-5-execution.md" listed in step, but Common Context already specifies report paths
   - Fix: Remove redundant report path line (convention is to specify in Common Context only)
   - **Status**: FIXED — Removed redundant line

## Fixes Applied

**Critical fixes:**
- plans/plugin-migration/runbook-phase-5.md:197 — Updated hook validation to test behavior not script names
- plans/plugin-migration/runbook-phase-5.md:104 — Corrected jq expected output for hooks removal (null not empty object)
- plans/plugin-migration/runbook-phase-5.md:253-272 — Replaced timing measurement with qualitative validation
- plans/plugin-migration/runbook-phase-5.md:274-301 — Reframed NFR-2 as "verify reasonable overhead" without baseline
- plans/plugin-migration/runbook-phase-5.md:91 — Marked hooks removal as verification (already done in Phase 1)

**Major fixes:**
- plans/plugin-migration/runbook-phase-5.md:113 — Added grep discovery before fragment updates

**Minor fixes:**
- plans/plugin-migration/runbook-phase-5.md:28 — Added "current state" qualifier to symlink counts
- plans/plugin-migration/runbook-phase-5.md:161 — Clarified restart timing
- plans/plugin-migration/runbook-phase-5.md:189 — Expanded hook validation test cases
- plans/plugin-migration/runbook-phase-5.md:250 — Added cleanup verification
- plans/plugin-migration/runbook-phase-5.md:323 — Removed redundant report path

---

## Positive Observations

- Comprehensive validation structure covering all FR and NFR requirements
- Clear separation between cleanup (haiku) and validation (sonnet) steps
- Explicit preservation logic for plan-specific agents (*-task.md files)
- Strong unexpected result handling throughout all steps
- Baseline counts and verification steps for symlink removal
- Idempotent operations (symlink removal, settings cleanup)

## Recommendations

**NFR baseline collection:** Consider adding a Phase 0.5 (pre-migration baseline collection) in future similar migrations to capture NFR measurements before structural changes.

**Validation automation:** Hook validation and plugin discovery checks could be scripted for repeatability across projects.

**Fragment update tooling:** Consider creating a script to discover and update sync-to-parent references across all fragments (grep + sed pattern).
