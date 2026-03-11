# Problem.md Migration

## Context

Commit `21e0d899` ("Document all pending tasks with plan artifacts") created 16 plan files — 9 as `requirements.md`, 7 as `problem.md`. The agent invented `problem.md` as an artifact type: free-form problem statements with `## Problem` / `## Success Criteria` structure, vs the structured FR/NFR format of `requirements.md`.

`problem.md` is not specified in any skill. `/requirements` doesn't produce it. Planstate treats it as `requirements` status but `_derive_next_action` templates the wrong filename (`requirements.md` instead of `problem.md`), causing session.md to contain non-existent paths. This has broken precommit in two consecutive sessions.

The intended artifact for "not yet structured requirements" is `brief.md` — it bridges to `/requirements` or `/design`.

## Scope

1. **Rename:** 13 `problem.md` → `brief.md` (with git history context recovery per file — match each to its originating task for proper brief content, don't just rename)
2. **Planstate fix:** `_derive_next_action` should resolve actual filename from plan directory, not assume from status label
3. **Precommit gate:** Reject `problem.md` as an unrecognized plan artifact
4. **Test:** Add `problem.md`-only → correct next_action test case to `test_planstate_inference.py`

## Affected Plans

ar-how-verb-form, ar-idf-weighting, ar-threshold-calibration, design-backlog-review, design-pipeline-evolution, diagnose-compression-loss, markdown-migration, parallel-orchestration, quality-grounding, research-backlog, review-agent-quality, skill-agent-bootstrap, worktree-lifecycle-cli
