# Step 2.2

**Plan**: `plans/error-handling/runbook.md`
**Execution Model**: opus
**Phase**: 2

---

## Step 2.2: Update orchestrate/SKILL.md with rollback protocol and timeout

**Objective**: Add error recovery section to orchestrate/SKILL.md covering rollback strategy (D-5), timeout handling (Q1), and dirty tree recovery protocol.
**Script Evaluation**: Prose (25-100 lines — new section added to 471-line file)
**Execution Model**: Opus (skill artifact)

**Prerequisite**: Read `agent-core/skills/orchestrate/SKILL.md` sections 3 (Execute Steps Sequentially) and 4 (Error Escalation) — understand current dirty-tree check and escalation flow before adding recovery protocol.

**Implementation**:
Add a new "### 4b. Error Recovery" section immediately after the existing "### 4. Error Escalation" section (before "### 5. Progress Tracking"):

1. **Rollback Protocol (D-5)**:
   - Trigger: When Sonnet diagnostic confirms step cannot be fixed (level 2 escalation path fails)
   - Action: Revert to last clean git commit before the failed step. Use `git log --oneline -5` to identify the checkpoint commit; `git reset --hard <checkpoint-sha>` to restore
   - Principle: No partial undo — reverting a commit IS restoring state (git's atomic snapshot model)
   - Assumption: All relevant state is git-managed. If non-git state is involved (external service calls, unreachable session.md edits), the simple revert model breaks — escalate to user rather than reverting
   - After rollback: Clean tree confirmed → step can be retried with corrected context or user revises the step

2. **Timeout Protocol (Q1)**:
   - Spinning failure mode (high activity, no convergence): Set `max_turns=150` on Task calls when invoking step agents
   - Calibration: 938 clean Task observations; p90=40 turns, p95=52, p99=73, max=129; threshold 150 provides ~99.9th percentile headroom
   - If step agent hits max_turns: orchestrator receives "max turns exceeded" result → treat as execution error → escalate to Sonnet diagnostic
   - Duration timeout (hanging failure mode, no activity): Deferred — requires Claude Code infrastructure support not currently available to project

3. **Dirty Tree Recovery**:
   - Trigger: `git status --porcelain` returns output after step completion (step left uncommitted changes — current behavior: STOP orchestration)
   - With rollback: After stopping, revert to last checkpoint commit → re-execute the failed step from clean state
   - The clean tree check (existing section 3.3) remains unchanged — STOP is correct. This section documents what happens AFTER the stop: rollback then retry

**Expected Outcome**: New "4b. Error Recovery" section in orchestrate/SKILL.md with rollback, timeout, and dirty tree recovery. max_turns ~150 documented with calibration rationale.

**Error Conditions**:
- If section 4 location unclear after reading, search for "Error Escalation" heading and insert after

**Validation**:
- `grep -n "Error Recovery\|4b" agent-core/skills/orchestrate/SKILL.md` returns match
- "max_turns" and "150" both present in new section
- "git reset" or "revert" (rollback mechanism) present
- Calibration data (938 observations, p99=73) referenced

---

*(Independent of Phase 2 — run in parallel after Phase 1 completes)*
