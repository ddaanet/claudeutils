# Learnings Consolidation: Runbook Outline

**Status:** Draft outline for review
**Date:** 2026-02-06
**Source Design:** `plans/learnings-consolidation/design.md`

---

## Requirements Mapping

| Requirement | Phase | Steps | Notes |
|-------------|-------|-------|-------|
| FR-1 | 2 | 2.1 | Handoff step 4c — run script, evaluate trigger conditions |
| FR-2 | 1 | 1.1 | Script calculates git-active-day age with staleness detection |
| FR-3 | 2 | 2.1 | Trigger thresholds: 150 lines OR 14 days staleness, 7 days freshness |
| FR-4 | 3 | 3.1 | Remember-task agent pre-check — keyword overlap + negation patterns |
| FR-5 | 3 | 3.1 | Remember-task agent pre-check — semantic comparison with target file |
| FR-6 | 3 | 3.1 | Remember-task agent pre-check — keyword/phrase overlap scoring |
| FR-7 | 2 | 2.1 | Handoff refactor flow: detect limit → spawn memory-refactor → retry |
| FR-8 | 3 | 3.1 | Remember-task agent embeds /remember protocol per D-4 |
| FR-9 | 2 | 2.2 | Remember skill quality criteria and staging retention sections |
| NFR-1 | 2 | 2.1 | Try/catch wrapper in handoff step 4c, log and continue on error |
| NFR-2 | 3 | 3.1, 3.2 | Both agents use model: sonnet in frontmatter |
| NFR-3 | 3 | 3.1 | Remember-task agent writes report to tmp/consolidation-report.md |

---

## Phase Structure

### Phase 1: Script Foundation (learning-ages.py)

**Complexity:** Moderate (git operations, active-day calculation, staleness heuristic)
**Model:** Sonnet (git log analysis requires semantic judgment)
**Estimated scope:** ~150 lines

**Steps:**
- 1.1: Implement learning-ages.py script with age calculation and staleness detection
  - Script location: `agent-core/bin/learning-ages.py`
  - Shebang and executable permission for direct invocation
  - Parse learnings.md (skip first 10 lines per validate-learnings.py pattern, extract H2 headers)
  - Git blame with `-C -C` for entry dates (handles renames, merge commits)
  - Calculate active-day age: count unique commit dates between entry date and today
  - Detect staleness: walk `git log -p` for removed H2 headers (consolidation evidence)
  - Fallback: report "unknown (no prior consolidation detected)" when no evidence found
  - Output markdown format per D-2: file lines, last consolidation age, total entries, entries ≥7 days, then per-entry headers with age/added date
  - Error handling: exit 0 on success, 1 on error (stderr)
  - Reference: design § D-2, Implementation Component 1

**Success criteria:**
- Script runs without errors on current agents/learnings.md
- Output matches design spec format exactly (§ D-2)
- Staleness detection works (finds last consolidation or reports "unknown")
- Active-day calculation accurate (excludes inactive days, includes merge commits)
- Handles edge cases: entry added today (0 active days), file renames, no prior consolidation

---

### Phase 2: Skill Updates (handoff + remember)

**Complexity:** Low-moderate (careful insertion, preserve existing behavior)
**Model:** Sonnet (skill modification requires protocol understanding)
**Estimated scope:** ~50 lines total across 2 skills

**Steps:**
- 2.1: Add step 4c to handoff skill with trigger logic and refactor flow
  - File: `agent-core/skills/handoff/SKILL.md`
  - Insert new step 4c: "Consolidation Trigger Check" between existing step 4b and step 5
  - Step 4c implementation:
    - Run `agent-core/bin/learning-ages.py agents/learnings.md` to get age data
    - Evaluate trigger conditions (any one sufficient):
      - Size trigger: file exceeds 150 lines
      - Staleness trigger: 14+ active days since last consolidation
    - If triggered:
      - Filter entries with age ≥ 7 active days
      - Check batch size ≥ 3 entries
      - If sufficient: delegate to remember-task agent with filtered entry list (Task tool)
      - Read report from returned filepath
      - Handle escalations:
        - Contradictions → note in handoff output under Blockers/Gotchas
        - File limits → delegate to memory-refactor agent for target file, then re-invoke remember-task with only skipped entries
    - If not triggered or batch insufficient: skip consolidation, continue to step 5
    - Wrap entire step in try/catch (NFR-1): log error to stderr, note in handoff output, continue to step 5
  - Update frontmatter allowed-tools: add `Task`, `Bash(agent-core/bin/learning-ages.py:*)`
  - Preserve existing step 5 numbering and all other steps unchanged
  - Reference: design § D-1, D-3, D-6, D-7, Implementation Component 4

- 2.2: Update remember skill with quality criteria and staging retention guidance
  - File: `agent-core/skills/remember/SKILL.md`
  - Add new section: "Learnings Quality Criteria" per design Implementation Component 5
    - Principle-level (consolidate) with examples
    - Incident-specific (reject/revise) with examples
    - Meta-learnings guidance (use sparingly)
  - Add new section: "Staging Retention Guidance" per design Implementation Component 5
    - Keep in staging criteria (< 7 days, pending cross-refs, active investigation)
    - Consolidate criteria (≥ 7 days proven, applied consistently, referenced multiple times)
    - Drop criteria (superseded, contradicted, incident-specific without principle)
  - No protocol changes to existing steps 1-4a
  - Reference: design § Implementation Component 5

**Success criteria:**
- Handoff step 4c correctly positioned (after 4b, before 5)
- Tool permissions include learning-ages.py and Task
- Trigger thresholds match design (150 lines, 14 days, 7 days freshness, 3 minimum)
- Remember skill has new guidance sections
- Existing handoff/remember behavior unchanged

---

### Phase 3: Agent Definitions (remember-task + memory-refactor)

**Complexity:** Moderate-high (embed protocol, pre-checks, reporting)
**Model:** Sonnet (agent protocol design requires architectural understanding)
**Estimated scope:** ~200 lines total across 2 agents

**Steps:**
- 3.1: Create remember-task agent with embedded protocol and pre-consolidation checks
  - File: `agent-core/agents/remember-task.md`
  - Frontmatter (YAML):
    - name: remember-task
    - description: Multi-line, include use case (delegating learnings consolidation during handoff), execution pattern (filtered entry list with age metadata), output (tmp/consolidation-report.md)
    - model: sonnet
    - color: green
    - tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
  - Body content structure:
    - Role statement: Consolidation agent executing remember protocol
    - Input specification: Receives filtered entry list with age metadata in task prompt
    - Pre-consolidation checks (§ D-5, run before consolidation):
      - Supersession: keyword overlap + negation patterns, drop older entry
      - Contradiction: semantic comparison with target file content, escalate to orchestrator
      - Redundancy: keyword/phrase overlap scoring with target file, drop from batch
      - Conservative bias: escalate when uncertain (false positive > false negative)
    - Consolidation protocol: Extract from /remember skill steps 1-4a (understand, route, draft, apply+verify) per D-4
    - Source comment: `<!-- Source: agent-core/skills/remember/SKILL.md -->` (synchronization tracking per D-4)
    - Discovery mechanism updates: memory index, CLAUDE.md/@-refs, rules entries (from remember protocol)
    - Retention: Keep 3-5 most recent learnings in staging (from remember protocol)
    - Report format: Write detailed report to `tmp/consolidation-report.md` with sections:
      - Summary: entries processed, consolidated, dropped, escalated
      - Supersession decisions: entry pairs dropped
      - Redundancy decisions: entries dropped with rationale
      - Contradictions: entries escalated with target file conflicts
      - File limits: target files at 400-line limit, entries skipped
      - Discovery updates: memory index entries, CLAUDE.md changes, rules updates
    - Return protocol: filepath on success (`tmp/consolidation-report.md`), error message on failure
    - Escalation protocol: report contradictions and file-limit conditions in report (handoff reads and responds)
  - Key difference from interactive /remember: operates on pre-filtered batch (only ≥7 active days), not entire learnings file
  - Reference: design § D-4, D-5, Implementation Component 2

- 3.2: Create memory-refactor agent for oversized file splitting
  - File: `agent-core/agents/memory-refactor.md`
  - Frontmatter (YAML):
    - name: memory-refactor
    - description: Multi-line, include use case (target file exceeds 400 lines), trigger (remember-task encounters limit), process (split into logical sections)
    - model: sonnet
    - color: yellow
    - tools: ["Read", "Write", "Edit", "Grep", "Glob"]
  - Body content structure:
    - Role statement: Documentation refactoring agent
    - Input specification: Target file path at/near 400-line limit
    - Process (§ D-6):
      1. Read target file, analyze content sections
      2. Identify logical split points (by H2/H3 topic boundaries)
      3. Create new files with appropriate headers
      4. Move content to new files, preserve formatting
      5. Update original file with cross-references to new files
      6. Run `validate-memory-index.py` with autofix to update index entries
    - Constraints:
      - Create headers for new files only (index validator handles consistency)
      - Preserve all content (splitting, not summarizing)
      - New files should be 100-300 lines each (balanced split)
      - Maintain semantic groupings (don't split mid-topic)
    - Output: List of files created/modified
    - Return protocol: filepaths on success, error message on failure
  - Reference: design § D-6, Implementation Component 3

**Success criteria:**
- remember-task agent embeds protocol faithfully (source comment included per D-4)
- Agent performs pre-checks before consolidation
- Agent writes report to tmp/consolidation-report.md
- memory-refactor agent splits files cleanly at logical boundaries
- Autofix validator runs after refactor
- Both agents follow quiet execution pattern (report to file, return filepath)

---

### Phase 4: Testing

**Complexity:** Moderate (mock git operations, test workflow integration)
**Model:** Sonnet (test design)
**Estimated scope:** ~200 lines test code

**Steps:**
- 4.1: Unit tests for learning-ages.py with git operation mocking
  - File: `tests/test_learning_ages.py`
  - Test categories per design Implementation Component 6:
    - Parsing:
      - Extract H2 headers from learnings.md
      - Skip preamble (first 10 lines matching validate-learnings.py pattern)
      - Handle malformed headers gracefully
    - Age calculation:
      - Mock git blame → extract commit hash + date
      - Mock git log → get set of unique commit dates
      - Count active days between entry date and today
      - Edge cases: entry added today (0 active days), same-day commits, merge commits
    - Staleness detection:
      - Mock git log -p for removed H2 headers (consolidation evidence)
      - Test with prior consolidation (recent and old)
      - Test without prior consolidation (fallback to "unknown")
      - Edge case: multiple consolidations (use most recent)
    - Trigger logic:
      - Size threshold: 149 lines (no trigger), 150 lines (trigger), 151 lines (trigger)
      - Staleness threshold: 13 days (no trigger), 14 days (trigger), 15 days (trigger)
      - Batch minimum: 2 entries (no trigger), 3 entries (trigger), 4 entries (trigger)
    - Freshness filter:
      - Include entries ≥7 active days
      - Exclude entries <7 active days
      - Boundary: exactly 7 active days (include)
    - Error handling:
      - Missing file (exit 1, stderr message)
      - Git not available (exit 1, stderr message)
      - Malformed learnings.md (skip bad entries, continue)
  - Testing approach: mock subprocess calls for git operations, create temporary learnings.md with known content
  - Reference: design § Implementation Component 6

- 4.2: Integration validation with manual testing
  - Unit test integration:
    - Create temporary learnings.md with known entries (various ages)
    - Run learning-ages.py with mocked git repo
    - Verify markdown output format matches design § D-2 exactly
    - Verify all summary fields present (file lines, last consolidation, total entries, entries ≥7 days)
  - Manual handoff trigger test:
    - Option A: Create session with learnings.md >150 lines, run handoff, verify step 4c triggers
    - Option B: Mock staleness >14 days, run handoff, verify step 4c triggers
    - Verify filtered entry list passed to remember-task agent
    - Verify handoff continues if consolidation fails (NFR-1)
  - Agent definition validation:
    - Read `agent-core/agents/remember-task.md`, verify protocol embedding faithful to remember skill
    - Verify source comment present (synchronization tracking per D-4)
    - Read `agent-core/agents/memory-refactor.md`, verify process structure matches design § D-6
    - Verify both agents use model: sonnet, appropriate tools, quiet execution pattern (report to file, return filepath)
  - No automated integration test for full workflow (complexity too high, manual validation sufficient)
  - Reference: design § Implementation Component 6

**Success criteria:**
- All unit tests pass
- Test coverage for git edge cases (merge commits, file renames)
- Integration test validates markdown output format
- Manual trigger test confirms handoff integration

---

## Key Design Decisions Reference

**D-1:** Step 4c insertion point (between 4b and 5)
**D-2:** Markdown output from script (not JSON)
**D-3:** Trigger evaluation in skill (not script) — thresholds: 150 lines, 14 days staleness, 7 days freshness, 3 minimum batch
**D-4:** Embedded protocol in agent (not skill reference via Skill tool)
**D-5:** Conservative pre-checks (supersession, contradiction, redundancy) — escalate when uncertain
**D-6:** Reactive refactoring (only when file at limit, not preemptive)
**D-7:** Graceful failure (consolidation errors don't block handoff)

---

## Cross-Phase Dependencies

**Sequential dependencies:**
- Phase 2 → Phase 1: Handoff step 4c calls learning-ages.py script (Step 2.1 → Step 1.1)
- Phase 3 → Phase 2: Remember-task agent embeds updated remember protocol (Step 3.1 → Step 2.2)
- Phase 2 → Phase 3: Handoff step 4c delegates to remember-task and memory-refactor agents (Step 2.1 → Steps 3.1, 3.2)
- Phase 4 → Phases 1-3: Tests require all components to exist

**Parallelization opportunities:**
- Phase 3: Steps 3.1 and 3.2 can be developed in parallel (no cross-dependency between remember-task and memory-refactor agents)
- Phase 4: Step 4.1 (unit tests) can start in parallel with Phase 3 completion

**Critical path:** Phase 1 → Phase 2 Step 2.2 → Phase 3 Step 3.1 → Phase 4 Step 4.2 (handoff manual test)

---

## Complexity Assessment

| Phase | Complexity | Lines | Model | Rationale |
|-------|-----------|-------|-------|-----------|
| 1 | Moderate | ~150 | Sonnet | Git operations complex, staleness heuristic requires log analysis |
| 2 | Low-Moderate | ~50 | Sonnet | Skill modification delicate, protocol preservation critical |
| 3 | Moderate-High | ~200 | Sonnet | Protocol embedding, pre-checks, two agents with coordination |
| 4 | Moderate | ~200 | Sonnet | Mock git, test workflow, integration validation |

**Total estimated scope:** ~600 lines across 6 files (script, 2 skills, 2 agents, tests)

---

## Risk Areas

**High risk:**
- Protocol embedding drift (remember skill changes → agent out of sync)
- Staleness detection edge cases (no prior consolidation, file renames)
- Handoff skill insertion (preserve existing step numbering and behavior)

**Mitigation:**
- Phase 2 includes comment in agent noting protocol source
- Phase 1 includes fallback for missing staleness data
- Phase 2 careful testing of handoff step ordering

---

## Success Metrics

**Phase completion:**
- Phase 1: Script runs, produces correct markdown, handles edge cases
- Phase 2: Skills updated, existing behavior preserved, new steps functional
- Phase 3: Agents created, protocols embedded, reporting works
- Phase 4: Tests pass, integration validated

**Overall success:**
- Handoff triggers consolidation when conditions met
- Consolidation processes learnings correctly
- Reports written to tmp/consolidation-report.md
- Handoff continues even if consolidation fails
- Memory refactor handles file-limit escalations

---

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Required file loading (before planning):**
- Load `plugin-dev:skill-development` and `plugin-dev:agent-development` skills per design Documentation Perimeter
- Read design-specified reference files: handoff skill, remember skill, consolidation-patterns.md, validate-learnings.py, validate-memory-index.py, exploration reports
- Reference existing agent patterns: quiet-task.md, vet-agent.md for agent body structure

**Phase 1 cycle guidance:**
- Create working script early (TDD RED if applicable: mock git first, then implement)
- Verify staleness detection with real repo before proceeding (git log -p pattern correctness critical)
- Include comprehensive error messages for git operation failures (user-facing diagnostics)

**Phase 2 cycle guidance:**
- Step 2.1: Preserve exact step numbering in handoff skill (4c insertion between 4b and 5)
- Step 2.1: Include complete error handling example in step 4c (try/catch with log and note pattern)
- Step 2.1: Refactor flow complexity warrants separate sub-step documentation (detect → spawn → retry logic)
- Step 2.2: Cross-reference quality criteria examples with existing learnings.md entries (show good vs bad)

**Phase 3 cycle guidance:**
- Step 3.1: Extract remember protocol sections verbatim from skill (steps 1-4a), preserve structure
- Step 3.1: Include detailed pre-check algorithm descriptions (keyword overlap scoring thresholds, conservative bias examples)
- Step 3.1: Report format examples critical (show all sections with sample content)
- Step 3.2: Logical split points require judgment — provide heuristics (semantic groupings, preserve dependencies)

**Phase 4 cycle guidance:**
- Step 4.1: Prioritize staleness detection tests (highest complexity, most edge cases)
- Step 4.1: Mock strategy documentation (subprocess.run patching pattern for git blame/log)
- Step 4.2: Manual test procedure detail (step-by-step handoff trigger validation)
- Step 4.2: Agent definition review checklist (protocol embedding, source comment, tools, color, model)

**Checkpoint guidance:**
- Phase 1→2 checkpoint: Verify script output format matches design § D-2 exactly (validate with sample learnings.md)
- Phase 2→3 checkpoint: Verify handoff step 4c insertion preserves existing behavior (no step renumbering, step 5 unchanged)
- Phase 3→4 checkpoint: Verify both agents follow quiet execution pattern (report to file, return filepath only)
- Phase 4→complete checkpoint: Run manual handoff trigger test, verify end-to-end workflow

**Consolidation candidates:**
- Phase 4 could potentially merge into Phase 3 if test development is trivial (but outline estimates 200 lines, likely not trivial)

**References to include in expansion:**
- Design decision references (D-1 through D-7) at relevant cycle points
- Implementation Component references (1-6) for cross-checking completeness
- Exploration report references for agent patterns and workflow map context
