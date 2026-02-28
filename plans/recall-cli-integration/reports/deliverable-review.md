# Deliverable Review: recall-cli-integration

**Date:** 2026-02-28
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | Lines |
|------|------|-------|
| Code | `src/claudeutils/recall_cli/__init__.py` | +1 |
| Code | `src/claudeutils/recall_cli/artifact.py` | +36 |
| Code | `src/claudeutils/recall_cli/cli.py` | +201 |
| Code | `src/claudeutils/cli.py` | +2 |
| Test | `tests/test_recall_artifact.py` | +102 |
| Test | `tests/test_recall_cli_check.py` | +98 |
| Test | `tests/test_recall_cli_resolve.py` | +277 |
| Test | `tests/test_recall_cli_diff.py` | +307 |
| Test | `tests/test_recall_cli_integration.py` | +32 |
| Agentic prose | `agents/decisions/defense-in-depth.md` | +1/-1 |
| Agentic prose | `agent-core/agents/design-corrector.md` | +3/-3 |
| Agentic prose | `agent-core/agents/outline-corrector.md` | +1/-1 |
| Agentic prose | `agent-core/agents/runbook-outline-corrector.md` | +1/-1 |
| Agentic prose | `agent-core/skills/deliverable-review/SKILL.md` | +1/-1 |
| Agentic prose | `agent-core/skills/design/SKILL.md` | +2/-2 |
| Agentic prose | `agent-core/skills/design/references/research-protocol.md` | +1/-1 |
| Agentic prose | `agent-core/skills/inline/SKILL.md` | +2/-3 |
| Agentic prose | `agent-core/skills/orchestrate/SKILL.md` | +1/-1 |
| Agentic prose | `agent-core/skills/review-plan/SKILL.md` | +2/-2 |
| Agentic prose | `agent-core/skills/runbook/SKILL.md` | +1/-1 |
| Agentic prose | `agent-core/skills/runbook/references/tier3-planning-process.md` | +1/-1 |
| Submodule | `agent-core` (pointer) | Prototype deletion: `recall-check.sh`, `recall-resolve.sh`, `recall-diff.sh` |

**Totals:** 4 code (+240), 5 test (+816), 12 agentic prose (net -1), 1 submodule pointer. 1073 lines net.

**Design conformance:** All outline In-scope items delivered. `test_recall_cli_integration.py` unspecified but justified (FR-4 acceptance criteria coverage). Prototype deletion (Q-1) confirmed via submodule diff. All 12 reference updates are correct mechanical substitutions.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

### Naming

1. **`resolve_cmd` function name inconsistent with siblings** — `cli.py:88`: function named `resolve_cmd` while `check` (line 32) and `diff` (line 140) use bare names. Click 8.3 resolves this correctly (command name is `resolve`), but the `_cmd` suffix is inconsistent within the module. No functional impact.

### Conformance

2. **Argument mode processing deviates from outline** — Outline specifies "each arg through `parse_trigger`" for argument mode. Code uses `_strip_operator` instead (`cli.py:110`). Functionally equivalent because CLI args don't carry ` — ` annotations, but if an arg contained annotation syntax it would pass through to the resolver. Practical impact: nil (agents don't pass annotations as CLI args).

### Coverage

3. **Missing test: resolve with invalid artifact in artifact mode** — `_load_triggers_from_artifact` (`cli.py:74-76`) exits 1 with "Artifact has no Entry Keys entries" when artifact lacks the section or has no entries. This resolve-specific error path has no dedicated test. The behavior is correct (verified by code reading) and the underlying parse logic is tested via `test_recall_cli_check.py`, but the resolve invocation path is not exercised.

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| FR-1: `_recall check` structural validation | Covered | `cli.py:30-56`, 5 tests |
| FR-2: `_recall resolve` artifact + argument modes | Covered | `cli.py:86-135`, 7 tests |
| FR-3: `_recall diff` mtime-based file list | Covered | `cli.py:138-201`, 5 tests |
| FR-4: Hidden Click group registration | Covered | `cli.py:25`, `cli.py` main line 148, 3 integration tests |
| FR-5: LLM-native output | Covered | All output via `click.echo` to stdout, `_fail` pattern, no stderr |
| C-1: Reuse `when.resolver.resolve()` | Covered | `cli.py:11,115` |
| C-2: Project root via `CLAUDE_PROJECT_DIR` | Covered | `cli.py:37,98,147` |
| C-3: No hardcoded paths | Covered | Dynamic derivation from `project_root` |
| C-4: Terminal section parsing | Covered | `artifact.py:26-34`, parse to EOF |
| Q-1: Prototype deletion + reference updates | Covered | Submodule diff, 12 prose files updated |

No missing deliverables. No unjustified excess.

## Cross-Cutting Checks

- **Path consistency:** `agents/memory-index.md` in `cli.py:99` matches actual file location (verified on disk). Bug fix from Phase 5 (`index_path` was `.claude/memory-index.json`) confirmed correct.
- **API contract alignment:** `artifact.py` exports `parse_entry_keys_section` and `parse_trigger`; `cli.py` imports and uses both correctly. Resolver import `from claudeutils.when.resolver import ResolveError, resolve` matches existing API.
- **Naming convention:** `recall_cmd` group name follows `when_cmd` pattern in main `cli.py`. Command names `check`, `resolve`, `diff` are consistent.
- **Allowed-tools update:** `runbook/SKILL.md` updated from `agent-core/bin/recall-diff.sh` to `claudeutils _recall diff:*` — correct pattern for Click CLI invocation.
- **Recall context:** Resolved `plans/recall-cli-integration/recall-artifact.md` — 7 decision entries. All applicable conventions verified: LLM-native output (cli.md), `_fail` consolidation (cli.md), CliRunner testing (testing.md), E2E with real git repos (testing.md), behavioral RED assertions (testing.md). No additional findings from recall.
- **Inline skill update:** `agent-core/skills/inline/SKILL.md` post-step verification changed from two separate commands to single compound command (`git status --porcelain && just lint`). Correct fix per learnings.md compound-command decision.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 3 |

28 tests pass. Precommit clean. All FR and constraint requirements covered with no gaps. Prior corrector review (4 minor, all fixed) confirmed. Three new minor findings: naming inconsistency, outline conformance deviation, test coverage gap — none affect correctness or behavior.
