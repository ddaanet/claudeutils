# Worktree Update TDD Runbook: Outline

**Design:** `plans/worktree-update/design.md`
**Type:** TDD
**Model:** haiku (execution), sonnet (checkpoints)

---

## Requirements Mapping

| Requirement | Implementation Phase | Notes |
|-------------|---------------------|-------|
| FR-1: Sibling directory paths (`<repo>-wt/<slug>`) | Phase 1: `wt_path()` | Container detection, path construction |
| FR-2: Worktree-based submodule (shared object store) | Phase 5: `new` command | Replace `--reference` with worktree add |
| FR-3: Sandbox permission registration | Phase 2: `add_sandbox_dir()` + Phase 5 | JSON manipulation, both settings files |
| FR-4: Existing branch reuse | Phase 5: `new` command | Branch detection before creation |
| FR-5: Submodule removal ordering | Phase 6: `rm` command | Submodule first, then parent |
| FR-6: Graceful branch deletion (`-d` with fallback) | Phase 6: `rm` command | Safe delete, warn on unmerged |
| FR-7: 4-phase merge ceremony | Phase 7: `merge` command | Clean tree, submodule, parent, precommit |
| FR-8: Focused session generation | Phase 4: `focus_session()` + Phase 5 | Task extraction, context filtering |
| FR-9: Task-based mode (`--task`) | Phase 5: `new` command | Combines slug + session + creation |
| FR-10: Justfile independence | Phase 8 (non-TDD) | Native bash for wt-ls, both-sides clean for wt-merge |

---

## Phase Structure

### Phase 0: Setup and Registration

**Complexity:** Low (2 cycles)
**Files:** `src/claudeutils/cli.py`
**Description:** Register `_worktree` CLI group in main CLI

**Cycles:**
- 0.1: Import and register worktree CLI group
- 0.2: Verify hidden from help output

---

### Phase 1: Path Computation (`wt_path()`)

**Complexity:** Medium (5 cycles)
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_path.py`
**Description:** Extract path computation logic into testable function

**Cycles:**
- 1.1: `wt_path()` basic path construction
- 1.2: Container detection (`-wt` parent)
- 1.3: Sibling path when in container
- 1.4: Container creation when not in container
- 1.5: Edge cases (root directory, deep nesting)

**Depends on:** Phase 0 (CLI registration exists)

---

### Phase 2: Sandbox Registration (`add_sandbox_dir()`)

**Complexity:** Medium (4 cycles)
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_sandbox_registration.py`
**Description:** JSON manipulation for sandbox permissions

**Cycles:**
- 2.1: Create `add_sandbox_dir()` function — basic JSON read/write
- 2.2: Deduplication logic (avoid adding existing paths)
- 2.3: Missing file handling (create with `{}`)
- 2.4: Nested key creation (`permissions.additionalDirectories`)

**Depends on:** Phase 1 (needs `wt_path()` for container determination)

---

### Phase 3: Slug Derivation (`derive_slug()`)

**Complexity:** Low (3 cycles)
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_cli.py`
**Description:** Fix edge cases in existing `derive_slug()` function

**Cycles:**
- 3.1: Special character handling (non-alphanumeric to hyphen)
- 3.2: Truncation edge cases (exactly 30, trailing hyphen removal)
- 3.3: Empty/whitespace input handling

**Depends on:** Phase 0 (function already exists, verifying behavior)

---

### Phase 4: Focused Session Generation (`focus_session()`)

**Complexity:** Medium (5 cycles)
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_focus_session.py`
**Description:** Parse session.md and generate focused content

**Cycles:**
- 4.1: Task extraction by name (with metadata continuation lines)
- 4.2: Blockers filtering (relevant entries only)
- 4.3: Reference files filtering (relevant entries only)
- 4.4: Missing task error handling
- 4.5: Output formatting (H1, status, sections)

**Depends on:** Phase 3 (slug derivation used internally)

---

### Phase 5: Update `new` Command + Task Mode

**Complexity:** High (10 cycles)
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_new.py`
**Description:** Refactor `new` command using extracted functions, add `--task` mode

**Cycles:**
- 5.1: Use `wt_path()` for sibling directory paths
- 5.2: Existing branch detection and reuse
- 5.3: Worktree-based submodule creation (replace `--reference`)
- 5.4: Existing submodule branch detection and reuse
- 5.5: Sandbox registration (both main and worktree settings files)
- 5.6: Environment initialization (`just setup` with warning)
- 5.7: Add `--task` option with `--session-md` default
- 5.8: Task mode: slug derivation + focused session generation
- 5.9: Task mode: tab-separated output format (`<slug>\t<path>`)
- 5.10: Session file handling (warn and ignore `--session` when branch exists)

**Depends on:** Phases 1, 2, 4 (functions must exist)

---

### Phase 6: Update `rm` Command

**Complexity:** Medium (7 cycles)
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_rm.py`
**Description:** Refactor `rm` command with improved removal logic

**Cycles:**
- 6.1: Use `wt_path()` for path resolution
- 6.2: Uncommitted changes warning
- 6.3: Worktree registration probing (parent and submodule)
- 6.4: Submodule-first removal ordering
- 6.5: Directory cleanup (orphaned directories)
- 6.6: Container cleanup (empty container removal)
- 6.7: Safe branch deletion (`-d` with fallback warning)

**Depends on:** Phase 1 (`wt_path()` function)

---

### Phase 7: Add `merge` Command (4-Phase Ceremony)

**Complexity:** High (12 cycles)
**Files:** `src/claudeutils/worktree/cli.py`, `tests/test_worktree_merge.py`
**Description:** Implement 4-phase merge ceremony with auto-resolution

**Cycles:**
- 7.1: Phase 1 pre-checks — OURS clean tree (session exempt)
- 7.2: Phase 1 pre-checks — THEIRS clean tree (strict, no session exemption)
- 7.3: Phase 1 pre-checks — branch existence, worktree directory check
- 7.4: Phase 2 submodule resolution — ancestry check
- 7.5: Phase 2 submodule resolution — fetch if needed (with object check)
- 7.6: Phase 2 submodule resolution — merge and commit
- 7.7: Phase 3 parent merge — initiate merge
- 7.8: Phase 3 conflict handling — agent-core auto-resolve
- 7.9: Phase 3 conflict handling — session.md auto-resolve (task extraction)
- 7.10: Phase 3 conflict handling — learnings.md auto-resolve (append theirs-only)
- 7.11: Phase 3 conflict handling — source file abort
- 7.12: Phase 4 precommit validation — run and check exit code

**Depends on:** Phase 1 (`wt_path()` for directory resolution), Phase 0 (`clean-tree` command)

**Checkpoint:** Full checkpoint at end of Phase 7 (fix + vet + functional)

---

### Phase 8: Non-Code Artifacts

**Complexity:** Low (not TDD)
**Files:** `justfile`, `agent-core/justfile`, `agent-core/skills/worktree/SKILL.md`, `agent-core/fragments/execute-rule.md`
**Description:** Update justfile recipes, skill, and documentation

**Tasks (not cycles):**
- 8.1: Justfile `wt-ls` — native bash `git worktree list` parsing
- 8.2: Justfile `wt-merge` — add THEIRS clean tree check (strict)
- 8.3: Agent-core justfile — add `setup` recipe
- 8.4: Skill Mode A — use `new --task`, remove inline focus-session
- 8.5: Skill Mode C — use `merge` command
- 8.6: Execute-rule.md — update Worktree Tasks marker (slug-only, no `wt/` prefix)

---

### Phase 9: Interactive Refactoring

**Complexity:** N/A (opus interactive, not delegated)
**Files:** `justfile` (wt-* recipes)
**Description:** Reduce verbosity in justfile recipes, extract shared patterns, apply deslop

**Approach:** Opus interactive session (not TDD, not delegated). User-driven refactoring.

---

## Key Design Decisions Reference

Decision 1 (D1): Path computation — `wt_path(slug)` with container detection
Decision 2 (D2): Worktree-based submodule — `git -C agent-core worktree add`
Decision 3 (D3): Skill primary, recipes independent — zero coupling
Decision 4 (D4): Single implementation — no duplication for shared logic
Decision 5 (D5): Environment init warn only — `just setup` prerequisite
Decision 6 (D6): CLI hidden — `_worktree` prefix
Decision 7 (D7): Task mode — `new --task "<name>"` combines operations
Decision 8 (D8): Justfile independence — both Python merge and justfile check both sides

---

## Complexity Distribution

| Phase | Cycles | Complexity | Model |
|-------|--------|------------|-------|
| 0: Setup | 2 | Low | haiku |
| 1: wt_path() | 5 | Medium | haiku |
| 2: add_sandbox_dir() | 4 | Medium | haiku |
| 3: derive_slug() | 3 | Low | haiku |
| 4: focus_session() | 5 | Medium | haiku |
| 5: new command | 10 | High | haiku |
| 6: rm command | 7 | Medium | haiku |
| 7: merge command | 12 | High | haiku |
| 8: Non-code | N/A | Low | sonnet (direct) |
| 9: Refactoring | N/A | N/A | opus (interactive) |

**Total TDD cycles:** 48 (Phases 0-7)

---

## Expansion Guidance

**Phase-by-phase expansion:**
- Each phase generates cycle details with RED/GREEN/Stop Conditions
- Per-phase review by tdd-plan-reviewer (prescriptive code detection)
- Full review after all phases complete (cross-phase consistency)

**Investigation prerequisites:**
- Phase 5 and 7 modify existing `new` and `rm` commands — read current implementations before writing
- Phase 7 merge ceremony — read justfile `wt-merge` recipe (lines 200-310) for reference

**Conformance note:**
- Phase 7 merge command conforms to justfile prototype behavior
- Tests must include exact exit codes (0, 1, 2) and phase outcomes
- Session file auto-resolution strategies must match justfile patterns

**File size tracking:**
- `cli.py` currently ~386 lines
- Phase 5 adds ~100-150 lines (new command refactor + task mode)
- Phase 7 adds ~150-200 lines (merge ceremony)
- Estimate: ~636-736 lines after Phase 7 → split required in Phase 7 cleanup cycle

---

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Consolidation candidates:**
- Phase 8 tasks 8.1-8.3 (justfile changes) could be consolidated into single task if editing same recipe sections
- Phase 0 cycles (2 total, both trivial) could merge with Phase 1 start if no independent verification needed
- Consider whether Phase 3 (derive_slug edge cases, 3 cycles) merges with Phase 5 cycle 5.8 (slug derivation in task mode) for integration testing

**Cycle expansion:**
- Phase 5 cycle 5.3 (worktree-based submodule): Include shell line reference to justfile wt-new recipe (lines 150-180) for object store verification approach
- Phase 7 cycles 7.8-7.11 (conflict handling): Reference justfile wt-merge recipe conflict resolution section (lines 250-290) for auto-resolution patterns
- Phase 7 cycle 7.9 (session.md task extraction): Specify exact regex pattern from design (line 152): `- [ ] **<name>**`
- Phase 6 cycle 6.4 (removal ordering): Note git error message for detection: "fatal: 'remove' refusing to remove..." when order violated

**Checkpoint guidance:**
- Phase 7 checkpoint must include functional validation: create worktree, make conflicting changes (session.md, learnings.md, agent-core), verify auto-resolution behavior
- Phase 7 exit code validation: Test all three exit codes (0=success, 1=conflicts/precommit, 2=fatal) with explicit assertions
- Post-Phase 5 state: Verify `claudeutils _worktree new --task` creates worktree at sibling path and outputs tab-separated format

**References to include:**
- Design lines 64-101 (new command update section) → expand into Phase 5 cycle details
- Design lines 123-172 (merge command 4-phase ceremony) → expand into Phase 7 cycle details
- Design lines 178-196 (focus_session function) → expand into Phase 4 cycle details
- Justfile lines 100-300 (wt-* recipes) → reference for conformance verification in test assertions

**Module split guidance (if cli.py >700 lines after Phase 7):**
- Extract functions to `src/claudeutils/worktree/core.py`: wt_path, add_sandbox_dir, derive_slug, focus_session
- Leave CLI commands in `cli.py` as thin wrappers calling core functions
- Update tests to import from core module for function-level tests, cli module for command-level tests
