# TDD Integration Runbook Review

**Runbook**: `plans/tdd-integration/runbook.md`
**Reviewer**: Task Agent (Sonnet)
**Date**: 2026-01-19
**Status**: NEEDS_REVISION

---

## Overall Assessment

**Status**: NEEDS_REVISION

**Summary**: The runbook demonstrates strong structure with comprehensive Common Context and detailed step specifications. However, several critical issues prevent weak orchestrator execution: implicit file operations expecting bash tool usage, inconsistent script evaluation categorization, and missing execution model specifications for inline scripts.

**Readiness Score**: 6/10
- Strong: Common Context, validation standards, step detail
- Weak: Script execution model, tool usage specification, dependency clarity

---

## Critical Issues

### Issue C1: Inline Script Execution Model Undefined

**Location**: Steps 1, 8 (inline bash scripts)

**Problem**: Steps include inline bash scripts but don't specify:
- Which agent executes the script (haiku/sonnet)
- Whether script should be written to file first
- Tool usage constraints for script execution

**Evidence**:
```markdown
## Step 1: Create oneshot workflow documentation
**Execution Model**: Sonnet

**Implementation**:
```bash
#!/usr/bin/env bash
# Move workflow.md to agent-core as oneshot-workflow.md
...
```
```

**Impact**:
- Weak orchestrator doesn't know HOW to execute the inline script
- Violates "Task Agent Tool Usage" rule (must use Read/Write/Edit, not bash file ops)
- Script uses `cp` command which should be direct Bash execution, not file creation

**Fix Required**:
Either:
1. Mark as "direct execution" and remove script wrapper, OR
2. Add explicit instruction: "Execute this script directly via Bash tool (do not write to file)"

**Recommended Fix**:
```markdown
**Execution Model**: Sonnet - Direct bash execution (inline)

**Implementation**:
Execute the following commands directly via Bash tool:

```bash
# Verify source exists
if [[ ! -f agents/workflow.md ]]; then
  echo "ERROR: agents/workflow.md not found"
  exit 1
fi
...
```
```

---

### Issue C2: Step 1 Script Contradicts Task Agent Tool Rules

**Location**: Step 1, lines 150-182

**Problem**: The inline script uses bash file operations (`cp`, `test -f`, `wc -c`) which violates the explicit rule that task agents must use specialized tools (Read, Write, Edit) instead of bash commands.

**Evidence from CLAUDE.md**:
> Use **Read** instead of `cat`, `head`, `tail`
> Use **Write** instead of `echo >` or `cat <<EOF`
> **NEVER use heredocs** (`<<EOF`) in bash commands

**Conflict**:
- Script uses: `cp agents/workflow.md agent-core/agents/oneshot-workflow.md`
- Should use: Read tool + Write tool
- Script uses: `wc -c < file`
- Should use: Read tool (returns file info)

**Impact**:
- Weak agent following task rules will refuse to execute as written
- Creates confusion about when bash file ops are acceptable
- Violates project's explicit tool usage standards

**Fix Required**:
Rewrite Step 1 to use proper tool sequence:
1. Read `agents/workflow.md`
2. Write content to `agent-core/agents/oneshot-workflow.md`
3. Validate via Bash: `test -f agent-core/agents/oneshot-workflow.md`

---

### Issue C3: Inconsistent Script Evaluation Classifications

**Location**: Multiple steps

**Problem**: Script evaluation labels don't match actual complexity:

| Step | Label | Actual Complexity | Correct Label |
|------|-------|-------------------|---------------|
| 1 | "Small script (direct execution)" | 30+ lines with error handling | Should be "≤25 lines = inline" with note about execution model |
| 5 | "Small script (straightforward additions)" | Actually prose description, not script | Should be "Prose description" |
| 8 | "Small script (direct execution)" | 75+ lines with multiple operations | Borderline ≤100 lines, acceptable |

**Evidence**:
- Step 1: 32 lines of bash script (exceeds ≤25 threshold)
- Step 5: No script provided, pure prose modifications
- Step 8: 79 lines but mostly sequential operations (acceptable)

**Impact**:
- Orchestrator may misclassify execution complexity
- Violates script-first evaluation criteria from CLAUDE.md
- Creates precedent for loose interpretation

**Fix Required**:
1. Step 1: Relabel as "Simple file operation (direct execution)" - remove script wrapper, use direct commands
2. Step 5: Change to "Prose description (semantic file modifications)"
3. Step 8: Keep current label but note it's near complexity threshold

---

### Issue C4: Missing Explicit Tool Usage Instructions

**Location**: Steps 2, 3, 4, 5

**Problem**: Steps involving file creation/modification don't explicitly remind agent to use specialized tools (Read, Write, Edit, Grep) instead of bash commands.

**Evidence from CLAUDE.md**:
> **When delegating tasks, remind agents to:**
> - Use **Read** instead of `cat`, `head`, `tail`
> - Use **Write** instead of `echo >` or `cat <<EOF`
> - **NEVER use heredocs** (`<<EOF`) in bash commands
> - **Critical:** Always include this reminder in task prompts

**Current State**:
- Step 2: No tool usage reminder
- Step 3: Has section 7 "Tool Usage Constraints" in OUTPUT (agent instructions) but not in step execution instructions
- Steps 4-5: No tool usage guidance

**Impact**:
- Weak agents may default to bash file operations
- Violates explicit "always include this reminder" directive
- Inconsistent with project tool usage standards

**Fix Required**:
Add to each file operation step:

```markdown
**Tool Usage**:
- Use Read tool for reading existing files
- Use Write tool for creating new files
- Use Edit tool for modifying existing files
- Use Grep tool for content validation
- Use Bash only for git commands and test execution
- Never use heredocs or bash file redirection
```

---

## Major Issues

### Issue M1: Step Dependencies Graph Incomplete

**Location**: Weak Orchestrator Metadata, lines 29-35

**Problem**: Dependency graph shows:
> - Step 3: After Step 1 (depends on workflow.md move)

But Step 3's objective is "Create TDD task agent baseline" which has NO dependency on Step 1's workflow.md move. The actual dependency would be Step 2 completing (tdd-workflow.md) for reference consistency.

**Evidence**: Step 3 creates `tdd-task.md` baseline template. This doesn't require oneshot-workflow.md to exist first.

**Impact**:
- Orchestrator may enforce unnecessary sequential execution
- Reduces potential parallelization (steps 1-3 could all run parallel)
- Misleading dependency tracking

**Fix Required**:
```markdown
**Step Dependencies**:
- Steps 1-3: Parallel (independent file creation)
- Steps 4-5: Parallel (independent skill updates)
- Step 6: After Steps 1-5 (needs tdd-task.md baseline)
- Step 7: After Step 6 (needs prepare-runbook.py updates)
- Step 8: After Step 7 (final integration)
```

Or if you want to enforce Step 3 after Steps 1-2 for semantic consistency:
```markdown
- Step 3: After Steps 1-2 (ensures workflow docs exist for reference)
```

---

### Issue M2: Validation Commands Use Bash Tools Instead of Specialized Tools

**Location**: All steps' validation sections

**Problem**: Validation sections use bash commands that should use specialized tools:

**Examples**:
- Step 1: `grep "## Oneshot Workflow" agent-core/agents/oneshot-workflow.md`
  - Should use: **Grep tool** with pattern and file path
- Step 2: `grep "## Overview" agent-core/agents/tdd-workflow.md`
  - Should use: **Grep tool**
- Step 3: `test -f agent-core/agents/tdd-task.md`
  - Should use: **Read tool** (file existence confirmed by successful read)

**Evidence from CLAUDE.md**:
> Use **Grep** instead of `grep` or `rg`

**Impact**:
- Inconsistent tool usage across runbook
- Agent may execute bash grep when specialized tool expected
- Violates project tool usage standards in validation phase

**Fix Required**:
Rewrite validation sections to use proper tools:

```markdown
**Validation**:
- File exists: Read `agent-core/agents/oneshot-workflow.md` (successful read confirms existence)
- Contains workflow content: Grep for "Oneshot Workflow" in `agent-core/agents/oneshot-workflow.md`
- File size appropriate: Read tool returns file metadata
```

---

### Issue M3: Step 8 Execution Location Ambiguity

**Location**: Step 8, lines 777-905

**Problem**: Script changes working directory to pytest-md but doesn't clarify whether orchestrator should:
1. Execute from claudeutils and let script handle `cd`, OR
2. Change orchestrator working directory to pytest-md first

**Evidence**:
```bash
cd "$PYTEST_MD_DIR"
```

**Current Metadata**:
- No working directory specified in step instructions
- Orchestrator working directory is `/Users/david/code/claudeutils`

**Impact**:
- Agent may execute from wrong directory
- Git operations may fail if relative paths assumed
- Submodule operations depend on correct working directory

**Fix Required**:
Add explicit instruction:

```markdown
**Working Directory**: Execute from claudeutils root (script handles directory changes)

OR

**Working Directory**: `/Users/david/code/pytest-md` (orchestrator changes dir before execution)
```

Recommended: First option (script handles cd) for safety.

---

### Issue M4: Step 6-7 Success Criteria Don't Match Execution Model

**Location**: Steps 6 and 7

**Problem**: Steps marked as "Separate planning session required" but success criteria say:
> **Success Criteria**:
> - Separate planning session initiated
> - Planning request includes all requirements
> - Step execution deferred until plan complete

**Conflict**:
- Success criteria imply step execution creates planning request
- But "Execution Model: Separate planning session required" suggests step is blocked/skipped
- Unclear if orchestrator should CREATE planning request or just MARK step as blocked

**Impact**:
- Orchestrator doesn't know what action to take
- "Success" is ambiguous - is it creating request file or skipping step?
- Report path suggests creating planning request file, but execution model says "separate session"

**Fix Required**:
Clarify execution model:

**Option A** (Create planning request):
```markdown
**Execution Model**: Sonnet

**Implementation**:
Create planning request file at `plans/tdd-integration/reports/step-6-planning-request.md` with:
- Task objective
- Complexity rationale
- Planning requirements (from current step content)
- Dependencies
- Reference material

**Success Criteria**:
- Planning request file created
- Contains all planning requirements
- Step marked as BLOCKED pending separate planning session
```

**Option B** (Skip step):
```markdown
**Execution Model**: N/A - Deferred to separate planning session

**Implementation**:
Mark step as BLOCKED. No execution in this runbook.

**Success Criteria**:
- Step marked BLOCKED in execution log
- User notified that separate planning required
- Reference to this step's requirements provided for future planning
```

Recommend Option A - creates actionable artifact for future work.

---

### Issue M5: Prerequisites Verification Incomplete

**Location**: Weak Orchestrator Metadata, lines 50-54

**Problem**: Prerequisites show verification status but missing critical checks:

**Current**:
```markdown
**Prerequisites**:
- agent-core submodule accessible at `agent-core/` (✓ verified via ls)
- `agents/workflow.md` exists (✓ verified via ls)
- pytest-md available at `~/code/pytest-md/` (path from design doc)
- Skills modifiable in `agent-core/skills/` (✓ verified via ls)
```

**Missing**:
- No verification that pytest-md directory exists (only "path from design doc")
- No verification that current working directory is `/Users/david/code/claudeutils`
- No verification that git is available for Step 8 submodule operations
- No verification that python3 is available for Step 6 script validation

**Impact**:
- Step 8 may fail with cryptic error if pytest-md missing
- Step 6 validation criteria can't be met without python3
- Silent assumptions about environment

**Fix Required**:
Add comprehensive prerequisite checks or mark unverified:

```markdown
**Prerequisites**:
- Working directory: `/Users/david/code/claudeutils` (✓ verified)
- agent-core submodule accessible at `agent-core/` (✓ verified via ls)
- `agents/workflow.md` exists (✓ verified via ls)
- Skills modifiable in `agent-core/skills/` (✓ verified via ls)
- pytest-md available at `~/code/pytest-md/` (⚠ NOT VERIFIED - will check in Step 8)
- Git available for submodule operations (⚠ NOT VERIFIED - required for Step 8)
- Python3 available for script validation (⚠ NOT VERIFIED - required for Step 6 if executed)
```

---

## Minor Issues

### Issue m1: Common Context Has Redundant Sections

**Location**: Common Context, lines 58-138

**Problem**: "Project Paths" section (lines 105-120) duplicates information from "File Locations" (lines 62-66).

**Evidence**:
- File Locations lists: `agent-core/agents/`, `agent-core/skills/`, etc.
- Project Paths lists same information with additional context

**Impact**: Minor - slightly verbose but not harmful

**Fix**: Merge into single "File Locations and Paths" section with consolidated information.

---

### Issue m2: Step 3 File Size Range Too Narrow

**Location**: Step 3, validation section, lines 441-444

**Problem**: Expected file size is 6000-10000 bytes but success criteria calls protocol "comprehensive" which could easily exceed 10000 bytes.

**Evidence**:
- 7 required sections with detailed protocols
- Code examples for multiple commands
- Structured log entry template
- Could reasonably be 12000+ bytes

**Impact**: Agent may question success if file exceeds upper bound

**Fix**: Widen range to 6000-12000 bytes or make upper bound approximate "~10000 bytes"

---

### Issue m3: Step 4 File Size Increase Vague

**Location**: Step 4, lines 540-544

**Problem**: "File size increase of ~500-1000 bytes" is imprecise for validation.

**Evidence**: Adding 5 major sections could easily exceed 1000 bytes. The TDD mode documentation alone could be 1500+ bytes.

**Impact**: Agent may question completeness if exceeds range

**Fix**:
- Change to "File size increase of 800-1500 bytes" (more realistic), OR
- Change success criteria to focus on content presence, not size

---

### Issue m4: Inconsistent Error Escalation Format

**Location**: Various steps

**Problem**: Some steps have both "Unexpected Result Handling" and "Error Conditions" sections which overlap.

**Example - Step 1**:
- "Unexpected Result Handling": If source file missing: STOP
- "Error Conditions": File not found → STOP and report to user

These describe the same condition twice.

**Impact**: Minor redundancy, slight confusion

**Fix**: Consolidate into single "Error Handling" section:

```markdown
**Error Handling**:
- File not found → STOP and report (source missing or destination dir missing)
- Permission denied → STOP and report
- Copy operation fails → STOP and report with error details
```

---

### Issue m5: Step 2 Expected File Size Range Overlaps with Validation Range

**Location**: Step 2, lines 278-292

**Problem**:
- Expected Outcome: "File size 5000-8000 bytes"
- Validation: "File size 5000-8000 bytes"
- Success Criteria: "File size indicates substantial documentation (5000-8000 bytes)"

But earlier states:
- Expected Outcome: "substantial documentation"
- Validation: "File size 5000-8000 bytes"

**Conflict**: If file is 4800 bytes (just under) but contains all 7 sections with good content, is it success or failure?

**Impact**: Creates ambiguity about what matters - byte count or content completeness

**Fix**: Make file size a guideline, not hard requirement:

```markdown
**Validation**:
- File exists and contains all 7 required sections
- Content accurately reflects design document
- File size typically 5000-8000 bytes (may vary with detail level)
- Markdown syntax valid
```

---

### Issue m6: Missing Report File Directory Creation

**Location**: All steps

**Problem**: Steps specify report paths like `plans/tdd-integration/reports/step-1-report.md` but don't verify or create the `reports/` directory.

**Impact**:
- First step execution may fail writing report if directory missing
- Orchestrator may need to handle directory creation

**Fix**: Add to orchestrator instructions:

```markdown
**Before Execution**:
- Ensure reports directory exists: `mkdir -p plans/tdd-integration/reports/`
```

Or add to prerequisites:
```markdown
- Reports directory exists: `plans/tdd-integration/reports/` (create if missing)
```

---

### Issue m7: Step 8 Backup Logic May Fail Silently

**Location**: Step 8, lines 830-851

**Problem**: Backup commands use `|| true` to suppress errors:

```bash
cp -r .claude/skills/* .backup/skills/ 2>/dev/null || true
```

**Conflict with Error Handling Rule**:
From CLAUDE.md:
> Errors should never pass silently.
> Never use error suppression patterns (e.g., `|| true`, `2>/dev/null`)

**Impact**:
- Violates explicit project error handling standards
- If backup fails, user won't know until they need it

**Fix**: Remove error suppression:

```bash
echo "Backing up old skills..."
mkdir -p .backup/skills
if [[ -d .claude/skills ]] && [[ "$(ls -A .claude/skills)" ]]; then
  cp -r .claude/skills/* .backup/skills/
  echo "✓ Old skills backed up to .backup/skills/"
else
  echo "ℹ No skills to backup (directory empty or missing)"
fi
```

---

## Evaluation Summary

### 1. Completeness - All design decisions documented?

**Rating**: ✅ GOOD

**Findings**:
- Design decisions section present (lines 938-963)
- Key architectural choices documented
- Rationale provided for each decision
- Note: Steps 6-7 deferral is documented as Decision 1

**Missing**:
- No decision documented about tool usage standards (why specialized tools vs bash)
- No decision about error escalation model choice

**Verdict**: Adequate for execution, minor gaps acceptable.

---

### 2. Executability - Can weak agents execute with just this runbook?

**Rating**: ❌ INSUFFICIENT

**Findings**:
- **Critical blockers** (Issues C1-C4):
  - Inline script execution model undefined
  - Script contradicts task agent tool rules
  - Missing explicit tool usage instructions
  - Inconsistent script evaluation

**Impact**: Weak orchestrator (haiku/sonnet) cannot execute Steps 1, 2, 3, 4, 5, 8 without clarification on:
- How to execute inline scripts (direct vs file-write)
- Which tools to use for file operations
- Whether to follow bash script as written or translate to specialized tools

**Verdict**: NEEDS_REVISION before weak orchestrator execution.

---

### 3. Script vs Direct - Are complexity assessments appropriate?

**Rating**: ⚠️ MIXED

**Findings**:
- **Appropriate**: Step 8 (75 lines, sequential ops, marked as script)
- **Questionable**: Step 1 (32 lines, marked "small script" but exceeds ≤25 guideline)
- **Incorrect**: Step 5 (marked "small script" but is prose description)

**Evidence from CLAUDE.md**:
> **≤25 lines**: Execute directly with Bash - don't delegate to agent

**Verdict**: Needs recategorization for Steps 1 and 5. Step 8 acceptable.

---

### 4. Validation - Are success criteria measurable and specific?

**Rating**: ✅ MOSTLY GOOD

**Findings**:
- **Strong**: File existence checks, content verification via grep, size ranges
- **Weak**: File size ranges sometimes arbitrary (Issue m2, m3, m5)
- **Problematic**: Validation uses bash commands instead of specialized tools (Issue M2)

**Examples of Good Validation**:
- Step 1: File exists, size matches source, readable content
- Step 3: Contains all sections, specific byte range, grep for commands

**Examples Needing Improvement**:
- Step 4: File size increase vague (500-1000 bytes)
- Step 2: Size range conflict with actual content needs

**Verdict**: Mostly measurable, needs tool usage correction.

---

### 5. Error Handling - Are escalation triggers clear and actionable?

**Rating**: ✅ GOOD

**Findings**:
- **Strong**: Each step has "Error Conditions" section
- **Clear**: Escalation path (Sonnet → User) defined in metadata
- **Actionable**: Specific conditions trigger specific actions (STOP and report)

**Issues**:
- Some redundancy between "Unexpected Result Handling" and "Error Conditions" (Issue m4)
- Step 8 violates error suppression rule (Issue m7)

**Verdict**: Well-defined with minor cleanup needed.

---

### 6. Metadata - Is weak orchestrator metadata complete and accurate?

**Rating**: ⚠️ NEEDS IMPROVEMENT

**Findings**:
- **Complete**: Total steps, execution model, error escalation, report locations
- **Incomplete**: Prerequisites not fully verified (Issue M5)
- **Inaccurate**: Step dependencies incorrect (Issue M1)
- **Missing**: Orchestrator working directory specification

**Critical Gaps**:
- Step 3 dependency on Step 1 is incorrect (should be parallel or depend on Step 2)
- pytest-md prerequisite not verified (will fail at Step 8)

**Verdict**: Needs correction for accurate orchestrator execution.

---

### 7. Step Dependencies - Are dependencies correctly identified?

**Rating**: ⚠️ NEEDS CORRECTION

**Findings**:
- **Correct**: Step 6 after Steps 1-5 (needs tdd-task.md)
- **Correct**: Step 7 after Step 6 (needs prepare-runbook.py)
- **Incorrect**: Step 3 after Step 1 (no actual dependency)
- **Questionable**: Step 8 listed as "After Step 7" but in orchestrator instructions says "can proceed independently"

**Contradiction**:
- Metadata (line 33): "Step 3: After Step 1 (depends on workflow.md move)"
- Orchestrator Instructions (line 909): "Execute steps 1-2 in parallel (independent file creation)"
- Reality: Step 3 creates tdd-task.md, has no dependency on workflow.md location

**Verdict**: Dependencies need review and correction.

---

## Recommendations

### Immediate Actions (Before Execution)

1. **Fix Critical Issue C1**: Clarify inline script execution model for Steps 1 and 8
2. **Fix Critical Issue C2**: Rewrite Step 1 to use Read/Write tools instead of bash cp
3. **Fix Critical Issue C4**: Add explicit tool usage instructions to all file operation steps
4. **Fix Major Issue M1**: Correct step dependency graph (Steps 1-3 should be parallel)
5. **Fix Major Issue M4**: Clarify Steps 6-7 execution model (create planning request vs skip)

### High-Priority Improvements

6. **Fix Major Issue M2**: Rewrite validation sections to use specialized tools
7. **Fix Major Issue M5**: Verify all prerequisites or mark as unverified
8. **Fix Minor Issue m7**: Remove error suppression from Step 8 backup logic

### Low-Priority Improvements

9. Consolidate redundant sections in Common Context (Issue m1)
10. Adjust file size ranges to be more realistic (Issues m2, m3, m5)
11. Consolidate error handling sections (Issue m4)
12. Add reports directory creation to prerequisites (Issue m6)

---

## Conclusion

This runbook demonstrates strong structural design with comprehensive Common Context, detailed validation criteria, and clear error handling. However, **critical issues around tool usage and execution model prevent weak orchestrator execution** in its current form.

**Primary blockers**:
1. Inline scripts conflict with task agent tool usage rules
2. Missing execution model specifications for script handling
3. Inconsistent tool usage (bash grep vs Grep tool)
4. Incorrect step dependencies

**Estimated effort to resolve**: 2-3 hours of focused revision

**Recommendation**: Address Critical Issues C1-C4 and Major Issues M1, M4-M5 before attempting orchestrator execution. Other issues can be addressed during execution or post-execution review.

---

## Revision Checklist

- [ ] C1: Define inline script execution model (direct vs file-write)
- [ ] C2: Rewrite Step 1 to use Read/Write tools
- [ ] C3: Recategorize Steps 1, 5 script evaluations
- [ ] C4: Add tool usage instructions to all file operation steps
- [ ] M1: Correct step dependency graph
- [ ] M2: Rewrite validations to use specialized tools
- [ ] M4: Clarify Steps 6-7 execution model
- [ ] M5: Complete prerequisite verification
- [ ] m7: Remove error suppression from Step 8
- [ ] M3: Specify working directory for Step 8 execution

