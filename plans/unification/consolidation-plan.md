# Out-of-Tree Agent Consolidation Plan

**Goal**: Bring out-of-tree changes from emojipack, tuick, and pytest-md into claudeutils scratch/ directory, consolidate generation tooling, and establish unified composition system.

**Status**: Planning complete, ready for execution
**Date**: 2026-01-15

---

## Context

Three projects have agent-related infrastructure that needs consolidation:
- **emojipack**: Shell-based composition (compose.sh/compose.yaml)
- **tuick**: Python-based composition (build.py + Makefile)
- **pytest-md**: Manual CLAUDE.md, 7 reusable skills

Per design document (plans/unification/design.md):
- Shared content goes in agent-core (git submodule)
- Generation tooling goes in claudeutils (Python module)
- Projects consume via dev dependency

---

## Architecture Decision

**Generation tooling location**: `claudeutils` as Python module (not shell scripts in agent-core)

**Rationale**:
- tuick's build.py has proven features (header manipulation, decorators)
- Python enables extensibility (YAML parsing, validation, templating)
- Fits claudeutils pattern: dev dependency with CLI entry points
- Client projects use: `claudeutils compose <config>`

---

## Phase 1: Copy Files to Scratch

Copy out-of-tree files into scratch/ for sandbox-safe work:

```
scratch/consolidation/
  emojipack/
    compose.sh                # /Users/david/code/emojipack/agents/
    compose.yaml              # /Users/david/code/emojipack/agents/

  tuick/
    build.py                  # /Users/david/code/tuick/agents/
    Makefile                  # /Users/david/code/tuick/agents/
    src/                      # ALL .md files from /Users/david/code/tuick/agents/src/
      *.md                    # 17 fragment files

  pytest-md/
    CLAUDE.md                 # /Users/david/code/pytest-md/CLAUDE.md
    skills/                   # /Users/david/code/pytest-md/.claude/skills/
      commit/SKILL.md
      execute-tdd/SKILL.md
      handoff/SKILL.md
      plan-design/SKILL.md
      plan-tdd/SKILL.md
      review-analysis/SKILL.md
      review-updates/SKILL.md

  configs/
    justfile-claudeutils     # /Users/david/code/claudeutils/justfile
    justfile-pytest-md        # /Users/david/code/pytest-md/justfile
    justfile-tuick            # /Users/david/code/tuick/justfile
    pyproject-claudeutils.toml  # /Users/david/code/claudeutils/pyproject.toml
    pyproject-pytest-md.toml    # /Users/david/code/pytest-md/pyproject.toml
    pyproject-tuick.toml        # /Users/david/code/tuick/pyproject.toml
```

**Total files**: ~35 files to copy

---

## Phase 2: Analyze with diff/patch

Create comparison reports in scratch/consolidation/analysis/:

### 2.1 Compare Compose Scripts

```bash
# Should be identical
diff -u scratch/consolidation/emojipack/compose.sh \
        agents/compose.sh \
        > scratch/consolidation/analysis/compose-sh-diff.patch
```

### 2.2 Compare Config Files

```bash
# Identify common justfile recipes
diff -u scratch/consolidation/configs/justfile-* \
        > scratch/consolidation/analysis/justfile-comparison.patch

# Identify common ruff/mypy settings (already analyzed by explore agent)
```

### 2.3 Analyze pytest-md CLAUDE.md Fragmentation

Create `scratch/consolidation/analysis/pytest-md-fragmentation.md`:
- Section 1 (Commands/Environment) → stays in pytest-md (project-specific)
- Section 2 (Persistent vs Temporary) → reusable fragment for agent-core
- Section 3 (Context Management) → handoff skill in agent-core
- Section 4 (Opus Orchestration) → reusable fragment for agent-core
- Section 5 (Testing Guidelines) → stays in pytest-md (project-specific)
- Section 6 (Documentation Organization) → reusable fragment for agent-core

---

## Phase 3: Design Unified Composition API

Create `scratch/consolidation/design/compose-api.md`:

### 3.1 Core Composition Module

Location: `src/claudeutils/compose.py`

**Features** (extracted from tuick/build.py):
- Fragment concatenation
- Header level manipulation (`increase_header_levels`)
- Decorator injection (title + separators)
- YAML config parsing (read compose.yaml)
- Multiple output modes:
  - `agents` mode: CLAUDE.md generation
  - `role` mode: Role file generation with headers
  - `skill` mode: (future) Skill template generation

### 3.2 CLI Entry Point

Location: `src/claudeutils/cli_compose.py`

```toml
# pyproject.toml
[project.scripts]
claudeutils = "claudeutils.cli:main"

# Subcommand: claudeutils compose
```

**Usage patterns**:
```bash
# Simple CLAUDE.md generation
claudeutils compose agents/compose.yaml

# Role generation (tuick pattern)
claudeutils compose role \
  --output agents/roles/commit-agent.md \
  --title "Commit Agent" \
  agents/src/role-definition-commit.md \
  agents/src/core.md \
  agents/src/git.md
```

### 3.3 YAML Schema

```yaml
# agents/compose.yaml
sources:
  core: agent-core/fragments

fragments:
  - core/AGENTS-framework.md
  - core/communication.md
  - core/delegation.md
  - src/project-specific.md

output: CLAUDE.md
```

---

## Phase 4: Integrate Content into agent-core

Update agent-core repository structure:

### 4.1 Skills Directory (NEW)

```
agent-core/skills/
  handoff/SKILL.md               # From pytest-md (context management)
  commit/SKILL.md                # From pytest-md (generic parts only)
  plan-design/SKILL.md           # From pytest-md (generic core)
  plan-tdd/SKILL.md              # From pytest-md (TDD cycle structure)
  review-analysis/SKILL.md       # From pytest-md (generic analysis)
```

**Project-specific skills stay local**:
- pytest-md/execute-tdd (pytest-specific)
- pytest-md/review-updates (project-specific file refs)

### 4.2 Configs Directory (NEW)

```
agent-core/configs/
  justfile-base.just             # Common recipes (help, dev, test, check, format, lint, release)
  ruff-base.toml                 # Common ruff ignores and settings
  mypy-base.toml                 # Strict mode + common overrides
  docformatter-base.toml         # Common docformatter settings
```

### 4.3 Fragments Directory (expand existing)

```
agent-core/fragments/
  # Existing (from Phase 1):
  AGENTS-framework.md
  communication.md
  delegation.md
  tool-batching.md
  roles-rules-skills.md
  hashtags.md

  # NEW from pytest-md CLAUDE.md:
  context-management.md          # Session.md protocol, handoff patterns
  documentation-organization.md  # File naming conventions, directory structure
  orchestration-patterns.md      # Opus orchestration, sub-agent usage, model selection

  # NEW from tuick:
  code-style.md                  # Python conventions, typing, 88-char limit
  planning-principles.md         # Data-first architecture, design patterns
```

---

## Phase 5: Build Composition Tooling in claudeutils

### 5.1 Implementation Files

**Create**:
- `src/claudeutils/compose.py` - Core composition engine (extract from tuick/build.py)
- `src/claudeutils/compose_config.py` - YAML config models
- `src/claudeutils/cli_compose.py` - CLI subcommand implementation

**Update**:
- `src/claudeutils/cli.py` - Add `compose` subcommand
- `pyproject.toml` - Ensure claudeutils CLI entry point exists

### 5.2 Core Features

Extract from tuick/build.py:
```python
def increase_header_levels(content: str) -> str:
    """Shift all markdown headers down one level."""
    return re.sub(r'^(#+) ', r'#\1 ', content, flags=re.MULTILINE)

def build_role(output_path: Path, title: str, *sources: Path) -> None:
    """Compose role from fragments with title and separators."""
    sections = []
    for source in sources:
        content = source.read_text()
        elevated = increase_header_levels(content)
        sections.append(elevated)

    result = f"# {title}\n\n" + "\n\n---\n\n".join(sections)
    output_path.write_text(result)
```

### 5.3 YAML Config Parsing

```python
# compose_config.py
from pathlib import Path
from pydantic import BaseModel

class ComposeConfig(BaseModel):
    sources: dict[str, str]  # YAML anchors resolved
    fragments: list[str]      # Fragment paths
    output: str               # Output file path
```

---

## Phase 6: Client Project Integration

### 6.1 emojipack Migration

**Current**: compose.sh + compose.yaml (shell-based)
**Target**: claudeutils compose (Python-based)

```toml
# Add to pyproject.toml
[dependency-groups]
dev = ["claudeutils>=0.1.0"]
```

```bash
# Update workflow
claudeutils compose agents/compose.yaml
```

### 6.2 tuick Migration

**Current**: build.py + Makefile (Python local)
**Target**: claudeutils compose + Makefile delegation

```makefile
# agents/Makefile
BUILD = claudeutils compose role

roles/high-level-planner.md: $(ROLEDEF_PLANNER_HIGH) $(CORE) $(PLANNING)
	$(BUILD) --output $@ --title "High-Level Planner" $^
```

### 6.3 pytest-md Migration

**Current**: Manual CLAUDE.md
**Target**: Generated from fragments + local project rules

1. Create `pytest-md/agents/` directory
2. Fragment CLAUDE.md:
   - Keep project-specific sections in `agents/src/pytest-md-rules.md`
   - Reference agent-core fragments for reusable content
3. Create `agents/compose.yaml`
4. Generate: `claudeutils compose agents/compose.yaml`

---

## Phase 7: Validation

### 7.1 Composition Validation

For each project:
```bash
# Generate CLAUDE.md
claudeutils compose agents/compose.yaml

# Verify output matches expected structure
diff CLAUDE.md.expected CLAUDE.md
```

### 7.2 Config Validation

For justfile includes:
```bash
# Verify justfile imports work
just --list

# Verify recipes execute
just check
```

### 7.3 Skills Validation

For pytest-md skills:
```bash
# Verify skill loading in Claude Code
# Skills should be accessible as /skill-name commands
```

---

## Critical Files

**Design Reference**:
- plans/unification/design.md - Architecture decisions (already read)

**Source Files for Extraction**:
- /Users/david/code/tuick/agents/build.py - Composition logic (73 lines)
- /Users/david/code/emojipack/agents/compose.yaml - YAML config pattern
- /Users/david/code/pytest-md/CLAUDE.md - Content to fragment (153 lines)
- /Users/david/code/pytest-md/.claude/skills/ - 7 skills to integrate

**Target Files for Updates**:
- agent-core/skills/ - NEW directory
- agent-core/configs/ - NEW directory
- agent-core/fragments/ - Expand with new fragments
- src/claudeutils/compose.py - NEW composition engine
- src/claudeutils/cli.py - Add compose subcommand

---

## Open Questions Resolved

1. **pytest-md skills**: Integrate reusable skills into agent-core/skills/ ✓
2. **Config files**: Centralize in agent-core/configs/ (justfile, ruff, mypy) ✓
3. **Naming**: Use `claudeutils compose` (subcommand) ✓
4. **Makefile support**: Provide example, defer full integration ✓
5. **YAML templating**: Defer to v2 ✓
6. **Validation**: Basic validation only (valid markdown, files exist) ✓
7. **pytest-md fragmentation**: Section-level split per analysis above ✓

---

## Success Criteria

- [ ] All files copied to scratch/consolidation/
- [ ] diff/patch analysis complete in scratch/consolidation/analysis/
- [ ] Composition API designed in scratch/consolidation/design/
- [ ] agent-core updated with skills/, configs/, new fragments
- [ ] claudeutils compose module implemented and working
- [ ] All three projects validated with unified tooling
- [ ] Generated CLAUDE.md matches expected output for each project

---

## Execution Notes

**Orchestration pattern** (per design doc):
- Use haiku agents for file copying and diff operations
- Use sonnet for composition API implementation
- Terse returns: `done: <summary>` or `blocked: <reason>`
- Reports to files, not orchestrator context
- Final validation by diff-based review

**Sandbox considerations**:
- Work happens in scratch/ within claudeutils (sandbox-safe)
- Out-of-tree reads are read-only (no modifications to sibling projects)
- Git operations only in claudeutils and agent-core repos
