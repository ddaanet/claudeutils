# Orchestrate Evolution — Design

## Problem

The orchestrate skill assumes a weak (haiku) orchestrator. Many accumulated learnings are band-aids for haiku's inability to recover from dirty trees, failed steps, and unexpected state. The agent caching model doesn't embed design or outline context — orchestrator reads step content and passes it inline, growing context proportionally to step count. No post-step remediation exists (dirty tree = immediate user escalation). The refactor agent lacks quality directives for deslop and factorization.

## Requirements

**Source:** `plans/orchestrate-evolution/orchestrate-evolution-analysis.md` (gap analysis, 7 FR + 3 NFR). Phase B resolved scope: FR-1 deferred, NFR-3 revised (sonnet replaces haiku, not "weak orchestrator preservation"). The inline requirements below supersede the skeletal `plans/orchestrate-evolution/requirements.md`.

**Functional:**
- FR-2: Post-step remediation — resume step agent, fallback to recovery → D-3
- FR-3: RCA task generation — after any remediation → D-3 step 6
- FR-4: Delegation prompt deduplication — plan-specific agents cache design+outline → D-2
- FR-5: Commit instruction in prompts — agent definition footer → D-2
- FR-6: Scope constraint in prompts — structural + prose boundary → D-2
- FR-7: Precommit verification — git status + precommit check → D-3 step 1

**Non-functional:**
- NFR-1: Context bloat mitigation — file references only, never read content → D-2, Principles
- NFR-2: Backward compatibility — clean break, regenerate old plans → Q-4
- NFR-3: Orchestrator model — sonnet replaces haiku, mechanical checks preserved → D-1

**Deferred:**
- FR-1: Parallel step dispatch → `plans/parallel-orchestration/` (requires worktree isolation)

### Requirements Traceability

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-2 | Yes | Post-Step Remediation Protocol (D-3), steps 1-4 |
| FR-3 | Yes | Post-Step Remediation Protocol (D-3), step 3 (RCA task) |
| FR-4 | Yes | Agent Caching Model (D-2), plan-specific agent templates |
| FR-5 | Yes | Agent Caching Model (D-2), "Clean tree requirement" footer |
| FR-6 | Yes | Agent Caching Model (D-2), "Scope enforcement" footer + structural boundary |
| FR-7 | Yes | Verification Script, git status + precommit check |
| NFR-1 | Yes | Orchestrator Plan Format + Key Orchestration Principles (bloat prevention) |
| NFR-2 | Yes | Q-4 resolution: clean break |
| NFR-3 | Yes | D-1: sonnet default, mechanical checks preserved |
| FR-1 (deferred) | N/A | Out of scope: parallel execution deferred to plans/parallel-orchestration/ |

**Out of scope:**
- Planning orchestration (plan-tdd / plan-adhoc stay as independent skills)
- vet-fix-agent behavioral changes
- Continuation passing changes (preserved as-is)

## Architecture

### Orchestrate Skill (SKILL.md rewrite)

The skill shrinks significantly. The current 474-line skill contains verbose examples, weak orchestrator constraints, and haiku-specific patterns. The rewrite targets ~200 lines.

**Execution loop:**

```
1. Verify artifacts (step files, plan-specific agent, orchestrator plan)
2. Read orchestrator plan (step list with metadata)
3. For each step:
   a. Dispatch to plan-specific task agent with step file reference
   b. Run verification script (git clean + precommit)
   c. If dirty: remediate (resume agent or recovery delegation)
   d. If phase boundary: delegate to plan-specific vet agent
4. Completion vet: single-phase uses generic vet-fix-agent with file references; multi-phase already vetted per-phase
5. Cleanup plan-specific agents, continuation protocol
```

**What changes from current skill:**
- Sonnet orchestrator (not haiku) — can handle exceptions inline
- Step dispatch is a file reference, not inline content
- Post-step remediation replaces immediate user escalation
- Phase boundary uses plan-specific vet agent (not ad-hoc vet-fix-agent prompt)
- Error escalation simplifies to sonnet → user (2 levels, not 3)
- Refactor agent invoked for complexity warnings with deslop directives
- Cleanup step deletes plan-specific agents from `.claude/agents/`

**What stays:**
- Sequential execution (one step at a time)
- Continuation passing protocol (cooperative, default-exit chain)
- Progress tracking (step completion logging)
- Mechanical checks (UNFIXABLE grep, git status)

**Skill frontmatter changes:**
- Remove `allowed-tools` constraint (sonnet doesn't need tool restriction — no replacement needed, defaults to all tools)
- Keep continuation configuration (cooperative mode, default-exit chain)

### Agent Caching Model (D-2)

**Principle:** All common context lives in the agent definition. The only non-cached input per step is the step file reference.

**prepare-runbook.py generates two agent types per plan:**

#### `<plan>-task.md` (always generated)

```markdown
---
name: <plan>-task
description: Execute <plan> runbook steps...
model: <from-runbook-frontmatter>
color: blue
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---

[baseline template body — quiet-task or tdd-task]

---

# Plan Context

## Design

[full text of plans/<plan>/design.md]

## Runbook Outline

[full text of runbook outline section OR plans/<plan>/outline.md]

---

# Runbook-Specific Context

[Common Context section from runbook, if any]

---

**Scope enforcement:** Execute ONLY the step file provided in your prompt. Do NOT read or execute other step files. Do NOT read ahead in the runbook.

**Clean tree requirement:** Commit all changes before reporting success. The orchestrator will reject dirty trees — there are no exceptions.
```

**Content source priority for design embedding:**
1. `plans/<plan>/design.md` — always present (created during design phase)
2. Falls back to empty section with note "No design document found"

**Content source for outline embedding:**
1. Runbook `## Outline` section (if present in assembled runbook)
2. `plans/<plan>/outline.md` (if separate file exists)
3. Falls back to empty section

#### `<plan>-vet.md` (multi-phase plans only)

```markdown
---
name: <plan>-vet
description: Review and fix <plan> runbook phase checkpoints...
model: sonnet
color: yellow
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---

[vet-fix-agent baseline body — review protocol, fix protocol, return protocol]

---

# Plan Context

## Design

[full text of plans/<plan>/design.md]

## Runbook Outline

[full text of runbook outline]

---

**Scope enforcement:** Review ONLY the phase checkpoint described in your prompt. Focus on changed files provided. Do NOT flag items explicitly listed as OUT of scope.
```

**Multi-phase detection:** prepare-runbook.py already detects phases (from H3 "Phase N" markers or major cycle number changes). Generate vet agent when phase count > 1.

**Model for vet agent:** Always sonnet. Vet requires reasoning and judgment regardless of implementation model.

#### Single-phase plans: generic vet-fix-agent

Single-phase plans don't get `<plan>-vet.md`. At completion, the orchestrator delegates to the generic `vet-fix-agent` with file references (non-cached):

```
Review all changes from runbook execution.

**Design reference:** plans/<name>/design.md
**Runbook outline:** plans/<name>/outline.md
**Changed files:** [git diff --name-only]

Fix all issues. Write report to: plans/<name>/reports/completion-vet.md
Return filepath or error.
```

The vet-fix-agent reads design and outline on demand. Context is not cached (no plan-specific vet agent), but this is acceptable — single-phase plans have fewer steps, so one non-cached vet invocation at completion is a minor cost.

#### Orchestrator prompt (minimal)

The orchestrator sends only:

```
Execute: plans/<name>/steps/step-N.md
```

For vet checkpoints:

```
Phase N checkpoint.

**Scope:**
- IN: [from orchestrator plan phase summary]
- OUT: [from orchestrator plan phase summary]

**Changed files:** [git diff --name-only output]

Write report to: plans/<name>/reports/checkpoint-N-vet.md
Return filepath or error.
```

The vet agent has design+outline cached — orchestrator doesn't repeat them.

### Orchestrator Plan Format

**Current format:** Prose instructions with step list and phase boundary markers.

**New format:** Structured metadata for mechanical parsing by sonnet orchestrator.

```markdown
# Orchestrator Plan: <runbook-name>

**Agent:** <runbook-name>-task
**Vet Agent:** <runbook-name>-vet (or "none" for single-phase)
**Type:** tdd | general

## Steps

- step-0-1.md | Phase 0 | sonnet
- step-0-2.md | Phase 0 | sonnet
- step-0-3.md | Phase 0 | sonnet | PHASE_BOUNDARY
- step-1-1.md | Phase 1 | sonnet
- step-1-2.md | Phase 1 | sonnet | PHASE_BOUNDARY
- step-2-1.md | Phase 2 | haiku

## Phase Summaries

### Phase 0: Foundation
- IN: [what this phase implements]
- OUT: [what future phases implement]

### Phase 1: Core Implementation
- IN: [what this phase implements]
- OUT: [what future phases implement]
```

**Step list format:** `filename | phase | model [| PHASE_BOUNDARY]`
- PHASE_BOUNDARY marker on last step of each phase
- Model from step file metadata
- Phase from step file metadata

**Phase summaries:** IN/OUT scope for vet checkpoint delegation. Generated from runbook phase descriptions.

**What this eliminates:**
- Prose instructions ("Execute steps sequentially using...")
- Verbose phase boundary instructions
- Example execution patterns
- The orchestrator reads structured data, not prose

### Verification Script

**Location:** `agent-core/skills/orchestrate/scripts/verify-step.sh`

**Contract:**
- Input: None (checks current git state)
- Output: Exit code 0 (clean) or 1 (dirty) + details on stdout
- Checks: `git status --porcelain` + `just precommit`

```bash
#!/usr/bin/env bash
exec 2>&1
set -xeuo pipefail

# Check git status
status=$(git status --porcelain)
if [[ -n "$status" ]]; then
    echo "DIRTY: uncommitted changes"
    echo "$status"
    exit 1
fi

# Check precommit
just precommit || {
    echo "PRECOMMIT: validation failed"
    exit 1
}

echo "CLEAN"
exit 0
```

**Orchestrator invocation:**
```bash
agent-core/skills/orchestrate/scripts/verify-step.sh
```

### Post-Step Remediation Protocol (D-3)

**After each step, orchestrator runs verification script.**

**If clean (exit 0):** Proceed to phase boundary check or next step.

**If dirty (exit 1):**

1. **Resume step agent** — the agent has context for fixing its own issues.
   - Use Task tool `resume` parameter with the agent ID from step dispatch
   - Prompt: "Your step left uncommitted changes or precommit failures. Fix and commit."
   - Skip resume if orchestrator estimates agent context > 100k tokens (heuristic: >15 messages in agent conversation)

2. **If resume fails or skipped:** Delegate recovery to fresh sonnet agent.
   - Recovery agent is a generic sonnet (not plan-specific — recovery is mechanical, goal is lint-clean + git-clean)
   - Prompt includes: step file reference, `git diff`, `git status`, error output from verification
   - Recovery does not need design/outline context — it fixes lint and commit issues, not design alignment

3. **After any remediation:** Append RCA pending task to session.md.
   - Format: `- [ ] **RCA: Step N dirty tree** — [brief description] | sonnet`
   - Purpose: Fix the root cause (agent definition, step spec, or skill) in a future session

4. **If recovery fails:** Escalate to user with full context.

**Context measurement heuristic:** The Task tool doesn't expose token counts. Use message count as proxy: if the step agent exchanged >15 messages (tool calls + responses), skip resume and delegate recovery directly. This avoids resuming into a near-full context window.

**Note:** The outline's D-3 step 5 describes recovery agent receiving "design + outline from task agent." This design narrows that: recovery is mechanical (lint-clean + git-clean), so design/outline context is unnecessary. Recovery agents receive only step file reference, git diff, git status, and error output.

### Refactor Agent Updates

**Current:** 266 lines, focused on complexity warnings and script-first refactoring. No deslop awareness.

**Additions:**

1. **Deslop directives** (add to Refactoring Protocol, before Step 3):

   Before any structural refactoring (splitting, extracting):
   - Remove slop: trivial docstrings, narration comments, premature abstractions, unnecessary guards
   - Factor duplication: extract shared code into helpers, eliminate copy-paste
   - Only THEN consider structural changes (splitting files, extracting modules)

   Rationale: Splitting a sloppy file produces two sloppy files. Deslop first reduces the need for splitting.

2. **Resume pattern** (add to return protocol):

   If refactoring is incomplete (precommit still has warnings after changes):
   - Orchestrator may resume this agent once (if context < 100k / <15 messages)
   - On resume: continue from current state, don't restart analysis
   - If resumed and still cannot fix: return error, orchestrator delegates recovery

3. **Factorization-before-splitting rule** (add to Evaluation section):

   When file exceeds line limit:
   - Step 1: Remove slop (deletion test on every construct)
   - Step 2: Factor duplication (extract helpers for repeated patterns)
   - Step 3: Only if still over limit after steps 1-2, split by functional responsibility

### delegation.md Updates

**Current:** 44 lines covering model selection, quiet execution, tool reminders.

**Changes:**
- Model selection: Remove haiku as default, sonnet is default for execution
- Remove "Never use opus for straightforward execution" (still true but covered by orchestrate skill)
- Add: Orchestrator provides file references, never inline content
- Add: Plan-specific agents cache common context
- Update quiet execution pattern to reference plan-specific agents

### Files Changed

| File | Action | Description |
|------|--------|-------------|
| `agent-core/skills/orchestrate/SKILL.md` | Rewrite | ~200 lines, sonnet orchestrator, new execution loop |
| `agent-core/bin/prepare-runbook.py` | Modify | Embed design+outline in agents, new orchestrator plan format, vet agent generation |
| `agent-core/agents/refactor.md` | Modify | Add deslop directives, factorization rule, resume pattern |
| `agent-core/fragments/delegation.md` | Modify | Update model selection, add file reference pattern |
| `agent-core/skills/orchestrate/scripts/verify-step.sh` | Create | Post-step verification script (new `scripts/` directory under orchestrate skill) |
| `plans/<plan>/orchestrator-plan.md` | Generated | New orchestrator plan format (generated by prepare-runbook.py per plan) |

### Testing Strategy

- **Orchestrate skill:** Manual integration test — regenerate and run against existing runbook (e.g., plugin-migration; requires regeneration per Q-4 clean break)
- **prepare-runbook.py:** Unit tests for design/outline embedding, vet agent generation
- **Verification script:** Unit test with clean/dirty git states
- **Refactor agent:** Manual validation via orchestrated execution
- **delegation.md:** Review-only (documentation)

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agents/decisions/implementation-notes.md` — module patterns, implementation decisions
- `agent-core/fragments/delegation.md` — current delegation patterns (to update)
- `plans/orchestrate-evolution/reports/explore-orchestration-infra.md` — infrastructure details
- `agent-core/skills/orchestrate/SKILL.md` — current skill (to rewrite)
- `agent-core/agents/refactor.md` — current refactor agent (to update)
- `agent-core/bin/prepare-runbook.py` — current script (to modify)

**Skill loading:**
- Load `plugin-dev:agent-development` before planning (agent definition generation)
- Load `plugin-dev:skill-development` before planning (skill rewrite)

## Next Steps

Route to `/plan-adhoc` for runbook generation. This is a general workflow (infrastructure changes, not test-first).

**Execution model:** Sonnet for orchestrate skill rewrite, prepare-runbook.py changes, and refactor agent updates. Opus not required — design decisions are resolved.
