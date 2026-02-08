# Exploration Report: Validation Patterns and Domain-Specific Context

**Date:** 2026-02-07

**Scope:** Analysis of current validation mechanisms, how domain context is delivered to agents, and extensibility patterns for domain-specific validation.

---

## Summary

The codebase implements a sophisticated layered validation architecture with multiple validation entry points (vet agents, review agents, hooks) and context delivery mechanisms (agent frontmatter, rules files, skills loading). Domain context is primarily delivered through three mechanisms: (1) agent-specific rules files with `paths:` matching patterns, (2) skills specified in agent frontmatter, and (3) embedded guidance in agent markdown bodies. The system is extensible through new agent definitions, rules files, and hooks without requiring monolithic validation centralization.

---

## Key Findings

### 1. Core Vet Pattern: Three-Agent Hierarchy

**File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/fragments/vet-requirement.md`

**Current Pattern:**

| Agent | Model | Purpose | Fix Capability |
|-------|-------|---------|-----------------|
| `vet-agent` | sonnet | Review-only (writes report, no fixes) | Report only |
| `vet-fix-agent` | sonnet | Review + autofix ALL issues | Fixes critical/major/minor |
| `design-vet-agent` | opus | Design document review + autofix | Fixes all issues + architectural analysis |

**Key insight:** Different agents handle different artifact types:
- Code/runbooks → `vet-agent` or `vet-fix-agent`
- Design documents → `design-vet-agent` (opus for architectural analysis)
- TDD runbooks → `tdd-plan-reviewer` (sonnet with specialized review-tdd-plan skill)

**Artifacts requiring vet:**
- Plans (runbooks)
- Code (implementations, scripts)
- Tests
- Agent procedures
- Skill definitions
- Documentation that defines behavior or contracts

**Artifacts NOT requiring vet:**
- Execution reports
- Diagnostic outputs
- Log files
- Temporary analysis
- Session handoffs

**File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/vet-agent.md` (lines 1-40)

---

### 2. Domain-Specific Context Delivery: Rules Files

**Discovery:** The system uses `.claude/rules/` directory with path-matching patterns to inject domain context automatically.

**File:** `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/skill-development.md`

**Pattern:**
```yaml
---
paths:
  - ".claude/skills/**/*"
  - "agent-core/skills/**/*"
---

# Skill Development Context

**Before editing skill files, load the skill development guide:**

```
/plugin-dev:skill-development
```

This provides skill structure patterns, frontmatter guidance, progressive disclosure techniques, and triggering condition best practices.
```

**How it works:**
1. Rules file specifies `paths:` patterns (glob-style)
2. When agent opens/edits files matching those paths, rule activates
3. Rule suggests loading a skill (e.g., `/plugin-dev:skill-development`)
4. Skill provides domain-specific knowledge (patterns, conventions, guardrails)

**Current rules files:**
- `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/skill-development.md` — Skills work
- `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/hook-development.md` — Hook development
- `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/agent-development.md` — Agent development
- `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/design-work.md` — Design documents
- `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/planning-work.md` — Runbook planning
- `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/test-work.md` — Test development
- `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/cli-work.md` — CLI development
- `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/workflow-work.md` — Workflow patterns
- `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/command-development.md` — Command development
- `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/commit-work.md` — Commit workflow patterns

**Key insight:** This is a distributed validation pattern — no centralized validator, but each domain gets its own rules file + skill.

---

### 3. Agent Context Injection via Frontmatter and Skills

**File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/tdd-plan-reviewer.md` (lines 1-20)

**Frontmatter pattern:**
```yaml
---
name: tdd-plan-reviewer
description: Reviews TDD runbooks/phase files for prescriptive code, RED/GREEN violations...
model: sonnet
color: yellow
tools: ["Read", "Grep", "Glob", "Write", "Edit", "Skill"]
skills:
  - review-tdd-plan
---
```

**How skill loading works:**
1. Agent frontmatter lists `skills: [review-tdd-plan]`
2. When agent loads, skill is pre-loaded and available
3. Agent markdown body can reference skill directly (e.g., "Load and follow the review-tdd-plan skill")
4. Skill provides specialized review criteria (e.g., GREEN phase anti-patterns, RED/GREEN sequencing violations)

**Example:** `tdd-plan-reviewer` has `skills: [review-tdd-plan]`

**File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/skills/review-tdd-plan/SKILL.md`

The skill defines:
- Review criteria (GREEN phase anti-pattern, RED/GREEN sequencing, prose quality)
- Check procedures (scan for code blocks, validate file references, analyze cycles)
- Fix protocols (fix-all policy, constraints)
- Report structure (issues found, fixes applied, unfixable escalation)

---

### 4. Validation via Hooks (Reactive, Not Agent-Based)

**File:** `/Users/david/code/claudeutils-domain-validation-design/.claude/settings.json` (lines 34-81)

**Hook system configuration:**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash $CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse-block-tmp.sh"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/submodule-safety.py"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/agent-core/hooks/userpromptsubmit-shortcuts.py"
          }
        ]
      }
    ]
  }
}
```

**Current hooks:**
- **pretooluse-block-tmp.sh** — Blocks Write/Edit to `/tmp/`
- **pretooluse-symlink-redirect.sh** — Redirects Write/Edit to `.claude/` symlinks
- **submodule-safety.py** — Enforces working directory safety (PreToolUse + PostToolUse)
- **userpromptsubmit-shortcuts.py** — Translates command shortcuts (s, x, h, wt, etc.)

**Hook characteristics:**
- Reactive (fire on tool use, not proactive)
- Can block operations (exit 2 to deny)
- Can inject context via `additionalContext` or `systemMessage`
- Run at project-level (not per-agent)
- Do NOT fire in sub-agents spawned via Task tool

**Key insight for validation:** Hooks are constraint enforcement (boundaries), not domain-specific validation. They prevent bad operations before they happen.

---

### 5. Skilled Review Agents for Domain-Specific Work

**File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/design-vet-agent.md`

**Pattern:** Agent + specialized skill combination

**Example: design-vet-agent**
- **Model:** opus (architectural analysis)
- **Scope:** Design documents only (rejects code, runbooks)
- **Review criteria:** Completeness, clarity, feasibility, consistency (lines 89-127)
- **Special checks:**
  - Requirements alignment (if present)
  - Plugin topics validation (hook/agent/skill/MCP detection with skill-loading directives)
  - Documentation perimeter validation
  - Traceability verification (FR-* to design elements)

**File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/tdd-plan-reviewer.md` (lines 63-99)

**Example: tdd-plan-reviewer**
- **Model:** sonnet (specialized document review)
- **Scope:** TDD runbooks only
- **Skill:** review-tdd-plan
- **Review criteria:** (from skill) GREEN phase prescriptive code, RED/GREEN sequencing, prose quality, metadata accuracy
- **Fix policy:** Fix ALL issues (critical, major, minor)
- **Escalation:** Mark UNFIXABLE issues requiring caller attention

---

### 6. Review Skill Pattern: Reusable Domain-Specific Guidance

**File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/skills/review-tdd-plan/SKILL.md`

**Skill structure:**
```
SKILL.md (frontmatter + metadata)
  ├─ Purpose statement
  ├─ Review criteria (9 sections of what to check)
  ├─ Review process (5 phases of analysis)
  ├─ Fix strategy (fix-all policy + constraints)
  ├─ Report structure (standard format)
  ├─ Output format (success/failure cases)
  ├─ Integration notes (how it fits in workflow)
  └─ Key principles (TDD discipline rules)
```

**Key insight:** Skills are not just hints — they're executable specifications that agents follow precisely. They include:
- Validation criteria with examples (good/bad patterns)
- Procedural steps (how to scan, analyze, apply fixes)
- Classification schemes (CRITICAL/MAJOR/MINOR issue levels)
- Escalation protocols (what can be fixed vs requires escalation)

**File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/skills/vet/SKILL.md`

**Review scope options:** The `/vet` skill provides user-selectable review scope:
1. "Uncommitted changes" — git diff (staged + unstaged)
2. "Recent commits" — last N commits
3. "Current branch" — all commits since branch point
4. "Specific files" — named files
5. "Everything" — all changes

---

### 7. Checkpoint Validation in Workflows

**File:** `/Users/david/code/claudeutils-domain-validation-design/agents/decisions/workflow-core.md` (lines 252-266)

**Pattern: Two-step checkpoints at phase boundaries**

```markdown
## Checkpoint Process for Runbooks

1. **Fix checkpoint:** `just dev` (lint, tests, build verification)
2. **Vet checkpoint:** Quality review (code review, architecture validation)
```

**Rationale:** Balances early detection with cost efficiency.

**Implementation:** In orchestrate skill, explicit phase boundary checks trigger vet-fix-agent review before proceeding to next phase.

---

### 8. Outline Review Pattern: Early-Stage Validation

**File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/runbook-outline-review-agent.md`

**Pattern:** Review outline BEFORE expansion to full runbook

**Benefit:** Early feedback prevents large-scale rewrites. Outline review happens after 4-point planning but before full phase expansion.

**Agent model:** sonnet (planning-level analysis)

**Key insight:** Validation at multiple granularities:
- Outline level (phase structure, requirements coverage, complexity assessment)
- Phase level (per-phase cycles, consolidation quality)
- Full runbook level (holistic view, integration checks)

---

### 9. Requirements Traceability Validation

**File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/design-vet-agent.md` (lines 143-169)

**Pattern:** Design documents include Requirements Traceability section

**Structure:**
```markdown
| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1        | ✓         | Section X        |
| FR-2        | ✗         | Missing          |
| NFR-1       | ✓         | Decision Z       |
```

**Validation check:**
- Every functional requirement (FR-*) must map to a design element
- Gaps flagged as critical issues
- Incomplete traceability flagged as major issue

**Key insight:** Traceability is embedded in design documents, not in separate matrices. Agents validate against design-embedded traceability.

---

### 10. Fragment System for Shared Validation Rules

**File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/fragments/` (20 files)

**Fragment structure:**
- Behavioral rules (communication.md, error-handling.md, delegation.md)
- Technical decisions (workflow-core.md, workflow-advanced.md, testing.md)
- Constraints (bash-strict-mode.md, tmp-directory.md, vet-requirement.md)

**How fragments enable domain validation:**
1. Fragments codify project-specific validation rules
2. Loaded via `@` references in CLAUDE.md (always in context)
3. Agents consult fragments for domain rules (e.g., vet-requirement.md defines what needs vetting)
4. New domains can create new fragments (e.g., plugin-dev-validation.md)

**Key insight:** Fragments are distribution mechanism for validation rules, not enforcement. Enforcement happens in agents/skills/hooks.

---

### 11. Multi-Layer Validation Architecture

**Validation happens at four layers:**

| Layer | Mechanism | Examples | Domain-Specific? |
|-------|-----------|----------|------------------|
| **Hooks** | PreToolUse/PostToolUse intercept | Block `/tmp/`, redirect symlinks, check cwd | Project-level only |
| **Skills** | Reusable domain-specific review specs | `/vet`, `/review-tdd-plan`, design review | Yes (per-skill) |
| **Rules** | Path-triggered knowledge injection | `.claude/rules/skill-development.md` | Yes (per-rule-file) |
| **Agents** | Domain-specific reviewers | `design-vet-agent`, `tdd-plan-reviewer` | Yes (per-agent) |

**How they compose:**
- Hook blocks bad operation → prevents validation need
- Rule injects context → agent loads skill → agent reviews artifact using skill criteria

---

### 12. Escalation Pattern: Unfixable Issues

**File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/skills/review-tdd-plan/SKILL.md` (lines 315-355)

**Pattern: Review agents classify issues into FIXABLE vs UNFIXABLE**

**Fixable issues:**
- Typos, formatting, unclear wording
- Missing sections (add placeholder)
- Incomplete rationale (add clarifying text)
- Structural improvements
- GREEN phase prescriptive code (replace with behavior)
- RED phase vague prose (strengthen with specific assertions)

**Unfixable issues:**
- Missing requirements in design (can't invent)
- Fundamental cycle structure (need outline revision)
- Scope conflicts with design decisions
- Sequencing violations requiring outline restructuring

**Return format for unfixable:**
```
plans/<feature>/reports/runbook-review.md
ESCALATION: 2 unfixable issues require attention (see report)
```

**Key insight:** Review agents write audit trail (documents ALL findings), fix what they can, and escalate UNFIXABLE to caller for decision.

---

### 13. Agent Context Isolation and Tool Access

**File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/vet-agent.md` (lines 6-7)

**Pattern: Tools specified in frontmatter, not implicit**

```yaml
tools: ["Read", "Write", "Bash", "Grep", "Glob", "AskUserQuestion"]
```

**Why this matters for validation:**
- Agent can only use listed tools (prevents accidental data corruption)
- Different agents get different tool sets based on role (design-vet-agent gets Edit, vet-agent does not)
- Skill tool access declared in skill YAML (read/write/edit/bash permissions)

**Example: tdd-plan-reviewer**
```yaml
tools: ["Read", "Grep", "Glob", "Write", "Edit", "Skill"]
```

Includes Edit (can fix issues) but no AskUserQuestion (no interactive prompts — fixed delegation).

---

### 14. Artifact Classification and Routing

**File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/design-vet-agent.md` (lines 49-77)

**Pattern: Agents validate document type before proceeding**

**Design-vet-agent validation:**
```
If given a runbook or implementation plan:
  Error: Wrong agent type
  Recommendation: Use vet-agent for runbook review, or tdd-plan-reviewer for TDD runbooks
```

**Vet-agent validation:**
```
If given a design document:
  Error: Wrong agent type
  Recommendation: Use design-vet-agent for design document review
```

**Key insight:** Artifact routing is agent responsibility, not orchestrator. Each agent knows its domain and rejects out-of-scope work.

---

### 15. Skill Loading and Progressive Disclosure

**File:** `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/tdd-plan-reviewer.md` (lines 64-75)

**Pattern: Skills loaded on-demand in agent body, not in all contexts**

Agent body references skill:
```markdown
Load and follow the review-tdd-plan skill (preloaded via skills field above). Key focus areas:

1. **GREEN phases:** Detect prescriptive implementation code...
2. **RED phases:** Validate prose test quality...
```

**Key insight:** Progressive disclosure — skill documentation is loaded only when agent executes, not in every context. Reduces initial context load for users not working with TDD.

---

## Patterns for Domain-Specific Validation

### Pattern 1: Domain = Rules File + Skill + Agent

**Template:**

```
Domain: Plugin Development Review

1. Rules file: `.claude/rules/plugin-dev-validation.md`
   paths:
     - ".claude/plugins/**/*"

   References skill: `/plugin-dev:plugin-validation`

2. Skill: `agent-core/skills/plugin-validation/SKILL.md`
   Contains: Review criteria, fix procedures, escalation rules

3. Agent: `agent-core/agents/plugin-vet-agent.md`
   Frontmatter:
     tools: [Read, Write, Edit, Grep, Glob]
     skills: [plugin-validation]

   Body: Review instructions, validation logic
```

**How it works:**
- Developer edits file in `.claude/plugins/`
- Rule file matches path pattern
- Rule suggests loading skill `/plugin-dev:plugin-validation`
- Developer loads skill
- Developer delegates to `plugin-vet-agent` or reviews using skill criteria directly
- Agent reviews artifact using skill criteria, fixes issues, escalates blockers

---

### Pattern 2: Layered Validation (Hooks → Rules → Agents)

**Example: Skill file creation workflow**

```
1. Developer creates `.claude/skills/my-skill/SKILL.md`

2. PreToolUse hook fires (Write tool)
   → Blocks `/tmp/` writes (sandbox enforcement)
   → Redirects `.claude/` symlinks (configuration management)

3. Rule file activates (matches `.claude/skills/**/*` path)
   → Suggests loading `/plugin-dev:skill-development`
   → Provides skill structure patterns, frontmatter guidance

4. Developer finishes skill creation

5. Developer or orchestrator delegates to `vet-agent`
   → Agent reviews using `/vet` skill
   → Can escalate to skill-specific review if needed
   → Writes report with issues and fixes

6. All issues addressed, commit workflow proceeds
```

---

### Pattern 3: Context Inheritance in Agent Hierarchy

**Example: design-vet-agent execution**

```
1. Orchestrator delegates: Task(subagent_type="design-vet-agent", ...)

2. Agent loads with frontmatter context:
   - model: opus (architectural analysis)
   - tools: [Read, Edit, Write, Bash, Grep, Glob]
   - No skills listed (inherits design knowledge from agent body)

3. Agent body (markdown) contains:
   - Protocol: 6-step validation workflow
   - Criteria: Completeness, clarity, feasibility, consistency checks
   - Special logic: Plugin topic detection, requirements traceability
   - Fix policy: Apply ALL fixes (critical, major, minor)

4. Agent executes:
   Step 0: Validate document type (design.md)
   Step 1: Read design document
   Step 2: Analyze design (4 dimensions)
   Step 3: Check documentation perimeter
   Step 4: Assess plugin topics
   Step 4.5: Validate requirements alignment
   Step 5: Write review report
   Step 6: Return result (filepath or error)
```

**Key:** Each agent encapsulates domain knowledge in its markdown body. No external lookup needed.

---

### Pattern 4: Fix-All vs Review-Only Distinction

**Current distinction:**

| Agent | Fix Scope | When to Use |
|-------|-----------|-------------|
| `vet-agent` | Review only (report + no fixes) | Tier 1/2: direct/lightweight delegation where caller has context to apply fixes |
| `vet-fix-agent` | ALL fixes (critical/major/minor) | Tier 3: orchestration where no agent has fix context |
| `design-vet-agent` | ALL fixes (critical/major/minor) | Design review where document fixes are low-risk |
| `tdd-plan-reviewer` | ALL fixes (critical/major/minor) | TDD runbook review (document fixes + escalation) |

**Key insight for new domains:** If validation is for planning artifacts (low-risk document changes), use fix-all. If for code (higher risk), consider review-only with caller applying fixes.

---

## Extensibility Model: How to Add Domain-Specific Validation

### Option 1: New Agent + Skill (Full Domain)

**Scenario:** Plugin development review validation

**Steps:**

1. **Create rules file:** `.claude/rules/plugin-dev-review.md`
   ```yaml
   ---
   paths:
     - ".claude/plugins/**/*"
     - "agent-core/plugins/**/*"
   ---

   # Plugin Development Context

   Before reviewing plugin files, load the plugin development guide:

   ```
   /plugin-dev:plugin-development
   ```
   ```

2. **Create skill:** `agent-core/skills/plugin-validation/SKILL.md`
   - Define: Check procedures for plugin structure
   - Define: Common anti-patterns (hardcoded paths, missing handlers, etc.)
   - Define: Fix procedures and escalation rules
   - Frontmatter: `user-invocable: false` (used by agents, not directly)

3. **Create agent:** `agent-core/agents/plugin-vet-agent.md`
   ```yaml
   ---
   name: plugin-vet-agent
   description: Reviews Claude Code plugins for structure, compliance, and integration
   model: sonnet
   tools: ["Read", "Edit", "Write", "Bash", "Grep", "Glob"]
   skills:
     - plugin-validation
   ---
   ```

4. **Agent body:** Protocol section + review logic (follow design-vet-agent pattern)

5. **Integration:** Orchestrate skill or user delegation can reference `plugin-vet-agent`

---

### Option 2: Hook-Based Validation (Constraints)

**Scenario:** Block invalid hook configurations

**Implementation:**

1. **Create hook script:** `.claude/hooks/plugin-validation.py`
   ```python
   # Check plugin.json syntax
   # Verify hook event types are valid
   # Validate configuration
   # exit 2 if invalid
   ```

2. **Register in settings.json:**
   ```json
   "PreToolUse": [
     {
       "matcher": "Write|Edit",
       "hooks": [{
         "type": "command",
         "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/plugin-validation.py"
       }]
     }
   ]
   ```

3. **Behavior:** Hook fires BEFORE Write/Edit, blocks invalid changes immediately

---

### Option 3: Fragment-Based Validation Rules

**Scenario:** Document validation rules for new domain

**Implementation:**

1. **Create fragment:** `agent-core/fragments/plugin-validation.md`
   - List validation rules specific to plugins
   - Define artifact types requiring validation
   - Document escalation procedures

2. **Reference in CLAUDE.md:**
   ```markdown
   When working with plugins, follow plugin validation rules:
   @agent-core/fragments/plugin-validation.md
   ```

3. **Benefit:** Rules available in every context without explicit invocation

**Limitation:** Fragments don't enforce — they educate. Enforcement needs agents or hooks.

---

### Option 4: Skill Enhancement (Existing Domain)

**Scenario:** TDD review needs new check for async/await patterns

**Implementation:**

1. **Update skill:** `agent-core/skills/review-tdd-plan/SKILL.md`
   - Add new check criteria: "Async/await test patterns"
   - Add examples of good/bad patterns
   - Add Grep patterns to detect violations

2. **Update agent:** `agent-core/agents/tdd-plan-reviewer.md`
   - Update review process to execute new check
   - Update report structure if new issue category

3. **Benefit:** Immediately available to all TDD plan reviews (agent loads skill in frontmatter)

---

## Integration Points with Session.md

**File:** `/Users/david/code/claudeutils-domain-validation-design/agents/session.md` (lines 7-27)

**Current design task context:**

```markdown
## Pending Tasks

- [ ] **Design support for domain-specific and optional project-specific validation**
      — Start with plugin-dev review agents | opus

## Design Questions

- How do agents discover which validations apply to current work?
- Where do validation rules live? (fragments, dedicated directory, plugin-specific?)
- How do projects opt into optional validations?
- Integration with existing vet/review workflows?
- Extensibility model for new domains?
```

**Answers based on exploration:**

1. **Agent discovery:** Rules files in `.claude/rules/` match paths and suggest skills; agents declare skills in frontmatter
2. **Validation rules live in:**
   - **Agent bodies (primary)** — Skills + embedded protocols
   - **Fragments (distribution)** — Shared constraints, behavioral rules
   - **Hooks (enforcement)** — Reactive constraints
   - **Skills (specification)** — Detailed review criteria, fix procedures
3. **Optional validations:** Create separate rule file with optional `enabled: false` (if system supports it), or separate skill/agent that's not in frontmatter
4. **Integration:** Rules files + agents integrate via skill loading in frontmatter; no separate plumbing needed
5. **Extensibility:** New domain = rules file + skill + agent; fits existing architecture without modification

---

## Gaps and Open Questions

### 1. Optional/Plugin-Specific Validation

**Current state:** All validation is binary (enabled or not). No mechanism for:
- Project A uses strict plugin validation, Project B skips it
- Optional validations that don't block execution

**Possible solutions:**
- Rule files support `enabled: false` flag (not observed in current system)
- Separate optional skills loaded conditionally
- Hook-based opt-in/opt-out via configuration
- Session.md flags for optional validations

### 2. Validation Rules Discovery

**Current state:** Agent knows what to validate based on markdown body + skill. No central discovery mechanism.

**Gap:** How does a new developer know which validations apply to their work?

**Current answer:** Rules files map paths to skills; rules files are loaded when paths match

**Limitation:** Rules files are files, not in-context. Developer must know to check `.claude/rules/` directory.

### 3. Cross-Domain Validation

**Current state:** Validation is domain-scoped (skills, agents are single-domain)

**Gap:** What if validation depends on interaction between domains? (e.g., plugin skill references agent-core skill — are references valid?)

**Observation:** This is not currently handled. Each agent validates its domain independently.

### 4. Validation Report Aggregation

**Current state:** Each vet agent writes its own report (design-review.md, runbook-review.md, etc.)

**Gap:** No aggregation of all validation issues across domains for holistic view

**Current pattern:** Orchestrator reads reports post-execution; no pre-execution aggregation

### 5. Validation Cost Tracking

**Current state:** No observation of which validations are expensive (Opus design-vet-agent vs Sonnet vet-fix-agent)

**Gap:** Can't optimize validation cost or defer non-critical validations based on model budget

**Current pattern:** Hard-coded model per agent; no cost awareness

---

## Recommendations for Domain Validation Design

### 1. Establish Domain Definition Protocol

Create a standard template for defining new domains:

```markdown
# Domain: [Name]

## Artifacts in Scope
- File patterns (glob)
- Artifact types (skill, hook, plugin, etc.)

## Validation Rules
- **Critical:** Must pass (block merge/commit)
- **Major:** Should pass (warning)
- **Minor:** Nice-to-have (informational)

## Validation Entry Points
- **Agent:** [agent-name] (model, tool access)
- **Skill:** [skill-name] (review procedures)
- **Hook:** [hook-name] (reactive enforcement)
- **Fragment:** [fragment-name] (rules/constraints)

## Escalation Protocol
- What's fixable vs requires caller decision
- Error messages and resolution paths

## Examples
- Good artifact (passes all checks)
- Bad artifact (multiple violations)
```

### 2. Create Discovery Mechanism

Make validation rules discoverable:

```
1. Add to memory-index.md under "Domain-Specific Validation":
   - Entry: "Plugin validation — `.claude/rules/plugin-dev-review.md`"
   - Guides to agent and skill

2. Update CLAUDE.md with validation section:
   ```
   ## Validation Domains

   [linked to rules files]
   ```

3. Add `/discover-validations` command to list applicable validations for current file
```

### 3. Support Optional Validations

Add capability for projects to opt into/out of validations:

```
Option A: Feature flags in settings.json
```json
"validations": {
  "plugin-dev": true,  // enabled by default
  "advanced-testing": false  // disabled by default
}
```

Option B: Separate validation agents for optional domains
- Load conditionally in workflow

Option C: Session.md toggles
- Capture project preferences in session.md
- Agents read and respect flags
```

### 4. Establish Validation Tiers

Align validation to work complexity:

```
Tier 1 (Direct execution):
  - Minimal validation (syntax, format)
  - No agent delegation

Tier 2 (Lightweight delegation):
  - Design-level validation (agent reviews artifact)
  - Single-model agent (sonnet)

Tier 3 (Full orchestration):
  - Multi-domain validation (design + code + integration)
  - Multiple agents, specialist models (opus for design)
```

---

## File Inventory: Validation-Related Artifacts

| File | Purpose | Extensible |
|------|---------|-----------|
| `agent-core/fragments/vet-requirement.md` | Defines vet pattern | No (foundational rule) |
| `agent-core/agents/vet-agent.md` | Review-only agent | Yes (template for new agents) |
| `agent-core/agents/vet-fix-agent.md` | Review + fix agent | Yes (template for new agents) |
| `agent-core/agents/design-vet-agent.md` | Design review (opus) | Yes (domain-specific pattern) |
| `agent-core/agents/tdd-plan-reviewer.md` | TDD runbook review | Yes (domain-specific pattern) |
| `agent-core/skills/vet/SKILL.md` | General review skill | Yes (can be extended) |
| `agent-core/skills/review-tdd-plan/SKILL.md` | TDD-specific review | Yes (template for new domains) |
| `.claude/rules/*.md` | Path-triggered knowledge injection | Yes (add new rule files) |
| `.claude/settings.json` | Hook configuration | Yes (add new hooks) |
| `agent-core/fragments/*.md` | Validation rules (shared) | Yes (add domain fragments) |

---

## Conclusion

The codebase implements a sophisticated, layered validation architecture with multiple entry points and extensibility mechanisms:

1. **Hooks** provide reactive enforcement (constraints)
2. **Rules files** provide path-triggered knowledge injection
3. **Skills** provide reusable domain-specific review specifications
4. **Agents** encapsulate domain logic (classification, escalation, fixing)
5. **Fragments** distribute shared validation rules

To add domain-specific validation for plugin development or other domains:

1. **Create a rules file** mapping path patterns to skills (discovery mechanism)
2. **Create a skill** with detailed review criteria, procedures, and escalation rules
3. **Create an agent** that implements the validation protocol (review + optional fix)
4. **Reference in CLAUDE.md or memory-index.md** for context visibility

The system is designed for gradual extension without centralized bottlenecks. New domains integrate naturally into the existing validation hierarchy.
