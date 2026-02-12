# Worktree-Skill Deliverable Review Outline

Review of worktree-skill delivery against `plans/worktree-skill/outline.md` using `agents/decisions/deliverable-review.md` methodology.

## Context

- **Ground truth:** `plans/worktree-skill/outline.md` (human-validated)
- **Methodology:** `agents/decisions/deliverable-review.md`
- **Total:** 24 deliverables, 42K tokens, single session
- **Do NOT read:** `agents/decisions/review-methodology.md`, any execution report, any planning artifact beyond outline.md

## Deliverables by Type

### Code (5 modules, 10K tokens)

| # | File | Tokens | Outline sections to verify against |
|---|------|--------|-------------------------------------|
| 1 | `cli.py` | 977 | §CLI Subcommands — dispatch to 6 subcommands, `claudeutils _worktree` naming |
| 2 | `commands.py` | 2506 | §CLI Subcommands — `new`, `rm`, `ls`, `clean-tree`, `add-commit` signatures and behavior |
| 3 | `conflicts.py` | 2697 | §Session File Conflict Resolution — session.md/learnings.md/jobs.md algorithms, §Source Code Conflict Resolution — take-ours/take-theirs/precommit gate, §Batch Stale Worktree Removal — task extraction algorithm |
| 4 | `merge_helpers.py` | 1208 | §Submodule Merge Resolution — fetch, ancestry check, post-merge verification |
| 5 | `merge_phases.py` | 2662 | §Submodule Merge Resolution — 4-step resolution sequence, §Key Decisions — idempotent merge |

**Code-specific axes:** robustness, modularity, testability, idempotency, error signaling

**Per-file checks:**
- `cli.py`: Is the CLI name `_worktree` or `worktree`? (outline says `_worktree`). Subcommand list matches outline's 6 commands. Slug derivation if present.
- `commands.py`: Each subcommand signature matches outline (`new <slug> [--base HEAD] [--session <path>]`, etc.). `clean-tree` reports status for tree + submodules. `add-commit` reads commit message from stdin.
- `conflicts.py`: Session.md algorithm matches §Task extraction algorithm (5-step regex-based). Learnings.md is keep-both. Jobs.md is keep-ours + status advancement. Source conflicts follow 4-step take-ours/take-theirs/precommit/stop sequence.
- `merge_helpers.py`: Fetch uses worktree submodule path. Ancestry check uses `merge-base --is-ancestor`. Post-merge verifies both pointers are ancestors.
- `merge_phases.py`: Implements 4-step resolution sequence from §Submodule Merge Resolution. Idempotent — stops at conflict/precommit failure, resumes after resolution.

### Test (12 files, 22K tokens)

| # | File | Tokens | Covers |
|---|------|--------|--------|
| 6 | `test_worktree_cli.py` | 1697 | cli.py dispatch |
| 7 | `test_worktree_new.py` | 2642 | commands.py new |
| 8 | `test_worktree_rm.py` | 1171 | commands.py rm |
| 9 | `test_worktree_clean_tree.py` | 2097 | commands.py clean-tree |
| 10 | `test_worktree_merge_verification.py` | 2744 | merge_helpers.py verification |
| 11 | `test_worktree_source_conflicts.py` | 1881 | conflicts.py source |
| 12 | `test_merge_helpers.py` | 857 | merge_helpers.py |
| 13 | `test_merge_phase_2.py` | 2423 | merge_phases.py submodule |
| 14 | `test_merge_phase_3_conflicts.py` | 3103 | conflicts.py session |
| 15 | `test_merge_phase_3_precommit.py` | 2343 | precommit gate |
| 16 | `test_session_conflicts.py` | 2652 | conflicts.py session algorithms |
| 17 | `test_execute_rule_mode5_refactor.py` | 1705 | execute-rule.md changes |
| 18 | `test_worktree_skill_frontmatter.py` | 1056 | SKILL.md structure |

**Test-specific axes:** specificity, coverage, independence

**Per-file checks:**
- Each test file: Are tests behavioral (verify outcomes) or structural (verify implementation details like command strings)?
- Vacuity scan: Does each test assert something meaningful? Tests that only check existence/absence without verifying correctness are vacuous.
- Outline §Testing critical scenarios coverage. Check each is covered by at least one test:
  - [ ] Submodule merge (diverged commits)
  - [ ] Submodule merge (fast-forward)
  - [ ] Session file conflict resolution (learnings keep-both)
  - [ ] Session file conflict resolution (session keep-ours)
  - [ ] Conflict resolution + resume
  - [ ] Idempotent merge
  - [ ] Clean-tree gate
  - [ ] Merge debris cleanup after abort
  - [ ] Overlapping source refactors (take-ours + precommit gate)
  - [ ] Task recovery from worktree session.md
  - [ ] Jobs.md status advancement
- Outline §Testing conventions: integration-first with real git repos (tmp_path), no subprocess mocking for behavior, autospec on all mocks, shared fixture.

### Agentic Prose (1 file, 2.5K tokens)

| # | File | Tokens | Outline sections |
|---|------|--------|-----------------|
| 19 | `SKILL.md` | 2522 | §Skill Orchestration — slug derivation, session.md task movement, focused session extraction, parallel group detection, handoff/commit ceremony, error communication |

**Agentic-specific axes:** actionability, constraint precision, determinism, scope boundaries

**Per-file checks:**
- Every instruction step produces a tool call or observable state change
- No vague criteria ("relevant", "appropriate", "as needed")
- Slug derivation algorithm specified precisely
- Session.md manipulation steps deterministic (task regex, section names)
- Parallel group detection is "prose, not scripted" per outline — verify skill reflects this
- Directory paths: must use `wt/<slug>/` convention (known bug: may reference `../<repo>-<slug>`)
- Error handling: lock file wait-and-retry, never agent-initiate lock removal, merge debris cleanup

### Human Documentation (2 files, 2.8K tokens)

| # | File | Tokens | Outline sections |
|---|------|--------|-----------------|
| 20 | `execute-rule.md` | 1975 | §Key Decisions — Mode 5 triggers, behavior, worktree task notation |
| 21 | `sandbox-exemptions.md` | 792 | §Key Decisions — directory convention, sandbox patterns |

**Human-doc-specific axes:** accuracy, consistency, completeness, usability

**Per-file checks:**
- `execute-rule.md` Mode 5: Triggers match outline (`wt` no args, `wt <task-name>`). References SKILL.md correctly. Worktree Tasks section notation consistent with rest of document.
- `sandbox-exemptions.md`: Directory path must be `wt/<slug>/` not `worktrees/<slug>/` (known bug). Sandbox bypass list matches what CLI actually needs.

### Configuration (3 items, ~0.5K tokens)

| # | File | Check |
|---|------|-------|
| 22 | `justfile` | wt-new, wt-task, wt-ls, wt-rm, wt-merge recipes absent |
| 23 | `.cache/just-help.txt` | Regenerated, no wt-* entries |
| 24 | `.gitignore` | `/wt/` entry present |

**Universal axes only.** Verification is mechanical.

## Gap Analysis Checklist

Items from outline §Scope In that must map to at least one deliverable:

- [ ] CLI subcommand (TDD) → deliverables 1-5
- [ ] SKILL.md → deliverable 19
- [ ] execute-rule.md Mode 5 update → deliverable 20
- [ ] Delete justfile recipes → deliverable 22-23
- [ ] Update handoff template → **verify: which file? is it done?**
- [ ] End-to-end tests (submodule merging) → deliverables 10, 12, 13
- [ ] Absorb wt-merge-skill → **verify: plan artifacts cleaned up?**
- [ ] §Error Handling — lock file retry, merge debris cleanup, submodule object fetch → verify in code

## Review Procedure

1. Read `plans/worktree-skill/outline.md` (already in CLAUDE.md context)
2. Read `agents/decisions/deliverable-review.md` for axes
3. Read all code deliverables (1-5), evaluate per-file checks + code axes
4. Read all test deliverables (6-18), evaluate per-file checks + test axes + critical scenario coverage
5. Read agentic prose (19), evaluate per-file checks + agentic axes
6. Read human docs (20-21), evaluate per-file checks + human-doc axes
7. Verify configuration (22-24)
8. Complete gap analysis checklist
9. Cross-cutting: path consistency (`wt/<slug>/` everywhere), API contracts between modules (cli→commands→merge_phases→merge_helpers→conflicts), naming conventions
10. Write findings to `plans/worktree-skill/reports/deliverable-review.md` with per-deliverable findings (file:line, axis, severity, description)
