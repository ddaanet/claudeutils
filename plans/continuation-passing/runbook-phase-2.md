# Phase 2: Skill Modifications

**Objective:** Add frontmatter declarations and consumption protocol to 6 skills

**Context:** All cooperative skills need:
1. Frontmatter `continuation:` block with `cooperative: true` and `default-exit` list
2. Consumption protocol section (~5-8 lines) replacing hardcoded tail-calls
3. `Skill` tool added to `allowed-tools` if not present

## Common Phase Context

**Design references:**
- D-2: Explicit passing via Skill args (`[CONTINUATION: ...]` suffix format)
- D-3: Default exit appending (hook appends terminal skill's default exit)
- D-5: Sub-agent isolation (prohibition in protocol)

**Consumption protocol template** (use verbatim from design):
```markdown
## Continuation

As the **final action** of this skill:

1. Read continuation from `additionalContext` (first skill in chain) or from `[CONTINUATION: ...]` suffix in Skill args (chained skills)
2. If continuation is empty: stop (terminal)
3. Consume first entry as tail-call target
4. Invoke via Skill tool: `Skill(skill: "<target>", args: "<target-args> [CONTINUATION: <remainder>]")`

**CRITICAL:** Do NOT include continuation metadata in Task tool prompts. Continuation is for main-agent skill chaining only.
```

---

## Steps 2.1-2.3: Workflow Planning Skills (Template Pattern)

**Skills:** `/design`, `/plan-adhoc`, `/plan-tdd`

**Execution Model:** Sonnet (interpreting design intent for protocol text)

**Pattern:**
For each skill, apply these modifications:

### 1. Add frontmatter `continuation:` block

```yaml
continuation:
  cooperative: true
  default-exit: ["/handoff --commit", "/commit"]
```

### 2. Add `Skill` to `allowed-tools` (if not present)

**Note:** Only `/design` needs this addition. `/plan-adhoc` and `/plan-tdd` already have `Skill` in their allowed-tools.

### 3. Remove hardcoded tail-call section

**Current locations per design Component 3:**
- `/design`: C.5 "Handoff and Commit" section (line ~219: "CRITICAL: As the final action, invoke `/handoff --commit`")
- `/plan-adhoc`: Step 3 "Tail-call `/handoff --commit`" section (line ~688)
- `/plan-tdd`: Step 6 "Tail-call `/handoff --commit`" section (similar location at end)

### 4. Add continuation protocol section

Insert the consumption protocol template (from Common Phase Context above) where the hardcoded tail-call was removed.

**Expected Outcome:**
Each skill has frontmatter declaration, protocol section, and hardcoded tail-call removed.

---

## Step 2.4: Update /orchestrate Skill

**Execution Model:** Sonnet

**File:** `agent-core/skills/orchestrate/SKILL.md`

**Implementation:**

### 1. Add frontmatter `continuation:` block

```yaml
continuation:
  cooperative: true
  default-exit: ["/handoff --commit", "/commit"]
```

### 2. Add `Skill` to `allowed-tools`

Current `allowed-tools: Task, Read, Bash, Grep, Glob`
Updated: `allowed-tools: Task, Read, Bash, Grep, Glob, Skill`

### 3. Add continuation protocol section

**Note:** Design states "/orchestrate has no hardcoded Skill tail-call to remove — suggests next actions in prose". Add continuation protocol alongside existing completion handling (Section 6 "Completion").

Insert protocol at end of skill, after completion section:

```markdown
## Continuation

As the **final action** of this skill:

1. Read continuation from `additionalContext` (first skill in chain) or from `[CONTINUATION: ...]` suffix in Skill args (chained skills)
2. If continuation is empty: stop (terminal)
3. Consume first entry as tail-call target
4. Invoke via Skill tool: `Skill(skill: "<target>", args: "<target-args> [CONTINUATION: <remainder>]")`

**CRITICAL:** Do NOT include continuation metadata in Task tool prompts. Continuation is for main-agent skill chaining only.
```

**Expected Outcome:**
/orchestrate skill has frontmatter, `Skill` tool, and continuation protocol added. Existing completion prose preserved.

---

## Step 2.5: Update /handoff Skill

**Execution Model:** Sonnet

**File:** `agent-core/skills/handoff/SKILL.md`

**Implementation:**

### 1. Add frontmatter `continuation:` block

```yaml
continuation:
  cooperative: true
  default-exit: ["/commit"]
```

**Note:** `/handoff` default exit is `["/commit"]` only when `--commit` flag present. Hook handles this conditional logic (design "Handoff --commit Special Case" line 249-252).

### 2. Replace hardcoded tail-call section

**Current location:** "Tail-Call: --commit Flag" section (line ~213: "If `--commit` flag was provided: As the **final action** of this skill, invoke `/commit` using the Skill tool.")

**Replacement:** Continuation protocol template (from Common Phase Context).

**Expected Outcome:**
/handoff skill has frontmatter and continuation protocol. Conditional default exit handled by hook, not skill logic.

---

## Step 2.6: Update /commit Skill

**Execution Model:** Sonnet

**File:** `agent-core/skills/commit/SKILL.md`

**Implementation:**

### 1. Add frontmatter `continuation:` block

```yaml
continuation:
  cooperative: true
  default-exit: []
```

**Note:** `/commit` is terminal — empty `default-exit` list.

### 2. No other changes needed

`/commit` already terminal (displays STATUS and stops). No hardcoded tail-call to remove, no protocol section needed (empty continuation = no tail-call).

**Expected Outcome:**
/commit skill has frontmatter with empty `default-exit`. No behavioral changes.

---

## Phase Checkpoint

After all 6 skills modified:

**Verify frontmatter:**
```bash
# Check each skill has continuation block
grep -A 3 "continuation:" agent-core/skills/{design,plan-adhoc,plan-tdd,orchestrate,handoff,commit}/SKILL.md
```

Expected: All 6 skills have `continuation:` block with correct `default-exit` values.

**Verify Skill tool:**
```bash
# Check /design and /orchestrate have Skill in allowed-tools
grep "allowed-tools:" agent-core/skills/{design,orchestrate}/SKILL.md
```

Expected: Both include `Skill` in allowed-tools list.

**Verify protocol sections:**
```bash
# Check continuation protocol section exists
grep -l "## Continuation" agent-core/skills/{design,plan-adhoc,plan-tdd,orchestrate,handoff}/SKILL.md
```

Expected: 5 files (all except /commit).

**Run precommit:**
```bash
just precommit
```

Expected: All checks pass (no YAML syntax errors).

If checks fail: STOP and report which skill/check failed.

If checks pass: Proceed to Phase 3.
