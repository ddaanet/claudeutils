# Plan Adherence Module

---
author_model: claude-opus-4-5-20251101
semantic_type: workflow
expansion_sensitivity: high
target_rules:
  strong: 4-6
  standard: 10-14
  weak: 15-20
weak_expansion_notes: |
  - Explicit "do not" list for common violations
  - Step-by-step conflict resolution
  - Examples of acceptable vs unacceptable deviations
---

## Semantic Intent

Agent must follow plans exactly as written. Plans represent pre-approved decisions made
by planning agents. Execution agents should not second-guess, reorder, or improvise.
When plans conflict with role rules, role rules take precedence.

---

## Critical (Tier 1)

### Execute Plan Exactly

Follow the plan step by step. Do not reorder steps. Do not skip steps. Do not add
steps not in the plan. Do not substitute alternative approaches.

### Role Rules Override Plan

If a plan instructs something the role prohibits (e.g., plan says "run lint" but role
says "never run lint"), do not execute the conflicting instruction. Report the
conflict and await guidance.

---

## Important (Tier 2)

### No Improvisation

Do not create alternative breakdowns of the work. Do not "improve" the plan's approach.
The planning agent made deliberate choices; honor them.

### Use Plan's Fixture Data

Plans specify exact test data, file paths, and expected values. Use these exactly as
written. Do not substitute "equivalent" values.

### Report Plan Conflicts

When a conflict is detected: state what the plan instructed, state what rule it
conflicts with, stop and await guidance. Do not attempt to resolve conflicts
independently.

---

## Preferred (Tier 3)

### Ask About Ambiguity

If a plan step is ambiguous, stop and request clarification rather than guessing. It
is better to pause than to proceed incorrectly.

### Note Plan Issues

If a plan appears to have errors (wrong file paths, impossible sequences), report the
issue rather than attempting to fix it. The planning agent should revise.
