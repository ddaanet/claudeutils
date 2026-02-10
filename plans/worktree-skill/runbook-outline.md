# Worktree Skill — TDD Runbook Outline

## Requirements Mapping

| Requirement | Phase | Cycles | Notes |
|-------------|-------|--------|-------|
| FR-1: CLI subcommand with 6 subcommands | 0-2 | 0.2, 1.1, 1.6, 2.1, 2.6 | All subcommands (group, ls, add-commit, new, rm) |
| FR-2: Submodule merge resolution | 4 | 4.1-4.5 | Ancestry check, fetch, merge, verify |
| FR-3: Session conflict resolution | 3 | 3.1-3.2 | Extract tasks before merge |
| FR-4: Source conflict resolution | 5 | 5.1-5.3 | Take-ours + precommit gate |
| FR-5: SKILL.md orchestration | 6 | 6.1-6.4 | Three modes + error communication |
| FR-6: execute-rule.md Mode 5 update | 7 | 7.2 | Reference skill |
| FR-7: Delete justfile recipes | 7 | 7.4 | Remove wt-* recipes |
| FR-8: Integration tests with real repos | All | Throughout | E2E test strategy |
| NFR-1: Idempotent merge | 4 | 4.9 | Resume after conflicts |
| NFR-2: Deterministic session resolution | 3 | 3.1-3.4 | No agent judgment |
| NFR-3: Direct git plumbing | 2, 4 | 2.5, 4.1-4.5 | No /commit skill |
| NFR-4: Mandatory precommit gate | 4, 5 | 4.8, 5.2 | Correctness oracle |
| NFR-5: CLI follows claudeutils patterns | 0 | 0.1-0.3 | Click, stderr, exit codes |

## Phase Structure

### Phase 0: CLI Foundation and Simple Subcommands
- **Complexity:** Low-Medium
- **Cycles:** ~9
- **Model:** sonnet (implementation)
- **Checkpoint:** light
- **Files:** `src/claudeutils/worktree/__init__.py`, `src/claudeutils/worktree/cli.py`, `tests/test_worktree_cli.py`

This phase establishes the package structure, Click command group, slug derivation utility, and three simple subcommands (ls, clean-tree, add-commit). These form the foundation for more complex operations.

#### Cycle 0.1: Package initialization
RED: Test import `from claudeutils.worktree.cli import worktree` raises ImportError (package doesn't exist). GREEN: Create `__init__.py` (empty per minimal convention) and empty `cli.py`.

#### Cycle 0.2: Click group structure
RED: Test `_worktree --help` displays command group. GREEN: Create Click group decorator and stub command in `cli.py`.

#### Cycle 0.3: Slug derivation utility
RED: Test `derive_slug("Implement ambient awareness")` returns `"implement-ambient-awareness"` (lowercase, hyphens, truncate 30 chars). GREEN: Implement pure function with regex substitution.

#### Cycle 0.4: ls subcommand structure
RED: Test `_worktree ls` with no worktrees exits 0 with empty output. GREEN: Parse `git worktree list --porcelain`, emit tab-delimited lines.

#### Cycle 0.5: ls with multiple worktrees
RED: Test with 2 worktrees outputs correct `<slug>\t<branch>\t<path>` per line. GREEN: Parse worktree, branch, path from porcelain format.

#### Cycle 0.6: clean-tree with clean repo
RED: Test clean repo + submodule exits 0 silently. GREEN: Run `git status --porcelain` for parent and submodule, exit 0 if empty.

#### Cycle 0.7: clean-tree with session files
RED: Test dirty `agents/session.md` exits 0 (exempt). GREEN: Filter out `agents/session.md`, `agents/jobs.md`, `agents/learnings.md` from status output.

#### Cycle 0.8: clean-tree with non-session dirt
RED: Test dirty source file exits 1 with file list to stdout. GREEN: Print remaining files after filtering, exit 1.

#### Cycle 0.9: add-commit idempotent behavior
RED: Test add-commit with no staged changes exits 0 with empty output. GREEN: `git diff --quiet --cached && exit 0` before commit. Read message from stdin, output commit hash.

### Phase 1: Worktree Lifecycle (new, rm)
- **Complexity:** Medium
- **Cycles:** ~7
- **Model:** sonnet (implementation)
- **Checkpoint:** light
- **Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_cli.py`

#### Cycle 1.1: new subcommand basic flow
RED: Test `_worktree new <slug>` creates `wt/<slug>/` and branch. GREEN: Run `git worktree add wt/<slug> -b <slug> HEAD`.

#### Cycle 1.2: new with collision detection
RED: Test existing branch or directory exits 1 with error message. GREEN: Validate no `wt/<slug>/` directory, no `<slug>` branch before creating.

#### Cycle 1.3: new with submodule initialization
RED: Test new worktree has submodule initialized at correct commit. GREEN: `git -C wt/<slug> submodule update --init --reference <project-root>/agent-core`.

#### Cycle 1.4: new with submodule branching
RED: Test submodule in new worktree is on `<slug>` branch. GREEN: `git -C wt/<slug>/agent-core checkout -b <slug>`.

#### Cycle 1.5: new with --session pre-commit
RED: Test `--session <path>` creates worktree with focused session.md at HEAD, main index unmodified. GREEN: Git plumbing sequence: hash-object, read-tree with temp index, update-index, write-tree, commit-tree, branch, worktree add.

#### Cycle 1.6: rm subcommand with worktree removal
RED: Test `_worktree rm <slug>` removes worktree and branch. GREEN: `git worktree remove --force wt/<slug>` then `git branch -d <slug>`.

#### Cycle 1.7: rm with branch-only cleanup
RED: Test rm when worktree already removed still deletes branch. GREEN: Check if `wt/<slug>/` exists before worktree remove, always attempt branch delete.

### Phase 2: Conflict Resolution Utilities (session, learnings, jobs)
- **Complexity:** Medium
- **Cycles:** ~4
- **Model:** sonnet (implementation)
- **Checkpoint:** light
- **Files:** `src/claudeutils/worktree/conflicts.py`, `tests/test_worktree_conflicts.py`
- **Parallel:** Can run parallel to Phases 0-2 (no dependencies on CLI implementation)

#### Cycle 3.1: Session conflict resolution with task extraction
RED: Test `resolve_session_conflict(ours, theirs)` preserves ours base, appends new tasks from theirs. GREEN: Parse tasks via regex `^- \[ \] \*\*(.+?)\*\*`, compute set difference, append new task blocks to Pending Tasks section.

#### Cycle 3.2: Session conflict removes merged worktree entry
RED: Test resolution removes worktree entry from Worktree Tasks section. GREEN: Match `→ wt/<slug>` line, remove from Worktree Tasks section.

#### Cycle 3.3: Learnings conflict keep-both
RED: Test `resolve_learnings_conflict(ours, theirs)` preserves all entries from both sides. GREEN: Parse on `## ` headings, identify new theirs entries, append to ours.

#### Cycle 3.4: Jobs conflict status advancement
RED: Test `resolve_jobs_conflict(ours, theirs)` advances status when theirs > ours per ordering. GREEN: Parse table rows into plan→status maps, compare via ordering (`requirements < designed < outlined < planned < complete`), update ours.

### Phase 3: Merge Orchestration and Source Conflicts
- **Complexity:** High
- **Cycles:** ~13
- **Model:** sonnet (implementation)
- **Checkpoint:** full
- **Files:** `src/claudeutils/worktree/merge.py`, `src/claudeutils/worktree/conflicts.py`, `tests/test_worktree_merge.py`
- **Depends on:** Phase 2 (conflicts.py)

#### Cycle 3.1: Phase 1 pre-checks (clean tree gate)
RED: Test merge with dirty tree exits 1. GREEN: Run clean-tree logic, validate branch exists, check worktree directory.

#### Cycle 3.2: Phase 2 submodule resolution - no divergence
RED: Test merge when worktree submodule commit equals local exits early (no merge needed). GREEN: Extract both commits via `git ls-tree` and `git -C agent-core rev-parse HEAD`, compare, skip if equal.

#### Cycle 3.3: Phase 2 submodule resolution - fast-forward
RED: Test merge when local already includes worktree commit (ancestry check passes) skips merge. GREEN: `git -C agent-core merge-base --is-ancestor <wt-commit> <local-commit>`, skip if true.

#### Cycle 3.4: Phase 2 submodule resolution - diverged commits
RED: Test merge with diverged submodule commits merges both sides. GREEN: Fetch from worktree path, merge with `--no-edit`, stage submodule, commit.

#### Cycle 3.5: Phase 2 post-verification
RED: Test after submodule merge both original commits are ancestors of new HEAD. GREEN: `git -C agent-core merge-base --is-ancestor` for both original pointers.

#### Cycle 3.6: Phase 3 parent merge - clean merge
RED: Test merge with no conflicts commits with custom message. GREEN: `git merge --no-commit --no-ff <slug>`, detect clean merge, commit with `🔀 Merge wt/<slug>` or `--message` value.

#### Cycle 3.7: Phase 3 parent merge - session conflicts
RED: Test merge with session.md conflict resolves deterministically. GREEN: Detect conflicts via `git diff --name-only --diff-filter=U`, apply conflicts.py resolution functions, stage, commit.

#### Cycle 3.8: Phase 3 post-merge precommit gate
RED: Test merge runs `just precommit` after commit and exits 1 on precommit failure without rolling back merge. GREEN: Run precommit, report failures to stderr, exit 1 if fails (no rollback).

#### Cycle 3.9: Idempotent merge - resume after conflict resolution
RED: Test re-running merge after manual conflict fix succeeds. GREEN: Detect merge in progress, skip completed phases, resume from current state.

#### Cycle 3.10: Merge debris cleanup
RED: Test aborted merge leaves untracked files, cleanup removes them. GREEN: After `git merge --abort`, run `git clean -fd -- <affected-dirs>` for materialized files.

#### Cycle 3.11: Take-ours strategy
RED: Test source conflicts default to `--ours` version. GREEN: For each non-session conflict file, `git checkout --ours <file> && git add <file>`.

#### Cycle 3.12: Precommit gate validates ours
RED: Test take-ours + passing precommit completes merge. GREEN: Run `just precommit` after ours resolution, output merge commit hash on success.

#### Cycle 3.13: Precommit gate fallback to theirs
RED: Test precommit failure on ours triggers retry with theirs. GREEN: On precommit failure, try `--theirs` for failed files, re-run precommit, exit with conflict list if neither passes.

### Phase 4: SKILL.md (orchestration)
- **Complexity:** Medium-High
- **Cycles:** ~5
- **Model:** opus (workflow artifact)
- **Checkpoint:** full (design-vet-agent)
- **Files:** `agent-core/skills/worktree/SKILL.md`
- **Depends on:** Phases 0-3 (all CLI implementation)

#### Cycle 4.1: Frontmatter and file structure
RED: Skill frontmatter validates (YAML parser). GREEN: Frontmatter with description, allowed-tools, continuation config. Add H2 section headers for three modes.

#### Cycle 4.2: Mode A implementation (single-task worktree)
RED: Skill contains Mode A prose for single-task worktree creation. GREEN: Imperative prose with tool anchors, focused session.md template, launch command output.

#### Cycle 4.3: Mode B implementation (parallel group detection)
RED: Skill contains Mode B prose for parallel group creation. GREEN: Parallel detection criteria as prose analysis, execute Mode A per task, consolidated launch commands.

#### Cycle 4.4: Mode C implementation (merge ceremony)
RED: Skill contains Mode C prose for merge ceremony orchestration. GREEN: Handoff → commit → merge → cleanup flow with error handling for three exit codes.

#### Cycle 4.5: D+B hybrid tool anchors and error communication polish
RED: Every major step opens with tool call, error messages include resolution guidance. GREEN: Add tool anchors, polish error messages with numbered steps, add Usage Notes section.

### Phase 5: Integration and Documentation
- **Complexity:** Low
- **Cycles:** ~4
- **Model:** haiku (mechanical)
- **Checkpoint:** light
- **Files:** `src/claudeutils/cli.py`, `.gitignore`, `agent-core/fragments/execute-rule.md`, `agent-core/fragments/sandbox-exemptions.md`, `justfile`, `.cache/just-help.txt`

#### Cycle 5.1: CLI registration and .gitignore
RED: Test `claudeutils _worktree --help` works from main CLI. GREEN: Add import and `cli.add_command(worktree, "_worktree")` to main `cli.py`. Add `wt/` to `.gitignore`.

#### Cycle 5.2: execute-rule.md Mode 5 update
RED: Mode 5 references `/worktree` skill. GREEN: Replace inline prose with "Invoke `/worktree` skill" and link to `agent-core/skills/worktree/SKILL.md`.

#### Cycle 5.3: sandbox-exemptions.md worktree patterns
RED: Document includes worktree sandbox bypass patterns. GREEN: Add section for `uv sync` and `direnv allow` in new worktrees (network/filesystem access).

#### Cycle 5.4: Justfile recipe deletion
RED: Recipes `wt-new`, `wt-task`, `wt-ls`, `wt-rm`, `wt-merge` do not exist. GREEN: Delete recipe definitions, regenerate `.cache/just-help.txt` via `just cache`.

## Expansion Guidance

### Conventions

**Test fixture patterns:**
- Use `tmp_path` to create real git repos + submodules (not mocks)
- Shared fixtures: `base_repo`, `base_submodule`, `repo_with_submodule` in `conftest.py`
- Each test gets fresh `git clone` of fixtures for isolation
- Mock only for error injection (lock files, permission errors, disk full)

**CLI patterns (from agents/decisions/cli.md):**
- Click framework with command groups
- Errors to stderr before exit 1
- Success output to stdout (machine-readable)
- Progress/status to stderr
- Entry points in `pyproject.toml` `[project.scripts]` section

**TDD patterns (from agents/decisions/testing.md):**
- RED phase: behavioral verification, not just structure
- GREEN phase: behavior hints (approach), not prescriptive code
- Test behavior, defer presentation to vet checkpoints
- Integration test gap: assert outcomes at phase boundaries

**Git plumbing patterns:**
- Temp index file pattern: `GIT_INDEX_FILE=<tmpfile>` for isolated operations
- Ancestry checks: `git merge-base --is-ancestor` before merge attempts
- Porcelain parsing: `git worktree list --porcelain`, `git status --porcelain`
- Submodule fetch: use worktree path `wt/<slug>/agent-core` as fetch source

### Gotchas

**Submodule merge complexity:**
- Worktree-only commits not reachable via remote fetch
- Must fetch from worktree's local submodule path before merge
- Verify ancestry after merge (both original commits reachable from new HEAD)

**Session conflict extraction:**
- Must parse worktree-side tasks BEFORE resolving conflict
- Blind `--ours` loses worktree-created tasks (critical fix for FR-3)
- Task block extraction includes continuation lines (indented metadata)

**Git plumbing temp index:**
- `GIT_INDEX_FILE` must be absolute path or relative to project root
- Clean up temp index file after commit-tree sequence
- Verify main index unmodified after --session pre-commit operation

**Precommit as oracle:**
- Precommit failure does NOT roll back merge commit
- User fixes and amends (idempotent merge allows re-run)
- Precommit validates take-ours strategy mechanically (not agent judgment)

**Merge debris:**
- Aborted merge may materialize untracked files from source branch
- Must clean with `git clean -fd -- <dirs>` before retry
- Check file count and timestamps to identify debris vs. existing files

**Idempotent merge phases:**
- Each phase checks current state before acting
- Safe to re-run after manual conflict resolution
- Detect merge in progress via `git rev-parse --verify MERGE_HEAD`

### Phase-Specific Notes

**Phase 0-2 (CLI foundation + lifecycle):**
- Start with simplest non-degenerate cases (happy path)
- Pattern repetition: 6 subcommands follow same Click decorator pattern
- Can consolidate trivial validation cycles if patterns emerge early

**Phase 3 (conflicts.py):**
- Pure functions, no git operations (easy to test)
- Session conflict resolution is most complex (task extraction + removal)
- Jobs.md includes `outlined` status (not in canonical jobs.md progression)

**Phase 4 (merge.py):**
- Highest complexity phase — requires full checkpoint with vet review
- 3-phase flow (pre-checks, submodule, parent) must stay distinct
- Idempotency is architectural requirement (detect state, resume safely)
- Integration tests critical: diverged commits, fast-forward, conflicts, resume

**Phase 5 (source conflicts):**
- Heuristic with precommit as oracle (not deterministic like session files)
- Take-ours is CLI-level strategy, not agent judgment
- Fallback to theirs only if ours fails precommit

**Phase 6 (SKILL.md):**
- Load `plugin-dev:skill-development` before starting
- Opus model for workflow artifact authoring
- Three modes must be distinct (single-task, parallel, merge)
- D+B hybrid: anchor every step with tool call (Read, Bash, Edit)
- Error messages must include resolution guidance ("what to do next")

**Phase 7 (integration):**
- Mechanical wiring, suitable for haiku execution
- Verify CLI registration with `claudeutils _worktree --help`
- Justfile recipe deletion updates cached help text automatically

### File Size Awareness

**Expected large files:**
- `cli.py`: 6 subcommands + utilities (~300-400 lines) — within limits
- `merge.py`: 3 phases + idempotency (~250-350 lines) — within limits
- `conflicts.py`: 4 resolution functions (~150-200 lines) — no split needed
- `test_worktree_merge.py`: 12+ tests (~300-400 lines) — monitor for split

**Split triggers:**
- Any test file exceeding 400 lines: split by subcommand or phase
- CLI file exceeding 400 lines: extract utilities to separate module

### Consolidation Opportunities

**Pattern cycles (same structure, different inputs):**
- Phase 1: clean-tree filtering (1.3-1.5) — 3 cycles for filter behavior (slight repetition, but tests distinct cases)
- Phase 2: new subcommand flow (2.1-2.4) — 4 cycles building up complexity (not repetitive — sequential build-up)
- Phase 3: conflict resolution (3.1-3.4) — 4 cycles, similar parse-diff-merge pattern (independent functions, not consolidation candidates)

**Potential consolidation gates:**
- Phase 1.3-1.5 could merge if filter logic is simple (single regex)
- Phase 2.1-2.4 are sequential build-up, not repetitive — keep distinct
- Phase 3 functions are independent (parallel), not consolidation candidates

**Trivial cycles:**
- Cycle 0.1 (empty `__init__.py`) — single line, but necessary TDD step
- Cycle 7.1 (`.gitignore` entry) — single line, but validates integration

**Recommendation:** No consolidation needed. Cycles are appropriately scoped for complexity and behavioral verification.

## Key Decisions Reference

**D-1: Directory inside project root** — `wt/<slug>/` not `../<repo>-<slug>/` (sandbox-compatible)
**D-2: No branch prefix** — branches = `<slug>`, not `wt/<slug>` (user requirement)
**D-3: Merge uses --no-commit --no-ff** — custom message + audit trail
**D-4: Precommit as correctness oracle** — validates take-ours conflict resolution
**D-5: CLI does git plumbing, skill does ceremony** — clean boundary for testing
**D-6: Session conflict resolution extracts before resolving** — critical fix for FR-3
**D-7: Submodule merge before parent merge** — phase ordering requirement
**D-8: Idempotent merge** — detect state, resume after manual fixes
**D-9: No plan-specific agent needed** — skill + CLI only
**D-10: add-commit is idempotent** — exits cleanly if nothing staged

## Parallel Execution Notes

**Phase 3 can run parallel to Phases 0-2:**
- Phases 0-2: CLI implementation (sequential within group — foundation → subcommands → lifecycle)
- Phase 3: Conflict resolution utilities (independent — no CLI dependencies, pure functions)
- Phase 4+ (merge.py) depends on Phase 3 (conflicts.py) completing — sequential after parallel work

**Test file parallelization:**
- `test_worktree_cli.py` (Phases 0-2) and `test_worktree_conflicts.py` (Phase 3) fully independent
- `test_worktree_merge.py` (Phases 4-5) depends on conflicts.py existing

**Not recommended for this feature:** Intake assessment notes tight integration requirements and sequential validation needs outweigh parallelization benefits. However, if user wants parallel execution, Groups A and B provide the structure.

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Consolidation candidates:**
- No phases qualify for consolidation — all have appropriate scope
- Phase 1 cycles 1.3-1.5 (clean-tree filtering) have slight pattern repetition but test distinct behavioral cases — keep separate for clarity

**Cycle expansion:**
- **Phase 0**: Cycle 0.1 should verify both ImportError before package exists AND successful import after creation — establishes RED→GREEN transition clearly
- **Phase 2**: Cycle 2.5 (--session pre-commit) is most complex single cycle — ensure RED phase specifies verifying main index unmodified (critical assertion)
- **Phase 4**: Cycle 4.4 (diverged submodule merge) — RED phase must verify both original commits become ancestors after merge (post-verification)
- **Phase 4**: Cycle 4.9 (idempotent merge) — test must simulate interruption (manual conflict resolution) then resume flow

**Checkpoint guidance:**
- **Phase 4 checkpoint (full)**: Verify merge idempotency explicitly — run same merge twice, assert same result
- **Phase 6 checkpoint (full, design-vet-agent)**: SKILL.md requires opus review for workflow artifact quality
- **Light checkpoints**: Phases 0-3, 5, 7 use vet-fix-agent (not design-vet-agent)

**Test fixture strategy:**
- Create shared fixtures in `conftest.py`: `base_repo`, `base_submodule`, `repo_with_submodule`
- Each test clones fixtures fresh (isolation) — don't recreate repos per test
- Mock ONLY for error injection (lock files, permission errors, disk full) — never for behavior validation

**Git plumbing references:**
- Phase 2 cycle 2.5: Temp index pattern requires `GIT_INDEX_FILE=<tmpfile>` prefix for all index operations
- Phase 4 cycles 4.2-4.5: Ancestry checks use `git merge-base --is-ancestor` before merge attempts
- Phase 4 cycle 4.10: Debris cleanup after abort requires `git clean -fd -- <affected-dirs>` not blanket clean

**Integration wiring:**
- Phase 7 cycle 7.1: Verify CLI registration with `claudeutils _worktree --help` after adding to main cli.py
- Phase 7 cycle 7.4: Justfile recipe deletion triggers automatic `.cache/just-help.txt` regeneration via `just cache`

**Critical behavioral assertions:**
- **FR-3 (session conflict resolution)**: Must extract NEW tasks from worktree side BEFORE applying --ours resolution (parse both, diff, append)
- **NFR-1 (idempotency)**: Each merge phase checks state before acting — safe to re-run after manual fixes
- **NFR-4 (precommit gate)**: Precommit failure exits 1 WITHOUT rolling back merge commit — user fixes and amends
