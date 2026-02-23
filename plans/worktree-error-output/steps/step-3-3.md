# Step 3.3

**Plan**: `plans/worktree-error-output/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Step 3.3: Precommit validation

**Objective:** Verify full quality gate passes before handoff.

**Script Evaluation:** Direct

**Execution Model:** Haiku

**Implementation:**
```
just precommit
```

If failures:
- Lint/type errors from the new `Never` import or `_fail()` signature → fix in cli.py
- Test failures from the `err=True` changes → check if existing tests assert on `result.output`
  (output captured by CliRunner) vs stderr. Tests asserting `result.output` already pass;
  if any test captured stderr directly (unlikely), update the assertion.

**Expected Outcome:** All checks pass, clean tree ready for commit.

**Error Conditions:** Escalate to sonnet if unexpected failures.

**Validation:** `just precommit` exits 0
