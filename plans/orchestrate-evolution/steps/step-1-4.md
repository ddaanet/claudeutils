# Cycle 1.4

**Plan**: `plans/orchestrate-evolution/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

**Scope:** Restructure prepare-runbook.py agent generation from per-phase to per-role model. Single task agent with embedded design+outline replaces N per-phase agents.

**Files:** `agent-core/bin/prepare-runbook.py`, `tests/test_prepare_runbook_agents.py` (extend)

**File growth constraint:** `tests/test_prepare_runbook_agents.py` is currently 354 lines. Phase 1 adds 4 test functions (~20-30 lines each), projecting to 434-474 lines — above the 400-line enforcement threshold. Before starting Cycle 1.3, check line count: if `tests/test_prepare_runbook_agents.py` exceeds 380 lines, extract the new Cycle 1.1/1.2 test classes to `tests/test_prepare_runbook_agent_caching.py` before continuing.

**Key constraints:**
- Clean break (Q-4): no backward compatibility with `crew-` naming
- Agent naming: `<plan>-task.md`, `<plan>-corrector.md`
- Baseline selection: `artisan.md` for general/mixed, `test-driver.md` for pure TDD
- Content source priority for design: `plans/<plan>/design.md` → empty section fallback
- Content source priority for outline: runbook `## Outline` section → `plans/<plan>/outline.md` → empty fallback
- Scope enforcement + clean tree footers at bottom of every agent definition

---

---

## Cycle 1.4: Corrector agent generation for multi-phase plans

**RED Phase:**

**Test:** `test_corrector_agent_generated_for_multi_phase`
**File:** `tests/test_prepare_runbook_agents.py`
**Prerequisite:** Read `agent-core/agents/corrector.md` first 10 lines (frontmatter structure) — understand corrector baseline format

**Assertions:**
- For a runbook with 2+ non-inline phases: `{name}-corrector.md` agent file created in agents directory
- Corrector agent uses corrector.md baseline body (not artisan.md or test-driver.md)
- Corrector agent frontmatter has `model: sonnet` (always sonnet, regardless of task agent model)
- Corrector agent contains same `# Plan Context` with Design + Outline as task agent
- Corrector agent has corrector-specific scope footer: "Review ONLY the phase checkpoint described in your prompt"
- For a single-phase runbook: no corrector agent file created

**Expected failure:** AssertionError — no corrector agent generation exists

**Why it fails:** Current code only generates task agents, never corrector agents

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py::test_corrector_agent_generated_for_multi_phase -v`

**GREEN Phase:**

**Implementation:** Add corrector agent generation path

**Behavior:**
- Detect multi-phase: count non-inline phases > 1
- Read corrector.md baseline (new path in `read_baseline_agent` or separate function)
- Generate `{name}-corrector.md` with corrector baseline + Plan Context (design + outline) + corrector scope footer
- Always model: sonnet for corrector
- Skip generation for single non-inline phase plans

**Approach:** Add corrector generation after task agent generation in `validate_and_create`. Create a `generate_corrector_agent` function mirroring `generate_task_agent` but with corrector baseline and scope footer.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add `generate_corrector_agent` function
  Location hint: near `generate_task_agent`

- File: `agent-core/bin/prepare-runbook.py`
  Action: Add corrector agent generation in `validate_and_create` (conditional on multi-phase)
  Location hint: after task agent generation

- File: `agent-core/bin/prepare-runbook.py`
  Action: Extend `read_baseline_agent` to support "corrector" type or add separate reader
  Location hint: around line 821

**Verify GREEN:** `just check && just test`


### Phase 2: Orchestrator plan and verification (type: tdd, model: sonnet)

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
