# Cycle 1.1

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

## Cycle 1.1: Single task agent with new naming and footers

**RED Phase:**

**Test:** `test_single_task_agent_replaces_per_phase`
**File:** `tests/test_prepare_runbook_agents.py`
**Prerequisite:** Read `agent-core/bin/prepare-runbook.py` lines 844-876 (current `generate_agent_frontmatter` and `generate_phase_agent`), lines 1341-1375 (current per-phase agent generation in `validate_and_create`)

**Assertions:**
- For a general runbook with 2 phases: exactly 1 agent file created (not 2 per-phase agents)
- Agent filename is `{name}-task.md` (not `crew-{name}-p1.md` or `crew-{name}-p2.md`)
- Agent frontmatter `name:` field is `{name}-task`
- Agent body ends with scope enforcement footer containing "Execute ONLY the step file"
- Agent body ends with clean tree footer containing "Commit all changes before reporting success"
- Agent body contains artisan.md baseline content (for general runbook)

**Expected failure:** AssertionError — current code generates `crew-{name}-p{N}` per-phase agents

**Why it fails:** `validate_and_create` iterates `phase_types` and generates one agent per non-inline phase with `crew-` prefix naming

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py::test_single_task_agent_replaces_per_phase -v`

**GREEN Phase:**

**Implementation:** Restructure agent generation in `validate_and_create` and supporting functions

**Behavior:**
- Generate single `{name}-task.md` agent regardless of phase count
- Use artisan.md baseline for general/mixed runbooks, test-driver.md for pure TDD
- Append scope enforcement and clean tree footers at bottom of agent definition
- `generate_agent_frontmatter` → rename or create new function with `{name}-task` naming
- Remove per-phase agent loop; replace with single agent generation call

**Approach:** Replace the `for phase_num, ptype in sorted(phase_types.items())` loop in `validate_and_create` with single-agent generation. The phase_agents dict should map all non-inline phases to the same agent name.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Replace `generate_phase_agent` with `generate_task_agent` that takes all plan context
  Location hint: line 858 (`generate_phase_agent` function — rename/replace this function)

- File: `agent-core/bin/prepare-runbook.py`
  Action: Modify `validate_and_create` to generate single task agent
  Location hint: around line 1341

**Verify GREEN:** `just check && just test`

---
