# Exploration: Orchestration Infrastructure

## Summary

The orchestration infrastructure consists of three core subsystems: (1) **prepare-runbook.py** — a build-time tool that transforms markdown runbooks into execution artifacts (plan-specific agents, step files, orchestrator plans), (2) **Task delegation pattern** — execution agents (quiet-task, tdd-task) that run steps in isolated contexts and report to files, (3) **Vet-fix-agent** — a review+fix agent that validates changes and applies all corrections automatically. The current design is asynchronous fire-and-forget with weak (haiku) orchestrators, relying on scripted state machines and deterministic patterns rather than real-time adaptation.

## Key Findings

### 1. prepare-runbook.py — Artifact Generation

**Location:** `/Users/david/code/claudeutils/agent-core/bin/prepare-runbook.py` (970 lines)

**Input:** Markdown runbook with frontmatter + H2 sections (Steps or Cycles)

**Output artifacts:**
1. **Plan-specific agent** → `.claude/agents/<runbook-name>-task.md`
   - Frontmatter: name, description, model (from runbook metadata)
   - Body: baseline agent (quiet-task or tdd-task) + Common Context section from runbook
   - Injected contract: "Commit all changes before reporting success. The orchestrator will reject dirty trees — there are no exceptions."

2. **Step/Cycle files** → `plans/<runbook-name>/steps/step-X-Y.md`
   - Uniform naming: `step-{major}-{minor}.md` for TDD cycles, `step-{N.M}.md` for general steps
   - Header metadata: Plan path, Execution Model, Phase number, Report Path (optional)
   - Content: Full step/cycle spec from runbook
   - Phase extracted from H3 "Phase N" markers in runbook or inferred from major cycle number

3. **Orchestrator plan** → `plans/<runbook-name>/orchestrator-plan.md`
   - Default: Sequential step execution instructions
   - TDD-specific: Phase boundary markers with checkpoint instructions
   - Custom: Can be provided in runbook as "## Orchestrator Instructions" section

**Key mechanisms:**

- **Phase-grouped assembly** (lines 398-483): Detects `runbook-phase-*.md` files, validates sequential numbering, assembles into single markdown with metadata injection
- **Frontmatter injection for TDD** (line 463-469): Adds YAML frontmatter when phases lack it
- **DEFAULT_TDD_COMMON_CONTEXT** (lines 47-60): Injected when TDD phases don't provide Common Context — provides standard stop/error conditions (RED fails, GREEN passes, regression checks)
- **Validation layers**:
  - Cycle numbering (fatal: duplicates, wrong start)
  - Phase numbering (fatal: non-monotonic decrease; warning: gaps)
  - Cycle structure (fatal: missing RED/GREEN phases; warning: missing dependencies/conditions)
  - File references (warning: non-existent paths; skips report paths and creation patterns)

**Contract enforcement:**
- Cycles must have RED/GREEN sections (except spike cycles 0.x and regression markers)
- Stop/Error Conditions required in each cycle OR inherited from Common Context
- Phase numbers must not decrease (enforced in general runbooks)
- Cycle numbers must be unique and sequential (per major) or gaps warn but don't fail

### 2. Plan-Specific Agents — Context Injection & Execution

**Example:** `/Users/david/code/claudeutils/.claude/agents/worktree-skill-task.md`

**Structure:**
- Frontmatter: `name`, `description` (references runbook), `model`, `color`, `tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]`
- Baseline body: **tdd-task.md or quiet-task.md** — ~300 line protocol definitions
- Appended context: "# Runbook-Specific Context" section with Common Context from runbook
- Enforced contract: Clean tree requirement (bottom of agent)

**Baseline agents:**

**quiet-task.md** (143 lines) — General execution agent:
- Role: Execute assigned tasks using available tools; "do what has been asked; nothing more, nothing less"
- When to proceed: All info available, scope clear, no blockers
- When to stop: Missing info, unexpected results, errors, ambiguity, out-of-scope work
- Tools: Read, Edit, Write, Glob, Grep, Bash (with constraints: no file ops via Bash, use specialized tools)
- Constraints: Never create files unless required; prefer editing; absolute paths only; no estimates without request
- Verification: Confirm through appropriate checks (tests, builds, file contents)
- Response: Success (brief report 3-5 sentences) or Error (what failed, error details, expected vs observed)

**tdd-task.md** (328 lines) — TDD cycle execution agent:
- Role: Execute RED/GREEN/REFACTOR cycles following strict TDD methodology
- RED protocol: Write test exactly as spec → run suite → verify failure matches → handle unexpected pass (regression vs blocker)
- GREEN protocol: Write minimal implementation → run suite → verify passes → run full suite (regression check) → handle individually
- REFACTOR protocol: Format & lint → WIP commit → precommit validation → escalate if warnings → log entry → amend commit → sanity check
- Stop conditions: RED unexpected pass (not regression), GREEN fails after 2 attempts, refactoring fails precommit, architectural refactoring needed, new abstraction proposed
- Response protocol: Execute → verify → write log → report (success, quality-check, blocked, error, refactoring-failed)
- Critical: Commit all work per cycle; never batch refactoring fixes; no error suppression
- Tool constraints: Use absolute paths, heredocs for multiline messages, specialized tools over Bash, no suppression patterns

**Execution isolation:**
- Each cycle/step gets fresh context (no accumulation from previous)
- Agent is bound to step file at execution time
- Tree must be clean before starting
- Report written to specified Report Path in step metadata

### 3. Orchestrator Plan Format

**Location examples:**
- `/Users/david/code/claudeutils/plans/worktree-skill/orchestrator-plan.md` (99 lines, TDD-heavy)
- `/Users/david/code/claudeutils/plans/plugin-migration/orchestrator-plan.md` (6 lines, minimal)

**Minimal format:**
```markdown
# Orchestrator Plan: {runbook-name}

Execute steps sequentially using {runbook-name}-task agent.

Stop on error and escalate to sonnet for diagnostic/fix.
```

**TDD-enhanced format:**
```markdown
# Orchestrator Plan: {runbook-name}

Execute steps sequentially using {runbook-name}-task agent.

Stop on error and escalate to sonnet for diagnostic/fix.

## Step Execution Order

## Step 0-1 (Cycle 0.1)
## Step 0-2 (Cycle 0.2)
...
## Step 0-9 (Cycle 0.9) — PHASE_BOUNDARY
[Last cycle of phase 0. Insert functional review checkpoint before Phase 1.]

## Step 1-1 (Cycle 1.1)
...
```

**Phase boundary markers:**
- Added by prepare-runbook.py for TDD runbooks (line 745-747)
- Detect when next cycle's major number changes
- Include instruction: "Insert functional review checkpoint before Phase N+1"
- Enable manual pause points for human validation

### 4. Step File Format

**Location:** `plans/<runbook-name>/steps/step-{N.M}.md` (TDD) or `step-{major}-{minor}.md` (general)

**Structure (generated by prepare-runbook.py):**

```markdown
# Cycle X.Y (or Step X.Y)

**Plan**: `{runbook-path}`
**Execution Model**: {model}
**Phase**: {phase-number}
**Report Path**: `{optional-report-path}`

---

## [Cycle/Step description and spec]

## RED Phase
[Test spec, expected failure, verification command]

## GREEN Phase
[Implementation spec, expected behavior, verification commands]

## REFACTOR Phase (TDD only)
[Quality checks, refactoring guidance]

---

**Expected Outcome**: ...
**Error Conditions**: ...
**Validation**: ...
**Success Criteria**: ...
**Report Path**: ...

---
```

**Metadata extraction (prepare-runbook.py lines 541-574):**
- `**Execution Model**: {model}` → regex search, normalized lowercase, validated against {haiku, sonnet, opus}
- `**Report Path**: {path}` → optional, regex search with backtick tolerance
- Phase number extracted from content header or inferred from cycle major number
- Default model: haiku (unless overridden in step content)

**Contract:**
- Step files are PRIMARY SOURCE for execution (orchestrator reads each step before delegating)
- Metadata headers guide model tier and report location
- Common Context from runbook provides shared design decisions + stop conditions
- Step isolation: No carrying state between steps (each cycle reads fresh spec)

### 5. Delegation Fragment (44 lines)

**Location:** `/Users/david/code/claudeutils/agent-core/fragments/delegation.md`

**Scope:** Governs orchestration coordination (not interactive work).

**Key patterns:**

1. **Orchestrator role:** Dispatch, monitor, synthesize (doesn't implement)
2. **Model selection:**
   - Haiku: Execution, implementation, simple edits, file operations
   - Sonnet: Default for most work
   - Opus: Architecture, complex design only
   - Never opus for straightforward execution

3. **Pre-delegation checkpoint:**
   - Verify model matches stated plan
   - State reason explicitly if changing model

4. **Quiet execution pattern:**
   - Agent writes detailed output to file (no context bloat)
   - Agent returns ONLY: filepath (success) or error message (failure)
   - Use second agent to read report if summary needed
   - Output locations: `plans/[plan]/reports/` (execution), `plans/reports/` (persistent research), `tmp/` (ephemeral)

5. **Task agent tool usage:**
   - Grep not grep/rg, Glob not find, Read not cat/head/tail, Write not echo, Edit not sed/awk

**Gap:** Fragment assumes existing orchestrate skill but doesn't define its interface.

### 6. Execution Routing Fragment (26 lines)

**Location:** `/Users/david/code/claudeutils/agent-core/fragments/execution-routing.md`

**Scope:** Interactive agent decision-making (not orchestration).

**Route decision tree:**
1. Examine work first
2. Do directly if feasible (Read, Edit, Write, Bash)
3. Use project recipe if exists
4. Delegate ONLY when isolated context or different model needed

**When to delegate:**
- Runbook step execution
- Parallel independent tasks
- Different model tier
- Specialized agents (vet, design review)

**When NOT to delegate:**
- Reading files to understand
- Few edits across known files
- Running recipes or short bash
- Answering questions about code you can read

**Principle:** Delegation is for runbook orchestration and parallel execution, NOT default mode.

### 7. Vet-Fix-Agent (430 lines)

**Location:** `/Users/david/code/claudeutils/agent-core/agents/vet-fix-agent.md`

**Model:** Sonnet (requires reasoning and judgment)

**Role:** Code review agent that both identifies issues AND applies ALL fixes. Reviews changes, writes detailed report, applies all fixable issues (critical, major, minor), returns report filepath.

**Review scope:**
- Implementation changes only (code, tests)
- Rejects runbooks (wrong agent type), design docs (design-vet-agent), requirements
- Input: Changed file list, NOT git diff text
- Requires: Requirements context (FR/NFR) + execution context (Scope IN/OUT, changed files, prior state, design reference)

**Validation layers:**

1. **Task scope:** Rejects runbooks and design docs explicitly
2. **Requirements context:** Must be provided; if missing, note in report "Requirements validation skipped"
3. **Execution context:** Should include Scope IN/OUT to prevent confabulating issues from future work; if missing, review all changed files
4. **Code quality:** Logic, error handling, clarity, abstractions, debug code, docstrings, comments, duplication, patterns
5. **Project standards:** Conventions, style, dependencies, CLAUDE.md compliance
6. **Security:** No secrets, input validation, vulnerabilities
7. **Testing:** Coverage, behavior verification, edge cases, meaningful assertions
8. **Documentation:** Comments (why not what), updated docs, commit messages
9. **Completeness:** TODOs addressed, no debug code, related changes included
10. **Requirements validation:** If context provided, verify FRs satisfied, NFRs addressed
11. **Design anchoring:** If design reference provided, verify implementation matches decisions (not just requirements)
12. **Alignment:** Compare implementation behavior against requirements summary
13. **Integration review:** Cross-file duplication, pattern consistency, error handling consistency
14. **Runbook file references:** Extract all paths, verify existence, check test function names
15. **Self-referential modification:** Flag if steps modify their own plan directory (breaks re-execution)

**Review structure:**

```markdown
# Vet Review: [scope]

**Scope**: [What was reviewed]
**Date**: [ISO timestamp]
**Mode**: review + fix

## Summary
[2-3 sentences, Overall Assessment: Ready / Needs Minor / Needs Significant]

## Issues Found

### Critical Issues
1. **[Title]**
   - Location: [file:line or commit]
   - Problem: [What's wrong]
   - Fix: [What to do]
   - Status: [FIXED / UNFIXABLE — reason]

### Major Issues / Minor Issues

## Fixes Applied
[Summary of changes made with file:line references]

## Requirements Validation
| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1 | Satisfied/Partial/Missing | [evidence] |
**Gaps:** [Requirements not satisfied]

## Positive Observations
[What was done well]

## Recommendations
[High-level suggestions]
```

**Fix protocol:**
1. Read file containing issue
2. Apply fix using Edit tool
3. Update review report: mark as FIXED with description
4. If fix unsafe/ambiguous, mark UNFIXABLE with reason
5. Fix ALL issues regardless of priority
6. Each fix: minimal, targeted, no scope creep
7. No slop: no trivial docstrings, narration comments, premature abstractions

**Return protocol:**
- Success: ONLY filepath (relative or absolute)
- Failure: Structured error (Error, Details, Context, Recommendation)
- Do NOT provide summary in return message (file contains all details)

**Verification before return:**
1. Review file created successfully
2. All issues have Status (FIXED or UNFIXABLE)
3. Fixes Applied section lists all changes
4. Assessment reflects post-fix state

### 8. Delegation Contracts & Patterns

**Quiet execution pattern (delegation.md):**
- Specify output file path in task prompt
- Agent writes detailed output to file
- Agent returns ONLY: filepath or error
- Orchestrator reads report independently (second agent if summary needed)
- Token efficiency: Avoids context bloat from large reports

**Clean tree requirement (prepare-runbook.py line 803):**
- Injected into all plan-specific agents
- "Commit all changes before reporting success"
- Orchestrator rejects dirty trees (no exceptions)
- Enforces deterministic state transitions

**Report paths:**
- Execution reports: `plans/[plan-name]/reports/`
- Persistent research: `plans/reports/`
- Ephemeral scratch: `tmp/`

**Task tool signature (inferred):**
```
Task(
  name: str,  # Agent name (.claude/agents/foo-task.md)
  description: str,  # Task prompt
  model: str  # 'haiku', 'sonnet', 'opus'
)
```

## Patterns & Architecture

### Artifact Generation Pipeline

```
Markdown runbook (with phases or single file)
  ↓
prepare-runbook.py parses frontmatter + sections
  ↓
Phase assembly (if phase files) + validation
  ↓
Extract Common Context, Steps/Cycles, Orchestrator
  ↓
Generate outputs:
  - .claude/agents/{name}-task.md (baseline + common context)
  - plans/{name}/steps/step-*.md (metadata headers + content)
  - plans/{name}/orchestrator-plan.md (default or custom)
```

### Execution Model

```
Orchestrator (interactive agent or skill)
  ↓ reads orchestrator-plan.md
  ↓ for each step in order:
    - Read step file (plans/.../steps/step-*.md)
    - Delegate to Task agent with step file path
      ↓
      Task agent reads step + runs execution
      ↓
      Writes report to Report Path
      ↓
      Commits changes (clean tree enforced)
      ↓
      Returns filepath or error
    - Grep report for UNFIXABLE (mechanical check)
    - If UNFIXABLE: STOP and escalate
    - If dirty tree: Resume or escalate
    - Continue to next step
```

### Context Isolation

**Per-step isolation:**
- Each step gets fresh context (no accumulation)
- Agent reads step file at execution time (primary source)
- Common Context provides shared knowledge (design decisions, conventions, stop conditions)
- Step file metadata guides model tier and report location

**Context sources:**
1. **System prompt** — Baseline protocol (quiet-task/tdd-task)
2. **Agent frontmatter** — Name, model, tools, color
3. **Step file header** — Plan path, execution model, phase, report path
4. **Step file body** — Complete spec (RED/GREEN/tests/implementation)
5. **Common Context** — Design decisions, conventions, stop conditions, dependencies

### State Management

**Clean tree requirement enforces state transitions:**
- Dirty tree: Agent failed to commit or incomplete work
- Orchestrator rejects immediately (no attempt to continue)
- Forces explicit handling: Resume or escalate
- Prevents accumulation of uncommitted changes

**Runbook state tracking:**
- Session.md tracks execution progress across runs
- Worktree Tasks section separates independent execution
- Pending Tasks section tracks work not yet started
- Can resume from phase boundaries or specific cycles

### Model Tier Strategy

**Current:** Haiku execution default (cost optimization)
- Assumes straightforward implementation tasks
- Uses sonnet for diagnostic/fix on errors
- Opus for architecture decisions only

**Weaknesses (per learnings.md):**
- Haiku fails at recovery (dirty tree, unexpected state)
- Many orchestration band-aids compensate for haiku limitations
- Sonnet now default for orchestration (more robust)

## Gaps & Unresolved Questions

1. **Orchestrate skill undefined** — delegation.md references `/orchestrate` but its interface isn't documented. How does orchestrator load step files? How does it handle errors? How is model tier determined at runtime?

2. **Phase boundary handling undefined** — TDD orchestrator plan marks phase boundaries with "Insert functional review checkpoint before Phase N+1" but this is prose instruction only. How should orchestrator pause/resume? Is this manual or automated?

3. **Error escalation model undefined** — "Stop on error and escalate to sonnet for diagnostic/fix" in orchestrator plan is instruction-only. No defined Task interface for diagnostic agents or recovery flow.

4. **Quiet execution assumes second agent** — Delegation.md says "Use second agent to read report and provide summary if needed" but doesn't specify when/how this is triggered. Are summaries automatic or user-requested?

5. **Model tier mismatch detection** — No mechanism to detect if step specifies model different from agent model, or what happens if they conflict.

6. **Step file reading contract unclear** — prepare-runbook.py generates step files with metadata headers, but doesn't specify how orchestrator should parse them (regex? markdown parsing? just read full file?).

7. **Report path validation absent** — prepare-runbook.py validates file references exist, but doesn't validate that report paths are writable or in valid locations. Could steps specify invalid report paths?

8. **No checkpoint restart** — Phase boundaries are marked in orchestrator plan but there's no mechanism to load state from a phase and resume from that checkpoint (would require session.md integration).

9. **Parallel execution unsupported** — Current orchestrator is sequential (execute steps one-by-one). No Task batching mechanism for parallel independent steps (unlike delegation.md which supports multiple Task calls in one message).

10. **Vet-fix-agent confabulation risk** — Agent requires Scope IN/OUT to prevent flagging future-phase issues, but there's no automated enforcement. If prompt omits execution context, agent guesses scope from changed files (error-prone).

11. **UNFIXABLE detection mechanical only** — Orchestrator grep for UNFIXABLE works, but doesn't validate report format or issue severity. Could escalate low-priority UNFIXABLE items.

12. **No orchestrator context decay** — After N steps, orchestrator context can grow large (step files accumulate). Is there a context refresh mechanism or step history pruning?

## Recommendation for Design Input

This infrastructure is **sufficient for straightforward sequential execution** but has **clear limitations for complex orchestration:**

**Strengths:**
- Deterministic artifact generation (prepare-runbook.py)
- Explicit phase structure for TDD
- Mechanical escalation for UNFIXABLE issues
- Clean separation between step definition and execution

**Weaknesses:**
- Fire-and-forget delegation (no mid-flight communication)
- No recovery/retry mechanism (escalate only)
- Phase boundaries are prose-only (no checkpoint restart)
- Parallel execution unsupported
- Weak (haiku) orchestrator requires extensive band-aids

**Redesign opportunities:**
1. Make orchestrate skill interface explicit (step loading, error handling, model selection)
2. Add checkpoint/resume mechanism (load state from session.md, resume from phase boundary)
3. Support parallel independent steps via Task batching
4. Upgrade orchestrator to sonnet by default (eliminate haiku band-aids)
5. Add pre-delegation step validation (model tier, report paths, file references)
6. Formalize error escalation (diagnostic agents, recovery flow, UNFIXABLE severity levels)
7. Add context-aware scope injection (execution context templated, not hand-written)
8. Design phase boundary gates (checkpoint agents, alignment verification)
