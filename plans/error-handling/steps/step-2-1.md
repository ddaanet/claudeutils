# Step 2.1

**Plan**: `plans/error-handling/runbook.md`
**Execution Model**: opus
**Phase**: 2

---

## Step 2.1: Create escalation-acceptance.md fragment

**Objective**: Create new fragment defining acceptance criteria for escalation resolution (D-3). Establishes the three required criteria that must ALL pass before an escalated error is considered "fixed."
**Script Evaluation**: Small (create new file, ~40 lines)
**Execution Model**: Opus (fragment artifact)

**Prerequisite**: Read `agent-core/fragments/error-classification.md` (post-Step-1.2 state) — understand all 5 error categories to write per-category resolution guidance.

**Implementation**:
Create `agent-core/fragments/escalation-acceptance.md` with:

1. Section: "Escalation Resolution Criteria (D-3)" — three required criteria (ALL must pass):
   - (a) `just precommit` passes — no lint, format, or test failures
   - (b) `git status --porcelain` returns empty — working tree clean
   - (c) Step output validates against the step's acceptance criteria (from step definition Validation section)
   None of the three is optional. Sonnet diagnostic resolves by applying fix + verifying all three pass before reporting success.

2. Section: "Per-Category Resolution Guidance" — what "fixed" means for each error type:
   - Prerequisite Failure: resource now exists at expected path (verify with Read/Glob/Bash before re-executing step)
   - Execution Error: command now exits 0 and precommit clean; if test failure, test now passes
   - Unexpected Result: output now matches step validation criteria (re-read step definition criteria, validate output against them)
   - Ambiguity Error: step definition updated with clarification; ambiguous language replaced with unambiguous instruction; escalated to orchestrator for plan update
   - Inter-agent misalignment: re-executed agent output now matches specification; if same agent with stronger constraints still misaligns, escalate to user

3. Short section: "Verification Sequence" — the order to verify:
   - Fix the root cause first (resource, code, plan update)
   - Run `just precommit` — all checks must pass
   - Run `git status --porcelain` — must be empty
   - Re-read step's Validation section — run each check manually
   - Only report success after all three pass

**Expected Outcome**: New file `agent-core/fragments/escalation-acceptance.md` exists with ~40 lines. Three-criteria structure present. All 5 error categories have resolution guidance.

**Error Conditions**:
- STOP if file already exists (unexpected state — report to user)

**Validation**:
- `test -f agent-core/fragments/escalation-acceptance.md` succeeds
- File contains "just precommit" reference
- File contains "git status --porcelain" reference
- All 5 category names present (Prerequisite Failure, Execution Error, Unexpected Result, Ambiguity Error, Inter-agent misalignment / INTER_AGENT_MISALIGNMENT)

---
