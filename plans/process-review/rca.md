# Process RCA: Why Deliveries Are Expensive, Incomplete, Buggy, Sloppy, Overdone

**Date:** 2026-02-13
**Scope:** Agentic execution process (design → plan → execute → vet → deliver), not deliverable content
**Plans examined:** claude-tools-rewrite, claude-tools-recovery, statusline-parity, worktree-skill, memory-index-recall
**Method:** Retrospective artifact analysis from git history, cross-plan pattern extraction

## Executive Summary

Five development plans share a common failure pattern: the planning pipeline produces structural tests that verify artifact presence rather than behavioral correctness. Executing agents write minimal stubs to pass these tests. Vet agents confirm structural quality ("clean code, tests pass, types check") without verifying functional behavior. The result is well-structured, well-tested code that doesn't work.

The root cause is in the planning skill, not execution or review. The plan-tdd skill (Jan 20 version) provided presence-check examples as its model for RED phase assertions, and the downstream pipeline faithfully amplified this signal.

## Evidence

### claude-tools-rewrite (Jan 30)

37 TDD cycles completed. All tests pass. Vet review: "Overall Assessment: Ready" with zero critical/major issues.

**Actual state at delivery:**
- `account status`: Hardcoded state, doesn't read `~/.claude/` files
- Providers: Return empty strings for credentials (`"OPENROUTER_API_KEY": ""`)
- Statusline CLI: Validates JSON and prints "OK", doesn't format or display

**Test quality (from `runbook-analysis.md`):**
- `assert result.exit_code == 0` — command exists, doesn't crash
- `assert "OPENROUTER_API_KEY" in env_vars` — key exists, value empty
- No test checks actual file reading, keychain access, or output content

**Vet review highlights:**
- "Comprehensive test coverage (29 test files, 100% module coverage)"
- "Tests follow AAA pattern (Arrange-Act-Assert)"
- "TDD discipline: Clear RED/GREEN progression visible in commits"
- All "minor" issues dismissed as "expected for TDD incremental implementation"

**Additional failure:** Orchestrator launched cycles 1.2-1.5 in parallel despite plan saying "sequential". System prompt parallelization directive (strong: "MUST", repeated 3x) overrode orchestrate skill sequential requirement (weak: "always sequential unless").

**Recovery cost:** claude-tools-recovery plan (20 cycles), then interactive debugging for keychain identifier error that no test or vet caught.

### memory-index-recall (Feb 8)

50 tests pass. "7 modules, 50 tests" declared complete.

**Deliverable review findings (this session):** 3 critical, 4 major, 8 minor.

**Critical gaps:**
- Baseline comparison (`--baseline-before`): CLI parameter accepted, silently ignored. Underscore-prefixed unused arg. No code splits sessions, computes baseline, or reports lift. This was the primary analytical metric.
- Temporal constraint: Not implemented. All Reads counted regardless of when they occur relative to topic.
- User-directed detection: Enum value exists, aggregation counters track it, report displays it — always zero because no code path produces it.

**Real-data failure (M-2):** Index entries use relative paths (`agents/decisions/testing.md`), tool call inputs use absolute paths (`/Users/.../agents/decisions/testing.md`). `Path.__eq__` comparison never matches. Tool produces zero recall on any real session data. Unit tests pass because they use consistent path formats.

**Integration test:** `test_recall_pipeline_end_to_end` asserts `len(tool_calls) == 4` when fixture has 3 tool calls. Hidden behind `@pytest.mark.e2e` marker — excluded from default `pytest` run that reports 50/50 green.

### worktree-skill (Feb 5-11)

42 TDD cycles + 27 fixes in followup plan. Deliverable review found 27 issues (3C/12M/12m).

**Critical findings:**
- `merge --abort` after committed merge does nothing (MERGE_HEAD consumed by commit)
- Wrong paths in SKILL.md launch commands (`../<repo>-<slug>` instead of `wt/<slug>`)
- Wrong directory convention in sandbox-exemptions.md

**Test quality:**
- `test_worktree_merge_verification.py`: 341 lines proving `merge-base --is-ancestor` works (git concept, not production code)
- Mode 5 refactor tests: 6 of 8 assert old content was removed (absence, not correctness)
- Git init boilerplate defined 5 times independently; submodule setup 3 times
- Merge debris cleanup: code exists, no test

### statusline-parity (Feb 5)

14 cycles building on tools-rewrite output. Vet review quality improved vs tools-rewrite — behavioral assertions ("tests assert emoji presence"), proper requirements validation, found a real bug (duplicate function call).

Gap: Built on broken foundation. Parity tests verify Python output matches shell reference, but the underlying data-gathering code (from tools-rewrite) was broken. Formatters work correctly; the data they format is wrong.

### reflect-rca-sequential-task-launch (Feb 8)

Single-incident RCA for Task tool parallelization. Well-structured but narrow. The tool-batching fix it proposed has been implemented. Folded into this broader analysis as one instance of the directive-conflict pattern.

## Root Cause Chain

### 1. Planning skill provided presence-check examples

**plan-tdd skill (Jan 20 version), Phase 3 RED generation logic:**

> Generate assertion based on behavior (e.g., "assert section exists", "assert output contains X")

These examples are presence checks, not behavioral verification. "assert section exists" and "assert output contains X" can be satisfied by stubs. The skill used the word "behavior" but demonstrated "existence."

### 2. Runbook RED phases inherited the pattern

Tools-rewrite runbook RED phases specify:
- "assert command returns exit code 0"
- "assert key exists in dict"
- "assert method exists on class"

Each is satisfiable by a stub that returns a default value or empty collection.

### 3. Executing agents wrote minimal code to pass structural tests

TDD discipline says "write minimal code to pass the test." With structural tests, minimal code is a stub. This is correct TDD behavior given the tests — the agents followed the process faithfully.

### 4. Vet confirmed structure, not function

Vet review checked:
- Do artifacts exist? (modules, tests, configs) ✓
- Do tests pass? ✓
- Does code follow conventions? (types, lint, patterns) ✓
- Are there architectural problems? ✗ (not checked)
- Does it actually work? ✗ (not checked)

The vet-requirement.md at the time had no behavioral verification mandate. The vet agent's "Ready" assessment was accurate for the criteria it was given.

### 5. No integration gate in the pipeline

The design → plan → execute → vet pipeline has no point where:
- Real data passes through the system (e2e)
- Design requirements are checked against implementation (conformance)
- Scaffolded-but-unimplemented features are detected

## Cross-Plan Pattern Table

| Pattern | tools-rewrite | memory-recall | worktree-skill |
|---------|--------------|---------------|----------------|
| **Structural tests** | `exit_code == 0`, key exists | Unit tests with consistent mocks | Tests verify git works, not production code |
| **Scaffolded-not-implemented** | 37/45 cycles, stubs pass | CLI params accepted but unused | Lock file retry spec'd not built |
| **Vet says "Ready"** | 0 critical, features broken | 50/50 pass, tool non-functional | 27 findings found post-delivery |
| **Integration never tested** | No integration cycles | Relative vs absolute path mismatch | `merge --abort` after commit is no-op |
| **Hidden failures** | 8 missing cycles unnoticed | Broken e2e behind marker | — |

## Gap Analysis: Current Skills vs Detected Issues

### Addressed

- **Assertion quality:** Current runbook skill has weak-vs-strong assertion table with concrete examples ("returns correct value" → weak; "returns string containing emoji" → strong)
- **Vacuity detection:** "if RED can pass with `assert callable(X)`, the cycle is vacuous"
- **Prose test descriptions:** "behavioral, not structural" annotation on RED template
- **Sequential enforcement:** Orchestrate skill now enforces sequential for TDD
- **Task parallelization:** tool-batching.md updated to cover Task tool

### Partially addressed

- **Vet behavioral depth:** vet-requirement.md has execution context fields (IN/OUT scope, changed files, requirements summary). This helps the vet avoid confabulating future-phase issues, but doesn't mandate behavioral verification of the current phase.

### Not addressed

- **Design conformance gate:** No check that all design requirements are implemented. Scaffolded parameters (accepted but unused CLI flags, defined but unreturned enum values) pass all current checks. A conformance check would compare design FR-* list against implementation evidence.
- **Integration mandate:** No required e2e cycle testing real data paths. Cross-module path mismatches (relative vs absolute), missing wiring (stubs returning empty values), and hidden test failures (markers excluding broken tests) all survive the current pipeline.
- **Completeness verification:** No check that runbook cycle count matches design specification. Tools-rewrite: design said 45 cycles, runbook had 37, nobody noticed the gap until post-delivery analysis.
- **Scaffolding detection:** Underscore-prefixed unused parameters, enum values that no code path produces, and CLI flags that silently do nothing are all indicators of scaffolded-but-unimplemented features. No automated or review-time check for these patterns.

## Recommendations

Ranked by expected impact on the failure chain:

1. **Add conformance checkpoint to runbook skill** — After execution, verify each design FR-* has implementation evidence (not just test existence). This catches the scaffolded-but-unimplemented pattern.

2. **Add e2e integration cycle requirement to runbook skill** — Final phase of every TDD runbook must include at least one cycle testing real data flow through the full pipeline. This catches cross-module mismatches (path formats, empty stubs, broken wiring).

3. **Add completeness check to runbook outline review** — Compare design requirement count against runbook cycle coverage. Flag design requirements not mapped to any cycle.

4. **Add scaffolding detection to vet criteria** — Check for: unused function parameters (underscore prefix), enum values with zero production code paths, CLI options that are accepted but ignored. These are mechanical checks (grep-based), not judgment calls.

5. **Strengthen vet behavioral mandate** — vet-requirement.md should require "verify at least one behavioral assertion per module" in addition to current structural checks. This is harder to enforce mechanically but addresses the core "Ready but broken" pattern.

## Appendix: Source Artifacts

| Artifact | Location |
|----------|----------|
| tools-rewrite runbook analysis | `git show 80d5c97:plans/claude-tools-rewrite/runbook-analysis.md` |
| tools-rewrite vet review | `git show 80d5c97:plans/claude-tools-rewrite/reports/vet-review-2026-01-30.md` |
| tools-rewrite orchestration failure | `git show 80d5c97:plans/claude-tools-rewrite/orchestration-failure-analysis.md` |
| worktree-skill deliverable review | `git show 4dbcd52:plans/worktree-skill/reports/deliverable-review.md` |
| memory-recall deliverable review | `plans/memory-index-recall/reports/deliverable-review-report.md` |
| sequential-task-launch RCA | `git show 950e63e:plans/reflect-rca-sequential-task-launch/rca.md` |
| plan-tdd skill at execution time | `git -C agent-core show c525a1d:skills/plan-tdd/skill.md` |
| Current runbook skill | `agent-core/skills/runbook/SKILL.md` |
