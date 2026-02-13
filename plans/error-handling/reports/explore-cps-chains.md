# Exploration: Continuation-Passing Style in Skill Chains

## Summary

This codebase implements a structured continuation-passing style (CPS) for skill chains that enables sophisticated workflows without script-level control flow. Skills chain together through frontmatter metadata (`default-exit`), explicit continuation metadata (`[CONTINUATION: ...]`), and a tail-call mechanism in the Skill tool. The pattern supports both linear chains (handoff → commit) and dynamic chains with fallback defaults, with careful error isolation and session state management across hops.

---

## Key Findings

### 1. Tail-Call Mechanism

**Location:** All cooperative skills define continuation behavior in YAML frontmatter

**Pattern:**
```yaml
---
name: handoff
continuation:
  cooperative: true
  default-exit: ["/commit"]
---
```

**How it works:**
- **`cooperative: true`** — Skill participates in continuation-passing chains
- **`default-exit: [...]`** — Array of skill commands to invoke if no explicit continuation provided
- **Invocation flow:**
  1. Skill completes its work
  2. Checks for `[CONTINUATION: ...]` suffix in Skill args
  3. If present: parses, peels first entry, invokes next skill with remainder as continuation
  4. If absent: uses `default-exit` array, chains them together

**Example from `/handoff` SKILL.md (lines 304-311):**
```
As the **final action** of this skill:

1. Read continuation from `additionalContext` (first skill in chain)
   or from `[CONTINUATION: ...]` suffix in Skill args (chained skills)
2. If continuation is empty: stop (terminal)
3. Consume first entry as tail-call target
4. Invoke via Skill tool: `Skill(skill: "<target>", args: "<target-args> [CONTINUATION: <remainder>]")`
```

**Syntax rules (from `/handoff` flags documentation):**
- **Flag parsing is exact token match** — `/handoff --commit` has flag, `/handoff describe the commit process` does NOT
- Continuation metadata syntax: `[CONTINUATION: /skill1, /skill2, /skill3]`
- Nested skill args syntax: `/skill args="--flag [CONTINUATION: /next]"`

---

### 2. Default-Exit Chains (Happy Path)

**Location:** Orchestrate skill frontmatter and Handoff skill frontmatter

**Pattern — Orchestrate (lines 1-8):**
```yaml
---
default-exit: ["/handoff --commit", "/commit"]
---
```

**Happy path execution:**
1. Orchestrate completes successfully
2. No explicit `[CONTINUATION: ...]` in incoming args
3. Invokes: `Skill(/handoff args="--commit [CONTINUATION: /commit]")`
4. Handoff completes, peels `/commit` from continuation
5. Invokes: `Skill(/commit)`
6. Commit completes, no continuation, terminal

**From `/orchestrate` SKILL.md (lines 436-439):**
> Incoming: `/orchestrate myplan` (no continuation)
> - Complete orchestration
> - Use default-exit: `["/handoff --commit", "/commit"]`
> - Invoke: `Skill(/handoff args="--commit [CONTINUATION: /commit]")`

**Explicit continuation overrides defaults:**
- Input: `/orchestrate myplan [CONTINUATION: /commit]`
- Skips default-exit, uses explicit continuation instead
- Invokes: `Skill(/commit)` directly

---

### 3. Session State Management During Chains

**Location:** Handoff skill (sections 1-4 protocol)

**State preservation across hops:**

**Before tail-call (Handoff responsibility):**
1. **Gather context from conversation** — Read session.md to detect uncommitted prior handoff (lines 35)
2. **Merge multiple handoffs** — If prior handoff exists in working tree but not committed, append new work to existing sections, don't replace (lines 41-47)
3. **Update session.md incrementally** — Use Edit for section updates, NOT Write, to preserve uncommitted state
4. **Append learnings to learnings.md** — Append-only, never trim (line 153-157)
5. **Run consolidation checks** — Optional memory consolidation with escalation to remember-task agents (lines 169-204)

**Session state is FULLY COMMITTED before tail-call to /commit:**
- Handoff updates session.md and learnings.md
- These files are read-only at tail-call time
- /commit finds them in git index and stages them
- Next agent sees clean state (everything committed)

**From `/handoff` SKILL.md (lines 127-129):**
> When `--commit` flag is used, the tail-call makes commit atomic with handoff — write status assuming commit succeeds

**Critical constraint (line 313):**
> Do NOT include continuation metadata in Task tool prompts. Continuation is for main-agent skill chaining only.

---

### 4. Error Propagation in Skill Chains

**Location:** `/commit` SKILL.md (lines 96-132) and `/handoff` SKILL.md (full protocol)

**Error gates in commit skill (happy path only):**

**Gate A — Session freshness (lines 96-106):**
```
Read agents/session.md
Compare "Completed This Session" against conversation work
If stale: invoke `/handoff --commit` (the flag tail-calls /commit)
If current: proceed to Gate B
```

**Gate B — Vet checkpoint (lines 115-132):**
```
List changed files
Classify: production artifacts?
If none: proceed to validation
If artifacts exist but no vet report: STOP and delegate to vet-fix-agent
If UNFIXABLE issues in report: escalate to user
If no criteria for alignment: escalate to user
```

**Pattern: Escalation stops the chain**
- Gate failure = explicit STOP (no continuation)
- User must intervene before chain can proceed
- Chain is NOT automatically retried

**Contrast with orchestration escalation:**

From `/orchestrate` SKILL.md (lines 161-202):
- Level 1 error (haiku quality check) → delegate to refactor agent (sonnet)
- Level 1b error (file state issues) → delegate to sonnet for fix
- Level 2 error (design decisions) → stop and report to user
- If agent fixes: resume execution (continue with next step)
- If agent escalates: route to opus or user

---

### 5. Explicit Continuation Override Pattern

**Location:** `/orchestrate` SKILL.md (lines 407-441)

**Mechanism:**
- User can invoke: `/orchestrate myplan [CONTINUATION: /commit]`
- Orchestrate parses the continuation list
- Strips it from current context (doesn't process during orchestration)
- Peels first entry at final action
- Passes remainder to next skill

**Example (lines 429-434):**
```
Incoming: `/orchestrate myplan [CONTINUATION: /handoff --commit, /commit]`
- Complete orchestration
- Strip continuation from current context
- Peel first: `/handoff --commit`
- Remainder: `/commit`
- Invoke: `Skill(/handoff args="--commit [CONTINUATION: /commit]")`
```

**Key constraint (line 441):**
> This skill does NOT pass continuations to sub-agents (Task tool). Continuations apply only to the main session skill chain.

---

### 6. Skill Invocation Mechanism

**Location:** Skill tool definition (inferred from SKILL.md patterns) and `/design` SKILL.md (usage patterns)

**Invocation syntax:**
```
Skill(skill: "skillname", args: "arg1 arg2 [CONTINUATION: /next-skill arg]")
```

**Invocation from skills (observed patterns):**
- **Design skill (lines 302-309 in design/SKILL.md):** Tail-calls `/handoff --commit`
- **Handoff skill (lines 307-311):** Tail-calls next from continuation or default-exit
- **Commit skill (line 235-251):** Displays STATUS, no continuation (terminal)
- **Orchestrate skill (lines 403-441):** Consumes continuation, tail-calls next or defaults

**Loading mechanism:**
- Skill tool loads skill from `.claude/agents/<skillname>.md` (or `.claude/skills/` fallback)
- Frontmatter parsed for allowed-tools, requires, continuation metadata
- Skill executed in main session context (sub-agents don't participate in continuation chains)
- Model specified in frontmatter (default: sonnet)

---

### 7. Commit Delegation Pattern

**Location:** `/agent-core/fragments/commit-delegation.md` (complete pattern) and `/commit` SKILL.md

**Pattern motivation:**
- Orchestrator (sonnet) runs git diff analysis, drafts message, analyzes changes
- Delegates to commit agent (haiku) to execute git commands
- Saves ~20-50x tokens per commit (1000+ → 20-50)
- Keeps orchestrator context lean

**Orchestrator responsibilities:**
1. Run git diff HEAD to review changes
2. Analyze what changed and why
3. Check for invalidated learnings
4. Draft commit message (imperative tense, 50-72 chars)
5. Delegate to commit agent with exact message

**Commit agent responsibilities:**
1. Receive literal message from orchestrator
2. Execute: `git add`, `git commit -m "..."`
3. Return: commit hash on success, error message on failure

**Error recovery (lines 269-295):**
```
If commit fails:
  Agent returns detailed error + context
  Orchestrator classifies as execution error
  Escalates to sonnet for resolution
  If sonnet fixes: resume execution
  If unresolvable: escalate to user

If message was wrong:
  Orchestrator reads git log
  Verifies against original diff
  If mismatch: escalate to sonnet
  Sonnet amends commit with correct message
```

---

### 8. Handoff Skill Details

**Location:** `/handoff` SKILL.md (full 325 lines)

**Protocol breakdown:**

**Step 1 — Gather context (lines 30-35):**
- Review conversation to find completed/pending tasks
- Read session.md from working tree
- Detect uncommitted prior handoff (critical)
- Check for blockers/gotchas

**Step 2 — Update session.md (lines 37-57):**
- Merge multiple handoffs (append new work to existing sections if uncommitted prior handoff exists)
- Update Completed This Session, Pending Tasks, Blockers/Gotchas, Next Steps
- Task format: `- [ ] **Task Name** — description | model | restart?`
- 75-150 lines target (complete context without bloat)

**Step 3 — Context preservation (lines 85-129):**
- Preserve specifics that save time: commit hashes, file paths, line numbers, metrics, root causes
- Omit verbose details: step-by-step logs, obvious outcomes, intermediate debugging
- Goal: Next agent understands what happened and why, doesn't need to re-discover

**Step 4 — Write learnings (lines 131-194):**
- Append to agents/learnings.md (never overwrite)
- Extract patterns from completed work
- Run learning-ages.py to check consolidation triggers
- Optional consolidation delegation if ≥7 active days and ≥3 entries

**Step 5 — Session size check (lines 206-217):**
- Run `wc -l agents/session.md agents/learnings.md`
- Provide feedback on sizes

**Step 6 — Update jobs.md (lines 218-230):**
- Transition plan status: designed → planned → complete
- Move completed plans to archive section

**Step 7 — Trim completed tasks (lines 232-256):**
- Rule: Delete ONLY if completed before conversation started AND committed
- Never delete tasks completed in current conversation
- Never delete pending tasks, blockers, next steps
- Extract learnings before deleting

**Step 8 — Display STATUS or skip (lines 258-270):**
- If `--commit` flag NOT provided: Display STATUS with next pending task
- If `--commit` flag provided: Skip (commit will display)

---

### 9. Design → Planning → Execution Chain

**Location:** `/design` SKILL.md (full 340 lines) and `/runbook` SKILL.md (referenced)

**Three-phase workflow:**

**Phase A: Research + Outline (lines 39-148)**
- A.0: Requirements checkpoint (scan for skill dependencies)
- A.1: Documentation checkpoint (memory-index, decisions, fragments, skills)
- A.2: Explore codebase (delegate to quiet-explore agent)
- A.3-4: External research (Context7, WebSearch)
- A.5: Produce plan outline
- A.6: FP-1 checkpoint (outline-review-agent review)

**Phase B: Iterative discussion (lines 151-165)**
- Open outline for user review
- Apply deltas
- Re-review if significant changes
- Loop until convergence (3 rounds max)

**Phase C: Generate design (lines 170-310)**
- C.1: Create design document (dense, binding classifications)
- C.2: Checkpoint commit (preserve design state)
- C.3: Vet design (design-vet-agent review)
- C.4: Check for UNFIXABLE issues
- **C.5: Tail-call `/handoff --commit`** (lines 302-310)

**Critical tail-call (lines 302-310):**
```
As the final action, invoke `/handoff --commit`.

This tail-call chains:
1. `/handoff` updates session.md with completed design work
2. Tail-calls `/commit` which commits the design document
3. `/commit` displays STATUS showing next pending task
```

---

### 10. Orchestration Chain with Checkpoints

**Location:** `/orchestrate` SKILL.md (lines 65-254)

**Step-by-step execution chain:**

**3.1 — Invoke plan-specific agent (lines 69-81):**
```
Task(subagent_type: "<runbook-name>-task",
     prompt: "Execute step from: plans/<runbook-name>/steps/step-N.md")
```
- Model specified in step file header
- Critical: Do NOT default all steps to haiku

**3.2 — Check execution result (lines 83-93):**
- Success indicators: agent returns, report created, no errors
- Failure indicators: agent error, missing report, unexpected results

**3.3 — Post-step verification (lines 95-150):**
```bash
git status --porcelain
```
- If ANY output: **STOP orchestration immediately**
- Never clean up or proceed on dirty tree
- Escalate to user

**Phase boundary check (lines 113-150):**
- Read next step file header, compare Phase field
- Same phase: proceed to 3.4
- Phase changed: delegate to vet-fix-agent for checkpoint
- Checkpoint includes: `just dev` fix, scope declaration (IN/OUT), quality review
- If UNFIXABLE issues: STOP, escalate to user

**3.4 — On success (lines 152-153):**
- Log step completion
- Continue to next step

**3.5 — On failure (lines 156-201):**
- Read error report
- Escalate according to orchestrator plan
- Level 1 (haiku): escalate to refactor agent (sonnet)
- Level 1b (diagnostics): escalate to sonnet
- Level 2 (design decisions): escalate to user

**Completion (lines 244-260):**
- All steps successful: delegate vet-fix-agent, optional TDD process review
- If runbook type is TDD: delegate review-tdd-process
- **Default-exit: `/handoff --commit` → `/commit`**

---

## Patterns: Cross-Cutting Observations

### A. Linear vs. Fallback Default Chains

**Linear explicit continuation:**
- User invokes: `/design myplan` (no continuation)
- Design completes
- Uses default-exit: `["/handoff --commit"]`
- Chains: Design → Handoff → Commit (commit has no default-exit, terminal)

**Fallback default-exit:**
- Skill completes without continuation provided
- Automatically uses frontmatter default-exit array
- Enables predictable workflows without user orchestration
- Example: Every design/orchestrate/handoff ends with commit (unless overridden)

**User override:**
- User invokes: `/orchestrate myplan [CONTINUATION: /commit]`
- Overrides default-exit (which would be `/handoff --commit, /commit`)
- Skips handoff, goes directly to commit
- Useful for re-committing after manual changes

### B. Session State Atomicity

**Guarantee: State is committed before tail-call**
1. Handoff updates session.md, learnings.md, jobs.md
2. Calls for learnings consolidation (optional)
3. All updates written to disk
4. Commit skill reads clean state
5. Commits files atomically in git

**This ensures:**
- Next agent in chain sees consistent state
- No partial updates across hops
- Session.md reflects post-handoff state (not post-commit assumptions)

### C. Error Isolation: No Automatic Recovery

**Handoff/commit chain vs. Orchestration chain:**
- **Handoff/commit:** Gate failure (Gate A stale session, Gate B vet checkpoint) = STOP (user must fix)
- **Orchestration:** Step failure = delegate to sonnet/opus (automatic escalation with recovery attempt)
- Different patterns for different contexts:
  - Interactive chains (handoff→commit) prioritize user control
  - Execution chains (orchestrate→steps) prioritize forward progress with safety gates

### D. Continuation is Main-Session Only

**Constraint (from handoff and orchestrate docs):**
> Do NOT include continuation metadata in Task tool prompts. Continuation is for main-agent skill chaining only.

**Rationale:**
- Sub-agents (Task tool) execute independently
- They have their own session context (not shared)
- Continuation passing requires shared context
- Solution: Pass completion signals via report files + return values

### E. Model Tier Matching

**Design → Planning chains (examples from design/SKILL.md):**
- Design skill: Opus only (deep reasoning required, line 337)
- Outline review: outline-review-agent (Sonnet, fix-all mode)
- Design vet: design-vet-agent (Opus, comprehensive architectural review)

**Orchestration chains (from orchestrate/SKILL.md):**
- Orchestrator: Haiku (mechanical execution, line 1-2)
- Step agents: Model specified per step (lines 81)
- Escalation: Haiku → Sonnet → User
- Vet checkpoint: vet-fix-agent (Sonnet)
- TDD process: review-tdd-process (specialized agent)

---

## Gaps & Unresolved Questions

### 1. Skill Tool Implementation Details

**Missing:** How does Skill tool parse frontmatter and invoke agents?
- CLAUDE.md references "Skill tool" but doesn't specify implementation
- Assume: Tool reads `.claude/agents/<name>.md` or `.claude/skills/<name>/`
- Frontmatter parsing: YAML extraction (observed in prepare-runbook.py patterns)
- Model loading: Default sonnet, override via frontmatter

### 2. additionalContext First Hop

**From handoff protocol (line 308):**
> Read continuation from `additionalContext` (first skill in chain)

**Missing:** How is additionalContext injected?
- Assumption: User input or skill frontmatter default-exit mechanism
- Not documented in skill files
- Relevant for user-initiated chains vs. programmatic chains

### 3. Continuation Parsing Rules

**Documented:** `[CONTINUATION: /skill1, /skill2]` format
**Missing:** Complete parsing specification
- Are commas required?
- Can skills have args? (appears to be yes: `/skill args="..."`)
- What if skill name has special characters?

### 4. Sub-Agent Communication

**Constraint (from handoff line 313, orchestrate line 441):**
> Do NOT include continuation metadata in Task tool prompts

**Missing:** How do sub-agents report completion?
- Assumed: Return values or report files
- Orchestrate reads report files from expected paths
- No back-channel for mid-flight adjustments

### 5. Learning Consolidation Delegation

**From handoff (lines 169-204):**
- Runs learning-ages.py script
- Delegates to remember-task agent if ≥7 days and ≥3 entries
- May trigger memory-refactor agent if file limit hit
- Optional: Non-blocking if error

**Missing:**
- Error handling for remember-task escalations
- What if consolidation triggers contradictions? (mentioned, not fully detailed)
- How often does consolidation actually occur in practice?

---

## Implementation Notes

### Prepare-Runbook Integration

**Location:** `agent-core/bin/prepare-runbook.py` (python script)

**Purpose:** Transform markdown runbooks into execution artifacts
- Input: Runbook file or phase-directory
- Output:
  - `.claude/agents/<name>-task.md` (plan-specific agent)
  - `plans/<name>/steps/step-*.md` (step files)
  - `plans/<name>/orchestrator-plan.md` (orchestration metadata)

**Key detail:** TDD common context injection
```python
DEFAULT_TDD_COMMON_CONTEXT = """## Common Context

**TDD Protocol:**
Strict RED-GREEN-REFACTOR: 1) RED: Write failing test, 2) Verify RED, 3) GREEN: Minimal implementation, 4) Verify GREEN, 5) Verify Regression, 6) REFACTOR (optional)

**Stop/Error Conditions (all cycles):**
STOP IMMEDIATELY if: RED phase test passes (expected failure) • RED phase failure message doesn't match expected • GREEN phase tests don't pass after implementation • Any existing tests break (regression)
```

**Validates:** Phase numbering flexibility (0-based or 1-based)
- Detects starting phase number from first file
- Validates sequential numbering from that base
- Supports mixed TDD (## Cycle) and general (## Step) headers

---

## Files Referenced

### Core Skill Files
- `/Users/david/code/claudeutils-wt/error-handling/agent-core/skills/handoff/SKILL.md` — Handoff protocol, continuation parsing
- `/Users/david/code/claudeutils-wt/error-handling/agent-core/skills/commit/SKILL.md` — Commit gates, vet checkpoint, session freshness
- `/Users/david/code/claudeutils-wt/error-handling/agent-core/skills/orchestrate/SKILL.md` — Orchestration pattern, continuation consumption
- `/Users/david/code/claudeutils-wt/error-handling/agent-core/skills/design/SKILL.md` — Design phases, tail-call to handoff, documentation perimeter

### Supporting
- `/Users/david/code/claudeutils-wt/error-handling/agent-core/skills/runbook/SKILL.md` — Runbook creation, tier assessment, planning phases
- `/Users/david/code/claudeutils-wt/error-handling/agent-core/fragments/commit-delegation.md` — Orchestrator/agent split pattern for commits
- `/Users/david/code/claudeutils-wt/error-handling/agent-core/bin/prepare-runbook.py` — Artifact generation
- `/Users/david/code/claudeutils-wt/error-handling/agent-core/bin/learning-ages.py` — Learning consolidation age calculation

---

## Summary: Happy Path & Failure Modes

### Design → Handoff → Commit (Interactive)

**Happy path:**
1. `/design myplan` completes design
2. Tail-calls: `Skill(/handoff args="--commit [CONTINUATION: /commit]")`
3. `/handoff --commit` updates session.md, learnings.md, jobs.md
4. Tail-calls: `Skill(/commit)`
5. `/commit` gates:
   - Gate A: Session freshness ✓
   - Gate B: Vet checkpoint ✓
6. Stages and commits changes
7. Displays STATUS with next pending task
8. Terminal (no further continuation)

**Failure at Gate A (stale session):**
- Invoke `/handoff --commit` (recursive)
- Handoff re-runs, pulling fresh context
- Tail-calls `/commit` again
- Gate A now passes

**Failure at Gate B (vet report missing/UNFIXABLE):**
- STOP and report to user
- User must provide vet report or manual approval
- Chain does NOT automatically retry

### Orchestrate → Handoff → Commit (Execution)

**Happy path:**
1. `/orchestrate myplan` executes steps sequentially
2. Each step: delegate to plan-specific agent
3. Post-step: verify clean tree
4. Phase boundary: delegate vet-fix-agent if phase changed
5. All steps complete
6. Delegate vet-fix-agent for quality review
7. Optional: delegate review-tdd-process (if TDD runbook)
8. Tail-call: `Skill(/handoff args="--commit [CONTINUATION: /commit]")`
9. Handoff/commit chain proceeds as above
10. STATUS displayed, terminal

**Failure at step execution:**
- Agent reports error
- Escalate based on orchestrator plan (haiku → sonnet → user)
- Sonnet may attempt fix and resume
- If unfixable: STOP and report to user
- User fixes root cause, re-invokes orchestrate (continues from failed step or starts over)

**Failure at post-step verification (dirty tree):**
- `git status --porcelain` shows output
- Immediate STOP (no exceptions)
- Report: "Step N left uncommitted changes: [file list]"
- User must investigate: why did step agent not commit?
- User fixes, re-invokes orchestrate

### Key Invariants

1. **State is committed before tail-call** — Handoff ensures all changes staged/committed
2. **Main-session only** — Continuation passing doesn't cross sub-agent boundaries
3. **Error gates are hard stops** — No automatic recovery in interactive chains
4. **Orchestration escalates intelligently** — Haiku hands off to sonnet/opus for complexity
5. **Explicit overrides defaults** — User can provide `[CONTINUATION: ...]` to bypass defaults
