# Rules Unification Design

- **Status**: Design complete, ready for execution planning
- **Date**: 2025-01-14
- **Design Authority**: Opus (claude-opus-4-5-20251101)
- **Related**: plans/prompt-composer/design.md (generation, rules budgeting)
- **Test Cases**: scratch/ repositories (box-api, emojipack, pytest-md, home)

---

## Problem Statement

Multiple projects share common patterns for:
- justfile recipes and bash helpers
- pyproject.toml settings (ruff, mypy, docformatter)
- Agent behavior files (CLAUDE.md, roles, skills, rules)

Currently these are copy-pasted with drift. Goal: unified source with controlled local customization.

---

## Design Decisions

### 1. Repository Separation

**Decision**: Extract shared content to dedicated repo (`agent-core`), consumed as git submodule at project root.

```
agent-core/                    # Shared repo (git submodule at root)
  fragments/
    justfile-base.just         # Shared recipes, bash helpers
    ruff.toml                  # Shared ruff config
    mypy.toml                  # Shared mypy config
    communication.md           # Stop on unexpected, clarify requirements
    delegation.md              # Model selection, orchestrator patterns
    tool-preferences.md        # Prefer specialized tools over Bash
    hashtags.md                # #hashtag principle definitions
  agents/
    quiet-explore.md           # Explore with Write for reports
    quiet-task.md              # Task with quiet execution pattern
    summarize.md               # Structured summaries for orchestrator
  composer/                    # Generation scripts (future)
    compose.py
    ...

claudeutils/                   # Consumer project
  agent-core/                  # Git submodule (at root, not vendor/)
  agents/
    compose.yaml               # Local composition definition
    ...
  .claude/
    agents/                    # Claude agent definitions
      *.md
  pyproject.toml               # Generated/composed
  justfile                     # Imports from submodule
```

**Rationale**:
- Clean separation of shared vs project-specific
- Git submodule is painful manually, but agents handle it well
- Enables open-source distribution
- claudeutils becomes a consumer, not the canonical source

### 2. Directory Structure (Per-Project)

**Decision**: Option A with flat state files.

```
.claude/                       # Claude Code integration
  settings.json
  settings.local.json
  skills/                      # Claude skills
    skill-*.md
  agents/                      # Claude agent definitions
    quiet-explore.md
    quiet-task.md
    summarize.md
    ...

agents/                        # Agent system (committed)
  roles/                       # Role definitions
    role-*.md
  rules/                       # Action-triggered rules
    rules-*.md
  session.md                   # Session state (versioned)
  context.md                   # Active task context (versioned)
  todo.md                      # Shelved tasks (versioned)
  compose.yaml                 # Local composition definition
  sync-manifest.yaml           # Sync state tracking

plans/                         # Plans and reports
  <plan-name>/
    design.md                  # Plan document
    reports/                   # Exploration/execution reports (cross-session)
  ...

tmp/
  reports/                     # Ephemeral reports (no plan relevance)

agent-core/                    # Git submodule (at project root)

CLAUDE.md                      # Entry point (at project root, generated)
```

**State files versioned** (not gitignored):
- Enables rollback without archival workflow
- Provides context for controlled experiments
- Example: re-run session with tweaked rules or different model

**Report locations**:
- `plans/<name>/reports/` — tied to plan, cross-session value
- `tmp/reports/` — ephemeral, no long-term relevance
- Orchestrator specifies path explicitly

### 3. Composition Model

**Decision**: Local template references shared fragments. Generation happens locally.

**Not**: Shared repo generates → local copies → drift detection
**Instead**: Shared repo provides fragments → local template imports → local generation

```yaml
# agents/compose.yaml
sources:
  core: &core agent-core/fragments  # YAML anchor for path deduplication

fragments:
  - *core/communication.md
  - *core/delegation.md
  - *core/tool-preferences.md
  - *core/hashtags.md
  - local/project-rules.md

pyproject:
  ruff:
    import: agent-core/fragments/ruff.toml
    extend:
      lint.ignore: [PTH]       # Local addition
  mypy:
    import: agent-core/fragments/mypy.toml

justfile:
  import: agent-core/fragments/justfile-base.just
  # Local recipes in main justfile

agents:
  framework: agent-core/fragments/AGENTS-framework.md
  # Roles composed via template system
```

**Advantages**:
- Generation is local and fresh
- No "drift" - local template is source of truth
- Fragment updates propagate automatically
- Local customization is explicit

### 4. CLAUDE.md Generation

**Decision**: Template-based generation to handle project variation.

```bash
# Simple implementation (Phase 1)
cat agent-core/fragments/base.md \
    local/project-rules.md \
    agent-core/fragments/footer.md > CLAUDE.md

# Or with variables
cat agents/templates/CLAUDE.md.tmpl | envsubst > CLAUDE.md
```

**Template variables**: `$PROJECT_TYPE`, `$TEST_COMMAND`, `$BUILD_SYSTEM`

Skills and agents are hand-generated initially; template system handles CLAUDE.md divergence.

### 5. Sync Mechanism

**Decision**: Git history for sync state, no timestamps.

**Sync operations**:
- `sync-check`: Compare local files against generated-from-template
- `sync-update`: Pull latest submodule, regenerate
- `sync-diff`: Show differences for manual review

**No markers in generated files**:
- Markers are ugly, cause adoption resistance
- Line-based extraction is simpler
- Full-file comparison for agent files

**sync-manifest.yaml tracks**:
- Submodule commit reference
- Local override declarations (explicit acceptance of divergence)
- Use `git log -1 --format=%H -- <file>` for sync state (no timestamp field)

### 6. Backporting Workflow

**Decision**: Manual, per-file granularity.

Flow:
1. User improves local file
2. `sync-diff` shows local vs template
3. User manually edits fragment in shared repo (PR)
4. After merge: other projects get improvement via `sync-update`

**No automated backport** - human judgment on what belongs upstream. Appropriate for small number of projects with single author.

### 7. Agent Definitions

**Decision**: YAML frontmatter + markdown body.

```yaml
---
name: quiet-explore
description: Exploration with file output for quiet execution
tools:
  - Read
  - Glob
  - Grep
  - Bash: { read_only: true }
  - Write: { allow: ["plans/*/reports/*", "tmp/reports/*"] }
skills: tool-preferences  # Injected at startup
---

# QuietExplore Agent

File search specialist with report output capability.

## Output Rules

Write findings to specified report path. Return only:
- Success: `report: <path>`
- Failure: `error: <description>`

## Tool Preferences

Use specialized tools instead of Bash equivalents:
- Glob over find/ls
- Grep over grep/rg
- Read over cat/head/tail
```

**Skills injection**: Skills listed in frontmatter are injected into agent context at startup (no dynamic Skill tool access for sub-agents).

**Write tool constraints**:
- Orchestrator specifies output path explicitly in task prompt
- Write-only ensures no modification of existing files (new files only, or overwrite accepted for reports)
- Path restrictions prevent accidental writes outside designated areas

**Enforcement via hooks** (deterministic, unlike prompt instructions):
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write",
      "hooks": [{ "type": "command", "command": ".claude/hooks/write-only.sh" }]
    }]
  }
}
```

```bash
#!/bin/bash
# .claude/hooks/write-only.sh
FILE_PATH=$(jq -r '.tool_input.file_path' <<< "$1")
if [ -f "$FILE_PATH" ]; then
  echo "File already exists: $FILE_PATH" >&2
  exit 2  # Block operation
fi
exit 0
```

Exit code 2 blocks the operation; message shown to Claude as error feedback.

### 8. Shared Fragments

**Decision**: Extract common rules as composable fragments.

| Fragment | Content |
|----------|---------|
| `communication.md` | Stop on unexpected, wait for instruction, ask clarifying questions |
| `delegation.md` | Model selection (Haiku/Sonnet/Opus), orchestrator patterns |
| `tool-preferences.md` | Prefer Read/Glob/Grep/Edit/Write over Bash equivalents |
| `hashtags.md` | #hashtag principle definitions for emphasis |
| `quiet-execution.md` | Report to files, return success/failure only |

**#hashtag principles** (restored from old rules):
- `#stop` — Stop on unexpected results
- `#delegate` — Delegate to specialized agents
- `#tools` — Use specialized tools over Bash
- `#quiet` — Report to files, minimal context return

**Tool preferences rule** (critical for Bash-enabled agents):
- Included in main system prompt for interactive agents
- Repeats instructions from Bash tool description (insufficient alone for weak agents)
- Must be included in any agent with Bash access
- Source: system prompt fragment and Bash tool description in Claude Code

### 9. Agent Catalog

**Agents for agent-core**:

| Agent | Base | Modifications |
|-------|------|---------------|
| `quiet-explore` | Explore | Add Write (restricted paths), quiet output |
| `quiet-task` | Task | Quiet execution pattern, file-based reports |
| `summarize` | Custom | Structured output: 3-5 line summary, key items outline |

**Summarize agent output format**:
```
3-5 line summary of findings

Key items:
- item 1
- item 2
- ...
```

### 10. Integration with Prompt-Composer

**Decision**: Future feature. This design provides integration story; prompt-composer provides generation when implemented.

| Concern | Owner |
|---------|-------|
| Semantic sources, tiered rules, budgeting | prompt-composer (future) |
| Module extraction, variant generation | prompt-composer (future) |
| Fragment distribution, submodule management | this design |
| Local composition, sync workflow | this design |
| Claude skill/agent output | prompt-composer + Claude integration |

---

## Open Items

### Fragment Granularity

For justfile:
- One file (`justfile-base.just`) with all shared recipes?
- Split by concern (`justfile-dev.just`, `justfile-agent.just`)?

justfile native `import` works for whole files. Selective import requires file splitting.

### Python Version Handling

Projects have different Python version requirements (3.11, 3.12, 3.14). Fragments may need:
- Version-conditional sections
- Multiple fragment variants
- Template variables

### Claude Wrapper (Future)

Potential feature: wrapper for sysprompt optimization and tool selection. Example: optimized orchestration environment with disabled tools, simplified system prompt.

Not blocking current design - minimal impact on structure.

---

## Implementation Phases

### Phase 1: Foundation
1. Create `agent-core` repo
2. Extract justfile-base.just with shared recipes
3. Extract ruff.toml, mypy.toml fragments
4. Extract shared rule fragments (communication, delegation, tool-preferences, hashtags)
5. Template-based CLAUDE.md generation
6. Test in one scratch repo

### Phase 2: Agent Definitions
1. Create QuietExplore agent (Explore + restricted Write)
2. Create QuietTask agent (Task + quiet execution)
3. Create Summarize agent (structured output)
4. Define agent YAML frontmatter schema

### Phase 3: Sync Tooling
1. Basic sync-check (git history based)
2. sync-manifest.yaml structure
3. sync-update for submodule pull + regenerate

### Phase 4: Claude Integration
1. Place agent definitions in .claude/agents/
2. Map skills to Claude skill format
3. Validate orchestration workflow

---

## Compared Approaches

| Approach | Pros | Cons |
|----------|------|------|
| Copy-paste (current) | Simple, no tooling | Drift, manual sync |
| Markers in files | Precise section control | Ugly, adoption resistance |
| Full drift detection | Catches all changes | Complex, noisy |
| **Local template + fragments** | Clean, explicit customization | Requires composition step |

Selected: Local template + fragments.

---

## Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Repository model | Separate shared repo as git submodule | Clean separation, agent-friendly, open-sourceable |
| Shared repo name | `agent-core` | Concise, clear purpose |
| Submodule location | Project root (`agent-core/`) | Cleaner than vendor/ |
| Directory structure | agents/ flat with state files | Frequently accessed, stable names |
| .claude/ scope | Settings, skills, agent definitions | Native integration |
| State files | Versioned (not gitignored) | Rollback, reproducible experiments |
| Report locations | `plans/<name>/reports/`, `tmp/reports/` | Cross-session vs ephemeral |
| Composition model | Local template + shared fragments | No drift concept, explicit customization |
| CLAUDE.md | Template-based generation | Handle project variation |
| Agent definition format | YAML frontmatter + markdown | Simple, flexible |
| Sync mechanism | Git history, no timestamps | Leverage existing tooling |
| Backporting | Manual, per-file | Human judgment, appropriate for scale |
| Agent files | Full-file comparison | Defer granularity until prompt-composer exists |
| justfile | Native `import` from submodule | Built-in mechanism, clean |
| pyproject.toml | Line-based section extraction | Simplest, faster value |
| #hashtag principles | Restored | Emphasis for key behaviors |
| Skills in sub-agents | Injected at definition time | No dynamic Skill tool access |

---

## Rule Drift Analysis

Analysis of CLAUDE.md variants across projects (claudeutils, home, rules) identified:

**Preserved rules** (present in 2+ versions):
- Delegate to specialized agents
- Model cost matching (Haiku/Sonnet/Opus)
- Prefer specialized tools over Bash
- Orchestrator read-only mindset
- Write findings to disk
- Design before implementation

**Restored from old (rules/)**:
- #hashtag principle framework for emphasis
- Regular tool runs pattern (tests, format, check)
- Data-structure-first design principle
- Explicit whitespace/formatting standards

**Superseded/dropped**:
- Autonomous execution (#auto) — orchestration model handles this
- PLAN.md as live document — plans/ directory structure superior
- Loadable protocol documents — agent definitions superior for adherence
- Output verbosity rules — quiet execution pattern supersedes

**Conflicts resolved**:
- Edit tool vs Bash patch → Edit tool is standard
- Script vs tool calls → Tools for correctness, scripts for batch approval
- Wait vs autonomous → Model-dependent; orchestration handles delegation

---

## Handoff Notes

**For execution planning agent (Sonnet):**

1. Read this design document fully before planning
2. Implementation phases are ordered by dependency, execute sequentially
3. Each phase should produce testable artifacts
4. Test in scratch/emojipack or scratch/pytest-md before claudeutils

**Phase 1 deliverables:**
- `agent-core` repo created (can be local first, GitHub later)
- Shared fragments extracted: justfile-base.just, ruff.toml, mypy.toml
- Rule fragments: communication.md, delegation.md, tool-preferences.md, hashtags.md
- Template-based CLAUDE.md generation working in one test repo

**Phase 2 deliverables:**
- QuietExplore agent definition (.claude/agents/quiet-explore.md)
- QuietTask agent definition
- Summarize agent definition
- Write-only hook (.claude/hooks/write-only.sh)

**Technical notes:**
- compose.yaml uses YAML anchors for path deduplication
- sync-manifest.yaml uses git history, not timestamps
- Agent format: YAML frontmatter + markdown body
- QuietExplore: base Explore + Write restricted to `plans/*/reports/*`, `tmp/reports/*`
- Summarize output: 3-5 line summary first, key items outline

**Context from design session:**
- User prioritizes short-term value, will iterate toward long-term quality
- Markers rejected for ugliness and adoption resistance
- Git submodules acceptable because agents handle them well
- pyproject.toml variations across projects represent deliberate evolution, not drift
- #hashtag principles restored for at-a-glance behavior emphasis
- Sub-agents cannot invoke Skill tool; skills injected via frontmatter
- Write-only constraint enforced via PreToolUse hook (exit code 2 blocks)

**Source material locations:**
- Base Explore agent prompt: ../claude-code-system-prompts/system-prompts/
- Existing CLAUDE.md variants: claudeutils/, home/, rules/
- Tool preferences: system prompt fragment and Bash tool description in Claude Code

---

## References

- plans/prompt-composer/design.md - Generation pipeline, rule tiering (future)
- CLAUDE.md - Current agent instruction format
- scratch/ repos - Test cases (box-api, emojipack, pytest-md, home, dprint-testing, markdown-debug)
- ../claude-code-system-prompts/system-prompts/agent-prompt-explore.md - Base Explore agent
