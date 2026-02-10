# `/when` Recall System Design Context

Exploration of existing infrastructure and patterns to inform design decisions.

## 1. Existing Validator (`agent-core/bin/validate-memory-index.py`)

**Location:** `/Users/david/code/claudeutils-memory-index-recall/agent-core/bin/validate-memory-index.py`

**Line Count:** 480 lines

### Architecture

**Core Validation Logic:**
- Semantic header detection: `##+ [^.]` (headers NOT starting with dot)
- Structural header detection: `##+ \.` (headers starting with dot, organizational only)
- Index entry parsing: Bare lines with em-dash separator (`Key — description`)
- Autofix capability: Section placement, ordering, structural entry removal

**Key Functions:**
```
collect_structural_headers(root) → set[lowercase_titles]
collect_semantic_headers(root) → dict[lowercase_title → locations]
extract_index_entries(index_path, root) → dict[lowercase_key → (lineno, entry, section)]
extract_index_structure(index_path, root) → (preamble, sections)
validate(index_path, autofix=True) → list[errors]
autofix_index(index_path, root, headers, structural) → bool
```

### Validation Checks

**Hard Errors (block commit):**
1. Duplicate index entries
2. Missing em-dash separator (D-3 format)
3. Word count violations (8-15 words total for key + description)
4. Orphan semantic headers (headers without index entries)
5. Orphan index entries (entries without matching headers, except exempt sections)
6. Duplicate headers across files (different files only)

**Autofix (silent correction):**
1. Section placement (entry in wrong file section)
2. Ordering within sections (entries out of file order)
3. Structural entries (entries pointing to organizational headers)

**Exempt Sections:**
- "Behavioral Rules (fragments — already loaded)"
- "Technical Decisions (mixed — check entry for specific file)"

### Parsing Details

**Document intro exemption:**
- Content between `# Title` and first `##` header is exempt from requiring index entries
- Prevents false positives on preamble/instructions

**File-based validation:**
- Indexed globs: `agents/decisions/*.md`
- learnings.md excluded (inlined via CLAUDE.md, processed by `/remember`)
- Memory-index.md itself is the index, not an indexed file

**Line tracking:**
- Preserves line numbers for error messages
- Uses line number from source file for ordering enforcement

## 2. Skill File Structure

**Symlink Pattern:** `.claude/skills/` contains symlinks to `agent-core/skills/*/SKILL.md`

**Skill Files Found (17 total):**
```
commit, design, gitmoji, handoff, handoff-haiku, next, opus-design-question,
orchestrate, plan-adhoc, plan-tdd, reflect, release-prep, remember,
review-tdd-plan, shelve, token-efficient-bash, vet
```

### Frontmatter Format (YAML)

**Example from `/remember` skill:**
```yaml
---
name: remember
description: This skill should be used when the user asks to "remember this"...
allowed-tools: Read, Write, Edit, Bash(git:*), Glob
user-invocable: true
---
```

**Fields:**
- `name`: Skill identifier (lowercase, hyphenated)
- `description`: When/how to use (multi-line literal style `|` for examples)
- `allowed-tools`: Tool whitelist with optional prefix matching (e.g., `Bash(git:*)`)
- `user-invocable`: Boolean (true = user can invoke directly)

**Body Structure:**
- H1 title
- "When to Use" section
- Numbered execution steps
- Supporting sections (Tool Constraints, Common Patterns, Integration)
- Progressive disclosure via `references/` and `examples/` subdirectories

## 3. Decision File Heading Structure

### workflow-core.md (13 H2 sections, 0 H3)

**H2 Sections:**
```
Oneshot Workflow Pattern
TDD Workflow Integration
Handoff Pattern: Inline Learnings
Design Phase: Output Optimization
Planning Pattern: Three-Stream Problem Documentation
TDD Workflow: Commit Squashing Pattern
Orchestrator Execution Mode
Orchestration Assessment: Three-Tier Implementation Model
Checkpoint Process for Runbooks
Phase-Grouped TDD Runbooks
Cycle Numbering Gaps Relaxed
No Human Escalation During Refactoring
Defense-in-Depth: Commit Verification
```

**Pattern:** Flat H2 structure, no nesting.

### testing.md (9 H2 sections, 8 H3 nested)

**H2 Sections:**
```
.Test Organization (structural)
.Mock Patching (structural)
.TDD Approach (structural)
TDD RED Phase: Behavioral Verification
TDD: Presentation vs Behavior
TDD Integration Test Gap
Conformance Validation for Migrations
```

**H3 Sections (under structural parents):**
```
Under .Test Organization:
  - Test Module Split Strategy

Under .Mock Patching:
  - Mock Patching Pattern

Under .TDD Approach:
  - Testing Strategy for Markdown Cleanup
  - Success Metrics
  - .Tests as Executable Contracts (structural)
  - .Exact Expected Strings Requirement (structural)
  - .Conformance Exception to Prose Descriptions (structural)
  - .Conformance Pattern (structural)
```

**Pattern:** Mix of flat H2 and nested H2/H3, with structural (`.` prefix) used for organizational sections.

## 4. Current memory-index.md

**Total Lines:** 181

**Entry Count:** 140 entries (with em-dash separator)

**Sections:** 9 total
- 2 mixed/preamble sections (Behavioral Rules, Technical Decisions)
- 7 file-specific sections (agents/decisions/*.md)

**File Sections:**
```
agents/decisions/prompt-structure-research.md (8 entries)
agents/decisions/implementation-notes.md (14 entries)
agents/decisions/project-config.md (2 entries)
agents/decisions/testing.md (4 entries)
agents/decisions/workflow-advanced.md (20 entries)
agents/decisions/workflow-core.md (14 entries)
agents/decisions/workflow-optimization.md (14 entries)
```

**Format Consistency:**
- All entries use em-dash separator: `Key — description`
- Bare lines (no bullet markers, no bold)
- Grouped by source file (H2 section per file)
- Entries in file order within sections

**Preamble:**
- 4 instructional paragraphs
- Consumption pattern guidance
- Append-only directive
- Exemption for @-referenced content

## 5. Project Package Structure

**Package Name:** `claudeutils`

**Location:** `src/claudeutils/`

**Modules (7 domains):**
```
account/         - Account/provider/model CLI
model/           - Model configuration
statusline/      - Context/usage display
recall/          - Memory index recall analysis (7 modules)
validation/      - Validation infrastructure (7 modules)
[root modules]   - Parsing, filtering, extraction, tokens
```

**Entry Point:** `claudeutils.cli:main`

**Dependencies:**
- anthropic >= 0.75.0 (API client)
- click >= 8.3.1 (CLI framework)
- platformdirs >= 4.5.1 (Platform paths)
- pydantic >= 2.0 (Data validation)
- pyyaml >= 6.0 (YAML parsing)

**Development:**
- mypy (strict type checking)
- ruff (linting + formatting)
- pytest (testing)

**Validation Modules:**
```
validation/cli.py               - CLI entry
validation/common.py            - Shared utilities
validation/decision_files.py    - Decision file validation
validation/jobs.py              - Job lifecycle validation
validation/learnings.py         - Learnings validation
validation/tasks.py             - Task validation
validation/memory_index.py      - Memory index facade (delegates to checks/helpers)
validation/memory_index_checks.py   - Core validation logic
validation/memory_index_helpers.py  - Parsing/collection utilities
```

**Pattern:** Validation logic consolidated to package, with bin/ scripts as thin CLI wrappers.

## 6. `/remember` Skill Entry Generation

**Location:** `/Users/david/code/claudeutils-memory-index-recall/agent-core/skills/remember/SKILL.md`

### Current Memory Index Integration (Step 4a)

**After consolidating a learning:**
1. Append to memory index: "Add one-line entry (summary + file reference) to appropriate section"
2. If new fragment created: Add `@`-reference to CLAUDE.md OR create `.claude/rules/` entry if path-scoped
3. If existing fragment updated: Verify index entry reflects updated content
4. If decision file updated: Verify `.claude/rules/` entry exists for path trigger

**Entry Format Guidance:**
- "one-line entry"
- "summary + file reference"
- Added to "appropriate section" (file-based)

**No explicit format specification for:**
- Em-dash separator (implicitly required by validator)
- Word count targets (8-15 enforced by validator)
- Keyword density guidance

### Learnings Quality Criteria

**Principle-level (consolidate):**
- States general constraint or pattern
- Applies beyond specific incident
- Example: "Always load skill context before editing"

**Incident-specific (reject/revise):**
- Describes what happened, not what to do
- Narrow to one case, not generalizable
- Example: "Edited skill without loading it" → revise to principle

**Staging Retention:**
- Keep < 7 active days (insufficient validation)
- Consolidate ≥ 7 active days with proven validity
- Drop if superseded or incident-specific

### Routing Guidance

**Fragment destination:** `agent-core/fragments/*.md`
- Workflow patterns, anti-patterns, directive conflicts, agent behavior

**Decision destination:** `agents/decisions/*.md`
- Architecture, implementation patterns, technology choices
- Consult `agents/decisions/README.md` for domain → file routing

**Implementation notes:** `agents/decisions/implementation-notes.md`
- Mock patterns, Python quirks, API details

## 7. Recall Analysis Tool

**Location:** `src/claudeutils/recall/` (7 modules, 8 files with __init__.py)

### Architecture

**Module Structure:**
```
cli.py           - Click CLI entry (index, sessions, baseline-before, threshold, format, output)
recall.py        - Core recall calculation (DiscoveryPattern, EntryRecall, RecallAnalysis)
relevance.py     - Fuzzy matching + topic extraction (find_relevant_entries)
index_parser.py  - Parse memory-index.md (IndexEntry model)
tool_calls.py    - Extract Read/Grep/Glob from session JSONL (ToolCall model)
topics.py        - Extract session topics from messages (topic keywords)
report.py        - Generate markdown/JSON output
```

**Key Models (Pydantic):**
```python
class DiscoveryPattern(str, Enum):
    DIRECT = "direct"                    # Read with no preceding Grep/Glob
    SEARCH_THEN_READ = "search_then_read"  # Grep/Glob before Read
    USER_DIRECTED = "user_directed"      # User message contained file path
    NOT_FOUND = "not_found"              # Relevant but not Read

class EntryRecall(BaseModel):
    entry_key: str
    referenced_file: str
    total_relevant_sessions: int
    sessions_with_read: int
    recall_percent: float
    # ... pattern percentages

class RecallAnalysis(BaseModel):
    sessions_analyzed: int
    relevant_pairs_total: int
    pairs_with_read: int
    overall_recall_percent: float
    per_entry_results: list[EntryRecall]
    pattern_summary: dict[str, int]
```

### Analysis Flow

1. **Parse index** → list[IndexEntry] (key, description, file)
2. **List sessions** → recent N sessions from history
3. **For each session:**
   - Extract topics from messages
   - Extract tool calls (Read, Grep, Glob)
   - Find relevant entries (fuzzy match topics against index)
   - Classify discovery pattern (DIRECT, SEARCH_THEN_READ, etc.)
4. **Aggregate results** → RecallAnalysis
5. **Generate report** → markdown or JSON

### CLI Options

```bash
claudeutils recall \
  --index agents/memory-index.md \
  --sessions 50 \
  --baseline-before 2026-02-05 \
  --threshold 0.3 \
  --format markdown \
  --output reports/analysis.md
```

**Defaults:**
- sessions: 30
- threshold: 0.3 (relevance score)
- format: markdown
- output: stdout

### Findings (from final-summary.md)

**200 sessions analyzed:**
- 7,483 relevant (session, entry) pairs
- 0 Read operations when relevant
- **0.0% overall recall**

**Validated:**
- All sessions occurred after index creation (Feb 1+) and stability (Feb 5+)
- Index had 60-70 entries throughout analysis
- Consistent 0% across 50, 100, and 200 session samples

**Root Cause:** Agents do not consult the memory index despite:
- Being loaded in every session (5,000 tokens via @-reference)
- Containing relevant information (tool validates keyword match)
- Clear instructions to "mentally scan" it

**Conclusion:** Passive awareness model is non-functional.

## Key Design Inputs

### 1. Validation Infrastructure Exists

**Reusable components:**
- Semantic vs structural header detection
- Index entry parsing with em-dash format
- Word count enforcement (8-15 words)
- Section-based organization (file grouping)
- Autofix for placement/ordering

**Extension opportunities:**
- Add new validation rules (e.g., trigger uniqueness)
- Support new index format (e.g., fuzzy triggers)
- Maintain backward compatibility with existing entries

### 2. Skill Development Patterns Established

**Frontmatter conventions:**
- YAML with name, description, allowed-tools, user-invocable
- Multi-line descriptions use literal style `|` for readability

**Body structure:**
- When to Use (invocation triggers)
- Numbered execution steps (protocol)
- Progressive disclosure (references/, examples/ subdirectories)

**Tool constraints:**
- Explicit whitelist with optional prefix matching
- Skill-specific tool restrictions

### 3. Decision File Structure is Hybrid

**Two patterns observed:**
- Flat H2 (workflow-core.md: 13 sections, no nesting)
- Nested H2/H3 (testing.md: 9 H2, 8 H3, mix of semantic and structural)

**Structural marker (`.` prefix):**
- Used for organizational sections (no direct content)
- Validator removes index entries pointing to structural sections
- Recursive rule applies at all levels (H2, H3, H4)

**Implication:** `/when` design must accommodate both flat and nested decision file structures.

### 4. Memory Index is Passive and Non-Functional

**Current model:**
- Loaded via @-reference (5,000 tokens per session)
- Agents told to "mentally scan" for relevance
- Expected to Read referenced files when relevant

**Observed behavior:**
- 0% recall across 200 sessions, 7,483 opportunities
- Agents do not consult index despite keyword matches
- Passive awareness fails to trigger active retrieval

**Design requirement:** `/when` must provide **active retrieval**, not passive awareness.

### 5. Package Architecture Supports New CLI Commands

**Existing pattern:**
```
src/claudeutils/<domain>/cli.py  - Click command
src/claudeutils/<domain>/*.py    - Domain logic
src/claudeutils/cli.py           - Main CLI router
pyproject.toml                   - Entry point configuration
```

**Validation consolidation precedent:**
- Logic moved from bin/ scripts to src/claudeutils/validation/
- CLI entry points delegate to package modules
- Enables testing, type checking, and code reuse

**Implication:** `/when` implementation would follow same pattern (when-recall/ subpackage with CLI).

### 6. Recall Tool Provides Measurement Infrastructure

**Capabilities:**
- Fuzzy topic matching (keywords → index entries)
- Discovery pattern classification (DIRECT, SEARCH_THEN_READ, etc.)
- Statistical analysis (recall %, confidence intervals)
- Temporal filtering (baseline-before cutoff)
- Output formats (markdown, JSON)

**Reusable components:**
- index_parser.py (parse memory-index.md)
- relevance.py (fuzzy matching)
- tool_calls.py (extract Read operations)
- topics.py (session keyword extraction)

**Implication:** Measurement infrastructure exists for A/B testing `/when` effectiveness.

## Gaps and Questions

### 1. Fuzzy Matching Engine

**Question:** What fuzzy algorithm for trigger → heading matching?

**Context:**
- Validator currently uses exact lowercase match (key.lower() == title.lower())
- Recall tool uses fuzzy topic matching (keywords → index entries)
- Design outline mentions "fuzzy engine bridges the gap" between compressed triggers and readable headings

**Need:** Specify fuzzy algorithm (Levenshtein? Token overlap? Weighted similarity?)

### 2. Trigger Format and Validation

**Question:** How are `/when` triggers structured and validated?

**Context:**
- Current entries: bare lines with em-dash (`Key — description`)
- `/when` triggers: keyword-rich, compressed for density
- Validator needs to check trigger → heading uniqueness

**Need:** Define trigger syntax, delimiter, and validation rules.

### 3. Integration with Existing Skills

**Question:** How does `/when` integrate with `/remember` and existing workflows?

**Context:**
- `/remember` currently appends to memory-index.md (Step 4a)
- `/when` introduces new recall mechanism
- Need migration path or coexistence strategy

**Need:** Clarify whether `/when` replaces memory-index.md or coexists with it.

### 4. Context Injection Mechanism

**Question:** How are recalled decisions injected into agent context?

**Context:**
- UserPromptSubmit hooks can inject `additionalContext`
- Rules files support path-based triggers (frontmatter)
- MCP tools unavailable in sub-agents (Task tool)

**Need:** Choose injection mechanism (hook? rule file? skill invocation?)

### 5. Retrieval Behavioral Trigger

**Question:** What explicitly triggers retrieval when agent faces a decision?

**Context:**
- Passive model failed (agents don't "mentally scan")
- Active model requires explicit trigger
- Agents don't proactively seek definitions (per learnings.md: "Behavioral triggers beat passive knowledge")

**Need:** Define when and how agents invoke `/when` (automatic via hook? manual in skills? orchestrator prompt?)

## Files Referenced

**Validator:**
- `/Users/david/code/claudeutils-memory-index-recall/agent-core/bin/validate-memory-index.py`

**Skills:**
- `/Users/david/code/claudeutils-memory-index-recall/agent-core/skills/remember/SKILL.md`
- `/Users/david/code/claudeutils-memory-index-recall/agent-core/skills/design/SKILL.md`
- `/Users/david/code/claudeutils-memory-index-recall/agent-core/skills/handoff/SKILL.md`

**Decision Files:**
- `/Users/david/code/claudeutils-memory-index-recall/agents/decisions/workflow-core.md`
- `/Users/david/code/claudeutils-memory-index-recall/agents/decisions/testing.md`

**Memory Index:**
- `/Users/david/code/claudeutils-memory-index-recall/agents/memory-index.md`

**Recall Analysis:**
- `/Users/david/code/claudeutils-memory-index-recall/plans/memory-index-recall/reports/final-summary.md`
- `/Users/david/code/claudeutils-memory-index-recall/src/claudeutils/recall/*.py` (7 modules)

**Project Config:**
- `/Users/david/code/claudeutils-memory-index-recall/pyproject.toml`

---

**Report complete. Findings structured for design consumption.**
