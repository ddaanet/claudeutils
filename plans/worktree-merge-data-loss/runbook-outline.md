# Worktree Merge Data Loss — Runbook Outline

**Design**: `plans/worktree-merge-data-loss/design.md`
**Model**: haiku
**Status**: Draft outline

---

## Requirements Mapping

| Requirement | Phase | Steps/Cycles | Notes |
|-------------|-------|--------------|-------|
| FR-1: Branch classification (merged/focused/unmerged) | 1 | 1.1-1.3 | Helper functions + classification logic |
| FR-2: Refuse removal with unmerged history, exit 1 | 1 | 1.4 | Guard refusal with exit 1 |
| FR-3: Allow removal of focused-session-only branches | 1 | 1.3 | Marker text detection |
| FR-4: Exit codes (0/1/2) | 1 | 1.4 | Implemented in guard logic |
| FR-5: No destructive commands in output | 1 | 1.5 | Message cleanup |
| FR-6: MERGE_HEAD checkpoint, exit 2 when lost | 1 | 1.6-1.8 | Three-branch checkpoint logic |
| FR-7: Post-merge ancestry validation | 1 | 1.9 | Defense-in-depth validation |
| FR-8: Report removal type in success message | 1 | 1.5 | Success message differentiation |
| FR-9: Skill Mode C handles rm exit 1 | 2 | 2.1 | Prose update to SKILL.md |

---

## Phase Structure

### Phase 1: Safety Guards and Merge Correctness (type: tdd)

**Scope:** Implement removal safety guard (Track 1) and merge correctness fixes (Track 2). All behavioral changes to cli.py, merge.py, utils.py, with comprehensive test coverage.

**Estimated complexity:** 11 cycles, haiku execution

**Key design decisions:**
- D-1: Focused session detection via marker text `"Focused session for {slug}"`
- D-2: rm exit codes: 0 (removed), 1 (refused), 2 (error)
- D-3: No destructive instructions in CLI output
- D-4: MERGE_HEAD checkpoint before single-parent commit
- D-5: Post-merge ancestry validation with `merge-base --is-ancestor`
- D-6: Guard runs before ALL destructive operations
- D-7: `_is_branch_merged` helper in utils.py (shared)

#### Cycle 1.1: Add _is_branch_merged helper to utils.py
- **Integration:** Shared helper used by both cli.py (rm guard) and merge.py (MERGE_HEAD checkpoint)
- Test: Branch merged status detection using git merge-base

#### Cycle 1.2: Add _classify_branch helper to cli.py
- **Integration:** Used by rm guard to determine branch type
- **Dependencies:** Uses _is_branch_merged from Cycle 1.1
- Test: Branch classification (count + focused marker detection), handles orphan branches

#### Cycle 1.3: Implement rm guard logic for focused-session-only branches
- **Integration:** Guard inserted before destructive operations in rm
- **Dependencies:** Uses _classify_branch from Cycle 1.2
- Test: Focused-session-only branch removal succeeds with appropriate message

#### Cycle 1.4: Implement rm guard refusal for real-history unmerged branches
- **Integration:** Complete guard logic with exit codes
- **Dependencies:** Extends Cycle 1.3 guard
- Test: Unmerged real history refused (exit 1), worktree directory NOT removed

#### Cycle 1.5: Update rm success messages and remove destructive suggestions
- **Integration:** Final rm messaging cleanup
- **Dependencies:** Extends Cycle 1.4
- Test: No `git branch -D` in output, reports removal type correctly

#### Cycle 1.6: Implement MERGE_HEAD checkpoint in Phase 4
- **Integration:** Add branch-merged check before single-parent commit path
- **Dependencies:** Uses _is_branch_merged from Cycle 1.1
- Test: Simulated lost MERGE_HEAD with unmerged branch exits 2

#### Cycle 1.7: Handle already-merged idempotency in Phase 4
- **Integration:** elif path only executes for merged branches
- **Dependencies:** Extends Cycle 1.6 checkpoint logic
- Test: Re-merge already-merged branch succeeds without error

#### Cycle 1.8: Handle no-MERGE_HEAD + no-staged + unmerged case
- **Integration:** else path with branch-merged check
- **Dependencies:** Extends Cycle 1.7 flow
- Test: No MERGE_HEAD, no staged, branch not merged exits 2

#### Cycle 1.9: Add post-merge ancestry validation with diagnostic logging
- **Integration:** _validate_merge_result called after commit, before precommit; includes parent count diagnostic
- **Dependencies:** Uses _is_branch_merged from Cycle 1.1
- Test: Branch ancestry check after merge (exits 2 if branch not ancestor), parent count logged when <2 (warning)

#### Cycle 1.10: Integration test — parent repo file preservation (Track 2)
- **Integration:** End-to-end test for original bug scenario — verifies MERGE_HEAD checkpoint + ancestry validation working together
- **RED assertion:** Create worktree branch with both parent repo changes (e.g., add file `parent-change.md`) AND submodule changes → merge → verify parent repo file exists in merge result commit (tests that single-parent commit bug is fixed)
- Test: Parent repo file preservation across merge (regression test for data loss bug)

#### Cycle 1.11: Integration test — orphan branch handling (Track 1)
- **Integration:** Edge case coverage for rm guard with branch that has no merge-base (orphan branch)
- **RED assertion:** Create orphan branch (git checkout --orphan) with 1+ commits → create worktree pointing to it → rm worktree → exit 1 with "Branch {slug} is orphaned (no common ancestor). Merge first." message AND worktree directory still exists (regression test: guard must prevent directory removal)
- Test: Orphan branch refused by rm guard with specific message, directory preserved

**Checkpoint:** Full checkpoint after Phase 1
- Fix: All cycles complete, code committed
- Vet: vet-fix-agent review with execution context (scope: all Phase 1 changes)
- Functional: Run reproduction scenario — create worktree with parent repo changes, merge, verify rm refuses unmerged branch (if any), verify parent repo files present in merge result

---

### Phase 2: Skill Update for rm Exit 1 Handling (type: general)

**Scope:** Update worktree skill Mode C to handle rm exit 1 after successful merge.

**Estimated complexity:** 1 step, haiku execution

#### Step 2.1: Update SKILL.md Mode C for rm exit 1 escalation

**Objective:** Document rm exit 1 handling after successful merge (exit 0).

**Script Evaluation:** Small (prose addition, <25 lines)

**Implementation:**
- Read `agent-core/skills/worktree/SKILL.md` Mode C, step 3
- After "Exit code 0 (success)" section, before "Parse merge exit code 1", add:

> `rm` will refuse (exit 1) if the branch has unmerged commits. If this happens after a successful merge (exit 0), the merge itself may be incomplete. Escalate to user: "Merge may be incomplete — branch {slug} has unmerged commits after merge reported success."
>
> Do not retry `rm` or force-delete. The mismatch between merge-success and rm-refusal indicates a merge correctness issue.

**Expected Outcome:** Skill updated with rm exit 1 handling guidance

**Error Conditions:** File not found, wrong section identified

**Validation:** Read updated Mode C, verify prose present

---

## Key Constraints

**Testing:**
- All tests use real git repos (tmp_path, `repo_with_submodule` fixture)
- No mocked subprocess for git operations (per testing.md)
- Error injection only for specific failure scenarios

**Implementation:**
- Guard runs BEFORE any destructive operation (D-6)
- Shared helper in utils.py, not duplicated (D-7)
- Exit codes: 0 (success), 1 (refused), 2 (error) — consistent across both rm and merge (D-2)

**Scope boundaries:**
- In scope: rm guard, Phase 4 MERGE_HEAD checkpoint, ancestry validation, skill update
- Out of scope: Phase 2/3 merge logic, submodule resolution, conflict auto-resolution, merge strategy

---

## Design Reference

Full design at: `plans/worktree-merge-data-loss/design.md`

**Key sections:**
- Architecture: Track 1 (cli.py rm), Track 2 (merge.py Phase 4), Track 3 (SKILL.md)
- Helpers: _is_branch_merged (shared), _classify_branch (rm-specific)
- Guard Logic: insertion point, flow, exit codes
- MERGE_HEAD Checkpoint: three-path flow, validation
- Post-Merge Validation: ancestry check, diagnostic logging

---

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Cycle granularity:**
- Each cycle tests one branch point or error condition
- Foundation-first: helper functions → guard logic → checkpoint logic
- Integration tests last (after all unit cycles)
- No further consolidation recommended — 11 cycles test distinct branch points

**Test patterns (from test_worktree_merge_parent.py):**
- Use `repo_with_submodule` fixture for main repo setup
- Use `commit_file` fixture for creating test commits
- Use `mock_precommit` fixture to bypass precommit validation
- Use `CliRunner().invoke(worktree, [cmd, ...])` for CLI invocation
- Assert on exit codes, stderr content, and filesystem state

**RED phase assertions:**
- Behavioral verification (per testing.md): assert on content, not just structure
- Exit codes AND stderr messages for error cases
- Filesystem state verification (worktree directory existence, branch existence)
- No vacuous assertions (per testing.md): distinguish correct output from empty/default
- Integration tests (C1.10-C1.11) include specific scenario verification (parent repo file exists, directory preserved on refusal)

**GREEN phase implementation:**
- Track 1 (rm guard): Cycles 1.1-1.5, 1.11 — shared helper → classification → guard logic → messaging → orphan edge case
- Track 2 (merge correctness): Cycles 1.6-1.10 — checkpoint logic → idempotency → no-op case → validation → integration test
- Dependencies: C1.6 depends on C1.1 (_is_branch_merged helper) — ensure C1.1 completes first

**File growth monitoring:**
- cli.py: baseline 382 lines + ~35 LOC (guard logic) = 417 projected (borderline)
- If implementation exceeds 420 lines during expansion, extract to cli_guards.py module
- Split point: _classify_branch and guard logic to separate module
- merge.py: baseline 299 lines + ~25 LOC = 324 projected (safe)
- utils.py: baseline 38 lines + ~8 LOC = 46 projected (safe)

**Checkpoint validation detail:**
- Functional checkpoint includes reproduction scenario: parent repo changes + merge + rm behavior
- Verifies both tracks working together: merge preserves files AND rm refuses unmerged branches
- Use real git operations (no mocks) per testing.md conventions

**Prerequisite validation:**
- Transformation cycles (delete, modify): self-contained
- Creation cycles (new tests, new helpers): include prerequisite to read relevant implementation context
