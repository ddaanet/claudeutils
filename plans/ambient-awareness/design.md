# Design: Ambient Awareness of Consolidated Learnings

## Problem

When learnings are consolidated from `agents/learnings.md` into permanent locations (fragments, decisions, skill references), they disappear from the agent's ambient context. The agent has no mechanism to discover that new rules exist or that existing rules were updated — unless the fragment happens to be `@`-referenced in CLAUDE.md.

**Current state:**
- 24 fragments in `agent-core/fragments/`, 17 `@`-referenced in CLAUDE.md, 7 orphaned
- `.claude/rules/` path-scoped rules exist (8 files) — contextual "go read the docs" triggers
- Remember skill consolidates learnings but doesn't update discovery mechanisms
- No index, notification, or awareness system for consolidated learnings

**Concrete failure modes:**
- Agent creates fragment `agent-core/fragments/foo.md` via `/remember` — nobody knows it exists
- Agent updates fragment `error-handling.md` with new pattern — other sessions use stale mental model
- Orphaned fragments contain valuable content that's never loaded

## Requirements

**Functional:**
- After consolidation, new/updated rules become discoverable without manual intervention
- Agents starting new sessions encounter condensed summaries of all consolidated knowledge
- Design and plan skills actively search for relevant prior knowledge before making decisions
- Progressive disclosure preserved — not everything loaded at once

**Non-functional:**
- No MCP servers, external databases, or hooks infrastructure beyond what exists
- Token-efficient — full fragments loaded on demand, not unconditionally
- Compatible with agent-core's multi-project deployment (agent-core is a git submodule)
- Simple enough for the remember skill to maintain as a final step

**Out of scope:**
- Confidence scoring / decay
- Semantic search / embeddings
- Automatic extraction from conversation (handled by `/remember`)
- CLAUDE.md regeneration

## Architecture

### Key Insight

The project already has two discovery mechanisms:
1. **`@`-imports in CLAUDE.md** — always loaded, unconditional
2. **`.claude/rules/` with path frontmatter** — conditionally loaded when touching matching files

The gap: **neither mechanism is updated when `/remember` consolidates a learning.** And there's no way to passively discover what knowledge exists across all fragments/decisions without reading every file.

### Three-Part Solution

#### Part 1: Memory Index (`agent-core/fragments/memory-index.md`)

A condensed catalog of all consolidated knowledge. `@`-imported in CLAUDE.md. Each entry is one line: a condensed summary + file reference. No rotation, no trimming — grows with the knowledge base but each entry is minimal.

```markdown
# Memory Index

Condensed knowledge catalog. Read referenced files when working in related areas.

## Behavioral Rules
- Heredocs broken in sandbox — use TMPPREFIX fix for zsh | `fragments/bash-strict-mode.md`
- Orchestrator stop rules get overridden — use absolute language, no exceptions | `fragments/delegation.md`
- Skills need multi-layer discovery, not just good docs | `fragments/delegation.md`
- Shell command continuation exploitable in hooks — use exact match | `fragments/claude-config-layout.md`

## Workflow Patterns
- All tiers must end with /handoff --commit | `fragments/execute-rule.md`
- Vet uses two agents: vet-agent (review) vs vet-fix-agent (review+fix) | `fragments/vet-requirement.md`
- Don't delegate when context already loaded | `fragments/delegation.md`

## Technical Decisions
- Sandbox bypass: permissions.allow + dangerouslyDisableSandbox | `fragments/sandbox-exemptions.md`
- Shortcut systems need two layers: hook + fragment | `fragments/execute-rule.md`
- Case-sensitive shortcuts unreliable for LLM — use distinct tokens | `fragments/execute-rule.md`

## Tool & Infrastructure
- Hook output: additionalContext (agent sees) + systemMessage (user sees) | `fragments/claude-config-layout.md`
- Hooks only active in main agent session, not sub-agents | `fragments/claude-config-layout.md`
- SessionStart hook broken for new sessions (#10373) | `fragments/claude-config-layout.md`
```

**Why memory index, not changelog:**
- A changelog surfaces *what's recent*. A memory index surfaces *what exists*. The user's feedback ("condensed memory — a few lines + reference per learning") points to wanting a persistent catalog, not a temporal window.
- No rotation/trimming needed — entries are permanent records of consolidated knowledge
- Each entry is ~80 chars + reference ≈ ~100 chars. At 50 entries: ~5000 chars ≈ 1250 tokens. At 100 entries: ~2500 tokens. Acceptable for always-loaded context given the discovery value.
- Grouping by domain (behavioral, workflow, technical, tool) aids scanning

**Maintenance:**
- **Remember skill**: After consolidating a learning, append one-line entry to appropriate section. The skill has the best context to write a quality summary.
- **Soft limit: 100 entries.** When approaching, review index for entries that have become obvious or redundant (agent has internalized the pattern). Prune entries where the rule is now well-established in always-loaded fragments. This mirrors the learnings.md soft-limit pattern.
- **Deduplication**: When updating an existing fragment with new content, check if an index entry already covers that topic. Update if the learning substantially changes the rule; skip if it's a minor refinement.

#### Part 2: Memory Discovery Step in Design & Plan Skills

Add an explicit step to `/design` and `/plan-adhoc` skills where the agent actively searches for relevant prior knowledge before making decisions.

**In `/design` skill — after Step 1 (Understand Request), before Step 2 (Explore Codebase):**

```
### 1.5. Memory Discovery

Scan memory-index.md for entries relevant to the current task domain.
For any matches:
1. Read the referenced file(s) to load full context
2. Note relevant constraints, patterns, or prior decisions
3. Factor these into architectural decisions

This prevents re-learning known patterns or contradicting established rules.
```

**In `/plan-adhoc` skill — in Point 0.5 (Discover Codebase Structure):**

```
Add to Point 0.5:
- Scan memory-index.md for entries related to the task domain
- Read referenced files for relevant matches
- Factor known constraints into step design and model selection
```

**Why explicit step:**
- Passive loading (always-imported index) gives awareness but relies on the agent *noticing* relevance — unreliable
- Active discovery step forces the agent to search before deciding, using the index as a lookup table
- Cost is minimal — the index is already loaded, scanning is fast, only matched files get read
- Creates auditable trail ("I checked memory index, found X, read Y")

#### Part 3: Remember Skill — Post-Consolidation Updates

Add to the remember skill's "Apply + Verify" phase (Section 4):

**Step 4a: Update discovery mechanisms**

After consolidating a learning:

1. **Append to memory index**: Add one-line entry (summary + file reference) to appropriate section in `agent-core/fragments/memory-index.md`
2. **If new fragment created**: Add `@`-reference to CLAUDE.md OR create `.claude/rules/` entry if path-scoped. **Heuristic:** If the learning applies regardless of which files are being edited → `@`-ref in CLAUDE.md. If it only applies when working with a specific file type or directory → `.claude/rules/` entry with path frontmatter.
3. **If existing fragment updated**: Ensure memory index entry reflects the updated content (add new entry or update existing one)
4. **If decision file updated**: Verify corresponding `.claude/rules/` entry exists for path trigger

#### Part 4: Orphan Audit + Cleanup

One-time action: resolve orphaned fragments.

| Fragment | Action | Rationale |
|----------|--------|-----------|
| `AGENTS-framework.md` | Delete | 9-line stub, content superseded by CLAUDE.md structure |
| `error-classification.md` | Add `.claude/rules/` entry scoped to `plans/**` | Error taxonomy primarily relevant during plan execution. 131 lines — too expensive for always-loaded. |
| `prerequisite-validation.md` | Add `.claude/rules/` entry scoped to `plans/**` | Only relevant during planning |
| `roles-rules-skills.md` | Delete | Taxonomy content now in skill-development skill |
| `tool-preferences.md` | Delete | Content already in delegation.md (Task Agent Tool Usage section) |
| `commit-delegation.md` | Add `.claude/rules/` entry scoped to `agent-core/skills/commit/**`, `agent-core/fragments/commit-*.md` | 290 lines of unique commit delegation workflow. NOT duplicated in delegation.md. |
| `hashtags.md` | Delete | Content redundant with communication.md, delegation.md. Semantic markers already covered. |

**Net result:** 4 deletions, 3 new `.claude/rules/` entries. Fragments dir goes from 24 to 20 files, all discoverable.

## Design Decisions

**Why memory index, not changelog?**
A changelog surfaces what's *recent* — entries rotate out. A memory index surfaces what *exists* — entries are permanent. The user specifically wanted "condensed memory" (persistent catalog) not "recent changes" (temporal window). An index also serves active discovery better — agents can search it by topic at any time, not just notice recent entries.

**Why flat one-line entries?**
Token economy. Each entry is summary + reference. The summary gives enough context to decide relevance; the reference points to full content. Loading full content for every learning would defeat progressive disclosure.

**Why group by domain?**
At scale (50+ entries), a flat list becomes hard to scan. Lightweight section headers (Behavioral Rules, Workflow Patterns, Technical Decisions, Tool & Infrastructure) aid both human and agent scanning without adding structural overhead. Sections are soft categories — don't agonize over classification.

**Why active discovery step in skills?**
Passive awareness (always-loaded index) is necessary but insufficient. Agents must be prompted to *search* for relevant prior knowledge before making decisions. The explicit step creates a checkpoint: "Did I check what we already know about this domain?" This mirrors how experienced engineers review prior art before designing.

**Why not `.claude/rules/` for everything?**
Path-scoped rules only trigger when Claude touches matching files. The memory index is cross-cutting — you need to know what knowledge exists regardless of what you're editing. The index stays in CLAUDE.md; path-scoped rules handle the orphaned fragments.

**Why not auto-generate the index?**
The remember skill has the best context at consolidation time to write a quality one-line summary. Auto-generation from fragment content would produce worse summaries and add maintenance complexity. Manual append is simple and reliable.

## Implementation Notes

**Files affected:**
- `agent-core/fragments/memory-index.md` — new file (seeded from existing learnings)
- `CLAUDE.md` — add `@agent-core/fragments/memory-index.md` import (after Documentation Structure, before Communication Rules)
- `agent-core/skills/remember/SKILL.md` — add post-consolidation discovery step (4a)
- `agent-core/skills/remember/references/consolidation-patterns.md` — add memory index update guidance AND `.claude/rules/` as a routing destination with path-scoping criteria
- `agent-core/skills/design/SKILL.md` — add memory discovery step (1.5)
- `agent-core/skills/plan-adhoc/SKILL.md` — add memory discovery to Point 0.5
- `.claude/rules/planning-work.md` — new rule file scoping prerequisite-validation + error-classification to `plans/**`
- `.claude/rules/commit-work.md` — new rule file scoping commit-delegation to `agent-core/skills/commit/**`, `agent-core/fragments/commit-*.md`
- 4 fragment files — delete (AGENTS-framework, roles-rules-skills, tool-preferences, hashtags)
- `agents/README.md` — update or delete (references deleted fragments)
- `agent-core/README.md` — update directory tree listing

**Seeding the index:**
Reconstruct initial entries from `agents/learnings.md` (current 168 lines) and existing fragments. Each learning that was consolidated becomes one index entry. This is the initial population — future entries added by remember skill.

**Multi-project deployment:**
- Each project consuming agent-core needs `@agent-core/fragments/memory-index.md` added to its CLAUDE.md
- Known consumers: claudeutils, pytest-md, tuick
- One-time migration per project when they next update the agent-core submodule ref

**Testing strategy:**
- Verify memory-index.md is loaded at session start (visible in CLAUDE.md expansion)
- Run `/remember` on a synthetic learning, verify index entry added
- Verify design skill's memory discovery step fires and reads referenced files
- Verify orphan deletions don't break any existing `@`-references
- Verify new `.claude/rules/` entries trigger on plan file access and commit file access

## Next Steps

This is a general task — route to `/plan-adhoc`.
