# Design: Ambient Awareness of Consolidated Learnings

## Problem

When learnings are consolidated from `agents/learnings.md` into permanent locations (fragments, decisions, skill references), they disappear from the agent's ambient context. The agent has no mechanism to discover that new rules exist or that existing rules were updated — unless the fragment happens to be `@`-referenced in CLAUDE.md.

**Current state:**
- 22 fragments in `agent-core/fragments/`, 15 `@`-referenced in CLAUDE.md, 7 orphaned
- `.claude/rules/` path-scoped rules exist (7 files) — contextual "go read the docs" triggers
- Remember skill consolidates learnings but doesn't update discovery mechanisms
- No changelog, index, or notification system for consolidated learnings

**Concrete failure modes:**
- Agent creates fragment `agent-core/fragments/foo.md` via `/remember` — nobody knows it exists
- Agent updates fragment `error-handling.md` with new pattern — other sessions use stale mental model
- Orphaned fragments (error-classification, prerequisite-validation, hashtags, etc.) contain valuable content that's never loaded

## Requirements

**Functional:**
- After consolidation, new/updated rules become discoverable without manual intervention
- Agents starting new sessions encounter recently consolidated learnings
- Progressive disclosure preserved — not everything loaded at once

**Non-functional:**
- No MCP servers, external databases, or hooks infrastructure beyond what exists
- Token-efficient — avoid loading all fragments unconditionally
- Compatible with agent-core's multi-project deployment (agent-core is a git submodule)
- Simple enough for the remember skill to execute as a final step

**Out of scope:**
- Confidence scoring / decay (overkill for this scale — ~25 fragments, ~5 skill reference files)
- Semantic search / embeddings
- Automatic extraction from conversation (already handled by `/remember`)
- CLAUDE.md regeneration (the `@`-import system works fine)

## Architecture

### Key Insight

The project already has two discovery mechanisms:
1. **`@`-imports in CLAUDE.md** — always loaded, unconditional
2. **`.claude/rules/` with path frontmatter** — conditionally loaded when touching matching files

The gap is: **neither mechanism is updated when `/remember` consolidates a learning.**

The solution adds a third discovery mechanism: a **consolidation changelog** that provides session-start awareness of recent changes, plus a process fix to the remember skill.

### Three-Part Solution

#### Part 1: Consolidation Changelog (`agent-core/fragments/CHANGELOG.md`)

A rolling log of recent consolidation events. `@`-imported in CLAUDE.md. Capped at ~20 entries (newest first). Each entry is one line.

```markdown
# Fragment Changelog

Recent consolidation events. Read referenced files when working in related areas.

- 2026-01-31: **error-handling.md** — Added TMPPREFIX pattern for zsh sandbox heredocs
- 2026-01-30: **delegation.md** — Updated quiet execution with two-phase communication
- 2026-01-28: NEW **prerequisite-validation.md** — 4-category checklist for plan prerequisites
```

**Why this works:**
- ~20 lines = negligible token cost (always loaded)
- Agent sees *what changed recently* and *where to look*
- Creates natural "ambient awareness" without loading full content
- Rolling window means stale entries age out

**Maintenance:**
- **Remember skill:** Append-only. Adds one entry at top of list after consolidation. Never trims.
- **Scripted trim:** `just trim-changelog` target handles rotation. Counts lines matching `^- ` (entry lines), removes oldest (bottom) when count exceeds 20. Preserves header block verbatim.
- **Trigger:** Run `just trim-changelog` periodically (e.g., after several `/remember` invocations, or as part of `just sync-to-parent`). Not required after every append — the file works fine with 21-25 entries.

**Why split:** The skill has the best context to write a quality description (it just consolidated the learning). But trimming is mechanical work that doesn't belong in the skill's cognitive flow. Separation keeps the skill focused on consolidation.

#### Part 2: Remember Skill — Post-Consolidation Steps

Add to the remember skill's "Apply + Verify" phase (Section 4):

**Step 4a: Update discovery mechanisms**

After consolidating a learning:

1. **If new fragment created:** Add `@`-reference to CLAUDE.md OR create `.claude/rules/` entry if path-scoped. **Heuristic:** If the learning applies regardless of which files are being edited → `@`-ref in CLAUDE.md. If it only applies when working with a specific file type or directory (e.g., `plans/**`, `*.py`, `.claude/hooks/`) → `.claude/rules/` entry with path frontmatter.
2. **If existing fragment updated:** Append entry to `agent-core/fragments/CHANGELOG.md`
3. **If skill reference updated:** If significant behavioral change (new required steps, changed contract): append entry to CHANGELOG.md. If minor clarification: no action needed.
4. **If decision file updated:** Verify corresponding `.claude/rules/` entry exists for path trigger

This closes the loop — consolidation automatically updates discoverability.

#### Part 3: Orphan Audit + Cleanup

One-time action: resolve the 7 orphaned fragments.

| Fragment | Action | Rationale |
|----------|--------|-----------|
| `AGENTS-framework.md` | Delete | 9-line stub, content superseded by CLAUDE.md structure |
| `error-classification.md` | Add `.claude/rules/` entry scoped to `plans/**` | Error taxonomy primarily relevant during plan execution, not general work. 131 lines — too expensive for always-loaded. |
| `prerequisite-validation.md` | Add `.claude/rules/` entry scoped to `plans/**` | Only relevant during planning |
| `roles-rules-skills.md` | Delete | Taxonomy content now in skill-development skill |
| `tool-preferences.md` | Delete | Content already in delegation.md (Task Agent Tool Usage section) |
| `commit-delegation.md` | Add `.claude/rules/` entry scoped to commit-related paths | 290 lines of unique commit delegation workflow. NOT duplicated in delegation.md (which has no commit content). Scope to skill/commit files. |
| `hashtags.md` | Delete | Content redundant with communication.md (#stop), delegation.md (#delegate, #tools, #quiet). Semantic markers are already covered by the fragments they reference. |

**Net result:** 3 deletions, 3 new `.claude/rules/` entries. Fragments dir goes from 22 to 19 files, all discoverable.

## Design Decisions

**Why changelog, not index?**
An index is a static catalog that agents must proactively read. A changelog surfaces *what's new* — the critical information for ambient awareness. Agents naturally scan recent changes; they don't browse catalogs. Indexes also create maintenance burden (must be kept in sync).

**Why not `.claude/rules/` for everything?**
Path-scoped rules only trigger when Claude touches matching files. Cross-cutting concerns (error handling, communication patterns, delegation) apply everywhere — they belong in CLAUDE.md `@`-imports. The changelog is also cross-cutting (you need to know what changed regardless of what you're editing).

**Why not auto-generate CLAUDE.md from fragments?**
The `@`-import mechanism already does this effectively. CLAUDE.md is hand-curated — the order and grouping of `@`-refs encodes priority (tier 1 at top). Auto-generation would lose this curation. The memory-mcp approach of regenerating CLAUDE.md makes sense at scale (100+ memories with decay scores) but is overkill here.

**Why 20-entry cap on changelog?**
- 20 entries × ~80 chars = ~1600 chars ≈ 400 tokens. Negligible cost.
- At typical consolidation rate (~2-5 per week), 20 entries covers ~4-10 weeks of history.
- Beyond that timeframe, the fragment itself is the source of truth.

**Why not a SessionStart hook to inject learnings?**
Hooks add infrastructure complexity. The `@`-import of the changelog achieves the same result with zero moving parts. If the changelog grows stale (no consolidations in weeks), it simply shows old entries — no harm, no wasted computation.

## Implementation Notes

**Files affected:**
- `agent-core/fragments/CHANGELOG.md` — new file
- `CLAUDE.md` — add `@agent-core/fragments/CHANGELOG.md` import (after Documentation Structure section, before Communication Rules)
- `agent-core/skills/remember/SKILL.md` — add post-consolidation discovery step
- `agent-core/skills/remember/references/consolidation-patterns.md` — update with discovery guidance
- `.claude/rules/planning-work.md` — new rule file scoping prerequisite-validation + error-classification to `plans/**`
- `.claude/rules/commit-work.md` — new rule file scoping commit-delegation to commit-related paths
- `justfile` — add `trim-changelog` target
- 3 fragment files — delete (AGENTS-framework, roles-rules-skills, tool-preferences, hashtags)
- `agents/README.md` — update or delete (references AGENTS-framework.md and roles-rules-skills.md; may be largely obsolete)
- `agent-core/README.md` — update directory tree listing (references tool-preferences.md and AGENTS-framework.md)

**Multi-project deployment:**
- Each project consuming agent-core needs `@agent-core/fragments/CHANGELOG.md` added to its CLAUDE.md
- Known consumers: claudeutils, pytest-md, tuick
- This is a one-time migration per project when they next update the agent-core submodule ref

**Testing strategy:**
- Verify CHANGELOG.md is loaded at session start (check `/memory` output)
- Run `/remember` on a synthetic learning, verify changelog entry added and entry count correct
- Verify orphan deletions don't break any existing `@`-references (grep all CLAUDE.md files for deleted fragment names)
- Verify new `.claude/rules/` entries trigger on plan file access and commit file access
- Multi-project: verify pytest-md's CLAUDE.md correctly loads the changelog after submodule update

**Migration:**
- Seed CHANGELOG.md with recent consolidation history (reconstruct from git log of fragment changes)
- Run orphan audit as part of implementation

## Next Steps

This is a general/oneshot task — route to `/plan-adhoc`.
