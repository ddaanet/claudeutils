# Cycle 3.13

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 3
**Report Path**: `plans/worktree-skill/reports/cycle-3-13-notes.md`

---

## Cycle 3.13: Precommit gate fallback to theirs

**RED — Behavioral Verification:**

Test merge flow where take-ours fails precommit, triggering fallback to theirs. Setup requires conflict scenario where neither ours nor theirs alone satisfies precommit (requires manual resolution).

Expected behavior:
1. Take-ours resolution applied
2. Precommit fails (exit non-zero)
3. Merge logic parses precommit stderr for failed files
4. For files that failed precommit, apply `git checkout --theirs <file>` and re-stage
5. Re-run `just precommit`
6. If theirs passes: output merge commit hash, exit 0
7. If theirs also fails: `git merge --abort`, clean debris, output conflict list to stderr, exit 1

Test verifies fallback logic when ours fails:
- Initial precommit failure detected (stderr contains "FAILED" or similar)
- Failed files identified from precommit output (parse stderr for file paths)
- Theirs version applied via `git checkout --theirs <file> && git add <file>`
- Second precommit invocation
- **If both fail:** merge aborted, working tree clean, stderr contains conflict list with message "Manual resolution required for: <files>", exit 1

Setup conflict scenario: ours version has formatting issue (fails format check), theirs version has linting issue (fails linter). Neither passes precommit alone. Merge must exit with conflict list.

**GREEN — Behavioral Description:**

Extend merge logic to implement precommit fallback strategy. After initial precommit failure, parse stderr to identify which files caused failure, apply theirs resolution for those files, retry precommit.

Behavior hints:
- After first precommit failure, capture stderr output
- Parse stderr for file paths (precommit tools often report `<file>: FAILED` or similar patterns)
- If file paths extracted, apply theirs strategy: `git checkout --theirs <file> && git add <file>` for each failed file
- Re-run precommit with same subprocess pattern
- On second success: output commit hash, exit 0
- On second failure: mechanical cleanup sequence (abort merge, clean debris per Phase 3 Cycle 3.10 pattern), format error message with conflict list
- Stderr message format: "Source conflict resolution failed. Manual resolution required for:\n" followed by file list (one per line)
- Exit 1 (conflicts remain)

Implementation approach: stderr parsing with regex for file paths (tool-specific patterns), fallback list management (track which files tried theirs), cleanup invokes same debris removal logic from merge.py Phase 3. Precommit stderr is diagnostic — include in final error output for user debugging.

**Edge case:** Precommit stderr may not contain parseable file paths (some tools report aggregate failures). In this case, fallback strategy cannot isolate failed files. Behavior: skip fallback, go directly to abort + conflict list with message "Precommit failed with unparseable output. Manual resolution required."

**CRITICAL:** Neither ours nor theirs guaranteed to pass precommit. This is heuristic resolution with mechanical validation (D-4). Agent does not judge correctness — precommit is the oracle.

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-3-13-notes.md

### Phase 4: SKILL.md (orchestration)

**Model:** opus (workflow artifact authoring)
**Files:** `agent-core/skills/worktree/SKILL.md`
**Depends on:** Phases 0-3 (all CLI implementation)
**Checkpoint:** Full with design-vet-agent (workflow artifact requires opus review)

**Prerequisites:**
- Load `plugin-dev:skill-development` before starting (imperative/infinitive style guide)
- Review design decisions D-5 (CLI/skill boundary), D-9 (no plan-specific agent)
- Understand D+B hybrid pattern (every skill step opens with tool call)

**Context:** The CLI implementation is complete. This phase creates the `/worktree` skill that orchestrates the ceremony: session.md manipulation, handoff/commit chain, parallel detection, merge coordination, and error communication. The skill is the user interface; the CLI is the implementation.

---
