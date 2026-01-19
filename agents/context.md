# Context: Oneshot Workflow (Pattern Validated)

<!--
Purpose: Task-related, relatively stable, cross-session context
Pattern validation complete. Phase 1 (Script) and Phase 2 (Skills) implemented.
Documentation formalized in WORKFLOW.md.
-->

## Objective

✅ **Complete:** Oneshot workflow pattern validated and documented.

**Status:** Phase 1 (Script) and Phase 2 (Skills) complete. Phase 3 (Documentation) complete. Phase 4 (Cleanup) pending.

**Deliverables:**
- ✅ Workflow guide (`WORKFLOW.md`)
- ✅ Baseline task agent (`agent-core/agents/quiet-task.md`)
- ✅ Runbook preparation script (`agent-core/bin/prepare-runbook.py`)
- ✅ Five skills: `/design`, `/plan-adhoc`, `/orchestrate`, `/vet`, `/remember`
- ✅ Terminology standardization in `CLAUDE.md`

## Key Documents

**Primary Documentation:**
- `WORKFLOW.md` - User-facing workflow guide (6 stages, 5 skills)
- `plans/oneshot-workflow/design.md` - Original design document

**Implementation:**
- `agent-core/agents/quiet-task.md` - Baseline task agent
- `agent-core/bin/prepare-runbook.py` - Runbook preparation script (300 lines, stdlib-only)

**Skills (`.claude/skills/`):**
- `design/` - Opus design sessions
- `plan-adhoc/` - Sonnet planning with runbook prep
- `orchestrate/` - Weak orchestrator execution
- `vet/` - In-progress change review
- `remember/` - Documentation updates

**Terminology:** See `CLAUDE.md` for standardized terms (job, runbook, phase, step, etc.)

## Architecture

### Pattern: Runbook-Specific Agent

**Problem:** Context overhead prevents agent-per-step delegation pattern.

**Solution:** Cache runbook context in specialized agent system prompt.

**Implementation:**
1. Create baseline task agent (`quiet-task.md`)
2. Planning agent creates runbook-specific agent (baseline + common context)
3. Store in agents directory: `.claude/agents/<runbook-name>-task.md`
4. For each step: Load runbook-specific agent, append step reference, invoke
5. Fresh agent invocation per step (no noise accumulation)

**Creation responsibility:**
- Planning agent (sonnet) creates runbook-specific agent during planning phase
- Uses `prepare-runbook.py` script to generate artifacts
- NOT weak orchestrator's job (too complex for haiku-level)
- Runbook-specific agent must exist before execution begins

**Benefits:**
- Context caching (runbook context reused across steps)
- Clean execution (no transcript bloat)
- Quiet pattern compatible (reports to files, terse returns)
- Reviewable (agent prompt visible in agents directory)
- Versionable (agent evolves with runbook)

### Pattern: Weak Orchestrator

**Role:** Execute runbook steps reliably, escalate on error (haiku-level complexity).

**Behavior:**
- Read runbook step from step file
- Invoke runbook-specific agent with step reference
- On success: Continue to next step
- On simple error: Delegate to sonnet for diagnostic/fix
- On complex error: Abort, provide context, request opus runbook update

**Key characteristic:** Delegation-only, no judgment calls.

**Skill:** `/orchestrate` - Implements this pattern for prepared runbooks.

### Pattern: Quiet Execution

**Agents write detailed output to files, return only:**
- Success: Filename
- Failure: Error message + diagnostic info

**Benefits:**
- Orchestrator context stays lean
- Detailed logs available for debugging
- Token-efficient delegation

## Design Decisions

### Pattern Validation Approach

**Original scope:** 12 tasks, comprehensive documentation before validation.

**Problems identified:**
1. Circular dependency: Documenting patterns before validating
2. No proof-of-concept or integration testing
3. Scope unrealistic for single session

**Chosen approach (Option A - MVP):**
- Validate pattern through implementation first
- Document after validation (evidence-based)
- Immediate value (working tools) vs. speculative documentation
- Risk mitigation: Practice reveals issues before investment

**Result:** Pattern validated successfully through Phase 1 and 2 implementation.

### Why Baseline Agent First

**Current Task tool behavior:**
- Assumes large codebase → verbose search/analysis directives
- Emphasizes thoroughness, exploration, detailed reporting
- Includes emoji directives
- Mixed execution + research responsibilities

**Baseline agent modifications:**
- Remove codebase size assumptions
- Remove search/analyze/explore language (plan-time concerns)
- Remove detailed report requirements
- Remove emoji directive
- Focus role: Execute steps, stop on missing info or unexpected results
- Output: Brief report (success) or diagnostic info (error)

**Usage:**
- Baseline = reusable foundation
- Specialization = append runbook context (runbook-specific agent)
- Further specialization = append step reference (step execution)

### Weak Orchestrator Validation

**Testing hypothesis:**
- Can haiku execute runbook steps reliably with runbook-specific agents?
- Does error escalation pattern work (haiku → sonnet → opus)?
- Is quiet execution + terse return sufficient for orchestration?

**Validation approach:**
- Implement pattern in `/orchestrate` skill
- Test with real runbook execution
- Capture lessons learned
- Refine pattern based on results

**Result:** Pattern works as designed. `/orchestrate` skill implements validated pattern.

## Implementation Status

**Completed Phases:**
- ✅ Phase 1: Script implementation (`prepare-runbook.py`, `quiet-task.md`)
- ✅ Phase 2: Skill creation (5 skills: `/design`, `/plan-adhoc`, `/orchestrate`, `/vet`, `/remember`)
- ✅ Phase 3: Documentation (`WORKFLOW.md`, terminology updates)

**Pending:**
- Phase 4: Cleanup (archive obsolete scripts, update existing runbooks, terminology pass)

**Deferred Work:**
- Context monitoring skill (100k/125k thresholds)
- Feature development workflow (TDD-focused, separate from oneshot)
- Additional tooling (decision catalog, dependency analyzer)

**Pattern Status:** Validated and production-ready. Documentation complete.

## Source Materials

**Current Task tool system prompt:** Extract from tool descriptions, basis for baseline agent.

**Existing patterns:**
- `/shelve` skill: Just implemented (progressive disclosure, template separation)
- `/commit` skill: Example of proper Claude Code skill structure
- `skills/skill-shelf.md`: Older pattern, reference only

**Related projects:**
- agent-core: `/Users/david/code/agent-core` (git submodule in claudeutils)
- Target for pattern documentation and baseline agent
