# Cycle 7.12

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.12: Phase 4 precommit validation — run and check exit code

**Objective:** Run precommit validation after successful merge, exit 1 on failure.

**RED Phase:**

**Test:** `test_merge_precommit_validation`
**Assertions:**
- After successful merge (no conflicts): commit with message `🔀 Merge <slug>`
- Only commit if staged changes exist (check `git diff --cached --quiet`)
- Then run `just precommit` (capture exit code and stderr)
- If precommit passes (exit 0): exit 0 with success message
- If precommit fails (exit ≠ 0): exit 1 with message "Precommit failed after merge" + stderr
- Exit codes: 0 (success), 1 (conflicts or precommit failure), 2 (fatal error)

**Expected failure:** AssertionError: no precommit run, or wrong exit code, or no commit before precommit

**Why it fails:** Phase 4 precommit validation not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_precommit_validation -v`

---

**GREEN Phase:**

**Implementation:** Add merge commit and precommit validation

**Behavior:**
- After conflict resolution (or clean merge from 7.7): check for staged changes
- Run `git diff --cached --quiet` (exit ≠ 0 means changes staged)
- If staged changes: `git commit -m "🔀 Merge <slug>"`
- If no staged changes: skip commit (no-op merge)
- Then run `just precommit` with `check=False` (capture exit code and stderr)
- If exit code 0: print success, exit 0
- If exit code ≠ 0: print failure message with stderr, exit 1

**Approach:** Staged changes check, commit, precommit run, exit code handling

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add merge commit in `merge` command (Phase 4 start)
  Location hint: After Phase 3 conflict handling
- File: `src/claudeutils/worktree/cli.py`
  Action: Check for staged changes before commit
  Location hint: `git diff --cached --quiet`, commit if exit ≠ 0
- File: `src/claudeutils/worktree/cli.py`
  Action: Run `just precommit` and capture result
  Location hint: subprocess with check=False
- File: `src/claudeutils/worktree/cli.py`
  Action: Handle precommit result (success message or failure exit)
  Location hint: Conditional on exit code

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_precommit_validation -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 7 tests still pass

---

**Checkpoint: Post-Phase 7**

**Type:** Full checkpoint (Fix + Vet + Functional)

**Process:**
1. **Fix:** Run `just dev`. If failures, sonnet quiet-task diagnoses and fixes. Commit when passing.
2. **Vet:** Review all Phase 1-7 changes for quality, clarity, design alignment. Apply all fixes. Commit.
3. **Functional:** Review all implementations against design.
   - Check: Is 4-phase ceremony implemented completely? Do auto-resolutions actually work?
   - Check: Are exit codes correct (0=success, 1=conflicts/precommit, 2=fatal)?
   - Check: Is session.md task extraction correct (regex matching, theirs-only detection)?
   - If stubs found: STOP, report which implementations need real behavior
   - If all functional: TDD implementation complete, proceed to Phase 8 (non-code artifacts)

**Rationale:** Phase 7 completes TDD implementation. Final full checkpoint validates all 40 TDD cycles before non-code artifacts.
