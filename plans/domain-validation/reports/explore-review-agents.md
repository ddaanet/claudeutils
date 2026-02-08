# Exploration Report: Review/Validation Agent Ecosystem

**Date:** 2026-02-07
**Scope:** Comprehensive mapping of review agents, validation workflows, and domain-specific validation infrastructure

## Summary

The codebase implements a sophisticated review/validation agent ecosystem with specialized agents for different artifact types (code, design, runbooks, TDD processes), a rules-based context injection system for domain-specific guidance, and a clear vet workflow that delegates to appropriate agents. The architecture enables domain-specific validation through path-matched rules files that inject context based on file types being edited. The plugin-dev review agents are referenced as a first use case for domain-specific validation, but the plugin-dev submodule is not present in the current checkout.

---

## Key Findings

### 1. Review Agent Definitions (Core Ecosystem)

All core review agents live in `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/` with YAML frontmatter for discovery.

#### Design Review Agent
- **File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/design-vet-agent.md`
- **Model:** Opus (architectural analysis)
- **Color:** Purple
- **Tools:** Read, Edit, Write, Bash, Grep, Glob
- **Domain:** Design documents (`plans/*/design.md`)
- **Specialization:** Reviews for completeness, clarity, feasibility, consistency with existing patterns
- **Fix Behavior:** Applies ALL fixes (critical, major, minor) — document fixes are low-risk
- **Validation checks:**
  - Requirements traceability (every FR-* maps to design element)
  - Architectural feasibility
  - Out-of-scope items explicitly listed
  - Integration points clearly specified
  - Plugin topic detection (flags if design involves hooks/agents/skills but lacks skill-loading directive)
- **Output:** Detailed review to `plans/<job>/reports/design-review.md`
- **Assessment scale:** Ready / Needs Minor Changes / Needs Significant Changes

#### Implementation Vet Agent (Review-Only)
- **File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/vet-agent.md`
- **Model:** Sonnet
- **Color:** Cyan
- **Tools:** Read, Write, Bash, Grep, Glob, AskUserQuestion
- **Domain:** Code, runbooks, implementation changes (NOT design docs, NOT prescriptive design documents)
- **Specialization:** Quality assessment of work-in-progress changes
- **Fix Behavior:** Review-only — returns findings, does NOT apply fixes
- **Input requirement:** Must be given changed file list, NOT git diff text or runbook paths
- **Validation checks:**
  - Code quality (logic, edge cases, error handling, clarity)
  - Project standards (patterns, conventions, style)
  - Security (no hardcoded secrets, input validation)
  - Testing (behavior verification, edge cases, meaningful assertions)
  - Documentation and completeness
  - Requirements validation (if context provided)
- **Special handling for runbooks:** Checks for outline review at `plans/<job>/reports/runbook-outline-review.md` before runbook expansion
- **Output:** Detailed review to `tmp/vet-review-[timestamp].md` or `plans/[plan-name]/reports/vet-review.md`
- **Assessment scale:** Ready / Needs Minor Changes / Needs Significant Changes

#### Implementation Vet + Fix Agent
- **File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/vet-fix-agent.md`
- **Model:** Sonnet
- **Color:** Cyan
- **Tools:** Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion
- **Domain:** Code, tests, implementation changes (NOT runbooks, NOT design)
- **Specialization:** Reviews implementation AND applies all fixes directly
- **Fix Behavior:** Apply ALL fixes (critical, major, minor) with Edit tool
- **Input scope requirement:** Determines review scope via:
  1. Task prompt specification, OR
  2. AskUserQuestion with options: Uncommitted / Recent Commits / Current Branch / Specific Files / Everything
- **Scope validation:** Rejects runbooks and design documents with error messages
- **Validation checks:** Same as vet-agent, plus:
  - Design anchoring (if design reference provided, verify implementation matches)
  - Integration review (duplication, pattern consistency, cross-cutting concerns)
- **Fix constraints:** All fixes minimal and targeted, no scope creep, preserve intent
- **UNFIXABLE marking:** Issues requiring architectural changes or multiple valid approaches
- **Output:** Detailed review + fixes applied to `tmp/vet-review-[timestamp].md` or plan-specific path
- **Assessment scale:** Ready / Needs Minor Changes / Needs Significant Changes

#### TDD Plan Reviewer
- **File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/tdd-plan-reviewer.md`
- **Model:** Sonnet
- **Color:** Yellow
- **Tools:** Read, Grep, Glob, Write, Edit, Skill
- **Skills:** review-tdd-plan (preloaded)
- **Domain:** TDD runbooks and phase files (`runbook.md` with `type: tdd`, `runbook-phase-N.md`)
- **Specialization:** Validates TDD discipline (RED/GREEN violations, prescriptive code detection)
- **Fix Behavior:** Apply ALL fixes (critical, major, minor)
- **Validation checks:**
  - GREEN phases: Detect prescriptive code (should be behavioral hints, not exact implementations)
  - RED phases: Validate prose test quality (specific assertions, not vague descriptions)
  - Consolidation quality: Merged cycles maintain test isolation (≤5 assertions, no conflicts)
  - Prose quality: If executor could write different tests satisfying description, prose is too vague
  - Outline review: Checks for `plans/<plan-name>/reports/runbook-outline-review.md` (warns if missing for full runbooks, skips for phase files)
  - Requirements inheritance: Verifies runbook covers requirements from outline
- **Output:** Detailed review to `plans/<feature>/reports/runbook-review.md` or `phase-N-review.md`
- **Assessment scale:** Ready / Needs Escalation
- **UNFIXABLE escalation:** Missing requirements in design, fundamental cycle structure problems, scope conflicts

#### Outline Review Agent
- **File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/outline-review-agent.md`
- **Model:** Sonnet
- **Color:** Cyan
- **Tools:** Read, Write, Edit, Bash, Grep, Glob
- **Domain:** Design outlines after Phase A.5 (`outline.md`, pre-discussion draft)
- **Specialization:** Validates outline soundness before user presentation
- **Fix Behavior:** Apply ALL fixes (critical, major, minor)
- **Input validation:**
  - Must be `outline.md` (not `design.md`, not `runbook.md`)
  - Requires requirements.md OR inline requirements in task
- **Validation checks:**
  - Soundness (feasible approach, no contradictions, solutions match problems)
  - Completeness (all requirements covered)
  - Scope (boundaries clear, no scope creep)
  - Feasibility (no blockers, realistic dependencies)
  - Clarity (key decisions explicit, trade-offs documented)
  - Requirements traceability (every FR-* maps to outline section)
- **Output:** Detailed review with traceability matrix to `plans/<job>/reports/outline-review.md`
- **Assessment scale:** Ready / Needs Iteration / Needs Rework

#### Runbook Outline Review Agent
- **File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/runbook-outline-review-agent.md`
- **Model:** Sonnet
- **Color:** Cyan
- **Tools:** Read, Write, Edit, Bash, Grep, Glob
- **Domain:** Runbook outlines after plan-adhoc Point 0.75 or plan-tdd Phase 1.5 (`runbook-outline.md`, pre-expansion)
- **Specialization:** Validates phase structure, complexity distribution, design alignment
- **Fix Behavior:** Apply ALL fixes (critical, major, minor)
- **Input validation:**
  - Must be `runbook-outline.md` (not `outline.md`, not `runbook.md`)
  - Requires: design.md AND (design Requirements section OR requirements.md OR inline requirements)
- **Validation checks:**
  - Requirements coverage (every FR-* maps to steps/cycles with explicit references)
  - Design alignment (steps match design decisions, module structure, architecture)
  - Phase structure (balanced complexity, logical grouping, clean boundaries)
  - Complexity distribution (no phase >40% of total work)
  - Dependency sanity (no circular dependencies, prerequisites before dependents)
  - Step clarity (clear objectives, descriptive titles, bounded scope)
- **Expansion guidance:** Appends "## Expansion Guidance" section to outline with:
  - Consolidation candidates (trivial phases to merge)
  - Cycle expansion hints (test case suggestions)
  - Checkpoint guidance (validation steps for phase boundaries)
  - References for context
- **Output:**
  - Review to `plans/<job>/reports/runbook-outline-review.md`
  - Guidance appended to `plans/<job>/runbook-outline.md`
- **Assessment scale:** Ready / Needs Iteration / Needs Rework

### 2. Vet Workflow Architecture

The vet requirement is documented in `/Users/david/code/claudeutils-domain-validation-design/agent-core/fragments/vet-requirement.md`:

**Flow:**
1. Create production artifact (code, test, agent, skill, plan, design)
2. Delegate to appropriate vet agent:
   - `design-vet-agent` → Design documents (design.md)
   - `design-vet-agent` (via outline-review-agent) → Design outlines (outline.md)
   - `vet-fix-agent` → Code, tests, implementation
   - `tdd-plan-reviewer` → TDD runbooks (type: tdd)
   - `vet-agent` → Code reviews when caller has context to fix (Tier 1/2)
3. Read report, check for UNFIXABLE issues
4. Escalate UNFIXABLE items to user

**Key principle:** No importance filtering — agents apply ALL fixes (critical, major, minor). Early review catches issues before propagation.

**Artifacts requiring vet:**
- Plans (runbooks)
- Code (implementations, scripts)
- Tests
- Agent procedures
- Skill definitions
- Documentation that defines behavior/contracts

**Artifacts NOT requiring vet:**
- Execution reports
- Diagnostic outputs
- Log files
- Temporary analysis
- Session handoffs

### 3. Rules-Based Context Injection System

Domain-specific validation is implemented via path-matched rules files in `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/`:

#### Design Work Context
- **File:** `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/design-work.md`
- **Paths:** `plans/*/design.md`, `plans/*/runbook.md`
- **Injected guidance:**
  - Design decision escalation to `/opus-design-question` instead of user prompts
  - Criteria for when to ask user vs. escalate to Opus

#### Agent Development Context
- **File:** `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/agent-development.md`
- **Paths:** `.claude/agents/**/*`
- **Injected guidance:**
  - Before editing agents, load `/plugin-dev:agent-development` skill
  - Agent structure, frontmatter fields, system prompt patterns, tool configuration

#### Skill Development Context
- **File:** `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/skill-development.md`
- **Paths:** `.claude/skills/**/*`, `agent-core/skills/**/*`
- **Injected guidance:**
  - Before editing skills, load `/plugin-dev:skill-development` skill
  - Skill structure patterns, progressive disclosure, triggering conditions

#### Hook Development Context
- **File:** `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/hook-development.md`
- **Paths:** `.claude/hooks/**/*`, `.claude/hooks.json`
- **Injected guidance:**
  - Before editing hooks, load `/plugin-dev:hook-development` skill
  - Hook event types, validation patterns, Claude plugin root integration

#### Skill Development Context
- **File:** `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/skill-development.md`
- **Paths:** `.claude/skills/**/*`, `agent-core/skills/**/*`
- **Injected guidance:** `/plugin-dev:skill-development`

#### Command Development Context
- **File:** `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/command-development.md`
- **Paths:** `.claude/commands/**/*`, `.claude/commands.json`
- **Injected guidance:** `/plugin-dev:command-development`

#### Commit Work Context
- **File:** `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/commit-work.md`
- **Paths:** All (no path filter specified in header)
- **Injected guidance:** `@agent-core/fragments/commit-delegation.md` (detailed commit workflow, delegation protocols)

#### Planning Work Context
- **File:** `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/planning-work.md`
- **Paths:** All (no path filter specified)
- **Injected guidance:**
  - `@agent-core/fragments/error-classification.md`
  - `@agent-core/fragments/prerequisite-validation.md`

#### Other Domains
- **CLI work:** `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/cli-work.md`
- **Test work:** `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/test-work.md`
- **Workflow work:** `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/workflow-work.md`

**Rules frontmatter format:**
```yaml
---
paths:
  - "pattern1/**/*"
  - "pattern2/**/*.md"
---
```

**How it works:**
1. Claude Code matches file path against `paths` patterns
2. When a match occurs, injected rule content is prepended to agent context
3. Agent sees domain-specific guidance automatically
4. Rules can reference skills via `/plugin-dev:skill-name` or fragments via `@agent-core/fragments/file.md`

### 4. Plugin-Dev Review Agent References

The architecture anticipates domain-specific review agents for plugin development (skills, agents, hooks). These are referenced throughout but the plugin-dev submodule is not checked out in the current workspace.

**References found:**
- `design-vet-agent` checks for plugin topics in design documents and flags if plugin components present but no skill-loading directive
- `.claude/rules/agent-development.md` recommends loading `/plugin-dev:agent-development` before editing agents
- `.claude/rules/skill-development.md` recommends loading `/plugin-dev:skill-development` before editing skills
- `.claude/rules/hook-development.md` recommends loading `/plugin-dev:hook-development` before editing hooks
- `.claude/rules/command-development.md` recommends loading `/plugin-dev:command-development` before editing commands
- `agent-core/skills/design/SKILL.md` (Phase A.0) includes **skill dependency scan** that loads plugin-dev skills when requirements mention creating agents, skills, hooks, or plugins

**Expected plugin-dev skill discovery:**
- Plugin-dev is a separate repository/submodule
- Skills are invoked via `/plugin-dev:skill-name` syntax
- Skills cover: agent-development, skill-development, hook-development, command-development, (possibly) mcp-integration, plugin-structure

### 5. Agent Discovery Mechanism

**Discovery method:** Agents are discovered via YAML frontmatter in markdown files

**Frontmatter fields (required):**
```yaml
---
name: agent-name
description: |
  Multi-line description of agent purpose
model: sonnet|opus|haiku
color: cyan|purple|yellow|etc
tools: [Read, Write, Edit, Bash, Grep, Glob, ...]
skills: (optional array of preloaded skills)
---
```

**Agent location conventions:**
- Core agents: `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/*.md`
- Plan-specific agents: `/Users/david/code/claudeutils-domain-validation-design/.claude/agents/*-task.md` (auto-created by prepare-runbook.py)
- Plugin agents: `.claude/plugins/*/agents/*.md` (not present in current checkout)

**Naming conventions:**
- Review agents: `*-agent.md` (e.g., `vet-fix-agent.md`, `design-vet-agent.md`)
- Task agents: `*-task.md` (e.g., `statusline-parity-task.md`, plan-specific)
- Utility agents: `*-task.md` (e.g., `quiet-explore.md`, `remember-task.md`)
- Workflow agents: `*-task.md` or process-specific (e.g., `tdd-task.md`, `tdd-plan-reviewer.md`)

**Selection mechanism:**
- Matched by name in task prompt: "delegate to vet-fix-agent"
- Matched by `/plan-name` skill invocation: `/plan-adhoc` routes to appropriate task agent
- Matched by domain rules: `.claude/rules/*.md` path matching injects context for domain-specific guidance

### 6. Model-Based Agent Specialization

**Opus (design-vet-agent):**
- Architectural analysis (feasibility, completeness, consistency)
- Design document review (high-level reasoning)
- Suitable for architectural decisions requiring deep domain knowledge

**Sonnet (vet-agent, vet-fix-agent, tdd-plan-reviewer, outline/runbook reviewers):**
- Implementation review (code quality, standards, security)
- TDD discipline validation
- Runbook outline/phase structure review
- Good balance of capability for domain-specific validation

**Haiku (quiet-explore):**
- File search and exploration (specialized search, not general reasoning)
- Report writing from exploration results
- Efficient for targeted, well-scoped discovery tasks

### 7. Tool Access Patterns by Agent Type

**Code review agents (vet-agent, vet-fix-agent):**
- Read, Grep, Glob (analyze changes)
- Bash (git operations for gathering changes)
- Write (report output)
- Edit (fixes only for vet-fix-agent)
- AskUserQuestion (scope determination if needed)

**Design review agents (design-vet-agent, outline-review-agent, runbook-outline-review-agent):**
- Read (document analysis)
- Edit (apply fixes)
- Write (review report)
- Grep/Glob (verify references, file paths)
- Bash (git context if needed)

**Exploration agents (quiet-explore):**
- Read, Glob, Grep (find and analyze files)
- Bash (git history investigation)
- Write (structured report output)
- NO Edit (read-only)

**TDD review agent (tdd-plan-reviewer):**
- Read, Grep, Glob (analyze runbook content)
- Edit (apply fixes)
- Write (review report)
- Skill (invoke review-tdd-plan skill)
- Bash (git operations if needed)

---

## Patterns

### Review Agent Architecture
1. **Artifact-specific agents:** Each artifact type has a dedicated review agent (design, runbook, TDD, outline)
2. **Fix-all vs review-only:** vet-fix-agent applies all fixes; vet-agent reports only (when caller can fix)
3. **Structured output:** All agents write detailed reports to file with consistent structure (issues categorized by severity, status tracked)
4. **Escalation mechanism:** UNFIXABLE issues are clearly marked for caller escalation (not silently ignored)
5. **Assessment scales:** Each agent has clear assessment outcome: Ready / Needs Changes / Needs Significant Changes / Needs Escalation

### Domain-Specific Context Injection
1. **Path-matched rules:** `.claude/rules/*.md` files declare paths and inject context
2. **Skill-based guidance:** Domain guidance is delivered via skills (e.g., `/plugin-dev:agent-development`)
3. **Automatic discovery:** Rules are matched by file path automatically (no manual activation)
4. **Cascading fallbacks:** Design skill documentation checkpoint defines hierarchy (memory-index → skills → Context7 → explore → web)

### TDD Discipline
1. **Separate reviewer:** tdd-plan-reviewer validates TDD-specific concerns (RED/GREEN discipline, prescriptive code)
2. **Prose quality validation:** RED phases require specific assertions, not vague descriptions
3. **Consolidation guidance:** Trivial cycles should be merged or inlined, not left isolated
4. **Outline-before-expansion:** Runbook outlines are reviewed before full expansion (prevents wasted effort)

### Requirements Traceability
1. **Design level:** outline-review-agent validates every FR-* maps to outline section
2. **Runbook level:** runbook-outline-review-agent validates every FR-* maps to steps/cycles
3. **TDD level:** tdd-plan-reviewer validates outline requirements coverage
4. **Explicit mapping:** References (FR-1 → Section X) required, not assumed

### Quiet Execution Pattern
1. **Exploration results persisted:** quiet-explore writes to `plans/{name}/reports/explore-{topic}.md`
2. **No tmp/ for persistent output:** Exploration results live in plans/ for cross-session reuse
3. **Structured reports:** Findings include absolute paths, patterns, code snippets, gaps
4. **Return values:** Success = filepath; Failure = structured error message

---

## Gaps and Unresolved Questions

### Missing Plugin-Dev Submodule
- Plugin-dev agents, skills, and hooks are referenced throughout but the submodule is not present in current checkout
- Cannot inspect actual plugin-dev:agent-development, plugin-dev:skill-development, etc. skill definitions
- Cannot verify how plugin-dev review agents differ from core agents
- Design mentions checking for plugin topics but cannot verify actual plugin-specific validation rules

### Domain-Specific Validation Implementation
From `agents/session.md` Pending Tasks:
1. **How do agents discover which validations apply?**
   - Current: Path-matched rules files + skill references
   - Gap: No visible mechanism for discovering plugin-specific validation rules beyond skill loading
2. **Where do validation rules live?**
   - Design question lists fragments, dedicated directory, plugin-specific as options
   - Current implementation uses rules files + skills
   - No separate "validation rules" directory found
3. **How do projects opt into optional validations?**
   - Gap: No visible mechanism for opt-in validation (all validations appear mandatory if artifact type matches)
4. **Integration with vet/review workflows?**
   - Partially answered: design-vet-agent checks for plugin topics
   - Gap: No visible mechanism for plugin-specific validators in vet workflow
5. **Extensibility model for new domains?**
   - Design pattern evident: Create rules file with paths + skill reference
   - Gap: No documented procedure for adding new domain-specific validators

### Agent-Specific Gaps
1. **vet-agent vs vet-fix-agent distinction:** vet-agent documented as "Tier 1/2" agent but no clear definition of what makes Tier 1/2 vs full orchestration
2. **Outline review timing:** outline-review-agent triggers at Phase A.5 but runbook-outline-review-agent triggers at Point 0.75/Phase 1.5 — purpose of two separate outline agents unclear
3. **Rules auto-matching:** No visible documentation of how rules files are matched/injected (implied automatic but not explicit)

### Technical Documentation
1. **No plugin-dev skill reference guide:** Cannot verify what plugin-dev skills provide beyond tool/method names
2. **Quiet-explore report structure:** Report format documented in agent, but no examples of actual exploration reports in plans/
3. **Assessment outcome criteria:** Each agent has assessment scale but thresholds for transitions not always explicit

---

## Architecture Summary for Domain-Specific Validation Design

**Current strength:** Specialized agents for each artifact type (design, code, runbook, TDD) with clear separation of concerns and fix-all policy ensuring early issue detection.

**Current mechanism for domain-specific validation:**
1. **Rules-based context injection:** `.claude/rules/*.md` files declare path patterns and inject context (including skill references)
2. **Skill-based guidance:** Domain-specific details provided via skills (e.g., `/plugin-dev:agent-development`)
3. **Agent-level checks:** Some agents (design-vet-agent) detect plugin topics and flag if appropriate skills not loaded

**Extensibility pattern:**
1. Create `.claude/rules/domain-name.md` with:
   - Path patterns matching files in that domain
   - References to domain-specific skills
2. Create skills at `/plugin-dev:skill-name` with detailed validation guidance
3. Each agent consuming the domain rule automatically gets injected context

**For plugin-dev use case:** Review agents would likely:
1. Load `/plugin-dev:agent-development`, `/plugin-dev:skill-development`, `/plugin-dev:hook-development` per domain
2. Validate plugin-specific patterns (YAML structure, tool access, frontmatter fields)
3. Check for common plugin development anti-patterns
4. Verify integration with Claude Code plugin system (symlinks, discovery, configuration)

