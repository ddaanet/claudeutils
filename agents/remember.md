---
name: remember
description: Documentation updates and rules maintenance
---

# Remember Skill

This skill governs how to maintain project documentation and manage the rules themselves.

---

## Documentation Update Rules

### When to Update Documentation

1. **Update `agents/USER_FEEDBACK_SESSION.md`** - Add new user feedback with timestamp and context
2. **Update `agents/STEP*_COMPLETION.md`** - Single file for both completion notes and handoff info
3. **Avoid hardcoded counts** - Run `just test` for status, don't maintain test counts in markdown

### What NOT to Document

🚫 **Don't:**
- Duplicate dynamic state (test counts, current status)
- Add unnecessary documentation files proactively
- Create README or docs unless explicitly requested

✅ **Do:**
- Update feedback files when user provides guidance
- Keep handoff files current during multi-step work
- Reference commands for dynamic info (`just test`)

---

## Rules Budgeting System

**Maximum 150 user rules total across all files. Fewer is better.**

### Three-Tier System

Rules within each skill file should follow this distribution:

| Tier | Percentage | Position in File | Purpose |
|------|------------|------------------|---------|
| 1 | 20% | Start of file | Critical - must always follow |
| 2 | 60% | Middle of file | Important - follow in most cases |
| 3 | 20% | End of file | Optional - nice to have |

### How to Apply Tiers

**Within each skill file:**
- Place most critical rules at the top (Tier 1)
- Middle section contains important rules that apply in most cases (Tier 2)
- End section has optional rules and style preferences (Tier 3)

**Example from code.md:**
- Tier 1: RED phase rules (must always run test before implementing)
- Tier 2: Type safety, linting standards (important but not workflow-breaking)
- Tier 3: Specific type annotation preferences (nice to have)

### Maintaining the Budget

**When to promote rules:**
- User repeatedly corrects violations of a lower-tier rule
- A pattern consistently causes problems

**When to demote rules:**
- A rule is rarely violated or referenced
- The rule applies only to specific edge cases

**When to archive/delete rules:**
- Rule hasn't been needed in 10+ sessions
- Rule is obsolete due to project evolution
- Replacing with a better, more general rule

**When adding new rules:**
- Remove lowest-tier rules to stay under 150 total
- Consider if the new rule can replace existing rules
- Evaluate if the rule is truly needed or just nice-to-have

### Rule Count by File

Track approximate rule counts to stay under budget:
- `AGENTS.md` core rules: ~30 rules
- `agents/code.md`: ~40 rules
- `agents/plan.md`: ~20 rules
- `agents/commit.md`: ~15 rules
- `agents/remember.md`: ~15 rules
- `agents/handoff.md`: ~10 rules
- **Headroom:** ~20 rules

*These are targets, not hard limits per file. The 150 total is what matters.*
