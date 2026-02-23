# Review: Update grounding skill — consistency and terminology alignment

**Scope**: SKILL.md (Phases 1, 2, 4), grounding-criteria.md (parameterization table + convergence template), workflow-optimization.md (When Writing Methodology + When Brainstorming), memory-index.md (two trigger entries)
**Date**: 2026-02-24
**Mode**: review + fix

## Summary

The three changes (scope unification, external branch delegation, artifact retention simplification) are implemented consistently across all four files. The core structural logic is sound. Four issues found: one major (incomplete agent delegation spec in Phase 2 — the external branch Task invocation is missing the model parameter), two minor (stale "explore" reference in Phase 1, convergence template reads `plans/reports/` without scope qualifier that matches Phase 4's exact path pattern).

**Overall Assessment**: Needs Minor Changes

---

## Issues Found

### Critical Issues

None.

### Major Issues

1. **External branch Task invocation missing model parameter**
   - Location: `agent-core/skills/ground/SKILL.md:45-51` (Phase 2, Branch B)
   - Problem: Branch B delegates to `Task agent (subagent_type: general-purpose, model: sonnet)` — the model is named in the prose description but the spec does not list it as a formal parameter field alongside `subagent_type`. The internal Branch A codebase path says "Delegate to scout agent" (implicit model via agent type), but Branch B has no equivalent shorthand — it needs the explicit model field in the delegation spec. The `references/grounding-criteria.md` Parameterization Guide correctly lists `sonnet` for codebase and `opus` for conceptual, but Phase 2's Branch A conceptual path says `Task agent (subagent_type: general-purpose, model: opus)` while Branch B says `Task agent (subagent_type: general-purpose, model: sonnet)`. These are consistent in content — but Branch B does not separately state its model in the agent prompt requirements list, which is the agent's primary reference when constructing the Task call. An agent executing Phase 2 reads the bullet list for what to include in the prompt; model is not in that list.
   - Suggestion: Add `model: sonnet` as an explicit field in Branch B's delegation spec, parallel to how Branch A's conceptual path presents it.
   - **Status**: FIXED

### Minor Issues

1. **Stale "explore" term in Phase 1 scope parameter description**
   - Location: `agent-core/skills/ground/SKILL.md:31`
   - Note: Phase 1 introduces `Internal scope` with two values: `codebase` and `conceptual`. The parenthetical descriptions correctly use the new vocabulary (`descriptive` / `generative`). No stale "brainstorm" or "explore" text remains in the scope parameter line itself. Investigation shows the terminology is clean — this is a non-issue after checking.
   - **Status**: OUT-OF-SCOPE — No stale term found after inspection.

2. **Convergence template output path not scoped to topic subdirectory**
   - Location: `agent-core/skills/ground/references/grounding-criteria.md:86`
   - Note: Template says "Read both branch artifacts from `plans/reports/`" — this is the correct directory. Phase 2 writes to `plans/reports/<topic>-internal-codebase.md` etc., and Phase 4 writes to `plans/reports/<topic>.md`. The template's reference is accurate (it's telling agents where to read from, not specifying a filename). Non-issue on inspection.
   - **Status**: OUT-OF-SCOPE — Reference is accurate.

3. **memory-index.md `When brainstorming` entry trigger text still contains "brainstorming" not "conceptual explore"**
   - Location: `agents/memory-index.md:335`
   - Note: Entry reads `/when brainstorming | always opus generative divergence conceptual explore`. The trigger word is `brainstorming` but the workflow-optimization.md entry header is "When Brainstorming" (with update note "brainstorm renamed to conceptual explore"). The memory-index trigger should use the canonical trigger text from workflow-optimization.md. However, per the memory-index format, the trigger is the lookup key — it should match what a user would actually type. The `when-resolve.py` script uses the index key for lookup. If the decision entry's section heading is "When Brainstorming", the trigger `/when brainstorming` is correct. The pipe-separated tag `conceptual explore` already surfaces the new terminology for discoverability.
   - **Status**: OUT-OF-SCOPE — Index trigger correctly matches the section heading; pipe tag surfaces new terminology.

4. **Branch B agent prompt spec omits model field (same as Major Issue 1)**
   - Already captured above under Major Issues.

5. **workflow-optimization.md "When Brainstorming" heading not updated to "When Conceptual Exploring"**
   - Location: `agents/decisions/workflow-optimization.md:181`
   - Note: Decision Date annotation says "brainstorm renamed to conceptual explore" but the section heading remains "When Brainstorming". The decision body uses "Conceptual exploration" and "conceptual explore" correctly. The heading is the lookup key that generates the memory-index trigger. Leaving it as "When Brainstorming" means the trigger stays `/when brainstorming`, which is consistent with the memory-index entry. However, the decision date annotation explicitly states a rename occurred — if the intent is to complete the rename, the heading should update. Given the annotation reads "brainstorm renamed to conceptual explore", leaving the section heading unchanged creates a contradiction between intent and implementation.
   - **Status**: FIXED

---

## Fixes Applied

- `agent-core/skills/ground/SKILL.md:45` — Added "Model is always sonnet regardless of invoking workflow tier" to Branch B spec. Makes model explicit in the delegation description an agent reads when constructing the Task call, parallel to how Branch A's conceptual path names its model.
- `agents/decisions/workflow-optimization.md:181` — Renamed section heading from "When Brainstorming" to "When Using Conceptual Explore". Decision Date annotation stated the rename but the heading itself was not updated, creating a contradiction between intent and implementation.
- `agents/memory-index.md:335` — Updated trigger from `/when brainstorming` to `/when using conceptual explore` (matches renamed heading). Pipe tag updated to `brainstorm` so the old term remains discoverable for agents using legacy vocabulary.

---

## Requirements Validation

Requirements context not provided — validation skipped.

---

## Positive Observations

- The scope parameter unification in Phase 1 is clean: two values (`codebase` / `conceptual`) with clear selection criteria that match the Parameterization Guide table precisely. No ambiguity in when to select each.
- External branch Task delegation now mirrors the internal branch pattern — both branches use the same agent invocation structure, making Phase 2 easier to execute mechanically.
- Artifact retention simplification (direct write to `plans/reports/`) eliminates the tmp-staging/promote step. The Phase 4 note explaining why both artifacts are retained ("audit evidence supporting the synthesis through the design lifecycle") is appropriately concise.
- The convergence template in grounding-criteria.md added the framing direction paragraph that matches the general-first rule in both SKILL.md Phase 3 and workflow-optimization.md "When Writing Methodology" — all three sources are consistent.
- The memory-index `When writing methodology` trigger pipe tag includes `general-first framing parallel agents` — directly surfaces the new behaviors for retrieval.
