# Session Handoff: 2026-02-17

**Status:** Deliverable code findings (M-4/M-5/M-6/M-7) complete. All workwoods deliverable fixes done.

## Completed This Session

**RCA: failure to use CLI for project state queries:**
- Deviation: ad-hoc `python3 -c` scripts to call `list_plans()` instead of `claudeutils _worktree ls`
- Root cause: execute-rule.md used Python function syntax → agent followed literally, skipping project-tooling check
- Deeper cause: specific procedural instructions suppress cross-cutting operational rules (same class as "shortcuts bypass upstream steps")
- Fix: execute-rule.md updated to reference CLI command, prohibit ad-hoc Python (uncommitted)
- Learning added to `agents/learnings.md`: "When querying project state"

**Deliverable code fixes (M-4/M-5/M-6/M-7):**
- M-4: Full gate priority chain in `inference.py` — 4 gate types per D-7 (design > runbook outline > phase > outline)
- M-5: Dynamic phase discovery in `vet.py` — glob-based, replaces hardcoded 6-phase map
- M-6: TreeInfo enriched with all design fields (commits_since_handoff, latest_commit_subject, is_dirty, task_summary). display.py rewritten — zero subprocess calls, uses aggregated data
- M-7: 12 new tests — outline-only/problem-only status, VetStatus.any_stale, 8 gate priority parametrized cases, dynamic phase discovery
- Vet: 4 minor deslop fixes applied, report at `plans/workwoods/reports/deliverable-code-fixes-vet.md`
- Precommit: 1038/1039 passed (up from 1026/1027, +12 new tests)
- Behavioral change: display.py commit counting now uses aggregation.py algorithm (last session.md commit as anchor per design C-2), not old display.py algorithm (oldest session.md commit)

## Pending Tasks

- [x] **Fix deliverable code findings** — M-4/M-5/M-6/M-7 code + test gaps

- [ ] **Design runbook evolution** — `/design plans/runbook-evolution/` | opus | restart
  - Requirements at `plans/runbook-evolution/requirements.md`
  - Outline exists at `plans/runbook-evolution/outline.md` — resume from Phase A.6 (outline review)
  - Scope: runbook SKILL.md generation directives only

- [ ] **Migrate test suite to diamond** — needs scoping | depends on runbook evolution design
  - Existing 1027 tests, separate design from runbook evolution
  - Different scope and execution profile

- [ ] **Design quality gates** — `/design plans/runbook-quality-gates/` | opus | restart
  - Requirements at `plans/runbook-quality-gates/requirements.md`
  - 3 open questions: script vs agent (Q-1), insertion point (Q-2), mandatory vs opt-in (Q-3)

## Blockers / Gotchas

**test_submodule_safety failures from main:**
- 4 tests failing: cd-and-single, cd-and-chain, cd-and-pytest, dquote-and
- From merged main content, not workwoods changes
- Precommit passes (1038/1039, 1 xfail)

**learnings.md at ~139 lines (soft limit 80):**
- No entries at ≥7 active days — consolidation trigger not met

**Gate wiring incomplete in production path:**
- `list_plans()` → `infer_state()` never passes `vet_status_func`, so `PlanState.gate` is always None in production
- M-4 implemented all 4 gate types, but wiring `get_vet_status` through `aggregate_trees` → `list_plans` → `infer_state` is separate work
- `_task_summary` now populates TreeInfo but is not yet rendered in CLI output

## Next Steps

Design runbook evolution (opus, restart). All deliverable fixes complete.

---
*Handoff by Sonnet. Deliverable code fixes complete, pipeline improvements next.*
