# Continuation Prepend (Subroutine Calls)

## Problem

After continuation passing lands, skills can consume and tail-call the next entry in a chain. But a skill cannot invoke another skill as a subroutine — inserting work *before* the existing chain resumes.

Example: `/orchestrate` completes a phase checkpoint and needs `/commit` to run before continuing to the next phase — but the user's continuation chain (`/handoff --commit, /commit`) must be preserved afterward.

This is a subroutine call pattern, not recursion. The invoking skill does not re-enter itself.

## Mechanism

Purely additive. Skills prepend entries to the continuation before consuming:

```
/orchestrate has: [/handoff --commit, /commit]
  Needs /commit for checkpoint first.
  Prepend: [/commit, /handoff --commit, /commit]
  Consume /commit → tail-call with [/handoff --commit, /commit]
  Chain resumes normally.
```

## Protocol Extension

The consumption protocol (from continuation-passing design §Consumption Protocol) gains one optional step:

```
Current:
  1. Read continuation
  2. If empty → stop
  3. Consume first entry → tail-call with remainder

Extended:
  1. Read continuation
  2. If empty → stop
  3. If skill needs a subroutine: prepend entries to continuation
     - Existing entries remain in original order (append-only invariant)
     - Prepend only — never remove, reorder, or modify existing entries
  4. Consume first entry from (possibly modified) list → tail-call with remainder
```

Backward-compatible: skills that don't prepend skip step 3.

## Constraint

**Append-only for existing entries.** The user's original chain plus default exits form an immutable suffix. Skills may only add work *before* it. This preserves user intent and prevents chain hijacking.

## No Infrastructure Changes

- Hook parser: unchanged (builds initial chain)
- Transport format: unchanged (`[CONTINUATION: ...]` in args)
- Frontmatter schema: unchanged
- Single-skill invocations: unchanged

The extension is purely protocol-level — a paragraph added to each cooperative skill's continuation section.

## Scope

- Update §Consumption Protocol in each cooperative skill's continuation section (~1 line addition per skill)
- Add integration test: skill prepends subroutine, chain resumes correctly
- Update `agent-core/fragments/continuation-passing.md` protocol reference

## Dependencies

Requires continuation-passing to be complete (all 15 steps).
