# Phase 1: Foundation - Execution Plan

**Status**: Ready for review
**Target**: Haiku execution
**Date**: 2026-01-15

---

## Overview

Phase 1 establishes the foundation for the rules unification system by creating the `agent-core` repository, extracting shared fragments, and implementing template-based generation for AGENTS.md. This phase will be tested in one scratch repository before broader rollout.

---

## Prerequisites

- [ ] claudeutils repository on `unification` branch
- [ ] Access to scratch repositories for testing (emojipack or pytest-md)
- [ ] Current AGENTS.md variants available for extraction

---

## Execution Steps

### Step 1: Create agent-core Repository Structure

**Objective**: Initialize the shared repository with proper directory structure.

**Technical Details**:
- Initialize as git repository locally first (GitHub remote can be added later)
- Location: `/Users/david/code/agent-core` (sibling to claudeutils)
- Structure based on design.md:64-68

**Actions**:
1. Create repository directory: `/Users/david/code/agent-core`
2. Initialize git: `git init`
3. Create directory structure:
   ```
   agent-core/
     fragments/
       justfile-base.just
       ruff.toml
       mypy.toml
       communication.md
       delegation.md
       tool-preferences.md
       hashtags.md
       AGENTS-framework.md
     agents/
       (reserved for Phase 2)
     composer/
       (reserved for future)
     README.md
   ```
4. Create initial README.md documenting purpose and structure
5. Initial commit: "Initialize agent-core repository structure"

**Validation**:
- [ ] Directory structure matches design
- [ ] Git repository initialized
- [ ] README.md explains purpose

---

### Step 2: Extract justfile-base.just

**Objective**: Identify and extract shared justfile recipes used across projects.

**Source Analysis Required**:
- claudeutils/justfile
- scratch/emojipack/justfile (if exists)
- scratch/pytest-md/justfile (if exists)
- home repository justfile (mentioned in design)

**Shared Recipes to Extract** (common patterns):
- Development environment setup (venv, install)
- Testing commands (test, test-watch)
- Code quality (format, lint, type-check)
- Agent-related helpers (read-agents, sync-check)
- Build/packaging commands

**Technical Decisions**:
- Start with single file approach (justfile-base.just)
- Can split by concern in later phases if needed
- Include bash helper functions that are generally useful
- Preserve comments documenting recipe purpose

**Actions**:
1. Read all justfile sources to identify common recipes
2. Extract shared recipes to `agent-core/fragments/justfile-base.just`
3. Document recipe purpose and parameters in comments
4. Ensure recipes use variables for project-specific paths (e.g., `SRC_DIR`, `TEST_DIR`)
5. Test that extracted recipes are syntactically valid

**Validation**:
- [ ] Recipes compile with `just --check`
- [ ] All extracted recipes have documentation comments
- [ ] Project-specific hardcoded paths replaced with variables

---

### Step 3: Extract Python Tool Configurations

**Objective**: Extract shared ruff and mypy configurations.

**Source Files**:
- claudeutils/pyproject.toml
- Other scratch repo pyproject.toml files

**Configuration Sections**:
- `[tool.ruff]` and subsections (lint, format, lint.per-file-ignores)
- `[tool.mypy]`

**Technical Decisions**:
- Extract as standalone TOML files, not fragments with markers
- Include only truly shared settings
- Document extension points for local customization
- Note Python version handling as potential variable (design.md:342-346)

**Algorithm for "Common" Settings:**

1. Parse [tool.ruff] from all available pyproject.toml files
2. For each setting key:
   - If present in ALL files with IDENTICAL value → Include in shared fragment
   - If present in some files or values differ → Exclude, document in comment
3. For list settings (e.g., select, ignore):
   - Include only items present in ALL projects
   - Document: "# Local projects may add: E501, F401, etc."
4. Create ruff.toml with intersection of settings
5. Add header comment: "# Shared ruff configuration - extend locally as needed"

Repeat same algorithm for mypy.toml.

**Actions**:
1. Read pyproject.toml from multiple projects
2. Identify common ruff settings using algorithm above:
   - Target version
   - Line length
   - Common lint rules (enabled/disabled)
   - Format settings
3. Create `agent-core/fragments/ruff.toml` with shared settings
4. Identify common mypy settings using algorithm above:
   - Python version
   - Strictness flags
   - Plugin configuration
5. Create `agent-core/fragments/mypy.toml`
6. Document in comments: "Local projects can extend with project-specific rules"

**Open Decision Points**:
- **Python version**: Should fragments specify minimum version or use template variable?
  - Recommendation: Use `py312` as baseline, document override mechanism
- **Per-file ignores**: These are project-specific, exclude from shared fragment

**Validation**:
- [ ] TOML files parse correctly
- [ ] Settings represent intersection of current projects
- [ ] Extension mechanism documented

---

### Step 4: Extract Rule Fragments

**Objective**: Extract shared agent behavior rules as markdown fragments.

**Fragments to Create** (design.md:273-283):

#### 4a. communication.md
**Content from**: AGENTS.md:10-16 (Communication Rules)
- Stop on unexpected results
- Wait for explicit instruction
- Be explicit (ask clarifying questions)
- Stop at boundaries

**Technical Note**: This is a direct extraction, verbatim.

#### 4b. delegation.md
**Content from**: AGENTS.md:19-52 (Delegation Principle, Model Selection, Quiet Execution)
- Delegation principle (orchestrator coordinates, doesn't implement)
- Model selection rules (Haiku/Sonnet/Opus)
- Quiet execution pattern (write to files, not context)

**Technical Note**: Includes examples from current AGENTS.md

#### 4c. tool-preferences.md
**Content from**: AGENTS.md:56-68 (Task Agent Tool Usage)
- Use specialized tools instead of Bash
- Specific mapping: LS, Grep, Glob, Read, Write, Edit
- Critical reminder about including in task prompts

**Source Note**: Also informed by Claude Code system prompt fragment (design.md:493)

#### 4d. hashtags.md
**Content**: Restored from old rules (design.md:285-289)
- `#stop` — Stop on unexpected results
- `#delegate` — Delegate to specialized agents
- `#tools` — Use specialized tools over Bash
- `#quiet` — Report to files, minimal context return

**Note**: Select hashtags that add value; avoid over-engineering with too many

**Actions**:
1. Create each fragment in `agent-core/fragments/`
2. Use markdown headers for section organization
3. Include concrete examples where helpful
4. Keep language concise and directive (agent instructions)
5. Add brief header comment explaining fragment purpose

**Validation**:
- [ ] Each fragment is self-contained and readable
- [ ] Examples included where they clarify behavior
- [ ] Language is directive ("Do X", not "Consider doing X")

---

### Step 5: Create AGENTS-framework.md Fragment

**Objective**: Extract the structural/framework parts of AGENTS.md that are consistent across projects.

**Content to Include**:
- Header explaining purpose of AGENTS.md
- Roles table (design.md:93-101)
- Rules table (design.md:105-107)
- Skills table (design.md:112-114)
- Loading mechanism explanation

**Technical Note**: This provides the "scaffold" that fragments will be composed into.

**Content Boundary:**

Include in AGENTS-framework.md:
- File header explaining AGENTS.md purpose (current AGENTS.md:1-7)
- Section structure (## Communication Rules, ## Delegation Principle, etc. headers only)
- Roles/Rules/Skills tables (AGENTS.md:91-114)
- Loading mechanism (AGENTS.md:116-120)

Exclude from AGENTS-framework.md:
- Specific communication rules (goes in communication.md)
- Delegation content (goes in delegation.md)
- Tool preferences content (goes in tool-preferences.md)
- Hashtag definitions (goes in hashtags.md)

Result: Framework provides structure and tables; fragments provide rule content.

**Actions**:
1. Create `agent-core/fragments/AGENTS-framework.md`
2. Extract structural content from existing AGENTS.md (headers, tables)
3. Structure as complete markdown document (no composition markers needed)
4. Will be concatenated with other fragments in Step 6

**Validation**:
- [ ] Framework is project-agnostic
- [ ] Framework contains structure/tables but not rule content
- [ ] Tables match current AGENTS.md format

---

### Step 6: Implement Template-Based AGENTS.md Generation

**Objective**: Create simple composition script to generate AGENTS.md from fragments.

**Approach**: Start with bash script (simple concatenation), can evolve to Python if needed.

**Technical Decisions**:
- Script location: `agent-core/scripts/compose-agents.sh` or in consuming project?
  - **Recommendation**: Consumer project controls composition (`agents/compose.sh`)
  - Rationale: Local template defines order and customization
- Template format: Simple marker-based or full template?
  - **Recommendation**: Simple bash concatenation for Phase 1
  - Example from design.md:162-169

**compose.yaml Structure** (design.md:122-148):
```yaml
sources:
  core: &core agent-core/fragments

fragments:
  - *core/AGENTS-framework.md
  - *core/communication.md
  - *core/delegation.md
  - *core/tool-preferences.md
  - *core/hashtags.md

output: AGENTS.md
```

**Generation Script** (simple version):
```bash
#!/bin/bash
# agents/compose.sh
# Generates AGENTS.md from fragments defined in compose.yaml

FRAGMENTS=(
  "agent-core/fragments/AGENTS-framework.md"
  "agent-core/fragments/communication.md"
  "agent-core/fragments/delegation.md"
  "agent-core/fragments/tool-preferences.md"
  "agent-core/fragments/hashtags.md"
)

OUTPUT="AGENTS.md"

# Clear output
> "$OUTPUT"

# Concatenate fragments
for fragment in "${FRAGMENTS[@]}"; do
  if [ -f "$fragment" ]; then
    cat "$fragment" >> "$OUTPUT"
    echo "" >> "$OUTPUT"  # Blank line between fragments
  else
    echo "ERROR: Fragment not found: $fragment" >&2
    exit 1
  fi
done

echo "Generated $OUTPUT from ${#FRAGMENTS[@]} fragments"
```

**Actions**:
1. Create `agents/compose.yaml` in claudeutils
2. Create `agents/compose.sh` generation script
3. Make script executable
4. Add to justfile: `generate-agents: agents/compose.sh`
5. Run generation and compare with existing AGENTS.md
6. Document usage in agents/README.md (if it doesn't exist, create it)

**Validation**:
- [ ] Script runs without errors
- [ ] Generated AGENTS.md is valid markdown
- [ ] Content matches expected composition
- [ ] Generation is repeatable (same input → same output)

**Open Decision Points**:
- **YAML parsing in bash**: Phase 1 uses hardcoded array; future can parse YAML
- **Fragment order**: Does order matter? (Yes, framework should come first)

---

### Step 7: Add agent-core as Submodule to Test Repository

**Objective**: Test the submodule integration in a scratch repository.

**Test Repository Options**:
- scratch/emojipack (simpler codebase)
- scratch/pytest-md (more representative)

**Recommendation**: Start with emojipack for simpler validation.

**Technical Details**:
- Submodule location: project root (`emojipack/agent-core/`)
- Submodule URL: Local path works for testing (`/Users/david/code/agent-core`)

**Actions**:
1. Navigate to test repository (e.g., `scratch/emojipack`)
2. Add submodule: `git submodule add /Users/david/code/agent-core agent-core`
3. Create `agents/` directory if it doesn't exist
4. Copy composition script and compose.yaml from claudeutils
5. Update paths in compose.yaml to reference `agent-core/fragments/`
6. Run generation: `agents/compose.sh`
7. Review generated AGENTS.md
8. Commit: "Add agent-core submodule and generate AGENTS.md"

**Validation**:
- [ ] Submodule added successfully
- [ ] `.gitmodules` file created
- [ ] Generation script works with submodule paths
- [ ] Generated AGENTS.md is usable

---

### Step 8: Test justfile Import in Test Repository

**Objective**: Verify justfile import mechanism works with submodule.

**Technical Details**:
- justfile native import: `import 'path/to/file.just'`
- Import path: `agent-core/fragments/justfile-base.just`

**Actions**:
1. In test repository justfile, add at top: `import 'agent-core/fragments/justfile-base.just'`
2. Add project-specific recipes after import
3. Run `just --list` to verify imported recipes visible
4. Test one imported recipe (e.g., `just format` if format recipe exists)
5. Verify project-specific recipes still work

**Validation**:
- [ ] Import syntax accepted by just
- [ ] Imported recipes visible in `just --list`
- [ ] Imported recipes execute correctly
- [ ] Local recipes can override imported ones (if tested)

**Error Cases to Handle**:
- Import path incorrect
- Circular import (shouldn't occur in Phase 1)
- Variable conflicts between imported and local

---

### Step 9: Test pyproject.toml Section Usage

**Objective**: Verify that extracted config fragments work when included in project pyproject.toml.

**Approach**: Manual copy for Phase 1 (automated composition is future work).

**Actions**:
1. Read `agent-core/fragments/ruff.toml`
2. In test repo `pyproject.toml`, update `[tool.ruff]` section
3. Add comment: `# Base configuration from agent-core/fragments/ruff.toml`
4. Test: `ruff check .` to verify config loads
5. Repeat for mypy configuration
6. Test: `mypy .` to verify config loads

**Validation**:
- [ ] Ruff configuration loads without errors
- [ ] Mypy configuration loads without errors
- [ ] Local extensions work (e.g., adding project-specific ignore rules)

**Note**: Full composition automation deferred to Phase 3 or prompt-composer integration.

---

### Step 10: Document Phase 1 Deliverables

**Objective**: Create clear documentation for what was built and how to use it.

**Documentation Files**:

#### agent-core/README.md
- Purpose of repository
- Directory structure explanation
- Fragment descriptions
- Usage instructions (how consuming projects integrate)
- Contribution guidelines (for backporting improvements)

#### agents/README.md (in consumer projects)
- How to compose AGENTS.md
- How to update from upstream (submodule pull)
- Local customization guidelines
- Regeneration workflow

**Actions**:
1. Write comprehensive README for agent-core
2. Write usage README for agents/ directory
3. Document compose.yaml format
4. Add examples of common customizations

**Validation**:
- [ ] README explains purpose clearly
- [ ] New user could follow instructions
- [ ] Common questions anticipated and answered

---

## Technical Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **agent-core location** | `/Users/david/code/agent-core` | Sibling to consuming projects |
| **Initial remote** | Local only (GitHub later) | Faster iteration, can push when stable |
| **Test repository** | scratch/emojipack | Simpler for initial validation |
| **Generation script** | Bash with hardcoded fragments | Simplest implementation, YAML parsing deferred |
| **Script location** | Consumer project (`agents/compose.sh`) | Local control over composition |
| **Fragment granularity** | Single justfile-base.just | Can split later if needed |
| **Python version in configs** | py312 baseline | Document override mechanism |
| **pyproject composition** | Manual copy for Phase 1 | Automation deferred to later phases |
| **Hashtag principles** | Include 4 core tags | #stop, #delegate, #tools, #quiet |
| **Submodule URL** | Local path for testing | `/Users/david/code/agent-core` |

---

## Open Questions for Review

1. **Fragment granularity**: Is single justfile-base.just sufficient, or should we split by concern immediately?
   - Recommendation: Start single file, split in Phase 3 if needed

2. **Python version handling**: Template variable or hardcoded baseline?
   - Recommendation: Hardcode py312, document override in comments

3. **compose.yaml parsing**: Bash hardcoding or lightweight YAML parser?
   - Recommendation: Hardcode for Phase 1, parser when needed

4. **AGENTS-framework.md composition points**: Comment markers or simpler full-fragment approach?
   - Recommendation: Start without markers (simple concatenation), add if customization points emerge

5. **justfile variable naming**: What variables should be parameterized for project-specific paths?
   - Recommendation: Identify during extraction (Step 2), likely `SRC_DIR`, `TEST_DIR`, `VENV`

---

## Success Criteria

Phase 1 is complete when:

- [ ] agent-core repository exists with documented structure
- [ ] Shared fragments extracted (justfile, ruff, mypy, rule fragments)
- [ ] Template-based AGENTS.md generation works
- [ ] One test repository (emojipack or pytest-md) successfully:
  - [ ] Has agent-core as submodule
  - [ ] Generates AGENTS.md from fragments
  - [ ] Imports justfile recipes
  - [ ] Uses extracted tool configs
- [ ] Documentation explains usage and customization
- [ ] All technical decisions documented

---

## Dependencies for Execution

**Required by haiku executor**:
- Access to file system for reading/writing
- Git operations (init, submodule add, commit)
- Bash execution for testing scripts
- just command for validating justfile syntax
- ruff and mypy for validating config

**Context files for reference**:
- plans/unification/design.md (this document provides full context)
- Current AGENTS.md (claudeutils/AGENTS.md)
- Current justfile (claudeutils/justfile)
- Current pyproject.toml (claudeutils/pyproject.toml)

---

## File Outputs

This plan will result in:

**New repository**: `/Users/david/code/agent-core/`
- fragments/justfile-base.just
- fragments/ruff.toml
- fragments/mypy.toml
- fragments/communication.md
- fragments/delegation.md
- fragments/tool-preferences.md
- fragments/hashtags.md
- fragments/AGENTS-framework.md
- README.md

**Modified in test repo** (e.g., scratch/emojipack):
- .gitmodules (new submodule)
- agent-core/ (submodule directory)
- agents/compose.yaml (new)
- agents/compose.sh (new)
- agents/README.md (new)
- AGENTS.md (regenerated)
- justfile (add import statement)

**Reports**:
- plans/unification/reports/phase1-execution.md (execution log from haiku)
- plans/unification/reports/phase1-test-results.md (validation results)

---

## Execution Notes for Haiku

**Use specialized tools**:
- Read/Write/Edit for file operations (not cat/echo)
- Glob for finding files (not find/ls)
- Grep for searching content (not grep command)

**Report structure**:
Write findings to `plans/unification/reports/phase1-execution.md` with:
- Step-by-step progress
- Technical decisions made during execution
- Any deviations from plan (with rationale)
- Validation results
- Issues encountered and resolutions

**Return format**:
- Success: `report: plans/unification/reports/phase1-execution.md`
- Failure: `error: <description>`

**Error Handling:**

If git operation fails:
- Report exact error message
- Do not retry automatically
- STOP if in Steps 1-6 (foundation required)
- Continue if in Steps 7-9 (test phase, can document failure)

If file operation fails:
- Verify parent directory exists
- Check file permissions
- Report specific missing prerequisite

If validation fails:
- Document specific failure in execution report
- Continue to next step (accumulate results)
- Mark step as incomplete in report

If critical step fails (Steps 1-6):
- STOP execution
- Report: "Critical failure in Step N: <description>"
- Do not proceed to test repository integration

**Critical**: Follow communication.md rules - stop on unexpected results and report.

---

## Review Checklist for Sonnet

When reviewing this plan:

- [ ] All Phase 1 steps from design.md:358-365 addressed
- [ ] Technical decisions are concrete and actionable
- [ ] No ambiguous instructions remain
- [ ] Validation criteria clear and measurable
- [ ] Dependencies identified
- [ ] Success criteria complete
- [ ] Plan is executable by haiku without further clarification
- [ ] Open questions have recommendations
- [ ] Report structure defined

---

## References

- plans/unification/design.md — Full design context
- AGENTS.md — Current agent instruction format (line references throughout)
- claudeutils/justfile — Source for recipe extraction
- claudeutils/pyproject.toml — Source for config extraction
