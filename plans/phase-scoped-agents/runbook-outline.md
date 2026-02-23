# Runbook Outline: Phase-Scoped Agent Context

**Design:** `plans/phase-scoped-agents/outline.md`
**Status:** Draft

## Requirements Mapping

| Requirement | Phase | Items |
|---|---|---|
| FR-1: Per-phase agents with phase-scoped context | 1 | 1.1–1.4 |
| FR-2: Same base type, injected context differentiator | 1 | 1.2, 1.3 |
| FR-3: Orchestrate-evolution dispatch compatibility | 2 | 2.1–2.3 |
| Orchestrate skill reads Agent: field | 3 | inline |

## Key Decisions (from outline)

- Naming: `crew-<plan>-p<N>` multi-phase, `crew-<plan>` single-phase
- Baseline per phase type: TDD → test-driver, general → artisan
- Context layers: frontmatter + baseline + plan context + phase context + footer
- Inline phases: no agent generated (unchanged)
- Orchestrator plan: Phase-Agent Mapping table populated, `Agent:` field per step

## Expansion Guidance

- New test file `tests/test_prepare_runbook_agents.py` for Phase 1–2 tests (existing files at 200–380 lines — avoid growth past 400)
- Phase 1 tests unit-level functions; Phase 2 tests integration through `validate_and_create()`
- `validate_and_create()` signature change: `agent_path` → `agents_dir` (breaking change, all callers update in Phase 2)
- Existing test helper `_run_validate()` in 4 test files passes `agent_path` — regression updates needed in Phase 2

---

### Phase 1: Per-phase agent generation functions (type: tdd, model: sonnet)

Core functions for naming, composition, and per-phase baseline selection.

**Affected files:**
- `agent-core/bin/prepare-runbook.py` — new/modified functions
- `tests/test_prepare_runbook_agents.py` — new test file

- Cycle 1.1: Agent naming convention
  - RED: `generate_agent_frontmatter()` with `phase_num=2, total_phases=3` produces frontmatter containing `name: crew-testplan-p2`. Also test single-phase case: `total_phases=1` produces `name: crew-testplan` (no `-pN`).
  - GREEN: Add `phase_num` and `total_phases` params to `generate_agent_frontmatter()`. Use `crew-{name}-p{phase_num}` when `total_phases > 1`, `crew-{name}` otherwise. Update description to `Execute phase {N} of {name}`.

- Cycle 1.2: Per-phase baseline selection
  - RED: New function `get_phase_baseline_type(phase_content)` returns `"tdd"` when content contains `## Cycle` headers, `"general"` otherwise. Test with TDD content (has `## Cycle 1.1:`) and general content (has `## Step 1.1:`).
  - GREEN: Implement `get_phase_baseline_type()` using regex match on `## Cycle` vs `## Step`. Feed result to existing `read_baseline_agent()`.

- Cycle 1.3: Phase agent body composition
  - Depends on: 1.1, 1.2
  - RED: New function `generate_phase_agent(name, phase_num, phase_type, plan_context, phase_context, model, total_phases)` returns markdown with all 5 layers: (1) frontmatter with crew naming, (2) baseline body per phase_type, (3) plan context section, (4) phase context section, (5) clean-tree footer. Assert each layer present and ordered correctly.
  - GREEN: Implement `generate_phase_agent()` composing all layers. Uses `generate_agent_frontmatter()` for (1), `read_baseline_agent()` for (2), wraps plan/phase context in sections for (3)/(4), appends footer for (5).

- Cycle 1.4: Phase type detection from assembled content
  - RED: New function `detect_phase_types(content)` returns `{phase_num: "tdd"|"general"|"inline"}` dict. Test with mixed runbook content having TDD phase (cycles), general phase (steps), inline phase (type: inline tag). Assert correct type per phase.
  - GREEN: Implement `detect_phase_types()` — parse phase headers, classify each by scanning content between phase boundaries for `## Cycle` (tdd), `## Step` (general), or `(type: inline)` tag.

### Phase 2: Orchestrator plan format and integration (type: tdd, model: sonnet)

Orchestrator plan format changes and integration through `validate_and_create()`.

**Affected files:**
- `agent-core/bin/prepare-runbook.py` — orchestrator generation, validate_and_create
- `tests/test_prepare_runbook_agents.py` — integration tests
- `tests/test_prepare_runbook_orchestrator.py` — regression updates
- `tests/test_prepare_runbook_mixed.py` — regression updates
- `tests/test_prepare_runbook_inline.py` — regression updates
- `tests/test_prepare_runbook_phase_context.py` — regression updates

- Cycle 2.1: Orchestrator plan Agent: field per step
  - RED: `generate_default_orchestrator()` output includes `Agent: crew-<name>-p<N>` line for each step entry. Test with 2-phase TDD runbook, assert each step has its phase's agent name.
  - GREEN: Add `phase_agents` parameter (dict of phase_num → agent_name) to `generate_default_orchestrator()`. Emit `Agent: {agent_name}` after each step's `##` header line. Update header text from "Execute steps sequentially using {name}-task agent" to "Execute steps using per-phase agents."

- Cycle 2.2: Phase-Agent Mapping table
  - RED: Orchestrator plan contains `## Phase-Agent Mapping` section with table rows: phase number, agent name, model, type. Test with 3-phase runbook (TDD, general, inline).
  - GREEN: Generate mapping table in `generate_default_orchestrator()` before step list. Each phase: `| {N} | crew-{name}-p{N} | {model} | {type} |`. Inline phases: agent column shows "(orchestrator-direct)".

- Cycle 2.3: validate_and_create creates per-phase agents
  - Depends on: 1.3, 1.4, 2.1, 2.2
  - RED: Integration test through `validate_and_create()` with a 2-phase mixed runbook (TDD phase 1, general phase 2). Assert: (a) `crew-<name>-p1.md` and `crew-<name>-p2.md` agent files created; (b) old `<name>-task.md` NOT created; (c) TDD phase agent contains test-driver baseline; (d) general phase agent contains artisan baseline; (e) both agents contain plan context (common context); (f) each has its own phase context.
  - GREEN: Modify `validate_and_create()`: change `agent_path` param to `agents_dir` (Path to `.claude/agents/`). Use `detect_phase_types()` to classify phases. For each non-inline phase, call `generate_phase_agent()` and write to `agents_dir / f"crew-{name}-p{N}.md"`. Pass `phase_agents` dict to `generate_default_orchestrator()`. Update `main()` to pass `agents_dir` instead of `agent_path`. Update `derive_paths()` to return `agents_dir` instead of single path.

- Cycle 2.4: Inline phases produce no agent file
  - RED: `validate_and_create()` with a runbook having phases 1 (TDD), 2 (inline), 3 (general). Assert `crew-<name>-p1.md` and `crew-<name>-p3.md` exist, `crew-<name>-p2.md` does NOT exist. Orchestrator plan shows phase 2 as "(orchestrator-direct)" in mapping table.
  - GREEN: Skip `generate_phase_agent()` call for inline phases. Already handled by type detection.

- Cycle 2.5: Existing test regression updates
  - [REGRESSION]
  - GREEN: Update `_run_validate()` helpers in all 4 test files to pass `agents_dir` instead of `agent_path`. Update assertions that check for `<name>-task.md` to check for `crew-<name>[-p<N>].md`. Verify all existing tests pass with the new agent naming format.

### Phase 3: Orchestrate skill update (type: inline)

- Update `agent-core/skills/orchestrate/SKILL.md` Section 3.1:
  - Line 97: Change `subagent_type: "<runbook-name>-task"` to `subagent_type: [from orchestrator plan "Agent:" field for this step]`
  - Lines 39, 47: Update `<runbook-name>-task` references to describe per-phase agents
  - Line 1014 of `generate_default_orchestrator()`: update header text (already done in 2.1, verify)
