# Cycle 1.2

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

## Cycle 1.2: Design.md embedding in task agent

**RED Phase:**

**Test:** `test_task_agent_embeds_design_document`
**File:** `tests/test_prepare_runbook_agents.py`
**Prerequisite:** Read `agent-core/bin/prepare-runbook.py` lines 858-875 (current agent generation) — understand how `plan_context` is currently used (only Common Context, no design embedding)

**Assertions:**
- Task agent body contains `# Plan Context` section
- Task agent body contains `## Design` subsection under Plan Context
- The `## Design` subsection contains the full text of `plans/<plan>/design.md`
- When design.md doesn't exist: agent still generated; Design section contains "No design document found"

**Expected failure:** AssertionError — current code only embeds Common Context from runbook, not design.md

**Why it fails:** `generate_phase_agent` (now `generate_task_agent` after Cycle 1.1) passes `plan_context` which is Common Context only — no design file reading

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py::test_task_agent_embeds_design_document -v`

**GREEN Phase:**

**Implementation:** Read design.md and inject into agent body

**Behavior:**
- Derive design path from runbook path: `plans/<plan>/design.md`
- Read design file content (full text)
- Embed under `# Plan Context / ## Design` in agent body
- Fallback: if file doesn't exist, include empty section with "No design document found" note

**Approach:** Add design reading to `validate_and_create` before agent generation call. Pass design content to the task agent generator function.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add design.md reading logic in `validate_and_create`
  Location hint: before agent generation call

- File: `agent-core/bin/prepare-runbook.py`
  Action: Modify task agent generator to accept and embed design content
  Location hint: in the new `generate_task_agent` function

**Verify GREEN:** `just check && just test`

---
