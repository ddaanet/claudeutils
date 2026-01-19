# Context: Task Agent Pattern Implementation (Option A - MVP)

<!--
Purpose: Task-related, relatively stable, cross-session context
This session implements the minimal viable pattern for plan-specific task agents.
Full session plan reviewed and scoped down from 12 tasks to focused MVP.
-->

## Objective

Implement and validate the task agent execution pattern through a proof-of-concept, then apply to Phase 2 unification work.

**Approach:** Practice before documentation - build working pattern first, document after validation.

## Key Documents

**Session Plan:**
- `tmp/session-plan-task-agents.md` - Original 12-task plan (reviewed by sonnet)
- `tmp/session-context-scope.md` - session.md vs context.md scope definition (by opus)

**Scope Definition:**
- session.md: Volatile handoff context (current work, progress, blockers)
- context.md: Stable reference (documents, architecture, paths)
- No duplication between files

**Deliverables (Option A):**
- `agent-core/agents/quiet-task.md` - Base task agent template
- `agent-core/pattern-weak-orchestrator.md` - Weak orchestrator pattern (POC)
- `.claude/agents/phase2-task.md` - Phase 2 plan-specific agent
- Phase 2 step execution using pattern (validation)

## Architecture

### Pattern: Plan-Specific Agent

**Problem:** Context overhead prevents agent-per-step delegation pattern.

**Solution:** Cache plan context in specialized agent system prompt.

**Implementation:**
1. Create baseline task agent (extract from current Task tool)
2. Planning agent creates plan-specific agent file (baseline + plan context)
3. Store in plan directory: `.claude/agents/<plan-name>-task.md`
4. For each step: Load plan-specific agent, append step reference, invoke
5. Fresh agent invocation per step (no noise accumulation)

**Creation responsibility:**
- Planning agent (medium-strength, sonnet-level) creates plan-specific agent during plan phase
- NOT weak orchestrator's job (too complex for haiku-level)
- Plan-specific agent must exist before execution begins

**Benefits:**
- Context caching (plan context reused across steps)
- Clean execution (no transcript bloat)
- Quiet pattern compatible (reports to files, terse returns)
- Reviewable (agent prompt visible in plan directory)
- Versionable (agent evolves with plan)

### Pattern: Weak Orchestrator

**Role:** Execute plan steps, escalate on error (haiku-level complexity).

**Behavior:**
- Read plan step
- Invoke plan-specific agent with step reference
- On success: Continue to next step
- On simple error: Delegate to sonnet for diagnostic/fix
- On complex error: Abort, provide context, request opus plan update

**Key characteristic:** Delegation-only, no judgment calls.

### Pattern: Quiet Execution

**Agents write detailed output to files, return only:**
- Success: Filename
- Failure: Error message + diagnostic info

**Benefits:**
- Orchestrator context stays lean
- Detailed logs available for debugging
- Token-efficient delegation

## Design Decisions

### Why Option A (MVP) Over Full Implementation

**Original scope:** 12 tasks, 50-70 agent calls, 750k-1.5M tokens (3-5 handoffs).

**Problems identified by review (sonnet):**
1. Circular dependency: Documenting patterns before validating
2. No proof-of-concept or integration testing
3. Scope unrealistic for single session
4. Missing acceptance criteria for pattern docs

**Option A rationale:**
- Validate pattern on real work (Phase 2) before documenting
- Immediate value (Phase 2 continues) vs. speculative documentation
- Risk mitigation: Practice reveals issues before investment
- Foundation for Session 2 (informed documentation)

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
- Focus role: Execute plan, stop on missing info or unexpected results
- Output: Brief report (success) or diagnostic info (error)

**Usage:**
- Baseline = reusable foundation
- Specialization = append plan context (plan-specific agent)
- Further specialization = append step reference (step execution)

### Why Weak Orchestrator POC

**Testing hypothesis:**
- Can haiku execute plan steps reliably with plan-specific agents?
- Does error escalation pattern work (haiku → sonnet → opus)?
- Is quiet execution + terse return sufficient for orchestration?

**Validation approach:**
- Document pattern first (design artifact)
- Execute Phase 2 step using pattern
- Capture lessons learned
- Refine pattern based on results

## Deferred Work

**See:** `agents/todo.md` section "Deferred from Task Agent Pattern Session"

**Includes:**
- Context monitoring skill (100k/125k thresholds)
- Phase planning pattern documentation
- Additional tooling (decision catalog, dependency analyzer)
- Phase 2 full plan (weak orchestrator applied across all steps)

**Completed:**
- ✅ Plan-specific agent pattern documentation
- ✅ Error classification fragment
- ✅ Prerequisite validation fragment
- ✅ Commit delegation fragment
- ✅ Agent generation script (create-plan-agent.sh)

**Rationale:** Pattern validation completed through Phase 2 execution; formalization now complete. Ready for Phase 3+ application.

## Source Materials

**Current Task tool system prompt:** Extract from tool descriptions, basis for baseline agent.

**Existing patterns:**
- `/shelve` skill: Just implemented (progressive disclosure, template separation)
- `/commit` skill: Example of proper Claude Code skill structure
- `skills/skill-shelf.md`: Older pattern, reference only

**Related projects:**
- agent-core: `/Users/david/code/agent-core` (git submodule in claudeutils)
- Target for pattern documentation and baseline agent
