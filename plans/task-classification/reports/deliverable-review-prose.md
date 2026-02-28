# Deliverable Review: Task Classification Prose Artifacts

**Scope**: Agentic prose changes for task-classification plan
**Date**: 2026-02-28
**Baseline**: `plans/task-classification/outline.md` (D-1 through D-9)

## Summary

Seven prose files reviewed. The `/prime` skill is well-structured and D+B compliant. The handoff skill correctly implements the D-9 classification heuristic. The execute-rule.md changes accurately implement two-section display, graceful degradation, and `#execute` pickup. One major issue found: stale `--task` flag reference in execute-rule.md contradicts the actual CLI signature (positional argument) documented in the worktree skill. Two minor issues: residual "pending tasks" terminology in worktree skill Mode B, and a stale reference file within the worktree skill.

**Counts**: 0 Critical, 1 Major, 2 Minor

---

## Issues Found

### Critical Issues

None.

### Major Issues

### [Major] execute-rule.md references nonexistent `--task` flag
- **File:** `agent-core/fragments/execute-rule.md:226`
- **Axis:** Functional correctness
- **Description:** Line 226 states: "`-> <slug>` added by `_worktree new --task` when worktree created, removed by `_worktree rm`". The CLI uses a positional `TASK_NAME` argument, not a `--task` flag. The actual signature is `claudeutils _worktree new [TASK_NAME] [--branch TEXT] [--base TEXT]`. The worktree skill itself (SKILL.md:123) correctly documents this and explicitly notes "There is no `--task` flag — the task name is always positional." This is new content introduced by this branch (the pre-branch execute-rule.md had no `_worktree new` reference). An agent reading execute-rule.md would form an incorrect mental model of the CLI interface. Since the worktree skill's body text overrides at invocation time, the practical risk is limited to status-display contexts where the agent reasons about how markers get added — but the contradiction between two always-loaded fragments (execute-rule.md and project-tooling.md line 40, which also uses the stale `--task` form) creates a confusing signal.

### Minor Issues

### [Minor] Worktree skill Mode B uses stale "pending tasks" terminology
- **File:** `agent-core/skills/worktree/SKILL.md:50`, `:52`, `:64`
- **Axis:** Conformance (terminology consistency)
- **Description:** Mode B Step 1 says "identify all pending tasks and plan statuses." Step 2 says "For each pending task, extract the plan directory." Step 3 error message says "All pending tasks have dependencies or incompatible requirements." The corrector review (review.md, Recommendations) flagged this as scope OUT per outline.md Open Question 1. That assessment is correct — Mode B scan scope (whether to scan Worktree Tasks exclusively vs. all sections) is an unresolved design question. However, the residual "pending tasks" phrasing is a terminology inconsistency: the deliverable renamed "Pending Tasks" to "In-tree Tasks" everywhere else. Even if Mode B's scan scope remains broad, it should say "all tasks" or "tasks from both sections" rather than "pending tasks" (which implies a section that no longer exists). This is distinct from the scan scope question — it is purely a naming consistency issue within delivered prose.

### [Minor] Worktree skill reference file uses stale `--task` flag
- **File:** `agent-core/skills/worktree/references/branch-mode.md:15`, `:20`, `:23`
- **Axis:** Functional correctness (cross-reference consistency)
- **Description:** `branch-mode.md` references `--task` form three times: heading "Prefer `--task` Form", code block `claudeutils _worktree new --task "<task name>"`, and prose "The `--task` form automates all side effects." The main worktree skill body (SKILL.md:123) explicitly contradicts this: "There is no `--task` flag — the task name is always positional." This reference file predates the current branch — the stale content was not introduced here — but it creates a within-skill contradiction. Since reference files are loaded on-demand by agents, an agent following Mode A could reach this file and form an incorrect CLI invocation. Lower severity than the execute-rule.md issue because reference files are not always-loaded.

---

## Design Decision Conformance

| Decision | Status | Evidence |
|----------|--------|----------|
| D-1: `/prime` for ad-hoc plan work | Conformant | `prime/SKILL.md` scoped to ad-hoc; "What This Is Not" section explicitly excludes workflow optimization |
| D-2: No frozen artifact restriction | Conformant | Uses Read calls in Step 1, allowed-tools includes Read and Glob, no @ref injection |
| D-3: Chain-call `/recall` | Conformant | Step 2 invokes `Skill(skill: "recall")` with no explicit topic |
| D-3a: D+B compliance | Conformant | Step 1 anchors with `Glob: plans/<name>/*.md` then Read — concrete tool calls before any prose gate |
| D-4: Static classification, no move semantics | Conformant | execute-rule.md:215 "Classification is static — set at creation... No move semantics between sections"; handoff skill:80 "Classification is static"; worktree skill:44,71 describe add/remove marker, not move task |
| D-5: No backward migration | Conformant | execute-rule.md:93 "Old section name ('Pending Tasks') -> treat as 'In-tree Tasks'" |
| D-7: In-tree first, then Worktree in status | Conformant | execute-rule.md:24-33 shows In-tree section before Worktree section in STATUS format |
| D-8: `#execute` picks in-tree, `wt` picks worktree | Conformant | execute-rule.md:102 "start first in-tree task. ... Worktree tasks require `wt` setup — `x` does not pick them up"; worktree skill Mode A reads from Worktree Tasks |
| D-9: Classification heuristic | Conformant | handoff/SKILL.md:77-80 prescriptive for clear cases (plan dir + behavioral changes, opus, restart, parallel), defaults to in-tree when uncertain |

---

## Cross-Reference Consistency

| Term/Section | execute-rule.md | handoff/SKILL.md | handoff-haiku/SKILL.md | worktree/SKILL.md | operational-tooling.md |
|---|---|---|---|---|---|
| "In-tree Tasks" | Yes | Yes | Yes | N/A (reads from Worktree) | Yes |
| "Worktree Tasks" | Yes | Yes | Yes | Yes | Yes |
| Static classification | Yes (:215) | Yes (:80) | N/A | Yes (:44) | Yes (:67) |
| No move semantics | Yes (:215) | Yes (:80) | N/A | Yes (:44,131) | Yes (:67) |
| `→ slug` marker semantics | Yes (:221,226) | N/A | N/A | Yes (:44,71,131) | Yes (:67) |
| `#status` from filesystem | Yes (:47) | N/A | N/A | N/A | Yes (:67) |

No cross-reference inconsistencies in terminology or section naming across the delivered files, except the "pending tasks" residue in worktree Mode B noted above.

---

## Axis Assessment by File

### `agent-core/skills/prime/SKILL.md` (NEW)
- **Actionability**: Strong. Step 1 opens with Glob, then Read with explicit priority order and exclusion rule. Step 2 is a single Skill invocation. No interpretation needed.
- **Constraint precision**: Strong. Exclusion of `recall-artifact.md` is explicit. Priority order is enumerated. "What This Is Not" section sets clear boundaries.
- **Determinism**: Strong. Same plan directory produces same Glob results, same Read sequence, same `/recall` chain-call.
- **Scope boundaries**: Strong. IN/OUT clear via "What This Is Not" section. Agent knows to stop after `/recall` chain-call completes.

### `agent-core/fragments/execute-rule.md`
- **Actionability**: Strong for STATUS display (format template is concrete). Major finding on line 226 (`--task` flag) affects accuracy of the rules section but not agent behavior during status display.
- **Constraint precision**: Strong. Graceful degradation rules are enumerated with specific conditions and outputs.
- **Determinism**: Strong. Same session state produces same display format.
- **Scope boundaries**: Strong. `x` vs `wt` routing is explicit.

### `agent-core/skills/handoff/SKILL.md`
- **Actionability**: Strong. D-9 heuristic gives concrete criteria for each section. Command derivation table maps planstate to skill invocation mechanically.
- **Constraint precision**: Strong. "Default to In-tree when uncertain" eliminates ambiguity for edge cases.
- **Determinism**: Strong for clear cases (restart, opus, plan dir). Advisory for ambiguous cases by design (D-9 Open Question 2 recommendation).

### `agent-core/skills/handoff-haiku/SKILL.md`
- **Actionability**: Strong. MERGE semantics explicitly cover both sections. Template shows both sections.
- **Constraint precision**: Strong. "Follow the format defined in `execute-rule.md`" delegates format precision to the authoritative source.
- **Determinism**: Strong. Mechanical handoff — no judgment calls.

### `agent-core/skills/worktree/SKILL.md`
- **Actionability**: Strong for Mode A (reads from Worktree Tasks, adds marker). Mode B has minor terminology issue but step sequence is clear.
- **Constraint precision**: CLI signature note (line 123) is precise and explicitly corrects the stale `--task` form.
- **Determinism**: Strong. Mode A is fully deterministic. Mode B has agent judgment in dependency analysis (acceptable per design).

### `agents/decisions/operational-tooling.md`
- **Actionability**: N/A (decision record, not procedural).
- **Constraint precision**: Strong. Three failure modes enumerated with cross-reference to D-4.
- **Conformance**: Correct supersession date and updated pattern description.

### `agents/memory-index.md`
- **Actionability**: N/A (index entries, not procedural).
- **Conformance**: Both trigger phrase entries updated from "inline marker" to "two-section in-tree worktree static classification no move". Trigger phrases match the new decision content.

---

## Out-of-Scope Observations

These are not findings against the deliverable — they are pre-existing issues or deferred items noted for completeness:

- `agent-core/skills/reflect/SKILL.md:148,168` and `agent-core/skills/next/SKILL.md:19` reference "Pending Tasks" — flagged by corrector review as deferred cleanup.
- `agent-core/skills/prioritize/SKILL.md:23` references "Pending Tasks" — same category.
- `agent-core/fragments/project-tooling.md:40` uses stale `--task` flag form — predates this branch, not in scope.
- `agent-core/skills/worktree/references/branch-mode.md` stale `--task` references — noted as Minor finding above because it creates within-skill contradiction with new content on line 123.
- Mode B scan scope (Worktree Tasks only vs. all sections) — design Open Question 1, explicitly scope OUT.
