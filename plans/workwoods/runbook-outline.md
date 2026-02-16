# Workwoods Runbook Outline

## Requirements Mapping

| Requirement | Implementation Phase | Notes |
|-------------|---------------------|-------|
| FR-1: Cross-tree status display | Phase 3, Phase 4 | Aggregation + CLI output |
| FR-2: Vet artifact staleness | Phase 2 | Mtime-based detection |
| FR-3: Plan state inference | Phase 1 | Planstate module core |
| FR-4: Bidirectional worktree merge | Phase 5 | Skill update only |
| FR-5: Per-section session.md merge | Phase 5 | Merge strategies implementation |
| FR-6: Eliminate jobs.md | Phase 6 | Planstate adoption + archive |
| NFR-1: No writes during status | All phases | Read-only aggregation pattern |
| NFR-2: No unversioned state | All phases | Each tree owns session.md |
| NFR-3: Git-native | All phases | All state versioned or computed |
| C-1: Filesystem mtime | Phase 2 | Captures uncommitted edits |
| C-2: Git commit hash anchor | Phase 3 | Stable work counting |
| C-3: Sandbox permissions | All phases | No new config needed |

## Phase Structure

### Phase 1: Plan State Inference (type: tdd)

**Scope:** `src/claudeutils/planstate/` module (inference.py, models.py, __init__.py)

**Complexity:** ~8 cycles (status levels, next action derivation, gate attachment, helper extraction, edge cases)

**Model:** sonnet

**Cycles:**
- Cycle 1.1: Empty directory detection (not a plan)
- Cycle 1.2: Requirements status detection (requirements.md only)
- Cycle 1.3: Designed status detection (design.md exists)
- Cycle 1.4: Planned status detection (runbook-phase-*.md files)
- Cycle 1.5: Ready status detection (steps/ + orchestrator-plan.md)
- Cycle 1.6: Next action derivation from status
- Cycle 1.7: Gate attachment from vet status (integration with Phase 2)
- Cycle 1.8: list_plans() helper for directory scanning

**Dependencies:** None (foundation phase)

---

### Phase 2: Vet Staleness Detection (type: tdd)

**Scope:** `src/claudeutils/planstate/vet.py`

**Complexity:** ~7 cycles (source types, mtime comparison, missing reports, iterative reviews, escalation variants)

**Model:** sonnet

**Cycles:**
- Cycle 2.1: Outline.md → reports/outline-review.md mapping
- Cycle 2.2: Design.md → reports/design-review.md mapping
- Cycle 2.3: runbook-outline.md → reports/runbook-outline-review.md mapping
- Cycle 2.4: runbook-phase-N.md → reports/phase-N-review.md mapping with fallback glob
- Cycle 2.5: Mtime comparison (stale = source_mtime > report_mtime)
- Cycle 2.6: Missing report handling (report_mtime = None → stale = True)
- Cycle 2.7: Iterative review handling (highest-numbered or highest-mtime wins)

**Dependencies:** Phase 1 (planstate module must exist for integration)

---

### Phase 3: Cross-Tree Aggregation (type: tdd)

**Scope:** `src/claudeutils/planstate/aggregation.py`

**Complexity:** ~8 cycles (git worktree parsing, per-tree data, commits since handoff, task summary, sorting)

**Model:** sonnet

**Cycles:**
- Cycle 3.1: Parse `git worktree list --porcelain` output
- Cycle 3.2: Detect main tree (is_main=True, slug=None)
- Cycle 3.3: Commits since handoff (git log anchor on agents/session.md)
- Cycle 3.4: Latest commit subject + timestamp
- Cycle 3.5: Dirty state detection (git status --porcelain)
- Cycle 3.6: Task summary from session.md (first pending task)
- Cycle 3.7: Per-tree plan discovery (list_plans per tree)
- Cycle 3.8: Sort trees by latest_commit_timestamp descending

**Dependencies:** Phases 1 + 2 (aggregates planstate + vet status)

---

### Phase 4: Upgraded wt-ls CLI (type: tdd)

**Scope:** `src/claudeutils/worktree/cli.py` (ls command)

**Complexity:** ~6 cycles (flag addition, rich output formatting, backward compat, integration)

**Model:** sonnet

**Cycles:**
- Cycle 4.1: Add --porcelain flag to ls command
- Cycle 4.2: Porcelain mode preserves existing behavior
- Cycle 4.3: Rich mode header format (slug/branch, dirty indicator, commits)
- Cycle 4.4: Task line formatting (first pending task)
- Cycle 4.5: Plan line formatting (plan-name [status] → next-action)
- Cycle 4.6: Gate line formatting (advisory condition display)

**Dependencies:** Phase 3 (CLI consumes aggregation)

---

### Phase 5: Merge Strategies + Skill Update (type: mixed)

**Scope:**
- TDD: `src/claudeutils/worktree/merge.py`, `src/claudeutils/worktree/session.py`
- General: `agent-core/skills/worktree/SKILL.md`, `agent-core/fragments/execute-rule.md`

**Complexity:** ~10 TDD cycles + 4 general steps

**Model:** sonnet (TDD), opus (skill edits)

**Execution Dependency:** worktree-merge-data-loss Track 1 + Track 2 must be deployed before starting this phase.

**TDD Cycles:**
- Cycle 5.1: Section identification via find_section_bounds()
- Cycle 5.2: Status line strategy (keep ours)
- Cycle 5.3: Completed This Session strategy (keep ours)
- Cycle 5.4: Pending Tasks strategy (existing additive logic preserved)
- Cycle 5.5: Worktree Tasks strategy (keep ours)
- Cycle 5.6: Reference Files strategy (keep ours)
- Cycle 5.7: Next Steps strategy (keep ours)
- Cycle 5.8: extract_blockers() function in session.py
- Cycle 5.9: Blockers evaluation strategy (extract, tag with [from: slug], append)
- Cycle 5.10: Integration test for per-section merge

**General Steps:**
- Step 5.11: Update worktree skill Mode C (no auto-rm after merge)
  - Model: opus
  - File: agent-core/skills/worktree/SKILL.md
  - Change: Mode C step 3 exit code 0 path → "Output merge success. To remove: `wt-rm <slug>`"

- Step 5.12: Update execute-rule.md STATUS (use planstate instead of jobs.md)
  - Model: opus
  - File: agent-core/fragments/execute-rule.md
  - Change: Replace jobs.md reads with list_plans() calls
  - Change: Unscheduled Plans section uses planstate instead of parse_jobs_md()

- Step 5.13: Update execute-rule.md Unscheduled Plans (full transition)
  - Model: opus
  - File: agent-core/fragments/execute-rule.md (continuation)
  - Change: Remove jobs.md status value reference, use PlanState.status

- Step 5.14: Verify Phase 5 changes with integration test
  - Model: sonnet
  - Action: Run test suite for merge + session parsing
  - Expected: All tests pass

**Dependencies:** Phase 1 (execute-rule.md uses planstate), worktree-merge-data-loss deployment

---

### Phase 6: jobs.md Elimination + Archive (type: mixed)

**Scope:**
- TDD: `src/claudeutils/validation/planstate.py`
- General: Migration, removals, skill updates

**Complexity:** ~6 TDD cycles + 8 general steps

**Model:** sonnet (TDD), opus (skill edits), sonnet (removals)

**TDD Cycles:**
- Cycle 6.1: Validator detects missing artifacts (no recognized files in plans/<name>/)
- Cycle 6.2: Validator checks artifact consistency (steps/ without runbook-phase-*.md)
- Cycle 6.3: Validator warns on plan-archive orphans (referenced plans not deleted)
- Cycle 6.4: Integration with validation CLI (replace jobs validator)
- Cycle 6.5: Validator registration in cli.py
- Cycle 6.6: Remove jobs validator tests, add planstate validator tests

**General Steps:**
- Step 6.7: Create agents/plan-archive.md via jobs.md migration
  - Model: sonnet
  - Action: Read jobs.md Complete section, use git history for enrichment
  - Output: agents/plan-archive.md with H2 entries (plan summaries)

- Step 6.8: Update handoff skill (write plan-archive.md instead of jobs.md)
  - Model: opus
  - File: agent-core/skills/handoff/SKILL.md
  - Change: Plan completion writes to plan-archive.md

- Step 6.9: Update design skill (A.1 loads plan-archive.md on demand)
  - Model: opus
  - File: agent-core/skills/design/SKILL.md
  - Change: Phase A.1 research loads plan-archive.md

- Step 6.10: Remove jobs.md from CLAUDE.md @-reference
  - Model: sonnet
  - File: CLAUDE.md
  - Change: Remove `@agents/jobs.md` line

- Step 6.11: Remove validation/jobs.py and CLI integration
  - Model: sonnet
  - Files: src/claudeutils/validation/jobs.py, cli.py (remove import/call)
  - Action: Delete jobs.py, remove from cli.py _run_all_validators()

- Step 6.12: Remove _resolve_jobs_md_conflict() from merge.py
  - Model: sonnet
  - File: src/claudeutils/worktree/merge.py
  - Change: Remove function and call from _phase3_merge_parent()

- Step 6.13: Remove jobs.md from merge exempt_paths
  - Model: sonnet
  - File: src/claudeutils/worktree/merge.py
  - Change: Remove "agents/jobs.md" from exempt_paths set in _phase1_validate_clean_trees()

- Step 6.14: Update worktree skill Mode B (read planstate instead of jobs.md)
  - Model: opus
  - File: agent-core/skills/worktree/SKILL.md
  - Change: Parallel group analysis uses list_plans() instead of parse_jobs_md()

**Dependencies:** Phases 1 + 5 (completes elimination after adoption)

---

## Key Decisions Reference

- **D-1:** New planstate module (not worktree extension) — conceptual independence
- **D-2:** Upgrade existing wt-ls (don't create new command) — avoid command proliferation
- **D-3:** Direct jobs.md replacement — no transition period, phases are the migration
- **D-4:** Bidirectional merge = skill update only — CLI already correct
- **D-5:** New code for Blockers evaluation — per-section strategies require new logic
- **D-6:** worktree-merge-data-loss execution dependency — Track 1+2 before Phase 5
- **D-7:** Workflow gates as advisory — displayed, not enforced
- **D-8:** Plan archive on demand — loaded at design A.1 and RCA, not in CLAUDE.md

## Complexity Distribution

| Phase | Cycles/Steps | Type | Model | Estimated Effort |
|-------|-------------|------|-------|-----------------|
| 1 | 8 cycles | TDD | sonnet | Medium (new module setup) |
| 2 | 7 cycles | TDD | sonnet | Medium (mtime logic + conventions) |
| 3 | 8 cycles | TDD | sonnet | High (git interaction complexity) |
| 4 | 6 cycles | TDD | sonnet | Low-Medium (CLI output formatting) |
| 5 | 10 cycles + 4 steps | Mixed | sonnet + opus | High (merge refactor + skill edits) |
| 6 | 6 cycles + 8 steps | Mixed | sonnet + opus | Medium (validator + removals) |
| **Total** | **45 cycles + 12 steps** | | | **~57 items** |

## Checkpoints

**Light checkpoints** (Fix + Functional) at:
- End of Phase 1 (foundation module complete)
- End of Phase 2 (vet integration complete)
- End of Phase 3 (aggregation complete)
- End of Phase 4 (CLI upgrade complete)

**Full checkpoint** (Fix + Vet + Functional) at:
- End of Phase 5 (merge strategies complete, before elimination)
- End of Phase 6 (final validation before completion)

## Expansion Guidance

**Phase 1 expansion notes:**
- Use parametrized tests with tmp_path fixtures for all status levels
- Test edge cases: empty dirs, reports/ only, mixed artifacts
- Helper function extraction: list_plans() scans all plan directories
- Gate computation integrated after status inference

**Phase 2 expansion notes:**
- Use os.utime() in tests to set known mtimes
- Cover all source artifact types from vet chain conventions table
- Handle iterative review numbering (highest-numbered file wins)
- Handle escalation variants (*-opus.md suffix)
- Only most recent report counts per source artifact

**Phase 3 expansion notes:**
- Real git repos via tmp_path fixtures (same pattern as worktree tests)
- No mocked subprocess for git operations
- Create main repo with worktrees for integration tests
- Test commit counting with and without session.md anchor
- Cover dirty/clean states, multiple trees, main-only scenarios

**Phase 4 expansion notes:**
- CLI output assertions for rich format structure
- Backward compatibility tests for --porcelain flag
- Integration test with real worktrees verifying plan status display
- Verify correct use of aggregate_trees() from planstate.aggregation

**Phase 5 expansion notes:**
- TDD: Refactor _resolve_session_md_conflict() to call per-section strategies
- TDD: New extract_blockers() function returns blocker items as line groups
- TDD: Tag blockers with [from: <slug>] before appending to ours
- General: Skill edits require opus model per design directive
- Verify external dependency deployed before starting Phase 5

**Phase 6 expansion notes:**
- TDD: Validator checks artifact presence and consistency
- TDD: Plan-archive orphan detection (referenced plans should be deleted)
- General: Migration enriches entries using git log for commit messages
- General: Update three skills (handoff, design, worktree) with opus
- General: Removals are mechanical (sonnet sufficient)

**Classification table binding (Phase 5):**
The D-5 per-section merge strategies table is binding on planners and implementers. Follow strategies literally:
- Status line: Squash (keep ours)
- Completed This Session: Squash (keep ours)
- Pending Tasks: Additive (existing logic)
- Worktree Tasks: Preserve main's (keep ours)
- Blockers/Gotchas: Evaluate (extract, tag, append)
- Reference Files: Squash (keep ours)
- Next Steps: Squash (keep ours)

**Investigation prerequisites:**
- Phase 3 cycles touching git operations need prerequisite: Read explore-worktree-cli.md to understand worktree discovery
- Phase 4 cycles need prerequisite: Read current cli.py ls implementation
- Phase 5 merge cycles need prerequisite: Read current _resolve_session_md_conflict() and find_section_bounds()
- Phase 6 validator cycles need prerequisite: Read validation/jobs.py structure

## Affected Files Summary

**New files (6):**
- src/claudeutils/planstate/__init__.py
- src/claudeutils/planstate/models.py
- src/claudeutils/planstate/inference.py
- src/claudeutils/planstate/vet.py
- src/claudeutils/planstate/aggregation.py
- src/claudeutils/validation/planstate.py
- agents/plan-archive.md

**Modified files (11):**
- src/claudeutils/worktree/cli.py (Phase 4)
- src/claudeutils/worktree/merge.py (Phase 5, Phase 6)
- src/claudeutils/worktree/session.py (Phase 5)
- src/claudeutils/validation/cli.py (Phase 6)
- agent-core/skills/worktree/SKILL.md (Phase 5, Phase 6)
- agent-core/fragments/execute-rule.md (Phase 5)
- agent-core/skills/handoff/SKILL.md (Phase 6)
- agent-core/skills/design/SKILL.md (Phase 6)
- CLAUDE.md (Phase 6)

**Deleted files (2):**
- src/claudeutils/validation/jobs.py (Phase 6)
- agents/jobs.md (Phase 6)

**Test files (new):**
- tests/test_planstate_inference.py (Phase 1)
- tests/test_planstate_vet.py (Phase 2)
- tests/test_planstate_aggregation.py (Phase 3)
- tests/test_worktree_ls_upgrade.py (Phase 4)
- tests/test_worktree_merge_sections.py (Phase 5)
- tests/test_validation_planstate.py (Phase 6)

**Test files (deleted):**
- tests/test_validation_jobs.py (Phase 6)

## Execution Model

**Per-phase model assignments:**
- Phase 1-4: sonnet (standard TDD implementation)
- Phase 5 TDD: sonnet
- Phase 5 general (skill edits): opus (per design directive)
- Phase 6 TDD: sonnet
- Phase 6 general skill edits: opus (handoff, design, worktree skills)
- Phase 6 general removals: sonnet (mechanical deletions)

**Rationale for opus in skill edits:**
Skill modifications affect agent behavior and workflow coordination. Design specifies opus for these edits to ensure behavioral correctness and rule alignment.

## External Dependencies

**Execution dependency:** worktree-merge-data-loss Track 1 + Track 2 must be deployed before Phase 5 execution. Tracks implement:
- Track 1: Removal guard (prevent accidental deletion of unmerged work)
- Track 2: Merge correctness (prevent data loss during merge)

Phase 5 modifies merge strategies. Running Phase 5 without the data loss protections risks loss of unmerged worktree changes.

**Verification before Phase 5:**
Check that worktree-merge-data-loss changes are in current codebase:
- Grep for removal guard logic in worktree/cli.py (Track 1)
- Grep for merge correctness validation in worktree/merge.py (Track 2)

If not found, STOP and escalate: "worktree-merge-data-loss deployment required before Phase 5."
