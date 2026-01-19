# Phase 1 Execution Plan Review

**Plan**: `/Users/david/code/claudeutils/plans/oneshot-workflow/phase1-execution-plan.md`
**Design**: `/Users/david/code/claudeutils/plans/oneshot-workflow/design.md`
**Reviewer**: Sonnet (specialized review agent)
**Date**: 2026-01-19

---

## Overall Assessment: NEEDS_REVISION

The plan is well-structured and demonstrates strong weak orchestrator pattern adherence, but has several critical issues that would block execution. The script specification in Step 1.3 is comprehensive, but Step 1.4 contains incorrect test assumptions that would cause false failures.

**Recommendation**: Address critical issues before execution. Major issues are important for plan quality but not execution-blocking.

---

## Critical Issues (MUST FIX)

### 1. Step 1.4: Incorrect test runbook expectations

**Location**: Lines 444-445, 451, 490-495

**Issue**: The plan expects the test runbook to generate files with incorrect naming:
- Expected: `.claude/agents/phase2-execution-plan-task.md`
- Actual: Should be `.claude/agents/unification-task.md` (derived from parent directory `plans/unification/`)

**Evidence from design.md line 378**:
```
From input `plans/foo/runbook.md`:
- Runbook name: `foo` (from parent directory)
```

The test runbook is at `plans/unification/phase2-execution-plan.md`, so the parent directory is `unification`, not `phase2-execution-plan`.

**Impact**:
- Step 1.4 validation would fail even with correct script implementation
- False negative would block execution and cause unnecessary debugging

**Fix Required**:
Update Step 1.4 Part C to use correct expected paths:
- Agent: `.claude/agents/unification-task.md` (not `phase2-execution-plan-task.md`)
- Steps: `plans/unification/steps/step-2-1.md`, `step-2-2.md`, `step-2-3.md`
- Orchestrator: `plans/unification/orchestrator-plan.md`

### 2. Step 1.3: Missing executable permission setting

**Location**: Line 407 validation mentions `chmod +x` but implementation doesn't specify it

**Issue**: The implementation section doesn't explicitly state that the script should be made executable. While mentioned in validation, weak agents need this in the implementation directive.

**Impact**:
- Haiku may not make script executable
- Step 1.4 might fail to execute script
- Forces manual intervention

**Fix Required**:
Add to Step 1.3 implementation section (after **8. Output**):
```markdown
**9. Make Executable**
- Set executable permission: `chmod +x prepare-runbook.py`
- Add shebang line: `#!/usr/bin/env python3`
```

### 3. Step 1.2: Missing verification step for reference search completeness

**Location**: Lines 258-267 (Part C)

**Issue**: The plan specifies searching for `task-execute` references in only 4 specific files, but doesn't validate this is exhaustive. If references exist in other locations, they'll be missed.

**Impact**:
- Broken references left behind
- Future failures when old path is referenced
- Incomplete migration

**Fix Required**:
Add to Step 1.2 Part C (before "Update each reference"):
```markdown
**Verification: Search entire repository**
```bash
# Search entire claudeutils repo for task-execute references
cd /Users/david/code/claudeutils
rg "task-execute" --type md --files-with-matches
```
If files found beyond the 4 known locations, document in report and escalate to sonnet.
```

---

## Major Issues (STRONGLY RECOMMENDED)

### 4. Step 1.3: Frontmatter update logic unclear

**Location**: Lines 332-338 (Component 4)

**Issue**: The plan says "Update agent frontmatter: name, description" but doesn't specify:
- Whether to parse and modify existing frontmatter from quiet-task.md
- Whether to replace it entirely
- What the new frontmatter should contain

**Current behavior from build-plan-agent.sh** (line 73-82): Frontmatter is completely replaced with plan-specific version.

**Recommendation**: Clarify whether prepare-runbook.py should:
- **Option A**: Replace frontmatter entirely (like build-plan-agent.sh does)
- **Option B**: Parse and modify name/description fields only

Suggest Option A for consistency with existing pattern, but needs explicit direction.

**Suggested addition** to Step 1.3, Component 4:
```markdown
**Frontmatter strategy**: Replace baseline frontmatter entirely
- name: `<runbook-name>-task`
- description: "Execute <runbook-name> steps from the plan with plan-specific context."
- model: From runbook frontmatter or "haiku" default
- color: "cyan"
- tools: Inherit from baseline or specify ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
```

### 5. Missing success criteria for Common Context section parsing

**Location**: Lines 323-329 (Component 3)

**Issue**: Step 1.3 Component 3 describes parsing the "Common Context" section but validation criteria (lines 408-415) don't verify this works correctly.

**Recommendation**: Add specific test case to Step 1.4 validation:
```markdown
**Part D: Validate content**
1. Read plan-specific agent, verify structure:
   - Contains baseline quiet-task content
   - Contains separator: "---\n# Runbook-Specific Context"
   - Contains Common Context section from runbook (if present)
   - Frontmatter updated with correct name
2. Read step-2-1.md, verify format:
   - Has "# Step 2.1:" heading
   - Contains step content from runbook
   - Has reference to plan or common context
3. Read orchestrator-plan.md, verify contains instructions
```

### 6. Step 1.3: Section extraction logic underspecified

**Location**: Lines 323-329 (Component 3)

**Issue**: The plan describes what to extract but not the parsing logic:
- How to identify section boundaries (headings at what level?)
- Whether to preserve blank lines between sections
- How to handle nested subsections within steps
- Whether step content includes the "## Step N:" heading or starts after it

**Evidence from phase2-execution-plan.md**: Steps use `## Step 2.1:` format (H2 headings)

**Recommendation**: Add parsing specification to Step 1.3, Component 3:
```markdown
**Section boundary detection**:
- Common Context: `## Common Context` (H2) to next H2 heading or Steps
- Steps: Each `## Step N:` or `## Step N.M:` (H2 heading with "Step" prefix)
- Orchestrator: `## Orchestrator Instructions` (H2) to end of file

**Content extraction**:
- Include the heading line in extracted content
- Preserve all content until next H2 heading
- Preserve blank lines and formatting within sections
- Strip leading/trailing blank lines from section content
```

### 7. Step 1.4: Missing negative test case (validation failure)

**Location**: Lines 420-498

**Issue**: Step 1.4 only tests success path. Doesn't verify script validation works (e.g., rejects invalid runbooks).

**Recommendation**: This is good-to-have but not blocking. Could add as Phase 1.5 or defer to manual testing.

**Suggested addition** (optional):
```markdown
**Part F: Test validation (optional)**
- Create invalid runbook (e.g., no steps)
- Run script, verify exits with error
- Check error message is clear and actionable
```

---

## Minor Issues (QUALITY IMPROVEMENTS)

### 8. Inconsistent terminology: "runbook" vs "execution plan"

**Location**: Throughout document

**Issue**: The document uses "runbook" in the design and script spec, but the test file is named `phase2-execution-plan.md`. This could cause confusion.

**Observation**: The design.md uses "runbook" consistently. The existing file was created before terminology standardization.

**Recommendation**: Add note to Step 1.4 acknowledging this:
```markdown
**Note**: Test file is named `phase2-execution-plan.md` (pre-standardization). After Phase 1, future runbooks will use consistent naming.
```

### 9. Script location rationale could reference existing pattern

**Location**: Line 504-506 (Design Decision #1)

**Current**: "Rationale: Reusable across projects, aligns with existing tooling patterns"

**Improvement**: Reference the fact that `build-plan-agent.sh` already exists at project-local location and this is the evolution. Stronger rationale.

**Suggested revision**:
```markdown
**1. Script location: agent-core/bin/**
- Rationale: Reusable across projects (unlike build-plan-agent.sh which is in plans/unification/). Establishes pattern for shared tooling. agent-core is already a dependency.
- Alternative considered: claudeutils/bin/ (project-specific, rejected for reduced reusability)
```

### 10. Step 1.3: Python version could be more specific

**Location**: Lines 47, 267, 307

**Issue**: Says "Python 3" but doesn't specify minimum version. Some stdlib features may vary.

**Recommendation**: Specify minimum version or test on available version:
```markdown
**Language**: Python 3.8+ (pathlib, argparse, re all available)
**Validation**: Script should check Python version if using 3.8+ features
```

Not blocking - stdlib modules listed are available in all Python 3.x versions.

### 11. Missing cross-reference to build-plan-agent.sh

**Location**: Step 1.3 implementation

**Observation**: The existing `build-plan-agent.sh` script provides a working reference implementation for agent composition. Plan could reference it as a model.

**Suggested addition** to Step 1.3 implementation intro:
```markdown
**Reference implementation**: See `/Users/david/code/claudeutils/plans/unification/build-plan-agent.sh` for existing agent composition approach (lines 73-100). The prepare-runbook.py script extends this pattern with step extraction and validation.
```

### 12. Step file format could specify metadata more precisely

**Location**: Lines 342-351 (Component 5)

**Issue**: The step file format example shows:
```markdown
**Plan**: [path to runbook]
**Common Context**: [path to common context file or inline]
```

But doesn't clarify:
- Should paths be absolute or relative?
- Is "Common Context" a file reference or instruction to read from plan-specific agent?
- Is this metadata used by execution or just documentation?

**Recommendation**: Clarify purpose and format:
```markdown
**Step file format** (metadata is documentation, not parsed):
```markdown
# Step N: [Title from runbook]

**Plan**: plans/<runbook-name>/<runbook-filename>
**Agent**: .claude/agents/<runbook-name>-task.md

[Step content from runbook, starting with heading line]
```
**Note**: Metadata helps agents locate context, but plan-specific agent already contains common context.
```

### 13. Design Decision #6 could clarify "parent directory"

**Location**: Lines 524-527

**Current**: "Uses parent directory of runbook as runbook name"

**Improvement**: Provide example for clarity:
```markdown
**6. Step file naming from parent directory**
- Rationale: Clear association, avoids filename parsing complexity
- Example: `plans/unification/phase2-execution-plan.md` → runbook name is `unification`
- Uses parent directory of runbook file, not filename
```

---

## Completeness Assessment

### Design Decisions: COMPLETE

All major design choices documented with rationale:
- ✓ Script location and reusability
- ✓ Dependency minimization (stdlib only)
- ✓ Agent composition strategy (append vs template)
- ✓ Compatibility during transition (keep old file)
- ✓ Idempotency approach
- ✓ Path derivation logic

### Executability for Weak Agents: MOSTLY COMPLETE

**Step 1.1** (Haiku): Fully executable
- ✓ Complete bash script provided
- ✓ Error handling specified
- ✓ Validation criteria clear

**Step 1.2** (Haiku): Executable with Critical Issue #3 fix
- ✓ File operations clear
- ✓ Edit tool usage specified
- ⚠️  Reference search needs completeness check (Critical #3)

**Step 1.3** (Sonnet): Mostly executable with Major Issues #4, #5, #6 addressed
- ✓ Component structure clear
- ✓ Validation requirements comprehensive
- ⚠️  Frontmatter strategy needs clarification (Major #4)
- ⚠️  Section parsing needs specification (Major #6)
- ⚠️  Executable permission needs explicit directive (Critical #2)

**Step 1.4** (Haiku): Blocked by Critical Issue #1
- ✗ Expected file paths incorrect (Critical #1)
- ✓ Validation approach sound (once paths fixed)
- ✓ Idempotency test included

### Script vs Direct Assessment: APPROPRIATE

- ✓ Step 1.1: Correctly identified as ≤25 lines (direct execution)
- ✓ Step 1.2: Correctly identified as small script + prose (hybrid approach)
- ✓ Step 1.3: Correctly identified as >100 lines (prose description)
- ✓ Step 1.4: Correctly identified as prose (multi-step validation)

All complexity assessments align with Script-First Evaluation rule from CLAUDE.md.

### Validation Criteria: STRONG

Each step has measurable success criteria:
- ✓ Step 1.1: Directory existence and writability
- ✓ Step 1.2: File copied, frontmatter updated, references updated
- ✓ Step 1.3: Script exists, executable, syntax valid, functions implemented
- ✓ Step 1.4: Expected files created, content validated, idempotency verified

Validation is specific and actionable.

### Error Handling: EXCELLENT

Escalation triggers are clear and appropriate:
- ✓ Haiku → Sonnet triggers well-defined (unexpected states, permission errors)
- ✓ Sonnet → User triggers clear (design decisions, architecture changes)
- ✓ Each step specifies what constitutes "unexpected result"
- ✓ Error conditions documented with escalation paths

Aligns perfectly with weak orchestrator pattern.

---

## Self-Hosting Considerations

**Critical observation**: This plan will be processed by the very script it's creating (prepare-runbook.py).

### Bootstrap Paradox Resolution

The plan handles this well:
1. **Step 1.3**: Creates the script
2. **Step 1.4**: Tests the script with a different runbook (phase2-execution-plan.md)
3. **Implicit**: To use prepare-runbook.py on THIS plan, it would need to be run AFTER Phase 1 completion

### Runbook Format Compliance

Does this plan comply with the runbook format it's designed to process?

**Frontmatter**: ❌ MISSING
- No YAML frontmatter with name/model
- Script should handle this (defaults per design.md line 246-248)

**Common Context**: ✓ PRESENT (lines 52-149)
- "Common Context" section exists
- Contains script spec and baseline rename info

**Steps**: ✓ PRESENT (lines 152-498)
- 4 steps with clear "## Step N.N:" format
- Follows H2 heading pattern

**Orchestrator Instructions**: ❌ MISSING
- No explicit orchestrator section
- Would use default per design.md line 246-248

**Self-hosting compatibility**: ✓ WORKS
- Plan can be processed by prepare-runbook.py after Phase 1
- Missing sections will use defaults (acceptable)
- Could add frontmatter/orchestrator sections for completeness but not required

---

## Comparison with Baseline (task-execute.md)

The plan correctly identifies the baseline agent and its purpose. Review of `.claude/agents/task-execute.md`:

**Alignment with quiet execution pattern**: ✓
- Baseline emphasizes "Do what has been asked; nothing more, nothing less"
- Tool usage guidelines comprehensive
- Error reporting protocol clear
- "Stop and report" behavior emphasized

**Renaming rationale (task-execute → quiet-task)**: ✓ SOUND
- Avoids conflict with Task tool in Claude Code
- Emphasizes quiet execution pattern
- More descriptive of purpose

**Migration approach**: ✓ APPROPRIATE
- Copying (not moving) during Phase 1 maintains compatibility
- Deferred cleanup to Phase 4 is sensible
- Reduces risk during transition

---

## Recommendations Summary

### Before Execution (Required)

1. **Fix Critical Issue #1**: Correct expected file paths in Step 1.4 (use `unification-task.md`, not `phase2-execution-plan-task.md`)
2. **Fix Critical Issue #2**: Add explicit executable permission directive to Step 1.3
3. **Fix Critical Issue #3**: Add repository-wide reference search to Step 1.2

### Before Execution (Strongly Recommended)

4. **Address Major Issue #4**: Clarify frontmatter update strategy in Step 1.3
5. **Address Major Issue #6**: Specify section parsing logic in Step 1.3

### Quality Improvements (Optional)

6. Address Major Issue #5: Add content validation to Step 1.4
7. Address Minor Issues #8-13: Terminology, cross-references, metadata clarification

---

## Plan Strengths

1. **Excellent weak orchestrator metadata**: Clear model assignments, dependencies, error escalation
2. **Comprehensive script specification**: All required functionality documented
3. **Strong validation strategy**: Each step has measurable success criteria
4. **Appropriate complexity assessment**: Script vs direct evaluation correctly applied
5. **Good error handling**: Escalation triggers clear and actionable
6. **Design decisions documented**: Rationale for key choices provided
7. **Bootstrap awareness**: Plan can be self-hosted after completion

---

## Conclusion

This is a **well-structured execution plan** that demonstrates strong understanding of weak orchestrator patterns and delegation principles. The script specification in Step 1.3 is particularly comprehensive.

However, **Critical Issues #1-3 MUST be fixed** before execution to avoid false failures and incomplete migrations. Step 1.4's incorrect path expectations would cause the test to fail even with a correct implementation.

**Major Issues #4-6** should be addressed to improve executability for weak agents (particularly Sonnet in Step 1.3), but the plan is theoretically executable without them if the implementing agent makes reasonable assumptions.

**Recommendation**: Apply critical fixes, address major issues if time permits, proceed to execution.

---

## Revision Checklist

- [ ] Critical #1: Fix Step 1.4 expected file paths (unification-task.md, not phase2-execution-plan-task.md)
- [ ] Critical #2: Add executable permission directive to Step 1.3
- [ ] Critical #3: Add repository-wide reference search to Step 1.2
- [ ] Major #4: Clarify frontmatter update strategy in Step 1.3
- [ ] Major #5: Add content validation to Step 1.4
- [ ] Major #6: Specify section parsing logic in Step 1.3
- [ ] Optional: Address minor issues for quality improvement
- [ ] Update "Reviewed" line in plan frontmatter with date and status
- [ ] Increment revision number and document changes in Revision History
