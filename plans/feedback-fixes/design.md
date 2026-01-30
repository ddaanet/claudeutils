# Design: Feedback Fixes for Skill Improvements Commit

## Problem

The last agent-core commit (140ff8f — "Strengthen TDD workflow with behavioral guardrails") and parent commit (2fe5743 — "Add hookify rules and update agent-core submodule") contain implementation errors and handoff quality issues identified in user review.

Issues span four areas:
- **tdd-task.md**: Structural errors in step ordering, orphaned sections, missing verification
- **Handoff quality**: Lost design decision detail, learnings misplacement, stale example
- **Hookify/git**: Committed .local files (should be untracked), gitignore gap
- **Workflow gaps**: Submodule confusion, skill composition limitation, batching ineffectiveness

## Scope

**In scope:**
- `agent-core/agents/tdd-task.md` — step ordering, orphaned sections, verification, bash style
- `agents/session.md` — recover lost detail, fix structure
- `agents/learnings.md` — absorb design decisions from session.md
- `agent-core/skills/handoff/SKILL.md` — clarify design decisions → learnings, add section constraints
- `agent-core/skills/handoff/examples/good-handoff.md` — remove pre-migration learnings section
- `.gitignore` — add `*.local.*` pattern
- Git cleanup — remove committed .local.md files from tracking
- New hook — submodule git operation safety
- `agent-core/skills/handoff/references/template.md` — verify no stale section references

**Out of scope:**
- Hookify rule recreation (user removed them; defer)
- @ reference support (answered: not available in skills/agents)
- refactor.md changes (already has equivalent post-refactoring updates section)

## Changes

### 1. tdd-task.md (agent-core)

#### 1a. Move structured log entry BEFORE commit

Currently: Structured Log Entry section is after Step 8 (Post-Commit Sanity Check).
Problem: Log entry isn't written before commit, so it's not included in the cycle's commit.

Move "Structured Log Entry" section to become **Step 5** (between "Escalate Refactoring" and current "Amend Commit").

#### 1b. Remove orphaned Post-Refactoring Updates section

Currently: "Post-Refactoring Updates" (lines 132-160) still in tdd-task.md.
Problem: tdd-task STOPs at Step 4 for refactoring escalation. This section is unreachable. refactor.md already has identical content (lines 131-157).

**Delete** the entire Post-Refactoring Updates section from tdd-task.md.

#### 1c. Verify intermediate commit

Currently: Step 2 creates WIP commit but doesn't verify.
Fix: Add verification line to commit block.

#### 1d. Token-efficient bash for amend commit step

Currently: Step 7 (Amend Commit) uses two separate bash blocks.
Fix: Combine into single token-efficient bash block.

**Bash block style rule for all changes:** No blank lines within bash blocks. Add explanatory comment as first line.

```bash
# Verify WIP commit exists, stage all changes, amend with final message
exec 2>&1
set -xeuo pipefail
current_msg=$(git log -1 --format=%s)
[[ "$current_msg" == WIP:* ]]
git add -A
git commit --amend -m "Cycle X.Y: [name]"
```

#### 1e. Fix step numbering

Current numbering jumps Step 4 → Step 6. After applying 1a/1b, renumber all steps:
- Step 1: Format & Lint
- Step 2: Intermediate Commit
- Step 3: Quality Check
- Step 4: Escalate Refactoring (STOP if warnings)
- Step 5: Write Structured Log Entry
- Step 6: Amend Commit
- Step 7: Post-Commit Sanity Check

#### 1f. Discuss: Are git status checks still necessary?

Since commit templates now use `git add -A` and the report template was placed correctly, question whether post-commit sanity checks (Step 7 and orchestrator's post-step tree check) are still needed.

**Decision: Keep but simplify.**
- `git add -A` in the amend step (1d) handles unstaged files
- The sanity check still catches a different class of bug: report file not written at all (code bug, not staging bug)
- Simplify Step 7: remove the "stage missing files, amend" self-heal logic (now handled by `git add -A` in Step 6). Keep only the "verify commit contains expected files" check as a diagnostic, not self-healing.
- Orchestrator's post-step tree check: keep as defense-in-depth (different agent, different failure mode)

### 2. Handoff skill improvements (agent-core)

Root cause analysis: The "## New Learnings" section appeared in session.md because:
1. `good-handoff.md` example has `## Recent Learnings` section (line 58) — pre-migration artifact
2. No explicit constraint listing allowed session.md sections
3. No explicit instruction that design decisions should go to learnings.md

#### 2a. Remove learnings from good-handoff.md example

Delete lines 57-77 (`## Recent Learnings` and its content) from `examples/good-handoff.md`. This is a pre-migration artifact from before learnings were separated into their own file.

#### 2b. Add section constraints to handoff SKILL.md

Add to Protocol section (after "3. Context Preservation"):

```markdown
**session.md allowed sections:**
- `## Completed This Session`
- `## Pending Tasks`
- `## Blockers / Gotchas`
- `## Reference Files`

**NEVER create other sections.** No "Learnings", "New Learnings", "Recent Learnings", "Key Design Decisions", or "Next Steps". Learnings and design decisions go to `agents/learnings.md`. Session.md is work state only.
```

#### 2c. Add design decisions → learnings guidance

Add to "4. Write Learnings to Separate File":

```markdown
**Design decisions are learnings.** When the session produced significant design decisions (architectural choices, trade-offs, anti-patterns discovered), write them to `agents/learnings.md` using the standard learning format. learnings.md is a staging area — `/remember` consolidates to permanent locations (fragments/, decisions/, skill references/).
```

#### 2d. Remove "Key Design Decisions" section from session.md

**Decision:** Do NOT add "Key Design Decisions" to template. Remove it from session.md.

**Rationale:** learnings.md is @file referenced in CLAUDE.md, so the next agent already sees all learnings. A separate "Key Design Decisions" section in session.md is redundant — it creates a second place where decisions live, and the handoff agent has to decide what goes where. Simpler: decisions go to learnings.md, session.md stays focused on work state (completed, pending, blockers, references).

**Updated allowed sections:**
- `## Completed This Session`
- `## Pending Tasks`
- `## Blockers / Gotchas`
- `## Reference Files`

Remove `## Key Design Decisions Made` from the constraint list in §2b as well.

#### 2e. Add anti-pattern: "commit this" as pending task

Add to "6. Trim Completed Tasks" section (Do NOT list):

```markdown
- Create "commit this" or "commit changes" as a pending task (commits don't update session.md to mark done)
```

### 3. Session.md — fix current state

- Remove `## New Learnings` section (lines 66-80)
- Remove `## Key Design Decisions Made` section (lines 52-64) — content moves to learnings.md
- Remove `- [ ] Commit skill improvements` from pending tasks
- Content from removed sections + lost design decisions → learnings.md (§4)

### 4. Learnings.md — absorb design decisions

Append the following (design decisions that were lost in handoff + new learnings from this session):

```markdown
**No human escalation during refactoring:**
- Design decisions are made during /design phase
- Opus handles architectural refactoring within design bounds
- Human escalation only for execution blockers (in orchestrate skill)
- Rationale: Blocking pipeline for human input during refactoring is expensive

**Defense-in-depth for commit verification:**
- tdd-task: post-commit sanity check (verify commit contains expected files)
- orchestrate: post-step tree check (escalate if dirty)
- Rationale: Catches different failure modes at different levels

**Handoff must preserve design decision detail:**
- Anti-pattern: Abbreviating design decisions during handoff, losing rationale
- Correct pattern: Write design decisions with rationale to learnings.md (staging area for /remember)
- session.md sections are fixed: Completed, Pending, Blockers, References only (see handoff skill §2b)
- learnings.md is staging → /remember consolidates to permanent locations (fragments/, decisions/, skill references/)

**Don't track "commit this" as pending task:**
- Anti-pattern: `- [ ] Commit changes` in session.md pending tasks
- Issue: Commits don't update session.md, so task is never marked done
- Correct pattern: Commits happen organically; only track substantive work

**Skills cannot invoke other skills:**
- Anti-pattern: Skill A invokes `/skill-b` via Skill tool
- Behavior: Agent stops when first skill finishes; second skill never runs
- Known issue: Open bug in Claude Code
- Correct pattern: Inline the logic or use references/ files
- Implication: /commit cannot call /handoff; must be separate user actions
```

Note: learnings.md will be ~110 lines. Needs `/remember` consolidation.

### 5. Git cleanup — .local files

#### 5a. Add gitignore pattern

Add to `.gitignore`:
```
# Local configuration (per-user, not shared)
*.local.*
```

Pattern `*.local.*` covers both `.local.md` (hookify rules) and `.local.json` (settings).

#### 5b. Remove committed files from tracking

```bash
git rm --cached .claude/hookify.batch-edit-reminder.local.md .claude/hookify.block-placeholder-edits.local.md
```

User already deleted from disk. `git rm --cached` removes from git index.

### 6. Submodule safety hook

**Problem:** Agents repeatedly:
1. Forget to `cd` into submodule before `git add`/`git commit`
2. Forget to `cd` back to parent after submodule operations

**Constraint from claude-code-guide:** PostToolUse hooks cannot change cwd. They can only report/warn. PreToolUse hooks can warn before execution.

**Solution: PreToolUse hook on Bash**

Add to `agent-core/hooks/hooks.json`:

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/submodule-safety.py"
        }
      ]
    }
  ]
}
```

Script logic (Python, reads stdin JSON):
- Extract `command` from tool_input
- Extract `cwd` from hook input
- Detect git operations: `git add`, `git commit`, `git push`, `git status`
- If git operation detected:
  - Check if cwd is project root but command references submodule paths → warn "cd into submodule first"
  - Check if cwd is inside a submodule → warn "You are in submodule [name]. Remember to cd back to project root after this operation."
- Non-blocking (warn only, don't block)

**Discussion: Can we auto-cd back?**
No. PostToolUse hooks cannot modify cwd.

**cwd persistence behavior:**
- **Main interactive agent:** cwd DOES persist between Bash calls. `cd submodule` in one call means all subsequent calls run in submodule. This is the root cause — agents cd in and forget to cd back.
- **Sub-agents (Task tool):** cwd does NOT persist between Bash calls. CLAUDE.md guidance about absolute paths targets sub-agents.

The PreToolUse warning is the best available solution. Warning message should recommend subshells: `(cd agent-core && git commit -m "msg")` — parentheses create a subshell that preserves parent cwd.

**Note:** Merge with existing PreToolUse hooks in hooks.json (currently has pretooluse-block-tmp.sh). The existing entry doesn't use a matcher, so it fires on all tools. Restructure:

```json
{
  "PreToolUse": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/pretooluse-block-tmp.sh"
        }
      ]
    },
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/submodule-safety.py"
        }
      ]
    }
  ]
}
```

## Design Decisions

### D1. Skills cannot call other skills — no handoff-in-commit

**Decision:** Cannot merge handoff into commit. Known limitation.

**Facts:**
- Skills cannot invoke other skills (agent stops when first skill finishes)
- This is a known Claude Code bug (open issue)
- Already documented in learnings (see §4)

**Implication:** User must invoke `/handoff` and `/commit` separately. The ordering issue (agents doing commit before handoff) is a prompt compliance problem, not solvable architecturally.

**Action:** Document in commit skill: "If session needs updating, user should invoke /handoff before /commit."

### D2. Tool batching — documentation is ineffective

**Decision:** Accept that documentation and direct interactive guidance are both insufficient to enforce batching. Don't recreate hookify rule either (session bloat concern). This is an unsolved problem.

**Rationale:**
- Documentation (tool-batching.md fragment) doesn't reliably change behavior
- Direct interactive guidance ("batch your edits") is often ignored
- Hookify rules add per-tool-call context bloat
- The cost-benefit may not favor batching (thinking tokens for planning vs. cached re-read tokens)

**Action:** Keep tool-batching.md as aspirational guidance. No enforcement mechanism currently.

**Pending discussion:** Explore "contextual block with contract" — a mechanism where a hook rule applies to a batch of tool calls rather than firing per-call. Not clear if Claude Code hooks support batch-level rules (they fire per individual tool use). This would require either:
- A stateful hook that tracks across calls within a message
- A new hook event type for "batch of tool calls"
- An alternative enforcement mechanism outside hooks

### D3. Session.md section constraints (learnings AND design decisions)

**Decision:** Add explicit allowed-section list to handoff skill. Four sections only: Completed, Pending, Blockers, References.

The constraint covers:
- **Learnings:** Must go to learnings.md
- **Design decisions:** Must go to learnings.md (not a separate session.md section)
- **No "Key Design Decisions" section** in session.md — redundant because learnings.md is @file referenced in CLAUDE.md, so next agent already sees all staged learnings

**Root cause of violation:** `good-handoff.md` example showed `## Recent Learnings` in session.md (pre-migration artifact). Agent followed the example.

**Action:** Fix example, add section constraint, remove Key Design Decisions from session.md.

### D4. Gitignore uses `*.local.*` pattern

**Decision:** Use `*.local.*` (not `*.local.md`).

Covers: `.local.md` (hookify rules), `.local.json` (settings), any future `.local.*` files. Consistent with `.env.local` convention.

### D5. Post-commit sanity check: simplify, don't remove

**Decision:** Keep sanity check but remove self-healing logic.

With `git add -A` in the amend step, staging bugs are handled. The sanity check now only needs to verify the commit contains expected files (diagnostic). If something is wrong, escalate rather than self-heal — self-healing masks bugs.

## Execution

Route: Direct execution (simple edits, no orchestration needed)

**Files to modify:**
- `agent-core/agents/tdd-task.md` (§1: reorder, delete, restyle)
- `agent-core/skills/handoff/SKILL.md` (§2b, §2c, §2e)
- `agent-core/skills/handoff/examples/good-handoff.md` (§2a: delete learnings)
- `agent-core/skills/handoff/references/template.md` (§2d: remove Key Design Decisions reference if present)
- `agents/session.md` (§3: remove New Learnings, Key Design Decisions, commit pending task)
- `agents/learnings.md` (§4: append)
- `.gitignore` (§5a: add pattern)
- `agent-core/hooks/hooks.json` (§6: add Bash matcher)
- `agent-core/hooks/submodule-safety.py` (§6: new script)

**Git operations:**
- `git rm --cached` for .local.md files (§5b)

**Pending discussion (not in this design):**
- Tool batching: contextual block with contract — explore whether hooks can enforce batch-level rules
