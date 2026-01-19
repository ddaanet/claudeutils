# Plan: Formalize Phase 2 Validation Patterns in agent-core

## Context

Phase 2 execution successfully validated the weak orchestrator pattern with 5/5 hypotheses confirmed. This plan formalizes those patterns into agent-core documentation for reuse across projects.

**Validation results:**
- ✅ Haiku reliable for direct execution
- ✅ Sonnet effective for semantic analysis
- ✅ Error escalation works as designed
- ✅ Quiet execution + terse return efficient
- ✅ Plan-specific agents provide sufficient context

**Source material:** `plans/unification/reports/phase2-lessons-learned.md`

**Agent-core location:** `/Users/david/code/agent-core` (additional working directory)

## Objectives

1. Create pattern documentation for plan-specific agents (context caching)
2. Formalize error classification taxonomy with escalation rules
3. Document prerequisite validation checklist and methodology
4. Create commit delegation pattern documentation
5. Update existing patterns with Phase 2 validation results
6. Provide automated agent generation script

## Implementation Strategy

**Approach:** Hybrid documentation structure
- NEW pattern doc: Plan-specific agents (orthogonal to weak orchestrator)
- UPDATE existing: Weak orchestrator with validation results + error taxonomy
- NEW fragments: Error classification, prerequisite validation, commit delegation
- NEW script: Automated plan-specific agent generation
- UPDATE cross-references: Integrate new docs with existing patterns

**Organization:**
```
agent-core/
├── pattern-plan-specific-agent.md    # NEW
├── pattern-weak-orchestrator.md      # UPDATE
├── fragments/
│   ├── error-classification.md       # NEW
│   ├── prerequisite-validation.md    # NEW
│   ├── commit-delegation.md          # NEW
│   └── delegation.md                 # UPDATE
├── scripts/
│   └── create-plan-agent.sh          # NEW
└── skills/task-plan/skill.md         # UPDATE
```

## Critical Files

**NEW files (5):**
1. `/Users/david/code/agent-core/pattern-plan-specific-agent.md` (~280 lines)
2. `/Users/david/code/agent-core/fragments/error-classification.md` (~90 lines)
3. `/Users/david/code/agent-core/fragments/prerequisite-validation.md` (~75 lines)
4. `/Users/david/code/agent-core/fragments/commit-delegation.md` (~45 lines)
5. `/Users/david/code/agent-core/scripts/create-plan-agent.sh` (~160 lines)

**UPDATE files (3):**
1. `/Users/david/code/agent-core/pattern-weak-orchestrator.md` (add ~100 lines)
2. `/Users/david/code/agent-core/fragments/delegation.md` (add ~20 lines)
3. `/Users/david/code/agent-core/skills/task-plan/skill.md` (add ~30 lines)

## Detailed Steps

### Step 1: Create Pattern: Plan-Specific Agent

**File:** `/Users/david/code/agent-core/pattern-plan-specific-agent.md`

**Content structure** (following pattern-weak-orchestrator.md template):

1. **Problem Statement**
   - Context churn in multi-step plans (~1000+ tokens/step)
   - Noise accumulation when reusing agents
   - Inconsistent context across steps

2. **Solution**
   - Plan-Specific Agent = Baseline Agent + Plan Context
   - Created once, cached as file, reused for all steps
   - Fresh invocation per step (no noise)

3. **Implementation**
   - Agent structure (YAML frontmatter + baseline + plan context)
   - Generation process (planning agent creates, script automates)
   - File location (`.claude/agents/<plan-name>-task.md`)
   - Invocation pattern (orchestrator loads agent, appends step)

4. **Integration**
   - With weak orchestrator (delegation target)
   - With task-plan skill (Point 4: agent generation step)
   - With quiet execution (reports to files)

5. **Examples**
   - Phase 2 validation walkthrough (phase2-task.md)
   - Evidence: 3 steps, 0 context requests
   - Token analysis: ~30KB overhead vs ~3000 tokens saved

6. **Design Rationale**
   - Token efficiency (break-even at 2-3 steps)
   - Context isolation (fresh agent per step)
   - Specialization (agent knows plan goals/constraints)
   - Reviewability (agent prompt visible)

7. **Status**
   - Validated in Phase 2 execution
   - 5/5 hypotheses confirmed
   - Ready for production use

**Key data from Phase 2:**
- Agent file: `.claude/agents/phase2-task.md`
- Steps executed: 3 (all successful)
- Context requests: 0 (agent had sufficient context)
- Token savings: ~3000 tokens (1000/step × 3 steps)

### Step 2: Create Fragment: Error Classification

**File:** `/Users/david/code/agent-core/fragments/error-classification.md`

**Content:**

1. **Taxonomy table** (4 categories × columns: definition, examples, trigger, escalation)
   - Prerequisite Failures (file missing, path mismatch → sonnet diagnostic)
   - Execution Errors (tests fail, build error → simple: sonnet / complex: opus)
   - Unexpected Results (wrong output despite success → sonnet analysis)
   - Ambiguity Errors (unclear requirements → user clarification)

2. **Detailed classification** for each category:
   - Triggers (when this error type occurs)
   - Examples (concrete instances from Phase 2 and general)
   - Escalation path (who handles, how to recover)
   - Prevention strategy

3. **Phase 2 example:**
   - Step 2.3 prerequisite failure (CLAUDE.md vs AGENTS.md)
   - Escalation flow: haiku detected → sonnet diagnosed → corrected → retry
   - Lesson: Prerequisite validation in planning prevents 80% of these

4. **Integration references:**
   - Pattern: pattern-weak-orchestrator.md (expanded Error Classification)
   - Related: prerequisite-validation.md (prevention)

**Format:** Table for quick reference + detailed sections with examples

### Step 3: Create Fragment: Prerequisite Validation

**File:** `/Users/david/code/agent-core/fragments/prerequisite-validation.md`

**Content:**

1. **When to validate:**
   - Planning phase (RECOMMENDED): Verify during plan review
   - Execution phase (DEFENSIVE): Re-check before use

2. **Validation checklist** (4 categories):
   - File Resources (exists, readable, size, format)
   - Directory Resources (exists, writable, not empty)
   - External Dependencies (command available, version, access)
   - Environment (variables set, paths absolute, permissions)

3. **Validation methods:**
   - Bash checks (`[ -f path ]`, `which command`)
   - Read tool (file accessibility)
   - Glob tool (pattern matching)
   - Examples for each method

4. **Integration with planning:**
   - Metadata format for prerequisite section
   - Verification method documentation
   - Example from task-plan skill

5. **Common pitfalls:**
   - Relative paths (avoid)
   - Assumptions without verification
   - Checking only during planning (re-check at execution)

6. **Phase 2 lesson:**
   - Issue: Step 2.3 file path not validated
   - Impact: Escalation required
   - Fix: Add to plan review criteria
   - Prevention rate: ~80% of prerequisite failures

### Step 4: Create Fragment: Commit Delegation

**File:** `/Users/david/code/agent-core/fragments/commit-delegation.md`

**Content:**

1. **Pattern overview:**
   - Responsibility split (orchestrator analyzes, agent executes)
   - Goal: Lean orchestrator context, quality commit messages

2. **Orchestrator responsibilities:**
   - Review changes (`git diff HEAD`)
   - Analyze what/why changed
   - Draft commit message (imperative, 50-72 chars)
   - Delegate with literal message

3. **Commit agent responsibilities:**
   - Receive literal message
   - Execute git commands
   - Return result (commit-hash or error)

4. **Benefits:**
   - Token efficiency (~20 tokens return vs ~1000+ git output)
   - Context cleanliness (git output stays in agent)
   - Message quality (orchestrator analyzes with context)

5. **Example walkthrough:**
   - Orchestrator analysis → message draft
   - Delegation format
   - Agent execution
   - Terse return

6. **Integration:**
   - With weak orchestrator (quiet execution pattern)
   - With commit agent/skill
   - Reference: delegation.md (quiet execution)

### Step 5: Update Pattern: Weak Orchestrator

**File:** `/Users/david/code/agent-core/pattern-weak-orchestrator.md`

**Changes:**

1. **Expand Error Classification section (lines 54-67):**
   - Add formal taxonomy from error-classification.md fragment
   - Include 4 categories with triggers and escalation paths
   - Add prerequisite validation subsection
   - Reference error-classification.md for details

2. **Update Status section (lines 330-350):**
   - Change status: "Proof-of-concept" → "Validated in Phase 2 execution"
   - Update validation approach with Phase 2 results
   - Replace "Open questions" with validated answers:
     - Can haiku classify errors? YES (demonstrated Step 2.3)
     - Does escalation overhead outweigh savings? NO (effective)
     - How often do simple errors need reclassification? Rare
     - Is step-level granularity appropriate? YES
   - Update "Next steps" with formalization complete

3. **Add cross-references:**
   - Reference pattern-plan-specific-agent.md (line ~110)
   - Reference error-classification.md fragment (line ~54)
   - Reference prerequisite-validation.md (after line 67)

**Size change:** 350 lines → ~430 lines (add ~80 lines)

### Step 6: Update Fragment: Delegation

**File:** `/Users/david/code/agent-core/fragments/delegation.md`

**Changes:**

1. **Expand Quiet Execution Pattern section (lines 22-36):**
   - Add explicit return format specification
   - Success: filename (absolute path or relative to working dir)
   - Failure: error message with diagnostic info
   - Add two-phase communication (agent reports, summary agent distills)

2. **Add cross-references:**
   - Reference plan-specific-agent pattern
   - Reference commit-delegation.md for git workflow example

**Size change:** 51 lines → ~70 lines (add ~19 lines)

### Step 7: Create Script: Plan Agent Generator

**File:** `/Users/david/code/agent-core/scripts/create-plan-agent.sh`

**Purpose:** Automate plan-specific agent generation

**Enhancements over existing `build-plan-agent.sh`:**
- CLI argument parsing (--plan, --model, --color, --tools)
- Input validation (plan file exists, readable)
- Output verification (frontmatter valid, content combined)
- Usage help and examples
- Error handling with diagnostics
- Default values (model=haiku, color=cyan)

**Usage:**
```bash
create-plan-agent.sh \
  --plan phase3 \
  --model haiku \
  --color cyan \
  --output .claude/agents \
  plans/phase3-execution-plan.md
```

**Script structure:**
1. Parse arguments
2. Validate inputs (plan file exists, baseline agent exists)
3. Read baseline agent template
4. Read plan file
5. Generate YAML frontmatter
6. Combine baseline + plan context
7. Write to output location
8. Verify output (frontmatter syntax, file created)

**Reference:** Existing `plans/unification/build-plan-agent.sh` for baseline logic

### Step 8: Update Skill: Task Plan

**File:** `/Users/david/code/agent-core/skills/task-plan/skill.md`

**Changes:**

1. **Update Point 2 "Metadata" section** (~line 100):
   - Add prerequisite validation subsection
   - Reference prerequisite-validation.md fragment
   - Include validation checklist format
   - Show example prerequisite section with verification methods

2. **Update template** (~line 320-410):
   - Add enhanced prerequisite section to plan template
   - Include verification method placeholders
   - Show validation checklist format

3. **Add cross-references:**
   - Reference error-classification.md for error escalation
   - Reference pattern-plan-specific-agent.md for agent generation

**Size change:** 440 lines → ~470 lines (add ~30 lines)

## Execution Order

**Phase 1: Core fragments** (parallel, independent)
- Step 2: Create error-classification.md
- Step 3: Create prerequisite-validation.md
- Step 4: Create commit-delegation.md

**Phase 2: Pattern documentation** (depends on fragments)
- Step 1: Create pattern-plan-specific-agent.md
- Step 5: Update pattern-weak-orchestrator.md

**Phase 3: Integration** (depends on patterns)
- Step 6: Update delegation.md fragment
- Step 8: Update task-plan skill

**Phase 4: Tooling** (independent, can run parallel with Phase 1-3)
- Step 7: Create create-plan-agent.sh script

## Validation

**Completeness checks:**
1. Can a practitioner follow pattern docs without additional context?
2. Are all decision points documented?
3. Are examples concrete and realistic?
4. Do cross-references work (files exist, sections correct)?

**Actionability tests:**
1. Can you generate plan-specific agent from pattern doc alone?
2. Can you classify error using taxonomy?
3. Can you validate prerequisites using checklist?
4. Does script generate valid agent files?

**Integration verification:**
1. Pattern documents reference each other correctly
2. Fragments composable without conflicts
3. Script integrates with documented process
4. Skill references updated patterns

**Real-world application:**
- Apply to Phase 3 execution (validate through use)
- Collect feedback on clarity
- Iterate based on practitioner experience

## Key Content Sources

**From Phase 2 validation:**
- Lessons learned: `plans/unification/reports/phase2-lessons-learned.md`
- Execution reports: `plans/unification/reports/phase2-step*.md`
- Phase 2 plan: `plans/unification/phase2-execution-plan.md`
- Plan-specific agent: `.claude/agents/phase2-task.md`

**Existing templates:**
- Pattern structure: `pattern-weak-orchestrator.md`
- Fragment examples: `fragments/delegation.md`, `fragments/hashtags.md`
- Skill structure: `skills/task-plan/skill.md`
- Script baseline: `plans/unification/build-plan-agent.sh`

## Success Criteria

1. **Pattern documentation:**
   - ✅ Plan-specific agent pattern created (~280 lines)
   - ✅ Follows weak-orchestrator template structure
   - ✅ Includes Phase 2 validation evidence
   - ✅ Actionable examples and rationale

2. **Error taxonomy:**
   - ✅ 4 categories documented with triggers
   - ✅ Escalation paths clear
   - ✅ Phase 2 example included
   - ✅ Referenced in weak-orchestrator pattern

3. **Prerequisite validation:**
   - ✅ Checklist covers 4 resource categories
   - ✅ Validation methods documented
   - ✅ Integration with planning shown
   - ✅ Phase 2 lesson captured

4. **Commit delegation:**
   - ✅ Responsibility split documented
   - ✅ Benefits quantified
   - ✅ Example workflow shown
   - ✅ Integration references added

5. **Updates:**
   - ✅ Weak-orchestrator status updated to "Validated"
   - ✅ Open questions answered from Phase 2
   - ✅ Delegation fragment expanded
   - ✅ Task-plan skill references new patterns

6. **Tooling:**
   - ✅ Agent generation script created
   - ✅ Input validation implemented
   - ✅ Usage examples included
   - ✅ Error handling robust

7. **Integration:**
   - ✅ Cross-references work
   - ✅ Patterns composable
   - ✅ Documentation discoverable
   - ✅ Ready for Phase 3 application

## Constraints

**Follow existing conventions:**
- Pattern docs: Problem/Solution/Implementation/Examples/Rationale/Status
- Fragments: Focused, composable, 40-100 lines typical
- Scripts: Input validation, error handling, usage help
- Skills: YAML frontmatter, clear sections, examples

**Quality standards:**
- Concrete examples (not abstract)
- Actionable guidance (practitioners can follow)
- Evidence-based (Phase 2 validation data)
- Cross-referenced (integration story clear)

**Location requirements:**
- Patterns: Repository root
- Fragments: `/fragments/` directory
- Scripts: `/scripts/` directory
- Skills: `/skills/[name]/` directory

## Post-Implementation

**After all steps complete:**
1. Verify cross-references work (run link checker)
2. Test script on sample plan (create agent, verify output)
3. Review documentation for clarity
4. Update README.md with new patterns (if needed)
5. Consider creating pattern catalog/index

**Application to Phase 3:**
- Use pattern-plan-specific-agent.md to create phase3-task.md
- Use error-classification.md during execution
- Use prerequisite-validation.md during plan review
- Validate patterns work in practice

**Metrics to track:**
- Token savings (actual vs estimated)
- Error escalation frequency by category
- Prerequisite validation effectiveness
- Pattern adoption in future phases
