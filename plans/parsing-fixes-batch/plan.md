# Parsing Fixes Batch — Tier 2 Plan

**Tier:** 2 (Lightweight Delegation)
**Model:** sonnet
**Absorbs:** `runbook-generation-fixes` plan scope

## Scope

| # | Bug | File | Fix Direction |
|---|-----|------|---------------|
| 1 | model-tags false positive: bash scripts flagged | `validate-runbook.py:25-28` | Extension check in `_is_artifact_path()` |
| 2 | lifecycle false positive: pre-existing files | `validate-runbook.py:116-171` | Git-aware or parameter-based pre-existing file detection |
| 3 | Model propagation (C1) | `prepare-runbook.py` | Verify — may be pre-fixed |
| 4 | Phase numbering (C2) | `prepare-runbook.py` | Verify — may be pre-fixed |
| 5 | Phase context extraction (C3) | `prepare-runbook.py` | Verify — may be pre-fixed |
| 6 | Dead code: `strip_fenced_blocks` discarded return | `prepare-runbook.py:450` | Remove dead line |
| 7 | Dead code: section header discarded | `memory_index_checks.py:44` | Remove dead expression |

**Excluded:** Markdown xfail (multi-line inline code spans — separate task, blocks markdown migration)

## Cycle Plan

### Cycle 1: validate-runbook model-tags extension filter

**RED:** Test that `_is_artifact_path("agent-core/skills/commit/format-message.sh")` returns `True` for artifact check, but `check_model_tags()` does NOT flag it as a violation when Execution Model is sonnet. Test that `.md` files under artifact paths ARE still flagged.

**GREEN:** Add file extension filter — only flag `.md` files (the actual LLM-consumed artifacts). Non-markdown files under artifact paths are scripts/configs, not architectural prose.

**Files:** `agent-core/bin/validate-runbook.py`, `tests/test_validate_runbook.py`

### Cycle 2: validate-runbook lifecycle pre-existing files

**RED:** Test that `check_lifecycle()` accepts a `known_files` parameter (set of paths known to pre-exist). A file in `known_files` with modify-first should NOT be flagged. Files NOT in `known_files` with modify-first should still be flagged.

**GREEN:** Add `known_files: set[str] | None = None` parameter to `check_lifecycle()`. Skip violation for files in the set. Update `cmd_lifecycle()` to accept `--known-file` repeated option.

**Alternative approach:** Use `git ls-tree HEAD --name-only` at validation time to determine pre-existing files. This is more automatic but couples validation to git state. Prefer parameter approach — deterministic, testable, no git dependency in unit tests.

**Files:** `agent-core/bin/validate-runbook.py`, `tests/test_validate_runbook.py`

### Cycle 3: Verify C1 — model propagation

**RED:** Test multi-phase runbook where frontmatter says `model: haiku` and Phase 1 header says `model: sonnet`. Verify generated step file has `**Execution Model**: sonnet`, not `haiku`.

If RED passes → bug is already fixed. Document and skip GREEN.
If RED fails → fix model resolution chain in `validate_and_create()`.

**Files:** `agent-core/bin/prepare-runbook.py`, `tests/test_prepare_runbook_phase_context.py` (or new test file)

### Cycle 4: Verify C2 — phase numbering

**RED:** Test runbook with phases numbered 1, 3, 5 (gaps). Verify generated step files have correct phase numbers matching source, not sequential 1, 2, 3.

If RED passes → bug is already fixed. Document and skip GREEN.
If RED fails → fix phase number derivation.

**Files:** `agent-core/bin/prepare-runbook.py`, existing or new test file

### Cycle 5: Verify C3 — phase context completeness

**RED:** Test that completion validation section (appearing after last cycle in a phase) is captured in preamble. Current `extract_phase_preambles()` only captures text between phase header and first cycle/step — post-cycle content may be lost.

If RED passes → content is captured (or the concern is moot).
If RED fails → extend preamble extraction to include post-cycle phase content.

Note: This cycle tests a specific edge case (post-cycle content) beyond what existing tests cover (pre-cycle preamble only).

**Files:** `agent-core/bin/prepare-runbook.py`, `tests/test_prepare_runbook_phase_context.py`

### Cycle 6: Dead code cleanup

**Not TDD — mechanical removal.**

- Remove `content.splitlines(keepends=True)` at `prepare-runbook.py:450` (discarded return)
- Remove `stripped[3:] if stripped.startswith("## ") else None` at `memory_index_checks.py:44` (discarded expression)

Run `just dev` to verify no regressions.

**Files:** `agent-core/bin/prepare-runbook.py`, `src/claudeutils/validation/memory_index_checks.py`

## Checkpoint

After all cycles: `just dev` (fix + format + lint + test), review accumulated changes, commit.

## Execution Sequence

1. Cycles 1-2 (validate-runbook fixes) — definite bugs, straightforward
2. Cycles 3-5 (C1-C3 verification) — RED determines if GREEN needed
3. Cycle 6 (dead code) — mechanical
4. Checkpoint: `just dev`, review, commit
5. Update `runbook-generation-fixes` planstate to delivered (absorbed)
6. `/handoff --commit`
