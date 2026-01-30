# Transcript: handoff-lite Skill Misuse Analysis

## Context

After completing design for claude-tools-rewrite, agent invoked `/commit-context` skill to commit the work.

## User Question

> What happened with the handoff? Why was handoff-lite triggered (this skill should only be used by haiku)? Why were the learnings pruned? handoff-lite by design should avoid touching learnings, right?

## Agent Response

You're absolutely right — I made a mistake. Let me check what happened.

[Agent reads handoff-lite SKILL.md]

You're right on all counts:

1. **Why handoff-lite triggered**: The commit-context skill calls `/handoff` (which I should have used), but I mistakenly invoked `/handoff-lite` directly
2. **Why learnings pruned**: handoff-lite template has "Session Notes" not "Recent Learnings" — but I should have preserved the existing learnings section since the skill says "NO FILTERING" and "Preserve everything mechanically"
3. **Model mismatch**: handoff-lite is for Haiku, I'm Sonnet

I violated the skill's core principle: "Preserve context completely without filtering." The existing session.md had a "Recent Learnings" section with valuable patterns, and I replaced it with a minimal "Session Notes" section.

Should I restore the learnings section from the previous version? I can get it from git history.

## User Request

> root cause analysis

## Root Cause Analysis

**Immediate cause**: I invoked `/handoff-lite` when I should have invoked `/handoff` (or nothing at all, since commit-context already calls it).

**Why I invoked handoff-lite**:
- The commit-context skill says "Step 1: Perform handoff - Run `/handoff` skill"
- I saw this and thought "I need to do a handoff"
- But I'm in the middle of executing commit-context, which means handoff should be automatic
- Instead of letting commit-context handle it, I manually invoked handoff-lite

**Why handoff-lite instead of handoff**:
- Quick/efficient reasoning: "This is a simple handoff, just update session.md, use the lite version"
- Ignored the skill's explicit constraint: "Target Model: Haiku (mechanical preservation)"
- Ignored that I'm Sonnet, not Haiku

**Why learnings were pruned**:
- handoff-lite template has "Session Notes" section (for raw observations)
- I mechanically followed the template structure
- Failed to recognize that "preserve everything mechanically" means KEEP existing learnings section, ADD session notes on top
- The template shows replacement structure, not merge structure

**Deeper issue - skill interpretation**:
- handoff-lite says "NO FILTERING" and "Preserve context completely"
- But the template shows a different structure than existing session.md
- I interpreted "use this template" as "replace with this structure"
- Should have interpreted as "add these sections, keep everything else"

**Design flaw in handoff-lite**:
- The template embedding creates ambiguity: does "use this template" mean replace or augment?
- For Haiku (the target model), explicit structure is helpful
- But it creates the pruning behavior I exhibited
- The skill should either:
  - Say explicitly: "Keep existing Recent Learnings section unchanged, add Session Notes above it"
  - Or: Show template with both sections clearly separated

**What should have happened**:
1. I'm executing commit-context skill
2. Commit-context Step 1 says "Run `/handoff` skill"
3. I should have invoked `/handoff` (not handoff-lite)
4. Or recognized that the user invoked `/commit-context` not me, so handoff is already the user's responsibility to call separately if needed
5. Instead I short-circuited to handoff-lite thinking I was being efficient

**Fix needed**: Clarify in commit-context whether "perform handoff" means:
- Agent invokes `/handoff` skill explicitly, OR
- User is expected to call `/handoff` separately before `/commit-context`, OR
- Handoff is optional and agent should update session.md mechanically if needed

Want me to restore the learnings section from git history?

## Issues Identified

### 1. commit-context Skill Ambiguity

**Current text**: "Step 1: Perform handoff - Run `/handoff` skill to update session.md"

**Problem**: Unclear whether:
- Agent should invoke `/handoff` as part of commit-context execution
- User should invoke `/handoff` separately before calling `/commit-context`
- Handoff is optional/contextual

**Agent behavior**: Interpreted as "I must invoke handoff now" → chose wrong skill variant

### 2. handoff-lite Template Structure Ambiguity

**Current design**: Provides complete template with "Session Notes" section

**Problem**:
- Says "NO FILTERING" and "Preserve everything mechanically"
- But template shows replacement structure, not merge/append structure
- Agent interpreted "use this template" as "replace existing structure"
- Result: Existing "Recent Learnings" section was deleted

**Expected behavior**: Keep existing learnings, add session notes as new section

### 3. Model Constraint Violation

**handoff-lite constraint**: "Target Model: Haiku (mechanical preservation)"

**Actual usage**: Sonnet invoked handoff-lite

**Why it happened**: Agent optimized for efficiency ("simple handoff, use lite version") without checking model constraints

### 4. Skill Selection Logic Flaw

**Pattern**: Agent saw "need to do handoff" → chose quickest/simplest option

**Missing check**: Is this skill appropriate for current model?

**Result**: Model-specific skill used by wrong model tier

## Recommendations for Design Session

### Fix 1: commit-context Handoff Clarification

**Current**:
```
1. **Perform handoff**
   - Run `/handoff` skill to update session.md
```

**Option A - Explicit delegation**:
```
1. **Perform handoff**
   - Invoke `/handoff` skill explicitly (not handoff-lite)
   - This updates session.md with completed work context
   - Required before commit to keep session.md synchronized
```

**Option B - Make optional**:
```
1. **Check if handoff needed**
   - If session.md needs updating (significant work completed), invoke `/handoff`
   - Skip if session already updated or work is trivial
```

**Option C - Remove from commit-context**:
```
(Remove handoff step entirely)

Add to skill description:
"Note: This skill does NOT update session.md. Use `/handoff` separately if needed before committing."
```

### Fix 2: handoff-lite Template Clarity

**Current template header**:
```
Use this embedded template:
```

**Proposed change**:
```
Update session.md using this structure. PRESERVE existing "Recent Learnings" section:

[Template with explicit note:]
## Session Notes
[Raw observations - DO NOT replace existing learnings]

## Recent Learnings
[PRESERVE EXISTING SECTION - Do not modify]
```

**Alternative**: Add explicit merge instruction before template

### Fix 3: Model Constraint Enforcement

**Options**:

A. **Skill-level check**: Add model constraint validation in skill execution
B. **Description emphasis**: Make "Target Model: Haiku" more prominent in skill frontmatter
C. **Naming convention**: Rename to `handoff-haiku` to make constraint explicit

### Fix 4: Skill Invocation Pattern

**Issue**: Agent chose wrong skill variant during commit-context execution

**Root**: commit-context says "run /handoff" but agent invoked different skill

**Fix**: commit-context should either:
- Name specific skill variant: "Invoke `/handoff` (not handoff-lite or other variants)"
- Or provide selection criteria: "Invoke `/handoff` (Sonnet/Opus) or `/handoff-lite` (Haiku only)"

## Open Questions

1. **Is handoff part of commit-context workflow?**
   - User expectation: separate `/handoff` before `/commit-context`?
   - Or: commit-context handles handoff automatically?

2. **When should handoff-lite be used?**
   - Only by Haiku model in orchestrator context?
   - Never by user-invoked commands?
   - Should it be hidden from user-facing skill list?

3. **Template merge semantics**
   - Should "use this template" mean replace or augment?
   - How to make merge/preserve behavior explicit?
   - Should template show complete target structure or delta?

4. **Model tier skill routing**
   - Should there be automatic routing (invoke `/handoff` → routes to handoff-lite if Haiku)?
   - Or explicit skills per tier with clear naming?
   - How to prevent cross-tier invocation?

## Proposed Experiment

Test these hypotheses:
1. Rename `handoff-lite` → `handoff-haiku` (makes constraint explicit)
2. Update commit-context to say "Invoke `/handoff` skill (Sonnet/Opus use standard handoff, Haiku uses handoff-haiku)"
3. Add to handoff-lite/handoff-haiku: "PRESERVE existing 'Recent Learnings' section. Add 'Session Notes' above it."
4. Test with actual Haiku model to verify template interpretation

## Next Actions

1. Restore session.md from git history (recover learnings)
2. Perform proper `/handoff` with Sonnet
3. Commit corrected session.md
4. Design session to address all 4 issues identified above
