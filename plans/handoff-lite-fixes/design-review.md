# Design Review: Handoff-Lite Fixes

## Verdict: APPROVE WITH CHANGES

The design correctly identifies and addresses all four root causes from the transcript analysis. The solutions are well-reasoned and appropriately scoped. However, several important issues need addressing before implementation.

## Strengths

- **Root cause alignment**: Each fix directly addresses a specific root cause from the transcript
- **Separation of concerns**: Fix 1 (decouple handoff from commit) correctly identifies conceptual mismatch
- **Strong rationale**: Fix 3 (rename to handoff-haiku) makes constraint enforcement self-documenting through naming
- **Progressive disclosure**: Design follows skill-dev best practices by focusing on SKILL.md changes without bloating
- **Explicit merge semantics**: Fix 2 PRESERVE/ADD/REPLACE pattern directly addresses template ambiguity
- **Comprehensive scope**: Fixes 5 and 6 catch additional issues found during skill-dev reevaluation

## Issues

### Fix 2 - Incomplete PRESERVE/ADD/REPLACE Implementation
**Severity:** Critical

**Details:** The PRESERVE/ADD/REPLACE merge semantics are well-designed but the proposed implementation has gaps:

1. The design says "Replace current Step 2" with merge rules, but doesn't specify what happens to the actual template content
2. Template should be restructured to show ONLY the sections being REPLACED/ADDED
3. Current template (lines 24-47 of handoff-lite SKILL.md) shows complete session.md structure — this will recreate the same ambiguity

**Current template structure:**
```markdown
# Session Handoff: [DATE]
...
## Session Notes
...
```

This complete structure implies "replace session.md with this." The merge rules say PRESERVE other sections, but the template doesn't show WHERE to preserve them.

**Suggestion:**
- Remove the complete template structure from Step 2
- Replace with a partial template showing ONLY REPLACE/ADD sections
- Add explicit instruction: "Preserve all other sections in their current position"
- Example structure:

```markdown
### 2. Update session.md

**Merge rules:**
- **REPLACE** these sections: "Completed This Session", "Pending Tasks", "Blockers / Gotchas", "Next Steps"
- **ADD** "Session Notes" section IF new observations exist
- **PRESERVE UNCHANGED** all other sections (especially "Recent Learnings", "Reference Files", "Prior Session")

**How to apply:**
1. Read current session.md
2. Update ONLY the sections listed under REPLACE
3. Add Session Notes section if new observations exist
4. Keep everything else exactly as-is

**Template for sections you ARE replacing/adding:**

## Completed This Session
[What was accomplished - factual, specific]

## Pending Tasks
- [ ] Task 1
- [ ] Task 2

## Session Notes
[Raw observations - NO FILTERING, let standard model judge later]

## Blockers / Gotchas
[Any blockers or warnings]

## Next Steps
[Immediate next action]

**CRITICAL:** Do NOT delete existing sections not shown above.
```

This makes it clear the template is a PARTIAL replacement, not a complete structure.

### Fix 5 - Description Still Invites Misuse
**Severity:** Important

**Details:** The proposed handoff-haiku description improves on the current version but still has a routing problem:

**Proposed:**
```yaml
description: This skill should be used ONLY by Haiku models for mechanical session handoff. Not for Sonnet or Opus — use /handoff instead. Preserves session context without learnings judgment for quick orchestrator handoffs.
```

**Problem:**
- Skill-dev best practices (line 44) say descriptions should include "specific trigger phrases users would say"
- This description has NO user trigger phrases — it's agent-selection criteria
- The skill is NEVER user-invoked (orchestrators invoke it)
- But the skill system loads based on description matching user input

**Current behavior:** When user says "handoff", both skills match. Agent picks one.

**Better approach:**
```yaml
description: Internal skill for Haiku model orchestrators only. Never user-invoked. Use /handoff for standard handoffs. This skill preserves session context mechanically without learnings judgment.
```

Lead with "Internal skill" to signal this isn't user-facing.

**Even better - consider marking non-user-invocable:**
Add frontmatter field:
```yaml
user-invocable: false
```

This prevents skill from appearing in user-facing skill lists while still being invokable by agents who know the exact name.

### Fix 1 - Commit Skills Missing Session.md
**Severity:** Important

**Details:** The design removes handoff from commit skills but doesn't address the resulting gap: **session.md won't be included in commits**.

**Current state:**
- `commit-context` Step 1: "Perform handoff" (updates session.md)
- Then commits, including session.md

**After Fix 1:**
- Handoff step removed
- Commits won't include session.md updates

**Problem:** User completes work, invokes `/commit-context`, expects session.md to be committed alongside code. But session.md changes aren't staged.

**From transcript (line 225):**
> Fix: Skills should explicitly include session.md and plans/ in commit guidance

**Suggestion:**
Add to commit-context and commit SKILL.md Step 5 (staging):
```markdown
5. **Stage, commit, verify**
   - Stage specific files based on conversation context
   - **Include session.md and plans/** if they changed
   - Stage code files that were written/edited
   - Do NOT commit secrets (.env, credentials.json, etc.)
```

This ensures session.md gets committed when appropriate without coupling handoff into commit.

### Fix 6 - Writing Style Changes Are Minor
**Severity:** Minor

**Details:** Fix 6 identifies writing style violations but the examples given are actually correct:

**Quoted from design:**
> Line 14: "When invoked, update session.md mechanically:" — second-person-adjacent ("you update"). Better: "Update session.md mechanically on invocation:"

**Analysis:**
- "When invoked, update X" is temporal conditional, not second person
- Skill-dev examples (line 369): "To create a hook, define the event type" — same pattern
- This is imperative form with context clause

**Current handoff-lite line 14:**
```markdown
When invoked, update session.md mechanically:
```

This IS imperative form. No change needed.

**Actual style issue (if any):**
Line 3 of handoff-lite uses "efficient models (Haiku)" which could be more direct, but Fix 5 already addresses description rewrite.

**Suggestion:**
- Drop Fix 6 as a separate fix
- If minor style improvements are noticed during implementation, make them
- Don't treat as a design requirement

### Fix 3 - Cross-References Incomplete
**Severity:** Minor

**Details:** Design identifies cross-reference locations to update but misses one:

**Listed in design:**
- handoff/SKILL.md line 21
- handoff/SKILL.md lines 171-175
- agents/session.md
- CLAUDE.md

**Missing:**
- commit-context/SKILL.md line 113 (references `/handoff` in Step 1 — though this entire step is being removed by Fix 1)
- commit/SKILL.md line 108 (references `/handoff` in Step 2 — also being removed)

**Since Fix 1 removes these steps entirely, the cross-references vanish anyway.**

**Suggestion:** Clarify in design that commit skill cross-references are handled by Fix 1 removal, not by explicit updates.

## Questions for Designer

**Q1: User workflow after decoupling**
With Fix 1, user must invoke `/handoff` then `/commit-context` separately. This adds friction. What's the expected workflow?

- Option A: User invokes `/handoff`, then `/commit-context` (2 commands)
- Option B: User invokes `/commit-context` only, manually updates session.md first
- Option C: Create a wrapper skill that calls both in sequence

Which is intended? If Option A, should we document this in commit-context description?

**Q2: Session.md commit timing**
If handoff is decoupled from commit, when should session.md be committed?

- After handoff completes?
- User manually includes it in next commit?
- Commit skills auto-detect session.md changes and include?

Design doesn't specify. Recommend adding explicit guidance.

**Q3: Haiku orchestrator handoff pattern**
The transcript mentions "orchestrator handoffs" (line 163). When does a Haiku orchestrator invoke `/handoff-haiku`?

- After completing an execution step?
- Before returning control to Sonnet?
- Only when explicitly told by orchestration plan?

Understanding this helps validate Fix 5 description changes.

**Q4: Migration path for existing sessions**
After renaming handoff-lite → handoff-haiku, what happens to existing session.md files that reference "handoff by efficient model" or other handoff-lite artifacts?

- Update session.md template footer?
- Leave existing session.md files as-is?
- Run a one-time migration?

**Q5: Skill-dev compliance - Progressive disclosure**
Current handoff-lite is 78 lines. After adding PRESERVE/ADD/REPLACE instructions and CRITICAL warnings, it may grow.

Skill-dev guidance: Keep SKILL.md under 2000 words (handoff-lite is ~400 words now).

Should detailed merge examples go in `references/merge-semantics.md` instead? Or is the current approach (inline instructions) better for Haiku consumption?

## Recommendations

### Critical Changes Required

**1. Fix 2 - Restructure template to partial form**
Remove complete session.md template structure. Show only REPLACE/ADD sections. Add explicit preservation instructions.

**2. Fix 1 - Address session.md commit gap**
Add guidance to commit skills about including session.md/plans/ when changed.

**3. Fix 5 - Clarify skill invocability**
Either lead with "Internal skill" or add `user-invocable: false` frontmatter.

### Important Changes Recommended

**4. Document user workflow**
Add to commit-context description: "Note: This skill does not update session.md. Run `/handoff` first if session context needs updating."

**5. Specify session.md commit timing**
Clarify whether session.md commits happen:
- Via handoff skill directly
- Via commit skills auto-detection
- Via user manual staging

### Minor Improvements

**6. Drop Fix 6 as separate fix**
Merge into general "implement and polish" guidance.

**7. Add validation test cases**
Specify expected behavior:
- Haiku invokes handoff-haiku with existing Recent Learnings → learnings preserved
- Sonnet invokes handoff → learnings section updated
- commit-context without prior handoff → session.md excluded from commit

## Overall Assessment

The design demonstrates strong root cause analysis and appropriate fixes. The main gaps are:

1. **PRESERVE/ADD/REPLACE implementation details** - template structure needs rework
2. **Session.md commit workflow** - unclear after decoupling
3. **User-facing impact** - decoupling adds workflow steps

With the critical changes implemented, this design will solve the original problem and improve skill quality according to skill-dev best practices.

**Recommendation:** Implement with critical changes. Consider adding a follow-up task to create a comprehensive test suite for handoff scenarios (Haiku vs Sonnet, with/without existing learnings, etc.).
