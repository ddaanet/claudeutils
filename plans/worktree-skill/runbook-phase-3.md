### Phase 3: Merge Orchestration and Source Conflicts

**Complexity:** High
**Cycles:** ~13
**Model:** sonnet (implementation)
**Checkpoint:** full
**Files:** `src/claudeutils/worktree/merge.py`, `src/claudeutils/worktree/conflicts.py`, `tests/test_worktree_merge.py`
**Depends on:** Phase 2 (conflicts.py)

This phase implements the 3-phase merge ceremony (pre-checks, submodule resolution, parent merge) plus source conflict resolution with precommit validation. The merge is fully idempotent and handles both session and source conflicts deterministically.

---

## Cycle 3.1: Phase 1 pre-checks (clean tree gate)

**RED — Behavioral Verification:**

Verify merge enforcement of clean working tree. Create test scenario with dirty repository state (modified source file `src/claudeutils/__init__.py`), invoke `_worktree merge <slug>`, assert exit code 1 and error message to stderr indicating dirty tree prevents merge. Verify session context files (agents/session.md) do NOT trigger dirty tree rejection (exempt from gate).

Expected: Exit 1, stderr contains "dirty" or "uncommitted changes", merge does NOT proceed.

**GREEN — Behavioral Description:**

Implement `merge` subcommand entry point and Phase 1 pre-check logic. Reuse clean-tree validation logic from clean-tree subcommand (filter session context files, check parent + submodule status). Add branch validation (`git rev-parse --verify <slug>`), worktree directory check (warn if `wt/<slug>/` missing but continue — branch-only merge valid). Exit 1 with descriptive error if dirty tree detected. Return early from merge if pre-checks fail.

Design decisions: D-4 (precommit oracle), NFR-4 (mandatory precommit). Approach: extract shared validation logic into helper function, invoke from both clean-tree subcommand and merge Phase 1.

## Cycle 3.2: Phase 2 submodule resolution - no divergence

**RED — Behavioral Verification:**

Verify merge optimization when submodule pointers match. Create worktree with submodule at same commit as parent (no divergence), invoke merge, assert submodule merge phase skipped (no fetch, no merge commands executed). Trace execution to confirm skip path taken. Verify merge proceeds to Phase 3 (parent merge).

Expected: Merge succeeds, no submodule operations in trace, submodule pointer unchanged after merge.

**GREEN — Behavioral Description:**

Implement Phase 2 submodule resolution with no-divergence optimization. Extract worktree submodule commit pointer using `git ls-tree <slug> -- agent-core` (parse 160000 mode line, extract SHA). Extract local submodule commit using `git -C agent-core rev-parse HEAD`. Compare commits — if equal, skip to Phase 3. Log skip reason to stderr for traceability.

Design decisions: D-7 (submodule before parent), D-8 (idempotent). Approach: early return pattern for optimization, git plumbing for pointer extraction.

## Cycle 3.3: Phase 2 submodule resolution - fast-forward

**RED — Behavioral Verification:**

Verify merge optimization when local submodule includes worktree changes (ancestry check passes). Create worktree, make submodule commits in worktree, merge those commits to parent submodule manually (local ahead of worktree), invoke merge, assert submodule merge skipped via ancestry check. Verify `git merge-base --is-ancestor <wt-commit> <local-commit>` detected inclusion.

Expected: Merge succeeds, ancestry check passes, no fetch or merge executed, submodule pointer unchanged.

**GREEN — Behavioral Description:**

Extend Phase 2 with ancestry check optimization. After extracting both commits, run `git -C agent-core merge-base --is-ancestor <wt-commit> <local-commit>`. If exit 0 (ancestor check passes), local already includes worktree changes — skip merge. Log skip reason with commit SHAs. Handle command failure (commit not found) as divergence indicator — proceed to fetch+merge path.

Design decisions: D-8 (idempotent — safe to re-run). Approach: ancestry check as second optimization gate after equality check.

## Cycle 3.4: Phase 2 submodule resolution - diverged commits

**RED — Behavioral Verification:**

Verify merge with diverged submodule commits. Create worktree, make distinct submodule commit in worktree (file A), make different commit in parent submodule (file B), invoke merge, assert submodule merge executes (fetch from worktree path, merge via `--no-edit`, stage, commit). Verify both files A and B present in final submodule state. Verify merge commit message follows pattern `🔀 Merge agent-core from <slug>`.

Expected: Submodule merge commit created, both diverged changes integrated, commit message matches pattern, submodule staged in parent index.

**GREEN — Behavioral Description:**

Implement diverged submodule merge flow. Fetch worktree submodule commits into local object store: `git -C agent-core fetch <project-root>/wt/<slug>/agent-core HEAD` (uses absolute path to worktree submodule directory). Merge fetched commit: `git -C agent-core merge --no-edit <wt-commit>` (no-edit prevents editor prompt). Stage submodule pointer: `git add agent-core`. Create merge commit if staged: `git diff --quiet --cached || git commit -m "🔀 Merge agent-core from <slug>"` (idempotent — no-op if already committed).

Design decisions: D-7 (submodule before parent), D-10 (idempotent commit), NFR-3 (direct git plumbing). Approach: fetch from worktree path not remote (worktree-only commits), hardcoded gitmoji for submodule merges.

## Cycle 3.5: Phase 2 post-verification

**RED — Behavioral Verification:**

Verify merge correctness via ancestry verification. After diverged submodule merge (cycle 3.4), extract both original commit SHAs (worktree pointer and pre-merge local HEAD), assert both are ancestors of final submodule HEAD using `git merge-base --is-ancestor`. Create negative test case with corrupted merge (manually reset submodule to wrong commit before verification), assert post-verification catches error.

Expected: Both original commits pass ancestry check after successful merge. Corrupted merge fails verification with descriptive error.

**GREEN — Behavioral Description:**

Implement post-merge verification for submodule merge correctness. After merge commit (or skip), extract final submodule HEAD: `git -C agent-core rev-parse HEAD`. Verify both original commits are ancestors: `git -C agent-core merge-base --is-ancestor <wt-commit> HEAD` and same for `<local-commit>`. If either check fails, exit 2 with error message listing commits and ancestry failure. This catches merge corruption or logic errors.

Design decisions: D-8 (idempotent — verification enables safe re-run), FR-2 (submodule resolution correctness). Approach: defensive verification, fail-fast on unexpected state.

## Cycle 3.6: Phase 3 parent merge - clean merge

**RED — Behavioral Verification:**

Verify parent merge with no conflicts. Create worktree with non-overlapping changes (new file in worktree, different new file in parent), invoke merge, assert clean merge executes (`git merge --no-commit --no-ff <slug>` succeeds), commit created with default message `🔀 Merge wt/<slug>`. Test custom message via `--message` flag, assert commit message becomes `🔀 <custom-text>`. Verify merge commit is created even if fast-forwardable (--no-ff behavior).

Expected: Merge commit created, message matches pattern, changes from both branches integrated, exit 0.

**GREEN — Behavioral Description:**

Implement Phase 3 parent merge for clean (no-conflict) case. Execute `git merge --no-commit --no-ff <slug>` (no-commit allows custom message, no-ff ensures merge commit). Check merge result: `git diff --name-only --diff-filter=U` returns empty (no conflicts). Construct commit message: default = `🔀 Merge wt/<slug>`, with --message = `🔀 <custom-text>`. Create commit: `git commit -m "<message>"`. Output merge commit SHA to stdout. Proceed to Phase 3 post-merge steps (precommit gate in cycle 3.8).

Design decisions: D-3 (--no-commit --no-ff for custom message + audit trail), NFR-3 (direct git plumbing). Approach: clean merge is fast path, conflict handling in 3.7.

## Cycle 3.7: Phase 3 parent merge - session conflicts

**RED — Behavioral Verification:**

Verify deterministic session file conflict resolution. Create worktree with new task in session.md Pending Tasks, make conflicting edit to same section in parent, invoke merge, assert session.md conflict detected and resolved via conflicts.py logic (new task extracted and appended). Verify learnings.md and jobs.md conflicts also resolved deterministically. Assert agent-core submodule conflict resolved via `--ours` (Phase 2 already merged). Check no unresolved conflicts remain after automatic resolution.

Expected: Session conflicts resolved without manual intervention, new task preserved, agent-core taken from ours, merge proceeds to commit.

**GREEN — Behavioral Description:**

Implement conflict detection and resolution for session context files. After merge command, detect conflicts: `git diff --name-only --diff-filter=U` (U = unmerged). For each conflict file, route to appropriate resolver: agent-core → `git checkout --ours agent-core && git add agent-core` (already merged in Phase 2), session.md → apply `resolve_session_conflict()`, learnings.md → `resolve_learnings_conflict()`, jobs.md → `resolve_jobs_conflict()`. Extract conflict sides via `git show :2:<path>` (ours) and `git show :3:<path>` (theirs), pass to resolver, write result to working tree, stage with `git add <path>`. Check remaining conflicts after resolution — if any remain, proceed to abort flow (cycle 3.10).

Design decisions: D-6 (extract before resolve), NFR-2 (deterministic session resolution). Approach: conflict file routing table, git show for conflict extraction, conflicts.py provides resolution functions.

## Cycle 3.8: Phase 3 post-merge precommit gate

**RED — Behavioral Verification:**

Verify mandatory precommit validation after merge commit. Create worktree merge that produces merge commit passing unit tests but failing precommit check (e.g., line length violation in merged file). Assert merge creates commit successfully, then runs `just precommit`, detects failure, reports to stderr which checks failed, exits 1. Verify merge commit is NOT rolled back (remains in history). Test user fix flow: amend commit, re-run merge (idempotent — already merged, skips to verification).

Expected: Precommit runs after commit, failures reported, exit 1, commit persists (no rollback), re-run succeeds after fix.

**GREEN — Behavioral Description:**

Implement post-merge precommit gate as mandatory correctness check. After merge commit created, run `just precommit` (shell out to just recipe). Capture exit code and output. If exit 0, output merge commit SHA to stdout and exit 0 (success). If non-zero, report failure to stderr: "Precommit checks failed:" followed by just output, exit 1. Do NOT roll back merge commit — user fixes issues and amends commit or re-runs merge (idempotent flow handles already-merged state). This validates take-ours conflict resolution strategy mechanically.

Design decisions: D-4 (precommit as oracle), NFR-4 (mandatory gate), D-8 (idempotent — no rollback, safe to re-run). Approach: precommit is external validation, not merge logic, failure is expected path requiring user intervention.

## Cycle 3.9: Idempotent merge - resume after conflict resolution

**RED — Behavioral Verification:**

Verify merge resumes safely after manual conflict resolution. Create scenario with source code conflict (non-session file), invoke merge, assert automatic resolution fails (both --ours and --theirs fail precommit in cycle 3.12), merge exits 1 with conflict list. User manually resolves conflict and stages file. Re-invoke merge command, assert merge detects staged resolution (no re-merge attempt), creates commit, runs precommit, succeeds. Test all three phases for idempotency: Phase 1 re-checks (pass if clean), Phase 2 re-checks submodule state (skip if already merged), Phase 3 detects in-progress merge and completes.

Expected: First run exits 1 with conflicts. Second run after manual staging succeeds, no duplicate operations, commit created, exit 0.

**GREEN — Behavioral Description:**

Implement idempotent merge state detection across all phases. Phase 1: clean-tree check passes if tree clean (manual staging allowed). Phase 2: submodule resolution checks current state (ancestry checks work on manually merged state). Phase 3: detect merge in progress using `git rev-parse --verify MERGE_HEAD` (exits 0 if merge active) — skip `git merge` command if MERGE_HEAD exists, proceed directly to conflict resolution checks. After conflict resolution (manual or automatic), detect if conflicts remain, commit if resolved. This allows merge to be interrupted at any point and resumed by re-running command.

Design decisions: D-8 (idempotent is architectural requirement), NFR-1 (resume after conflicts). Approach: state detection before each phase, MERGE_HEAD detection for in-progress merge, no assumptions about starting state.

## Cycle 3.10: Merge debris cleanup

**RED — Behavioral Verification:**

Verify cleanup of untracked files materialized during merge. Create merge scenario with source code conflict that cannot be auto-resolved (both --ours and --theirs fail precommit). Invoke merge, assert abort executes (`git merge --abort`), verify merge materialized new untracked files from source branch (check with `git status --porcelain` for `??` entries). Assert cleanup logic identifies and removes these files via `git clean -fd -- <affected-dirs>`. Verify existing untracked files NOT removed (only merge-materialized debris). Re-invoke merge after cleanup, assert clean starting state.

Expected: Aborted merge leaves debris, cleanup removes only merge-materialized files, existing untracked files preserved, retry succeeds.

**GREEN — Behavioral Description:**

Implement merge debris cleanup after abort. Before aborting merge, capture list of untracked files: `git status --porcelain | grep '^??'`. Execute `git merge --abort`. Check for NEW untracked files (present after abort but not before). Identify affected directories from conflict file list. Clean debris: `git clean -fd -- <affected-dirs>` targeting only paths that contained conflicts. Log cleanup actions to stderr for traceability. This prevents "untracked files would be overwritten" errors on merge retry. Only invoke cleanup if merge was aborted due to unresolvable conflicts.

Design decisions: D-8 (idempotent — cleanup enables safe retry). Approach: pre-abort snapshot for diff, targeted clean by affected directories not blanket clean, defensive check to avoid removing user files.

## Cycle 3.11: Take-ours strategy

**RED — Behavioral Verification:**

Create test fixture for source code merge conflict between main and worktree branches. Setup a diverged state where both branches modify same source file at same location. Test that `resolve_source_conflicts()` defaults to `--ours` version for all non-session conflict files.

Expected behavior: Each conflicted source file resolved with `git checkout --ours <file>`, then staged with `git add <file>`. Function returns list of resolved files (exact file paths depend on test fixture — verify list contains all conflicted files excluding session context patterns).

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

**GREEN — Behavioral Description:**

Implement `resolve_source_conflicts()` in `conflicts.py`. Function takes conflict list and exclude patterns, filters to source files only (excluding session context files), then applies take-ours resolution.

Behavior hints:
- Filter conflict list against exclude patterns (deterministic, not fuzzy matching)
- For each source file in filtered list, run subprocess commands: `git checkout --ours <file>` followed by `git add <file>`
- Capture any git command failures and propagate errors
- Return list of successfully resolved files
- Function is deterministic (no agent judgment), relies on mechanical git operations

Implementation approach: subprocess wrappers for git checkout and git add, error handling for missing files or git failures, return resolved paths for caller verification.

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
