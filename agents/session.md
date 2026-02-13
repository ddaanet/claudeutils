# Session Handoff: 2026-02-13

**Status:** RCAs complete, worktree skill merge-ready, 4 mechanical fixes applied.

## Completed This Session

**Three RCAs — parallel sonnet + opus comparison (10 agents total):**
- RCA #1 (general-step detection): Downstream consumer update gap — runbook-review.md created 4.5hr before per-phase typing shipped (verified via git timestamps), never updated. Fix: normalize axes to type-agnostic concept + `**TDD:**`/`**General:**` detection bullets
- RCA #2 (file growth): Projection-action gap — outline HAD a projection but wrong threshold (700 vs 400 limit), deferred split. Measured: High complexity = 42 lines/cycle mean (fabricated heuristic was 18-25, 42% error). Threshold conflation, not knowledge gap. Fix: hybrid (planning warns, execution enforces at 380 lines)
- RCA #3 (vet over-escalation): Binary status model (FIXED|UNFIXABLE) insufficient. Two-layer failure: zero checkpoint reports follow structured scope template (orchestrator) + agent ignores scope when provided (Cycle 0.6). Fix: investigation protocol as primary intervention (creates escalation cost), taxonomy as vocabulary, orchestrate template enforcement as precondition
- Cross-cutting meta root cause: designs inventory producers but not semantic consumers (3 confirmed instances of propagation gap)
- Model comparison: opus first-pass ≈ sonnet + one deepening round. Key delta: opus verifies against primary sources (found projection existed in RCA #2), sonnet accepts secondary summaries (assumed no projection). For autonomous RCA delegation, opus is the right tier.

**Deliverable review (worktree skill merge readiness):**
- Opus agent: **Mergeable with caveats** — 0C/4M/7m (down from 5C/10M/24m → 3C/12M/12m → 0C/4M/7m)
- All 5 recovery findings confirmed fixed, all tests pass (797/798 + 1 xfail)

**Mechanical fixes from deliverable review (4 applied):**
- N5: `_git()` extracted to `utils.py`, imports updated in cli.py + merge.py
- N6: Dead `commit_file` local functions deleted from 3 test files (fixture already injected via conftest)
- N8: Vacuous `test_merge_submodule_ancestry` deleted (mocks away behavior, E2E test covers same scenario)
- N11: SKILL.md Mode C step 1 trimmed — removed rationale, kept actionable instruction

## Prior Session (preserved)

**Recovery runbook executed (worktree-update):**
- All 4 steps via worktree-update-task agent (haiku), checkpoint passed
- 6 commits: C2, C3, M1, M2, C4, C5 fixes

## Pending Tasks

- [ ] **Worktree skill remaining review findings** — N1 (wt-ls Python delegation), N2 (post-commit precommit gap, documented recovery), N3 (session task extraction FR-3 incomplete), N4+N9 (design doc divergences: path convention, module naming), N7 (_setup_repo_with_submodule duplication), N10 (justified inconsistency, skip) | sonnet
  - See `plans/reports/deliverable-review-worktree-skill-2.md` for full findings

- [ ] **Workflow fixes from RCA** — Implement process improvements from 3 RCA reports (opus versions authoritative). Key fixes: normalize runbook-review.md axes, add execution-time split enforcement, add vet investigation protocol + UNFIXABLE taxonomy, orchestrate template enforcement | sonnet
  - See `plans/reports/rca-*-opus.md` for authoritative reports

- [ ] **Fix skill-based agents not using skills prolog section** — Agents duplicate content instead of referencing skills via `skills:` frontmatter | sonnet

- [ ] **Upstream plugin-dev: document `skills:` frontmatter** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` field | sonnet

## Blockers / Gotchas

**Two methodology documents exist:**
- `agents/decisions/review-methodology.md` — sonnet-generated, user distrusts, do NOT use
- `agents/decisions/deliverable-review.md` — ISO-grounded, use this one

**Learnings file at 386 lines** — well past 80-line soft limit. Run `/remember` to consolidate.

## Reference Files

- `plans/reports/rca-general-step-detection-opus.md` — RCA #1 authoritative (opus deepened)
- `plans/reports/rca-planning-file-growth-opus.md` — RCA #2 authoritative (opus deepened)
- `plans/reports/rca-vet-over-escalation-opus.md` — RCA #3 authoritative (opus deepened)
- `plans/reports/rca-*-detection.md` / `rca-*-growth.md` / `rca-*-escalation.md` — Sonnet versions (comparison data)
- `plans/reports/deliverable-review-worktree-skill-2.md` — Merge readiness review (0C/4M/7m)
- `plans/worktree-skill/design.md` — Worktree implementation design (conformance baseline)

---
*Handoff by Opus. RCAs complete, mechanical fixes applied, remaining findings queued.*
