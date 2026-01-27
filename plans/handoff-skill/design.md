# Handoff Skill Split: Design Outline

**Status**: Ready for implementation
**Implementer**: Standard model

## Goal

Split handoff into two skills matching model capability:
- **handoff-lite**: Efficient model, mechanical preservation
- **handoff**: Standard/premium, full protocol with judgment

## Implementation Tasks

### 1. Create handoff-lite skill

**Path**: `.claude/skills/handoff-lite/SKILL.md`

**Frontmatter**:
```yaml
name: handoff-lite
description: Lightweight session handoff for efficient models. Preserves context mechanically without learnings judgment. Use when ending orchestration sessions.
```

**Content requirements**:
- No reference files (template embedded)
- No judgment calls
- 3 steps max

**Protocol**:
1. Review conversation for completed/pending tasks
2. Write session.md with embedded template (below)
3. Report completion with line count

**Embedded template**:
```markdown
# Session Handoff: [DATE]

**Status**: [Brief status]

## Completed This Session
[Bullet list of completed work with commit hashes/file refs]

## Pending Tasks
[Bullet list with checkboxes]

## Session Notes
[Raw observations, discoveries, issues encountered - NO FILTERING]
[Preserve verbatim what happened, let standard model judge later]

## Blockers / Gotchas
[Any blockers or warnings for next agent]

## Next Steps
[Immediate next action]

---
*Handoff by efficient model. Session notes preserved for learnings review.*
```

**Key difference**: "Session Notes" not "Recent Learnings". No judgment about what's a learning. Dump observations.

### 2. Update existing handoff skill

**Path**: `.claude/skills/handoff/SKILL.md`

**Changes**:
- Line 12: Change "Haiku" to "Standard (Sonnet)"
- Add to Protocol section after step 1: "If reviewing an efficient-model handoff, process Session Notes for learnings"
- Principles: Add note about reviewing efficient handoffs

### 3. Update plugin.json (if skills registered there)

Check if skills need registration. Add handoff-lite if so.

## Verification

After implementation:
- [ ] handoff-lite skill exists with embedded template
- [ ] handoff skill updated with correct target model
- [ ] No reference file dependencies in handoff-lite

## Notes

- Learnings management (discoverability issues) is separate work stream: `plans/learnings-management/`
- Don't move add-learning.py or change @ chain requirements in this work
