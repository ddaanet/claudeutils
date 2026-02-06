# Design: Structural Fix for Prose Skill Gates

## Problem Statement

Execution-mode cognition optimizes for "next tool call." Skill steps that contain only prose judgment (no tool call instruction) get scanned but not executed. This has manifested in three independent instances despite increasingly strong language each time.

## Analysis of Three Affected Cases

### Case 1: Commit Skill Step 0 -- Session Freshness Check

**Location:** `agent-core/skills/commit/SKILL.md` lines 84-99

**What it does:** Before any commit work, check whether session.md reflects current state. If stale, run `/handoff` first.

**Why it's prose-only:** The step instructs the agent to mentally compare session.md contents against conversation context. There is no Read command, no script invocation, no tool call. The entire step is a cognitive evaluation: "look at session.md, decide if it's stale."

**What gets skipped to:** Step 1 (`just precommit`) -- the first concrete Bash command in the skill.

### Case 2: Commit Skill Step 0b -- Vet Checkpoint

**Location:** `agent-core/skills/commit/SKILL.md` lines 100-114

**What it does:** Before committing production artifacts, verify that a vet review was completed. If no vet review exists, stop and delegate to vet-fix-agent.

**Why it's prose-only:** The step asks three yes/no questions that require the agent to recall conversation context. No file is read, no command is run. The answers determine whether to proceed or stop.

**What gets skipped to:** Same as Case 1 -- Step 1 (`just precommit`).

### Case 3: Orchestrate Skill 3.4 -- Phase Boundary Checkpoint

**Location:** `agent-core/skills/orchestrate/SKILL.md` lines 107-138

**What it does:** At every phase boundary, delegate to vet-fix-agent for quality review before proceeding to the next phase.

**Why it's prose-only:** The step is embedded within the step execution loop (section 3). After completing a cycle and its post-step tree check (3.3), the agent must detect a phase boundary and then delegate. But phase boundary detection is a mental operation (compare Phase field of current step vs previous step), and the subsequent delegation is described in prose rather than as a concrete tool invocation template.

**What gets skipped to:** The next cycle's step delegation (3.1) -- the next concrete Task tool invocation.

### Structural Pattern

All three cases share these characteristics:
- They are **decision gates** positioned between concrete execution steps
- Their first action is **cognitive** (compare, evaluate, recall) rather than **instrumental** (run command, read file, invoke tool)
- The step following them has an **immediately actionable tool call** that acts as an attractor
- Strengthening the language ("MUST", "no exceptions", "CRITICAL") has failed 3/3 times

The root cause is not willfulness or laziness. It is an optimization: when scanning a skill definition for "what to do next," steps with tool calls register as actionable while prose steps register as contextual commentary.

## Fix Options

### Option A: Concrete Gate Actions (Script-Based)

**Approach:** Replace each prose gate with a script that performs the evaluation and outputs a pass/fail result.

**Implementation:**

**For Step 0 (session freshness):** Create `agent-core/bin/check-session-freshness.py` that:
- Reads `agents/session.md`
- Reads recent git log for uncommitted context indicators
- Checks timestamp/date in session header vs current date
- Outputs PASS (session current) or FAIL with specific staleness indicators
- Agent acts on output: PASS = proceed, FAIL = run handoff first

**For Step 0b (vet checkpoint):** Create `agent-core/bin/check-vet-status.py` that:
- Scans `plans/*/reports/` and `tmp/` for recent vet reports
- Checks git log for production file changes since last vet
- Outputs PASS (vet completed or no production artifacts) or FAIL (unvetted artifacts listed)
- Agent acts on output: PASS = proceed, FAIL = delegate to vet-fix-agent

**For 3.4 (phase boundary):** No script needed -- restructure into the execution loop (see Option B hybrid below).

**Evaluation:**
- Reliability: HIGH -- script execution is a concrete tool call that cannot be scanned past
- Token cost: MODERATE -- adds ~3 lines per gate (run script, read output, act on result)
- Maintainability: MODERATE -- scripts need maintenance as project conventions evolve
- Generality: LOW -- each gate needs a custom script; doesn't establish a reusable pattern

**Risk:** False confidence. If the script passes, the agent may treat the gate as "done" without applying judgment to edge cases the script cannot detect. The script can catch mechanical staleness (date mismatch, missing files) but not semantic staleness (session.md exists but doesn't reflect recent work).

### Option B: Gate-Before-Command Restructuring

**Approach:** Restructure skill definitions so that prose gates become the opening paragraph of the next tool-call step, rather than standalone steps.

**Implementation:**

**Commit skill Steps 0/0b + Step 1 become a single Step 1:**

```markdown
### 1. Pre-commit validation

**Gate: Session freshness.**
Read `agents/session.md` and check:
- Does "Completed This Session" reflect work done in this conversation?
- Are pending tasks recorded?
- Are blockers/gotchas documented?

If stale: Run `/handoff` (or `/handoff-haiku`) first. Return to commit after handoff completes.

**Gate: Vet checkpoint.**
Read the conversation context. Were production artifacts (code, scripts, plans, skills, agents) created this session?
- If yes: Verify a vet report exists in `plans/*/reports/` or `tmp/`
- If no vet review: STOP. Delegate to vet-fix-agent first.

**Validation** (the concrete action):
[bash block with just precommit + git status -vv]
```

**Key change:** The `Read agents/session.md` instruction is now the first concrete action of the combined step, and it precedes the validation bash block. The gates are not separate steps that can be skipped -- they are preconditions within the same step as the first tool call.

**For orchestrate 3.4:** Merge phase boundary detection into step 3.3 (post-step tree check):

```markdown
### 3.3 Post-step verification

After agent returns success:
[git status --porcelain check]

**Phase boundary check:**
Compare current step's `Phase: N` with previous step.
If phase changed: delegate to vet-fix-agent for checkpoint (template below).
Do NOT proceed to next step until checkpoint completes.

[checkpoint delegation template]
```

**Evaluation:**
- Reliability: MODERATE -- the gate text is now in the same step as a concrete action, but the agent could still skip the gate paragraphs and jump to the bash block within the step
- Token cost: LOW -- no new files, just restructuring existing content
- Maintainability: HIGH -- no external scripts, changes are local to skill files
- Generality: HIGH -- establishes a convention (no standalone prose steps) that applies to all future skills

**Risk:** Grouping gate + action into one step doesn't guarantee the gate paragraphs are executed. The agent might still jump to the bash block within the step.

### Option C: Hook-Based Enforcement

**Approach:** Use PreToolUse hooks to enforce gate conditions before allowing the first tool call in a skill.

**Implementation:**

**For commit skill:** A PreToolUse hook on `Bash(just precommit)` that:
- Checks if session.md was recently modified (within last N minutes or since conversation start)
- Checks for vet reports corresponding to recent production changes
- Blocks the bash call with exit 2 and error message if conditions not met

**Technical fit with existing infrastructure:**
- The project already has PreToolUse hooks (block-tmp, symlink-redirect, submodule-safety)
- Hook configuration in `.claude/settings.json` supports `matcher` for specific tools
- Hook can read stdin JSON to get tool_input and match `just precommit`

**For orchestrate skill:** A PreToolUse hook on `Task` that:
- Checks if phase boundary checkpoint is needed before allowing next step delegation
- Would need to maintain state (which phase was last completed)

**Evaluation:**
- Reliability: HIGH -- hooks fire before every tool call, cannot be skipped by the agent
- Token cost: LOW -- hooks run externally, no skill text bloat
- Maintainability: LOW -- hooks are brittle (need to track conversation state externally), hard to debug, and hook infrastructure has known bugs (excludedCommands unreliable per settings.json comments)
- Generality: LOW -- each gate needs a custom hook; hooks can't easily reason about semantic conditions

**Risk:** Hooks run in a separate process without conversation context. They can check mechanical conditions (file timestamps, file existence) but cannot evaluate semantic conditions (is session.md actually current for this conversation's work?). Also, hooks don't fire in sub-agents, limiting applicability.

### Option D: Concrete Read as Gate Anchor

**Approach:** Every prose gate gets a mandatory `Read` call as its first instruction. The Read provides the data the gate needs to evaluate, and the evaluation happens in the same breath as processing the Read output.

**Implementation:**

**Commit Step 0 becomes:**
```markdown
### 0. Session freshness check

Read `agents/session.md`.

Compare "Completed This Session" against work done in this conversation:
- If session reflects current state: proceed to Step 0b
- If stale: run `/handoff` first, then return to Step 0b

Staleness indicators:
- [same list as current]
```

**Commit Step 0b becomes:**
```markdown
### 0b. Vet checkpoint

Read the list of files changed in this session:
[bash: git diff --name-only HEAD~N or git status --porcelain]

Classify each changed file: production artifact or not.
If production artifacts exist AND no vet report in plans/*/reports/ or tmp/:
  STOP. Delegate to vet-fix-agent.
```

**Orchestrate 3.4 becomes:**
```markdown
### 3.4 Phase boundary checkpoint

Read the next step file header:
[Read plans/<name>/steps/step-{N+1}.md, first 5 lines]

Compare `Phase:` field with current phase.
If phase changed: delegate to vet-fix-agent with checkpoint template.
```

**Evaluation:**
- Reliability: HIGH -- `Read` is a concrete tool call. The agent must execute it to get the data it needs for the gate evaluation. The gate judgment and the tool call are coupled: you can't evaluate without reading.
- Token cost: LOW -- adds one Read call per gate (which was arguably needed anyway for accurate evaluation)
- Maintainability: HIGH -- no external scripts, changes are minimal and local to skill files
- Generality: HIGH -- establishes a clear convention: every gate step starts with a tool call that provides the data needed for the judgment

**Risk:** Agent could execute the Read but still not apply the gate judgment. However, this is significantly less likely than the current pattern because:
1. The Read output is fresh in context when the evaluation instructions follow
2. The Read provides concrete data that makes the evaluation specific (not abstract)
3. The step now has a tool call, so it registers as "actionable" during scanning

## Recommended Fix: Option D (Concrete Read as Gate Anchor) + Convention

Option D is the best fit because it addresses the root cause directly: prose gates lack a tool call, so they don't register during execution-mode scanning. Adding a Read as the first instruction in each gate step:

1. Makes the step register as actionable (has a tool call)
2. Provides the concrete data needed for accurate gate evaluation
3. Couples the judgment to its inputs (can't skip the evaluation when the data is right there)
4. Requires minimal changes (one Read instruction per gate, no new scripts)
5. Establishes a generalizable convention for all future skill design

### Complementary Convention (from Option D + Option B insights)

Establish a skill design rule:

> **Every skill step MUST begin with a concrete tool call.** Steps that require judgment or evaluation must start with a Read, Bash, or other tool call that provides the data needed for that judgment. Pure prose judgment steps are a structural anti-pattern -- they will be skipped during execution.

This convention prevents the problem from recurring in future skills.

## Implementation Sketch

### Files Changed

**1. `agent-core/skills/commit/SKILL.md`** -- Modify Steps 0 and 0b

Step 0 change (session freshness):
- Add `Read agents/session.md` as the first instruction
- Keep existing evaluation criteria and staleness indicators
- The Read grounds the judgment in concrete, visible data

Step 0b change (vet checkpoint):
- Add `Bash: git diff --name-only HEAD` (or equivalent) as the first instruction
- Follow with file classification and vet report check
- The diff output provides the concrete artifact list for evaluation

**2. `agent-core/skills/orchestrate/SKILL.md`** -- Modify Section 3.4

- Add `Read plans/<name>/steps/step-{N+1}.md` (first 5 lines) as the first instruction of the phase boundary check
- This naturally provides the Phase field for comparison
- Follow with existing checkpoint delegation template

**3. `agent-core/fragments/skill-design-convention.md`** (new fragment, or append to existing)

Document the convention:
- Every step must begin with a concrete tool call
- Prose-only gates are a structural anti-pattern
- Pattern: Read the data first, then evaluate

**4. `agents/decisions/implementation-notes.md`** -- Add entry

Document the decision and rationale for memory index.

**5. `agents/learnings.md`** -- Remove "Prose skill gates skipped" learning

The learning is superseded by the structural fix and the new convention.

### Detailed Changes

#### Commit Skill Step 0

Current (prose-only):
```markdown
### 0. Session freshness check

**Before any commit work**, verify session.md reflects current state:

- If session.md is stale (doesn't reflect work done in this conversation), run handoff first:
  ...
```

Proposed (Read-anchored):
```markdown
### 0. Session freshness check

**Read `agents/session.md`.**

Compare "Completed This Session" against work done in this conversation:
- Does it reflect the changes you're about to commit?
- Are pending tasks and blockers current?

If stale: run `/handoff` (haiku: `/handoff-haiku`) with `--commit` flag before proceeding.
If current: proceed to Step 0b.

Staleness indicators:
- Completed work not in "Completed This Session"
- New pending tasks not recorded
- Blockers/gotchas discovered but not documented
```

#### Commit Skill Step 0b

Current (prose-only):
```markdown
### 0b. Vet checkpoint (all models)

**Before committing production artifacts**, verify alignment:

- **Production artifacts created this session?** (code, scripts, plans, skills, agents)
- **Vet review with alignment check completed?** Report in `plans/*/reports/` or `tmp/`
...
```

Proposed (Bash-anchored):
```markdown
### 0b. Vet checkpoint (all models)

**List changed files:**
```bash
git diff --name-only HEAD
git status --porcelain
```

Classify each file: is it a production artifact (code, scripts, plans, skills, agents)?

- **No production artifacts?** Proceed to Step 1.
- **Production artifacts exist?** Check for vet report in `plans/*/reports/` or `tmp/`.
- **No vet report?** STOP. Delegate to `vet-fix-agent` first. Return after vet completes.
- **UNFIXABLE issues in vet report?** Escalate to user before commit.

Reports are exempt -- they ARE the verification artifacts.
```

#### Orchestrate Skill 3.4

Current (prose within loop):
```markdown
**3.4 Checkpoint at phase boundary:**

At every phase boundary, delegate to vet-fix-agent for quality review.

**Phase boundary detection:** When step file `Phase: N` field changes from previous step.
```

Proposed (Read-anchored):
```markdown
**3.4 Checkpoint at phase boundary:**

**Read the next step file header** (first 10 lines of `plans/<name>/steps/step-{N+1}.md`).

Compare its `Phase:` field with the current step's phase.
- **Same phase:** Skip checkpoint, proceed to 3.5.
- **Phase changed (or no next step = final phase):** Delegate to vet-fix-agent:

[existing checkpoint delegation template unchanged]
```

## Trade-off Analysis

| Criterion | Option A (Scripts) | Option B (Restructure) | Option C (Hooks) | **Option D (Read Anchor)** |
|---|---|---|---|---|
| Prevents skipping | High | Moderate | High | **High** |
| Token cost | Moderate | Low | Low | **Low** |
| Maintainability | Moderate | High | Low | **High** |
| Generality | Low | High | Low | **High** |
| Semantic evaluation | Low (mechanical only) | N/A | Low | **High (data in context)** |
| New files needed | 2-3 scripts | 0 | 1-2 hooks | **0-1 fragment** |
| Risk of false pass | High | Moderate | High | **Low** |

Option D wins on the combined criteria. It is the only option that both prevents skipping (tool call anchor) and preserves semantic evaluation quality (data in context for judgment).

## Open Questions Resolved

From the RCA:

> Does Option A create false confidence?

Yes. A script that outputs PASS removes the agent's need to reason about edge cases. Mechanical checks miss semantic staleness.

> Does Option D over-constrain skill design?

The convention ("every step must begin with a tool call") is not restrictive in practice. Every gate that requires judgment also requires data. The Read/Bash call provides that data. If a step truly needs no data and no tool call, it likely belongs as a paragraph within an adjacent step, not as a standalone step.

> Is the real fix at the skill-design level or the execution-pattern level?

Skill-design level. Changing execution-mode behavior would require changes to Claude Code itself. Changing skill structure is within project control and addresses the root cause directly.

> Would a "gate checklist" pattern work?

Unnecessary given Option D. The Read output naturally structures the evaluation. A formal checklist adds token cost without additional reliability.
