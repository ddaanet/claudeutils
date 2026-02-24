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

## Cycle 2.2: PHASE_BOUNDARY markers and phase summaries

**RED Phase:**

**Test:** `test_orchestrator_plan_boundaries_and_summaries`
**File:** `tests/test_prepare_runbook_orchestrator.py`
**Prerequisite:** Read current `generate_default_orchestrator` — understand how `is_phase_boundary` is currently detected (line 1160) and how phase boundary markers currently work

**Assertions:**
- Last step entry of each phase has `| PHASE_BOUNDARY` appended
- Inline phases appear as `- INLINE | Phase N | —` (no filename, no model/max_turns)
- Plan contains `## Phase Summaries` section after Steps section
- Each phase has a `### Phase N: title` subsection with `- IN:` and `- OUT:` bullet items
- Phase summary count matches number of distinct phases in the step list

**Expected failure:** AssertionError — new structured format from Cycle 2.1 doesn't yet have PHASE_BOUNDARY markers or Phase Summaries section

**Why it fails:** Cycle 2.1 produces step list but no boundary markers or summaries

**Verify RED:** `pytest tests/test_prepare_runbook_orchestrator.py::test_orchestrator_plan_boundaries_and_summaries -v`

**GREEN Phase:**

**Implementation:** Add PHASE_BOUNDARY markers and Phase Summaries section to orchestrator plan

**Behavior:**
- Detect phase boundaries: last item before phase number changes (same logic as current `is_phase_boundary`)
- Append `| PHASE_BOUNDARY` to those entries
- Format inline phases: `- INLINE | Phase N | —`
- Generate `## Phase Summaries` section from phase descriptions
- Each phase summary has placeholder IN/OUT that will be populated from runbook phase descriptions

**Approach:** Phase boundary detection already exists in current code. Add PHASE_BOUNDARY suffix to pipe-delimited entries. For summaries, extract from phase preambles (passed via `phase_preambles` parameter) or generate placeholder if not available.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add PHASE_BOUNDARY suffix and Phase Summaries section to `generate_default_orchestrator`
  Location hint: in the step list generation loop and after the loop

**Verify GREEN:** `just check && just test`

---

## Cycle 2.3: max_turns extraction from step metadata

**RED Phase:**

**Test:** `test_max_turns_extraction_and_propagation`
**File:** `tests/test_prepare_runbook_orchestrator.py`
**Prerequisite:** Read `agent-core/bin/prepare-runbook.py` `extract_step_metadata` (line 878) — understand current metadata extraction for model and report_path

**Assertions:**
- `extract_step_metadata` returns `max_turns` key when `**Max Turns**: 25` present in content
- `extract_step_metadata` returns `max_turns: 30` (default) when no Max Turns field present
- Orchestrator plan step entries include max_turns value from metadata: `- step-1-1.md | Phase 1 | sonnet | 25`
- Default max_turns (30) appears in step entries when not specified in content

**Expected failure:** AssertionError — `extract_step_metadata` doesn't look for Max Turns field

**Why it fails:** Current metadata extraction only handles Execution Model and Report Path

**Verify RED:** `pytest tests/test_prepare_runbook_orchestrator.py::test_max_turns_extraction_and_propagation -v`

**GREEN Phase:**

**Implementation:** Add Max Turns extraction to `extract_step_metadata` and propagate to orchestrator plan

**Behavior:**
- Parse `**Max Turns**:\s*(\d+)` from step content (case-insensitive)
- Default to 30 when not specified
- Include max_turns in orchestrator plan step entries

**Approach:** Add regex to `extract_step_metadata` alongside existing model/report_path extraction. Pass extracted max_turns through to `generate_default_orchestrator` step list generation.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add max_turns regex extraction to `extract_step_metadata`
  Location hint: line 878, after report_path extraction

- File: `agent-core/bin/prepare-runbook.py`
  Action: Include max_turns in step list entries in `generate_default_orchestrator`
  Location hint: in the step list formatting loop

**Verify GREEN:** `just check && just test`

---

## Cycle 2.4: verify-step.sh creation and testing

**RED Phase:**

**Test:** `test_verify_step_clean_state` and `test_verify_step_dirty_states`
**File:** `tests/test_verify_step.py` (create)
**Prerequisite:** Read `agent-core/skills/orchestrate/SKILL.md` — confirm the `scripts/` subdirectory doesn't exist yet and will be created. Read design section "Verification Script" for contract.

**Assertions (clean state test):**
- Script at `agent-core/skills/orchestrate/scripts/verify-step.sh` exists and is executable
- In a clean git repo (all committed, no submodules out of sync): script exits 0
- stdout contains "CLEAN"

**Assertions (dirty state tests — parametrized):**
- Uncommitted changes (modified tracked file): script exits 1, stdout contains "DIRTY"
- Untracked files: script exits 1, stdout contains "DIRTY"
- Submodule pointer drift (submodule at different commit than recorded): script exits 1, stdout contains "SUBMODULE"

**Test setup:** Create real git repos in `tmp_path` using `git init`, `git add`, `git commit`. For submodule test: create two repos, add one as submodule, advance submodule HEAD without updating parent.

**Expected failure:** FileNotFoundError or similar — script doesn't exist yet

**Why it fails:** `agent-core/skills/orchestrate/scripts/verify-step.sh` hasn't been created

**Verify RED:** `pytest tests/test_verify_step.py -v`

**GREEN Phase:**

**Implementation:** Create verify-step.sh script

**Behavior:**
- Check `git status --porcelain` — any output means dirty tree
- Check `git submodule status` — lines starting with `+` mean pointer drift
- Run `just precommit` — non-zero exit means validation failure
- Exit 0 with "CLEAN" on stdout if all pass
- Exit 1 with diagnostic details on stdout if any fail

**Approach:** Write bash script using token-efficient pattern (`exec 2>&1; set -xeuo pipefail`). Three sequential checks, each with early exit on failure.

**Changes:**
- File: `agent-core/skills/orchestrate/scripts/verify-step.sh` (create)
  Action: Create verification script per design contract
  Location hint: new file

**Note on precommit test:** The `just precommit` check is hard to test in isolation (requires project tooling in tmp_path). The E2E tests cover git-clean and submodule checks. Precommit validation is tested implicitly through the existing test suite's precommit runs. If needed, mock `just precommit` as a simple script in the test fixture.

**Verify GREEN:** `just check && just test`
