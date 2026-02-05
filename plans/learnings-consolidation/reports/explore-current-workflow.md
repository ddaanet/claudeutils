# Exploration Report: Current Handoff and Remember Workflows

**Date:** 2026-02-05
**Scope:** Handoff skill, Remember skill, learnings.md structure, validators, and agent patterns

---

## Executive Summary

The claudeutils project has a mature two-skill workflow for session handoffs and persistent documentation:

1. **Handoff skill** — Updates `agents/session.md` with completed tasks, pending work, blockers, and learnings
2. **Remember skill** — Processes learnings and consolidates them into permanent documentation (fragments, decisions, rules)
3. **learnings.md** — Staging area for cross-session institutional knowledge (80-line soft limit triggers consolidation)
4. **Memory index validator** — Ensures all semantic headers have index entries and vice versa

The workflow is designed for incremental consolidation: handoff appends learnings to `agents/learnings.md`, remember processes them into permanent locations, and validators enforce consistency.

---

## Key Findings

### 1. Handoff Skill Definition

**File:** `/Users/david/code/claudeutils/agent-core/skills/handoff/SKILL.md` (275 lines)

**Step structure (numbered 1-8 in skill protocol):**

1. **Gather Context** — Review conversation for completed/pending tasks, blockers
2. **Update session.md** — Write handoff note with formatted task entries
3. **Context Preservation** — Maintain 75-150 line target with specific details (commit hashes, file paths, root causes)
4. **Write Learnings to Separate File** — Append to `agents/learnings.md` (not session.md)
   - **Format:** Learning headers (`## Title`) with bullet structure
   - **No blank line after header** (per line 137)
   - Example structure:
     ```markdown
     ## Learning title
     - Anti-pattern: [what NOT to do]
     - Correct pattern: [what TO do]
     - Rationale: [why]
     ```
5. **Session Size Check** — Run `wc -l agents/session.md agents/learnings.md` (lines 160-165)
6. **Update jobs.md** — Update plan status transitions (lines 167-179)
7. **Trim Completed Tasks** — Delete only if completed before session started AND work committed (lines 181-206)
8. **Display STATUS** — Unless `--commit` flag used (lines 207-219)

**Chaining:** Step 8 mentions tail-call to `/commit` if `--commit` flag present (lines 253-263)

**Critical learnings insertion point:** Step 4 explicitly states append to `agents/learnings.md`; Step 4b checks for invalidated learnings

**Size check location:** Step 5, uses `wc -l` command (not step 4 as outline suggested)

---

### 2. Remember Skill Definition

**File:** `/Users/david/code/claudeutils/agent-core/skills/remember/SKILL.md` (105 lines)

**Consolidation logic (protocol steps 1-5):**

1. **Understand Learning** — Read `agents/learnings.md`, determine category (behavioral rule vs technical detail vs implementation pattern)
2. **File Selection** — Route to appropriate target:
   - `agent-core/fragments/*.md` — Behavioral rules, workflow patterns, anti-patterns
   - `agents/decisions/*.md` — Architecture, implementation patterns, technology choices
   - `agents/decisions/implementation-notes.md` — Mock patterns, Python quirks, API details
   - `agents/session.md` — Active tasks, blockers, temporary state
   - `.claude/skills/*/references/learnings.md` — Domain-specific patterns
   - **See `references/consolidation-patterns.md` for detailed routing**

3. **Draft Update** — Follow principles:
   - Precision > brevity
   - Examples > abstractions
   - Constraints > guidelines
   - Atomic changes
   - Measured data

4. **Apply + Verify** — Edit/Write target files; verify formatting; **remove consolidated learnings from `agents/learnings.md` but keep 3-5 most recent**

   **Step 4a Update discovery mechanisms:**
   - Append to `agents/memory-index.md` (one-line entry)
   - If new fragment: add `@`-reference to CLAUDE.md or create `.claude/rules/` entry (path-scoped)
   - If existing fragment updated: verify memory index entry
   - If decision file updated: verify `.claude/rules/` entry exists

5. **Document** — Commit with message format: `Update [file]: [what]\n\n- [change 1]\n- [change 2]\n- [rationale]`

**Target files written to:**
- CLAUDE.md (fragments via @ references)
- agents/decisions/ (domain docs)
- agent-core/fragments/ (behavioral rules)
- agents/memory-index.md (discovery mechanism)
- agents/learnings.md (removal of consolidated learnings)

---

### 3. learnings.md Structure

**File:** `/Users/david/code/claudeutils/agents/learnings.md` (103 lines as of exploration date)

**Current format:**
- H1 title: `# Learnings`
- Preamble with soft limit guidance (lines 1-6)
- H2 section headers per learning: `## Learning Title`
- Bullet structure under each header:
  - Anti-pattern line
  - Correct pattern line
  - Rationale line
  - Optional additional context

**Current state:**
- 29 entries (learning sections)
- 103 lines total (23 lines over soft 80-line limit)
- Soft limit triggers `/remember` consolidation when approaching 80 lines
- Never trimmed or removed (append-only discipline)

**Consolidation instruction:** "Keep the 3-5 most recent learnings for continuity" (line 5 of learnings.md)

**Most recent entries in file:**
- "Prose skill gates skipped" (lines 96-102)
- "Phase boundaries require checkpoint delegation" (lines 88-95)
- "Vet-fix-agent confabulation from design docs" (lines 82-87)
- "Delegation without plan causes drift" (lines 75-81)
- "Output requires vet+fix with alignment" (lines 67-74)

---

### 4. Memory Index Validator

**File:** `/Users/david/code/claudeutils/agent-core/bin/validate-memory-index.py` (481 lines)

**What it validates:**
- All semantic headers (H2+ not starting with `.`) in `agents/decisions/*.md` have index entries
- All index entries have matching semantic headers
- No duplicate index entries
- Entries have em-dash separator (`—`) and word count 8-15
- Entries in correct file sections
- Entries in file order (by source line number)
- Entries don't point to structural sections (marked with `.` prefix)
- Duplicate headers not in different files

**Autofix capability (enabled by default):**
- Section placement: moves entries to correct file section
- Entry ordering: sorts by source line number within sections
- Structural entries: removes entries pointing to structural headers
- Returns True if autofix succeeds

**Indexed files:** Only `agents/decisions/*.md` (line 31-33)

**Exempt sections:**
- "Behavioral Rules (fragments — already loaded)"
- "Technical Decisions (mixed — check entry for specific file)"

**Key pattern:** Structural headers (marked with `## .Title` format) are scanned and entries pointing to them are removed (lines 52-78, 347-354)

**Index entry format:** `Key — description` with em-dash separator (line 173)

**Word count enforcement:** Hard error if entry has <8 or >15 words (lines 276-280)

---

### 5. Learnings Validator

**File:** `/Users/david/code/claudeutils/agent-core/bin/validate-learnings.py` (80 lines)

**What it validates:**
- Title format: `## Title` (markdown header)
- Max word count per title: 5 words (default, configurable)
- No duplicate titles (case-insensitive)
- No empty titles
- Skips first 10 lines (preamble/header, lines 23-25)

**Validation scope:**
- Only checks H2 headers with pattern `^## (.+)$`
- Extracts title text from each header
- Counts words and checks uniqueness

**Error output:** Line number, error type, title text

**Used by:** Precommit validation (runs as `just precommit`)

---

### 6. Learning Staging Infrastructure

**File:** `/Users/david/code/claudeutils/agent-core/bin/add-learning.py` (62 lines)

**Purpose:** Add learnings to pending staging area (NOT currently used in workflow)

**Behavior:**
- Creates individual learning files: `agents/learnings/{date}-{slug}.md`
- Appends reference to `agents/learnings/pending.md`
- Returns filename for caller

**Current status:** Script exists but **NOT integrated** into handoff workflow. Handoff directly appends to `agents/learnings.md` instead.

**Implication:** There is a disconnect between add-learning.py's intended two-tier system (pending stage + consolidation) and the actual handoff behavior (direct append).

---

### 7. Agent Definition Patterns

**Plan-specific agents created by prepare-runbook.py:**

Location: `.claude/agents/`

**Example agent files examined:**
- `/Users/david/code/claudeutils/.claude/agents/statusline-parity-task.md` (317 lines)

**Pattern observed:**
- YAML frontmatter: name, description, model, color, tools list
- Baseline system prompt: Role statement, context handling, protocol sections
- Combined with runbook-specific context by `prepare-runbook.py`
- No skill references in agent prologues (agents invoke skills via Skill tool when needed)

**Agent list (9 total):**
1. consolidation-task.md
2. test-refactor-task.md
3. claude-tools-recovery-task.md
4. claude-tools-rewrite-task.md
5. design-workflow-enhancement-task.md
6. workflow-controls-task.md
7. statusline-wiring-task.md
8. workflow-feedback-loops-task.md
9. statusline-parity-task.md

**Naming pattern:** `{plan-name}-task.md`

---

### 8. Existing bin Scripts Summary

**Location:** `/Users/david/code/claudeutils/agent-core/bin/`

**Current scripts (10 total):**

| Script | Purpose | Lines |
|--------|---------|-------|
| `add-learning.py` | Stage learnings (not integrated) | 62 |
| `validate-learnings.py` | Validate titles, word count | 80 |
| `validate-memory-index.py` | Validate index entries → headers | 481 |
| `validate-decision-files.py` | Validate decision file structure | TBD |
| `validate-tasks.py` | Validate session.md task format | TBD |
| `validate-jobs.py` | Validate jobs.md plan tracking | TBD |
| `prepare-runbook.py` | Assemble runbook from phases, create agent | 1,000+ |
| `assemble-runbook.py` | Legacy assembly (superseded?) | 200+ |
| `batch-edit.py` | Batch editing with marker syntax | 300+ |
| `task-context.sh` | Recover session.md from git history | Small |

---

## Workflow Integration Map

```
Session Execution
    ↓
[User/Agent completes work]
    ↓
/handoff skill
    ├─ Gather context from conversation
    ├─ Update agents/session.md with tasks
    ├─ Append learnings to agents/learnings.md ← KEY INSERTION
    ├─ Check file sizes (wc -l)
    ├─ Update agents/jobs.md
    ├─ Trim completed tasks
    └─ Display status (or tail-call /commit)
    ↓
agents/learnings.md accumulates across sessions
    (soft limit 80 lines triggers /remember)
    ↓
/remember skill
    ├─ Read learnings.md
    ├─ Route each learning to permanent location:
    │  ├─ agent-core/fragments/ (behavioral)
    │  ├─ agents/decisions/ (technical)
    │  ├─ agents/decisions/implementation-notes.md (patterns)
    │  └─ .claude/rules/ (path-scoped)
    ├─ Update agents/memory-index.md entries
    ├─ Remove consolidated learnings from learnings.md
    │  (keep 3-5 most recent)
    └─ Commit changes
    ↓
validators/precommit
    ├─ validate-learnings.py (titles, word count)
    ├─ validate-memory-index.py (entries ↔ headers)
    ├─ validate-decision-files.py
    ├─ validate-tasks.py
    └─ validate-jobs.py
```

---

## Patterns Identified

### 1. Two-Tier Learning System
- **Volatile (session.md):** Task execution state, blockers
- **Staging (learnings.md):** Cross-session institutional knowledge (80-line soft limit)
- **Permanent (fragments/, decisions/, rules/):** Actionable rules, patterns, constraints

### 2. Size-Triggered Consolidation
- `agents/learnings.md` accumulates without trimming
- Handoff checks size with `wc -l` command
- Advice given to user when file approaches 80 lines
- Consolidation is manual (user runs `/remember`)

### 3. Index as Discovery Mechanism
- `agents/memory-index.md` lists all learnings scattered across permanent files
- **Purpose:** Enable keyword-rich discovery without reading all files
- **Validator:** Ensures all semantic headers have entries (and vice versa)
- **Autofix:** Reorders entries by source file and line number

### 4. Validator Enforcement
- Hard errors (not warnings) — violation blocks commit
- Four validators enforce consistency:
  - Learning titles (max 5 words)
  - Index entries (8-15 words, em-dash format, no duplicates)
  - Decision files (TBD)
  - Task format (TBD)
  - Job tracking (TBD)

### 5. Context Preservation Strategy
- Handoff keeps 75-150 lines of detail (not verbose logs)
- Priorities: commit hashes, file paths, root causes, failed approaches
- Omits: obvious outcomes, intermediate steps, repetitive info
- Git history serves as archive

### 6. Memory Index Pattern
- Entry format: `Key — description` (em-dash separator)
- Sections organized by file (e.g., `## agents/decisions/cli.md`)
- Exempt sections: "Behavioral Rules (fragments)" and "Technical Decisions (mixed)"
- Structural markers: Headers with `.` prefix mark organizational sections (not indexed)

---

## Gaps and Unresolved Questions

### 1. Learning Staging Infrastructure Disconnect
**Issue:** `add-learning.py` exists but isn't integrated. Handoff directly appends to `agents/learnings.md`, bypassing the date-stamped staging system.

**Questions:**
- Was add-learning.py designed for a different workflow?
- Should handoff use add-learning.py to create dated files?
- Or should it continue direct append with current design?

### 2. Missing Consolidation Patterns Guide
**Issue:** Remember skill references `references/consolidation-patterns.md` for detailed routing guidance, but file was not explored.

**Note:** File exists at `/Users/david/code/claudeutils/agent-core/skills/remember/references/consolidation-patterns.md` but content not read in this exploration.

### 3. Validator Coverage
**Issue:** Decision file, task format, and job tracking validators exist but not examined.

**Questions:**
- What enforcement do they provide?
- Are they integrated into precommit?
- Do they autofix or error-only?

### 4. Size Check Timing
**Issue:** Handoff step 5 runs `wc -l` but doesn't make consolidation decision. It advises user to run `/remember` if file > 80 lines.

**Questions:**
- Should consolidation be automatic or manual?
- Current design assumes user monitors and runs `/remember` manually
- Should threshold be hard error (blocking commit) or soft advice?

### 5. Memory Index Exempt Sections Hardcoding
**Issue:** Exempt sections list is hardcoded in validator (lines 36-39 of validate-memory-index.py).

**Questions:**
- Should this list be configurable?
- How are new exempt sections added?
- Does documentation explain the exemption criteria?

---

## File Locations (Absolute Paths)

| Component | Path |
|-----------|------|
| Handoff skill | `/Users/david/code/claudeutils/agent-core/skills/handoff/SKILL.md` |
| Remember skill | `/Users/david/code/claudeutils/agent-core/skills/remember/SKILL.md` |
| Learnings file | `/Users/david/code/claudeutils/agents/learnings.md` |
| Memory index | `/Users/david/code/claudeutils/agents/memory-index.md` |
| Session file | `/Users/david/code/claudeutils/agents/session.md` |
| Jobs tracker | `/Users/david/code/claudeutils/agents/jobs.md` |
| Handoff rules | `/Users/david/code/claudeutils/agents/rules-handoff.md` |
| Remember role | `/Users/david/code/claudeutils/agents/role-remember.md` |
| Handoff examples | `/Users/david/code/claudeutils/agent-core/skills/handoff/examples/good-handoff.md` |
| Handoff template | `/Users/david/code/claudeutils/agent-core/skills/handoff/references/template.md` |
| Remember patterns | `/Users/david/code/claudeutils/agent-core/skills/remember/examples/remember-patterns.md` |
| Remember consolidation patterns | `/Users/david/code/claudeutils/agent-core/skills/remember/references/consolidation-patterns.md` |
| Remember rule management | `/Users/david/code/claudeutils/agent-core/skills/remember/references/rule-management.md` |
| Memory index validator | `/Users/david/code/claudeutils/agent-core/bin/validate-memory-index.py` |
| Learnings validator | `/Users/david/code/claudeutils/agent-core/bin/validate-learnings.py` |
| Add learning script | `/Users/david/code/claudeutils/agent-core/bin/add-learning.py` |
| Handoff semantic module | `/Users/david/code/claudeutils/agents/modules/src/handoff.semantic.md` |

---

## Code Snippets

### Handoff Skill: Learning Append (Step 4)

From `/Users/david/code/claudeutils/agent-core/skills/handoff/SKILL.md` (lines 119-145):

```markdown
### 4. Write Learnings to Separate File

If the session has learnings, append them to `agents/learnings.md` (not session.md).

**Learning format:**

```markdown
## [Learning title]
- Anti-pattern: [what NOT to do]
- Correct pattern: [what TO do]
- Rationale: [why]

## [Another learning]
- Anti-pattern: [what NOT to do]
- Correct pattern: [what TO do]
- Rationale: [why]
```

**Note:** No blank line after `## Title` header.

**Design decisions are learnings.** When the session produced significant design decisions
(architectural choices, trade-offs, anti-patterns discovered), write them to `agents/learnings.md`
using the standard learning format. learnings.md is a staging area — `/remember` consolidates
to permanent locations (fragments/, decisions/, skill references/).

**Learnings file is append-only:**
- Append new learnings to `agents/learnings.md` (do NOT overwrite)
- Never trim or remove learnings (separate from session.md lifecycle)
- Learnings accumulate across sessions as institutional knowledge
- When file reaches 80+ lines, note to user: "Learnings file at X/80 lines.
  Consider running /remember to consolidate."
```

### Remember Skill: Step 4a (Discovery Mechanism Update)

From `/Users/david/code/claudeutils/agent-core/skills/remember/SKILL.md` (lines 59-67):

```markdown
**Step 4a: Update discovery mechanisms**

After consolidating a learning:

1. **Append to memory index**: Add one-line entry (summary + file reference) to appropriate
   section in `agents/memory-index.md`
2. **If new fragment created**: Add `@`-reference to CLAUDE.md OR create `.claude/rules/`
   entry if path-scoped. **Heuristic:** If the learning applies regardless of which files
   are being edited → `@`-ref in CLAUDE.md. If it only applies when working with a
   specific file type or directory → `.claude/rules/` entry with path frontmatter.
3. **If existing fragment updated**: Ensure memory index entry reflects the updated
   content (add new entry or update existing one)
4. **If decision file updated**: Verify corresponding `.claude/rules/` entry exists
   for path trigger
```

### Memory Index Validator: Autofix Logic

From `/Users/david/code/claudeutils/agent-core/bin/validate-memory-index.py` (lines 393-431):

```python
def autofix_index(index_path, root, headers, structural=None):
    """Rewrite memory-index.md with entries in correct sections and order.

    Also removes entries pointing to structural sections.
    Returns True if rewrite succeeded.
    """
    if structural is None:
        structural = set()

    preamble, sections = extract_index_structure(index_path, root)

    # Build map: file path → sorted entries
    file_entries = {}
    exempt_entries = {}  # section_name → entries (preserve as-is)

    for section_name, entry_lines in sections:
        if section_name in EXEMPT_SECTIONS:
            exempt_entries[section_name] = entry_lines
            continue

        for entry in entry_lines:
            if " — " in entry:
                key = entry.split(" — ")[0].lower()
            else:
                key = entry.lower()

            # Skip entries pointing to structural sections
            if key in structural:
                continue

            # Find which file this entry belongs to
            if key in headers:
                source_file = headers[key][0][0]
                source_lineno = headers[key][0][1]
                file_entries.setdefault(source_file, []).append(
                    (source_lineno, entry)
                )

    # Sort entries within each file by source line number
    for filepath in file_entries:
        file_entries[filepath].sort(key=lambda x: x[0])
```

---

## Recommendations for Design

### For learnings-consolidation Outline

1. **Document the two-tier learning system explicitly** in the outline:
   - Staging (learnings.md) vs permanent (fragments/, decisions/)
   - Soft limit (80 lines) and consolidation trigger
   - Keep 3-5 most recent after consolidation

2. **Clarify the memory index role** in Phase C design:
   - It's the discovery mechanism for permanent documentation
   - Validator ensures consistency
   - Autofix capability suggests it's maintainable

3. **Address the staging infrastructure question**:
   - Should learnings.md continue as direct append?
   - Or should handoff integrate add-learning.py date-stamped system?
   - Design decision impacts Phase B (handoff enhancement) and Phase C (consolidation)

4. **Size check location ambiguity**:
   - Current design shows step 5 (handoff skill)
   - Consider if step number matters or if it's just sequential in protocol

5. **Exemption list management**:
   - Document how exempt sections are added/removed
   - Consider making hardcoded list configurable

---

## Summary Table

| Aspect | Current Implementation |
|--------|------------------------|
| **Handoff output** | Appends to `agents/learnings.md` (Step 4) |
| **Size check** | `wc -l` command in Step 5 |
| **Consolidation trigger** | Soft 80-line limit (advice to user, no hard block) |
| **Remember scope** | Fragments, decisions, implementation-notes, rules |
| **Index discovery** | `agents/memory-index.md` with keyword-rich entries |
| **Validator enforcement** | Hard errors on word count, format, uniqueness, coverage |
| **Autofix capability** | Memory index validator can reorder and remove entries |
| **Retention policy** | Keep 3-5 most recent learnings after consolidation |
| **Archive strategy** | Git history + file references (not separate archive) |

---

*Report completed: 2026-02-05. Exploration covers handoff skill, remember skill, learnings.md, validators, agent patterns, and bin scripts.*
