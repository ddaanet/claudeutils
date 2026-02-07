# Step 8

**Plan**: `plans/validator-consolidation/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Step 8: Update Justfile + Remove Old Scripts + E2E Verify

**Objective**: Wire precommit integration (FR-6) and clean up old scripts.

**Execution Model**: Haiku

**Implementation**:

1. Update `justfile` precommit recipe:
   - Replace:
     ```
     agent-core/bin/validate-tasks.py agents/session.md agents/learnings.md
     agent-core/bin/validate-learnings.py agents/learnings.md
     agent-core/bin/validate-decision-files.py
     agent-core/bin/validate-memory-index.py agents/memory-index.md
     agent-core/bin/validate-jobs.py
     ```
   - With:
     ```
     claudeutils validate
     ```

2. Remove old scripts:
   - Delete `agent-core/bin/validate-learnings.py`
   - Delete `agent-core/bin/validate-memory-index.py`
   - Delete `agent-core/bin/validate-decision-files.py`
   - Delete `agent-core/bin/validate-tasks.py`
   - Delete `agent-core/bin/validate-jobs.py`

3. Verify existing test for learning-ages still imports correctly:
   - Check `tests/test_learning_ages.py` — it imports from `agent-core/bin/learning-ages.py` (NOT a validator being removed), so should be unaffected
   - Run `pytest tests/test_learning_ages.py -q` to confirm

4. Run full verification:
   - `pytest -q` (entire test suite)
   - `just precommit` (end-to-end with new `claudeutils validate`)
   - `mypy src/claudeutils/validation/`

**Expected Outcome**: Precommit uses unified validator, old scripts gone, all tests green.

**Success Criteria**: `just precommit` passes in clean working tree, no old validate-*.py scripts remain in agent-core/bin/.

**Phase 3 Checkpoint**: `just precommit` on clean working tree passes. Full test suite green. Old scripts deleted.

---
