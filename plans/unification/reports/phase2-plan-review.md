# Phase 2 Execution Plan Review

**Plan**: plans/unification/phase2-execution-plan.md
**Reviewer**: Sonnet
**Date**: 2026-01-18
**Status**: NEEDS_REVISION

---

## Executive Summary

The Phase 2 execution plan has **critical blockers** preventing execution by weak agents. The plan assumes Phase 1 is complete, but Phase 1 was never executed. Additionally, there are path inconsistencies, missing design decisions, and unclear success criteria that would cause execution failures.

**Overall Assessment**: NEEDS_REVISION

**Critical Issues**: 3
**Major Issues**: 4
**Minor Issues**: 2

---

## 1. Completeness Review

### 1.1 Critical Issue: Phase 1 Prerequisite Not Met

**Finding**: Plan line 26-29 lists prerequisites including "Phase 1 complete (agent-core repo exists with fragments/)", but Phase 1 was never executed.

**Evidence**:
- `scratch/consolidation/` directory is empty except for a `reports/` subdirectory
- Phase 1 plan (phase1.md) specifies copying ~35 files to `scratch/consolidation/`
- None of these files exist

**Impact**: Steps 2.1 and 2.2 will fail immediately when attempting to diff non-existent files.

**Recommendation**: Either:
1. Add Phase 1 execution as explicit prerequisite step, OR
2. Modify Step 2.1 and 2.2 to work directly with source files without scratch/ copies

---

### 1.2 Critical Issue: Path Inconsistencies in Step 2.1

**Finding**: Step 2.1 (lines 40-47) references wrong source paths.

**Plan states**:
```bash
diff -u /Users/david/code/emojipack/agents/compose.sh \
        agents/compose.sh \
```

**Problem**: Phase 1 plan indicates files should be copied to `scratch/consolidation/emojipack/compose.sh`, but Step 2.1 uses direct paths. This creates ambiguity about execution model.

**Recommendation**: Clarify whether Phase 2 operates on:
- scratch/ copies (requires Phase 1), OR
- Direct source paths (Phase 1 becomes optional analysis step)

Choose ONE model and update all steps consistently.

---

### 1.3 Major Issue: Deferred Validation Decision

**Finding**: Line 171 states "No explicit validation step required - outputs are analysis artifacts, validated by usage in later phases."

**Problem**: This defers validation to future phases, creating risk that:
- Invalid analysis goes undetected
- Phase 3 agents receive incomplete/incorrect inputs
- Errors compound across phases

**Recommendation**: Add validation criteria for each step:
- Step 2.1: Verify patch file is valid (diff succeeded), document whether files are identical
- Step 2.2: Verify all 3 patch files created, at least one shows differences
- Step 2.3: Verify analysis document has all 6 sections with line numbers and classifications

---

### 1.4 Major Issue: Missing Error Recovery Decisions

**Finding**: Error conditions are identified (lines 59-62, 101-103, 134-136) but recovery strategy is missing.

**Example**: Step 2.1 line 60: "Source file not found → Escalate to sonnet (verify path)"

**Problem**: What happens after escalation? Plan doesn't specify:
- Does execution stop completely?
- Can weak orchestrator retry with corrected path?
- Does sonnet take over the step?

**Recommendation**: Document error recovery pattern:
1. Haiku agent reports error with context
2. Orchestrator escalates to sonnet with error details
3. Sonnet analyzes and either: fixes prerequisite, updates plan, or escalates to user
4. Clear handoff protocol for retry vs abort

---

### 1.5 Major Issue: Step 2.3 Implementation Ambiguity

**Finding**: Step 2.3 (lines 111-141) says "Direct execution (read + analysis + write, research task not scripting)" but doesn't provide implementation template.

**Problem**: Lines 118-130 list what to do but not HOW to do it. For example:
- "Analyze sections per guidance" - what does analysis output look like?
- "Target location in agent-core" - which specific directories?
- "Extraction plan" - what format? What level of detail?

**Comparison**: Steps 2.1 and 2.2 provide exact bash commands. Step 2.3 provides requirements but no implementation guidance.

**Recommendation**: Either:
1. Provide analysis template showing expected output format, OR
2. Reference existing analysis documents as examples, OR
3. Acknowledge this requires sonnet (not haiku) due to judgment needed

---

### 1.6 Minor Issue: Success Criteria Vagueness

**Finding**: Line 138 states "Analysis document complete with all 6 sections mapped" but doesn't define what "mapped" means.

**Problem**: Weak agent cannot verify task completion without concrete criteria.

**Example of concrete criteria**:
- Each section has start/end line numbers
- Each section has classification tag (reusable|project-specific)
- Reusable sections have target path in agent-core
- Document ends with extraction plan (numbered steps)

**Recommendation**: Replace "mapped" with verifiable checklist in success criteria.

---

## 2. Weak Agent Executability Review

### 2.1 Critical Issue: Haiku Cannot Execute Step 2.3

**Finding**: Line 18 states "Execution Model: Haiku for all steps (simple file operations and analysis)"

**Problem**: Step 2.3 requires:
- Understanding section boundaries (judgment)
- Classifying content as reusable vs project-specific (semantic analysis)
- Mapping sections to agent-core locations (architectural knowledge)
- Creating actionable extraction plan (strategic planning)

These are NOT "simple file operations" - they require sonnet-level judgment.

**Evidence**: The design doc (design.md line 480-486) notes this work was done by opus during design, suggesting complexity beyond haiku capability.

**Recommendation**: Change metadata line 17 to:
```
**Execution Model**: Haiku for steps 2.1-2.2, Sonnet for step 2.3
```

---

### 2.2 Major Issue: Missing File Path Completeness

**Finding**: Step 2.3 references "pytest-md CLAUDE.md" but doesn't verify file exists or provide fallback.

**Evidence**: Attempted read of `/Users/david/code/pytest-md/CLAUDE.md` returned "File does not exist."

**Problem**: Plan assumes source files exist but doesn't handle missing files gracefully.

**Recommendation**: Add prerequisite verification step or file existence checks with clear error messages.

---

### 2.3 Minor Issue: Report Path Inconsistency

**Finding**: Steps 2.1 and 2.2 use `plans/unification/reports/phase2-step{1,2}-execution.md` but Step 2.3 uses `scratch/consolidation/analysis/pytest-md-fragmentation.md`

**Problem**: Inconsistent report location pattern makes orchestrator tracking difficult.

**Recommendation**: Either:
1. All execution logs go to `plans/unification/reports/`, analysis artifacts to `scratch/consolidation/analysis/`, OR
2. Combine: execution log AND analysis artifact for Step 2.3

Current plan conflates these two concepts in Step 2.3.

---

## 3. Script vs Direct Execution Review

### 3.1 Assessment: Choices Well-Justified

**Finding**: Lines 153-159 provide clear rationale for direct execution.

**Evaluation**:
- Step 2.1: 1 diff command = clearly ≤25 lines ✓
- Step 2.2: 3 similar diffs = ~12 lines ✓
- Step 2.3: Research/analysis task, not automation ✓

**Recommendation**: No changes needed. Threshold and justification are appropriate.

---

## 4. Missing Design Decisions

### 4.1 Major Issue: Dependency Ordering Not Documented

**Finding**: Plan lists 3 steps but doesn't specify whether they must run sequentially or can run in parallel.

**Analysis**:
- Step 2.1 and 2.2 appear independent (different source files)
- Step 2.3 appears independent from 2.1/2.2
- All could potentially run in parallel

**Problem**: Weak orchestrator doesn't know if it can parallelize execution.

**Recommendation**: Add to metadata section:
```
**Step Dependencies**: All steps independent, can execute in parallel
```

OR if there are dependencies:
```
**Step Dependencies**:
- Steps 2.1, 2.2: Independent, can run in parallel
- Step 2.3: Requires 2.1 completion if ... [specify reason]
```

---

### 4.2 Finding: Error Condition Coverage Good But Incomplete

**Finding**: Each step lists 2-3 error conditions, which is good. However, some common errors are missing.

**Missing error conditions**:
- Disk full / write permission denied for output files
- Invalid diff output (binary files, encoding issues)
- Empty source files (exist but have no content)

**Recommendation**: Add generic error escalation rule:
```
**Generic Error Conditions** (apply to all steps):
- Output directory not writable → Escalate to sonnet
- Unexpected file format (binary, invalid encoding) → Escalate to sonnet
- Any other errors not explicitly handled → Stop and escalate to sonnet
```

---

### 4.3 Finding: Analysis Artifact Format Undefined

**Finding**: Step 2.3 produces "analysis document with actionable fragmentation plan" but format is not specified.

**Problem**: Downstream phases (3, 4) need to consume this artifact. Without format specification:
- Phase 3 agents may misinterpret analysis
- Manual rework may be needed
- Plan iteration cycles multiply

**Recommendation**: Define analysis document structure:
```markdown
# pytest-md CLAUDE.md Fragmentation Analysis

## Section 1: Commands/Environment (lines X-Y)
**Classification**: project-specific
**Rationale**: [why it's project-specific]
**Action**: Remains in pytest-md/CLAUDE.md

## Section 2: Persistent vs Temporary (lines X-Y)
**Classification**: reusable
**Rationale**: [why it's reusable]
**Target**: agent-core/fragments/file-organization.md
**Extraction**: [specific steps to extract]

[... repeat for all 6 sections ...]

## Extraction Plan
1. Create agent-core/fragments/file-organization.md with Section 2 content
2. Create agent-core/fragments/orchestration.md with Section 4 content
3. Create agent-core/fragments/documentation.md with Section 6 content
4. Update pytest-md/CLAUDE.md to reference fragments
5. Test composed output matches original semantics
```

---

## 5. Weak Orchestrator Format Review

### 5.1 Finding: Metadata Section Mostly Complete

**Finding**: Lines 14-30 provide orchestrator metadata.

**Strengths**:
- Total steps accurate (3) ✓
- Execution model specified (needs correction per 2.1) ✓
- Error escalation trigger clear ✓
- Report location pattern defined ✓
- Success criteria present (needs enhancement per 1.6) ✓

**Recommendation**: Enhance "Success Criteria" to be more measurable:

```markdown
**Success Criteria**:
- Step 2.1: compose-sh-diff.patch created, size documented (0 bytes = identical)
- Step 2.2: 3 justfile patch files created, at least 1 non-empty
- Step 2.3: pytest-md-fragmentation.md created with:
  - All 6 sections documented with line numbers
  - Each section has classification tag
  - Reusable sections have target paths specified
  - Extraction plan with numbered steps
- No blocking errors (missing files, permission issues)
- All execution reports written to expected paths
```

---

### 5.2 Finding: Prerequisites Section Misleading

**Finding**: Lines 26-29 list prerequisites that are not actually met.

**Current**:
```markdown
**Prerequisites**:
- Phase 1 complete (agent-core repo exists with fragments/)
- Source projects readable at documented paths
- scratch/consolidation/analysis/ directory created
```

**Reality Check**:
- ✗ Phase 1 NOT complete (scratch/ is empty)
- ✓ agent-core exists but Phase 1's scratch/ setup was never done
- ? Source projects - not verified
- ✗ scratch/consolidation/analysis/ does not exist

**Recommendation**: Update prerequisites to reality:
```markdown
**Prerequisites**:
- agent-core repo exists at /Users/david/code/agent-core (✓ verified)
- Source files readable:
  - /Users/david/code/emojipack/agents/compose.sh
  - /Users/david/code/claudeutils/agents/compose.sh
  - /Users/david/code/*/justfile (tuick, emojipack, pytest-md)
  - /Users/david/code/pytest-md/CLAUDE.md
- scratch/consolidation/analysis/ directory will be created in Step 2.1
- NOTE: Phase 1 scratch/ setup is NOT required for Phase 2
```

---

### 5.3 Finding: Context Handoff Protocol Clear

**Finding**: Lines 176-193 provide clear example task prompt.

**Strengths**:
- Plan path specified ✓
- Step reference clear ✓
- Report path explicit ✓
- Return format specified ✓

**Recommendation**: No changes needed. This section is exemplary.

---

## 6. Additional Observations

### 6.1 Positive: Design Decisions Section

Lines 144-173 provide valuable rationale documentation. This is excellent for future maintenance and iteration.

### 6.2 Positive: Direct Execution Rationale

Lines 153-159 clearly justify why no scripts are needed. This demonstrates appropriate threshold application.

### 6.3 Concern: "per phase2.md comment" Assumption

Line 14 (Step 2.1) says "# Should be identical" referencing phase2.md. If files are NOT identical, Step 2.1 has no guidance on what to do.

**Recommendation**: Add:
```bash
# Expected: identical (per phase2.md), but if different:
# 1. Document differences in execution report
# 2. Escalate to sonnet for path verification
# 3. Do NOT proceed to Step 2.2 until resolved
```

---

## 7. Summary of Required Changes

### Critical (Must Fix Before Execution)

1. **Resolve Phase 1 dependency conflict** - Update paths to work without Phase 1 or execute Phase 1 first
2. **Fix path inconsistencies** - Choose scratch/ vs direct paths model consistently
3. **Change Step 2.3 execution model** - Use sonnet not haiku for analysis task

### Major (Strongly Recommended)

4. **Add validation criteria** - Specify what makes each output valid/complete
5. **Define error recovery protocol** - Document what happens after escalation
6. **Specify Step 2.3 implementation** - Provide analysis template or acknowledge judgment needed
7. **Add dependency ordering** - Clarify if steps can run in parallel
8. **Define analysis artifact format** - Template for pytest-md-fragmentation.md

### Minor (Quality Improvements)

9. **Verify file existence** - Check prerequisites before execution
10. **Standardize report locations** - Clarify execution log vs analysis artifact distinction
11. **Enhance success criteria** - Make measurability explicit with checklists

---

## 8. Recommended Plan Structure Changes

### Before Execution Section (NEW)

```markdown
## Before Execution: Verify Prerequisites

Run these checks before delegating to haiku agents:

1. Verify source files exist:
   ```bash
   test -f /Users/david/code/emojipack/agents/compose.sh || echo "MISSING: emojipack compose.sh"
   test -f /Users/david/code/claudeutils/agents/compose.sh || echo "MISSING: claudeutils compose.sh"
   # ... repeat for all source files
   ```

2. Create output directory:
   ```bash
   mkdir -p scratch/consolidation/analysis
   ```

3. Decision point: Execute Phase 1 first?
   - If YES: Delegate Phase 1 execution, then return to Phase 2
   - If NO: Update Step 2.1, 2.2 paths to use direct source paths
```

### Updated Step 2.3 Metadata

```markdown
## Step 2.3: Analyze pytest-md CLAUDE.md Fragmentation

**Objective**: Map pytest-md CLAUDE.md sections to reusable vs project-specific

**Script Evaluation**: Analysis task requiring semantic judgment (sonnet needed)

**Execution Model**: Sonnet (NOT haiku - requires classification judgment)
```

---

## 9. Conclusion

The Phase 2 execution plan demonstrates good structure and documentation practices, particularly in the Design Decisions and Context sections. However, **critical prerequisite issues and execution model mismatches prevent weak agent execution** without significant revision.

**Primary Blockers**:
1. Phase 1 dependency conflict (plan assumes it's complete, but it's not)
2. Step 2.3 incorrectly assigned to haiku (requires sonnet for semantic analysis)
3. Missing validation and error recovery protocols

**Recommended Action**: Address critical issues (items 1-3) before attempting execution. Major issues (items 4-8) should be addressed to ensure downstream phase success.

**Estimated Revision Effort**: 2-3 hours for sonnet to address all critical and major issues.

**Overall Assessment**: NEEDS_REVISION (not ready for weak orchestrator execution)
