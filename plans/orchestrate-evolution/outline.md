# Orchestrate Evolution — Design Outline

## Approach

Evolve the orchestrate skill into a unified workflow coordinator. Sonnet orchestrator replaces haiku. Orchestrate absorbs both planning orchestration and runbook execution into a single skill with two modes. Structural context boundaries replace prose scope constraints.

The evolution preserves orchestrate's core loop (verify → read plan → execute steps → completion) while adding: planning mode, parallel dispatch, post-step remediation, and tiered recovery.

## Key Decisions

### D-1: Abandon weak orchestration, sonnet default

**Current:** Haiku orchestrator. Many learnings are band-aids for haiku's inability to recover from failures.

**Decision:** Sonnet as default orchestrator model.

**What changes:**
- Orchestrate skill assumes sonnet-level reasoning
- Error escalation: sonnet → user (2 levels)
- Post-step remediation possible (sonnet can commit/fix, not just stop)
- "Delegate, don't decide" relaxed to "delegate execution, handle exceptions"

**What stays the same:**
- Mechanical checks remain mechanical (UNFIXABLE grep, git status, precommit)
- Agents do the work, orchestrator coordinates
- Step files, orchestrator plans, plan-specific agents preserved

### D-2: Orchestrator references files, never reads content

**Current:** Orchestrator reads step file content, passes it in Task prompt. Bloats orchestrator context.

**Decision:** Orchestrator provides file references only. Never reads step file content into its own context.

**Step task context (provided as file references):**
- Full design document
- Runbook outline (for position understanding)
- Step file (the immediate task)

**Orchestrator prompt pattern:**
```
Execute the step defined in: plans/<name>/steps/step-N.md
Design reference: plans/<name>/design.md
Runbook outline: plans/<name>/outline.md
```

**Commit requirement:** Plan-specific agent definitions (created by prepare-runbook.py) include "Clean tree requirement" footer requiring commit before return. Orchestrator prompt doesn't repeat this — it's in the agent definition.

**Scope enforcement:** Orchestrator provides file *references* (paths), not pre-read content. Executing agent can technically read other files if it chooses, but orchestrator doesn't provide them in context, creating natural scope boundary. Prose "execute ONLY this step" constraint recommended as reinforcement in agent definition.

**Rationale:** Prevents orchestrator context bloat across 20+ step executions. Step agents are intelligent enough to load their own context from file references.

**What this eliminates:**
- Orchestrator reading step files
- Orchestrator generating agent prompts with inline content
- Context growth proportional to step count

### D-3: Two-tier context injection

**Tier 1 — Execution:** Step agent gets step file + design path + runbook outline path.

**Tier 2 — Review:** Vet-fix-agent gets step file + design path + runbook outline path + phase file path + changed files.

**Rationale:** Execution needs focus. Review needs breadth for alignment checking.

### D-4: Parallel execution support

**Decision:** First-class parallel dispatch. Orchestrator plan declares parallel groups.

**Format in orchestrator plan:**
```
## Execution Order

### Group 1 (sequential)
- step-0-1 (model: sonnet)

### Group 2 (parallel)
- step-1-1 (model: sonnet)
- step-1-2 (model: sonnet)
- step-1-3 (model: sonnet)

### Group 3 (sequential)
- step-2-1 (model: sonnet)
```

**Behavior:**
- Sequential groups: one Task call per step
- Parallel groups: batch all Task calls in single message
- Phase boundary checkpoints between groups

**prepare-runbook.py:** Emits execution order with explicit grouping based on runbook parallelism annotations.

### D-5: Post-step verify-remediate protocol

**Decision:** Resume step agent first, delegate recovery on failure or context overflow.

**Protocol:**
1. `git status --porcelain` + `just precommit` — if both clean, proceed
2. If dirty: resume step agent to fix and commit (it has context)
3. If step agent context > 100k tokens: skip resume, delegate recovery directly
4. If resumed step agent failed to fix: delegate recovery
5. Recovery agent: sonnet agent with full review-fix context, goal = lint-clean + git-clean
6. After any remediation: generate RCA pending task in session.md
7. If recovery fails: escalate to user

**Verification script:** Write a skill script (part of orchestrate skill directory) for orchestrator to call after each implementation step. Checks git clean + precommit clean efficiently.

### D-6: Plan-specific agents serve as deduplication

**Current concern:** N parallel dispatches = N copies of boilerplate in orchestrator context.

**Resolution:** Plan-specific agents already solve this. They contain cached behavioral rules and common context (from prepare-runbook.py). The step file is the only non-cached element.

Prompt deduplication was only needed when orchestrator followed a custom process (ad-hoc planning orchestration). With plan-specific agents, the agent definition IS the shared context — no separate deduplication mechanism needed.

**Cleanup:** Orchestrate skill includes cleanup as final execution mode action: remove plan-specific agent files from `.claude/agents/`.

### D-7: Simplified error escalation

**Decision:** sonnet → user (2 levels)
- Sonnet orchestrator handles execution-level issues inline (missing files, failed commands, dirty tree)
- Design-level issues escalate to user (wrong approach, scope change, blocking ambiguity)

## Resolved Questions

### Q-1: Planning absorption → Option A + planning orchestration

**Decision:** Orchestrate absorbs planning orchestration as a mode. Planning skills (plan-tdd, plan-adhoc) remain independent but orchestrate coordinates their phases.

"Absorb planning" means orchestrating the planning pipeline (planning mode only):
1. Generate full design from outline
2. Review+fix full design (design-vet-agent)
3. Generate runbook outline from design
4. Review+fix runbook outline (runbook-outline-review-agent)
5. Parallel generation of runbook phases + per-phase review+fix
6. Holistic runbook review+fix
7. prepare-runbook.py (assembly)
8. Display restart instructions and stop (plan-specific agents created, restart required)
9. After user restarts, resume with execution mode (step 9 runs in new session after `/orchestrate` re-invocation)

The orchestrate skill gains two modes:
- **Planning mode:** Orchestrate the design→runbook pipeline
- **Execution mode:** Orchestrate prepared runbook steps (current behavior, enhanced)

### Q-2: Plan-specific agents → Keep with cleanup

**Decision:** Keep plan-specific agents. The design is sound: cached agent behavioral rules and common context (loaded once), non-cached step file (passed per invocation).

Add a cleanup step after orchestration completes: orchestrate skill deletes `.claude/agents/<plan-name>-task.md` as final execution mode action.

### Q-3: Remediation authority → Resume step agent with fallback

**Decision:** Option C — resume original step agent first (it has context for fixing its own issues).

**Fallback conditions:**
- Step agent context > 100k tokens → delegate recovery directly (don't resume)
- Resumed step agent failed to fix → delegate recovery
- Recovery: sonnet agent with full review-fix context, goal = lint-clean + git-clean status

### Q-4: Backwards compatibility → Clean break

**Decision:** No backwards compatibility. New prepare-runbook.py generates new format. Old orchestrator plans must be regenerated.

**Rationale:** No active orchestrator plans need preservation. All in-progress plans can regenerate artifacts cheaply.

## Key Orchestration Principles

These are binding constraints for the design:

**Orchestrator bloat prevention:**
- Orchestrator does not generate agent prompts with inline content — only provides file references
- Orchestrator only reads agent return messages, not report content
- Orchestrator forwards report paths to recovery agents without reading reports itself

**Agent context tiers (what each agent type receives):**

| Agent Role | Design | Runbook Outline (outline.md) | Step File | Phase Outline | Full Runbook (runbook.md) | Changed Files |
|---|---|---|---|---|---|---|
| Design expansion | — | — | — | — | Design outline | — |
| Runbook outline generation | Full design | — | — | — | — | — |
| Runbook phase expansion | Full design | — | — | Their phase outline only | — | — |
| Runbook phase review+fix | Full design | — | — | — | Full runbook.md | — |
| Implementation (execution) | Full design | Runbook outline.md | Their step only | — | — | — |
| Recovery (post-step fix) | Full design | Runbook outline.md | Step file | — | — | `git diff --name-only` |

**Post-step verification:**
- Orchestrator checks git clean + precommit clean after each implementation step
- Script-based (orchestrate skill script) for efficiency
- Complexity fixes (refactor agent) and vet-fix at end of each phase
- Tree must be git-clean and precommit-clean at end of each phase

**Refactor agent behavior:**
- Resume once if complexity errors not fully fixed and context < 100k (same pattern as D-5 step agent recovery)
- If resumed refactor agent fails or context > 100k: delegate recovery
- Must include detailed deslop directives (like quiet-task and tdd-task agent definitions)
- Before splitting files: first remove slop and factor duplication — splitting is last resort after deslop + factorization

## Scope

**In scope:**
- Orchestrate skill (SKILL.md) — rewrite with planning mode + enhanced execution mode + cleanup action
- prepare-runbook.py — new orchestrator plan format with parallel groups and file references
- delegation.md — update for new patterns
- Orchestrator plan format — execution order groups, file reference metadata
- Orchestrate skill verification script — post-step check (git clean + precommit)

**Out of scope:**
- Plan-tdd / plan-adhoc skill rewrites (orchestrate calls them, doesn't rewrite them)
- Worktree-specific orchestration
- vet-fix-agent changes
- Continuation passing integration (preserved — already complete)
