## When Writing Red Phase Assertions

**Source:** `agents/decisions/testing.md`
**Relevance:** All cycles are TDD — RED tests must verify behavior, not structure.

RED phase tests must verify behavior with mocking/fixtures. Tests checking only structure (exit_code == 0, key existence) let trivial implementations pass. Assert on output content, not just success/failure.

## When Detecting Vacuous Assertions from Skipped RED

**Source:** `agents/decisions/testing.md`
**Relevance:** C1-C3 cycles may have RED pass unexpectedly (bug already fixed).

When RED passes unexpectedly, verify assertions would catch the defect class. Check if key assertions distinguish "correct output" from "empty/default output."

## When Testing CLI Tools

**Source:** `agents/decisions/testing.md`
**Relevance:** validate-runbook.py tests may invoke CLI.

Use Click test harness (`click.testing.CliRunner`) for Click CLIs. But validate-runbook.py uses argparse — test via function calls, not subprocess.

## When Splitting Validation into Mechanical and Semantic

**Source:** `agents/decisions/defense-in-depth.md`
**Relevance:** validate-runbook.py fixes are deterministic checks (file extension, git existence).

Script handles deterministic checks (blocking, zero false positives). Different enforcement layers for different failure modes.

## When Test Setup Steps Fail

**Source:** `agents/decisions/testing.md`
**Relevance:** Test setup using subprocess.run(check=True) swallows stderr.

Test setup should produce self-diagnosing failures. Use check=False + explicit assertion with stderr.

## prepare-runbook-fixes Diagnostic

**Source:** `plans/prepare-runbook-fixes/diagnostic.md`
**Relevance:** Bug 1 (trailing preamble) and Bug 2 (runbook.md path) already delivered — provides context for C1-C3 investigation.

Bug 1: extract_cycles() terminated only on H2, not H3 phase headers. Fix: add H3 as termination condition.
Bug 2: generate_cycle_file() used canonical runbook_path, not actual source file. Fix: _source_for_phase() resolves to actual phase file.

## runbook-generation-fixes Brief

**Source:** `plans/runbook-generation-fixes/brief.md`
**Relevance:** Diagnosed C1-C3 bugs during hook-batch execution. Manual patches applied, source fix status uncertain.

C1: Model propagation — step files get wrong model from agent's base, ignoring phase-level model.
C2: Phase numbering — off-by-one from sequential PHASE_BOUNDARY counting vs actual phase numbers.
C3: Phase context — prerequisites, constraints, completion validation not propagated to step files.
