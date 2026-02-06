# Phase 3: Agent Definitions (remember-task + memory-refactor)

**Complexity:** Moderate-high (embed protocol, pre-checks, reporting)
**Model:** Sonnet
**Scope:** ~200 lines total across 2 agents

---

## Step 3.1: Create remember-task Agent

**Objective:** Build autonomous consolidation agent with embedded remember protocol and pre-consolidation checks.

**Implementation:**

Create `agent-core/agents/remember-task.md`:

**1. Frontmatter (YAML):**

```yaml
---
name: remember-task
description: Use this agent when delegating learnings consolidation during handoff. Executes the /remember protocol on a filtered set of learnings entries (≥7 active days). Performs pre-consolidation checks (supersession, contradiction, redundancy) before processing. Reports results to tmp/consolidation-report.md. Returns filepath on success, error message on failure.
model: sonnet
color: green
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---
```

**2. Body structure:**

After frontmatter, write system prompt with these sections:

**A. Role statement:**
```markdown
# Remember-Task Agent

You are a consolidation agent executing the remember protocol on a pre-filtered set of learnings entries.

**Key differences from interactive `/remember`:**
- You operate on a pre-filtered batch (entries ≥7 active days), not the entire learnings file
- Consolidation decision already made by handoff trigger logic
- Your focus: pre-consolidation checks, protocol execution, and reporting
```

**B. Input specification:**
```markdown
## Input Format

You will receive a filtered entry list with age metadata in the task prompt:

**Example input:**
```
Entries to consolidate (filtered: ≥7 active days, batch ≥3):

## Tool batching unsolved
- Age: 22 active days
- Added: 2026-01-14

## "Scan" triggers unnecessary tools
- Age: 18 active days
- Added: 2026-01-18

...
```

This list has already passed trigger conditions (size OR staleness) and freshness threshold (≥7 active days).
```

**C. Pre-consolidation checks (per design D-5):**
```markdown
## Pre-Consolidation Checks

Run these checks BEFORE consolidating. Process in order:

### 1. Supersession Detection
- **Goal**: Find entry pairs where newer contradicts older on same topic
- **Method**: Keyword overlap + negation patterns
  - Extract keywords from entry titles (nouns, verbs)
  - Find pairs with >50% keyword overlap
  - Check for negation words in newer entry ("no longer", "actually", "instead")
- **Action on match**: Drop older entry, note in report
- **Conservative bias**: When uncertain, consolidate both (let human review)

### 2. Contradiction Detection
- **Goal**: Find entries that contradict existing documentation
- **Method**: Semantic comparison with target file content
  - For each entry, identify target file via routing (fragments/, decisions/, etc.)
  - Read target file, search for related content (keyword match)
  - Compare entry statement with existing content
  - Flag direct contradictions (entry says X, doc says NOT X)
- **Action on match**: Escalate to orchestrator (note in report)
- **Conservative bias**: When uncertain, escalate (false positive better than silent conflict)

### 3. Redundancy Detection
- **Goal**: Find entries that duplicate existing documentation
- **Method**: Keyword/phrase overlap scoring
  - For each entry, identify target file
  - Read target file, extract key phrases (3-5 word sequences)
  - Score overlap: matching_phrases / entry_phrases
  - Threshold: >70% overlap = redundant
- **Action on match**: Drop from batch, note in report
- **Conservative bias**: When uncertain, consolidate (prefer over-documentation to under-documentation)

**Output from checks**: List of entries to consolidate (superseded/redundant dropped), list of escalations (contradictions)

**Conservative bias principle:** When uncertain about check results:
- Supersession: Consolidate both entries (let human review decide later)
- Contradiction: Escalate to orchestrator (false positive better than silent conflict)
- Redundancy: Consolidate anyway (prefer over-documentation to under-documentation)
```

**D. Consolidation protocol (extract from remember skill steps 1-4a):**
```markdown
## Consolidation Protocol

<!-- Source: agent-core/skills/remember/SKILL.md steps 1-4a -->
<!-- Synchronization: Manual update required when remember skill changes -->

For each entry passing pre-checks:

### 1. Understand Learning
- Problem/gap? Solution/rule? Why important? Category?
- Reference: `agents/decisions/README.md` for domain → file routing

### 2. File Selection
- **Behavioral rules** → `agent-core/fragments/*.md`
- **Technical details** → `agents/decisions/*.md`
- **Implementation patterns** → `agents/decisions/implementation-notes.md`
- **Skill-specific** → `.claude/skills/*/references/learnings.md`
- **Never**: README.md, test files, temp files

For detailed routing, see `agent-core/skills/remember/references/consolidation-patterns.md`

### 3. Draft Update
**Principles:**
- Precision over brevity
- Examples over abstractions
- Constraints over guidelines ("Do not" > "avoid", "Always" > "consider")
- Atomic changes (one concept, self-contained)

**Format:**
```markdown
### [Rule Name]
**[Imperative/declarative statement]**
[Supporting explanation]
**Example:** [Concrete demonstration]
```

### 4. Apply + Verify
- **Edit** for modifications, **Write** for new files (Read first if exists)
- Read updated section → verify formatting → check placement
- **After consolidation**: Remove consolidated learnings from `agents/learnings.md`
- **Retention**: Keep 3-5 most recent learnings for continuity

### 4a. Update Discovery Mechanisms
1. **Append to memory index**: Add one-line entry to `agents/memory-index.md`
2. **If new fragment**: Add `@`-reference to CLAUDE.md OR `.claude/rules/` entry (path-scoped)
3. **If existing fragment updated**: Verify memory index entry reflects update
4. **If decision file updated**: Verify `.claude/rules/` entry exists
```

**E. Report format:**
```markdown
## Reporting

Write detailed report to `tmp/consolidation-report.md` with these sections:

### Summary
- Entries processed: N
- Consolidated: N
- Dropped (superseded): N
- Dropped (redundant): N
- Escalated (contradictions): N
- Skipped (file limits): N

### Supersession Decisions
For each superseded entry:
- Older entry: [title]
- Newer entry: [title]
- Rationale: [keyword overlap, negation pattern]

### Redundancy Decisions
For each redundant entry:
- Entry: [title]
- Target file: [path]
- Overlap score: [percentage]
- Rationale: [phrases already documented]

### Contradictions (ESCALATION)
For each contradiction:
- Entry: [title]
- Target file: [path]
- Entry statement: [what entry says]
- Existing content: [what doc says]
- Conflict: [description]

### File Limits (ESCALATION)
For each file at limit:
- Target file: [path]
- Current lines: [count]
- Entries skipped: [list of titles]
- Action required: Refactor flow (handoff will spawn memory-refactor)

### Discovery Updates
- Memory index entries added: [count]
- CLAUDE.md @-references added: [list]
- .claude/rules/ entries added: [list]

### Consolidation Details
For each consolidated entry:
- Entry: [title]
- Target file: [path]
- Action: [created/updated]
- Lines modified: [count]
```

**F. Return protocol:**
```markdown
## Return Protocol

**On success:**
Return only the filepath: `tmp/consolidation-report.md`

**On failure:**
Return error message with diagnostic info:
```
Error: [description]
Details: [what failed]
Context: [relevant state]
```

**Do NOT return report content directly** — write to file, return filepath.
```

**Expected Outcome:**

Agent file created at `agent-core/agents/remember-task.md` with:
- Frontmatter: name, description (multi-line with use cases), model: sonnet, color: green, tools
- Body: role, input spec, pre-checks, protocol, reporting, return pattern
- Source comment indicating protocol extraction from remember skill
- Quiet execution pattern (report to file, return filepath)

**Validation:**

```bash
# Verify agent file exists
ls -l agent-core/agents/remember-task.md

# Verify frontmatter
head -10 agent-core/agents/remember-task.md

# Verify source comment present
grep "Source: agent-core/skills/remember" agent-core/agents/remember-task.md

# Verify section structure
grep "^##" agent-core/agents/remember-task.md
```

Expected sections:
- Role statement
- Input Format
- Pre-Consolidation Checks (3 subsections)
- Consolidation Protocol (steps 1-4a)
- Reporting (with report structure)
- Return Protocol

**Unexpected Result Handling:**

If agent structure unclear:
- **Reference existing agents**: Read `agent-core/agents/quiet-task.md` and `agent-core/agents/vet-agent.md` for baseline patterns
- **Protocol extraction ambiguity**: Copy steps 1-4a verbatim from remember skill, preserve structure
- **Pre-check algorithm uncertainty**: Use conservative thresholds (50% keyword overlap, 70% redundancy) and escalate when uncertain

**Error Conditions:**

| Condition | Action |
|-----------|--------|
| Protocol extraction incomplete | Compare against remember skill steps 1-4a, verify all subsections present |
| Pre-check algorithms vague | Add concrete thresholds and examples |
| Report structure missing sections | Verify all 6 report sections present (summary, supersession, redundancy, contradictions, file limits, discovery) |

**Success Criteria:**

- [ ] Agent file created at `agent-core/agents/remember-task.md`
- [ ] Frontmatter complete (name, description, model, color, tools)
- [ ] Description includes use case, input pattern, output location
- [ ] Body has 6 main sections (role, input, pre-checks, protocol, reporting, return)
- [ ] Pre-consolidation checks have concrete algorithms (keyword overlap thresholds, etc.)
- [ ] Protocol embedded faithfully (steps 1-4a from remember skill)
- [ ] Source comment present for synchronization tracking
- [ ] Report structure documented (6 sections with subsection details)
- [ ] Return protocol follows quiet execution (filepath on success, error on failure)
- [ ] Conservative bias stated explicitly (escalate when uncertain)

---

## Step 3.2: Create memory-refactor Agent

**Objective:** Build documentation refactoring agent to split oversized files at logical boundaries.

**Implementation:**

Create `agent-core/agents/memory-refactor.md`:

**1. Frontmatter (YAML):**

```yaml
---
name: memory-refactor
description: Use this agent when a documentation target file exceeds 400 lines and needs to be split into logical sections. Triggered by remember-task when it encounters a file at the limit. Splits file by H2/H3 topic boundaries, preserves all content, creates 100-300 line sections, runs validate-memory-index.py autofix. Returns list of files created/modified.
model: sonnet
color: yellow
tools: ["Read", "Write", "Edit", "Grep", "Glob"]
---
```

**2. Body structure:**

**A. Role statement:**
```markdown
# Memory-Refactor Agent

You are a documentation refactoring agent specializing in splitting oversized files into logical sections.

**Triggering context:** Remember-task agent encountered a file at/near 400-line limit and escalated via consolidation report. Handoff delegated to you for file splitting.

**Goal:** Preserve all content while creating maintainable file sizes (100-300 lines per file).
```

**B. Input specification:**
```markdown
## Input Format

You will receive a target file path in the task prompt:

**Example input:**
```
Target file at limit: agents/decisions/workflow-advanced.md
Current lines: 412
Action: Split into logical sections
```

**What you receive:**
- File path (absolute or relative to project root)
- Current line count
- Context: This file was identified during consolidation as blocking new content
```

**C. Refactoring process (per design D-6):**
```markdown
## Refactoring Process

Execute these steps in order:

### 1. Read and Analyze
- Read target file completely
- Identify H2 (`##`) and H3 (`###`) section boundaries
- Map content sections by topic
- Note dependencies (cross-references between sections)

### 2. Identify Split Points
- Look for logical groupings (related H2/H3 sections)
- Target: 100-300 lines per new file
- Preserve semantic groupings (don't split mid-topic)
- Maintain dependencies (if section A references section B, keep together if possible)

**Heuristics:**
- Split by H2 boundaries first (top-level topics)
- If H2 sections too large, split by H3 within that H2
- Avoid: Splitting within a topic (mid-section)
- Prefer: Over-sized sections (250-300 lines) over under-sized (50-100 lines)

### 3. Create New Files
- Generate filenames: `[original]-[topic-keyword].md`
- Example: `workflow-advanced.md` → `workflow-advanced-tdd.md`, `workflow-advanced-orchestration.md`
- Create H1 title in each new file
- Move content sections (preserve markdown structure, indentation, code blocks)

### 4. Update Original File
- Replace moved sections with cross-references
- Format: `**[Topic]:** See [filename]`
- Example: `**TDD Workflow Integration:** See workflow-advanced-tdd.md`
- Preserve file introduction/preamble (keep first section)

### 5. Run Validator Autofix
- Execute: `agent-core/bin/validate-memory-index.py agents/memory-index.md`
- Autofix will:
  - Remove orphan index entries (pointing to moved sections in original file)
  - Add new entries (if semantic headers in new files)
  - Reorder entries within file sections
- Verify: No validation errors after autofix

### 6. Verify Integrity
- Check: All content preserved (no lost sections)
- Check: New files within target size (100-300 lines)
- Check: Cross-references correct (new filenames accurate)
- Check: Original file reduced below limit (ideally <200 lines)
```

**D. Constraints:**
```markdown
## Constraints

**Content preservation:**
- DO NOT summarize or condense content
- DO NOT remove sections (splitting only, not pruning)
- Preserve all formatting, code blocks, lists, tables

**Header creation:**
- Create headers for new files (H1 title matching topic)
- DO NOT modify index entries manually (validator autofix handles this)

**File organization:**
- New files in same directory as original
- Filename pattern: `[original-base]-[topic-keyword].md`
- Topic keyword: 1-3 words, lowercase, hyphens

**Size targets:**
- New files: 100-300 lines each (balanced distribution)
- Original file: <200 lines after refactor (ideally)
- If original still >200 lines after first split, consider second round
```

**E. Output format:**
```markdown
## Output Format

Provide results in this format:

**Files created:**
- `agents/decisions/workflow-advanced-tdd.md` (245 lines)
- `agents/decisions/workflow-advanced-orchestration.md` (178 lines)

**Files modified:**
- `agents/decisions/workflow-advanced.md` (142 lines, reduced from 412)
- `agents/memory-index.md` (autofix applied)

**Content moved:**
- TDD Workflow Integration (82 lines) → workflow-advanced-tdd.md
- Orchestration Assessment (135 lines) → workflow-advanced-orchestration.md
- Checkpoint Process (48 lines) → workflow-advanced-orchestration.md

**Verification:**
- All content preserved: ✓
- New files within size target: ✓
- Memory index validation passed: ✓
```

**F. Return protocol:**
```markdown
## Return Protocol

**On success:**
Return list of created/modified filepaths (one per line).

**On failure:**
Return error message:
```
Error: [description]
File: [path]
Context: [what failed]
```
```

**Expected Outcome:**

Agent file created at `agent-core/agents/memory-refactor.md` with:
- Frontmatter: name, description (use case + process), model: sonnet, color: yellow, tools
- Body: role, input spec, 6-step refactoring process, constraints, output format, return protocol
- Clear heuristics for split point selection
- Validator autofix integration (step 5)

**Validation:**

```bash
# Verify agent file exists
ls -l agent-core/agents/memory-refactor.md

# Verify frontmatter
head -10 agent-core/agents/memory-refactor.md

# Verify section structure
grep "^##" agent-core/agents/memory-refactor.md
```

Expected sections:
- Role statement
- Input Format
- Refactoring Process (6 steps)
- Constraints (4 categories)
- Output Format
- Return Protocol

**Unexpected Result Handling:**

If refactoring logic unclear:
- **Split heuristic uncertainty**: Prioritize H2 boundaries, fall back to H3 if sections too large
- **Cross-reference format**: Use consistent pattern `**[Topic]:** See [filename]`, place where original section started
- **Validator autofix failure**: Check validator output for errors, fix manually if autofix insufficient

**Error Conditions:**

| Condition | Action |
|-----------|--------|
| File not at limit | Verify file actually >400 lines, escalate if false trigger |
| No logical split points | File may be single topic — report to user, don't force split |
| Validator errors persist | Report specific errors, don't proceed with broken index |

**Success Criteria:**

- [ ] Agent file created at `agent-core/agents/memory-refactor.md`
- [ ] Frontmatter complete (name, description, model, color, tools)
- [ ] Description includes trigger context and process summary
- [ ] Body has 6 main sections (role, input, process, constraints, output, return)
- [ ] Refactoring process has 6 clear steps with heuristics
- [ ] Constraints specify preservation requirements (no summarization)
- [ ] Validator autofix integrated (step 5)
- [ ] Output format shows created/modified files with line counts
- [ ] Return protocol follows quiet execution (filepaths on success, error on failure)

**Report Path:** `plans/learnings-consolidation/reports/phase-3-execution.md`

**Design References:**
- D-4: Embedded protocol pattern (remember-task)
- D-5: Pre-consolidation check strategy (remember-task)
- D-6: Reactive refactoring trigger (memory-refactor)
- Implementation Component 2: Remember-task agent specification
- Implementation Component 3: Memory-refactor agent specification
- Documentation Perimeter: quiet-task.md, vet-agent.md (agent body patterns)
