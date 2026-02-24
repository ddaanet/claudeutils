### Phase 1: Agent caching model (type: tdd, model: sonnet)

**Scope:** Restructure prepare-runbook.py agent generation from per-phase to per-role model. Single task agent with embedded design+outline replaces N per-phase agents.

**Files:** `agent-core/bin/prepare-runbook.py`, `tests/test_prepare_runbook_agents.py` (extend)

**Key constraints:**
- Clean break (Q-4): no backward compatibility with `crew-` naming
- Agent naming: `<plan>-task.md`, `<plan>-corrector.md`
- Baseline selection: `artisan.md` for general/mixed, `test-driver.md` for pure TDD
- Content source priority for design: `plans/<plan>/design.md` → empty section fallback
- Content source priority for outline: runbook `## Outline` section → `plans/<plan>/outline.md` → empty fallback
- Scope enforcement + clean tree footers at bottom of every agent definition

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
  Location hint: around line 858

- File: `agent-core/bin/prepare-runbook.py`
  Action: Modify `validate_and_create` to generate single task agent
  Location hint: around line 1341

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v`
**Verify no regression:** `just test`

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

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v`
**Verify no regression:** `just test`

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

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v`
**Verify no regression:** `just test`

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

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v`
**Verify no regression:** `just test`
