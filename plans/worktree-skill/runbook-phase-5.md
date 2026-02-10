### Phase 5: Source Conflict Resolution (take-ours + precommit gate)

## Cycle 5.1: Take-ours strategy

**RED:**

Create test fixture for source code merge conflict between main and worktree branches. Setup a diverged state where both branches modify same source file at same location. Test that `resolve_source_conflicts()` defaults to `--ours` version for all non-session conflict files.

Expected behavior: Each conflicted source file resolved with `git checkout --ours <file>`, then staged with `git add <file>`. Function returns list of resolved files: `["src/claudeutils/worktree/cli.py", "tests/test_worktree_cli.py"]`.

Test verifies:
- Conflict markers present before resolution (`grep -q "^<<<<<<< HEAD" <file>`)
- After resolution, working tree version matches `git show :2:<file>` (ours side)
- File is staged (`git diff --cached --name-only` includes file)
- No conflict markers remain in working tree

Setup requires real git repos with actual merge conflicts (not mocked):
1. Create base repo with initial source file content
2. Branch to worktree branch, modify source file (add function A)
3. Return to main branch, modify same location (add function B)
4. Attempt merge → conflict state
5. Extract conflict list via `git diff --name-only --diff-filter=U`
6. Invoke `resolve_source_conflicts(conflict_list, exclude_patterns=["agents/session.md", "agents/jobs.md", "agents/learnings.md"])`

**GREEN:**

Implement `resolve_source_conflicts()` in `conflicts.py`. Function takes conflict list and exclude patterns, filters to source files only (excluding session context files), then applies take-ours resolution.

Behavior hints:
- Filter conflict list against exclude patterns (deterministic, not fuzzy matching)
- For each source file in filtered list, run subprocess commands: `git checkout --ours <file>` followed by `git add <file>`
- Capture any git command failures and propagate errors
- Return list of successfully resolved files
- Function is deterministic (no agent judgment), relies on mechanical git operations

Implementation approach: subprocess wrappers for git checkout and git add, error handling for missing files or git failures, return resolved paths for caller verification.

---

## Cycle 5.2: Precommit gate validates ours

**RED:**

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

**GREEN:**

Extend `merge.py` Phase 3 parent merge logic to invoke precommit gate after source conflict resolution. After all conflicts resolved and staged, commit merge, then immediately run precommit validation.

Behavior hints:
- After resolving conflicts (session files + source files), check for remaining conflicts via `git diff --name-only --diff-filter=U`
- If none remain, commit with merge message: `git commit -m "<merge-message>"`
- Capture merge commit hash from git output or `git rev-parse HEAD`
- Run precommit: `subprocess.run(["just", "precommit"], check=False, capture_output=True)`
- Check precommit exit code (not output parsing)
- On success (exit 0), output commit hash to stdout, exit 0
- On failure, proceed to Cycle 5.3 fallback logic (not implemented yet)

Implementation approach: subprocess for precommit with timeout (some checks may be slow), stderr capture for failure diagnosis, commit hash extraction via `git rev-parse HEAD` after commit succeeds, stdout write for machine-readable output.

**CRITICAL:** Precommit runs AFTER merge commit, not before. Precommit failure does NOT roll back merge commit (NFR-4). User will fix and amend or re-run merge.

---

## Cycle 5.3: Precommit gate fallback to theirs

**RED:**

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

**GREEN:**

Extend merge logic to implement precommit fallback strategy. After initial precommit failure, parse stderr to identify which files caused failure, apply theirs resolution for those files, retry precommit.

Behavior hints:
- After first precommit failure, capture stderr output
- Parse stderr for file paths (precommit tools often report `<file>: FAILED` or similar patterns)
- If file paths extracted, apply theirs strategy: `git checkout --theirs <file> && git add <file>` for each failed file
- Re-run precommit with same subprocess pattern
- On second success: output commit hash, exit 0
- On second failure: mechanical cleanup sequence (abort merge, clean debris per Phase 4 Cycle 4.10 pattern), format error message with conflict list
- Stderr message format: "Source conflict resolution failed. Manual resolution required for:\n" followed by file list (one per line)
- Exit 1 (conflicts remain)

Implementation approach: stderr parsing with regex for file paths (tool-specific patterns), fallback list management (track which files tried theirs), cleanup invokes same debris removal logic from merge.py Phase 4. Precommit stderr is diagnostic — include in final error output for user debugging.

**Edge case:** Precommit stderr may not contain parseable file paths (some tools report aggregate failures). In this case, fallback strategy cannot isolate failed files. Behavior: skip fallback, go directly to abort + conflict list with message "Precommit failed with unparseable output. Manual resolution required."

**CRITICAL:** Neither ours nor theirs guaranteed to pass precommit. This is heuristic resolution with mechanical validation (D-4). Agent does not judge correctness — precommit is the oracle.
