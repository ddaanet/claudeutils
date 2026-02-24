# Cycle 3.1

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

## Cycle 3.1: TDD agent type generation (4 agents)

**RED Phase:**

**Test:** `test_tdd_agents_generated_for_tdd_runbook` and `test_no_tdd_agents_for_general_runbook`
**File:** `tests/test_prepare_runbook_tdd_agents.py` (create)
**Prerequisite:** Read `agent-core/bin/prepare-runbook.py` lines 821-876 (`read_baseline_agent`, `generate_agent_frontmatter`, `generate_phase_agent`) — understand current baseline selection and agent composition. Read `agent-core/agents/test-driver.md` first 5 lines and `agent-core/agents/corrector.md` first 5 lines — understand frontmatter structure for baseline matching.

**Assertions (TDD runbook):**
- `validate_and_create` with a pure-TDD runbook (all phases `type: tdd`) produces exactly 4 agent files in agents directory
- Agent filenames are `{name}-tester.md`, `{name}-implementer.md`, `{name}-test-corrector.md`, `{name}-impl-corrector.md`
- Tester agent body contains test-driver.md baseline content (match a distinctive string from test-driver.md body)
- Implementer agent body contains test-driver.md baseline content
- Test-corrector agent body contains corrector.md baseline content
- Impl-corrector agent body contains corrector.md baseline content
- All 4 agents contain `# Plan Context` section with `## Design` subsection
- Tester agent contains "test quality" directive (role-specific rule embedding)
- Implementer agent contains "implementation" or "coding" directive

**Assertions (general runbook):**
- `validate_and_create` with a general runbook produces NO tester/implementer/test-corrector/impl-corrector files
- Only task agent and (if multi-phase) corrector agent generated (Phase 1 behavior preserved)

**Expected failure:** AssertionError — current code generates `crew-{name}` per-phase agents, no TDD-specific agent types exist

**Why it fails:** `validate_and_create` only calls `generate_phase_agent` in a per-phase loop; no TDD agent generation path exists

**Verify RED:** `pytest tests/test_prepare_runbook_tdd_agents.py -v`

**GREEN Phase:**

**Implementation:** Add TDD agent generation path to `validate_and_create` and supporting functions

**Behavior:**
- Detect TDD presence: any phase with `type: tdd` in `phase_types` dict
- When TDD detected: generate 4 additional agents using role-specific baselines and footers
- Tester + implementer use test-driver.md baseline; test-corrector + impl-corrector use corrector.md baseline
- Each agent gets same Plan Context (design + outline) as Phase 1's task agent
- Role-specific rule sections appended: tester gets test quality rules, implementer gets coding rules, correctors get review-specific rules
- Skip TDD agent generation entirely for pure-general runbooks

**Approach:** Add a `generate_tdd_agents` function called from `validate_and_create` after the existing task agent generation. This function checks `phase_types` for any TDD phases, then generates 4 agents using `read_baseline_agent` with appropriate type parameter and role-specific footers. Reuse Plan Context construction from Phase 1's task agent path.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add `generate_tdd_agents` function producing 4 role-specific agents
  Location hint: near `generate_phase_agent` (line 858)

- File: `agent-core/bin/prepare-runbook.py`
  Action: Call `generate_tdd_agents` from `validate_and_create` when TDD phases detected
  Location hint: after the per-phase agent generation loop (around line 1376)

**Verify GREEN:** `just check && just test`

---
