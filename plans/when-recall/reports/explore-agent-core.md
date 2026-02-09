# Agent-Core Infrastructure Exploration

**Date:** 2026-02-08

## Summary

The agent-core/ directory is a comprehensive toolkit for orchestrating workflows, managing decisions, and validating artifacts. It contains 16 skills, 14 specialized agents, 10 validation scripts, structured decision files (agents/decisions/), and production infrastructure for memory indexing and workflow execution. All index entry generation and decisions management is manual — no automated discovery or generation scripts exist.

---

## 1. Directory Structure

### agent-core/

```
agent-core/
├── skills/               # 16 executable skills for workflow management
├── agents/               # 14 specialized agents for execution, review, design
├── bin/                  # 10 validation + preparation scripts
├── hooks/                # Pre-tool and user-prompt hooks for session control
├── fragments/            # 17 behavioral rule fragments (already @-loaded via CLAUDE.md)
├── docs/                 # 7 progressive documentation files
├── configs/              # Environment configuration
├── templates/            # Templates for new projects and CLAUDE.md files
├── migrations/           # Historical migration documentation
├── plans/                # Internal planning artifacts
├── README.md             # Overview
├── justfile              # Recipe automation
└── .gitignore            # Excludes local configs
```

### agents/decisions/ — Semantic Header Structure

**10 decision files with H2/H3 structure:**

1. **data-processing.md** — 8 H2 sections (5 structural: .Module Architecture, .Path Handling, .Session Metadata, .Feedback Processing, .Encoding)
   - H3 decision headings: Minimal `__init__.py`, Private Helpers Stay With Callers, Module Split Pattern, Path Encoding Algorithm, etc.
   - ~400 lines, comprehensive module architecture + data model decisions

2. **cli.md** — 2 H2 sections (both structural: .CLI Conventions, .Output Formats)
   - H3 decision headings: Path.cwd() vs os.getcwd(), Error Output Pattern, Entry Point Configuration, Feedback Processing Output Formats, Token Output Format
   - ~70 lines, focused CLI patterns

3. **testing.md** — 2 H2 sections (both structural: .Test Organization, .Mock Patching)
   - H3 decision headings: Test Module Split Strategy, Mock Patching Pattern
   - ~60 lines, testing conventions

4. **validation-quality.md** — 2 H2 sections (both structural: .Data Models, .Code Quality)
   - H3 decision headings: Pydantic for Validation, FeedbackType Enum, Docformatter vs. Ruff D205 Conflict, Complexity Management, No Suppression Shortcuts, Type Annotations
   - ~80 lines, data validation and quality standards

5. **markdown-tooling.md** — 3 H2 sections (2 structural: .Token Counting, .Markdown Cleanup Architecture; 1 semantic: Remark-cli over Prettier)
   - H3 decision headings: Model as First Positional Argument, Model Alias Support, Anthropic API Integration, Empty File Optimization, No Glob Expansion, Problem/Solution/Design/Extend vs new functions/Error on invalid patterns/Processing order/Prefix detection/Indentation amount/Future direction
   - ~150 lines, token counting and markdown processing

6. **project-config.md** — 2 H2 sections (both structural: .Memory Index Pruning, .Claude Code Configuration)
   - H3 decision headings: Growth + Consolidation Model, Flags are exact tokens, Root marker for scripts
   - ~100 lines, project-level configuration decisions

7. **workflow-core.md** — 12 H2 sections (all semantic, no structural prefix)
   - H2 decision headings: Oneshot Workflow Pattern, TDD Workflow Integration, Handoff Pattern: Inline Learnings, Design Phase: Output Optimization, Planning Pattern: Three-Stream Problem Documentation, TDD Workflow: Commit Squashing Pattern, Orchestrator Execution Mode, Orchestration Assessment: Three-Tier Implementation Model, Checkpoint Process for Runbooks, Phase-Grouped TDD Runbooks, Cycle Numbering Gaps Relaxed, No Human Escalation During Refactoring, Defense-in-Depth: Commit Verification
   - ~320 lines, comprehensive workflow patterns

8. **workflow-optimization.md** — 5 H2 sections (all semantic)
   - H2 decision headings: Handoff tail-call pattern, Handoff commit assumption, Routing layer efficiency, Vet agent context usage, Outline-first design workflow, Model selection for design guidance, Design review uses opus, Vet catches structure misalignments, Agent-creator reviews in orchestration, Template commit contradiction, Orchestrator model mismatch, Happy path first TDD, Runbook Outline Format
   - ~170 lines, efficiency and resource optimization patterns

9. **workflow-advanced.md** — 4 H2 sections (1 structural: .Documentation and Knowledge Management; 3 semantic)
   - H2 decision headings: Seeding Before Auto-Generation, Index Entries Require Backing Documentation, Template Merge Semantics, Requirements Immutable During Execution, Ambient Awareness Beats Invocation, Task Prose Keys Pattern, Commit RCA Fixes Active, Precommit Is Read-Only, Outline Enables Phase-by-Phase Expansion, Phase-by-Phase Review Pattern, Review Agent Fix-All Pattern, Recommendations Inline Transmission, Prose Test Descriptions Save Tokens, Complexity Before Expansion, Consolidation Gates Reduce Orchestrator Overhead, Workflow Feedback Loop Insights, Dogfooding Validates Design, TDD GREEN Behavioral Descriptions, Efficient Model Analysis Requires Verification
   - ~250 lines, advanced pattern documentation

10. **implementation-notes.md** — 5 H2 sections (2 structural: .Claude Code Hooks and Sessions, .Version Control Patterns, .Tokenization and Formatting, .Design and Requirements; 1 semantic: Skill Rules Placement)
    - H3 decision headings: @ references limitation, SessionStart hook limitation, UserPromptSubmit hook filtering, Hook capture impractical, MCP tools unavailable, Loaded skill overrides fresh-session framing, Commits are sync points, Never auto-commit, Title-words beat kebab-case, Bare lines beat list markers, Default semantic/mark structural, Design tables are binding constraints, Header titles not index entries, Phase-Grouped Runbook Header Format, Prose Gate D+B Hybrid Fix
    - ~214 lines, implementation-specific decisions and limitations

**Header Pattern Summary:**
- Structural headers (H2/H3 starting with `.`): Used for organizational sections with only sub-headings (no direct content)
- Semantic headers (H2/H3 without `.`): Knowledge sections with decision content — MUST have index entries
- H3 used for individual decisions under H2 grouping sections
- No H4+ in use across decision files

---

## 2. Skills Infrastructure (agent-core/skills/)

### 16 Production Skills

1. **design** — Entry point for architecture sessions; complexity triage routes to TDD or general workflow
2. **plan-adhoc** — Create general-purpose runbooks (ad-hoc tasks, infrastructure, refactoring)
3. **plan-tdd** — Create TDD-specific cycle-based runbooks with automated review
4. **orchestrate** — Execute runbooks step-by-step with error escalation and state management
5. **vet** — Quality review and fix aggregation (deprecated, replaced by vet-fix-agent in Task tool)
6. **handoff** — Session context preservation before restart; updates pending tasks
7. **handoff-haiku** — Lightweight handoff for haiku sub-agents (no learnings judgment)
8. **commit** — Version control checkpoint with gitmoji selection and STATUS display
9. **reflect** — Post-execution Root Cause Analysis and pattern documentation
10. **remember** — Consolidate learnings into permanent decision files and memory index
11. **next** — Task recovery and context discovery
12. **shelve** — Deferred task management
13. **opus-design-question** — Delegation for architectural guidance during planning/execution
14. **review-tdd-plan** — Anti-pattern detection for TDD runbooks
15. **token-efficient-bash** — Token economy patterns for bash scripting
16. **gitmoji** — Emoji selection helper for commit messages

**Skill Organization:**
- Each skill in `agent-core/skills/<name>/SKILL.md`
- Supporting files in skill directory (references, examples, templates)
- Most skills have phase-based execution structure
- Integration points: CLAUDE.md commands (`/design`, `/plan-adhoc`, etc.)

---

## 3. Agents Infrastructure (agent-core/agents/)

### 14 Specialized Agents

**Execution Agents:**
1. **quiet-task.md** — Baseline for plan-specific agents; generic task execution
2. **tdd-task.md** — TDD-aware execution with cycle-based scoping
3. **quiet-explore.md** — File search and exploration specialist
4. **remember-task.md** — Learnings consolidation and index management

**Review Agents:**
5. **vet-agent.md** — Quality review (generic code/documentation review)
6. **vet-fix-agent.md** — Review + automatic fixing of issues
7. **tdd-plan-reviewer.md** — Anti-pattern detection (prescriptive code in GREEN phases)
8. **design-vet-agent.md** — Architecture design review (for opus-designed specs)

**Analysis Agents:**
9. **outline-review-agent.md** — Runbook outline validation
10. **runbook-outline-review-agent.md** — Phase-by-phase outline review
11. **review-tdd-process.md** — TDD process verification

**Specialized Agents:**
12. **refactor.md** — Refactoring assistance
13. **memory-refactor.md** — Memory index restructuring
14. **test-hooks.md** — Hook configuration and testing

**Agent Pattern:**
- Created dynamically by `prepare-runbook.py` at `.claude/agents/<plan-name>-task.md`
- Baseline agents in agent-core, plan-specific variants inherit and customize
- No manual agent creation in main project; generated during plan preparation

---

## 4. Validation & Preparation Scripts (agent-core/bin/)

### 10 Production Scripts

**Validation Scripts** (run in precommit via justfile):
1. **validate-memory-index.py** (480 lines)
   - Checks index entries against semantic headers in agents/decisions/
   - Validates entry format: `Key — description` (em-dash separator)
   - Word count 8-15 per entry (hard error)
   - Autofix: Reorders entries by file section and source line number
   - Removes entries pointing to structural sections
   - Detects orphan entries (no matching header) and orphan headers (no entry)

2. **validate-decision-files.py** (145 lines)
   - Detects sections with only sub-headings (no direct content)
   - Requires structural marker (`.` prefix) for organizational sections
   - Hard error, no autofix — agent decides: add marker or add content
   - Used during `/remember` skill to enforce decision file quality

3. **validate-learnings.py** (80 lines)
   - Checks learnings.md format (## Title headers)
   - Max 5 words per title (hard error)
   - Uniqueness check (no duplicate titles)
   - Skips preamble (first 10 lines)

4. **validate-tasks.py**
   - Validates session.md task format
   - Checks task metadata (command, model, restart flag)

5. **validate-jobs.py**
   - Validates agents/jobs.md plan tracking
   - Checks status enum values (requirements, designed, planned, complete)

**Preparation Scripts:**
6. **prepare-runbook.py** (250+ lines)
   - Transforms runbook markdown into execution artifacts
   - Creates: plan-specific agent, step/cycle files, orchestrator plan
   - Supports: general runbooks (## Step N:), TDD runbooks (## Cycle X.Y:), phase-grouped directories
   - Extracts YAML frontmatter (type: tdd|general, model, name)
   - Validates cycle numbering (gaps = warning, duplicates = error)
   - Output: `.claude/agents/<name>-task.md`, `plans/<name>/steps/`, `plans/<name>/orchestrator-plan.md`

7. **assemble-runbook.py** (200+ lines)
   - Assembles phase-grouped files (runbook-phase-*.md) into single runbook
   - Used by prepare-runbook.py for directory input
   - Maintains header levels (### Phase N, ## Step M)

**Utility Scripts:**
8. **batch-edit.py** (150+ lines)
   - Marker-based batch file editing (uses `<<<` `>>>` `===` markers)
   - Token-efficient alternative to JSON format
   - Supports multi-line content without escaping

9. **add-learning.py** (60 lines)
   - Creates dated learning files in agents/learnings/
   - Appends references to pending.md
   - **NOTE:** Obsolete — learnings now inline in session.md; kept for legacy

10. **learning-ages.py**
    - Analyzes learning staleness (not used in current workflow)

**Shell Utilities:**
11. **task-context.sh** (shell script)
    - Recovers session.md from git history by task name
    - Uses `git log -S` for pattern search
    - Returns full session.md from commit where task first appeared

---

## 5. Memory Index Format & Generation

### Current Index Structure (agents/memory-index.md)

**Organization:**
- Sections grouped by file: `## agents/decisions/<filename>.md`
- Exempt sections: "Behavioral Rules (fragments — already loaded)", "Technical Decisions (mixed — check entry for specific file)"
- Entries: `Key — description` (em-dash separator, 8-15 words hard limit)
- ~169 entries across 10 decision file sections + 2 exempt sections
- 5000 tokens (~25 tokens per entry)

**Entry Format Specification:**
- Key: lowercase title from corresponding semantic header
- Description: keyword-rich 5-7 word phrase (after em-dash)
- Example: `Minimal __init__.py — keep empty, prefer explicit imports from specific modules`
- Pattern: Bare lines (no list markers, no bold), flat structure within sections

**Validation Rules:**
- All semantic headers (##+ not starting with `.`) MUST have index entries
- All index entries MUST match semantic headers in agents/decisions/
- No duplicate entries (case-insensitive key matching)
- No orphan entries (entries without matching headers)
- No orphan headers (headers without entries)
- Entries in correct file section (autofix: reorders by source file)
- Entries in file order within sections (autofix: sorts by line number in source)

**Generation Status:**
- **MANUAL:** All entries added by hand during planning/design/learnings consolidation
- **NO AUTOMATION:** No scripts scan decision files and auto-generate entries
- **SEEDING PATTERN:** New decision files must have manual entries added (~5-10 per file as they're created)
- **VALIDATION ONLY:** validate-memory-index.py checks consistency, doesn't generate

### How Index Maps to Decisions

**Mapping Process:**
1. Decision file contains semantic header: `## Minimal __init__.py` (data-processing.md, line 7)
2. Index entry: `## agents/decisions/data-processing.md` section
3. Entry line: `Minimal __init__.py — keep empty, prefer explicit imports from specific modules`
4. Validation: Matches header title exactly (case-insensitive), em-dash separator required
5. Word count: 12 words total (within 8-15 limit)

**Consumption Pattern (from memory-index.md header):**
1. Index loaded via `@agents/memory-index.md` in CLAUDE.md
2. Agent scans loaded index mentally (no grep/re-read)
3. Identifies relevant entry keyword
4. Reads corresponding decision file directly
5. Accesses specific section via header anchor

---

## 6. Decisions Management Workflow

### Current Process (Manual)

**Entry Creation Flow:**
1. During `/design` or `/plan-adhoc`: Design produces decision output
2. After commit: `/remember` skill triggered (optional, user invokes)
3. Skill locates decision content in design/problem documents
4. Consolidates into permanent decision file (agents/decisions/*.md)
5. Adds new semantic header (H2/H3) to file
6. **MANUAL STEP:** Add corresponding index entry to agents/memory-index.md
7. `validate-memory-index.py` in precommit: Checks consistency
8. Commit includes both decision file update + index entry

**File Organization Logic:**
- **agents/decisions/data-processing.md** — Module architecture, data models, paths
- **agents/decisions/cli.md** — CLI patterns, output formats
- **agents/decisions/testing.md** — Test organization, mocking patterns
- **agents/decisions/validation-quality.md** — Data validation, code quality
- **agents/decisions/markdown-tooling.md** — Token counting, markdown processing
- **agents/decisions/project-config.md** — Project-level config, memory index strategy
- **agents/decisions/workflow-core.md** — Core workflow patterns (oneshot, TDD, handoff)
- **agents/decisions/workflow-optimization.md** — Efficiency patterns
- **agents/decisions/workflow-advanced.md** — Requirements, knowledge management, specialized patterns
- **agents/decisions/implementation-notes.md** — Implementation-specific decisions, limitations, hooks

### No Automated Index Generation

**Key Finding:**
- Decision files are created/updated by `/remember` skill (optional)
- Index entries are ALWAYS manual additions
- No script exists to scan decision files and auto-generate index entries
- No discovery mechanism to identify "new decision needs entry"
- Validation is reactive (precommit checks, errors if entry missing)

**Implications:**
1. Orphan headers (headers without entries) are errors that block commit
2. Orphan entries (entries without headers) are errors that block commit
3. Seeding required for new decision files (~5-10 entries manually added initially)
4. Growth is user-driven: `/remember` consolidates, agent manually indexes
5. Maintenance burden: Both file AND index must be updated together

---

## 7. Key Infrastructure Components

### Fragments (Behavioral Rules)

**17 fragments in agent-core/fragments/ (already @-loaded):**
- bash-strict-mode.md — Token-efficient bash patterns
- claude-config-layout.md — Hook configuration and symlink management
- code-removal.md — Delete obsolete code instead of archiving
- commit-delegation.md — Commit workflow and delegation protocols
- commit-skill-usage.md — Always use `/commit` skill
- communication.md — Stop on unexpected results, explicit instructions
- delegation.md — Delegate everything, script-first evaluation
- design-decisions.md — Use `/opus-design-question` for design choices
- error-classification.md — Error taxonomy and handling patterns
- error-handling.md — Never swallow errors
- execute-rule.md — Session modes (STATUS, EXECUTE, RESUME, WORKTREE)
- no-estimates.md — Never estimate unless requested
- prerequisite-validation.md — Dependency verification patterns
- project-tooling.md — Use project recipes before ad-hoc commands
- sandbox-exemptions.md — Sandbox bypass configuration (dangerouslyDisableSandbox)
- tmp-directory.md — Use project-local tmp/, not system /tmp/
- token-economy.md — Don't repeat file contents, be concise
- tool-batching.md — Batch reads and edits for efficiency
- vet-requirement.md — Vet all production artifacts
- workflows-terminology.md — Workflow definitions and routes

**All loaded by CLAUDE.md @-reference; not indexed in memory-index.md (would be noise)**

### Hooks

**2 Pre-tool use hooks:**
1. **submodule-safety.py** — Blocks commands when cwd != project root (enforces absolute paths)
2. **pretooluse-symlink-redirect.sh** — Redirects symlinks to real paths in agent-core/

**1 User prompt submit hook:**
1. **userpromptsubmit-shortcuts.py** — Parses workflow shortcuts (s, x, r, wt, etc.)

**Supporting shell scripts:**
- pretooluse-block-tmp.sh — Blocks writes to system /tmp/
- claude-env.sh — Environment setup

### Documentation

**Progressive discovery docs (agent-core/docs/):**
1. @file-pattern.md — File naming and path conventions
2. general-workflow.md — Step-by-step general workflow execution
3. migration-guide.md — Historical migration documentation
4. pattern-plan-specific-agent.md — Runbook-specific agent integration
5. pattern-weak-orchestrator.md — Weak orchestrator architecture
6. shortcuts.md — Workflow shortcut reference
7. tdd-workflow.md — TDD workflow execution guide

---

## 8. Patterns & Conventions

### Index Entry Standards

**Word Count (Hard Error: 8-15 words):**
- Minimum: Avoids single-word keys (too vague)
- Maximum: Forces concise descriptions (prevents verbosity)
- Counts: Key + description words combined
- Example: `Model as first positional argument — required parameter for accurate token counts` (11 words)

**Em-dash Separator (Hard Error):**
- Format: `Key — description` (em-dash, not hyphen or double-dash)
- Key part: Lowercase header title
- Description part: Keyword-rich discovery phrase
- No line breaks or special characters

**Placement & Ordering:**
- Entries grouped by file section
- Within section: sorted by source file line number (autofix maintains)
- Exempt sections: Preserved as-is (fragments, technical decisions)
- No explicit priority or importance ranking

### Decision File Structure

**Header Conventions:**
- H2 for major decision areas or individual large decisions
- H3 for grouped decisions under organizational H2 sections
- Structural sections (organizational only): Prefix with `.` (e.g., `## .Data Models`)
- Semantic sections: No prefix, must have substantive content
- Never nested more than H3 (no H4+)

**Decision Content Pattern:**
- Bold key phrase (e.g., **Decision**, **Rationale**, **Impact**)
- Structured sections under each decision
- Code examples where applicable
- Decision dates for traceability
- Cross-references to related decisions (rare)

**Validation:**
- Structural sections: No direct content (only sub-headings)
- Semantic sections: MUST have content before any sub-headings
- Content threshold: 2+ substantive lines before first sub-heading qualifies as "semantic"
- validate-decision-files.py enforces H2+ sections have either marker or content

---

## 9. Gaps & Unresolved Questions

### Index Generation

1. **No automation for new entries:** When new decision headers are added, there's no script to alert or auto-generate corresponding index entries. Manual process relies on developer discipline.

2. **Seeding mechanism unclear:** While policy says "seed existing permanent docs before auto-generation," no documented seeding process exists for new decision files. ~5-10 entries per file estimated but not formalized.

3. **Scalability of manual process:** 10 decision files × ~17 entries/file = 170 total index entries. Growth to 20+ files would create maintenance burden. No plan for consolidation or archival.

### Decisions Management

1. **Decision routing not formalized:** How does agent choose which decision file to update? Current pattern (by `/remember` skill) is assumed but not documented.

2. **H3 adoption inconsistent:** Some files use H3 for individual decisions (data-processing.md), others use H2 (workflow-core.md). No explicit rule for when to use which level.

3. **Fragment vs decision boundary:** 17 fragments in agent-core/fragments/ are not indexed. Fragments get @-loaded in CLAUDE.md, decisions require on-demand access. Boundary is clear (location-based) but not explicitly defined in architecture docs.

### Validation Coverage

1. **No validation for H3 headers:** validate-memory-index.py and validate-decision-files.py both work on H2+. H3 decisions are not explicitly validated (though H2 covering H3s are structural and exempt).

2. **Duplicate header detection incomplete:** Checks for duplicates across files but not within same file (edge case, currently assumes no within-file duplicates).

3. **No automation for removing orphan entries:** When a semantic header is deleted from decision file, the corresponding index entry becomes orphan. validate-memory-index.py flags it as error; requires manual removal or autofix-rebuild.

### Documentation Gaps

1. **No explicit "index generation" guide:** Documentation describes consumption (memory-index.md header), validation (validate-memory-index.py), but not creation process.

2. **Semantic vs structural decision:** Boundary between what goes in decision files vs fragments is not explicitly documented (implicit: fragments = @-loaded behavior rules, decisions = on-demand domain knowledge).

3. **Cross-referencing rare:** Decision files rarely reference each other; unclear if this is intentional (independent domains) or just current practice.

---

## 10. Implementation Reference

### Key Files for Index/Decisions Work

**For understanding memory index:**
- `/Users/david/code/claudeutils-memory-index-recall/agents/memory-index.md` — Index specification and all 169 entries
- `/Users/david/code/claudeutils-memory-index-recall/agent-core/bin/validate-memory-index.py` — Validation logic, autofix mechanism

**For understanding decisions:**
- `/Users/david/code/claudeutils-memory-index-recall/agents/decisions/` — All 10 decision files (2,000+ lines total)
- `/Users/david/code/claudeutils-memory-index-recall/agent-core/bin/validate-decision-files.py` — Structure validation

**For understanding workflow:**
- `/Users/david/code/claudeutils-memory-index-recall/agent-core/skills/remember/SKILL.md` — `/remember` skill that consolidates learnings to decisions
- `/Users/david/code/claudeutils-memory-index-recall/agent-core/bin/prepare-runbook.py` — Runbook preparation (referenced in workflow skills)

**For understanding agents:**
- `/Users/david/code/claudeutils-memory-index-recall/agent-core/agents/quiet-task.md` — Baseline agent for plan-specific variants
- `/Users/david/code/claudeutils-memory-index-recall/agent-core/agents/vet-fix-agent.md` — Review + fix pattern

**For understanding skills:**
- `/Users/david/code/claudeutils-memory-index-recall/agent-core/skills/design/SKILL.md` — Entry point for all work
- `/Users/david/code/claudeutils-memory-index-recall/agent-core/skills/plan-adhoc/SKILL.md` — General planning pattern
- `/Users/david/code/claudeutils-memory-index-recall/agent-core/skills/orchestrate/SKILL.md` — Execution orchestrator

### Command Reference

**Index validation (precommit):**
```bash
agent-core/bin/validate-memory-index.py agents/memory-index.md
```

**Decision validation (precommit):**
```bash
agent-core/bin/validate-decision-files.py
```

**Runbook preparation (manual, during planning):**
```bash
agent-core/bin/prepare-runbook.py plans/<name>/runbook.md
```

**Learning consolidation (via skill):**
```
/remember — consolidates learnings into decision files + updates index
```

---

## Summary of Key Findings

1. **Complete infrastructure exists** for workflow management, validation, and agent coordination
2. **Index is manually maintained** — 169 entries across 10 decision files, all hand-added
3. **No automation for entry generation** — validation only, no discovery or auto-generation
4. **Decision files are semantic** — H2/H3 structure with validation of content requirements
5. **Validation is reactive** — precommit checks, hard errors block commits
6. **Skills drive workflow** — 16 production skills in agent-core, extensible pattern
7. **Agents are generated** — prepare-runbook.py creates plan-specific variants from baselines
8. **Patterns are documented** — fragments + decision files cover both behavioral rules and technical decisions
9. **Seeding required for growth** — new decision files need ~5-10 manual index entries initially
10. **Clear separation** — fragments (behavior, @-loaded), decisions (domain knowledge, on-demand)
