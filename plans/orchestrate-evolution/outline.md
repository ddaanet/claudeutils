# Orchestrate Evolution — Design Outline

## Approach

Evolve the orchestrate skill from a weak haiku orchestrator to a capable sonnet orchestrator. Replace prose-based scope constraints with structural context boundaries. Add parallel dispatch, post-step remediation, and prompt deduplication.

The evolution is not a rewrite — it preserves the orchestrate skill's structure (verify → read plan → execute steps → completion) while upgrading the intelligence and adding missing mechanical patterns.

## Key Decisions

### D-1: Abandon weak orchestration, sonnet default

**Current:** Haiku orchestrator. Many learnings are band-aids for haiku's inability to recover from failures (dirty tree = stop, scope creep = prose constraint, error = user escalation).

**Proposed:** Sonnet as default orchestrator model. Haiku available as opt-in for proven simple runbooks.

**Rationale:** "Weak orchestration is premature optimization" — validated across 12+ sessions. Recovery, remediation, and exception handling require judgment. Sonnet provides this without opus cost.

**What changes:**
- Orchestrate skill assumes sonnet-level reasoning
- Error escalation simplifies: sonnet → user (2 levels, not 3)
- Post-step remediation possible (sonnet can commit/fix, not just stop)
- "Delegate, don't decide" relaxed to "delegate execution, handle exceptions"

**What stays the same:**
- Mechanical checks remain mechanical (UNFIXABLE grep, git status, precommit)
- Agents still do the work, orchestrator still coordinates
- Step files, orchestrator plans, plan-specific agents — all preserved

### D-2: Context-as-scope-boundary

**Current:** Prose constraint ("Execute ONLY this step") — violated repeatedly. Plan-specific agents get full context injection from prepare-runbook.py.

**Proposed:** Structural enforcement. Executing agent receives ONLY:
- The step file (its immediate task)
- Design reference path (for reading if needed)
- Outline reference path (for understanding position)

Agent cannot scope-creep to step N+1 because step N+1 is not in its context.

**Implementation:**
- Orchestrator reads step file content, passes it in Task prompt
- Design and outline are paths (agent reads if needed, not pre-loaded)
- Other step files never mentioned, never referenced
- Plan-specific agents become thinner (less pre-loaded context)

**Eliminates:**
- "Execute ONLY this step" prose constraints
- Return verification (checking agent didn't do extra work)
- Scope creep instructions in delegation prompts

### D-3: Two-tier context injection

**Tier 1 — Execution:** Step agent gets step content + design path + outline path. Minimal. For doing work.

**Tier 2 — Review:** Vet-fix-agent gets step content + design path + outline path + phase file path + changed files. Broader. For alignment checking.

**Rationale:** Execution needs focus (narrow context = less distraction). Review needs breadth (can the output be checked against the design?). These are different information needs.

**prepare-runbook.py role:** Generates context tier metadata in orchestrator plan. Orchestrator reads tiers and constructs appropriate prompts.

**Example metadata format in orchestrator plan:**
```
## Step 1-2: Implement merge detection

**Context Tier**: execution
**Files**: plans/<name>/steps/step-1-2.md, plans/<name>/design.md, plans/<name>/outline.md
**Model**: sonnet
```

### D-4: Parallel execution support

**Current:** "Always sequential unless orchestrator plan explicitly allows parallel."

**Proposed:** First-class parallel dispatch. The orchestrator plan declares parallel groups.

**Format in orchestrator plan:**
```
## Execution Order

### Group 1 (sequential)
- step-0-1 (model: sonnet, files: core.py)

### Group 2 (parallel)
- step-1-1 (model: sonnet, files: phase-1.md, tier: execution)
- step-1-2 (model: sonnet, files: phase-2.md, tier: execution)
- step-1-3 (model: sonnet, files: phase-3.md, tier: execution)

### Group 3 (sequential)
- step-2-1 (model: sonnet, files: runbook.md, tier: review)
```

**Orchestrate skill behavior:**
- Sequential groups: one Task call per step (current behavior)
- Parallel groups: batch all Task calls in single message
- Phase boundary checkpoints still occur between groups

**prepare-runbook.py:** Analyzes step dependencies (same files, shared state) to determine parallelism. Emits execution order with explicit grouping.

### D-5: Post-step verify-remediate-RCA

**Current:** Dirty tree = STOP, escalate to user. No remediation.

**Proposed three-step protocol:**
1. `git status --porcelain` — if clean, proceed
2. If dirty: sonnet orchestrator assesses and remediates (commit uncommitted files, or delegate fix)
3. After remediation: generate RCA pending task in session.md ("Why did step N leave dirty tree? Investigate skill/prompt: X")
4. `just precommit` — verify integrity after step completion

**Rationale:** Most dirty trees are forgotten commits, not design problems. Sonnet can handle this. RCA task ensures root cause gets fixed in the responsible skill.

**Escalation:** If remediation fails (conflict, test failure), THEN escalate to user.

### D-6: Delegation prompt deduplication

**Current:** Each Task call includes full prompt text. N parallel dispatches = N copies of boilerplate.

**Proposed:** For 3+ parallel tasks, write shared context to file. Reference by path in prompts.

**Rationale for 3+ threshold:** Below 3 tasks, deduplication overhead (file write, path references) exceeds savings. At 3+ tasks, repeated boilerplate becomes significant enough to justify the indirection.

**prepare-runbook.py role:** Generates `shared-context.md` alongside step files when parallel groups detected. Contains: design summary, conventions, commit instructions, scope constraints.

**Prompt template:**
```
Execute step from: plans/<name>/steps/step-N.md
Read shared context: plans/<name>/shared-context.md

[Step-specific instructions only]
```

### D-7: Simplified error escalation

**Current:** haiku → sonnet → user (3 levels, with Level 1/1b/2 sub-levels)

**Proposed:** sonnet → user (2 levels)
- Sonnet orchestrator handles execution-level issues inline (missing files, failed commands, dirty tree)
- Design-level issues escalate to user (wrong approach, scope change, blocking ambiguity)
- Opus removed from escalation chain (too expensive for error recovery)

## Open Questions

### Q-1: Planning absorption

The original requirement says "absorb planning into orchestrate." The analysis concludes planning stays separate. Which is correct?

**Reconciliation:** The requirement language "absorb planning" is misleading. What actually happened: orchestrate should absorb *patterns discovered during planning orchestration*, not absorb planning itself. Planning skills (plan-tdd, plan-adhoc) remain independent. The gaps (parallel dispatch, deduplication, remediation) are execution patterns applicable to all runbooks, not planning-specific.

**Option A:** Keep planning skills separate. Orchestrate gains patterns from planning experience (parallel dispatch, deduplication) but plan-tdd/plan-adhoc remain independent skills.

**Option B:** Orchestrate can orchestrate planning. plan-tdd/plan-adhoc emit orchestrable artifacts (phase files as steps), orchestrate skill coordinates them. This formalizes what opus did ad-hoc during worktree-skill.

**Option C:** Hybrid — plan skills emit DAG metadata but execute themselves. Orchestrate provides parallel dispatch as a utility but doesn't own planning flow.

### Q-2: Plan-specific agents fate

**Current:** prepare-runbook.py generates `.claude/agents/<name>-task.md` with injected context. These require restart to discover.

**With context-as-scope-boundary:** Agents need less pre-loaded context (context comes from orchestrator prompt, not agent definition). Do we still need plan-specific agents?

**Option A:** Keep plan-specific agents. They still serve context caching across steps (agent definition loaded once, reused per step).

**Option B:** Use generic task agents (quiet-task, tdd-task). All context comes from orchestrator prompt. No restart needed. prepare-runbook.py generates prompt templates instead of agent files.

**Option C:** Hybrid — thin plan-specific agents (just metadata, no content injection) + orchestrator-provided context.

### Q-3: Remediation authority

When dirty tree detected, who fixes it?

**Scenario-based guidance:**
- Simple uncommitted files → Option A (orchestrator commits inline, mechanical)
- Test failures or merge conflicts → Option B (delegate to remediation agent, requires judgment)
- Missing cleanup in step logic → Option C (resume original agent with "complete cleanup" instruction, reuses context)

**Option A:** Sonnet orchestrator fixes inline (simplest, but mixes orchestration with execution).

**Option B:** Orchestrator delegates remediation to a separate agent (clean separation, but adds agent overhead).

**Option C:** Orchestrator resumes the original step agent to complete its cleanup (reuses context, but relies on Task resume working correctly).

### Q-4: Backwards compatibility

**Design implications:**
- Option A: Simpler orchestrate skill code, no format detection overhead, but requires regenerating all existing orchestrator plans
- Option B: Orchestrate skill includes format detection (check for "## Execution Order" section), defaults to sequential for old format, allows gradual migration

**Option A:** Clean break. New prepare-runbook.py generates new format. Old orchestrator plans don't work.

**Option B:** Backwards compatible. New skill handles both old (sequential, no metadata) and new (groups, tiers) formats. Old plans default to sequential execution.

## Scope

**In scope:**
- Orchestrate skill (SKILL.md) — rewrite with new patterns
- prepare-runbook.py — new metadata format (parallelism, context tiers, shared context)
- delegation.md — update for parallel dispatch, prompt deduplication
- Orchestrator plan format — execution order groups, context tier metadata

**Out of scope:**
- Plan-tdd / plan-adhoc skill rewrites
- Worktree-specific orchestration
- vet-fix-agent changes
- Continuation passing integration (preserved — already complete)
- Agent file format changes beyond what's needed for context-as-scope-boundary
