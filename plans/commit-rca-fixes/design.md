# Commit RCA Fixes

**Problem:** Three recurring deviations in the commit/orchestration pipeline:
1. Submodule changes silently missed during commits
2. Plan skills don't stage `prepare-runbook.py` artifacts before tail-calling commit
3. Orchestrator STOP rule on dirty git gets overridden by LLM judgment

**Mode:** General (skill updates, no new infrastructure)
**Downstream:** `/plan-adhoc`

---

## Requirements

### Functional

- Commit skill detects and handles submodule modifications
- Plan skills explicitly stage generated artifacts before handoff
- Orchestrator post-step tree check is unambiguous (no room for judgment)

### Non-Functional

- No new skills, hooks, or scripts — surgical edits to existing skills only
- Fixes must not break existing tail-call chains
- Changes should be defensive (handle edge cases) without adding verbosity

### Out of Scope

- /reflect skill (deferred — workflow automation for future)
- Hook-based enforcement (overkill for these fixes)
- Changing prepare-runbook.py itself

---

## Fixes

### Fix 1: Commit skill — submodule awareness

**File:** `agent-core/skills/commit/SKILL.md`

**Problem:** `git status` shows `M agent-core` but the skill never inspects inside the submodule. Agent stages parent files but misses uncommitted submodule content.

**Change:** Add a submodule check step between step 1 (discovery) and step 2 (draft message).

**New section after "ERROR if working tree is clean" in step 1:**

```markdown
### 1b. Check submodules

If `git status` shows modified submodules (e.g., `M agent-core`):

1. Enter submodule: check `git status` inside it
2. If submodule has uncommitted changes: commit them first with a message generated from the submodule's own diff, prefixed with submodule name (e.g., "agent-core: Add hook script for shortcut expansion")
3. Stage the submodule pointer in parent: `git add <submodule-path>`
4. Continue with parent commit

**Scope:** Single-level submodules only. Nested submodules not used in this repo.

**Why:** Submodule pointer updates are invisible unless the submodule is committed first. A parent commit with a dirty submodule creates sync issues.
```

**Also update the Guidelines bullet list in step 4** to include submodules:
```
- **Include `agents/session.md`, `plans/` files, and submodule pointer updates if they have uncommitted changes**
```

### Fix 2: Plan skills — stage artifacts after prepare-runbook.py

**Files:** `agent-core/skills/plan-adhoc/SKILL.md`, `agent-core/skills/plan-tdd/SKILL.md`

**Problem:** `prepare-runbook.py` creates files in `plans/*/steps/`, `plans/*/orchestrator-plan.md`, and `.claude/agents/`. These are untracked when `/handoff --commit` runs. The commit skill may not discover/stage them all (especially `.claude/agents/`).

**Change:** Add explicit `git add` after `prepare-runbook.py` in both skills.

**plan-adhoc — after prepare-runbook.py invocation, before clipboard step:**
```bash
git add plans/{name}/steps/ plans/{name}/orchestrator-plan.md .claude/agents/{name}-task.md
```

**plan-tdd — after prepare-runbook.py invocation, before clipboard step:**
```bash
git add plans/{name}/steps/ plans/{name}/orchestrator-plan.md .claude/agents/{name}-task.md
```

**Precondition:** These paths are guaranteed to exist after successful `prepare-runbook.py` execution. If `git add` fails, `prepare-runbook.py` produced unexpected output — stop and report.

**Rationale:** Staging immediately after generation ensures artifacts are committed regardless of how downstream skills discover files. The tail-call chain (handoff → commit) then operates on pre-staged files.

### Fix 3: Orchestrator — strengthen post-step tree check

**File:** `agent-core/skills/orchestrate/SKILL.md` (the actual skill, which is at `.claude/skills/orchestrate/SKILL.md`)

**Problem:** The rule says "If dirty: STOP" but the executing agent rationalized "expected report file" and continued. The word "dirty" leaves room for the LLM to distinguish "expected dirty" from "unexpected dirty."

**Change:** Replace the current 3.3 section with stronger, unambiguous language:

```markdown
**3.3 Post-step tree check:**

After agent returns success:
```bash
git status --porcelain
```
- If clean (no output): proceed to next step
- If ANY output: **STOP orchestration immediately**
  - Report: "Step N left uncommitted changes: [file list]"
  - Do NOT proceed regardless of whether changes look expected
  - Do NOT clean up on behalf of the step
  - Escalate to user

**There are no exceptions.** Every step must leave a clean tree. If a step generates output files, the step itself must commit them. Report files, artifacts, and any other changes must be committed by the step agent before returning success.
```

**Delete contradictory scenario:** The "Handling Common Scenarios" section contains "Step succeeds but git shows unexpected changes → Continue execution." This directly contradicts section 3.3. Delete that scenario entirely — 3.3 already covers it unambiguously.

**Update agent template in `prepare-runbook.py`:** Add to the generated agent contract: "Commit all changes before reporting success. The orchestrator will reject dirty trees." This ensures future plan-specific agents know the clean-tree requirement.

---

## Implementation Notes

**Affected files (6 edits):**
- `agent-core/skills/commit/SKILL.md` — add 1b submodule check + update guidelines bullet
- `agent-core/skills/plan-adhoc/SKILL.md` — add `git add` after prepare-runbook.py
- `agent-core/skills/plan-tdd/SKILL.md` — add `git add` after prepare-runbook.py
- `.claude/skills/orchestrate/SKILL.md` — rewrite 3.3 section + delete contradictory scenario
- `agent-core/bin/prepare-runbook.py` — add clean-tree contract to agent template
- `agents/learnings.md` — add submodule commit learning

**Testing:** Manual verification — these are prose changes to skill instructions. Validate by running a workflow and observing correct behavior.

---

## Next Steps

`/plan-adhoc plans/commit-rca-fixes/design.md` | sonnet
