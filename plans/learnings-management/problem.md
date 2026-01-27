# Learnings Discoverability Problem

**Date**: 2026-01-27
**Status**: Ready for implementation

## Problem Statement

Learnings consolidation architecture exists (`plans/learnings-consolidation/design.md`) but requirements are buried in reference files, causing protocol violations.

## Existing Architecture

```
CLAUDE.md
  └─ @agents/session.md
       └─ @agents/learnings/pending.md
            └─ @agents/learnings/*.md
```

- **add-learning.py**: Stages learnings to individual files, updates pending.md
- **Handoff**: Extracts learnings, calls add-learning.py
- **Remember**: Consolidates pending.md to skill refs

See `plans/learnings-consolidation/design.md` for full design.

## Discoverability Gap

Requirements exist but are buried:

| Requirement | Current Location | Should Be |
|-------------|------------------|-----------|
| @ reference chain | references/learnings-staging.md | Main SKILL.md |
| Session size = @ chain total | references/learnings-staging.md | Main SKILL.md |
| add-learning.py usage | references/learnings-staging.md | Main SKILL.md |

## Impact

Sonnet agent violated protocol (2026-01-27):
- Did not stage learnings via add-learning.py
- Did not include @ reference chain
- Used manual wc -l instead of @ chain measurement

## Solution

Surface critical requirements in handoff SKILL.md directly, not via references.

**Task**: Update `.claude/skills/handoff/SKILL.md` to inline:
- @ chain requirement with example
- Session size measurement formula
- add-learning.py invocation

## Related

- `plans/learnings-consolidation/design.md` - Full architecture
- `plans/handoff-skill/design.md` - Handoff-lite split (defers learnings)
- `.claude/skills/handoff/references/learnings-staging.md` - Current buried location
