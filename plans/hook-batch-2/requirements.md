**⚠ UNREVIEWED — Agent-drafted from session.md task descriptions. Validate before design.**

# Hook Batch 2

Three new hooks for tool-use governance and recall integration. Builds on existing hook infrastructure in `agent-core/hooks/`.

## Requirements

### Functional Requirements

**FR-1: Tool deviation hook (PostToolUse)**
Detect when an agent uses raw commands (`grep`, `find`, `cat`, `sed`, `ln`) instead of project tools (Grep, Glob, Read, Edit, `just` recipes). Fires after Bash tool use.
- Acceptance: `Bash(grep -r "pattern" .)` → PostToolUse emits warning naming the preferred tool (Grep)
- Note: Existing `pretooluse-recipe-redirect.py` handles PreToolUse recipe redirection; this is the PostToolUse complement for tool-level deviations

**FR-2: Block cd-chaining (PreToolUse)**
Prevent `cd <dir> && <command>` patterns in Bash tool invocations. Agents should use absolute paths or the `path` parameter instead.
- Acceptance: `Bash(cd src && python -m pytest)` → PreToolUse blocks with "use absolute path" message
- Edge case: `cd` in subshells or scripts (not top-level chaining) should be allowed

**FR-3: Lint recall integration (Pre+PostToolUse)**
Gate recall artifact freshness at tool boundaries. PreToolUse: verify recall artifact exists before plan-modifying writes. PostToolUse: flag if recall artifact is stale relative to newly written plan artifacts.
- Acceptance: Write to `plans/foo/design.md` without `plans/foo/recall-artifact.md` → PreToolUse blocks
- Note: Existing `pretooluse-recall-check.py` does path-based inference; this extends to Pre+Post coordination

### Constraints

**C-1: Hook execution budget**
Each hook must complete in <500ms. Hooks run on every tool invocation — latency compounds across a session.

### Out of Scope

- Modifying existing hooks (pretooluse-recipe-redirect, pretooluse-recall-check) — those are separate maintenance
- UserPromptSubmit hooks (covered by existing userpromptsubmit-shortcuts.py)

### Skill Dependencies (for /design)

- Load `plugin-dev:hook-development` before design (all 3 FRs are hooks)
