# Worktree Skill — TDD Intake Assessment

**Date:** 2026-02-10
**Design:** `plans/worktree-skill/design.md`

## Tier Assessment

### Files Affected

**Source files (new):**
- `src/claudeutils/worktree/__init__.py` (empty)
- `src/claudeutils/worktree/cli.py` (Click group + 6 subcommands)
- `src/claudeutils/worktree/merge.py` (3-phase merge orchestration)
- `src/claudeutils/worktree/conflicts.py` (session/learnings/jobs/source resolution)

**Source files (modified):**
- `src/claudeutils/cli.py` (register `_worktree` command group)
- `.gitignore` (add `wt/` entry)

**Test files (new):**
- `tests/test_worktree_cli.py` (new, rm, ls, clean-tree, add-commit subcommands)
- `tests/test_worktree_merge.py` (full merge flow, submodule resolution, idempotency)
- `tests/test_worktree_conflicts.py` (session/learnings/jobs/source conflict resolution)

**Skill files (new):**
- `agent-core/skills/worktree/SKILL.md` (orchestration skill)

**Documentation files (modified):**
- `agent-core/fragments/execute-rule.md` (Mode 5 update to reference skill)
- `agent-core/fragments/sandbox-exemptions.md` (add worktree patterns)
- `justfile` (delete wt-* recipes)
- `.cache/just-help.txt` (regenerate after recipe deletion)

**Total:** 4 source modules, 3 test modules, 1 skill, 4 docs = **12 files**

### Open Decisions

**None.** All design decisions (D-1 through D-10) are resolved:
- D-1: Directory location (`wt/<slug>/` inside project root)
- D-2: Branch naming (no prefix, user requirement)
- D-3: Merge flags (`--no-commit --no-ff`)
- D-4: Precommit as oracle
- D-5: CLI vs skill boundary
- D-6: Session conflict extraction before resolution
- D-7: Submodule merge before parent
- D-8: Idempotent merge design
- D-9: No plan-specific agent
- D-10: add-commit idempotency

**Dependency resolution:** focus-session.py implementation deferred — skill generates inline (D-5, Dependencies section).

### Cycles Estimated

**Analysis from requirements + test scenarios:**

| Module | Cycles | Rationale |
|--------|--------|-----------|
| worktree/cli.py | ~12-15 | 6 subcommands (new, rm, ls, merge, clean-tree, add-commit) + slug derivation utility |
| worktree/merge.py | ~8-10 | 3 phases (pre-checks, submodule, parent) + idempotency + debris cleanup |
| worktree/conflicts.py | ~8-10 | 4 resolution functions (session, learnings, jobs, source) + parsing logic |
| SKILL.md | ~3-5 | 3 modes (single-task, parallel, merge ceremony) + frontmatter |
| Integration wiring | ~2-3 | CLI registration, .gitignore, documentation updates |
| Documentation | ~2-3 | execute-rule.md, sandbox-exemptions.md, justfile cleanup |

**Total estimate:** 35-46 cycles

**Refinement:** Test scenarios table (design line 443) lists 12 critical scenarios. With ~3 cycles per scenario (RED → GREEN → REFACTOR), base is ~36 cycles. Add integration wiring + skill + docs = **40-45 cycles**.

### Model Requirements

**Multiple models required:**

| Work Type | Model | Rationale |
|-----------|-------|-----------|
| SKILL.md authoring | Opus | Workflow artifact, integration point coordination |
| CLI implementation | Sonnet | Feature implementation with judgment (conflict resolution logic) |
| Test implementation | Sonnet | Behavioral verification, fixture setup |
| Integration wiring | Haiku | Mechanical (CLI registration, .gitignore update) |
| Documentation updates | Haiku | Prose updates to fragments, justfile recipe deletion |

**Multi-model coordination:** Opus for SKILL.md, sonnet for CLI + tests, haiku for wiring/docs.

### Session Span

**Multi-session.** Estimated 40-45 cycles exceed single-session capacity for sonnet (typical limit ~20-25 cycles with high complexity).

**Session boundaries:**
- Session 1: SKILL.md (opus) + CLI foundation + basic tests (sonnet)
- Session 2: Merge flow + conflict resolution (sonnet)
- Session 3: Integration tests + edge cases (sonnet)
- Session 4: Wiring + documentation (haiku)

### Tier Decision

**Tier 3: Full Runbook**

**Rationale:**
- 40-45 cycles exceeds Tier 2 threshold (10-20 cycles)
- Multiple models required (opus, sonnet, haiku)
- Multi-session span (estimated 3-4 sessions)
- High complexity: git plumbing, submodule operations, idempotent state machines
- Integration across CLI + skill + documentation with coordination points

**Tier 2 disqualified:** Despite some repetitive patterns (6 CLI subcommands), the merge flow and conflict resolution require careful orchestration. Not simple repetitive work.

## Codebase Discovery

### Existing Files

**None found:**
- No `tests/test_worktree*.py` files
- No `src/claudeutils/worktree/` directory
- No grep matches for "worktree" in `src/` or `tests/`

**Clean slate implementation.**

### Existing Patterns

**CLI registration pattern** (`src/claudeutils/cli.py:12-25`):
```python
from claudeutils.account.cli import account
from claudeutils.recall.cli import recall
# ... other imports

cli.add_command(account)
cli.add_command(recall)
```

Worktree will follow same pattern:
```python
from claudeutils.worktree.cli import worktree
cli.add_command(worktree, "_worktree")
```

**Test fixtures** (`tests/conftest.py`):
- `temp_project_dir`: Returns `(project_dir, history_dir)` with mocked paths
- `temp_history_dir`: Similar pattern for history-only testing
- Pattern: Use `tmp_path` from pytest, create git repos fresh per test

**Git operations in existing tests** (`tests/test_statusline_context.py:26-95`):
- Mock subprocess.run for git commands
- Test pattern: mock git commands, verify subprocess calls

**For worktree tests:** Integration-first approach (design line 431) — real git repos via `tmp_path`, not mocked subprocess. Only mock for error injection.

### Integration Points

**CLI entry point** (`src/claudeutils/cli.py`):
- Add import: `from claudeutils.worktree.cli import worktree`
- Add registration: `cli.add_command(worktree, "_worktree")`

**.gitignore:**
- Add line: `wt/`

**execute-rule.md Mode 5:**
- Replace inline prose with skill reference: "Invoke `/worktree` skill"

**sandbox-exemptions.md:**
- Add section for worktree patterns (uv sync, direnv allow in new worktrees)

**justfile:**
- Delete recipes: `wt-new`, `wt-task`, `wt-ls`, `wt-rm`, `wt-merge`
- Regenerate: `.cache/just-help.txt`

## Requirements Summary

### Functional Requirements

- **FR-1:** CLI subcommand `_worktree` with new/rm/merge/ls/clean-tree/add-commit
- **FR-2:** Submodule merge resolution (ancestry check, fetch, merge, verify)
- **FR-3:** Session file conflict resolution extracting new tasks before merge
- **FR-4:** Source code conflict resolution (take-ours + precommit gate + fallback)
- **FR-5:** SKILL.md orchestrating session manipulation, ceremony, parallel detection
- **FR-6:** execute-rule.md Mode 5 update to reference skill
- **FR-7:** Delete justfile wt-* recipes
- **FR-8:** Integration tests with real git repos + submodules

### Non-Functional Requirements

- **NFR-1:** Merge is idempotent — can resume after conflict resolution
- **NFR-2:** All session/learnings/jobs conflict resolution is deterministic (no agent judgment)
- **NFR-3:** Submodule commits use direct git plumbing, not `/commit` skill
- **NFR-4:** Post-merge precommit is mandatory correctness gate
- **NFR-5:** CLI follows existing claudeutils patterns (Click, error to stderr, exit codes)

### Design Decisions

- **D-1:** Directory inside project root (`wt/<slug>/`)
- **D-2:** No branch prefix (branches = `<slug>`, not `wt/<slug>`)
- **D-3:** Merge uses `--no-commit --no-ff` for custom messages + audit trail
- **D-4:** Precommit as correctness oracle for conflict resolution
- **D-5:** CLI does git plumbing, skill does ceremony
- **D-6:** Session conflict resolution extracts before resolving
- **D-7:** Submodule merge before parent merge
- **D-8:** Idempotent merge (detect state, resume safely)
- **D-9:** No plan-specific agent needed (skill + CLI only)
- **D-10:** add-commit is idempotent (exits cleanly if nothing staged)

### Phase Structure

**Design doesn't define explicit phases.** Planner should structure by functional grouping:

**Suggested phase structure:**
- **Phase 0:** CLI foundation (Click group, slug derivation, basic structure)
- **Phase 1:** Simple subcommands (ls, clean-tree, add-commit)
- **Phase 2:** Worktree lifecycle (new, rm)
- **Phase 3:** Conflict resolution utilities (session, learnings, jobs)
- **Phase 4:** Merge orchestration (3-phase flow, idempotency)
- **Phase 5:** Source conflict resolution (take-ours + precommit gate)
- **Phase 6:** SKILL.md (3 modes, orchestration logic)
- **Phase 7:** Integration wiring (CLI registration, .gitignore, docs)

**Rationale:** Build foundation → simple operations → complex state machines → skill orchestration → integration.

### Dependencies and Prerequisites

**Internal:**
- Click framework (already in use)
- Git 2.x with worktree + submodule support
- Existing test infrastructure (`tmp_path`, fixtures)

**External:**
- `plugin-dev:skill-development` — load before Phase 6 (SKILL.md authoring)

**Resolved dependencies:**
- focus-session.py NOT needed — skill generates inline (design Dependencies section)
- Continuation passing already merged (design Dependencies section)

## Parallelization Opportunities

### Test Files (Independent)

**Fully parallelizable:**
- `test_worktree_cli.py` — tests CLI subcommands (new, rm, ls, clean-tree, add-commit)
- `test_worktree_conflicts.py` — tests conflict resolution functions

**Partial dependency:**
- `test_worktree_merge.py` — depends on `conflicts.py` existing (uses conflict resolution in Phase 3)

**Strategy:** Develop cli.py + conflicts.py tests in parallel, merge.py tests after.

### Source Modules (Weak Dependencies)

**Independent:**
- `cli.py` — depends on `merge.py` only for `merge` subcommand
- `conflicts.py` — no dependencies (pure functions)

**Dependent:**
- `merge.py` — imports from `conflicts.py` for session file resolution

**Strategy:** Develop `cli.py` (with merge subcommand stubbed) + `conflicts.py` in parallel, then `merge.py`.

### Phases (Sequential)

**No phase parallelization.** Phases build on each other:
- Phase 0 (foundation) → Phase 1 (simple subcommands)
- Phase 3 (conflicts.py) → Phase 4 (merge.py uses conflicts)
- Phase 6 (SKILL.md) → requires all prior implementation complete

**Exception:** Phase 7 (documentation) could start during Phase 6 (SKILL.md authoring), but token savings minimal.

### Parallel Execution Assessment

**Not recommended for this feature.** Despite independent test files, the complexity of git operations and state management requires careful sequential validation. Merge conflicts between parallel branches would negate efficiency gains.

**Worktree pattern meta-irony:** This feature enables parallel work, but its own implementation benefits less from parallelization due to tight integration requirements.

## Critical Test Scenarios

From design line 443, 12 critical scenarios:

| Scenario | Module | Cycle Est. | Priority |
|----------|--------|-----------|----------|
| Submodule merge (diverged commits) | test_worktree_merge | 3-4 | High |
| Submodule merge (already included) | test_worktree_merge | 2-3 | High |
| Session keep-ours + task extraction | test_worktree_conflicts | 3-4 | Critical |
| Learnings keep-both | test_worktree_conflicts | 2 | Medium |
| Jobs status advancement | test_worktree_conflicts | 2-3 | Medium |
| Take-ours + precommit gate | test_worktree_merge | 3-4 | High |
| Conflict resolution + resume | test_worktree_merge | 3-4 | High |
| Idempotent merge | test_worktree_merge | 2-3 | High |
| New with --session pre-commit | test_worktree_cli | 3-4 | Critical |
| Clean-tree gate | test_worktree_cli | 2 | Medium |
| Merge debris cleanup | test_worktree_merge | 2-3 | Medium |
| Task recovery from worktree session.md | test_worktree_conflicts | 3-4 | Critical |

**Critical scenarios (5):** Session conflict resolution, task recovery, submodule divergence, --session pre-commit, precommit gate. These validate the core problem statement fixes.

## Integration Tests Strategy

**From design line 431:**
- **Approach:** Integration-first with `tmp_path` creating real git repos + submodules
- **Fixtures:** `base_repo`, `base_submodule`, `repo_with_submodule` in conftest
- **Isolation:** Each test gets fresh `git clone` of fixtures
- **Mocking:** Only for error injection (lock files, permission errors)

**Rationale:** Git with `tmp_path` is fast (milliseconds). Real git operations catch state transition bugs that mocks can't (E2E over mocked subprocess learning).

## Documentation Perimeter

**Required reading (planner must load):**
- `agents/decisions/cli.md` — CLI patterns (Click, error output, entry points)
- `agents/decisions/testing.md` — TDD approach, behavioral verification
- `plans/worktree-skill/outline.md` — Validated outline (binding scope)
- `plans/worktree-skill/reports/explore-integration.md` — Integration analysis

**Skill creation guidance:**
- Load `plugin-dev:skill-development` before Phase 6 (SKILL.md authoring)

**No Context7 needed.** All operations are git plumbing + Python Click.

## Next Steps

**Proceed to Phase 1: Runbook Outline Generation**

Runbook should follow phase structure suggested above (7 phases: CLI foundation → simple subcommands → lifecycle → conflicts → merge → skill → integration).

Load required documentation before Phase 2 (expansion):
- `agents/decisions/cli.md`
- `agents/decisions/testing.md`
- `plans/worktree-skill/outline.md`
- `plans/worktree-skill/reports/explore-integration.md`

Load `plugin-dev:skill-development` before Phase 6 expansion (SKILL.md authoring).

**Model assignments:**
- Phase 0-5: Sonnet (implementation + tests)
- Phase 6: Opus (SKILL.md authoring)
- Phase 7: Haiku (mechanical wiring + docs)

---

**Assessment by:** Sonnet
**Tier:** 3 (Full Runbook)
**Estimated cycles:** 40-45
**Parallelization:** Not recommended (tight integration, sequential validation needed)
