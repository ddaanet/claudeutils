# Module System Design Consultation

- **Audience**: Sonnet agent executing this consultation
- **Output optimization**: Compact presentation. Include design decisions and rationale,
  avoid unnecessary details. Simple formatting, no ASCII art.

## Verified Research

### Rule Format

[arXiv 2025](https://arxiv.org/html/2503.06926): Bullet points outperform prose for LLM
tasks due to pretraining corpus characteristics. Connected ideas benefit from
paragraphs.

### Model Capabilities

[Anthropic](https://www.anthropic.com/news/claude-3-family): Haiku needs precise, scoped
tasks. Sonnet handles clear prompts well. Opus handles complex/detailed prompts.

### Position Bias

[Serial Position Effects (2024)](https://arxiv.org/html/2406.15981v1): LLMs exhibit
strong primacy bias (beginning matters most) and recency bias. Middle content has
weakest influence ("lost in the middle" phenomenon).
[Primacy exploitation research](https://arxiv.org/html/2507.13949) confirms this
pattern.

### Context Loading

[Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents):
LLMs only read explicitly provided context. No inherent behavior to load additional
files. Context files like llm-context.md require explicit reading instructions.

### Rule Count Limits

User research: LLM adherence collapses >200 rules. Claude system prompt: ~50 rules.
Leaves 150 for user rules.

### Token Cost

Opus input/output tokens expensive. Planning work must minimize token count. Plan
compactness critical.

## Current System

**Files:**

- 6 roles: planning.md, code.md, lint.md, refactor.md, execute.md, remember.md
- 2 skills: commit.md, handoff.md
- 1 master: AGENTS.md (project overview, communication patterns, tool batching)

**Terminology:**

- Role file (e.g., `planning.md`): Defines agent behavior mode
- Plan artifact (e.g., `PLAN.md`): Task instructions created by planning/refactor roles,
  executed by code/execute roles

**Current state**: All Opus-generated. Prose for strong models, itemized with ⚠️ for
weak models.

## Target Requirements

### Core Changes

- Self-contained role files (no plan/task-specific content)
- Reusable modules for cross-cutting concerns
- Rule tiering: 20/60/20 distribution (user claims research basis, validate if possible)
- Target-appropriate wording (concise for strong, explicit for weak)
- Budget tracking: LLM itemizes, script counts, ≤150 total rules
- Selective project context (planning needs full, code needs data model only,
  lint/execute minimal)
- Remove "BEFORE STARTING" sections (plans loaded by user for context caching)

### Module Sources

- Version-controlled natural language (current Opus-generated files as source)
- Track which model generated each module
- Different agent classes need different rule counts for same semantic module
- Commit.md currently haiku-optimized, rebuild as semantic source

### Project Context

- Generic "just" recipes: AGENTS.md, README.md
- Role-specific recipes: included in role files
- Split context: overview, data model, commands (selective inclusion)
- AGENTS.md: fallback for non-role-primed agents only (won't be loaded by role-primed
  agents per research)

### Checkpoint Factorization Opportunity

- Planning role: instructions to INSERT checkpoints in PLAN.md artifact
- Code role: instructions to OBEY checkpoints when executing
- Optimize plan compactness (reduce Opus output tokens) while maintaining weak agent
  adherence
- Common "checkpoint obedience" instructions could be factored across roles

### Generation Pipeline

1. Module sources (natural language, version controlled)
2. Role configuration (which modules, priorities, target model)
3. Script combines + validates rule count
4. Opus rewords for target agent class (if needed)
5. Makefile + sentinels track rebuilds by model ID

## Design Questions

### 1. Module Structure

Research shows bullets outperform prose, but connected ideas need paragraphs. How should
modules balance this?

- Pure itemized?
- Hybrid (items for rules, prose for concepts)?
- Different formats per module type?

### 2. Strong→Weak Adaptation

Weak agents need 3-5 itemized rules for what strong agents grasp from one paragraph. How
should modules transform?

- Manual (Opus rewrites each variant)?
- Template (`{strong:..., weak:...}` markers)?
- Generative (on-demand Opus generation)?
- Hybrid (shared core + weak augmentations)?

### 3. Module Priority

User claims 20/60/20 is research result (Tier 1: 20% critical, Tier 2: 60% important,
Tier 3: 20% guidance). Validate if possible. Should priority be:

- Fixed (module-level tag)?
- Contextual (role config assigns)?
- Rule-level (within modules)?

Consider: Checkpoint behavior is Tier 1 for code role, Tier 2 for planning role.

### 4. Skills Structure

Commit/handoff loaded on-demand (token cost not issue). Should they:

- Follow modular structure?
- Remain standalone?
- Have strong/weak variants?

Note: Commit.md currently haiku-optimized, could rebuild as semantic source.

### 5. Role Configuration Schema

Beyond modules/priorities/model class, what metadata needed?

- Rule budget per role?
- Section structure templates?
- Project context inclusions (overview/data model/commands)?
- Conditional modules (e.g., "plan adherence" only if role uses plans)?

### 6. Semantic Module Expansion

TDD cycle module example: Strong needs 3 prose paragraphs, weak needs 12 itemized steps
with ⚠️. How to handle?

- Encode both variants?
- Store minimal, generate expansions?
- Mark "expansion-sensitive" for Opus decision?

### 7. AGENTS.md Content

Purpose: Fallback for non-role-primed agents. Planning/generic agents load it. What
should it contain?

- Communication patterns (stop on unexpected, wait for instruction)?
- Tool batching (universal cross-cutting)?
- TDD overview (project-specific, role-agnostic)?

Note: Rule tiering explanation belongs in remember role, not AGENTS.md.

### 8. Implementation Recommendations

Provide:

1. Module taxonomy (semantic groupings)
2. Format standards (items vs prose)
3. Adaptation mechanism (strong→weak)
4. Configuration schema
5. Generation sequence (automated vs manual steps)
6. Validation checks

Goal: Fully/semi-automated regeneration from module sources. Both sources and generated
files version controlled.

## Output Requirements

Provide system architecture design:

1. Module taxonomy with semantic groupings
2. Format recommendations (cite research)
3. Adaptation strategy for agent classes
4. Configuration schema for roles
5. Generation pipeline stages
6. Example module structure (not actual rule wording)

Focus on system design decisions and rationale. Optimize for compactness while including
necessary information.

## Sources

- [Effect of Selection Format on LLM Performance](https://arxiv.org/html/2503.06926)
- [Claude Model Family](https://www.anthropic.com/news/claude-3-family)
- [Serial Position Effects of LLMs](https://arxiv.org/html/2406.15981v1)
- [Exploiting Primacy Effect](https://arxiv.org/html/2507.13949)
- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [ResearchGate: The 20-60-20 Rule](https://www.researchgate.net/publication/270824843_The_20-60-20_rule)
