# Remaining Workflow Items

Workflow improvements identified during RCA that weren't captured in workflow-rca-fixes.

## Requirements

### Functional Requirements

**FR-1: Reflect skill produces pending tasks**
The `/reflect` skill's exit paths currently produce inline fixes (Exit Path 1) or prose fix descriptions in RCA reports (Exit Path 2, step 4: "Document fix tasks for user"). RCA findings should produce structured pending task entries (`- [ ] **Task Name** — command | model`) that can be scheduled and tracked via session.md, not prose descriptions buried in reports.

Acceptance criteria:
- Exit Path 2 writes pending tasks to session.md (or outputs them in session.md task format)
- Exit Path 3 (partial RCA) similarly produces pending tasks for upstream fix + RCA resumption
- Task format matches session.md conventions (name, command, model, restart flag)
- Existing RCA report output preserved — tasks supplement, don't replace the report

**FR-2: Tool-batching Task parallelization guidance**
`agent-core/fragments/tool-batching.md` covers Read/Edit batching (14 lines) but has no guidance for Task tool parallel launches. The learning "Sequential Task launch breaks parallelism" (from orchestrate-evolution analysis, line 82) needs codification.

Acceptance criteria:
- tool-batching.md includes Task tool section with parallel launch pattern
- Covers: when to batch (independent inputs, no inter-agent deps), how to batch (single message with multiple Task calls), anti-pattern (sequential launch when inputs are ready)
- Example showing parallel vs sequential Task dispatch

**FR-3: Orchestrator delegate resume**
No general mechanism exists for the orchestrator to resume delegates with incomplete work. The orchestrate-evolution design (D-3) covers resume for dirty-tree remediation specifically. This requirement is about the broader pattern: when any delegate is interrupted, stopped, or returns incomplete results, the orchestrator should resume it using the Task tool `resume` parameter rather than relaunching fresh.

Acceptance criteria:
- Orchestrate skill documents resume-before-relaunch pattern
- Covers: agent ID tracking (save from Task dispatch), resume decision criteria (context size heuristic), fresh-launch fallback
- Pattern applicable to both step agents and vet/review agents

**FR-4: Agent output optimization**
Agent definitions contain verbose output instructions (summarize, report to user, write summary) that conflict with the quiet execution pattern (write to file, return filepath). Several agents already have "Do NOT provide summary" directives, but positive-language summarize/report instructions still appear in agent bodies, creating contradictory signals.

Acceptance criteria:
- Audit all `agent-core/agents/*.md` for positive summarize/report language that conflicts with quiet execution
- Remove or replace instructions that tell agents to summarize findings in return messages
- Preserve "write report to file" instructions (those are correct)
- Preserve "Do NOT provide summary" directives (those are correct)

**FR-5: Commit skill simplification**
Three commit skill mechanisms add complexity without proportional value:
- **Gate A (handoff freshness):** Checks session.md staleness, can trigger `/handoff`. Handoff timing should be user's decision, not forced by commit skill. The `xc`/`hc` shortcuts already chain handoff+commit when the user wants both.
- **Gate B (vet coverage):** Currently boolean (any report exists?), not true coverage ratio (1:1 artifact:report). A boolean check provides weak assurance — it passes if any report exists regardless of which artifacts were reviewed. The orchestrate-evolution design embeds vet into the orchestration loop, making a commit-time vet gate redundant for planned work.
- **Branching after precommit:** Post-precommit branching logic adds decision paths. Simplify to linear flow.

Acceptance criteria:
- Gate A removed — commit skill does not check session.md freshness or invoke `/handoff`
- Gate B removed or simplified — commit skill does not check for vet reports (vet enforcement moves to orchestration and vet-requirement.md fragment)
- Post-precommit flow simplified to linear: validate → draft → stage → commit → status

### Out of Scope

- Orchestrate evolution — separate plan (`plans/orchestrate-evolution/`), designed, ready for `/runbook`. FR-3 (delegate resume) may overlap with orchestrate-evolution D-3; reconcile during planning.
- Parallel orchestration — deferred to `plans/parallel-orchestration/`
- vet-fix-agent behavioral changes — out of scope per orchestrate-evolution design
- New reflect skill exit paths beyond task output format change

### Dependencies

- FR-3 overlaps with orchestrate-evolution FR-2 (post-step remediation resume). Planning should determine whether FR-3 is a standalone change to the delegation fragment or subsumed into orchestrate-evolution execution.
- FR-5 (Gate B removal) assumes vet enforcement lives in orchestration loop + vet-requirement.md, not commit skill. Validate this assumption against current vet-requirement.md fragment.

### Open Questions

- Q-1: Should FR-3 (delegate resume) be implemented as a standalone delegation.md update or deferred into orchestrate-evolution? The pattern is general (applies to all orchestration), but the primary consumer is the orchestrate skill rewrite.
- Q-2: For FR-4 (agent output), what's the scope — all agents, or only agents that are dispatched by the orchestrator? Non-orchestrated agents (e.g., test-hooks) may legitimately report to users.

### References

- `plans/orchestrate-evolution/orchestrate-evolution-analysis.md` — gap analysis identifying Gate B boolean check (line 79), sequential Task launch anti-pattern (line 82)
- `plans/orchestrate-evolution/design.md` — D-3 post-step remediation with resume pattern
- `agent-core/skills/reflect/SKILL.md` — current reflect skill with 3 exit paths
- `agent-core/skills/commit/SKILL.md` — current commit skill with Gate A, Gate B
- `agent-core/fragments/tool-batching.md` — current batching guidance (Read/Edit only)
