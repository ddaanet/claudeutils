# Handoff Skill Protocol Adherence Problem

**Date**: 2026-01-27
**Status**: Problem identified, design discussion needed

## Problem Statement

Handoff skill protocol was violated when haiku agent executed `/handoff` and omitted:
1. "Recent Learnings" section from session.md
2. Step 4: Process learnings to staging area (add-learning.py)

## Root Cause Analysis

**Primary cause**: Skill complexity mismatch with target model

The skill header declares "Target Model: Haiku (simple file update)" but the protocol requires:
- 5-step process with conditional logic
- Progressive disclosure (reading reference files)
- Learnings detection requiring judgment
- Staging learnings via script execution

**Contributing factors**:
1. **No mandatory read enforcement**: References say "See X" not "Read X before proceeding"
2. **No verification checkpoint**: Nothing validates all sections present before completion
3. **Progressive disclosure without enforcement**: Agent can skip reference reads
4. **Conditional logic ambiguity**: "If session has learnings" interpreted as "if section exists" not "if learnings discovered"
5. **Section naming mismatch**: Previous session.md had "Session Notes" not "Recent Learnings"

## Protocol Gap

Step 4 says:
> "If the session has learnings in the 'Recent Learnings' section, stage them"

Agent interpreted this as "check if section already exists" rather than "identify if learnings were discovered this session and create section if needed."

## Observed Behavior

**Expected**:
1. Read template.md for section structure
2. Identify learnings from session (Session Notes, discoveries, anti-patterns)
3. Create "Recent Learnings" section
4. Stage learnings via add-learning.py
5. Verify completeness

**Actual**:
1. Wrote session.md from memory of skill instructions
2. Omitted "Recent Learnings" section
3. Skipped learnings staging entirely
4. No verification performed

## Evaluation Results

**Quality**: 7/10 (good context, missing critical section)
**Conformity**: 6/10 (violated template and protocol requirements)

**Compared to good-handoff.md example**:
- ✗ Missing Recent Learnings section with anti-patterns
- ✗ No learnings staged to pending.md
- ~ Pending tasks lack priority markers
- ✓ Good traceability and decision context

## Design Discussion Topics

1. **Two-level handoff protocol** - Split quick (haiku) vs full (sonnet) handoffs
2. **Skill enforcement mechanisms** - How to ensure reference reads and verification
3. **Learnings detection** - Make explicit what constitutes a "learning"
4. **Model-skill matching** - Should handoff always use sonnet regardless of complexity?

## Next Steps

- [ ] Design two-level handoff protocol (quick vs full)
- [ ] Propose skill enforcement mechanisms
- [ ] Define learnings detection criteria explicitly
- [ ] Update handoff skill with findings
- [ ] Document in design-decisions.md

## Related Context

- Session handoff: agents/session.md
- Handoff skill: .claude/skills/handoff/SKILL.md
- Template: .claude/skills/handoff/references/template.md
- Good example: .claude/skills/handoff/examples/good-handoff.md
- Evaluation: See earlier opus analysis in this session
