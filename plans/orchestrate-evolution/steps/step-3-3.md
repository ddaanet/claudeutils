# Cycle 3.3

**Plan**: `plans/orchestrate-evolution/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Phase Context

**Scope:** Extend prepare-runbook.py for ping-pong TDD: 4 agent types, step file splitting, orchestrator plan TDD markers, verify-red.sh.

**Files:** `agent-core/bin/prepare-runbook.py`, `agent-core/skills/orchestrate/scripts/verify-red.sh` (create), `tests/test_prepare_runbook_tdd_agents.py` (create), `tests/test_verify_red.py` (create)

**Depends on:** Phase 1 (agent caching model — `generate_task_agent` function, `read_baseline_agent`), Phase 2 (orchestrator plan format — pipe-delimited step list, `generate_default_orchestrator`)

**Key constraints:**
- TDD agents extend Phase 1's per-role model: 4 roles instead of 1 task + 1 corrector
- Agent naming: `<plan>-tester.md`, `<plan>-implementer.md`, `<plan>-test-corrector.md`, `<plan>-impl-corrector.md`
- Baseline selection: test-driver.md for tester/implementer, corrector.md for test-corrector/impl-corrector
- All 4 agents embed same Plan Context (design + outline) as task agent from Phase 1
- Generated only for TDD-typed runbooks (pure TDD or TDD phases in mixed)
- Step file splitting: each TDD cycle → `step-N-test.md` (RED) + `step-N-impl.md` (GREEN)
- Orchestrator plan TDD markers: TEST/IMPLEMENT role on step entries
- Tests in NEW file `tests/test_prepare_runbook_tdd_agents.py` — NOT in `test_prepare_runbook_agents.py` (354 lines, near 400-line threshold)
- verify-red.sh: deterministic script (non-cognitive → script, per recall "When Choosing Script vs Agent Judgment")
- Shell script testing: real git repos in tmp_path (per recall "When Preferring E2E Over Mocked Subprocess")

---

---

## Cycle 3.3: Orchestrator plan TDD role markers

**RED Phase:**

**Test:** `test_orchestrator_plan_tdd_role_markers`
**File:** `tests/test_prepare_runbook_tdd_agents.py`
**Prerequisite:** Read `agent-core/bin/prepare-runbook.py` lines 1065-1196 (`generate_default_orchestrator`) — understand how items list is built and how step entries are formatted. Understand the pipe-delimited format from Phase 2 Cycle 2.1.

**Assertions:**
- For a TDD runbook: orchestrator plan step entries include role marker
- Test step entries: `- step-1-1-test.md | Phase 1 | sonnet | 25 | TEST`
- Impl step entries: `- step-1-1-impl.md | Phase 1 | sonnet | 25 | IMPLEMENT`
- TEST and IMPLEMENT markers alternate within each cycle (test before impl)
- For a general runbook: step entries have NO role marker (existing format preserved)
- Orchestrator plan contains a phase-agent mapping table or header that associates TEST steps with the tester agent and IMPLEMENT steps with the implementer agent (e.g., Phase-Agent Mapping section or `**Agent:**` fields per step entry)

**Expected failure:** AssertionError — current orchestrator plan generates single entry per cycle with no role marker

**Why it fails:** `generate_default_orchestrator` builds items from cycles as single entries; no TEST/IMPLEMENT distinction exists

**Verify RED:** `pytest tests/test_prepare_runbook_tdd_agents.py::test_orchestrator_plan_tdd_role_markers -v`

**GREEN Phase:**

**Implementation:** Add TDD role markers to orchestrator plan step entries

**Behavior:**
- When TDD cycles detected: split each cycle into two items in the orchestrator plan
- Test item: `step-N-M-test.md | Phase N | model | max_turns | TEST`
- Impl item: `step-N-M-impl.md | Phase N | model | max_turns | IMPLEMENT`
- TEST steps dispatch to tester agent; IMPLEMENT steps dispatch to implementer agent
- General steps unchanged (no role marker)
- Agent mapping in plan header: include tester/implementer agent names for TDD dispatch

**Approach:** Modify the items list construction in `generate_default_orchestrator`. When cycle items are added, expand each into two items (test + impl) with role markers. Add role field to the item tuple. Update the step entry formatting to include role when present.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Expand TDD cycle items into test/impl pairs with role markers in `generate_default_orchestrator`
  Location hint: lines 1109-1120 (cycle items construction)

- File: `agent-core/bin/prepare-runbook.py`
  Action: Include role marker in step entry formatting
  Location hint: lines 1159-1186 (step entry output loop)

**Verify GREEN:** `just check && just test`

---
