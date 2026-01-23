# pytest-md AGENTS.md Fragmentation Analysis

**Source**: /Users/david/code/pytest-md/AGENTS.md
**Total Lines**: 152
**Date**: 2026-01-18

---

## Section 1: Developer Documentation + Commands + Environment Notes (lines 1-36)

**Classification**: project-specific
**Rationale**: Contains pytest-md specific installation commands, test commands using project's justfile, and references to project-specific dev documentation. The environment notes mention project-specific tools (`pytest`, `/commit-commands:commit`).
**Action**: Remains in pytest-md AGENTS.md
**Target**: Remains in pytest-md

**Content Preview** (first 10 lines):

```
# AGENTS.md

This file provides guidance to AI coding agents when working with code in this
repository.

## Developer Documentation

- `dev/architecture.md` - Plugin internals and implementation details
- `dev/design-decisions.md` - Design rationale and trade-offs
```

---

## Section 2: Persistent vs Temporary Information (lines 38-55)

**Classification**: reusable
**Rationale**: This is a universal guideline about what belongs in AGENTS.md vs session.md vs plans/. The concept applies to any project using agent-based development. Only the file paths mentioned are project-neutral (AGENTS.md, session.md, plans/).
**Action**: Extract to reusable fragment
**Target**: agent-core/fragments/persistent-vs-temporary.md

**Content Preview** (first 10 lines):

```
### Persistent vs Temporary Information

**CRITICAL**: AGENTS.md is for persistent, long-lived information only.

- **Do put in AGENTS.md**: Architecture, commands, design principles, testing guidelines
- **Do NOT put in AGENTS.md**: Current plans, active tasks, session-specific context,
  implementation details

**Current plans and tasks belong in:**

```

**Notes**:

- The REMEMBER directive concept (lines 52-55) is part of this reusable pattern
- No project-specific elements in this section

---

## Section 3: Context Management (lines 57-85)

**Classification**: handoff skill candidate (with reusable fragment)
**Rationale**: This section describes session.md management, handoff protocol, and context flushing strategy. The core concepts are reusable, but the handoff protocol (lines 80-85) is specifically a skill pattern. The size discipline and flushing strategy (lines 65-78) are reusable guidelines.
**Action**: Split into two components:

1. Reusable fragment: session.md management guidelines (lines 57-78)
2. Skill: handoff protocol (lines 80-85)
   **Target**:

- agent-core/fragments/context-management.md (lines 57-78)
- agent-core/skills/skill-handoff.md (lines 80-85 as basis)

**Content Preview** (first 10 lines):

```
### Context Management

1. **session.md** is the primary context file for:
   - Current work state (what's in progress)
   - Handoff notes for next agent
   - Recent decisions with rationale
   - Known blockers

2. **Size discipline**: Keep session.md under ~100 lines
```

**Notes**:

- Lines 74-78 reference claudeutils/agents/ as an example - keep this as-is
- The handoff protocol at the end is actionable and skill-like

---

## Section 4: Opus Orchestration (lines 87-104)

**Classification**: reusable
**Rationale**: Model selection guidelines, sub-agent usage patterns, and workflow principles are universal orchestration patterns. No project-specific elements except example paths (tmp/, plans/), which are standard conventions.
**Action**: Extract to reusable fragment
**Target**: agent-core/fragments/orchestration-patterns.md

**Content Preview** (first 10 lines):

```
### Opus Orchestration

**Model selection:**
- Simple mechanical tasks → write a script if shorter than prompting haiku (saves opus output tokens)
- Simple cognitive tasks → use haiku
- Use sonnet when it can be prompted in fewer tokens than haiku
- Sonnet writing a script instead of delegating to haiku is also valid

**Sub-agent usage:**
```

**Notes**:

- This section has clear architectural value for any multi-model orchestration
- The script-first evaluation principle here complements CLAUDE.md's delegation guidance

---

## Section 5: Testing Guidelines (lines 106-113)

**Classification**: project-specific
**Rationale**: Contains pytest-md specific test commands (`pytest tests/test_output_expectations.py`), references to quiet/default/verbose modes specific to this plugin, and a project-specific tool reference (`claudeutils tokens sonnet`).
**Action**: Remains in pytest-md AGENTS.md
**Target**: Remains in pytest-md

**Content Preview** (first 8 lines):

```
### Testing Guidelines

**Output Verification**: Always run `pytest tests/test_output_expectations.py -v` after
making changes to verify output format matches expectations. This automated test suite
validates quiet/default/verbose modes and collection error handling.

**Token Count Verification**: Do not guess token counts. Always use
`claudeutils tokens sonnet <file>` to verify actual token usage.
```

---

## Section 6: Documentation Organization (lines 115-152)

**Classification**: reusable
**Rationale**: File naming conventions, directory structure patterns, and documentation organization principles are project-neutral. The specific example uses pytest-markdown-report but the pattern is universal (UPPERCASE.md for agent docs, lowercase-dash.md for session, dev/ for internals, plans/ for plans).
**Action**: Extract to reusable fragment with template structure
**Target**: agent-core/fragments/documentation-organization.md

**Content Preview** (first 10 lines):

```
## Documentation Organization

**File naming conventions:**

**Root-level files** (UPPERCASE.md):

- `AGENTS.md` - Persistent agent guidance (this file)
- `README.md` - Project overview and user documentation

**Session context** (lowercase-dash.md):
```

**Notes**:

- The directory structure diagram (lines 140-152) is an example, not project-specific
- This pattern is already in use across multiple projects

---

## Extraction Plan

1. Create `agent-core/fragments/persistent-vs-temporary.md` with Section 2 content (lines 38-55)
2. Create `agent-core/fragments/context-management.md` with Section 3 guidelines (lines 57-78, excluding handoff protocol)
3. Create `agent-core/skills/skill-handoff.md` based on handoff protocol pattern (lines 80-85)
4. Create `agent-core/fragments/orchestration-patterns.md` with Section 4 content (lines 87-104)
5. Create `agent-core/fragments/documentation-organization.md` with Section 6 content (lines 115-152)
6. Update pytest-md/AGENTS.md to:
   - Keep Sections 1 and 5 (project-specific)
   - Reference fragments for Sections 2, 4, 6
   - Reference handoff skill for Section 3 protocol
   - Add composition includes/references at appropriate locations
7. Test composed output ensures all guidance remains accessible

---

## Summary

- **Reusable sections**: 4 → agent-core/fragments/
  - persistent-vs-temporary.md (Section 2)
  - context-management.md (Section 3 partial)
  - orchestration-patterns.md (Section 4)
  - documentation-organization.md (Section 6)
- **Project-specific sections**: 2 → remain in pytest-md
  - Developer Documentation + Commands + Environment (Section 1)
  - Testing Guidelines (Section 5)
- **Skills identified**: 1 → agent-core/skills/
  - skill-handoff.md (from Section 3 handoff protocol)

**Total extraction**: 4 fragments + 1 skill from 6 identified sections

**Composition strategy**: pytest-md AGENTS.md will use include/reference mechanism to compose from fragments while maintaining project-specific customization.
