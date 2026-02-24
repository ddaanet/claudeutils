# Cycle 2.1

**Plan**: `plans/orchestrate-evolution/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Phase Context

**Scope:** New structured orchestrator plan format with metadata fields. verify-step.sh creation with E2E tests.

**Files:** `agent-core/bin/prepare-runbook.py`, `agent-core/skills/orchestrate/scripts/verify-step.sh` (create), `tests/test_prepare_runbook_orchestrator.py` (extend), `tests/test_verify_step.py` (create)

**Depends on:** Phase 1 (agent naming used in orchestrator plan header)

**Key constraints:**
- Orchestrator plan format: structured metadata, not prose instructions
- Step list: `- filename | Phase N | model | max_turns [| PHASE_BOUNDARY]`
- Header fields: `**Agent:**`, `**Corrector Agent:**`, `**Type:**`
- INLINE marker for inline phases
- Phase summaries with IN/OUT scope
- verify-step.sh: deterministic script (non-cognitive → script, per recall "When Choosing Script vs Agent Judgment")
- Shell script testing: real git repos in tmp_path (per recall "When Preferring E2E Over Mocked Subprocess")

---

---

## Cycle 2.1: Structured step list format

**RED Phase:**

**Test:** `test_orchestrator_plan_structured_format`
**File:** `tests/test_prepare_runbook_orchestrator.py`
**Prerequisite:** Read `agent-core/bin/prepare-runbook.py` lines 1065-1196 (current `generate_default_orchestrator`) — understand current prose format with H2 per step

**Assertions:**
- Orchestrator plan header contains `**Agent:** {name}-task`
- Orchestrator plan header contains `**Corrector Agent:** {name}-corrector` (for multi-phase) or `**Corrector Agent:** none` (for single-phase)
- Orchestrator plan header contains `**Type:** general` (or `tdd` for TDD runbooks)
- Plan contains `## Steps` section
- Each step entry is a pipe-delimited line: `- step-N-M.md | Phase N | model | max_turns`
- No H2 headings per step (old format eliminated)

**Expected failure:** AssertionError — current code generates prose format with H2 per step and `Execute steps sequentially using...` header

**Why it fails:** `generate_default_orchestrator` outputs H2-per-step format with prose instructions

**Verify RED:** `pytest tests/test_prepare_runbook_orchestrator.py::test_orchestrator_plan_structured_format -v`

**GREEN Phase:**

**Implementation:** Rewrite `generate_default_orchestrator` to produce structured format

**Behavior:**
- Output header with Agent, Corrector Agent, and Type fields
- Output `## Steps` section with pipe-delimited entries per step
- Each entry: `- {filename} | Phase {N} | {model} | {max_turns}`
- Preserve phase ordering and step sequencing
- Use agent name from Phase 1 (`{name}-task`, not `crew-{name}`)

**Approach:** Replace the body of `generate_default_orchestrator`. Keep the same function signature for backward compatibility. Build step entries from cycles/steps/inline_phases the same way but format as pipe-delimited lines instead of H2 sections.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Rewrite body of `generate_default_orchestrator`
  Location hint: line 1065

**Verify GREEN:** `just check && just test`

---
