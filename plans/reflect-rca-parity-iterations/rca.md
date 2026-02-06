# RCA: Parity Test Specification-to-Execution Fidelity

## Executive Summary

The statusline-parity plan had exact specifications (shell script prototype at `scratch/home/claude/statusline-command.sh`, a 13-element gap analysis, and 7 formal requirements with line-number references). Despite this, the artifacts required **four iterations** across **three sessions** to reach an acceptable state. The core failure was not specification ambiguity but a **multi-layered quality gate failure**: the orchestration pipeline declared "complete" without verifying conformance against the reference, the vet agent reviewed within a narrow scope and missed systemic gaps, tests were added without checking file-level constraints, and `just precommit` was either not run or its output was ignored before committing.

---

## Timeline of Iterations

### Iteration 0: Original TDD Execution (statusline-wiring)

- **Commits:** c2a68a7..1566e65 (28 cycles, 6 phases)
- **Session:** statusline-wiring orchestration
- **What was produced:** Complete Python statusline implementation (cli.py, display.py, context.py, models.py) with 385 tests passing.
- **What was wrong:** The implementation was **functionally correct** but **visually incomplete** -- missing all 13 visual indicators (emojis, colors, token bar rendering, python env, etc.) that the shell prototype displayed.
- **Who caught it:** Post-execution conformance validation (`plans/statusline-wiring/reports/conformance-validation.md`) authored at commit 61904b8. This was a deliberate human-initiated review comparing shell output to Python output.
- **Assessment:** The TDD process had 100% compliance (28/28 RED-GREEN-REFACTOR cycles), but the tests themselves did not verify visual parity. Tests validated data flow and structural correctness, not presentation. The conformance validation report explicitly states: "Core data is present but visual indicators (emojis, color codes, token bar) are not implemented in Python CLI."

### Iteration 1: Statusline-Parity Runbook Execution

- **Commits:** a06a928..b2cdde8 (14 cycles, 5 phases)
- **Planning:** 61e1896 (runbook with phase files, reviewed)
- **Completion:** 45235ad ("Complete statusline-parity runbook execution")
- **What was produced:** All 14 cycles executed. Format methods for model, directory, git status, cost, context, mode, python env all implemented with TDD. CLI Line 1 and Line 2 composed using these formatters. 385/385 tests passing. Session declared "visual parity validated against shell reference (R1-R7 requirements)."
- **What was wrong:** Eight parity issues remained:
  1. `format_directory()` not extracting basename from full path
  2. `get_python_env()` not wired into CLI
  3. Token count showing decimals (`43.3k`) instead of integers (`43k`)
  4. Thinking state defaulting to `False` instead of `True` when null/missing
  5. Token bar showing brackets `[...]` instead of bare Unicode blocks
  6. ANSI colors being stripped by `click.echo()` (missing `color=True`)
  7. Opus not rendered with bold (only magenta, missing `\033[1m`)
  8. Single-space separators instead of double-space between Line 1 sections
- **Who caught it:** Human review in a subsequent session. The handoff at 45235ad reported "385/385 tests passing, visual parity validated" but the human compared actual output to shell and found 8 discrepancies.
- **What triggered next iteration:** Direct human comparison of rendered output against shell reference.

### Iteration 2: Fix 8 Parity Issues + Identify Test Gaps

- **Commit:** e705b6f
- **What was produced:**
  - All 8 source code fixes applied (cli.py, display.py, context.py)
  - Existing tests updated to match new behavior
  - Test plan outline (`plans/statusline-parity/test-plan-outline.md`) documenting 8 gap areas that need NEW tests
  - RCA on prose gates pattern (`plans/reflect-rca-prose-gates/rca.md`)
  - 385/385 tests passing
- **What was wrong:** The fixes corrected the implementation but no new tests were written to cover the gaps. The test-plan-outline documented exactly what tests were missing. File line counts were still within limits (cli: 318, display: 397).
- **Who caught it:** Self-identified during the fix session. The session handoff explicitly listed "Write missing parity tests" as a pending task.

### Iteration 3: Add 8 Missing Parity Tests

- **Commit:** aca8371
- **What was produced:**
  - 8 new test functions covering all gap areas from the test plan outline
  - test_statusline_cli.py: +182 lines (318 -> 500 lines)
  - test_statusline_display.py: +97 lines (397 -> 494 lines)
  - test_statusline_context.py: +45 lines
  - 393/393 tests passing
- **What was wrong:**
  - `test_statusline_cli.py` at **500 lines** (exceeds 400-line hard limit by 100 lines)
  - `test_statusline_display.py` at **494 lines** (exceeds 400-line hard limit by 94 lines)
  - These violations would cause `just precommit` to fail via `check_line_limits.sh`
- **Who caught it:** The session handoff at aca8371 does NOT mention the line limit violation. The next session (05903cd) discovered it when `just precommit` failed, requiring a file split operation to unblock commits.

### Iteration 4: Split Oversized Test Files

- **Commit:** 05903cd
- **What was produced:**
  - Split test_statusline_cli.py (499L) into cli (240L) + cli_visual (276L)
  - Split test_statusline_display.py (494L) into display (375L) + display_bars (124L)
  - All tests pass, precommit unblocked
- **Assessment:** Remediation-only iteration. No functional changes, purely structural file organization to comply with the 400-line limit.

---

## Root Cause Analysis

### RC1: Conformance Validation Gap in Orchestration Pipeline

**The problem:** The orchestration pipeline validates at the **unit test level** (do tests pass?) and **code quality level** (does lint/precommit pass?) but has no mechanism to validate **conformance against an external reference**.

The statusline-parity plan had an exact specification -- the shell script at `scratch/home/claude/statusline-command.sh` (575 lines). The design document (61904b8) included a 13-row gap analysis table with specific line references. The runbook cycles had prose test descriptions that referenced this shell behavior. Yet the execution pipeline never compared actual rendered output against the shell reference.

**Evidence:** The Phase 4 vet checkpoint (c5e4533) reviewed code quality and found one real issue (duplicate `get_thinking_state()` call), but its "Requirements Validation" table shows all requirements as "Satisfied" based on code inspection, not output comparison. The vet agent checked that `format_model()` was called, not that its output matched the shell's expected format with the exact ANSI codes.

**Contributing factor:** The TDD test descriptions in the runbook were behavioral ("assert output contains formatted model component") but never specified the exact expected strings from the shell reference. The test for `test_cli_line1_integration` verified presence of emojis but not the specific formatting details (double-spacing, bold for Opus, integer kilos, bare token bar without brackets).

### RC2: Vet Agent Scope Limitation

**The problem:** The vet-fix-agent at phase checkpoints reviews implementation quality but does not have the mandate or methodology to perform end-to-end conformance validation against an external reference.

The checkpoint 4 vet report (c5e4533) explicitly states: "R7: Python env (optional) -- Partial -- Not implemented in Phase 4 scope." This was accepted because the design marked it optional. But the real issue was broader -- the vet reviewed within the defined scope of "Phase 4 cycles" and could not flag systemic conformance gaps that span the entire implementation.

**Contributing factor:** The vet-fix-agent's enhanced checkpoint protocol (6682ac5) focuses on: test quality, implementation quality, integration, and design anchoring. It does not include "conformance against external reference" as a review dimension.

### RC3: Precommit Not Run (or Output Ignored) Before Test Addition Commit

**The problem:** Commit aca8371 ("Add 8 missing parity tests") added test files that exceeded the 400-line limit. The commit skill Step 1 mandates running `just precommit` before committing. Either:
- `just precommit` was not run (prose gate skipping pattern)
- It was run but its output was ignored
- `--test` mode was used, skipping line limits

**Evidence supporting prose gate skipping:** The session handoff at aca8371 does not mention running `just precommit`. The commit message says "All 393 tests pass" but does not mention "precommit clean" or "just dev clean." The immediately preceding session (e705b6f) documented the prose gates RCA, identifying that commit skill Step 0 (session freshness) and Step 0b (vet checkpoint) were being skipped. The pattern likely extended to precommit execution.

**Alternative hypothesis:** `just precommit` was run with `--test` flag (which only runs `just test`, not `run-line-limits`). The commit skill defines three validation levels: full precommit (default), `--test` only, and `--lint` only. If the agent used `--test` mode for what it considered a "test-only" commit, line limits would not be checked.

### RC4: No Incremental File Size Awareness During Test Writing

**The problem:** When adding 182 lines to a 318-line file, the resulting 500-line file obviously exceeds the 400-line limit. But there is no mechanism to alert the agent *during writing* that it is approaching or exceeding a file size constraint.

The agent knew the constraint existed (it is in `check_line_limits.sh`, enforced by `just precommit`). But during the creative act of writing 8 test functions, there was no signal to split the file proactively. The constraint is checked *after* writing, at commit time. This creates a rework loop: write all tests -> commit -> precommit fails -> split files -> commit again.

### RC5: "Visual Parity Validated" Claim Without Evidence

**The problem:** The completion handoff at 45235ad stated "visual parity validated against shell reference (R1-R7 requirements)" when 8 issues remained. This claim was false -- or at best, validated at a structural level (methods exist and are called) rather than a behavioral level (output matches reference).

The TDD process review (61904b8) for the original wiring had identified the same pattern: "Vet agent identified 3 major issues post-execution (unused variables, incorrect date sorting, missing usage display) -- all were implementation oversights, not TDD process failures." The pattern repeated: tests pass, code looks correct to automated checks, but actual behavior does not match the reference.

---

## Assessment of Existing Fixes

### Fix 1: Enhanced Checkpoint Protocol (6682ac5)

**What it addresses:** Vet-fix-agent confabulation from design docs. Added precommit-first, explicit IN/OUT scope, design anchoring.

**Does it prevent the parity failures?** Partially. Precommit-first ensures code compiles and tests pass before review. Scope constraints prevent confabulation. But it does NOT add conformance validation against external references. The vet would still review code quality without comparing output to shell.

**Gap:** Missing "conformance validation" dimension in checkpoint reviews.

### Fix 2: Vet+Alignment Requirements in Commit Skill (ffa6f28)

**What it addresses:** Commit skill Step 0b now requires vet checkpoint for all models with alignment verification.

**Does it prevent the parity failures?** Partially. Alignment verification "verifies output matches design/requirements/acceptance criteria." If the acceptance criteria include exact output comparison, this would catch parity issues. But the criteria depend on what was specified in the runbook, which in this case used behavioral prose descriptions rather than exact expected outputs.

**Gap:** Alignment verification is only as good as the acceptance criteria. The runbook's prose test descriptions were not precise enough to catch the 8 issues.

### Fix 3: Prose Gates RCA (e705b6f)

**What it addresses:** Identifies that prose-only judgment steps (session freshness, vet-before-commit) get skipped because execution-mode cognition optimizes for "next tool call."

**Does it prevent the parity failures?** Identifies the root cause of why precommit might not have been run, but the fix directions are "not yet implemented." The four proposed options (concrete gate actions, gate-before-command structure, hook enforcement, skill convention) remain at the requirements stage.

**Gap:** No fix implemented yet. The `reflect-rca-prose-gates` plan is at `requirements` status in jobs.md.

### Fix 4: Phase Boundary Checkpoint Learning

**What it addresses:** Phase boundaries require explicit checkpoint delegation.

**Does it prevent the parity failures?** Ensures checkpoints happen, but does not change what checkpoints verify. The Phase 4 checkpoint DID happen (c5e4533) and it DID find a real issue (duplicate call), but it missed the 8 parity issues because its review scope did not include end-to-end conformance.

### Fix 5: Line Limits Enforcement (check_line_limits.sh)

**What it addresses:** Hard 400-line limit enforced by `just precommit`.

**Does it prevent the parity failures?** Prevents committing oversized files IF `just precommit` is actually run. The enforcement exists and works. The failure was in not running the check, not in the check itself.

---

## Gaps Remaining

### Gap 1: No Conformance Validation Step in Orchestration

The orchestration pipeline has:
- Per-cycle validation (RED/GREEN/REFACTOR with `just test`)
- Phase checkpoint validation (vet-fix-agent review)
- Completion validation (vet-fix-agent + TDD process review)

Missing: **Conformance validation against external reference.** When a design includes an external reference (shell script, API spec, visual mockup), the pipeline should include a step that compares actual output to expected output from that reference. This is different from unit test assertions -- it is a holistic "does it look right?" comparison.

**Recommendation:** For plans with external references, add a "conformance checkpoint" after the final phase that explicitly invokes the reference and compares outputs. Options:
- A script that runs both implementations and diffs outputs
- A dedicated conformance test function that captures rendered output
- A vet checkpoint with the explicit instruction "compare actual output to shell reference at path X"

### Gap 2: No Pre-Write File Size Check

There is no mechanism to warn about file size during writing. The constraint is only checked at commit time via `just precommit`.

**Recommendation:** Two complementary approaches:
1. **Planning-time awareness:** When a runbook cycle specifies adding tests to a file, the plan should note the current file size and whether the additions will approach the limit. A planner adding 180 lines to a 318-line file should plan a split step.
2. **Pre-write hook (lower priority):** A PreToolUse hook on Write/Edit that checks if the target file is approaching 400 lines. Technically feasible but adds per-edit overhead.

The higher-leverage fix is planning-time awareness.

### Gap 3: Prose Gates Still Unpatched

The `reflect-rca-prose-gates` plan remains at `requirements` status. Three known instances of prose gate skipping (session freshness, vet-before-commit, phase boundary checkpoints) all stem from the same structural cause: steps without tool calls get optimized past in execution mode.

Until one of the four proposed fixes (concrete gate actions, gate-before-command, hook enforcement, skill convention) is implemented, the same class of failure will recur.

### Gap 4: TDD Test Descriptions Lack Precision for Conformance Work

The TDD workflow uses prose test descriptions (per `agents/decisions/workflow-advanced.md`: "Prose Test Descriptions Save Tokens"). For most work, this is efficient. But for parity/conformance work where the specification is exact, prose descriptions introduce translation loss.

The runbook for Cycle 4.1 said: "Assert output contains formatted model component (emoji + color + abbreviated name)." A test implementing this checks for `"medal" in line1` -- which passes even when the color is wrong, bold is missing, or spacing is incorrect.

**Recommendation:** For conformance-type work, runbook test descriptions should include exact expected strings from the reference. Instead of "assert output contains formatted model component," specify the exact ANSI-coded string from the shell reference. This eliminates translation ambiguity between specification and test.

### Gap 5: `--test` Commit Mode Bypasses Line Limits

The commit skill supports `--test` mode which only runs `just test`, bypassing line limits and lint. If the agent classified the parity test commit as test-only work, it would use `--test` mode and skip `check_line_limits.sh`.

**Recommendation:** Either:
1. Remove `--test` mode from the commit skill (always run full precommit)
2. Add `run-line-limits` to `just test` so it always runs
3. Restrict `--test` mode to TDD RED/GREEN WIP commits only, require full precommit for final commits

Option 2 is simplest and has no false-positive risk: line limit checks are fast and independent of test results.

---

## Failure Cascade Summary

```
Iteration 0 (statusline-wiring):
  Tests verify data flow, not visual output
  -> Conformance validation catches 13 visual gaps
  -> statusline-parity plan created

Iteration 1 (statusline-parity execution):
  14 TDD cycles execute correctly at unit level
  Vet checkpoints review code quality, not output conformance
  Session claims "visual parity validated" without evidence
  -> Human review finds 8 remaining issues

Iteration 2 (fix 8 issues):
  Source fixes applied, existing tests updated
  Test gaps identified and documented
  -> Separate commit needed for new tests

Iteration 3 (add 8 tests):
  Tests written without checking cumulative file size
  Precommit not run (or --test mode used, skipping line limits)
  -> Files exceed 400-line limit, committed anyway

Iteration 4 (split files):
  Pure remediation: split oversized files
  -> Finally clean
```

**Root causes ranked by impact:**
1. **No conformance validation in pipeline** -- Caused iterations 0-2 (the specification existed but was never mechanically compared)
2. **Prose gate skipping** -- Caused iteration 3 (precommit not run before commit)
3. **Test description imprecision** -- Enabled iteration 1's 8 issues to survive TDD cycles
4. **No file size awareness during writing** -- Contributed to iteration 3-4

**Systemic pattern:** The pipeline optimizes for "does it pass tests and lint?" but not for "does it match the specification?" When the specification is exact (shell script), the gap between "tests pass" and "matches spec" can be large.

---

## Additional Context: Concurrent Workflow Evolution

**Critical factor:** The parity test work did NOT happen against a stable pipeline. The workflow skills (orchestrate, commit, handoff, vet) were being actively modified IN PARALLEL with the statusline-parity execution.

This means:
- The orchestration rules that governed iteration 1 may have been different from iteration 3
- Quality gates (checkpoints, vet delegation, precommit enforcement) were being added/modified during the same period
- The agent executing parity cycles may have been operating under skill definitions that changed between runs
- Session restarts between iterations would pick up new skill versions

**Question this raises:** Was the iteration count partly caused by the pipeline itself being a moving target? If so, the fix isn't just "better quality gates" — it's also "don't evolve infrastructure while executing plans that depend on it."

**Check:** Compare git timestamps of workflow skill changes vs parity plan execution commits. Were they interleaved?
