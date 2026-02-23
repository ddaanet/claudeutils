# Step 3.1

**Plan**: `plans/remember-skill-update/runbook.md`
**Execution Model**: opus
**Phase**: 3

---

## Phase Context

Add agent templates as consolidation targets.

**Eligible agents (13):** artisan, brainstorm-name, corrector, design-corrector, hooks-tester, outline-corrector, refactor, runbook-corrector, runbook-outline-corrector, runbook-simplifier, scout, tdd-auditor, test-driver

**Excluded:** plan-specific agents (generated per-runbook by prepare-runbook.py), remember-task (deleted), memory-refactor (deleted)

**Platform prerequisite:** Load `/plugin-dev:skill-development` before editing skill files.

---

## Step 3.1: Add agent routing to remember skill (SKILL.md + consolidation-patterns.md)

**Objective**: Enable consolidation pipeline to route agent-relevant learnings to agent definitions.

**Target 1:** `agent-core/skills/remember/SKILL.md` Step 2 "File Selection" (line 26)
- Add agent templates as consolidation target category: `**Agent templates** → agent-core/agents/*.md: Execution patterns, tool usage, error handling, domain-specific guidance`
- Add selection criteria: learning is actionable for a specific agent role (execution pattern, stop condition, tool preference, error handling heuristic)
- List eligible agents (13) and exclusion rule (plan-specific)

**Target 2:** `agent-core/skills/remember/references/consolidation-patterns.md`
- Add "Agent-Specific" subsection under "Target Selection by Domain" (after line 30)
- Pattern: learnings about agent execution behavior → append to matching agent definition
- Example routing: "haiku rationalizes test failures" → test-driver.md; "step agents leave uncommitted files" → artisan.md

**Validation:** Read both files, verify agent routing section present with examples.

**Phase 3 Checkpoint:** `just precommit` passes.

---
