# Memory Management Module

---
author_model: claude-opus-4-5-20251101
semantic_type: workflow
expansion_sensitivity: medium
target_rules:
  strong: 4-6
  standard: 8-10
  weak: 10-14
---

## Semantic Intent

Agent documentation must be maintained as the project evolves. Rules should be tiered
by importance, budgeted for token efficiency, and updated based on session learnings.

---

## Critical (Tier 1)

### Rule Budgeting

Target: AGENTS.md (~40 rules) + role file, total <= 150 rules. Fewer is better.
Budget is a hard constraint.

### Tiering for Position Bias

Structure documents with critical rules at start (primacy bias), optional guidance at
end (recency bias). Middle position is weakest.

- Tier 1 (~20%, start): Violations cause immediate problems. Few, non-negotiable.
- Tier 2 (~60%, middle): Important for quality. Most rules live here.
- Tier 3 (~20%, end): Nice-to-have, edge cases, style preferences.

---

## Important (Tier 2)

### Model-Appropriate Wording

Strong models: Concise, one sentence per rule.
Weak models: Explicit step-by-step with numbered lists and warning symbols.
Don't assume inference for weak models.

### When to Update Documentation

Update after:
- Discovering a workflow improvement
- Identifying a missing constraint
- Resolving a compliance failure
- User explicitly requests changes

### What to Update

Update: AGENTS.md, START.md, role files, rule files.
Do NOT update: README.md, test files, plan files.

---

## Preferred (Tier 3)

### Maintenance Heuristics

- Promote rules after repeated violations
- Demote rules that apply only to edge cases
- Delete rules made obsolete by project evolution

### Documentation Principles

Precision over brevity - rules must be unambiguous.
Examples over abstractions - show, don't just tell.
Constraints over guidelines - "do not" beats "try to avoid".
