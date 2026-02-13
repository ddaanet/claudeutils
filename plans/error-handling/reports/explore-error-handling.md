# Error Handling Landscape Exploration

**Date:** 2026-02-13
**Scope:** Error handling architecture, patterns, gaps, and failure modes across orchestration, CPS, vetting, and agent recovery systems.

---

## Summary

The codebase has substantial error handling infrastructure with structured patterns for escalation, vet checkpoints, and recovery. Key systems exist for orchestration error classification, UNFIXABLE detection, and prerequisite validation. However, critical gaps remain: hook error handling lacks formalization, CPS tail-call failure recovery is undefined, task list error semantics are missing, and incomplete documentation of failure modes across distributed agent workflows.

---

## Key Findings

### 1. Orchestration Error Handling

**Current State:**
- `/orchestrate` skill implements weak orchestrator pattern with structured escalation (lines 161-201 of SKILL.md)
- Three escalation levels: Haiku→Sonnet (refactor/diagnostic), Sonnet→User
- Error classification taxonomy exists: Prerequisite Failure, Execution Error, Unexpected Result, Ambiguity Error
- Post-step verification: Git status check required after each step (line 102-111)
- Clean tree requirement: "There are no exceptions. Every step must leave a clean tree." (line 111)

**File locations:**
- `/Users/david/code/claudeutils-wt/error-handling/agent-core/skills/orchestrate/SKILL.md` (lines 1-450)
- `/Users/david/code/claudeutils-wt/error-handling/agent-core/fragments/error-classification.md` (lines 1-131)

**Gaps:**
- No formalized protocol for classifying errors AT agent level (agents should classify, but pattern is informal)
- Escalation success criteria undefined: what makes "sonnet fixed it"? No acceptance criteria for recovery
- "Unexpected result but no error" scenario handled (lines 368-371) but recovery is manual escalation only
- Missing: timeout handling for hung agents (mentioned as "if hanging: kill task" but no mechanism)
- No rollback guidance when escalation fails: if sonnet can't fix, what happens to partially-executed steps?

**Failure modes documented:**
- Step leaves uncommitted changes (learned: line 255-257 in learnings.md)
- Multiple steps fail with same error (lines 378-380 in SKILL.md)
- Agent never returns (lines 383-387 in SKILL.md) — detection exists, but recovery not specified

**Example error flow:**
```
Step execution → Agent error → Haiku detects → Escalates to Sonnet
Sonnet diagnostic → If fixable: apply fix, retry step
                 → If not fixable: escalate to user with context
```

---

### 2. CPS (Continuation-Passing) Skill Error Handling

**Current State:**
- Continuation passing protocol defined in `/Users/david/code/claudeutils-wt/error-handling/agent-core/fragments/continuation-passing.md`
- Skills declare `continuation: cooperative: true` and `default-exit` behavior
- Five cooperative skills: `/design`, `/runbook`, `/orchestrate`, `/handoff`, `/commit`
- Default-exit pattern: `["/handoff --commit", "/commit"]` chains completion to commit

**File locations:**
- Continuation protocol: `agent-core/fragments/continuation-passing.md` (lines 1-83)
- Handoff tail-call implementation: `agent-core/skills/handoff/SKILL.md` (lines 1-325)
- Commit skill: `agent-core/skills/commit/SKILL.md` (lines 1-264)

**Gaps:**
- No error handling defined for tail-call chains: what if `/handoff` fails? Does `/commit` execute anyway?
- Continuation parsing errors not specified: malformed `[CONTINUATION: ...]` format — error handling?
- Mid-chain failure recovery: if step 2 of 4 in chain fails, does chain stop or skip failed step?
- `/handoff --commit` → `/commit` is a two-step chain; if handoff succeeds but commit fails, no recovery guidance
- Background agent completion issue documented (classifyHandoffIfNeeded bug, learnings.md line 218-221) with workaround but no formal recovery protocol

**Critical learning (line 286-290 of learnings.md):**
```
Anti-pattern: Launch agent, then try to adjust scope mid-flight via resume
Correct pattern: Partition scope completely before launch
Limitation: Task tool resume requires agent completion; no channel for adjustments
```
This means once a skill is invoked with continuation, cannot adjust midway.

**Failure modes:**
- Background Task crashes with `classifyHandoffIfNeeded is not defined` (v2.1.27-2.1.38)
  - Impact: Work completes but status reporting fails
  - Workaround: Use `run_in_background=true` to avoid broken code path
  - Not fixed: GitHub issues #22087, #22544 remain open
- Pre-commit hook failure during handoff (no guidance what happens next)
- Session file merge conflicts during parallel worktree continuations (documented: line 320-331 in learnings.md)

---

### 3. Task List & TodoWrite Error Handling

**Current State:**
- Session tasks use notation: `- [ ]` (pending), `- [x]` (complete), `- [>]` (in-progress)
- Task metadata: `**Task Name** — description | model | restart?`
- Haiku tasks require execution criteria (handoff SKILL.md lines 59-83)

**File locations:**
- Task notation: `agent-core/fragments/workflows-terminology.md` (lines 78-130)
- Haiku task requirements: `agent-core/skills/handoff/SKILL.md` (lines 59-83)

**Gaps:**
- No error semantics defined: what if task fails during execution? How does it transition?
- No "blocked" state: tasks are pending/complete/in-progress but no "blocked: waiting for user input"
- No rollback: if task partially completes, no protocol to undo and re-queue
- Missing: "task failed" lifecycle state — system uses pending/complete only
- No task error reporting template: how should task errors be recorded back to session.md?

**Example gap:**
If haiku executes a task and returns "This requires design decision", task stays as `- [ ]` pending. No state for "blocked: needs design decision".

---

### 4. Runbook Preparation & Validation Errors

**Current State:**
- `prepare-runbook.py` (970 lines, validated at lines 94-99) normalizes runbook type field
- Default TDD common context injected (lines 47-60) when missing from phase files
- Phase file assembly detects phase gaps (flexible numbering supported, learnings.md line 276-278)
- Error classification taxonomy for runbook generation (runbook/references/error-handling.md)

**File locations:**
- Main script: `agent-core/bin/prepare-runbook.py` (lines 1-970)
- Validation patterns: `agent-core/skills/runbook/references/error-handling.md` (lines 1-125)

**Error categories in generation (error-handling.md):**
- Input validation (design not found, missing TDD sections, unresolved items)
- Cycle generation (empty cycles, circular dependencies, invalid IDs, duplicates, forward dependencies)
- Integration (write permissions, script missing, validation failure)
- Edge cases (single-cycle, all-parallel, all-regressions, very large runbooks >50 cycles)

**Gaps:**
- No execution-time validation: prepare-runbook.py assumes input is valid, no input sanitization
- Recovery mechanisms defined for generation (save to `.draft`, `.partial.md`) but unclear if orchestrator uses them
- Circular dependency detection mentioned as recovery protocol but cycle extraction logic (lines 103-150 in prepare-runbook.py) doesn't show cycle detection
- Error injection test patterns missing: how to test that prepare-runbook.py handles malformed input?

**Failure modes:**
- Malformed frontmatter: if YAML frontmatter parsing fails (lines 73-79), returns empty dict and continues
- Invalid type field: defaults to 'general' with warning to stderr (lines 94-99) — doesn't stop execution
- Phase numbering gaps tolerated but not documented in actual code — learning only (learnings.md)

---

### 5. Agent Crash Recovery

**Current State:**
- Background task crash documented: `classifyHandoffIfNeeded` error (learnings.md lines 218-221, 258-262)
- Recovery pattern: check output files and git diff — agents complete work before crash
- Evidence: 238 crashes across 26 sessions with 100% correlation to `run_in_background=false`
- Workaround: Use `run_in_background=true` (avoids broken code path in Claude Code)

**File locations:**
- Learning entry: `agents/learnings.md` (lines 218-221, 258-262)
- Orchestrate skill reference: `SKILL.md` (lines 383-387) mentions "Check task status" but no detail

**Gaps:**
- No protocol for detecting agent stillborn errors (never executes vs crashes mid-flight)
- No heartbeat/liveness mechanism: orchestrator trusts Task tool status without verification
- Recovery ambiguity: "Check output files" — what if partial output exists? How to verify completeness?
- Crash forensics undefined: how to distinguish "agent crashed before generating report" from "agent generated report and crashed after"?

**Failure modes:**
- Agent outputs nothing + crashes: orchestrator sees "agent failed" but cannot distinguish from "agent never ran"
- Git state after crash: may be partially committed; orchestrator doesn't verify clean tree post-crash
- Continuation loss: if crash occurs during tail-call chain, continuation metadata lost

---

### 6. Vet Escalation & UNFIXABLE Detection

**Current State:**
- UNFIXABLE detection is mechanical grep pattern (vet-requirement.md lines 82-110)
- Three issue statuses: FIXED (applied), DEFERRED (out of scope, non-blocking), UNFIXABLE (blocker)
- Protocol: Read report → grep for UNFIXABLE → STOP if found → escalate to user
- Execution context requirement: Scope IN/OUT prevents false positives from future work
- Vet-fix-agent validates task scope (rejects runbooks, design documents) and applies all fixes

**File locations:**
- UNFIXABLE protocol: `agent-core/fragments/vet-requirement.md` (lines 82-110)
- Vet-fix-agent: `agent-core/agents/vet-fix-agent.md` (lines 1-436)
- Commit skill vet gate: `agent-core/skills/commit/SKILL.md` (lines 115-131)

**Implementation quirks:**
- Agent confabulation learning (learnings.md line 144-148): vet made false "fixes" based on design context, not actual state
  - Root cause: Phase 6 error assumed features from Phase 2 design existed in current code
  - Fix: execution context template + grep UNFIXABLE protocol prevents confabulation
  - But: vet-fix-agent CAN still hallucinate fixes if scope not carefully scoped

**Gaps:**
- UNFIXABLE detection depends on agent writing exactly "UNFIXABLE" — no structured format
- Vet agent may escalate items as UNFIXABLE when they're actually fixable (over-escalation)
- Over-escalation learning (learnings.md line 315-320): agents label straightforward tasks (variable naming, format alignment) as UNFIXABLE when they're pattern-matching problems
- No acceptance criteria for vet fixes: "apply all fixes" assumes all fixes are correct, but vet may:
  - Fix wrong thing (misunderstood requirements)
  - Create new bugs while fixing (side effects)
  - Skip some fixes if uncertain (silent non-completion)

**Failure modes:**
- False UNFIXABLE: agent flags issue as UNFIXABLE, grep stops orchestration, but issue is actually fixable
  - Example: "This requires design decision" (from learnings.md line 315-320) when it's just variable naming
- Silent fix issues: agent reports issue FIXED without actually fixing (says applied but made mistake)
- Confabulation: agent invents fixes based on design context that don't match actual code state
- DEFERRED confusion: user doesn't understand DEFERRED vs UNFIXABLE, panics if DEFERRED items are reported

---

### 7. Hook Error Handling

**Current State:**
- Hook configuration in `.claude/settings.json` and `.claude/hooks/` (claude-config-layout.md)
- Hooks can exit with code 2 and write to stderr for blocking (lines 67-79)
- UserPromptSubmit hooks fire on every prompt with no matcher (implementation-notes.md)
- Hooks do NOT fire in sub-agents; only main session (implementation-notes.md, line 49)

**File locations:**
- Hook configuration: `agent-core/fragments/claude-config-layout.md` (lines 67-79)
- Hook implementation notes: `agents/decisions/implementation-notes.md` (lines 49-50)
- Hook development rules: `.claude/rules/hook-development.md`

**Gaps:**
- No error classification for hook failures: what if hook crashes?
- Hook output error propagation: if hook writes to stderr with exit 2, how does Claude Code handle it?
  - Documented: "User sees [UI message]" but what if UI message exceeds buffer? Truncated? Lost?
- No hook timeout: if hook hangs, does Claude Code wait forever?
- Hook return value validation: if hook returns invalid JSON in `additionalContext`, does it fail silently or crash?
- Hook test patterns missing: how to test that hooks handle errors gracefully?

**Failure modes:**
- Hook crash during UserPromptSubmit: entire prompt handling may fail
- Hook output mismatch: hook script outputs plain text but code expects JSON — silent failure or error?
- Hook execution environment: if hook depends on environment variables, what happens if missing? (no validation shown)

---

### 8. Existing Error-Handling Fragment vs. Gaps

**Current Fragment (`error-handling.md`):**
- Single rule: "Errors should never pass silently"
- Prohibits: `|| true`, `2>/dev/null`, ignoring exit codes
- Exception: token-efficient bash pattern uses `|| true` for expected non-zero exits

**File location:** `agent-core/fragments/error-handling.md` (lines 1-12)

**This fragment covers:**
- Suppressment prohibition (code level)
- Bash error handling (high level)
- Token-efficient pattern exception

**This fragment DOES NOT cover:**
- Agent-level error classification (classify error type before reporting)
- Escalation protocols (when to escalate, to whom)
- Recovery procedures (what to do after escalation)
- Hook error handling (hook-specific errors)
- Task error lifecycle (no task failure state)
- Prerequisite validation (prevention, not just reporting)
- CPS chain failure (tail-call error recovery)
- Agent crash detection (stillborn vs complete-then-crash)
- UNFIXABLE criteria (what makes something unfixable?)
- Vet confabulation (how to prevent agent hallucination)

---

## Patterns Across Error Handling

### 1. Escalation is Bidirectional

Errors flow up (agent → haiku → sonnet → user) and down (user input → sonnet → agent retry).

**Pattern observation:** No documented midway recovery. Once escalated, must wait for user decision or sonnet diagnostic. No "escalate and continue with fallback plan".

### 2. Mechanical Detection Preferred

Learnings.md (line 241-248): UNFIXABLE grep is mechanical, not judgment-based. Weak orchestrator pattern requires mechanical checks.

**Implication:** Error handling must be pattern-matchable (grep-able), not requiring reasoning.

### 3. Execution Context is Critical

Vet-requirement.md (lines 67-75): Without execution context (Scope IN/OUT), vet confabulates issues from future work.

**Implication:** Error handling quality depends on caller providing context. Errors escalate if context missing.

### 4. Clean Tree is Hard Requirement

Orchestrate skill (line 111): "There are no exceptions." Every step must leave clean tree.

**Implication:** Errors that leave dirty tree are STOP-and-escalate, not recoverable.

### 5. Prevention > Recovery

Prerequisite-validation.md (lines 162-234): Prerequisite validation during planning catches ~80% of execution errors.

**Implication:** Early validation is preferred over error recovery. But no enforcement mechanism exists.

---

## Critical Gaps Summary

| Gap | Impact | Severity | Workaround | Ideal Solution |
|-----|--------|----------|-----------|----------------|
| **Task failure state missing** | No "blocked" or "failed" task state; pending/complete only | Medium | Use session.md blockers section for failures | Add task status field: pending/in-progress/blocked/failed/complete |
| **CPS chain failure undefined** | If `/handoff --commit` fails, unclear if `/commit` executes | High | Use `--context` flag to skip discovery; manually commit if needed | Formalize tail-call error handling: retry failed step, skip to next, or abort |
| **Hook error propagation unclear** | Hook crash/invalid output behavior undefined | Medium | Test hooks in main session before deployment | Document hook error states: crash, timeout, invalid output |
| **Agent classification informal** | Agents should classify errors but pattern is loose | Medium | Require prompt to include error classification template | Provide error classification skeleton in task prompts |
| **Vet over-escalation** | Agents label fixable items as UNFIXABLE | Medium | Provide existing pattern examples to vet (variable naming, format standardization) | Add "pattern library" to vet prompt showing solved examples |
| **Recovery criteria absent** | "sonnet fixed it" undefined: how to verify? | High | Manual review of diffs after escalation retry | Define acceptance criteria for escalation recovery (tests pass? git clean? output validates?) |
| **Rollback undefined** | If escalation fails partway, no guidance to undo | High | Manual git reset or step retry | Document rollback strategy: revert to step start, clean git, retry with adjusted approach |
| **UNFIXABLE format loose** | Grep for string "UNFIXABLE" — fragile to typos | Low | Grep is sufficient for MVP; brittle but works | Vet agent should write structured JSON: `{status: "UNFIXABLE", reason: "...", requires: "user-input"}` |
| **No task timeout** | Long-running tasks hang orchestrator indefinitely | High | Use TaskOutput tool to check status; manually kill | Add timeout configuration to orchestrate step (default: 30min) with escalation on timeout |
| **Prerequisite validation not enforced** | Planning can skip validation; execution doesn't verify | Medium | Use prerequisite-validation.md as manual checklist | Script-enforce prerequisite validation in plan-reviewer (required section, automated checks) |

---

## Detailed Failure Mode Analysis

### Failure Mode: Mid-Chain CPS Collapse

**Scenario:**
```
User: "/design plans/foo, /runbook, /orchestrate, /handoff --commit, /commit"
→ /design succeeds
→ /runbook succeeds
→ /orchestrate succeeds, 10 steps, step 7 fails escalation to sonnet
→ Sonnet diagnostic fails to resolve (UNFIXABLE escalated to user)
→ User makes decision, but...
```

**Problem:** At this point, continuation chain is orphaned. `/handoff --commit` and `/commit` are waiting in the [CONTINUATION: ...] suffix but:
- No mechanism to resume chain from step 8
- User must manually restart workflow or invoke `/commit` directly
- Session.md may be stale (handoff never ran)

**Current behavior:** User escalation documentation in SKILL.md says "provide error context" but doesn't say "chain is broken, invoke /handoff --commit to continue".

**Ideal:** After user fixes issue, automatically resume: `Skill(/handoff args="--commit [CONTINUATION: /commit]")`.

---

### Failure Mode: Vet Confabulation During Phase Checkpoints

**Scenario (from learnings.md line 144-148):**
```
Orchestrate step 6 (final phase) of plugin-migration
Checkpoint delegates to vet-fix-agent with full design.md context
Vet sees "Plugin class should have X method" in Phase 2 design
Vet assumes method doesn't exist, "fixes" by adding method
Reports "FIXED: Added method X to Plugin class"
Orchestrator trusts report, continues
Later test discovers method was already there; refactor broke it
```

**Root cause:** Execution context provided design reference (full), but didn't specify Scope OUT (future phases).

**Pattern:** Vet-fix-agent can confabulate if given too much context without explicit scoping.

**Mitigation (current):** Execution context template requires Scope IN/OUT. But vet agent may ignore it or misinterpret it.

**Better:** Script-validate execution context in orchestrate skill before delegating:
```
IF Scope IN provided AND Scope OUT provided:
  Constrain vet agent prompt: "Do NOT flag items matching: [Scope OUT list]"
ELSE IF Scope missing:
  Warn orchestrator: "Execution context incomplete; vet confabulation risk"
```

---

### Failure Mode: Background Agent Crash with Partial Output

**Scenario (from learnings.md line 218-262):**
```
Task(run_in_background=false) → Agent executes step, writes report to disk
→ Agent returns result + calls classifyHandoffIfNeeded()
→ Crash: ReferenceError: classifyHandoffIfNeeded not defined
→ Claude Code never sends status back to orchestrator
Orchestrator: "Agent returned nothing; assume failure"
Reality: Agent completed work; just crashed reporting status
```

**Detection problem:** Orchestrator cannot distinguish:
- Agent never started (stillborn)
- Agent crashed mid-execution (partial output)
- Agent completed + crashed on status reporting (success masked as failure)

**Current detection:** None formalized. Learning says "check output files and git diff" but orchestrator doesn't do this.

**Better:** Orchestrate skill post-step should:
1. Check for report file (expected at known path)
2. If report exists: assume agent succeeded (ignore crash)
3. If no report: escalate as execution error

---

### Failure Mode: Hook Silent Failure

**Scenario:**
```
UserPromptSubmit hook defined with additionalContext injection
Hook script has syntax error: `echo $UNDEFINED_VAR | jq` fails
Hook returns nothing (empty string)
Claude Code receives empty additionalContext (or invalid JSON)
```

**Expected behavior:** Hook error should be visible, session should pause.

**Actual behavior:** Unknown. No documentation of how Claude Code handles invalid hook output.

**Gap:** No error contract for hooks. No testing pattern shown.

---

### Failure Mode: Clean Tree Assertion Violation

**Scenario (from learnings.md line 255-257):**
```
Orchestrate step 5 executes, generates test files, returns "success"
Orchestrator checks: git status → Shows untracked test_new_feature.py
Orchestrator: STOP, report "Step 5 left uncommitted changes"
User must either:
  - Commit manually + restart orchestrate
  - Fix step agent + retry
```

**Current handling:** Hard stop, escalate to user.

**Gap:** No recovery path. User must manually decide: "was this expected? should I commit? should I undo?"

**Better:** Provide options:
1. Automatically commit (if step didn't specify required clean tree)
2. Delegate to sonnet for cleanup + recommit
3. Escalate to user with "commit/revert/skip?" options

---

## Recommendations for Error Handling Framework Design

### Priority 1: CPS Chain Error Recovery (High Risk)

Define protocol:
1. Each skill must return error status: `{status: "success"|"error"|"partial", error?: {code, message, context}}`
2. If any skill in chain returns error:
   - Record error to session.md Blockers section
   - Preserve remaining continuation (don't discard)
   - Offer user: retry failed step, skip to next, or abort chain
3. Document recovery paths for common failures (handoff merge conflicts, commit message validation)

### Priority 2: Task Failure Lifecycle (Medium Risk)

Add task states to session.md:
- `- [ ]` pending
- `- [>]` in-progress
- `- [x]` complete
- `- [!]` blocked: [reason] (new)
- `- [✗]` failed: [reason] (new)

When task fails: record reason in failed state, don't discard.

### Priority 3: Escalation Acceptance Criteria (High Risk)

Define what "sonnet fixed it" means:
1. Test suite passes? Or just "compilation succeeds"?
2. Git tree is clean? (orchestrator already checks this)
3. Output validates against acceptance criteria? (runbooks only?)
4. Vet report shows no new UNFIXABLE issues?

Document per-error-type acceptance criteria.

### Priority 4: Vet Agent Pattern Library (Medium Risk)

Augment vet-fix-agent prompt with pattern examples:
- Variable naming: show 5 examples of consolidation decisions
- Test file alignment: show 3 examples of file organization choices
- Format standardization: show 2 examples of accepted trade-offs

Goal: Reduce agent uncertainty → fewer false UNFIXABLE escalations.

### Priority 5: Prerequisite Validation Enforcement (Medium Risk)

Script-enforce in plan-reviewer step:
1. Check: Plan has "Prerequisites" section? (required)
2. Check: Each prerequisite has verification method? (required)
3. Run: Verification commands from plan (bash checks, Read/Glob tests)
4. Report: Failed prerequisites BEFORE orchestration starts

---

## Implementation Notes

### Error Handling Fragment Expansion

Current `error-handling.md` should be expanded to cover:

1. **Agent-level classification** (section 2: "Error Classification")
   - Prerequisite failure, Execution error, Unexpected result, Ambiguity error
   - Template for agents to use

2. **Escalation paths** (section 3: "Escalation Paths")
   - Haiku → Sonnet → User flow
   - Decision trees for each error type

3. **Recovery protocols** (section 4: "Recovery Procedures")
   - Acceptance criteria for escalation resolution
   - Rollback procedures for partial execution

4. **Hook errors** (section 5: "Hook Error Handling")
   - Hook failure modes (crash, timeout, invalid output)
   - Expected behavior per failure mode

5. **Task lifecycle** (section 6: "Task Failure States")
   - blocked, failed states added to session.md
   - Transition rules (pending → blocked → pending or → failed → abandoned)

### New Fragments Needed

- `agent-core/fragments/escalation-acceptance.md` — Define success criteria for escalation recovery
- `agent-core/fragments/hook-error-handling.md` — Hook failure modes and recovery
- `agent-core/fragments/task-failure-recovery.md` — Task lifecycle including failure states

### Orchestrate Skill Updates

- Add timeout configuration to step execution (line 74-79)
- Add clean-tree post-crash verification (line 385-387)
- Add execution context validation before vet delegation (line 127)
- Document recovery path for dirty tree (line 102-111)

---

## File Cross-References

| Topic | Primary | Secondary |
|-------|---------|-----------|
| Error classification | `error-classification.md` | `prerequisites.md` |
| Orchestration escalation | `orchestrate/SKILL.md` | `delegation.md` |
| CPS tail-call | `continuation-passing.md` | `handoff/SKILL.md`, `commit/SKILL.md` |
| Vet escalation | `vet-requirement.md` | `vet-fix-agent.md`, `commit/SKILL.md` |
| Runbook errors | `runbook/references/error-handling.md` | `prepare-runbook.py` |
| Hook errors | `claude-config-layout.md` | `.claude/rules/hook-development.md` |
| Task lifecycle | `workflows-terminology.md` | `handoff/SKILL.md` |
| Agent crash | `learnings.md` | `orchestrate/SKILL.md` |

