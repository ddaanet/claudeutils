# Worktree-Skill Deliverable Review

**Date:** 2026-02-11
**Ground truth:** `plans/worktree-skill/outline.md`
**Methodology:** `agents/decisions/deliverable-review.md`
**Coverage:** 24/24 deliverables (100%)

## Summary

| Severity | Count |
|----------|-------|
| Critical | 3 |
| Major | 12 |
| Minor | 12 |
| **Total** | **27** |

---

## Code Findings (Deliverables 1-5)

### cli.py

**C1. Dead code: `derive_slug()` never called** — cli.py:17-31
- Axis: Excess
- Severity: Major
- `derive_slug()` is defined but never called by any CLI command or imported by any module. The CLI takes `slug` as an argument; slug derivation is agent-side (SKILL.md step 2). Tests exercise it, but the function has no production consumer.

**C2. No slug format validation in `cmd_new()`** — cli.py:60
- Axis: Robustness
- Severity: Major
- `cmd_new()` accepts any string as slug — empty string, `..`, path traversal (`../../etc`), special chars. No validation that slug is a safe directory name. The `derive_slug()` function produces safe slugs, but since it's not wired into the CLI, raw user input passes through.

### commands.py

**C3. Duplicate `get_dirty_files()` and `check_clean_tree()`** — commands.py:38-72 vs merge_helpers.py:82-116
- Axis: Modularity
- Severity: Major
- Near-identical implementations in both files. merge_helpers.py version has comment "Get dirty files without circular import." The duplication exists to break a circular dependency (commands.py → merge_helpers.py → commands.py). Refactor: extract shared utility to a common module (e.g., `git_utils.py`).

**C4. `__all__` re-exports from merge_helpers** — commands.py:23-35
- Axis: Modularity
- Severity: Minor
- `apply_theirs_resolution`, `capture_untracked_files`, `parse_precommit_failures` are re-exported from commands.py but defined in merge_helpers.py. Tests import from commands.py. Clean up: tests should import from the defining module.

### conflicts.py

**C5. `resolve_source_conflicts()` uses raw `subprocess.run`** — conflicts.py:244-252
- Axis: Modularity (inconsistency)
- Severity: Minor
- All other git operations use `run_git()` helper. This function uses raw `subprocess.run(["git", ...])` with its own `cwd` parameter. Inconsistent with codebase conventions.

### merge_phases.py

**C6. `merge --abort` after committed merge does nothing** — merge_phases.py:238, 242, 255
- Axis: Functional correctness
- Severity: Critical
- `merge_phase_3_commit_and_precommit()` creates the merge commit at line 217, then runs precommit at line 225. If precommit fails (and theirs-fallback also fails), it calls `run_git(["merge", "--abort"])` — but the merge is already committed (MERGE_HEAD was consumed by `git commit`). `git merge --abort` requires MERGE_HEAD; without it, the command fails silently (`check=False`). The merge commit persists. The user would need `git reset HEAD~1` to undo it, but the error message says "Manual resolution required" without mentioning this.

**C7. Missing lock file retry** — outline §Error Handling
- Axis: Conformance (missing specified behavior)
- Severity: Major
- Outline specifies "Lock file conflicts: built-in wait-1s-and-retry (2 retries max) before failing." No retry logic exists in any module. All `run_git()` calls fail immediately on lock file errors.

---

## Test Findings (Deliverables 6-18)

### test_merge_helpers.py (Deliverable 12)

**T1. Not a test file — utility module** — test_merge_helpers.py
- Axis: Vacuity
- Severity: Minor
- Contains `run_git()`, `init_repo()`, `setup_repo_with_submodule()` — zero test assertions. This is a shared test helper module, not a test file. Should be named `conftest_merge.py` or moved to a helpers package.

### test_worktree_merge_verification.py (Deliverable 10)

**T2. Tests verify git concepts, not production code** — test_worktree_merge_verification.py
- Axis: Independence
- Severity: Major
- Tests manually reproduce git merge operations and check ancestry — proving `merge-base --is-ancestor` works as expected. They do NOT exercise `submodule_merge_and_verify()` or `merge_phase_2_submodule()`. They verify the git primitives our code uses, not that our code calls them correctly. An e2e test through `cmd_merge()` would have higher value (and test_merge_phase_2.py already provides this).

### test_execute_rule_mode5_refactor.py (Deliverable 17)

**T3. 6 of 8 tests assert absence, not correctness** — test_execute_rule_mode5_refactor.py:49-139
- Axis: Vacuity (half-vacuous)
- Severity: Major
- Tests `test_*_no_slug_derivation_prose`, `test_*_no_single_task_flow_steps`, `test_*_no_parallel_group_flow_steps`, `test_*_no_focused_session_template`, `test_*_no_output_format_section` verify old content was removed. They provide no ongoing regression value — if someone adds "lowercase, hyphens" to Mode 5, these tests break, but that's unlikely and unrelated to behavioral correctness.

### Critical Scenario Coverage Checklist

| Scenario | Covered by | Status |
|----------|-----------|--------|
| Submodule merge (diverged commits) | test_merge_phase_2.py `test_merge_phase_2_diverged_commits` | ✓ |
| Submodule merge (fast-forward) | test_merge_phase_2.py `test_merge_phase_2_fast_forward` | ✓ |
| Session file conflict (learnings keep-both) | test_session_conflicts.py, test_merge_phase_3_conflicts.py | ✓ |
| Session file conflict (session keep-ours + append) | test_session_conflicts.py, test_merge_phase_3_conflicts.py | ✓ |
| Conflict resolution + resume | test_merge_phase_3_conflicts.py `test_merge_idempotent_resume` | ✓ |
| Idempotent merge | test_merge_phase_3_conflicts.py `test_merge_idempotent_resume` | ✓ |
| Clean-tree gate | test_worktree_clean_tree.py (3 tests) | ✓ |
| Merge debris cleanup after abort | Not directly tested | ✗ |
| Overlapping source refactors (take-ours + precommit gate) | test_merge_phase_3_precommit.py (partially) | ~  |
| Task recovery from worktree session.md | test_session_conflicts.py `test_*_extracts_from_worktree` | ✓ |
| Jobs.md status advancement | test_session_conflicts.py (2 tests) | ✓ |

**T4. Merge debris cleanup not tested** — outline §Testing
- Axis: Coverage
- Severity: Major
- `clean_merge_debris()` and the post-failure untracked file cleanup in `merge_phase_3_parent()` have no dedicated test. The behavior exists in code (merge_phases.py:155-161, 187-191) but is never directly exercised.

**T5. Source conflict take-ours + precommit gate only partially tested**
- Axis: Coverage
- Severity: Minor
- `test_merge_phase_3_precommit_gate_fallback_to_theirs` tests `apply_theirs_resolution()` in isolation and `parse_precommit_failures()` parsing. But the full flow (take-ours → precommit fails → fallback to theirs → re-check precommit) is not tested end-to-end through `cmd_merge()`.

### Test Suite Density Issues

**T6. Git init boilerplate defined 5 times independently**
- Axis: Excess (duplication)
- Severity: Major
- `_init_repo()` / `_init_git_repo()` independently defined in test_worktree_cli.py:12, test_worktree_rm.py:13, test_worktree_new.py:12, test_merge_helpers.py:20, and conftest.py:284 (`repo_with_submodule`). Five implementations of identical 6-line git init. conftest.py's fixture serves some tests, but most files define their own.

**T7. Submodule setup defined 3 times independently**
- Axis: Excess (duplication)
- Severity: Major
- test_worktree_new.py:33 `_setup_repo_with_submodule()` (40 lines), test_merge_helpers.py:27 `setup_repo_with_submodule()` (38 lines), conftest.py:271 `repo_with_submodule` fixture (70 lines). Three implementations with slightly different signatures and conventions. The conftest fixture uses `git submodule add`; the others use manual `update-index --cacheinfo`.

**T8. Raw subprocess boilerplate instead of shared helper** — multiple files
- Axis: Excess (verbosity)
- Severity: Minor
- test_worktree_merge_verification.py, test_worktree_source_conflicts.py, test_worktree_new.py use raw `subprocess.run(["git", ...], cwd=..., check=True, capture_output=True)` repeated dozens of times. test_merge_helpers.py provides `run_git()` for exactly this purpose, but only test_merge_phase_2.py, test_merge_phase_3_*.py use it.

**T9. test_worktree_merge_verification.py: ~90% setup, tests prove git works** — 341 lines
- Axis: Excess (signal-to-noise)
- Severity: Minor
- Two tests, each ~160 lines. Each manually constructs diverged git history via ~30 subprocess calls. The assertion is 3-4 lines checking `merge-base --is-ancestor`. Combined with T2 (tests don't exercise production code), these 341 lines could be deleted entirely — test_merge_phase_2.py already covers the same scenarios through the actual merge command.

**T10. test_execute_rule_mode5_refactor.py: section extraction copy-pasted 8 times**
- Axis: Excess (duplication)
- Severity: Minor
- Every test repeats the same 7-line pattern: read file → find "### MODE 5" → find next section → extract slice. A `_get_mode5_section()` helper + parametrize would reduce 139 lines to ~30.

**T11. test_worktree_skill_frontmatter.py: 10 micro-tests for YAML schema**
- Axis: Excess (granularity)
- Severity: Minor
- Each test calls `_parse_frontmatter()` independently. `test_*_has_continuation`, `test_*_cooperative`, `test_*_default_exit` are three tests for one nested dict. A single `test_frontmatter_schema()` or 2-3 grouped tests would cover the same contract with less overhead.

**T12. Near-duplicate test adds no value** — test_worktree_source_conflicts.py:201-222
- Axis: Vacuity
- Severity: Minor
- `test_resolve_source_conflicts_returns_list_of_resolved_files` asserts `isinstance(resolved, list)`, `len(resolved) > 0`, `"app.py" in resolved`, `isinstance(item, str)` — all already implied by `assert "app.py" in resolved` in the preceding test.

---

## Agentic Prose Findings (SKILL.md — Deliverable 19)

**A1. Wrong path in launch command** — SKILL.md:68, 95-96
- Axis: Functional correctness
- Severity: Critical
- Mode A step 7: `cd ../<repo>-<slug> && claude` — should be `cd wt/<slug>`. The worktree is inside the project root at `wt/<slug>/`, not a sibling directory. Mode B step 5 has the same error at lines 95-96.

**A2. Lock file removal instruction violates behavioral rule** — SKILL.md:129
- Axis: Constraint precision (contradicts established rule)
- Severity: Major
- Mode C step 5: "Run `git status` to inspect tree, check for stale locks (`rm .git/index.lock` if present)" — contradicts the "Never agent-initiate lock file removal" learning and behavioral rule. Agent should stop and report, not remove lock files.

**A3. Usage Notes contradict Mode C** — SKILL.md:140-141
- Axis: Consistency
- Severity: Minor
- "The worktree merge ceremony does not automatically delete branches or cleanup" and "Merge and cleanup are separate user actions" — but Mode C step 3 explicitly invokes `claudeutils _worktree rm <slug>` after successful merge, which DOES delete branches and cleanup. The Usage Notes describe a behavior that Mode C doesn't implement.

**A4. Vague "special characters" in slug derivation** — SKILL.md:33
- Axis: Determinism
- Severity: Minor
- "remove special characters" — which characters are special? The code uses `[^a-z0-9]+` (anything not alphanumeric becomes a hyphen). The SKILL.md instruction is imprecise enough that different agents might implement differently.

---

## Human Documentation Findings (Deliverables 20-21)

### sandbox-exemptions.md (Deliverable 21)

**D1. Wrong directory convention** — sandbox-exemptions.md:40
- Axis: Accuracy
- Severity: Critical
- "Git worktrees are created inside the project root (`worktrees/<slug>/`)" — should be `wt/<slug>/`. The entire worktree-skill uses `wt/` convention, and all code references `Path(f"wt/{slug}")`.

### execute-rule.md (Deliverable 20)

No issues found. Mode 5 section is minimal, correctly triggers on `wt`, and references SKILL.md for details.

---

## Configuration Findings (Deliverables 22-24)

### .gitignore (Deliverable 24)

**G1. Missing `/wt/` entry** — .gitignore
- Axis: Functional completeness
- Severity: Major
- The project .gitignore has no `/wt/` entry. Test fixtures add `wt/` to their test repos' .gitignore (test_worktree_new.py:111, test_merge_helpers.py:61), confirming the requirement. Without this entry, worktree directories would appear as untracked files and could be accidentally committed.

### justfile (Deliverable 22)

**G2. Dead `wt-path()` helper function** — justfile:252-260
- Axis: Excess
- Severity: Minor
- Old `wt-path()` bash helper still exists. Uses `../<parent>-wt/` convention which doesn't match current `wt/<slug>/` convention. wt-* recipes were deleted per outline, but this helper function was missed.

### .cache/just-help.txt (Deliverable 23)

No wt-* entries. Correct.

---

## Gap Analysis

| Outline §Scope In item | Deliverable(s) | Status |
|------------------------|----------------|--------|
| CLI subcommand (TDD) | 1-5 | ✓ |
| SKILL.md | 19 | ✓ (with bugs) |
| execute-rule.md Mode 5 update | 20 | ✓ |
| Delete justfile recipes | 22-23 | ✓ (dead helper remains) |
| Update handoff template | handoff/references/template.md | ✓ (Worktree Tasks section present) |
| End-to-end tests (submodule merging) | 10, 12, 13 | ✓ |
| Absorb wt-merge-skill | plans/wt-merge-skill/ deleted | ✓ |
| Lock file retry | — | ✗ Not implemented |
| Merge debris cleanup | merge_phases.py:155-161 | ✓ (code exists, not tested) |
| Submodule object fetch | merge_phases.py:128-142 | ✓ |

---

## Cross-Cutting Issues

**X1. Path inconsistency across documents**
Three deliverables use wrong directory conventions while all code correctly uses `wt/<slug>/`. Findings: A1, D1, G2.

**X2. API contract gap: commands.py ↔ merge_helpers.py**
Circular dependency forced code duplication (C3). The module boundary between commands.py (subcommand entry points) and merge_helpers.py (merge utilities) is unclear — both contain `get_dirty_files` and `check_clean_tree`.

---

## Findings by Severity

### Critical (3)
- C6: `merge --abort` after committed merge does nothing
- A1: Wrong path in SKILL.md launch commands
- D1: Wrong directory convention in sandbox-exemptions.md

### Major (12)
- C1: Dead `derive_slug()` in cli.py
- C2: No slug format validation in `cmd_new()`
- C3: Duplicate get_dirty_files/check_clean_tree across modules
- C7: Missing lock file retry (spec'd in outline)
- T2: Verification tests don't exercise production code
- T3: Mode 5 tests verify absence, not correctness (half-vacuous)
- T4: Merge debris cleanup untested
- T6: Git init boilerplate defined 5 times independently
- T7: Submodule setup defined 3 times independently
- A2: Lock file removal instruction contradicts rule
- G1: Missing `/wt/` in .gitignore
- G2: Dead `wt-path()` references wrong convention

### Minor (12)
- C4: `__all__` re-exports from wrong module
- C5: Inconsistent subprocess.run vs run_git
- T1: test_merge_helpers.py is a utility module, not tests
- T5: Source conflict flow partially tested
- T8: Raw subprocess boilerplate instead of shared helper
- T9: test_worktree_merge_verification.py ~90% setup (341 lines, deletable)
- T10: Mode 5 section extraction copy-pasted 8 times
- T11: 10 micro-tests for YAML schema (3 would suffice)
- T12: Near-duplicate test adds no value
- A3: Usage Notes contradict Mode C behavior
- A4: Vague "special characters" in slug derivation
- G2: Dead `wt-path()` in justfile

---

## Findings by Axis

| Axis | Count |
|------|-------|
| Functional correctness | 2 (C6, A1) |
| Functional completeness | 2 (C7, G1) |
| Conformance | 1 (C7) |
| Excess (including duplication/density) | 9 (C1, G2, T6, T7, T8, T9, T10, T11, T12) |
| Vacuity | 3 (T1, T3, T12) |
| Robustness | 1 (C2) |
| Modularity | 3 (C3, C4, C5) |
| Coverage | 2 (T4, T5) |
| Independence | 1 (T2) |
| Accuracy | 1 (D1) |
| Consistency | 1 (A3) |
| Constraint precision | 1 (A2) |
| Determinism | 1 (A4) |
