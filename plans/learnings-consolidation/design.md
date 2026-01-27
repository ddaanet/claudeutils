# Design: Learnings Consolidation

## Problem

Learnings captured in session.md are lost when session is trimmed. Current consolidation to CLAUDE.md/design-decisions.md lacks discoverability.

## Solution

Segmented learnings with @ chain expansion → consolidation to skill reference files.

## Architecture

```
CLAUDE.md
  └─ @agents/session.md
       └─ @agents/learnings/pending.md
            └─ @agents/learnings/2026-01-26-slug.md
            └─ @agents/learnings/2026-01-27-slug.md
```

## Components

### 1. Staging: `agents/learnings/`

**Structure:**
- `pending.md` - Index of @ references to individual learning files
- `*.md` - Individual learning files (one per learning)

**Learning file format:**
```markdown
**[Title]:**
- Anti-pattern: [what NOT to do]
- Correct pattern: [what TO do]
- Rationale: [why]
```

### 2. Script: `agent-core/bin/add-learning.py`

**Input:** slug, content (via multiline quoted string)
**Actions:**
- Write `agents/learnings/{date}-{slug}.md`
- Append `@agents/learnings/{date}-{slug}.md` to `pending.md`
- Return filename

**Usage:** `python3 agent-core/bin/add-learning.py "slug" "content..."`

### 3. Handoff skill update

- Extract learnings from conversation
- Call add-learning.py for each learning
- Line count must follow @ chain for size check

### 4. Remember skill update

- Read `agents/learnings/pending.md`
- For each learning: infer target skill from content, ask user if uncertain
- Append to `skills/{skill}/references/learnings.md`
- Remove processed entries from pending.md
- Delete processed learning files

### 5. Topical skills (future)

Cross-cutting learnings → new skills:
- `sandboxed` - Bash restrictions, heredocs, file system rules
- `token-optimization` - Quiet execution, minimal returns
- `interactive-orchestration` - User interaction timing

## Key Decisions

**@ expansion:** Memory files (CLAUDE.md chain) expand recursively; prompt @ refs do not.

**Staging needed:** Yes - allows batch consolidation, versioning before processing.

**Target inference:** Remember skill infers target skill from learning content keywords, asks user if uncertain.

**No auto-injection:** Learnings loaded via skill references (progressive disclosure), not hooks.

## Session Reference

Design session: `3571ef05-f905-44f7-83e5-11cb2d141e10`
