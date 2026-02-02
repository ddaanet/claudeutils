# Design: Memory Index Location Fix + Seeding

## Problem

The memory index (`agent-core/fragments/memory-index.md`) lives in the shared submodule, but catalogs project-specific learnings. This is architecturally wrong:

- `agent-core` is a git submodule shared across projects (claudeutils, pytest-md, tuick)
- Memory index entries reference project-specific files (`agents/decisions/*.md`, `.claude/rules/`)
- A commit to memory-index.md in agent-core propagates to all consumers
- Other projects would see irrelevant entries about claudeutils-specific decisions
- The index was created empty — never seeded with existing learnings despite design specifying "Reconstruct initial entries from agents/learnings.md"

**Root cause:** The ambient-awareness design treated the memory index as infrastructure (belongs in agent-core) when it's actually project-specific knowledge (belongs in consuming project).

## Requirements

**Functional:**
- Move memory-index.md from `agent-core/fragments/` to project-level (`agents/`)
- Seed the index with existing learnings from `agents/learnings.md` and `agents/decisions/*.md`
- Update all references: CLAUDE.md import, remember skill, consolidation-patterns, design/plan skills
- Preserve the existing memory-index header/structure (append-only, sections, etc.)

**Non-functional:**
- No behavioral change to remember skill or design/plan skills — just path correction
- Multi-project deployment: each project owns its own memory index (correct behavior)

**Out of scope:**
- Running `/remember` to consolidate learnings.md (separate task, unchanged in pending list)
- Changing the memory index format or sections

## Architecture

### Key Insight

The memory index has two kinds of entries:
1. **Shared entries** — reference `agent-core/fragments/*.md` (shared infrastructure)
2. **Project entries** — reference `agents/decisions/*.md`, `.claude/rules/`, project CLAUDE.md

Both belong in the project-level index because:
- Even shared fragment entries are *discoverable* via the project CLAUDE.md `@`-import
- The index's purpose is "what does THIS project know" — not "what does agent-core know"
- agent-core fragments are already discoverable via their `@`-imports in CLAUDE.md; the index adds discovery for those NOT `@`-imported

### File Changes

**Move:**
- FROM: `agent-core/fragments/memory-index.md`
- TO: `agents/memory-index.md`

**Update CLAUDE.md:**
- Change: `@agent-core/fragments/memory-index.md` → `@agents/memory-index.md`

**Update remember skill** (`agent-core/skills/remember/SKILL.md`):
- Step 4a line 63: `agent-core/fragments/memory-index.md` → project's `agents/memory-index.md`
- The skill must use a project-relative path. Since skills execute in project root, `agents/memory-index.md` works.

**Update consolidation-patterns** (`agent-core/skills/remember/references/consolidation-patterns.md`):
- Line 70: same path update (index file location)
- Lines 73, 78-79: example entry format — update the index file path reference
- **Note:** Index entries that reference `agent-core/fragments/*.md` or `agents/decisions/*.md` as *targets* remain valid — those are where learnings are stored, not the index location itself. Only the path to the index file changes.
- Lines 86-97 (Discovery Routing examples) reference `@agent-core/fragments/` — these remain correct because CLAUDE.md `@`-imports still point to agent-core fragments

**Update design skill** (`agent-core/skills/design/SKILL.md`):
- Step 1.5 mentions "memory-index.md" generically — no path change needed (it references the `@`-imported content)

**Update plan-adhoc skill** (`agent-core/skills/plan-adhoc/SKILL.md`):
- Point 0.5 mentions "memory-index.md" generically — no path change needed

**Update plan-tdd skill** (`agent-core/skills/plan-tdd/SKILL.md`):
- Step 3.5 mentions "memory-index.md" generically — no path change needed

**Update ambient-awareness design** (`plans/ambient-awareness/design.md`):
- Update Part 1 location reference for historical accuracy (not critical but prevents confusion)

**Delete from agent-core:**
- Remove `agent-core/fragments/memory-index.md` after move (not archive — git history preserves it)

### Seeding the Index

Prime `agents/memory-index.md` with entries from existing learnings. Source material:

**From `agents/learnings.md`** (169 lines, ~28 learnings):
Each learning that has been consolidated into permanent docs becomes one index entry pointing to its consolidation target.

**From `agents/decisions/*.md`**:
Key decisions already documented but not indexed — scan for major entries.

**Entry format** (unchanged from design):
```markdown
- [Summary of learning] | `path/to/file.md`
```

**Seeding heuristic — what to index vs skip:**
- **Index:** Knowledge NOT already `@`-imported in CLAUDE.md — decision files, skill references, `.claude/rules/` entries, orphaned fragments
- **Skip:** Knowledge in `@`-imported fragments — already discoverable via CLAUDE.md context loading
- **Focus areas:** (1) `agents/decisions/*.md` content not surfaced via path-scoped rules, (2) skill-specific `references/` learnings, (3) `.claude/rules/` entries (path-triggered, not ambient)

### Multi-Project Deployment

Each project consuming agent-core creates its own `agents/memory-index.md` (or equivalent project-level location) and adds `@agents/memory-index.md` to its CLAUDE.md. The remember skill uses a project-relative path, so it works across all consumers.

**Current consumer status:**
- claudeutils: imports `@agent-core/fragments/memory-index.md` — requires migration (this design)
- pytest-md, tuick: do NOT yet import memory-index — no breakage from deletion, no migration needed now

**Migration per consumer project (when ready):**
- Create `agents/memory-index.md` from template (header + empty sections)
- Add `@agents/memory-index.md` to project CLAUDE.md
- Seed with project-specific learnings (if any)

## Design Decisions

**Why `agents/` not project root?**
- `agents/` already holds project-specific agent knowledge (`learnings.md`, `session.md`, `decisions/`)
- Memory index is project-specific institutional knowledge — same domain
- Consistent location across consuming projects

**Why not keep a template in agent-core?**
- agent-core could provide a template/example, but the actual index must be project-owned
- Over-engineering for now — the header is 6 lines, easily created by hand or remember skill
- If needed later, `agent-core/templates/memory-index.md` can be added

**Why seed now instead of waiting for `/remember`?**
- The pending `/remember` task will consolidate learnings.md INTO permanent docs
- Seeding populates the index with entries POINTING TO existing permanent docs
- These are complementary operations, not redundant
- Seeding prevents an empty index from being useless until `/remember` runs

## Implementation Notes

**Files affected:**
- `agent-core/fragments/memory-index.md` — DELETE
- `agents/memory-index.md` — CREATE (with seeded entries)
- `CLAUDE.md` — update `@`-import path
- `agent-core/skills/remember/SKILL.md` — update path in step 4a
- `agent-core/skills/remember/references/consolidation-patterns.md` — update paths
- `plans/ambient-awareness/design.md` — update location references (optional, low priority)
- `agents/decisions/architecture.md` — historical reference to memory-index.md (optional, low priority)

**Note:** After this change, the remember skill no longer writes into `agent-core/`, which aligns with the PreToolUse symlink-redirect hook's intent.

**Testing strategy:**
- Verify `@agents/memory-index.md` loads in CLAUDE.md (session restart)
- Verify remember skill's step 4a references correct path
- Verify old agent-core path is removed

## Next Steps

Route to `/plan-adhoc`. Moderate complexity — likely Tier 1 or 2 (path updates + seeding).
