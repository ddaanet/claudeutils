# Runbook Review Guide

**Purpose**: Prevent false positives when reviewing execution runbooks by understanding the layered context model.

**Target audience**: Agents performing runbook reviews (via /vet skill or similar)

---

## Layered Context Model

Execution runbooks use a **three-layer context model** where information flows from baseline → common context → step content:

```
┌─────────────────────────────────────┐
│  Baseline Agent Template            │  ← quiet-task.md or tdd-task.md
│  (agent-core/agents/*.md)           │
│  - Tool usage rules                 │
│  - Execution protocol               │
│  - Error handling patterns          │
└──────────────┬──────────────────────┘
               │
               ↓ Combined via prepare-runbook.py
┌──────────────────────────────────────┐
│  Plan-Specific Agent                 │  ← .claude/agents/<runbook-name>-task.md
│  (.claude/agents/*-task.md)          │
│  = Baseline + Common Context         │
└──────────────┬───────────────────────┘
               │
               ↓ Provided to each step execution
┌──────────────────────────────────────┐
│  Individual Step File                │  ← plans/<runbook>/steps/step-N.md
│  (plans/*/steps/step-*.md)           │
│  - Step-specific instructions        │
│  - Validation criteria               │
│  - Expected outcomes                 │
└──────────────────────────────────────┘
```

---

## What Goes Where

### Baseline Agent Template (quiet-task.md, tdd-task.md)

**Location**: `agent-core/agents/*.md`

**Purpose**: Universal execution rules and protocols for ALL runbooks of that type

**Contains**:
- Tool usage instructions (Read vs cat, Edit vs sed, etc.)
- Execution protocol (read reports, stop on errors, etc.)
- Report file handling
- Error escalation patterns
- General constraints (no sub-agents, etc.)

**Example** (from quiet-task.md):
```markdown
## Tool Usage

1. **Use specialized tools over Bash for file operations:**
   - Use **Read** instead of `cat`, `head`, `tail`
   - Use **Edit** instead of `sed` or `awk`
   - Use **Write** instead of `echo >` or `cat <<EOF`
```

**Key point**: Tool usage reminders belong HERE, not in individual steps.

---

### Common Context Section

**Location**: `## Common Context` section in runbook.md

**Purpose**: Shared information specific to THIS runbook that ALL steps need

**Contains**:
- Objective and constraints for this specific runbook
- Project-specific paths and conventions
- Key design decisions
- Domain-specific terminology
- Cross-step dependencies

**Example**:
```markdown
## Common Context

**Objective**: Add TDD cycle format support to `prepare-runbook.py`

**Key Constraints**:
- Maintain backward compatibility with general runbooks
- Follow existing code patterns

**Project Paths**:
- Script: `agent-core/bin/prepare-runbook.py`
- TDD baseline: `agent-core/agents/tdd-task.md`
```

**What NOT to include**:
- Tool usage rules (those are in baseline)
- Step-specific implementation details
- Execution protocol (that's in baseline)

---

### Individual Step Content

**Location**: `## Step N:` sections in runbook.md → extracted to `plans/*/steps/step-N.md`

**Purpose**: Specific instructions for THIS step only

**Contains**:
- Step objective (what this step accomplishes)
- Implementation guidance (what to do)
- Expected outcome (what success looks like)
- Validation criteria (how to verify)
- Error conditions (what can go wrong)
- Report path (where to write output)

**What NOT to include**:
- Tool usage reminders (already in baseline)
- Common context (already in Common Context section)
- Execution protocol (already in baseline)

---

## Review Checklist: Avoiding False Positives

When reviewing a runbook, check these layers systematically:

### Layer 1: Check Baseline Agent

**Before flagging "missing tool reminders"**:

1. Identify which baseline the runbook uses:
   - Check frontmatter: `model: sonnet` → uses quiet-task.md
   - Check frontmatter: `type: tdd` → uses tdd-task.md
   - Default: quiet-task.md

2. Read the baseline agent file:
   - `agent-core/agents/quiet-task.md` (for general runbooks)
   - `agent-core/agents/tdd-task.md` (for TDD runbooks)

3. Verify tool usage instructions exist in baseline:
   ```markdown
   ## Tool Usage
   1. Use specialized tools over Bash...
   ```

4. **If baseline has tool instructions → DO NOT flag as missing in steps**

**False positive example**:
```
❌ WRONG: "Steps 3-8 missing tool usage reminders"
✅ CORRECT: "Tool usage instructions present in quiet-task.md baseline"
```

---

### Layer 2: Check Common Context

**Before flagging "missing project information"**:

1. Check if `## Common Context` section exists in runbook
2. Verify it contains:
   - Objective and constraints
   - Project paths
   - Key conventions
   - Domain terminology

3. **If Common Context has the info → DO NOT flag as missing in steps**

**False positive example**:
```
❌ WRONG: "Step 5 missing project path information"
✅ CORRECT: "Project paths documented in Common Context section"
```

---

### Layer 3: Check Individual Steps

**What to actually review in steps**:

1. **Step-specific content**:
   - Is objective clear?
   - Is implementation guidance sufficient?
   - Are validation criteria measurable?
   - Are error conditions handled?

2. **Step dependencies**:
   - Does step N depend on outputs from step N-1?
   - Are prerequisites verified?

3. **Execution model**:
   - Is model selection appropriate (haiku/sonnet/opus)?
   - Is script vs prose assessment correct?

4. **Report paths**:
   - Are paths absolute and consistent?
   - Do they follow naming convention?

---

## Common False Positives

### 1. Tool Usage Reminders

**False Positive**: "Implementation steps don't explicitly remind agents to use specialized tools"

**Why it's false**: Tool usage rules are in baseline agent template (quiet-task.md), which is combined with every step via prepare-runbook.py

**How to avoid**: Always check baseline agent before flagging missing tool reminders

---

### 2. Repeated Context

**False Positive**: "Step 5 missing project path information"

**Why it's false**: Project paths are in Common Context section, available to all steps

**How to avoid**: Check Common Context section before flagging missing information

---

### 3. Execution Protocol

**False Positive**: "Steps don't specify error escalation protocol"

**Why it's false**: Error escalation protocol is in baseline agent template

**How to avoid**: Read baseline agent to understand execution protocol

---

## Review Protocol

### Step 1: Understand the Context Layers

1. Identify baseline agent:
   - Read frontmatter for `model` and `type` fields
   - Determine which baseline (quiet-task.md or tdd-task.md)

2. Read baseline agent file:
   - Note tool usage instructions
   - Note execution protocol
   - Note error handling patterns

3. Read Common Context section:
   - Note project-specific information
   - Note shared constraints
   - Note cross-step dependencies

### Step 2: Review Runbook Structure

1. Check metadata completeness:
   - Total steps count
   - Execution model assignments
   - Step dependencies (sequential/parallel)
   - Error escalation triggers
   - Success criteria (overall)

2. Check design decisions:
   - Are all major decisions documented?
   - Is rationale provided?
   - Are alternatives considered?

### Step 3: Review Individual Steps

For each step, verify:

1. **Objective**: Clear and focused?
2. **Implementation**: Sufficient guidance?
3. **Expected outcome**: Specific and testable?
4. **Validation**: Measurable criteria?
5. **Error handling**: Clear escalation triggers?
6. **Report path**: Absolute and consistent?

**Do NOT check**:
- Tool usage rules (that's in baseline)
- Execution protocol (that's in baseline)
- Common context (that's in Common Context section)

### Step 4: Provide Assessment

**Assessment format**:
- Overall: READY / NEEDS_REVISION
- Critical Issues: Must fix before execution
- Major Issues: Strongly recommended
- Minor Issues: Quality improvements

**For each issue, specify**:
- Location (which step or section)
- Problem (what's missing or wrong)
- Impact (why it matters)
- Recommendation (how to fix)

---

## Example: Correct Review

**Runbook**: `prepare-runbook-tdd/runbook.md`

**Step 1: Check layers**
1. Baseline: quiet-task.md (default, no type specified)
2. Read quiet-task.md: ✓ Has tool usage instructions
3. Read Common Context: ✓ Has project paths and constraints

**Step 2: Review structure**
- Metadata: ✓ Complete (9 steps, sequential, error triggers)
- Design decisions: ✓ Complete (5 decisions with rationale)

**Step 3: Review steps**
- Step 1: ✓ Objective clear, implementation sufficient
- Step 3: ⚠️  Implementation guidance could be more specific
- Step 9: ❌ Script evaluation says "≤25 lines" but shows 55-line script

**Step 4: Assessment**
```markdown
Overall Assessment: NEEDS_REVISION

Critical Issues: None

Major Issues:
1. Step 9 script evaluation inconsistent (claims ≤25 lines, shows 55 lines)

Minor Issues:
1. Step 3 implementation could specify test cases
```

**What was NOT flagged** (because baseline handles it):
- Tool usage reminders (in quiet-task.md)
- Error escalation protocol (in quiet-task.md)
- Report file handling (in quiet-task.md)

---

## Summary

**Key principle**: Don't flag as missing what's already in a higher layer.

**Layer priority**:
1. Baseline agent template (universal rules)
2. Common Context section (runbook-specific shared info)
3. Individual steps (step-specific instructions)

**Review order**:
1. Read baseline agent first
2. Read Common Context second
3. Review individual steps third

**When in doubt**:
- Check the baseline agent
- Check the Common Context
- Only flag issues in individual steps if truly missing

This prevents false positives and focuses review on actual gaps.
