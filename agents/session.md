# Session Handoff: 2026-02-24

**Status:** Sync-to-parent sandbox bypass documented in CLAUDE.md and project-tooling.md.

## Completed This Session

**Recall pass pipeline (prior sessions, carried forward):**
- `plans/recall-pass/requirements.md` — 11 FRs, 3 NFRs, 5 constraints
- `plans/recall-pass/outline.md` — 10 key decisions, all open questions resolved
- 4 pipeline skill files edited with recall artifact generation, augmentation, injection, and review recall
- `/recall` skill created — interactive recall for sessions bypassing the pipeline

**Deliverable review (this session):**
- Full review: 10 files, 170 net lines, all agentic prose
- 4 major findings, all fixed in-session:
  1. Outline Q-4/D-7 contradicted FR-11 — outline updated to "progressive recall within design"
  2. FR-11 within-session boundaries lacked recall re-evaluation — added at A.5, C.1 (design), Phase 0.75 (runbook)
  3. Pipeline contracts didn't reflect progressive refinement — T1/T2 updated
  4. Deliverable-review skill lacked lightweight recall fallback — added (from /reflect RCA)
- 2 minor findings: FR-10 artifact format field (deferred), unspecified deliverables (justified)
- Report: `plans/recall-pass/reports/deliverable-review.md`

**Key reframing from discussion:**
- FR-11 rationale changed from "compaction insurance" to "progressive refinement" — each discovery phase changes what recall entries are relevant. Initial broad recall surfaces non-obvious connections for weakly specified tasks; subsequent recalls refine as the task becomes better specified.
- "Re-evaluate" not "re-read" — the cognitive operation is assessing existing entries against new understanding, not re-ingesting content

**/reflect RCA (prior session):**
- Deviation: deliverable review ran without recall pass
- Root cause: skill text said "if absent, proceed without" with no lightweight fallback
- Fix: added lightweight recall fallback to deliverable-review Layer 2

**Sync-to-parent sandbox documentation (this session):**
- Added `(requires dangerouslyDisableSandbox: true)` to `just sync-to-parent` in CLAUDE.md and `agent-core/fragments/project-tooling.md`

## Pending Tasks

- [x] **Recall pass requirements** — implemented via Tier 2 delegation
- [x] **Sync-to-parent sandbox documentation** — update references to document required sandbox bypass | haiku
- [x] **Read tool context optimization test** — run T1 protocol, no dedup confirmed | sonnet
- [ ] **Consolidate recall tooling** — rename `when-resolve.py` → `claudeutils _recall`, remove `..file` syntax; phase out `/when` and `/how` as separate skills, ensure `/recall` covers reactive single-entry lookups; memory-index entry format changes from `/when`+`/how` prefixes → new format; update `src/claudeutils/validation/memory_index_checks.py` and `when` module accordingly | sonnet

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files

**`just sync-to-parent` requires sandbox bypass:**
- Recipe removes and recreates symlinks in `.claude/` — sandbox blocks `rm` on those paths

## Next Steps

Consolidate recall tooling (sonnet): rename `when-resolve.py` → `claudeutils _recall`, phase out `/when`+`/how` as separate skills.

## Reference Files

- `plans/recall-pass/requirements.md` — 11 FRs, FR-11 progressive refinement model
- `plans/recall-pass/outline.md` — pipeline recall pass design, D-7 updated
- `plans/recall-pass/reports/deliverable-review.md` — full review with all findings
- `agents/decisions/pipeline-contracts.md` — T1/T2 progressive refinement in I/O flow
