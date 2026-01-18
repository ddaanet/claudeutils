# Session: Task Agent Pattern Implementation

## Current Work

**Branch:** unification

**Task:** Implement MVP task agent pattern (Option A)

**Status:** Infrastructure complete, ready for baseline agent creation

## Progress Summary

**This Session:**
- Reviewed session plan (`tmp/session-plan-task-agents.md`) with sonnet agent
  - Identified scope issues: 12 tasks, 50-70 agent calls, 750k-1.5M tokens
  - Chose Option A (MVP): Validate pattern before documenting
- Clarified session.md vs context.md scope with opus agent
  - Result: `tmp/session-context-scope.md`
  - Key: No duplication, session=volatile, context=stable
- Created `/shelve` skill as proper Claude Code skill
  - Location: `.claude/skills/shelve/`
  - Features: Decision logic, template separation, metadata headers
- Shelved unification project session and context
  - Archived to `agents/shelf/unification-*.md`
  - Updated `agents/todo.md` with references
- Populated new context.md with Option A plan
- Added deferred tasks to todo.md

## Handoff to Sonnet Orchestrator

**Remaining work (Option A scope):**

1. **Delegate baseline task agent creation**
   - Extract from current Task tool system prompt
   - Remove: codebase assumptions, search/analyze language, detailed reports, emoji
   - Focus: Execute plan, stop on missing info/unexpected results
   - Output to: `agent-core/agents/agent-task-baseline.md`
   - Model: Sonnet (requires judgment for extraction/modification)

2. **Delegate weak orchestrator pattern POC**
   - Document pattern as design artifact
   - Output to: `agent-core/pattern-weak-orchestrator.md`
   - Model: Sonnet (design work)

3. **Execute Phase 2 step using pattern validation**
   - Apply patterns to real work (Phase 2 unification)
   - Capture lessons learned
   - Validate hypotheses from context.md
   - Model: As needed per pattern (likely haiku for orchestration, sonnet for steps)

**Execution notes:**
- Use quiet execution pattern (reports to files, terse returns)
- Delegate one task at a time (no batching)
- Each task gets fresh agent (no noise accumulation)
- Stop on unexpected results (#stop pattern)

**Key files for delegates:**
- Context: `agents/context.md` (full Option A plan and rationale)
- Session plan: `tmp/session-plan-task-agents.md` (original 12-task plan)
- Scope definition: `tmp/session-context-scope.md` (session vs context)
- Deferred work: `agents/todo.md` (items for later sessions)

## Blockers

None currently.

## Decisions

**Shelving pattern:**
- Always shelve session.md (volatile handoff context)
- Conditionally shelve context.md (when project structure changes)
- Decision tree in `tmp/session-context-scope.md` lines 100-108
- Archive to `agents/shelf/<name>-[session|context].md`
- Reference in `agents/todo.md`

**Option A rationale:**
- Practice before documentation (validate patterns on real work)
- Avoid circular dependency (don't document unproven patterns)
- Immediate value (Phase 2 continues) vs. speculative infrastructure
- Foundation for Session 2 (informed by validation results)

**Template separation:**
- Embedded templates bloat skill prompts
- Separate template files enable progressive disclosure
- Use `cp` instead of Write for reset operations
- Pattern applied in `/shelve` skill

## Next Steps

1. Delegate baseline agent creation to sonnet
2. Delegate weak orchestrator pattern doc to sonnet
3. Execute Phase 2 step with pattern, capture lessons

**Success criteria:**
- Baseline agent exists in agent-core
- Weak orchestrator pattern documented
- Phase 2 step executed using pattern
- Lessons learned captured for pattern refinement
