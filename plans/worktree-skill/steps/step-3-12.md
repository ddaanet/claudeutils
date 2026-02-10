# Cycle 3.12

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 3
**Report Path**: `plans/worktree-skill/reports/cycle-3-12-notes.md`

---

## Cycle 3.12: Precommit gate validates ours

**RED — Behavioral Verification:**

Test complete merge flow with source conflicts that pass precommit after take-ours resolution. Setup requires conflict scenario where ours version is correct (precommit passes).

Expected behavior: After `resolve_source_conflicts()` completes, merge logic runs `just precommit`. On success (exit 0), merge commits with merge message and outputs commit hash to stdout.

Test verifies:
- Merge invoked with source conflicts
- `resolve_source_conflicts()` applied
- `just precommit` executed in subprocess
- Precommit exits 0 (success)
- `git log -1 --format=%H` returns new merge commit hash
- Stdout contains exactly the commit hash (machine-readable output)
- Working tree is clean after merge (no staged or unstaged changes)

Setup conflict scenario where ours version has correct formatting, imports, and logic (precommit will pass). Example: worktree added unused import (linter failure), main branch has clean import. Take-ours preserves main's clean state.

**GREEN — Behavioral Description:**

Extend `merge.py` Phase 3 parent merge logic to invoke precommit gate after source conflict resolution. After all conflicts resolved and staged, commit merge, then immediately run precommit validation.

Behavior hints:
- After resolving conflicts (session files + source files), check for remaining conflicts via `git diff --name-only --diff-filter=U`
- If none remain, commit with merge message: `git commit -m "<merge-message>"`
- Capture merge commit hash from git output or `git rev-parse HEAD`
- Run precommit: `subprocess.run(["just", "precommit"], check=False, capture_output=True)`
- Check precommit exit code (not output parsing)
- On success (exit 0), output commit hash to stdout, exit 0
- On failure, proceed to Cycle 3.13 fallback logic (not implemented yet)

Implementation approach: subprocess for precommit with timeout (some checks may be slow), stderr capture for failure diagnosis, commit hash extraction via `git rev-parse HEAD` after commit succeeds, stdout write for machine-readable output.

**CRITICAL:** Precommit runs AFTER merge commit, not before. Precommit failure does NOT roll back merge commit (NFR-4). User will fix and amend or re-run merge.

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-3-12-notes.md

---
