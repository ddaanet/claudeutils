# Cycle 1.3

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

## Cycle 1.3: Outline embedding in task agent

**RED Phase:**

**Test:** `test_task_agent_embeds_outline`
**File:** `tests/test_prepare_runbook_agents.py`
**Prerequisite:** Read `agent-core/bin/prepare-runbook.py` `extract_sections` function (line 459) — understand how `## Outline` section would be extracted from runbook content

**Assertions:**
- Task agent body contains `## Runbook Outline` subsection under `# Plan Context`
- When runbook has `## Outline` section: outline content embedded from runbook
- When no `## Outline` in runbook but `plans/<plan>/outline.md` exists: outline content embedded from file
- When neither exists: section contains "No outline found" fallback note
- Source priority: runbook section takes precedence over separate file

**Expected failure:** AssertionError — no outline embedding exists

**Why it fails:** Agent generation doesn't look for outline content in any source

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py::test_task_agent_embeds_outline -v`

**GREEN Phase:**

**Implementation:** Add outline source resolution and embedding

**Behavior:**
- Check runbook sections dict for `outline` key (if `extract_sections` captures it)
- If not found: check `plans/<plan>/outline.md` file existence
- Embed resolved outline under `# Plan Context / ## Runbook Outline`
- Fallback: empty section with note

**Approach:** Add outline resolution logic alongside design reading in `validate_and_create`. The outline may already be captured by `extract_sections` if it sees `## Outline` — verify and handle both sources.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add outline source resolution (runbook section → separate file → fallback)
  Location hint: in `validate_and_create`, near design reading

- File: `agent-core/bin/prepare-runbook.py`
  Action: Pass outline content to task agent generator
  Location hint: agent generation call

**Verify GREEN:** `just check && just test`

---
