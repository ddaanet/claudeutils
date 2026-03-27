# Session Handoff: 2026-03-27

**Status:** Skill-CLI integration designed (outlined). 3 SPs: hook, execute-rule, commit skill. SP-3 handoff deferred.

## Completed This Session

**Skill-CLI integration /design:**
- Classified: Moderate (all axes high), composite 3 sub-problems
- Explored CLI implementations (`_commit`, `_handoff`, `_status`) — full input/output/mutation surface mapped
- Design decisions: Stop hook trigger convention (`^Status\.$`), /commit composition boundary, execute-rule simplification
- SP-3 (handoff integration) deferred — `_handoff` CLI handles 2 of ~6 session.md mutations, partial composition adds complexity for minimal gain
- Discussion: incremental vs batch handoff model → batch wins (consistency, crash recovery, synthesis quality)
- Wrote: `plans/skill-cli-integration/classification.md`, `plans/skill-cli-integration/outline.md`

## In-tree Tasks

- [ ] **Runbook warnings** — `/inline plans/runbook-warnings` | sonnet
  - Plan: runbook-warnings | Status: planned | Tier 2 — route to /inline not prepare-runbook.py
- [x] **Stop hook spike** — `/design plans/stop-hook-status-spike/brief.md` | haiku
  - Spike complete. Findings positive. Production integration absorbed into skill-cli-integration SP-H.
- [ ] **Skill-CLI integration** — `/runbook plans/skill-cli-integration/outline.md` | sonnet
  - 3 SPs: SP-H (status hook, requires restart), SP-1 (execute-rule), SP-2 (commit skill). SP-H blocks SP-1/SP-2.
- [ ] **Outline template trim** — `/design plans/outline-template-trim/brief.md` | opus | restart

## Worktree Tasks

- [ ] **Planstate disambiguation** — `/design plans/planstate-disambiguation/brief.md` | sonnet
- [ ] **Historical proof feedback** — `/design plans/historical-proof-feedback/brief.md` | sonnet
  - Prerequisite: updated proof skill integrated in all worktrees
- [ ] **Learnings startup report** — `/design plans/learnings-startup-report/brief.md` | sonnet
- [ ] **Submodule vet config** — `/design plans/submodule-vet-config/brief.md` | sonnet
- [!] **Resolve learning refs** — `/design plans/resolve-learning-refs/brief.md` | sonnet
  - Blocker: blocks invariant documentation workflow (recall can't resolve learning keys)
- [ ] **Runbook integration-first** — `/design plans/runbook-integration-first/brief.md` | sonnet
  - Addendum to runbook-quality-directives plan
- [ ] **Commit drift guard** — `/design plans/commit-drift-guard/brief.md` | opus
  - Design how _commit CLI verifies files haven't changed since last diff
- [ ] **Inline resume policy** — `/design plans/inline-resume-policy/brief.md` | sonnet
  - Add resume-between-cycles directive to /inline delegation protocol
- [ ] **Pending brief generation** — `/design plans/pending-brief-generation/brief.md` | sonnet
  - p: directive should create plans/<slug>/brief.md to back the task
- [ ] **Inline dispatch recall** — `/design plans/inline-dispatch-recall/brief.md` | sonnet
  - Fix review-dispatch-template to enforce artifact-path-only recall pattern
- [ ] **Worktree ls filtering** — `/design plans/worktree-ls-filtering/brief.md` | sonnet
  - _worktree ls dumps all plans across all trees; handoff only needs session.md plan dirs
- [ ] **Design context prereq** — `/design plans/design-context-prerequisite/brief.md` | opus | restart
  - Agents modifying code need design spec in context. Fragment change.
- [ ] **Design segmentation gate** — `/design plans/design-segmentation-gate/brief.md` | opus | restart
  - Add sub-problem split gate after design finalization, before runbook. Prevents monolithic review scope.

## Blockers / Gotchas

**Learnings at soft limit (138 lines):**
- `/codify` overdue — next session should consolidate older learnings

**pretooluse-recall-check hook regex:**
- `[^/]+` matches across newlines/spaces, capturing prose text between `plans/` and next `/`. Brief at `plans/inline-dispatch-recall/brief.md` covers fix.

**Flaky test:**
- `test_worktree_merge_learnings.py::test_merge_learnings_segment_diff3_prevents_orphans` — intermittent merge conflict failure. Passes on retry.

## Reference Files

- `plans/skill-cli-integration/outline.md` — Design outline with SPs, composition boundary, dependency order
- `plans/skill-cli-integration/classification.md` — Moderate classification, SP-3 deferral rationale
- `plans/stop-hook-status-spike/brief.md` — Spike findings (trigger mechanism, ANSI styling)
- `tmp/spike-stop-hook/status-hook.sh` — Hook prototype (SP-H starting point)

## Next Steps

Execute runbook-warnings via `/inline plans/runbook-warnings`. Skill-CLI integration next after that (`/runbook` on outlined plan).
