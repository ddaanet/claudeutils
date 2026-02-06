---
name: learnings-consolidation
model: sonnet
---

# Learnings Consolidation Runbook

**Context:** Automate learnings consolidation during handoff, replacing manual `/remember` invocation.

**Source:** Design document at `plans/learnings-consolidation/design.md`

**Status:** Ready for execution
**Created:** 2026-02-06
**Model:** Sonnet (all phases)

---

## Weak Orchestrator Metadata

**Total Steps:** 7 (1.1, 2.1, 2.2, 3.1, 3.2, 4.1, 4.2)

**Execution Model:**
- All steps: Sonnet (script requires git log analysis, skill modification delicate, agents need protocol embedding, tests need design)
- No haiku delegation appropriate (all steps require semantic judgment)

**Step Dependencies:**
- Sequential chain: Step 2.1 → Step 1.1 (handoff calls script)
- Sequential chain: Step 3.1 → Step 2.2 (agent embeds updated protocol)
- Sequential chain: Step 2.1 → Steps 3.1, 3.2 (handoff delegates to agents)
- Parallel opportunity: Steps 3.1 and 3.2 can be developed concurrently (independent agents)
- Sequential chain: Step 4 → Steps 1-3 (tests require all components)

**Critical path:** Step 1.1 → Step 2.2 → Step 3.1 → Step 4.2

**Error Escalation:**
- Script failures (git unavailable, malformed learnings) → escalate to user
- Skill modification breaks existing behavior → escalate to user
- Agent protocol embedding incomplete → escalate to user
- Test failures → escalate to user

**Report Locations:**
- Phase 1: `plans/learnings-consolidation/reports/phase-1-execution.md`
- Phase 2: `plans/learnings-consolidation/reports/phase-2-execution.md`
- Phase 3: `plans/learnings-consolidation/reports/phase-3-execution.md`
- Phase 4: `plans/learnings-consolidation/reports/phase-4-execution.md`

**Success Criteria:**
- Handoff triggers consolidation when conditions met (size OR staleness)
- Consolidation processes learnings correctly (pre-checks, protocol execution, reporting)
- Reports written to `tmp/consolidation-report.md`
- Handoff continues even if consolidation fails (NFR-1)
- Memory refactor handles file-limit escalations
- All tests pass

**Prerequisites:**
- ✓ Git repository (verified: project is git-tracked)
- ✓ Python 3 environment (verified: pytest available)
- ✓ Design document complete (verified: `plans/learnings-consolidation/design.md` exists)
- ✓ Handoff skill exists (verified: `agent-core/skills/handoff/SKILL.md`)
- ✓ Remember skill exists (verified: `agent-core/skills/remember/SKILL.md`)
- ✓ Baseline agents exist (verified: `agent-core/agents/quiet-task.md`, `agent-core/agents/vet-agent.md`)
- ✓ Validators exist (verified: `agent-core/bin/validate-learnings.py`, `agent-core/bin/validate-memory-index.py`)

---

## Common Context

**Requirements (from design):**
- FR-1: Trigger consolidation conditionally during handoff — Step 2.1 (handoff skill modification)
- FR-2: Calculate learning age in git-active days — Step 1.1 (learning-ages.py script)
- FR-3: Two-test model (trigger + freshness) — Step 2.1 (trigger thresholds: 150 lines, 14 days)
- FR-4: Supersession detection — Step 3.1 (remember-task pre-check)
- FR-5: Contradiction detection — Step 3.1 (remember-task pre-check)
- FR-6: Redundancy detection — Step 3.1 (remember-task pre-check)
- FR-7: Memory refactoring at limit — Step 3.2 (memory-refactor agent), Step 2.1 (refactor flow)
- FR-8: Sub-agent with embedded protocol — Step 3.1 (remember-task agent)
- FR-9: Quality criteria in remember skill — Step 2.2 (remember skill update)
- NFR-1: Failure handling (skip consolidation, handoff continues) — Step 2.1 (try/catch wrapper)
- NFR-2: Consolidation model = Sonnet — Steps 3.1, 3.2 (agent frontmatter)
- NFR-3: Report to tmp/consolidation-report.md — Step 3.1 (remember-task output)

**Scope boundaries:**
- In scope: Script, skill updates, agents, tests
- Out of scope: Embedding-based redundancy detection, full handoff validation (deferred to handoff-validation plan)

**Key Constraints:**
- Script output format: Markdown (per design D-2, not JSON)
- Trigger thresholds: 150 lines (size), 14 days (staleness), 7 days (freshness), 3 minimum batch
- Agent protocol: Embedded directly (not via Skill tool due to sub-agent uncertainty)
- Error handling: Consolidation failures must not block handoff (NFR-1)

**Project Paths:**
- Script: `agent-core/bin/learning-ages.py`
- Handoff skill: `agent-core/skills/handoff/SKILL.md`
- Remember skill: `agent-core/skills/remember/SKILL.md`
- Remember-task agent: `agent-core/agents/remember-task.md`
- Memory-refactor agent: `agent-core/agents/memory-refactor.md`
- Tests: `tests/test_learning_ages.py`
- Learnings file: `agents/learnings.md`
- Report location: `tmp/consolidation-report.md`

**Conventions:**
- Git active days: Count unique commit dates, not calendar days
- Preamble skip: First 10 lines of learnings.md (matching validate-learnings.py pattern)
- Conservative bias: Escalate when uncertain (pre-checks), prefer over-documentation to under-documentation
- Quiet execution: Agents report to files, return filepaths (not content)

---

# Phase 1: Script Foundation (learning-ages.py)

**Complexity:** Moderate (git operations, active-day calculation, staleness heuristic)
**Model:** Sonnet
**Scope:** ~150 lines

---

## Step 1.1: Implement learning-ages.py Script

**Objective:** Create git-aware script to calculate learning entry ages in active days and detect consolidation staleness.

**Implementation:**

Create `agent-core/bin/learning-ages.py` with the following implementation:

**1. Script structure:**
```python
#!/usr/bin/env python3
"""Calculate git-active-day age per learning entry.

Usage:
    learning-ages.py [learnings-file]

Default: agents/learnings.md

Output: Markdown report to stdout
Exit: 0 on success, 1 on error (stderr)
"""
```

**2. Parsing logic:**
- Read learnings.md file (default: `agents/learnings.md`, accept argument)
- Skip first 10 lines (preamble) matching `validate-learnings.py` pattern
- Extract H2 headers (`## Title`) as learning entries
- Store (line_number, title_text) pairs

**3. Git blame for entry dates:**
```python
# For each H2 header line:
# git blame -C -C --first-parent -- agents/learnings.md
# Extract commit hash and date for that specific line
# -C -C flags: detect renames and copies across files
# --first-parent: handle merge commits via first-parent chain (matches staleness algorithm)
```

**4. Active-day calculation:**
```python
# For entry with date D:
# Run: git log --format='%ad' --date=short
# Build set of unique commit dates between D and today
# Active days = len(commit_dates_set)
# Edge case: entry added today → 0 active days
```

**5. Staleness detection algorithm:**
```python
# Walk git log -p -- agents/learnings.md looking for removed H2 headers
# Pattern: lines starting with "-## " (removed headers)
# Most recent commit with removed headers = last consolidation
# Calculate active days from that commit to today
# Fallback: if no removed headers found, report "N/A (no prior consolidation detected)"
```

**6. Output markdown format (per design § D-2):**
```markdown
# Learning Ages Report

**File lines:** 101
**Last consolidation:** 12 active days ago
**Total entries:** 15
**Entries ≥7 active days:** 8

## Tool batching unsolved
- Age: 22 active days
- Added: 2026-01-14

## "Scan" triggers unnecessary tools
- Age: 18 active days
- Added: 2026-01-18

...
```

**7. Error handling:**
- Missing file → stderr message, exit 1
- Git not available → stderr message, exit 1
- Malformed headers → skip, log warning to stderr, continue
- Git operations fail → stderr with git error, exit 1

**8. Shebang and permissions:**
```bash
# Add shebang: #!/usr/bin/env python3
chmod +x agent-core/bin/learning-ages.py
```

**Expected Outcome:**

Script executes successfully:
```bash
$ agent-core/bin/learning-ages.py agents/learnings.md
# Learning Ages Report
**File lines:** 103
**Last consolidation:** 12 active days ago
...
```

Output includes:
- Summary metadata (file lines, staleness, total entries, ≥7 days count)
- Per-entry sections with age and added date
- Sorted oldest-first (highest age first) for consolidation priority

**Validation:**

Run on current `agents/learnings.md`:
```bash
agent-core/bin/learning-ages.py agents/learnings.md | head -20
```

Verify:
- [ ] Output format matches design § D-2 exactly
- [ ] Staleness detection works (finds last consolidation or reports "unknown")
- [ ] Active-day count accurate (excludes days without commits)
- [ ] Handles today's entries (0 active days)
- [ ] Error cases produce stderr messages and exit 1

**Unexpected Result Handling:**

If script fails or output incorrect:
- Check git blame output manually: `git blame -C -C agents/learnings.md | grep "^## "`
- Verify staleness heuristic: `git log -p agents/learnings.md | grep "^-## "`
- Test with simple learnings.md (2-3 entries) first
- Escalate: Complex git edge cases (submodules, rebases) may need user guidance

**Error Conditions:**

| Condition | Action |
|-----------|--------|
| File not found | stderr: "Error: File not found: [path]", exit 1 |
| Not a git repo | stderr: "Error: Not a git repository", exit 1 |
| Git blame fails | stderr: "Error: git blame failed: [error]", exit 1 |
| No H2 headers | Warning to stderr, output summary with 0 entries |

**Success Criteria:**

- [ ] Script runs without errors on `agents/learnings.md`
- [ ] Output matches design specification (§ D-2)
- [ ] Summary section includes all 4 fields (lines, last consolidation, total, ≥7 days)
- [ ] Per-entry sections sorted oldest-first (highest age first)
- [ ] Staleness detection functional (finds last consolidation or reports "N/A")
- [ ] Active-day calculation accurate (manual spot-check 2-3 entries)
- [ ] Edge cases handled: entry added today, file renames, merge commits
- [ ] Error messages clear and actionable
- [ ] Test suite passes: `pytest tests/test_learning_ages.py`

**Report Path:** `plans/learnings-consolidation/reports/phase-1-execution.md` (detailed implementation log)

**Design References:**
- D-2: Markdown output format
- Implementation Component 1: Script specification
- Documentation Perimeter: validate-learnings.py (parsing pattern)
# Phase 2: Skill Updates (handoff + remember)

**Complexity:** Low-moderate (careful insertion, preserve existing behavior)
**Model:** Sonnet
**Scope:** ~50 lines total across 2 skills

---

## Step 2.1: Add Step 4c to Handoff Skill

**Objective:** Insert consolidation trigger logic into handoff workflow while preserving existing protocol.

**Implementation:**

Modify `agent-core/skills/handoff/SKILL.md`:

**1. Locate insertion point:**
- Find Step 4b: "Check invalidated learnings" (lines ~115-140)
- Find Step 5: "Session Size Check" (lines ~160-165)
- Insert new Step 4c between these two

**2. Step 4c content:**

```markdown
### 4c. Consolidation Trigger Check

Run `agent-core/bin/learning-ages.py agents/learnings.md` to get age data.

**Trigger conditions (any one sufficient):**
- File exceeds 150 lines (size trigger)
- 14+ active days since last consolidation (staleness trigger)

**If triggered:**
1. Filter entries with age ≥ 7 active days
2. Check batch size ≥ 3 entries
3. If sufficient: delegate to remember-task agent with filtered entry list
4. Read report from returned filepath
5. If report contains escalations:
   - **Contradictions**: Note in handoff output under Blockers/Gotchas
   - **File limits**: Execute refactor flow (see below)

**Refactor flow (when file at 400-line limit):**

Handoff executes these steps after reading remember-task report with file-limit escalation:

1. Delegate to memory-refactor agent for the specific target file
2. Memory-refactor agent splits file, runs `validate-memory-index.py` autofix
3. Re-invoke remember-task with only the entries that were skipped due to file limit
4. Read second report
5. Check for remaining escalations (contradictions or additional file limits)

Note: This is handoff's perspective. Design D-6 describes the full 7-step flow including remember-task's internal steps (detect → skip → report).

**If not triggered or batch insufficient:**
- Skip consolidation (no action needed)
- Continue to step 5

**On error:**
- Catch exception during script execution or agent delegation
- Log error to stderr: `echo "Consolidation skipped: [error-message]" >&2`
- Note in handoff output: "Consolidation skipped: [brief-reason]"
- Continue to step 5 (consolidation failure must not block handoff per NFR-1)
```

**3. Update frontmatter allowed-tools:**

Change line 4 from:
```yaml
allowed-tools: Read, Write, Edit, Bash(wc:*), Skill
```

To:
```yaml
allowed-tools: Read, Write, Edit, Bash(wc:*, agent-core/bin/learning-ages.py:*), Task, Skill
```

**4. Step numbering preservation:**

Verify:
- [ ] Step 4c inserted between 4b and 5
- [ ] Step 5 ("Session Size Check") unchanged
- [ ] All subsequent steps (6, 7, 8) unchanged
- [ ] No renumbering required

**Expected Outcome:**

Handoff skill updated with consolidation trigger:
- Step 4c present and correctly positioned
- Tool permissions include learning-ages.py and Task
- Trigger thresholds match design (150 lines, 14 days staleness, 7 days freshness, 3 minimum batch)
- Error handling wraps entire step 4c
- Refactor flow documented (detect → spawn → retry)

**Validation:**

```bash
# Verify insertion point
grep -n "### 4c" agent-core/skills/handoff/SKILL.md

# Verify step 5 unchanged
grep -A5 "### 5\." agent-core/skills/handoff/SKILL.md

# Verify tool permissions
grep "allowed-tools:" agent-core/skills/handoff/SKILL.md | head -1
```

Expected:
- Step 4c line number between 4b and 5
- Step 5 content matches original (session size check with wc command)
- Tool permissions include `learning-ages.py` and `Task`

**Unexpected Result Handling:**

If insertion breaks skill:
- **Step numbering collision**: Verify no duplicate "### 4c" headers exist
- **Tool permission error**: Ensure Bash pattern uses wildcard for arguments: `Bash(wc:*, agent-core/bin/learning-ages.py:*)`
- **Skill fails to load**: Check YAML frontmatter syntax (allowed-tools is comma-separated string)

**Error Conditions:**

| Condition | Action |
|-----------|--------|
| Step 4b not found | Verify current handoff skill version matches documentation |
| Step 5 already numbered 4c | Existing modification conflict, escalate to user |
| Tool syntax error | Check comma separation, no quotes around tool list |

**Success Criteria:**

- [ ] Step 4c inserted between 4b and 5 (no renumbering)
- [ ] Tool permissions include `agent-core/bin/learning-ages.py` and `Task`
- [ ] Trigger thresholds explicit (150 lines, 14 days, 7 days, 3 minimum)
- [ ] Refactor flow documented with 5 sub-steps
- [ ] Error handling try/catch pattern documented
- [ ] Step 5 "Session Size Check" unchanged
- [ ] No unintended changes to other steps

---

## Step 2.2: Update Remember Skill Quality Criteria

**Objective:** Add learnings quality and staging retention guidance to remember skill.

**Implementation:**

Modify `agent-core/skills/remember/SKILL.md`:

**1. Locate insertion point:**
- Find section "### 4. Apply + Verify" (around line 56)
- Insert new sections after this section, before "### 5. Document"

**2. New section: Learnings Quality Criteria**

Insert after "### 4. Apply + Verify":

```markdown
### Learnings Quality Criteria

**Principle-level (consolidate):** ✅
- States a general constraint or pattern
- Applies beyond the specific incident
- Example: "Always load skill context before editing"

**Incident-specific (reject/revise):** ❌
- Describes what happened, not what to do
- Narrow to one case, not generalizable
- Example: "Edited skill without loading it" → revise to principle

**Meta-learnings (use sparingly):**
- Rules about rules — only when behavioral constraint required
- Example: "Soft limits normalize deviance" → consolidate if recurrent
```

**3. New section: Staging Retention Guidance**

Insert after "Learnings Quality Criteria":

```markdown
### Staging Retention Guidance

**Keep in staging (do not consolidate):**
- Entries < 7 active days old (insufficient validation)
- Entries with pending cross-references (depend on other work)
- Entries under active investigation

**Consolidate:**
- Entries ≥ 7 active days with proven validity
- Entries that have been applied consistently
- Entries referenced by multiple sessions

**Drop (remove from staging):**
- Superseded by newer entry on same topic
- Contradicted by subsequent work
- Incident-specific without generalizable principle
```

**4. Cross-reference examples:**

Consider adding examples from current `agents/learnings.md`:
- Principle-level: "Prose gates skipped" (line ~85) — general pattern
- Incident-specific: (none currently) — show what NOT to consolidate
- Meta-learning: "Hard limits vs soft limits" (line ~31) — rules about rules

**Expected Outcome:**

Remember skill updated with quality guidance:
- Two new sections after "### 4. Apply + Verify"
- Learnings Quality Criteria with 3 categories (✅ and ❌ markers)
- Staging Retention Guidance with 3 categories (keep/consolidate/drop)
- Examples illustrate good vs bad learnings
- No changes to protocol steps 1-4a

**Validation:**

```bash
# Verify sections added
grep -n "### Learnings Quality Criteria" agent-core/skills/remember/SKILL.md
grep -n "### Staging Retention Guidance" agent-core/skills/remember/SKILL.md

# Verify position (after step 4, before step 5)
grep -B2 "### Learnings Quality Criteria" agent-core/skills/remember/SKILL.md | grep "### 4"
grep -A5 "### Staging Retention Guidance" agent-core/skills/remember/SKILL.md | grep "### 5"
```

Expected:
- Both new sections present
- Positioned between step 4 and step 5
- No unintended changes to protocol steps

**Unexpected Result Handling:**

If sections don't fit structurally:
- **Step 4 has substeps**: Insert after all substeps (after 4a)
- **Section numbering issues**: These are non-numbered sections (no "### 4.x" — just "###")
- **Markdown formatting**: Verify ✅ and ❌ emoji render correctly

**Error Conditions:**

| Condition | Action |
|-----------|--------|
| Section 4 not found | Verify remember skill structure matches documentation |
| Emoji not supported | Use text: "(consolidate)" and "(reject)" |
| Duplicate sections | Check for existing quality criteria, merge if present |

**Success Criteria:**

- [ ] "Learnings Quality Criteria" section added after step 4
- [ ] "Staging Retention Guidance" section added after quality criteria
- [ ] Both sections positioned before step 5 "Document"
- [ ] Examples provided for each category (principle, incident, meta)
- [ ] Keep/consolidate/drop criteria clearly differentiated
- [ ] No changes to existing protocol steps 1-5
- [ ] Markdown formatting correct (✅ and ❌ render)

**Report Path:** `plans/learnings-consolidation/reports/phase-2-execution.md`

**Design References:**
- D-1: Step 4c insertion point
- D-3: Trigger evaluation thresholds
- D-6: Reactive refactoring flow
- D-7: Graceful failure (try/catch)
- Implementation Component 4: Handoff skill modification
- Implementation Component 5: Remember skill update
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
- Reference: `agent-core/skills/remember/references/consolidation-patterns.md` for domain → file routing

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
# Phase 4: Testing

**Complexity:** Moderate (mock git operations, test workflow integration)
**Model:** Sonnet
**Scope:** ~200 lines test code

---

## Step 4.1: Unit Tests for learning-ages.py

**Objective:** Comprehensive test coverage for git-active-day calculation with mocked git operations.

**Implementation:**

Create `tests/test_learning_ages.py`:

**1. Test structure setup:**

```python
import pytest
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Add agent-core/bin to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "agent-core" / "bin"))

import learning_ages  # Import after path modification
```

**2. Test categories (per design Implementation Component 6):**

**A. Parsing tests:**
```python
def test_extract_h2_headers():
    """Extract H2 headers from learnings.md, skip first 10 lines (preamble)."""
    lines = [
        "# Learnings\n",
        "\n",
        "Preamble text...\n",
        *["...\n"] * 7,  # Lines 4-10
        "## First learning\n",  # Line 11 — first extracted
        "- Content\n",
        "## Second learning\n",
        "- More content\n",
    ]

    headers = learning_ages.extract_titles(lines)

    assert len(headers) == 2
    assert headers[0] == (11, "First learning")
    assert headers[1] == (13, "Second learning")
    # Verify preamble skipped: no headers from lines 1-10
    assert all(line_num > 10 for line_num, _ in headers)

def test_malformed_headers_skipped():
    """Skip malformed headers gracefully, continue processing."""
    lines = [
        *["preamble\n"] * 10,
        "## Valid header\n",
        "###Not a header (no space)\n",
        "## Another valid\n",
    ]

    headers = learning_ages.extract_titles(lines)

    assert len(headers) == 2
    assert "Valid header" in str(headers)
    assert "Another valid" in str(headers)
```

**B. Age calculation tests:**
```python
@patch('subprocess.run')
def test_active_day_calculation(mock_run):
    """Count unique commit dates between entry date and today."""
    # Mock git blame output
    mock_run.return_value = MagicMock(
        stdout="a1b2c3d (Author 2026-01-15 00:00:00 +0000 11) ## Learning title",
        returncode=0
    )

    entry_date = learning_ages.get_entry_date("agents/learnings.md", 11)

    assert entry_date == "2026-01-15"
    mock_run.assert_called_once_with(
        ["git", "blame", "-C", "-C", "--first-parent", "-L", "11,11", "--", "agents/learnings.md"],
        capture_output=True,
        text=True,
        check=True
    )

@patch('subprocess.run')
def test_active_days_excludes_inactive_days(mock_run):
    """Only count days with commits, not calendar days."""
    # Mock git log output — 5 unique dates over 10 calendar days
    mock_run.return_value = MagicMock(
        stdout="2026-01-15\n2026-01-16\n2026-01-18\n2026-01-22\n2026-01-25\n",
        returncode=0
    )

    active_days = learning_ages.count_active_days("2026-01-15", "2026-01-25")

    assert active_days == 5  # Not 10 (calendar days)

def test_entry_added_today_zero_active_days():
    """Entry added today should have 0 active days."""
    from datetime import date
    today = date.today().isoformat()

    active_days = learning_ages.count_active_days(today, today)

    assert active_days == 0

@patch('subprocess.run')
def test_merge_commits_handled(mock_run):
    """Merge commits processed via --first-parent flag."""
    # Mock git blame on merge commit
    mock_run.return_value = MagicMock(
        stdout="merge123 (Author 2026-01-20 00:00:00 +0000 15) ## Merge learning",
        returncode=0
    )

    entry_date = learning_ages.get_entry_date("agents/learnings.md", 15)

    assert entry_date == "2026-01-20"
    # Verify --first-parent flag present
    assert "--first-parent" in mock_run.call_args[0][0]
```

**C. Staleness detection tests:**
```python
@patch('subprocess.run')
def test_staleness_finds_last_consolidation(mock_run):
    """Find most recent commit with removed H2 headers (consolidation evidence)."""
    # Mock git log -p output with removed headers
    mock_run.return_value = MagicMock(
        stdout="""
commit abc123 2026-01-20
-## Old learning 1
-## Old learning 2

commit def456 2026-01-10
-## Even older learning
""",
        returncode=0
    )

    last_consolidation = learning_ages.find_last_consolidation("agents/learnings.md")

    assert last_consolidation == "2026-01-20"  # Most recent
    mock_run.assert_called_with(
        ["git", "log", "-p", "--", "agents/learnings.md"],
        capture_output=True,
        text=True,
        check=True
    )

@patch('subprocess.run')
def test_staleness_fallback_no_prior_consolidation(mock_run):
    """Report 'N/A (no prior consolidation detected)' when no removed headers found."""
    # Mock git log -p output with no removed H2 headers
    mock_run.return_value = MagicMock(
        stdout="commit abc123\n+## New learning\n",  # Only additions
        returncode=0
    )

    last_consolidation = learning_ages.find_last_consolidation("agents/learnings.md")

    assert last_consolidation is None  # Script formats this as "N/A (...)"

def test_multiple_consolidations_uses_most_recent():
    """When multiple consolidations found, use most recent."""
    # Test via integration with mocked git log (already covered in test above)
    pass  # Covered by test_staleness_finds_last_consolidation
```

**D. Trigger logic tests:**
```python
def test_size_trigger_thresholds():
    """Size trigger: <150 no trigger, ≥150 trigger."""
    assert learning_ages.check_size_trigger(149) is False
    assert learning_ages.check_size_trigger(150) is True
    assert learning_ages.check_size_trigger(151) is True

def test_staleness_trigger_thresholds():
    """Staleness trigger: <14 days no trigger, ≥14 days trigger."""
    assert learning_ages.check_staleness_trigger(13) is False
    assert learning_ages.check_staleness_trigger(14) is True
    assert learning_ages.check_staleness_trigger(15) is True

def test_batch_minimum_threshold():
    """Batch minimum: <3 entries insufficient, ≥3 sufficient."""
    entries = [("## Entry 1", 10), ("## Entry 2", 9)]
    assert learning_ages.check_batch_minimum(entries, threshold=3) is False

    entries.append(("## Entry 3", 8))
    assert learning_ages.check_batch_minimum(entries, threshold=3) is True
```

**E. Freshness filter tests:**
```python
def test_freshness_filter_includes_gte_7_days():
    """Include entries ≥7 active days, exclude <7 days."""
    entries = [
        ("## Old entry", 10),
        ("## Fresh entry", 6),
        ("## Boundary entry", 7),
        ("## Very old", 22),
    ]

    filtered = learning_ages.filter_by_freshness(entries, threshold=7)

    assert len(filtered) == 3
    assert ("## Fresh entry", 6) not in filtered
    assert ("## Boundary entry", 7) in filtered  # Boundary included

def test_boundary_exactly_7_days():
    """Exactly 7 active days should be included."""
    entries = [("## Boundary", 7)]

    filtered = learning_ages.filter_by_freshness(entries, threshold=7)

    assert len(filtered) == 1
```

**F. Error handling tests:**
```python
def test_missing_file_exits_with_error():
    """Missing learnings.md should exit 1 with stderr message."""
    with pytest.raises(FileNotFoundError):
        learning_ages.read_learnings_file("nonexistent.md")

@patch('subprocess.run')
def test_git_not_available(mock_run):
    """Git command failure should exit 1 with stderr message."""
    mock_run.side_effect = FileNotFoundError("git not found")

    with pytest.raises(FileNotFoundError):
        learning_ages.get_entry_date("agents/learnings.md", 11)

@patch('subprocess.run')
def test_malformed_learnings_continues(mock_run):
    """Malformed entries should be skipped with warning, not fatal."""
    # Already covered in parsing tests
    pass
```

**G. Integration test:**
```python
@patch('subprocess.run')
def test_full_pipeline(mock_run, tmp_path):
    """Full pipeline with mocked git repo produces correct markdown output."""
    # Create temp learnings.md
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""
# Learnings

Preamble...
...(lines 3-10)

## Tool batching unsolved
- Content

## Hard limits vs soft limits
- More content
""")

    # Mock git blame responses
    def mock_git_side_effect(*args, **kwargs):
        cmd = args[0]
        if "blame" in cmd:
            if "11" in cmd:
                return MagicMock(stdout="abc123 (Author 2026-01-14 ...) ## Tool batching", returncode=0)
            elif "13" in cmd:
                return MagicMock(stdout="def456 (Author 2026-01-28 ...) ## Hard limits", returncode=0)
        elif "log" in cmd and "-p" in cmd:
            return MagicMock(stdout="commit xyz789 2026-01-20\n-## Old learning\n", returncode=0)
        elif "log" in cmd:
            return MagicMock(stdout="2026-01-15\n2026-01-20\n2026-01-28\n2026-02-01\n", returncode=0)
        return MagicMock(stdout="", returncode=0)

    mock_run.side_effect = mock_git_side_effect

    output = learning_ages.generate_report(str(learnings_file))

    # Verify output format
    assert "# Learning Ages Report" in output
    assert "**File lines:**" in output
    assert "**Last consolidation:**" in output
    # Verify staleness calculation present (mocked consolidation 2026-01-20)
    # Active days between 2026-01-20 and mocked "today" should appear
    assert "active days ago" in output or "N/A" in output
    assert "## Tool batching unsolved" in output
    assert "- Age:" in output
    assert "- Added: 2026-01-14" in output
```

**Expected Outcome:**

Test file created at `tests/test_learning_ages.py` with:
- 7 test categories (A-G) covering all design test cases
- Git operation mocking via `subprocess.run` patches
- Edge case coverage (merge commits, file renames, today's entries, staleness fallback)
- Integration test with full pipeline

**Validation:**

Run test suite:
```bash
pytest tests/test_learning_ages.py -v
```

Expected:
- All tests pass
- Coverage for git operations (blame, log, log -p)
- Edge cases handled (0 active days, missing file, git unavailable)

**Success Criteria:**

- [ ] Test file created at `tests/test_learning_ages.py`
- [ ] 7 test categories present (parsing, age calculation, staleness, trigger logic, freshness, error handling, integration)
- [ ] Git operations mocked via subprocess patches
- [ ] Edge cases tested (merge commits, entry added today, no prior consolidation)
- [ ] Staleness detection test includes fallback ("N/A")
- [ ] All tests pass: `pytest tests/test_learning_ages.py`

---

## Step 4.2: Integration Validation

**Objective:** Validate end-to-end workflow integration with manual testing procedures.

**Implementation:**

**1. Unit test integration (automated):**

Already covered by step 4.1 integration test. Run:
```bash
pytest tests/test_learning_ages.py::test_full_pipeline -v
```

Verify:
- Script produces markdown output matching design § D-2
- Summary fields present (file lines, last consolidation, total entries, ≥7 days count)
- Per-entry sections formatted correctly

**2. Manual handoff trigger test:**

Create test scenario to verify handoff step 4c triggers consolidation:

**Option A: Size trigger (>150 lines)**

```bash
# Check current learnings.md size
wc -l agents/learnings.md

# If needed, add temp entries to exceed 150 lines
# (Do this in a test branch)

# Run handoff and verify step 4c executes
# Expected: Script runs, filtered entry list passed to remember-task agent
```

**Option B: Staleness trigger (>14 days)**

```bash
# Check staleness
agent-core/bin/learning-ages.py agents/learnings.md | head -5

# If staleness <14 days, use git manipulation to simulate old entries
# (Or wait for natural staleness)

# Run handoff and verify step 4c executes
```

**Verification steps:**
- [ ] Handoff skill loads without error
- [ ] Step 4c runs learning-ages.py
- [ ] Trigger condition evaluated (size OR staleness)
- [ ] If triggered: filtered entry list logged
- [ ] If triggered: remember-task agent delegated
- [ ] If not triggered: consolidation skipped, continues to step 5
- [ ] If error: logged to stderr, handoff continues (NFR-1)

**3. Agent definition validation:**

**A. Remember-task agent:**

```bash
# Read agent file
cat agent-core/agents/remember-task.md

# Verify frontmatter
head -10 agent-core/agents/remember-task.md | grep -E "(name|description|model|color|tools)"

# Verify source comment
grep "Source: agent-core/skills/remember" agent-core/agents/remember-task.md

# Verify sections present
grep "^##" agent-core/agents/remember-task.md | head -10
```

Expected sections:
- Role statement
- Input Format
- Pre-Consolidation Checks
- Consolidation Protocol
- Reporting
- Return Protocol

Checklist:
- [ ] Protocol embedded faithfully (compare with remember skill steps 1-4a):
  - Verify protocol steps present in same order (Understand → File Selection → Draft → Apply → Discovery)
  - Check terminology matches skill (e.g., "Precision over brevity", "Atomic changes")
  - Confirm routing patterns identical (fragments/ vs decisions/ vs implementation-notes.md)
  - Allow adaptation: agent body uses second-person ("You"), skill uses imperative
- [ ] Source comment present for synchronization tracking
- [ ] Pre-check algorithms concrete (thresholds specified: 50% keyword overlap, 70% redundancy)
- [ ] Report structure documented (6 sections: summary, supersession, redundancy, contradictions, file limits, discovery)
- [ ] Model: sonnet, color: green, tools include Read/Write/Edit/Bash/Grep/Glob
- [ ] Quiet execution pattern (report to file, return filepath)

**B. Memory-refactor agent:**

```bash
# Read agent file
cat agent-core/agents/memory-refactor.md

# Verify sections
grep "^##" agent-core/agents/memory-refactor.md
```

Expected sections:
- Role statement
- Input Format
- Refactoring Process (6 steps)
- Constraints
- Output Format
- Return Protocol

Checklist:
- [ ] Refactoring process has 6 steps with heuristics
- [ ] Validator autofix integration (step 5)
- [ ] Content preservation constraints (no summarization)
- [ ] Model: sonnet, color: yellow, tools include Read/Write/Edit/Grep/Glob
- [ ] Quiet execution pattern (filepaths on success, error on failure)

**4. No automated full workflow test:**

Design specifies no automated end-to-end test for full workflow (complexity too high). Manual validation sufficient:
- Phase 1-3 unit tests pass
- Agent definitions reviewed manually
- Handoff trigger test executed manually

**Expected Outcome:**

Integration validation complete:
- Unit tests pass
- Manual handoff trigger test executed
- Agent definitions validated against specifications
- No full workflow automation (manual validation acceptable per design)

**Validation:**

```bash
# Run all tests
pytest tests/test_learning_ages.py -v

# Verify no test failures
echo $?  # Should be 0
```

**Unexpected Result Handling:**

If tests fail:
- **Parse errors**: Verify preamble skip count (10 lines)
- **Git mock failures**: Check subprocess.run patch syntax
- **Integration test fails**: Verify markdown output format matches design § D-2

If manual trigger test doesn't trigger:
- **Size check**: Verify learnings.md actually >150 lines
- **Staleness check**: Verify staleness >14 days via script output
- **Threshold mismatch**: Compare handoff step 4c thresholds with design D-3

If agent definitions incomplete:
- **Compare against design**: Cross-reference Implementation Components 2 and 3
- **Check protocol embedding**: Compare remember-task protocol with remember skill steps 1-4a
- **Verify structure**: Ensure all required sections present per phase 3 success criteria

**Success Criteria:**

- [ ] All unit tests pass: `pytest tests/test_learning_ages.py`
- [ ] Integration test produces correct markdown format (matches design § D-2)
- [ ] Manual handoff trigger test executed (size OR staleness)
- [ ] Remember-task agent validated (protocol, source comment, pre-checks, reporting)
- [ ] Memory-refactor agent validated (6-step process, autofix integration, constraints)
- [ ] Both agents follow quiet execution pattern
- [ ] No critical issues found in agent definitions

**Report Path:** `plans/learnings-consolidation/reports/phase-4-execution.md`

**Design References:**
- Implementation Component 6: Testing specification
- D-2: Markdown output format (validation target)
- D-3: Trigger thresholds (manual test verification)
- NFR-1: Failure handling (handoff continues on error)
