# Commit RCA Fixes

**Problem:** Three recurring deviations in the commit/orchestration pipeline:
1. Submodule changes silently missed during commits
2. `prepare-runbook.py` artifacts aren't staged before tail-calling commit
3. Orchestrator STOP rule on dirty git gets overridden by LLM judgment

**Mode:** General (skill updates, no new infrastructure)
**Downstream:** `/plan-adhoc`

---

## Requirements

### Functional

- Commit skill detects and handles submodule modifications
- Generated artifacts are staged immediately after creation (before handoff)
- Orchestrator post-step tree check is unambiguous (no room for judgment)

### Non-Functional

- No new skills, hooks, or scripts — surgical edits to existing files only
- Fixes must not break existing tail-call chains
- Changes should be defensive (handle edge cases) without adding verbosity

### Out of Scope

- /reflect skill (deferred — workflow automation for future)
- Hook-based enforcement (overkill for these fixes)
- ~~Changing prepare-runbook.py itself~~ (revised: Fix 2 now adds `git add` to prepare-runbook.py — single fix point instead of duplicating across plan skills)

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
2. If submodule has uncommitted changes: commit them first with a message generated from the submodule's own diff, following standard commit message style. Do NOT prefix the message with the submodule name — the commit lives inside the submodule repo where it would be redundant
3. Stage the submodule pointer in parent: `git add <submodule-path>`
4. Continue with parent commit

**Scope:** Single-level submodules only. Nested submodules not used in this repo.

**Why:** Submodule pointer updates are invisible unless the submodule is committed first. A parent commit with a dirty submodule creates sync issues.
```

**Also update the Guidelines bullet list in step 4** to include submodules:
```
- **Include `agents/session.md`, `plans/` files, and submodule pointer updates if they have uncommitted changes**
```

### Fix 2: prepare-runbook.py — stage artifacts after creation

**File:** `agent-core/bin/prepare-runbook.py`

**Problem:** `prepare-runbook.py` creates files in `plans/*/steps/`, `plans/*/orchestrator-plan.md`, and `.claude/agents/`. These are untracked when `/handoff --commit` runs. The commit skill may not discover/stage them all (especially `.claude/agents/`).

**Previous approach (rejected):** Add `git add` to both plan-adhoc and plan-tdd skills after the prepare-runbook.py invocation. This duplicates the staging logic in two places and requires both skills to know what files the script creates — a coupling that breaks if prepare-runbook.py's output changes.

**Change:** Add `git add` at the end of `prepare-runbook.py` itself, after all files are written. The script already knows exactly which paths it created (agent_path, steps_dir, orchestrator_path), so it can stage them directly.

**Implementation:** Add `import subprocess` to the top-level imports (alongside `sys`, `re`, `os`, `Path`). In `validate_and_create()`, insert before the final `return True`, after the summary print block:
```python
# Stage all generated artifacts
paths_to_stage = [str(agent_path), str(steps_dir), str(orchestrator_path)]
result = subprocess.run(['git', 'add'] + paths_to_stage, capture_output=True, text=True)
if result.returncode != 0:
    print(f"⚠ git add failed: {result.stderr.strip()}")
    return False
print(f"✓ Staged artifacts for commit")
```

**Why in the script, not the skills:**
- Single fix point — no duplication across plan-adhoc and plan-tdd
- The script owns the knowledge of what files it creates
- If the script adds new output paths later, staging updates in one place
- Plan skills remain declarative ("run prepare-runbook.py") without implementation coupling

**Plan skill changes:** None. The skills call prepare-runbook.py unchanged; staging now happens inside it.

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

**Add clean-tree contract to generated agent content in `prepare-runbook.py`:** After appending runbook-specific context (line ~473), also append:

> **Clean tree requirement:** Commit all changes before reporting success. The orchestrator will reject dirty trees — there are no exceptions.

**Why prepare-runbook.py, not baseline templates:** `quiet-task.md` serves dual purpose — plan execution baseline AND generic delegation agent. Adding a commit requirement to the baseline would break generic delegation (e.g., file analysis tasks that shouldn't commit). The clean-tree rule is a plan-execution concern, so it belongs in the generated plan-specific agent content. `tdd-task.md` already enforces this via Step 7 (Post-Commit Sanity Check).

---

## Implementation Notes

**Affected files (5 edits across 4 files):**
- `agent-core/skills/commit/SKILL.md` — add 1b submodule check + update guidelines bullet
- `agent-core/bin/prepare-runbook.py` — add `git add` of generated artifacts (Fix 2) + append clean-tree contract to generated agent content (Fix 3)
- `.claude/skills/orchestrate/SKILL.md` — rewrite 3.3 section + delete contradictory scenario
- `agents/learnings.md` — add submodule commit learning

**Testing:** Manual verification — mostly prose changes to skill instructions. Fix 2 (prepare-runbook.py `git add`) is a code change: validate by running prepare-runbook.py on a runbook and confirming artifacts appear in `git status` as staged.

---

## Next Steps

`/plan-adhoc plans/commit-rca-fixes/design.md` | sonnet
