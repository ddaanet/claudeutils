# Session Handoff: Handoff Skill Protocol Adherence

**Date**: 2026-01-27
**Status**: Problem diagnosed, design discussion ready

## Completed This Session

**Protocol violation diagnosis:**
- Identified haiku agent executed `/handoff` and omitted Recent Learnings section
- Root cause: Skill complexity mismatch with target model (haiku labeled, sonnet-level complexity)
- Skill requires: 5-step protocol, progressive disclosure, learnings detection, script execution
- Agent behavior: Wrote session.md from memory, skipped reference reads, no verification
- Evaluation: 7/10 quality (good context), 6/10 conformity (violated template requirements)

**Problem documentation:**
- Created plans/handoff-skill/problem.md with complete analysis
- Documented: root cause, protocol gaps, observed vs expected behavior, design topics
- Preserved: evaluation details, comparison to good-handoff.md example
- Commit: 5270149 (✨ Add markdown composition API with TDD methodology)

## Pending Tasks

- [ ] **Design two-level handoff protocol** (IMMEDIATE)
  - Quick handoff (haiku): Status, Completed, Pending, Next Steps only
  - Full handoff (sonnet): Complete 5-step protocol with learnings
  - Auto-escalation: If Recent Learnings or #learning tags detected, escalate to full
  - Document: When to use each level, escalation criteria

- [ ] **Propose skill enforcement mechanisms** (AFTER PROTOCOL DESIGN)
  - Mandatory reads: "FIRST, read template.md" not "See template.md"
  - Verification checkpoint: "Before completing, verify sections present"
  - Learnings detection: Explicit criteria for what constitutes a learning
  - Reference: Compare to good-handoff.md structure

- [ ] **Update handoff skill** (AFTER DESIGN APPROVAL)
  - Split into two skill files or one with --full flag
  - Add verification step before completion
  - Make learnings detection explicit
  - Update references and examples

- [ ] **Document in design-decisions.md** (FINAL STEP)
  - Why two-level protocol chosen
  - Model-skill matching principles
  - Trade-offs and alternatives considered

## Blockers / Gotchas

**None currently blocking design work.**

**Key insights:**
- Progressive disclosure without enforcement is insufficient for haiku
- Conditional logic ("if learnings exist") needs explicit detection criteria
- Section naming conventions must be consistent (Recent Learnings not Session Notes)

## Design Discussion Topics

### 1. Two-Level Handoff Protocol

**Quick handoff (haiku)**:
- Scope: Update Status, Completed, Pending, Next Steps only
- No reference reads required
- Template embedded in skill
- 3-step protocol max
- Target: 30 seconds, mechanical update

**Full handoff (sonnet)**:
- Scope: Complete 5-step protocol with learnings
- Read template.md, learnings-staging.md
- Process and stage learnings
- Verification checkpoint
- Target: 2-3 minutes, thoughtful synthesis

**Auto-escalation criteria**:
- Recent Learnings section exists in current session.md
- Session contains #learning tags
- Session Notes has "What to improve" or "Anti-pattern" content
- User explicitly requests `--full` flag

### 2. Skill Enforcement Mechanisms

**Current problem**: "See X" is treated as optional by agents

**Proposed solutions**:
- **Mandatory reads**: "FIRST: Read `references/template.md` to load section structure"
- **Step sequencing**: Number steps 1-N, make each dependent on previous
- **Verification gate**: "Before completing, verify all sections present"
- **Explicit conditionals**: "Learnings exist if ANY of: anti-pattern, process improvement, unexpected behavior"

### 3. Learnings Detection Criteria

**Make explicit what constitutes a "learning":**
- Anti-pattern discovered (what NOT to do with example)
- Process improvement identified (workflow, timing, batching)
- Unexpected behavior encountered and resolved
- New pattern or technique validated
- Tool usage insight (efficiency, limitations)
- Delegation pattern refined

### 4. Model-Skill Matching

**Question**: Should handoff always use sonnet regardless of declared target?

**Current**: Skill says "Target Model: Haiku" but protocol is too complex
**Options**:
1. Remove target model declaration (let user/orchestrator choose)
2. Change target to "Sonnet" and accept the cost
3. Implement two-level protocol (quick for haiku, full for sonnet)

**Recommendation**: Option 3 - two-level protocol provides flexibility

## Implementation Strategy

**Phase 1: Design approval** (opus/sonnet)
- Review two-level protocol design
- Finalize enforcement mechanisms
- Approve learnings detection criteria

**Phase 2: Skill updates** (sonnet)
- Split handoff skill or add --full flag
- Add verification checkpoint
- Update template.md with explicit criteria
- Update examples with both quick and full handoffs

**Phase 3: Testing and validation** (sonnet)
- Test quick handoff with haiku
- Test full handoff with sonnet
- Verify auto-escalation works
- Update documentation

## Related Files

**Problem documentation:**
- plans/handoff-skill/problem.md - Complete problem analysis

**Skill files:**
- .claude/skills/handoff/SKILL.md - Current skill (needs updates)
- .claude/skills/handoff/references/template.md - Template structure
- .claude/skills/handoff/references/learnings-staging.md - Staging protocol
- .claude/skills/handoff/examples/good-handoff.md - Best practices example

**Evidence:**
- agents/session.md - Session handoff that violated protocol (now fixed with Recent Learnings)
- This conversation - Full diagnosis and evaluation

## Next Steps

**Immediate**: Opus/Sonnet design session to finalize two-level protocol and enforcement mechanisms

**After design**: Sonnet implementation to update skill files, add verification, create examples

**Success criteria**:
- Quick handoffs complete in <1 minute with mechanical updates
- Full handoffs capture all learnings and stage them correctly
- Haiku can successfully execute quick handoffs
- Sonnet can successfully execute full handoffs
- No protocol violations in next 5 handoffs
