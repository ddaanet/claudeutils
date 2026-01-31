---
name: workflow-controls
model: sonnet
---

# Workflow Controls Implementation

**Context**: Implement shortcut system, session modes, and universal tail behavior for workflow skills.

**Source**: `plans/workflow-controls/design.md`
**Design**: Same file

**Status**: Draft
**Created**: 2026-01-31

---

## Weak Orchestrator Metadata

**Total Steps**: 7

**Execution Model**:
- Steps 1-7: Sonnet (file edits, hook script creation, testing)

**Step Dependencies**: Sequential (skills depend on execute-rule.md rewrite; testing depends on all implementations)

**Error Escalation**:
- Sonnet → User: Test failures, validation errors

**Report Locations**: `plans/workflow-controls/reports/step-N.md`

**Success Criteria**:
- All shortcuts expand correctly in hook
- Fragment loaded in CLAUDE.md
- Skills display STATUS format
- Session restart shows new hook active

**Prerequisites**:
- ✓ Design complete: `plans/workflow-controls/design.md`
- ✓ All target files exist (verified via Point 0.5)
- ✓ Hook development patterns loaded

---

## Common Context

**Key File Paths**:
- Fragment: `agent-core/fragments/execute-rule.md`
- Hook script: `agent-core/hooks/userpromptsubmit-shortcuts.py`
- Settings: `.claude/settings.json`
- Commit skill: `agent-core/skills/commit/SKILL.md`
- Handoff skill: `agent-core/skills/handoff/SKILL.md`
- Handoff-haiku skill: `agent-core/skills/handoff-haiku/SKILL.md`
- Design skill: `agent-core/skills/design/SKILL.md`

**Shortcut Tables**:

Tier 1 - Commands (exact match):
- `s` → `#status`
- `x` → `#execute` (smart: resume OR start pending)
- `xc` → `#execute --commit`
- `r` → `#resume` (strict: resume only)
- `h` → `/handoff`
- `hc` → `/handoff --commit`
- `ci` → `/commit`

Tier 2 - Directives (colon prefix):
- `d: <text>` → discussion mode (analyze, don't execute)
- `p: <text>` → pending task (append to session.md)

**STATUS Display Format**:
```
Next: <task name>
  `<command>`
  Model: <model> | Restart: <yes/no>

Pending:
- <task 2> (<model if non-default>)
- <task 3>
```

**Session.md Task Metadata Convention**:
```markdown
- [ ] **Task Name** — `command` | model | restart?
```

**Stop Conditions**:
- Test failure → stop, report error
- Hook validation failure → stop, report error
- Session restart required after hook changes

**Pre-execution Setup**:
```bash
mkdir -p agent-core/hooks
mkdir -p plans/workflow-controls/reports
```

**Testing Pattern**:
- Create test input JSON
- Run hook script directly
- Validate JSON output structure
- Check expansion correctness

---

## Step 1: Create UserPromptSubmit Hook Script

**Objective**: Implement Python hook script for shortcut expansion.

**Script Evaluation**: Small script (50-60 lines)

**Execution Model**: Sonnet

**Implementation**:

Ensure directory exists:
```bash
mkdir -p agent-core/hooks
```

Create `agent-core/hooks/userpromptsubmit-shortcuts.py`:

```python
#!/usr/bin/env python3
"""
UserPromptSubmit hook: Expand workflow shortcuts.

Tier 1 - Commands (exact match, entire message):
  s, x, xc, r, h, hc, ci

Tier 2 - Directives (colon prefix):
  d:, p:

No match: silent pass-through (exit 0, no output)
"""

import json
import re
import sys


# Tier 1: Command shortcuts (exact match)
COMMANDS = {
    's': ('[SHORTCUT: #status] List pending tasks with metadata from session.md. '
          'Display in STATUS format. Wait for instruction.'),
    'x': ('[SHORTCUT: #execute] Smart execute: if an in-progress task exists, resume it. '
          'Otherwise start the first pending task from session.md. Drive to completion, then stop.'),
    'xc': ('[SHORTCUT: #execute --commit] Execute task to completion, then handoff → commit → status display.'),
    'r': ('[SHORTCUT: #resume] Strict resume: continue in-progress task only. '
          'Error if no in-progress task exists.'),
    'h': '[SHORTCUT: /handoff] Update session.md with current context, then display status.',
    'hc': '[SHORTCUT: /handoff --commit] Handoff → commit → status display.',
    'ci': '[SHORTCUT: /commit] Commit changes → status display.'
}

# Tier 2: Directive shortcuts (colon prefix)
DIRECTIVES = {
    'd': ('[DIRECTIVE: DISCUSS] Discussion mode. Analyze and discuss only — '
          'do not execute, implement, or invoke workflow skills. '
          "The user's topic follows in their message."),
    'p': ('[DIRECTIVE: PENDING] Record pending task. Append to session.md Pending Tasks section '
          'using metadata format: `- [ ] **Name** — `command` | model | restart?`. '
          'Infer defaults if not specified. Do NOT execute the task.')
}


def main():
    # Read hook input
    hook_input = json.load(sys.stdin)
    prompt = hook_input.get('prompt', '').strip()

    # Tier 1: Exact match for commands
    if prompt in COMMANDS:
        output = {
            'hookSpecificOutput': {
                'hookEventName': 'UserPromptSubmit',
                'additionalContext': COMMANDS[prompt]
            }
        }
        print(json.dumps(output))
        return

    # Tier 2: Directive pattern (shortcut: <rest>)
    match = re.match(r'^(\w+):\s+(.+)', prompt)
    if match:
        directive_key = match.group(1)
        if directive_key in DIRECTIVES:
            output = {
                'hookSpecificOutput': {
                    'hookEventName': 'UserPromptSubmit',
                    'additionalContext': DIRECTIVES[directive_key]
                }
            }
            print(json.dumps(output))
            return

    # No match: silent pass-through
    sys.exit(0)


if __name__ == '__main__':
    main()
```

Make executable:
```bash
chmod +x agent-core/hooks/userpromptsubmit-shortcuts.py
```

**Expected Outcome**: Hook script created and executable.

**Unexpected Result Handling**:
- If chmod fails → verify file was written correctly

**Error Conditions**:
- File write failure → escalate to user
- chmod failure → escalate to user

**Validation**:
- File exists at `agent-core/hooks/userpromptsubmit-shortcuts.py`
- File is executable (`-x` permission)
- Shebang is `#!/usr/bin/env python3`
- Hook produces valid JSON for test inputs:
  ```bash
  echo '{"prompt": "x"}' | python3 agent-core/hooks/userpromptsubmit-shortcuts.py | jq .
  echo '{"prompt": "d: some topic"}' | python3 agent-core/hooks/userpromptsubmit-shortcuts.py | jq .
  echo '{"prompt": "regular message"}' | python3 agent-core/hooks/userpromptsubmit-shortcuts.py
  # First two should output JSON, third should exit 0 silently
  ```

**Success Criteria**:
- Script file exists
- Executable bit set
- Contains all tier 1 and tier 2 shortcuts

**Report Path**: `plans/workflow-controls/reports/step-1.md`

---

## Step 2: Rewrite execute-rule.md Fragment

**Objective**: Define four session modes and shortcut vocabulary table.

**Script Evaluation**: Prose description (content rewrite)

**Execution Model**: Sonnet

**Implementation**:

Rewrite `agent-core/fragments/execute-rule.md` with new content defining:

1. **Four session modes**:
   - STATUS (default): List tasks, wait
   - EXECUTE (`#execute`, `x`): Resume OR start pending
   - EXECUTE+COMMIT (`#execute --commit`, `xc`): Execute → handoff → commit
   - RESUME (`#resume`, `r`): Resume in-progress only (error if none)

2. **Shortcut vocabulary tables**: Both tier 1 and tier 2

3. **`x` vs `r` behavior matrix**:
   | State | `x` | `r` |
   |-------|-----|-----|
   | In-progress exists | Resume | Resume |
   | No in-progress, pending exists | Start first pending | Error |
   | No tasks | "No pending tasks" | Error |

4. **STATUS display format**: As specified in Common Context

5. **Ambiguous prompt handling**: "next?", "what's next?", startup → default to STATUS

**Expected Outcome**: Fragment contains complete mode definitions and vocabulary.

**Unexpected Result Handling**:
- If file structure unclear → consult design.md section "Files to Modify"

**Error Conditions**:
- Missing required sections → add them

**Validation**:
- File contains all four modes (STATUS, EXECUTE, EXECUTE+COMMIT, RESUME)
- Both shortcut tables present (tier 1 commands, tier 2 directives)
- `x` vs `r` behavior matrix included (table with 3 states)
- STATUS format specified with code block example
- Ambiguous prompt handling documented

**Success Criteria**:
- Fragment is complete and coherent
- All shortcuts documented with semantics
- MODE definitions clear

**Report Path**: `plans/workflow-controls/reports/step-2.md`

---

## Step 3: Update commit Skill - STATUS Display

**Objective**: Replace bare "Next: task" with full STATUS format.

**Script Evaluation**: Direct execution (surgical edit)

**Execution Model**: Sonnet

**Implementation**:

Edit `agent-core/skills/commit/SKILL.md`.

Find this section (starts at line ~185):
```markdown
## Post-Commit: Display Next Task

**This applies to ALL commits**, whether invoked directly or via tail-call from `/handoff --commit`.

After a successful commit, read `agents/session.md` and check for pending tasks (first `- [ ]` item).

**If pending tasks exist** — display the next one:
```
Committed: <commit subject line>

Next: <first pending task description>
```

**If no pending tasks** — tail-call `/next` to find work from broader context (todo.md, etc.).

**Why:** This enables tail-call composition. When `/commit` is tail-called from `/handoff --commit` (which is tail-called from `/plan-tdd` or `/plan-adhoc`), the user sees the next action without manual inspection. For post-planning workflows, this displays "Restart session, switch to haiku model, paste `/orchestrate {name}` from clipboard." When all pending work is done, `/next` finds the next thing.
```

Replace it with:

```markdown
## Post-Commit: Display Next Task

**This applies to ALL commits**, whether invoked directly or via tail-call from `/handoff --commit`.

After a successful commit, read `agents/session.md` and check for pending tasks.

**Display STATUS format:**

```
Committed: <commit subject line>

Next: <first pending task name>
  `<command to start it>`
  Model: <recommended model> | Restart: <yes/no>

Pending:
- <task 2 name> (<model if non-default>)
- <task 3 name>
- ...
```

**Graceful degradation:**
- Missing session.md or no Pending Tasks section → "No pending tasks."
- Tasks in old format (no metadata) → display with defaults (model=sonnet, restart=no)
- Missing model field → default to sonnet
- Missing restart field → default to no

**If no pending tasks** — tail-call `/next` to find work from broader context.
```

**Expected Outcome**: Skill uses new STATUS format.

**Unexpected Result Handling**:
- If section structure changed → adapt edit to current structure

**Error Conditions**:
- Edit fails (string not found) → report current section structure

**Validation**:
- STATUS format code block present
- Graceful degradation rules documented
- Tail-call to `/next` if no tasks

**Success Criteria**:
- Post-commit section updated
- All STATUS format elements present

**Report Path**: `plans/workflow-controls/reports/step-3.md`

---

## Step 4: Update handoff Skill - STATUS Tail

**Objective**: Add STATUS display as default tail, skip when `--commit` specified.

**Script Evaluation**: Direct execution (surgical edit)

**Execution Model**: Sonnet

**Implementation**:

Edit `agent-core/skills/handoff/SKILL.md`.

**Part 1:** Add new step 7 after the "6. Trim Completed Tasks" section.

Insert this new section:

```markdown
### 7. Display STATUS (unless --commit)

**If `--commit` flag was NOT specified:**

Display STATUS listing as final output. Read session.md Pending Tasks section and format:

```
Next: <first pending task name>
  `<command to start it>`
  Model: <recommended model> | Restart: <yes/no>

Pending:
- <task 2 name> (<model if non-default>)
- <task 3 name>
```

**Graceful degradation:**
- Missing session.md or no Pending Tasks → "No pending tasks."
- Old format (no metadata) → use defaults (sonnet, no restart)

**If `--commit` flag WAS specified:**

Skip STATUS display. The `/commit` skill will show it after committing.

**Rationale:** STATUS replaces the old session size advice. Model recommendations are now shown in STATUS display's "Model:" field.
```

**Part 2:** Remove old session size advice section.

Find and delete this section (starts around line ~121):
```markdown
[If still >150 lines after trimming:]
session.md is [X] lines (threshold: 150) after trimming completed tasks.
Review pending tasks and learnings for further reduction.

[If workflow complete:]
All workflow tasks complete. Start fresh session for new work.

[If next task needs different model:]
Next task ([task name]) requires [model name]. Switch model when starting new session."
```

**If next pending task needs different model:**
- Design stage → Suggest Opus
- Execution stage → Suggest Haiku
- Planning/Review/Completion → Suggest Sonnet

Example: "Next task: Design stage. Switch to Opus model for architectural work."
```

This advice is superseded by STATUS display's model recommendations.

**Expected Outcome**: Handoff shows STATUS unless chaining to commit.

**Unexpected Result Handling**:
- If step numbering different → adjust insertion point

**Error Conditions**:
- Edit fails → report current structure

**Validation**:
- New step 7 exists
- Conditional logic for --commit flag present
- Old session size advice removed

**Success Criteria**:
- STATUS tail added
- Flag logic correct
- Old advice section removed

**Report Path**: `plans/workflow-controls/reports/step-4.md`

---

## Step 5: Update handoff-haiku Skill - Task Metadata Format

**Objective**: Document task metadata convention for mechanical merge.

**Script Evaluation**: Direct execution (surgical edit)

**Execution Model**: Sonnet

**Implementation**:

Edit `agent-core/skills/handoff-haiku/SKILL.md` in Pending Tasks section (around line 40-60):

Add after existing Pending Tasks instructions:

```markdown
**Task metadata format:**

Use this convention when writing tasks:

```
- [ ] **Task Name** — `command` | model | restart?
```

Examples:
```
- [ ] **Implement ambient awareness** — `/plan-adhoc plans/ambient-awareness/design.md` | sonnet
- [ ] **Design runbook identifiers** — `/design plans/runbook-identifiers/problem.md` | opus | restart
```

**Field rules:**
- Command: Backtick-wrapped command to start the task
- Model: `haiku`, `sonnet`, or `opus` (default: sonnet if omitted)
- Restart: Optional flag - only include if restart needed (omit = no restart)

**Mechanical merge:**
Preserve metadata format verbatim when carrying forward unresolved items. No judgment needed - copy unchanged.
```

**Expected Outcome**: Skill documents metadata convention.

**Unexpected Result Handling**:
- If Pending Tasks section reorganized → adapt to structure

**Error Conditions**:
- Section not found → report structure for guidance

**Validation**:
- Metadata format documented
- Examples provided
- Mechanical merge instruction present

**Success Criteria**:
- Convention documented
- Examples clear
- Merge behavior specified

**Report Path**: `plans/workflow-controls/reports/step-5.md`

---

## Step 6: Update design Skill - Add Tail-Call

**Objective**: Add step 7 that invokes `/handoff --commit` after applying fixes.

**Script Evaluation**: Direct execution (surgical edit)

**Execution Model**: Sonnet

**Implementation**:

Edit `agent-core/skills/design/SKILL.md`.

Find the "### 6. Apply Fixes" section (around line 72-76) and add new step 7 after it:

```markdown
### 7. Handoff and Commit

**CRITICAL: As the final action, invoke `/handoff --commit`.**

This tail-call chains:
1. `/handoff` updates session.md with completed design work
2. Tail-calls `/commit` which commits the design document
3. `/commit` displays STATUS showing next pending task

The next pending task will typically be the planning phase (`/plan-adhoc` or `/plan-tdd`).

**Why:** Universal tail behavior ensures consistent workflow termination. User always sees what's next.
```

**Note:** The Process section intro doesn't currently mention a step count, so no update needed there.

**Expected Outcome**: Design skill chains into handoff → commit → status.

**Unexpected Result Handling**:
- If step count in intro unclear → verify and update

**Error Conditions**:
- Edit fails → report structure

**Validation**:
- Step 7 exists
- Tail-call instruction present
- Process intro updated to 7 steps

**Success Criteria**:
- Tail-call step added
- Chain documented
- Step count correct

**Report Path**: `plans/workflow-controls/reports/step-6.md`

---

## Step 7: Add UserPromptSubmit Hook to Settings

**Objective**: Register hook in `.claude/settings.json`.

**Script Evaluation**: Direct execution (JSON edit)

**Execution Model**: Sonnet

**Implementation**:

Read `.claude/settings.json` current structure, then add UserPromptSubmit hook:

```json
{
  "hooks": {
    "PreToolUse": [...existing...],
    "PostToolUse": [...existing...],
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "python3 $CLAUDE_PROJECT_DIR/agent-core/hooks/userpromptsubmit-shortcuts.py",
        "timeout": 5
      }
    ]
  }
}
```

**Note:** UserPromptSubmit hooks do not support the `matcher` field (per design.md line 44, 98). The hook always fires on every prompt and does internal filtering via regex.

**Expected Outcome**: Hook registered in settings.

**Unexpected Result Handling**:
- If hooks structure different → adapt to format
- If UserPromptSubmit already exists → append to array

**Error Conditions**:
- JSON parse failure → verify syntax
- File write failure → escalate

**Validation**:
- Valid JSON after edit
- UserPromptSubmit key exists
- Command path uses $CLAUDE_PROJECT_DIR
- Timeout set to 5 seconds

**Success Criteria**:
- Hook registered
- JSON valid
- Path portable

**Report Path**: `plans/workflow-controls/reports/step-7.md`

---

## Design Decisions

**Lowercase shortcuts over case-sensitive:**
From learnings.md: "Case-sensitive shortcuts are unreliable for LLM interpretation." Used `xc`/`hc` instead of `X`/`H`.

**Colon convention for directives:**
`d: text` reads naturally and disambiguates from natural language without foreign sigils.

**Two-layer system (hook + fragment):**
Hook handles standalone use mechanically. Fragment enables inline comprehension ("then hc").

**STATUS as universal tail:**
Eliminates flag proliferation. Every workflow termination shows STATUS by default.

**UserPromptSubmit matcher always "*":**
Hook does internal filtering. The matcher field doesn't actually filter UserPromptSubmit events - they always fire.

---

## Dependencies

**Before This Runbook**:
- Design document complete: `plans/workflow-controls/design.md`
- Vet review complete with fixes applied

**After This Runbook**:
- Hook changes require session restart to activate
- All workflow skills use new tail behavior
- Shortcuts available for user testing

---

## Notes

**Testing workflow:**

**Hook testing (before session restart):**
```bash
# Test tier 1 shortcuts
echo '{"prompt": "s"}' | python3 agent-core/hooks/userpromptsubmit-shortcuts.py | jq .
echo '{"prompt": "x"}' | python3 agent-core/hooks/userpromptsubmit-shortcuts.py | jq .
echo '{"prompt": "xc"}' | python3 agent-core/hooks/userpromptsubmit-shortcuts.py | jq .
echo '{"prompt": "r"}' | python3 agent-core/hooks/userpromptsubmit-shortcuts.py | jq .
echo '{"prompt": "h"}' | python3 agent-core/hooks/userpromptsubmit-shortcuts.py | jq .
echo '{"prompt": "hc"}' | python3 agent-core/hooks/userpromptsubmit-shortcuts.py | jq .
echo '{"prompt": "ci"}' | python3 agent-core/hooks/userpromptsubmit-shortcuts.py | jq .

# Test tier 2 directives
echo '{"prompt": "d: trade-offs of approach A"}' | python3 agent-core/hooks/userpromptsubmit-shortcuts.py | jq .
echo '{"prompt": "p: fix login bug"}' | python3 agent-core/hooks/userpromptsubmit-shortcuts.py | jq .

# Test no-match (should exit 0, no output)
echo '{"prompt": "regular user message"}' | python3 agent-core/hooks/userpromptsubmit-shortcuts.py
echo "Exit code: $?"  # Should be 0

# Verify all outputs are valid JSON with hookSpecificOutput.additionalContext
```

**Integration testing (after session restart):**
1. Restart Claude Code session (required for hook activation)
2. Test each shortcut: `s`, `x`, `h`, `ci`, `xc`, `hc`, `r`
3. Test directives: `d: some topic`, `p: pending task description`
4. Verify STATUS display format in skills (`/commit`, `/handoff`)
5. Check inline shortcut comprehension: "design this then hc"
6. Verify hook additionalContext appears in debug mode: `claude --debug`

**Hook activation:**
Changes to hooks require session restart. The UserPromptSubmit hook won't be active until Claude Code is restarted.

**Graceful degradation:**
All skills handle missing session.md or old-format tasks gracefully (defaults: sonnet, no restart).
