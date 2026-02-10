### Phase 4: Merge Orchestration (3-phase flow)

## Cycle 4.1: Phase 1 pre-checks (clean tree gate)

**RED — Behavioral Verification:**

Verify merge enforcement of clean working tree. Create test scenario with dirty repository state (modified source file `src/claudeutils/__init__.py`), invoke `_worktree merge <slug>`, assert exit code 1 and error message to stderr indicating dirty tree prevents merge. Verify session context files (agents/session.md) do NOT trigger dirty tree rejection (exempt from gate).

Expected: Exit 1, stderr contains "dirty" or "uncommitted changes", merge does NOT proceed.

**GREEN — Behavioral Description:**

Implement `merge` subcommand entry point and Phase 1 pre-check logic. Reuse clean-tree validation logic from clean-tree subcommand (filter session context files, check parent + submodule status). Add branch validation (`git rev-parse --verify <slug>`), worktree directory check (warn if `wt/<slug>/` missing but continue — branch-only merge valid). Exit 1 with descriptive error if dirty tree detected. Return early from merge if pre-checks fail.

Design decisions: D-4 (precommit oracle), NFR-4 (mandatory precommit). Approach: extract shared validation logic into helper function, invoke from both clean-tree subcommand and merge Phase 1.

## Cycle 4.2: Phase 2 submodule resolution - no divergence

**RED — Behavioral Verification:**

Verify merge optimization when submodule pointers match. Create worktree with submodule at same commit as parent (no divergence), invoke merge, assert submodule merge phase skipped (no fetch, no merge commands executed). Trace execution to confirm skip path taken. Verify merge proceeds to Phase 3 (parent merge).

Expected: Merge succeeds, no submodule operations in trace, submodule pointer unchanged after merge.

**GREEN — Behavioral Description:**

Implement Phase 2 submodule resolution with no-divergence optimization. Extract worktree submodule commit pointer using `git ls-tree <slug> -- agent-core` (parse 160000 mode line, extract SHA). Extract local submodule commit using `git -C agent-core rev-parse HEAD`. Compare commits — if equal, skip to Phase 3. Log skip reason to stderr for traceability.

Design decisions: D-7 (submodule before parent), D-8 (idempotent). Approach: early return pattern for optimization, git plumbing for pointer extraction.

## Cycle 4.3: Phase 2 submodule resolution - fast-forward

**RED — Behavioral Verification:**

Verify merge optimization when local submodule includes worktree changes (ancestry check passes). Create worktree, make submodule commits in worktree, merge those commits to parent submodule manually (local ahead of worktree), invoke merge, assert submodule merge skipped via ancestry check. Verify `git merge-base --is-ancestor <wt-commit> <local-commit>` detected inclusion.

Expected: Merge succeeds, ancestry check passes, no fetch or merge executed, submodule pointer unchanged.

**GREEN — Behavioral Description:**

Extend Phase 2 with ancestry check optimization. After extracting both commits, run `git -C agent-core merge-base --is-ancestor <wt-commit> <local-commit>`. If exit 0 (ancestor check passes), local already includes worktree changes — skip merge. Log skip reason with commit SHAs. Handle command failure (commit not found) as divergence indicator — proceed to fetch+merge path.

Design decisions: D-8 (idempotent — safe to re-run). Approach: ancestry check as second optimization gate after equality check.

## Cycle 4.4: Phase 2 submodule resolution - diverged commits

**RED — Behavioral Verification:**

Verify merge with diverged submodule commits. Create worktree, make distinct submodule commit in worktree (file A), make different commit in parent submodule (file B), invoke merge, assert submodule merge executes (fetch from worktree path, merge via `--no-edit`, stage, commit). Verify both files A and B present in final submodule state. Verify merge commit message follows pattern `🔀 Merge agent-core from <slug>`.

Expected: Submodule merge commit created, both diverged changes integrated, commit message matches pattern, submodule staged in parent index.

**GREEN — Behavioral Description:**

Implement diverged submodule merge flow. Fetch worktree submodule commits into local object store: `git -C agent-core fetch <project-root>/wt/<slug>/agent-core HEAD` (uses absolute path to worktree submodule directory). Merge fetched commit: `git -C agent-core merge --no-edit <wt-commit>` (no-edit prevents editor prompt). Stage submodule pointer: `git add agent-core`. Create merge commit if staged: `git diff --quiet --cached || git commit -m "🔀 Merge agent-core from <slug>"` (idempotent — no-op if already committed).

Design decisions: D-7 (submodule before parent), D-10 (idempotent commit), NFR-3 (direct git plumbing). Approach: fetch from worktree path not remote (worktree-only commits), hardcoded gitmoji for submodule merges.

## Cycle 4.5: Phase 2 post-verification

**RED — Behavioral Verification:**

Verify merge correctness via ancestry verification. After diverged submodule merge (cycle 4.4), extract both original commit SHAs (worktree pointer and pre-merge local HEAD), assert both are ancestors of final submodule HEAD using `git merge-base --is-ancestor`. Create negative test case with corrupted merge (manually reset submodule to wrong commit before verification), assert post-verification catches error.

Expected: Both original commits pass ancestry check after successful merge. Corrupted merge fails verification with descriptive error.

**GREEN — Behavioral Description:**

Implement post-merge verification for submodule merge correctness. After merge commit (or skip), extract final submodule HEAD: `git -C agent-core rev-parse HEAD`. Verify both original commits are ancestors: `git -C agent-core merge-base --is-ancestor <wt-commit> HEAD` and same for `<local-commit>`. If either check fails, exit 2 with error message listing commits and ancestry failure. This catches merge corruption or logic errors.

Design decisions: D-8 (idempotent — verification enables safe re-run), FR-2 (submodule resolution correctness). Approach: defensive verification, fail-fast on unexpected state.

## Cycle 4.6: Phase 3 parent merge - clean merge

**RED — Behavioral Verification:**

Verify parent merge with no conflicts. Create worktree with non-overlapping changes (new file in worktree, different new file in parent), invoke merge, assert clean merge executes (`git merge --no-commit --no-ff <slug>` succeeds), commit created with default message `🔀 Merge wt/<slug>`. Test custom message via `--message` flag, assert commit message becomes `🔀 <custom-text>`. Verify merge commit is created even if fast-forwardable (--no-ff behavior).

Expected: Merge commit created, message matches pattern, changes from both branches integrated, exit 0.

**GREEN — Behavioral Description:**

Implement Phase 3 parent merge for clean (no-conflict) case. Execute `git merge --no-commit --no-ff <slug>` (no-commit allows custom message, no-ff ensures merge commit). Check merge result: `git diff --name-only --diff-filter=U` returns empty (no conflicts). Construct commit message: default = `🔀 Merge wt/<slug>`, with --message = `🔀 <custom-text>`. Create commit: `git commit -m "<message>"`. Output merge commit SHA to stdout. Proceed to Phase 3 post-merge steps (precommit gate in cycle 4.8).

Design decisions: D-3 (--no-commit --no-ff for custom message + audit trail), NFR-3 (direct git plumbing). Approach: clean merge is fast path, conflict handling in 4.7.

## Cycle 4.7: Phase 3 parent merge - session conflicts

**RED — Behavioral Verification:**

Verify deterministic session file conflict resolution. Create worktree with new task in session.md Pending Tasks, make conflicting edit to same section in parent, invoke merge, assert session.md conflict detected and resolved via conflicts.py logic (new task extracted and appended). Verify learnings.md and jobs.md conflicts also resolved deterministically. Assert agent-core submodule conflict resolved via `--ours` (Phase 2 already merged). Check no unresolved conflicts remain after automatic resolution.

Expected: Session conflicts resolved without manual intervention, new task preserved, agent-core taken from ours, merge proceeds to commit.

**GREEN — Behavioral Description:**

Implement conflict detection and resolution for session context files. After merge command, detect conflicts: `git diff --name-only --diff-filter=U` (U = unmerged). For each conflict file, route to appropriate resolver: agent-core → `git checkout --ours agent-core && git add agent-core` (already merged in Phase 2), session.md → apply `resolve_session_conflict()`, learnings.md → `resolve_learnings_conflict()`, jobs.md → `resolve_jobs_conflict()`. Extract conflict sides via `git show :2:<path>` (ours) and `git show :3:<path>` (theirs), pass to resolver, write result to working tree, stage with `git add <path>`. Check remaining conflicts after resolution — if any remain, proceed to abort flow (cycle 4.10).

Design decisions: D-6 (extract before resolve), NFR-2 (deterministic session resolution). Approach: conflict file routing table, git show for conflict extraction, conflicts.py provides resolution functions.

## Cycle 4.8: Phase 3 post-merge precommit gate

**RED — Behavioral Verification:**

Verify mandatory precommit validation after merge commit. Create worktree merge that produces merge commit passing unit tests but failing precommit check (e.g., line length violation in merged file). Assert merge creates commit successfully, then runs `just precommit`, detects failure, reports to stderr which checks failed, exits 1. Verify merge commit is NOT rolled back (remains in history). Test user fix flow: amend commit, re-run merge (idempotent — already merged, skips to verification).

Expected: Precommit runs after commit, failures reported, exit 1, commit persists (no rollback), re-run succeeds after fix.

**GREEN — Behavioral Description:**

Implement post-merge precommit gate as mandatory correctness check. After merge commit created, run `just precommit` (shell out to just recipe). Capture exit code and output. If exit 0, output merge commit SHA to stdout and exit 0 (success). If non-zero, report failure to stderr: "Precommit checks failed:" followed by just output, exit 1. Do NOT roll back merge commit — user fixes issues and amends commit or re-runs merge (idempotent flow handles already-merged state). This validates take-ours conflict resolution strategy mechanically.

Design decisions: D-4 (precommit as oracle), NFR-4 (mandatory gate), D-8 (idempotent — no rollback, safe to re-run). Approach: precommit is external validation, not merge logic, failure is expected path requiring user intervention.

## Cycle 4.9: Idempotent merge - resume after conflict resolution

**RED — Behavioral Verification:**

Verify merge resumes safely after manual conflict resolution. Create scenario with source code conflict (non-session file), invoke merge, assert automatic resolution fails (both --ours and --theirs fail precommit in cycle 5.3), merge exits 1 with conflict list. User manually resolves conflict and stages file. Re-invoke merge command, assert merge detects staged resolution (no re-merge attempt), creates commit, runs precommit, succeeds. Test all three phases for idempotency: Phase 1 re-checks (pass if clean), Phase 2 re-checks submodule state (skip if already merged), Phase 3 detects in-progress merge and completes.

Expected: First run exits 1 with conflicts. Second run after manual staging succeeds, no duplicate operations, commit created, exit 0.

**GREEN — Behavioral Description:**

Implement idempotent merge state detection across all phases. Phase 1: clean-tree check passes if tree clean (manual staging allowed). Phase 2: submodule resolution checks current state (ancestry checks work on manually merged state). Phase 3: detect merge in progress using `git rev-parse --verify MERGE_HEAD` (exits 0 if merge active) — skip `git merge` command if MERGE_HEAD exists, proceed directly to conflict resolution checks. After conflict resolution (manual or automatic), detect if conflicts remain, commit if resolved. This allows merge to be interrupted at any point and resumed by re-running command.

Design decisions: D-8 (idempotent is architectural requirement), NFR-1 (resume after conflicts). Approach: state detection before each phase, MERGE_HEAD detection for in-progress merge, no assumptions about starting state.

## Cycle 4.10: Merge debris cleanup

**RED — Behavioral Verification:**

Verify cleanup of untracked files materialized during merge. Create merge scenario with source code conflict that cannot be auto-resolved (both --ours and --theirs fail precommit). Invoke merge, assert abort executes (`git merge --abort`), verify merge materialized new untracked files from source branch (check with `git status --porcelain` for `??` entries). Assert cleanup logic identifies and removes these files via `git clean -fd -- <affected-dirs>`. Verify existing untracked files NOT removed (only merge-materialized debris). Re-invoke merge after cleanup, assert clean starting state.

Expected: Aborted merge leaves debris, cleanup removes only merge-materialized files, existing untracked files preserved, retry succeeds.

**GREEN — Behavioral Description:**

Implement merge debris cleanup after abort. Before aborting merge, capture list of untracked files: `git status --porcelain | grep '^??'`. Execute `git merge --abort`. Check for NEW untracked files (present after abort but not before). Identify affected directories from conflict file list. Clean debris: `git clean -fd -- <affected-dirs>` targeting only paths that contained conflicts. Log cleanup actions to stderr for traceability. This prevents "untracked files would be overwritten" errors on merge retry. Only invoke cleanup if merge was aborted due to unresolvable conflicts.

Design decisions: D-8 (idempotent — cleanup enables safe retry). Approach: pre-abort snapshot for diff, targeted clean by affected directories not blanket clean, defensive check to avoid removing user files.
