# Session Handoff: 2026-02-13

**Status:** Worktree skill deliverable review findings fixed, merge-ready.

## Completed This Session

**Deliverable review remaining findings (5 fixed):**
- N1: `wt-ls` converted to native bash (awk parsing, no Python delegation) — handles sibling container paths, excludes main worktree
- N3: Session task extraction completed — `_resolve_session_md_conflict` appends new tasks automatically (with or without section header)
- N7: Test fixture dedup — `setup_repo_with_submodule` extracted to `fixtures_worktree.py`, duplicates removed from 2 test files
- N4: Design doc updated to document sibling container (`../<repo>-wt/<slug>/`) with rationale (avoids CLAUDE.md inheritance)
- N9: Design doc Package Structure updated — shows `merge.py` (not `conflicts.py`)
- Vet review identified and fixed critical wt-ls bugs (wrong path logic, missing branch handling) and minor issues (merge logic edge cases, design doc consistency)
- All 59 worktree tests pass, 797/798 project tests pass

**Prior session preserved:**

**Three RCAs — parallel sonnet + opus comparison (10 agents total):**
- RCA #1 (general-step detection): Downstream consumer update gap — runbook-review.md created 4.5hr before per-phase typing shipped (verified via git timestamps), never updated
- RCA #2 (file growth): Projection-action gap — outline HAD a projection but wrong threshold (700 vs 400 limit), deferred split. Measured: High complexity = 42 lines/cycle mean (fabricated heuristic was 18-25, 42% error)
- RCA #3 (vet over-escalation): Binary status model (FIXED|UNFIXABLE) insufficient. Two-layer failure: zero checkpoint reports follow structured scope template (orchestrator) + agent ignores scope when provided
- Cross-cutting meta root cause: designs inventory producers but not semantic consumers (3 confirmed instances of propagation gap)
- Model comparison: opus first-pass ≈ sonnet + one deepening round. Opus verifies against primary sources, sonnet accepts secondary summaries

**Deliverable review (worktree skill merge readiness):**
- Opus agent: **Mergeable with caveats** — 0C/4M/7m (down from 5C/10M/24m → 3C/12M/12m → 0C/4M/7m)
- All 5 recovery findings confirmed fixed

**Mechanical fixes from deliverable review (4 applied):**
- N5: `_git()` extracted to `utils.py`, imports updated in cli.py + merge.py
- N6: Dead `commit_file` local functions deleted from 3 test files (fixture already injected via conftest)
- N8: Vacuous `test_merge_submodule_ancestry` deleted (mocks away behavior, E2E test covers same scenario)
- N11: SKILL.md Mode C step 1 trimmed — removed rationale, kept actionable instruction

**Recovery runbook executed (worktree-update):**
- All 4 steps via worktree-update-task agent (haiku), checkpoint passed
- 6 commits: C2, C3, M1, M2, C4, C5 fixes

## Pending Tasks

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

- `plans/reports/vet-review-deliverable-fixes.md` — Vet review of N1/N3/N4/N7/N9 fixes (all issues fixed)
- `plans/reports/deliverable-review-worktree-skill-2.md` — Merge readiness review (0C/4M/7m), basis for fixes
- `plans/reports/rca-*-opus.md` — RCA #1-3 authoritative (opus deepened)
- `plans/worktree-skill/design.md` — Worktree implementation design (updated for sibling container)

---
*Handoff by Sonnet. Deliverable review findings fixed, worktree skill merge-ready.*
