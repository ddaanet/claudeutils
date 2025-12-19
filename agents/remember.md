---
name: remember
description: Documentation updates and rules maintenance
---

# Remember Skill

**First:** Read `AGENTS.md` if not already in context.

Governs project documentation maintenance and rules management.

---

## Documentation Update Rules

**Update:**
- `agents/USER_FEEDBACK_SESSION.md` - New user feedback with timestamp/context
- `agents/STEP*_COMPLETION.md` - Completion notes and handoff info

**Avoid:**
- Hardcoded counts - use `just test` for dynamic status
- Proactive documentation files unless explicitly requested

---

## Rules Budgeting System

**Target: AGENTS.md (~40) + skill file ≤ 150 rules. Fewer is better.**

### Progressive Disclosure

Sessions load AGENTS.md + one relevant skill file. Budget applies to the combination.

**Exception:** commit.md and handoff.md load at session end. Recency bias deprioritizes earlier task rules, so these are effectively budget-exempt (~80 effective rules).

### Three-Tier Structure (per skill file)

| Tier | % | Position | Purpose |
|------|---|----------|---------|
| 1 | 20% | Top | Critical - always follow |
| 2 | 60% | Middle | Important - most cases |
| 3 | 20% | Bottom | Optional - nice to have |

### Rule Maintenance

**Promote:** Repeated violations, consistent problems
**Demote:** Rarely referenced, edge cases only
**Delete:** Obsolete due to project evolution, replaced by better rule
