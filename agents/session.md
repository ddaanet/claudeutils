# Session Handoff: 2026-03-30

**Status:** Runbook warnings fixed (directory-aware validation). Broad pipeline discussion — questioning runbooks, behavioral guardrails, planning-first paradigm.

## Completed This Session

**Runbook warnings fix:**
- Rejected original plan (cross-step creation-verb heuristic) — "fixes upon fixes" on ambiguous format
- Implemented approach A: directory-aware validation in `validate_file_references()`
- Parent dir exists + file missing → warn (likely typo). Parent dir missing → silent (greenfield).
- 2-line production change, 2 tests in new file
- Spec: `docs/superpowers/specs/2026-03-30-runbook-warnings-directory-aware-design.md`

**Pipeline comparative analysis (discussion, not implementation):**
- Explored superpowers plugin architecture (12 skills, 1 reviewer agent, platform-native)
- Compared with agent-core/edify (34 skills, 13 agents, 27 fragments, 3-tier pipeline)
- Referenced `inbox/brief-invariant-guided-agent.md` (prototype → observe → formalize → verify)
- Referenced `mac-de-anna/docs/memory-version-control-design.md` (git-backed memory)
- Conclusions: planning pipeline is BDUF under question. Behavioral guardrails are prompt-level patches for model-level tendencies. Memory/recall and structural enforcement (hooks, gates) survive any workflow paradigm. Runbooks, plan-specific agents, corrector chains, deliverable-review ceremony are candidates for removal.

## In-tree Tasks

- [x] **Runbook warnings** — `/inline plans/runbook-warnings` | sonnet
  - Replaced with directory-aware validation (approach A). Original cross-step plan abandoned.
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

**Learnings at soft limit (143 lines):**
- `/codify` overdue — next session should consolidate older learnings

**pretooluse-recall-check hook regex:**
- `[^/]+` matches across newlines/spaces, capturing prose text between `plans/` and next `/`. Brief at `plans/inline-dispatch-recall/brief.md` covers fix.

**Flaky test:**
- `test_worktree_merge_learnings.py::test_merge_learnings_segment_diff3_prevents_orphans` — intermittent merge conflict failure. Passes on retry.

**Pipeline direction under active questioning:**
- User questioning entire design → runbook → orchestrate pipeline, behavioral guardrails, and planning-first paradigm
- No decisions made yet — discussion only. Next session should not assume pipeline continuity.

## Reference Files

- `docs/superpowers/specs/2026-03-30-runbook-warnings-directory-aware-design.md` — Spec for directory-aware validation
- `plans/skill-cli-integration/outline.md` — Design outline with SPs, composition boundary, dependency order
- External: `~/code/inbox/brief-invariant-guided-agent.md` — prototype-first + invariant verification paradigm
- External: `~/code/mac-de-anna/docs/memory-version-control-design.md` — git-backed version-controlled memory

## Next Steps

Skill-CLI integration next (`/runbook` on outlined plan) — but pipeline direction is unsettled. User may want to reprioritize or restructure before continuing pipeline-dependent work.
