# Exploration: Worktree Merge Implementation

## Summary

The worktree merge implementation spans two entry points (`claudeutils _worktree merge` Python CLI and `just wt-merge` recipe) that both abort on source conflicts rather than leaving the merge in progress. The Python code (`src/claudeutils/worktree/merge.py`) has a 4-phase architecture where Phase 3 explicitly calls `git merge --abort` when unresolved conflicts remain after auto-resolving known files. The justfile recipe has similar logic (Phase 3, lines 258-310) that also calls `git merge --abort`. The key insight: both implementations treat "conflicts remaining" as a fatal error requiring abort, rather than leaving the merge in-progress state for the agent to resolve.

## Key Findings

### 1. Python Implementation: Four-Phase Architecture

**File:** `/Users/david/code/claudeutils/src/claudeutils/worktree/merge.py`

**Entry point (line 386-391):** `merge(slug: str)`
```python
def merge(slug: str) -> None:
    """Merge worktree branch: validate, resolve submodule, merge parent."""
    _phase1_validate_clean_trees(slug)
    _phase2_resolve_submodule(slug)
    _phase3_merge_parent(slug)
    _phase4_merge_commit_and_precommit(slug)
```

**Phase 1: Validate Clean Trees (lines 190-214)**
- Checks branch exists (`git rev-parse --verify`)
- Verifies parent repo is clean (exempt: session.md, jobs.md, learnings.md, agent-core)
- Verifies worktree is clean
- **Abort:** Exits with code 2 if branch not found or dirty tree

**Phase 2: Resolve Submodule (lines 217-259)**
- Gets submodule commit pointer from worktree branch: `git ls-tree <slug> -- agent-core`
- Compares to local agent-core HEAD
- **If commits differ:**
  - Checks if worktree commit is ancestor of local (if yes, skip)
  - Fetches worktree submodule commits if needed: `git fetch <worktree-path>/agent-core HEAD`
  - **Calls `_git("-C", "agent-core", "merge", "--no-edit", wt_commit)`**
  - **Abort point:** This merge call raises `CalledProcessError` on conflict (no catch handler) → entire pipeline fails (FR-1 issue)
  - Stages and commits: `git add agent-core` + `git commit`

**Phase 3: Merge Parent (lines 261-300)**
- Initiates merge: `git merge --no-commit --no-ff <slug>` (line 263-268)
- Checks if merge actually happened (MERGE_HEAD exists, line 272-281)
- **If conflicts found:**
  - Gets conflict list: `git diff --name-only --diff-filter=U` (line 283)
  - Auto-resolves known files:
    - `agent-core`: checkout ours, add (line 286-288)
    - `session.md`: calls `_resolve_session_md_conflict()` (line 291)
    - `learnings.md`: calls `_resolve_learnings_md_conflict()` (line 292)
    - `jobs.md`: calls `_resolve_jobs_md_conflict()` (line 293)
  - **Abort on remaining conflicts (lines 295-300):**
    ```python
    if conflicts:
        _git("merge", "--abort")
        _git("clean", "-fd")
        conflict_list = ", ".join(conflicts)
        click.echo(f"Merge aborted: conflicts in {conflict_list}")
        raise SystemExit(1)
    ```
  - This is **FR-2 issue:** Merge is aborted instead of left in-progress

**Phase 4: Commit and Validate (lines 332-384)**
- Checks if merge is in-progress (MERGE_HEAD exists)
- Commits merge with `--allow-empty` flag
- Validates branch is ancestor of HEAD
- Runs `just precommit` validation

### 2. Justfile Recipe: Parallel Structure

**File:** `/Users/david/code/claudeutils/justfile`, lines 199-327

**Entry recipe (line 199): `wt-merge name`**
- Pre-checks: Clean tree and worktree (lines 205-225)

**Phase 2: Submodule Resolution (lines 234-255)**
```bash
wt_commit=$(git ls-tree "$branch" -- agent-core | awk '{print $3}')
local_commit=$(git -C agent-core rev-parse HEAD)
if [ "$wt_commit" != "$local_commit" ]; then
    # ...ancestry checks...
    if ! visible git -C agent-core merge --no-edit "$wt_commit"; then
        echo "${RED}Submodule merge conflict in agent-core${NORMAL}" >&2
        fail "Resolve in agent-core/, commit, then re-run: just wt-merge $slug"
    fi
    visible git add agent-core
    git diff --quiet --cached || visible git commit -m "🔀 Merge agent-core from $slug"
fi
```
- **Abort on submodule conflict:** `fail` exits with error code instead of continuing (line 249)

**Phase 3: Parent Merge (lines 257-311)**
```bash
if ! git merge --no-commit --no-ff "$branch" 2>&1; then
    conflicts=$(git diff --name-only --diff-filter=U)
    # Auto-resolve agent-core, session.md, learnings.md, jobs.md...
    remaining=$(git diff --name-only --diff-filter=U)
    if [ -n "$remaining" ]; then
        echo "${RED}Unresolved conflicts after auto-resolution:${NORMAL}" >&2
        echo "$remaining" >&2
        git merge --abort
        git clean -fd -- agents/ src/ tests/ || true
        fail "Manual conflict resolution required"
    fi
fi
```
- **Abort on remaining conflicts (lines 303-310):** `git merge --abort` destroys merge state

**Phase 4: Commit and Validation (lines 313-327)**
- Commits merge with message
- Runs `just precommit`
- Returns success message

### 3. Cleanup Behavior After Abort

**Python code (merge.py line 296-297):**
```python
_git("merge", "--abort")
_git("clean", "-fd")
```

**Justfile recipe (justfile line 306-308):**
```bash
git merge --abort
git clean -fd -- agents/ src/ tests/ || true
```

**State left behind:**
- `git merge --abort` resets HEAD to pre-merge state, removes MERGE_HEAD
- `git clean -fd` removes untracked files in specified directories (justfile) or repo-wide (Python)
- Working tree is clean but merge is completely destroyed
- **Data loss:** Any staged conflict resolutions are lost, as is the merge context

### 4. Error Handling and Exit Codes

**Python (cli.py line 249-257):**
```python
@worktree.command()
@click.argument("slug")
def merge(slug: str) -> None:
    """Merge worktree branch back to main."""
    try:
        merge_impl(slug)
    except subprocess.CalledProcessError as e:
        click.echo(_format_git_error(e), err=True)
        raise SystemExit(1) from None
```
- Phase 2 submodule merge conflict → `CalledProcessError` → wrapped as `SystemExit(1)`
- Phase 3 remaining conflicts → explicit `SystemExit(1)`
- Phase 1 clean check → `SystemExit(2)` (fatal)
- Exit codes: 0 (success), 1 (merge error), 2 (fatal)

**Justfile:**
```bash
fail "message"  # Exits with code 1
```
- All failures exit with code 1 (same as Python)

### 5. Auto-Resolution Functions

**Session.md conflict (merge.py lines 121-144):**
- Extracts task blocks from both sides using `extract_task_blocks()`
- Merges: keeps ours as base, adds new tasks from theirs
- Falls back to `git checkout --ours` if write fails
- **Handles:** Missing task names that exist only on worktree side

**Learnings.md conflict (merge.py lines 147-171):**
- Line-based deduplication: keeps ours, appends theirs-only lines
- Writes directly to file, no fallback on failure

**Jobs.md conflict (merge.py lines 174-187):**
- Simple: `git checkout --ours` (local plan status is authoritative)

**Agent-core conflict in parent merge (merge.py lines 286-288):**
- Always take ours: `git checkout --ours agent-core`
- Rationale: agent-core was already merged in Phase 2

### 6. Resume/Idempotency Support

**Python Phase 4 (lines 339-346):**
```python
merge_in_progress = (
    subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        capture_output=True,
        check=False,
    ).returncode
    == 0
)
```
- **Handles in-progress merge:** Can resume Phase 4 if MERGE_HEAD exists
- **Does NOT handle:** Resuming Phase 2 (submodule merge) or Phase 3 conflict detection

**Phases 1-3 resumption:**
- Phase 1: Always runs clean checks (non-idempotent, will fail if tree is dirty from Phase 2)
- Phase 2: Always attempts submodule merge, even if already done
  - Safeguard: checks if `wt_commit == local_commit` and returns early
  - If submodule is mid-merge (MERGE_HEAD exists), Phase 2 merge command will fail
- Phase 3: Always attempts parent merge
  - Safeguard: checks if merge failed before MERGE_HEAD was created
  - If parent merge is in-progress (MERGE_HEAD exists), Phase 3 returns early

**Summary:** Phase 4 only has explicit resume logic. Phases 1-3 partially tolerate in-progress state via early returns.

### 7. Justfile Recipe Missing Logic

The justfile recipe at lines 199-327 lacks several safety features that the Python code has:

**Missing in justfile:**
- No attempt to detect/resume submodule mid-merge state
- No attempt to detect/resume parent mid-merge state
- No session.md conflict resolution (just warns to manually resolve)
- No learnings.md merge logic (just warns)
- No jobs.md merge logic (just warns)
- `git clean -fd` scoped to agents/, src/, tests/ (Python does repo-wide)

**Justfile's approach:** Simpler shell script that aborts and reports, expects agent to fix and re-run

### 8. Relationship Between Python Tool and Justfile

Both implement the same 4-phase strategy but with different levels of detail:

| Phase | Python | Justfile |
|-------|--------|----------|
| **Phase 1: Validate** | Full clean check, branch exists | Full clean check, branch exists |
| **Phase 2: Submodule** | Fetch missing commits, merge, stage | Fetch missing commits, merge, stage |
| **Phase 2: Abort on conflict** | Uncaught exception → SystemExit(1) | `fail` → exit 1 |
| **Phase 3: Parent merge** | `--no-commit --no-ff`, auto-resolve 4 files | `--no-commit --no-ff`, auto-resolve agent-core only |
| **Phase 3: Auto-resolution** | session.md (merge tasks), learnings (append), jobs (keep ours) | Warnings only, no automation |
| **Phase 3: Abort on remaining** | `git merge --abort; git clean -fd` | `git merge --abort; git clean -fd` |
| **Phase 4: Commit & precommit** | Commit with `--allow-empty`, run `just precommit` | Commit, run `just precommit` |

**Justfile is entry point for skill:** The worktree skill (SKILL.md Mode C) calls `just wt-merge` not `claudeutils _worktree merge`. The Python tool is more complete but unused in the skill pipeline.

### 9. What Happens on Source Conflicts

**Scenario:** Parent branch has file conflicts (e.g., `src/foo.py` modified on both sides, no auto-resolution rule)

1. **Phase 3 flow:**
   - `git merge --no-commit --no-ff` starts merge, returns non-zero, MERGE_HEAD created
   - Conflict check: `git diff --name-only --diff-filter=U` → `["src/foo.py"]`
   - Auto-resolve known files: none match
   - Remaining conflicts list: `["src/foo.py"]`
   - **Abort triggered:** `git merge --abort; git clean -fd`
   - Exit with code 1

2. **Working tree state after abort:**
   - MERGE_HEAD removed
   - All merge metadata cleaned (MERGE_MSG, MERGE_HEAD, etc.)
   - Untracked files in agents/, src/, tests/ removed (justfile) or repo-wide (Python)
   - Any staged resolutions lost
   - Agent has NO context to resolve conflicts (merge is gone)

3. **What agent sees:**
   - stderr: "Manual conflict resolution required" or "Merge aborted: conflicts in src/foo.py"
   - Exit code 1
   - No merge in progress (MERGE_HEAD gone)
   - Agent **cannot** recover by editing and re-running — merge state is destroyed

### 10. Submodule Merge State Loss

**Scenario:** Submodule (agent-core) merge produces conflicts

**Python Phase 2 (line 250):**
```python
_git("-C", "agent-core", "merge", "--no-edit", wt_commit)
```
- If this fails with conflict (CalledProcessError), Phase 2 raises exception
- **No catch handler** → entire pipeline exits without entering Phase 3/4
- **Result:** Submodule is left in mid-merge state (MERGE_HEAD exists in agent-core)
- **Parent merge never attempted**

**Justfile Phase 2 (line 247):**
```bash
if ! visible git -C agent-core merge --no-edit "$wt_commit"; then
    echo "${RED}Submodule merge conflict in agent-core${NORMAL}" >&2
    fail "Resolve in agent-core/, commit, then re-run: just wt-merge $slug"
fi
```
- If merge fails, `fail` exits immediately
- **Result:** Agent must resolve agent-core conflicts manually, commit, then re-run
- **On re-run:** Phase 2 will succeed (merge already done), Phase 3 starts
- **Behavior is idempotent for submodule but not because Phase 2 catches conflict—because it requires manual resolution first**

### 11. Code Density Issues (Learnings Context)

The merge code has several anti-patterns evident from session learnings:

**Learnings cited:** "When hit file line limits" (working around length constraints)

The merge.py file is 392 lines total. The 4-phase functions span:
- Phase 1: 24 lines
- Phase 2: 42 lines
- Phase 3: 39 lines
- Phase 4: 52 lines
- Plus helpers: ~155 lines (conflict resolution, formatting, session merge logic)

**Density observation:** Phases 2 and 3 could be consolidated. Phase 2 submodule merge is nearly identical to Phase 3 parent merge structurally (both call `git merge --no-edit`, both stage and commit). The difference is in conflict handling (Phase 2 aborts entirely, Phase 3 attempts auto-resolve). This duplication is not yet extractable without refactoring.

## Patterns

### Abort-on-Conflict Anti-Pattern

Both Python and justfile implement the same pattern:
1. Attempt operation
2. Check for conflicts
3. If any remain: abort and exit
4. Leave no trace for agent to resume

This pattern appears in:
- Phase 2: submodule merge abort (Python only)
- Phase 3: parent merge abort (both)

**Why it's a problem:** Agents cannot resolve conflicts in a destroyed merge state. The "resolve conflicts and re-run" instruction in error messages is aspirational—the merge context is gone, so re-running starts from scratch.

### Early-Return Idempotency

Phases 1-3 have early returns to skip already-completed work, but these are scattered and incomplete:

- Phase 1: No early return (always validates)
- Phase 2: Early return if `wt_commit == local_commit` (line 226-227), but no detection of in-progress submodule merge
- Phase 3: Early return if merge succeeds (line 269-270), but no detection of in-progress merge at start
- Phase 4: Explicit MERGE_HEAD check (line 339-346)

**Issue:** If submodule merge is in-progress and Phase 2 re-runs, the merge command will fail with "already in progress" error, not "already done" logic.

### Conflict Context Loss

Current outputs:
- Python: `"Merge aborted: conflicts in {conflict_list}"`
- Justfile: `"Unresolved conflicts after auto-resolution:\n{remaining}"`

Neither provides:
- Scope of conflicts (how many lines changed on each side)
- Branch divergence (how many commits ahead on each side)
- Actionable hint (what to do next)

### Auto-Resolution Scope Mismatch

Python has 3 auto-resolvers (session, learnings, jobs), justfile has none (except agent-core checkout). This creates inconsistency: the skill (uses justfile) behaves differently than direct Python invocation.

## Gaps

### Gap 1: Submodule Conflict Handling

**Issue:** Phase 2 doesn't distinguish "merge failed with conflict" from "merge failed for other reason"

Current code catches nothing—all failures are fatal. Should:
- Detect if MERGE_HEAD exists in agent-core after failed merge
- If yes: continue to Phase 3 with submodule in mid-merge state
- If no: fatal error

**Impact:** FR-1 blocker

### Gap 2: Parent Merge State Preservation

**Issue:** Phase 3 explicitly aborts merge instead of leaving it in-progress

Current behavior destroys merge state and requires agent to manually restart. Should:
- Leave merge in-progress if unresolved conflicts exist
- Report conflicts with context (file list, diff stats, branch divergence)
- Exit with code that signals "conflicts need resolution" (distinct from fatal error)

**Impact:** FR-2 blocker

### Gap 3: Resume Detection at Phase Start

**Issue:** Phases 1-3 don't detect or skip over in-progress merge states

Example: If agent manually resolves a submodule conflict and commits, then re-runs `claudeutils _worktree merge`, Phase 2 will attempt another submodule merge (failing with "already committed"). Phase 1's clean check will also fail (submodule has dangling merge metadata).

**Impact:** FR-5 blocker

### Gap 4: Untracked File Collision Detection

**Issue:** No handling for `git merge` failure due to untracked files that conflict with incoming branch

Git fails before starting merge: "error: The following untracked working tree files would be overwritten by merge"

Current code doesn't catch this, so merge command just fails with no recovery path.

**Impact:** FR-3 blocker

### Gap 5: Conflict Context in Output

**Issue:** Merge failures report only file names, not scope or actionability

Should include: diff stats between ours/theirs, branch commit counts, guidance on resolution.

**Impact:** FR-4 blocker

### Gap 6: Exit Code Semantics

**Issue:** No distinction between "fatal error" (exit 1/2) and "conflicts need resolution" (exit ?)

Current: All failures exit with 1 or 2. Should have a distinct exit code for "unresolved conflicts in merge state" to allow skill to route agent response appropriately.

**Impact:** NFR-1 and C-1 (skill contract) blocker

## Absolute File Paths

- `/Users/david/code/claudeutils/src/claudeutils/worktree/cli.py` — Python CLI entry point
- `/Users/david/code/claudeutils/src/claudeutils/worktree/merge.py` — 4-phase merge implementation
- `/Users/david/code/claudeutils/justfile` — Justfile recipes (lines 199-327)
- `/Users/david/code/claudeutils/plans/worktree-merge-resilience/requirements.md` — FR-1 through FR-5 requirements
