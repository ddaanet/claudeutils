# Session: Plugin Migration — Runbook Vetting + RCA (x2)

**Status:** All phases vetted (44 issues fixed). Ready for runbook assembly and execution.

## Completed This Session

**Retroactive vet reviews completed:**
- Phase 1: 4 minor issues fixed (validation improvements, complexity reassessment)
- Phase 2: 5 major, 5 minor fixed, 1 UNFIXABLE (consumer mode TODO marker format requires design decision)
- Phase 3: 3 major, 2 minor fixed (hooks.json format corrections, temp file path clarification)
- Phase 4: 3 major, 2 minor fixed (precommit validation, recipe extraction verification)
- Phase 5: 2 critical, 5 major, 4 minor fixed (hook validation reframing, NFR qualitative assessment)
- Phase 6: 1 critical, 1 major, 1 minor fixed — then REVERTED (vet error: validated against current state not execution-time state)

**Phase 6 vet error analysis:**
- Vet-fix-agent changed `just-help-edify-plugin.txt` → `just-help-agent-core.txt` (incorrect)
- Root cause: Validated against current filesystem instead of post-Phase 0 state (Phase 0 renames cache file)
- Error detected by orchestrator, manually reverted all 6 occurrences

**Two RCAs completed:**

**RCA #1: Sequential Task Launch (plans/reflect-rca-sequential-task-launch/rca.md)**
- Deviation: Launched Phase 1 vet, waited for completion, started Phase 2 sequentially instead of batching all 6 Task calls
- Root cause: Tool batching rule doesn't explicitly cover Task tool parallelization
- Wall-clock impact: ~14 min delay (sequential = sum(times) vs parallel = max(times))
- Learning added: Sequential Task launch breaks parallelism

**RCA #2: Vet-Fix-Agent Context-Blind Validation**
- Deviation: Phase 6 vet "fixed" correct references by validating against wrong state
- Root cause: No execution context provided in delegation prompt, no UNFIXABLE escalation protocol
- Phase 2 also had UNFIXABLE issue that didn't escalate (manual detection required)
- Learning added: Vet-fix-agent context-blind validation

## Pending Tasks

- [ ] **Strengthen commit Gate B coverage check** — Gate B is boolean (any report?) not coverage ratio (artifacts:reports 1:1) | sonnet
  - Commit skill Step 1 Gate B: count new/modified production artifacts, verify each has vet report
- [ ] **Review reflect skill: task output for skill/fragment fixes** — RCA should produce pending tasks for skill/fragment updates, not inline fixes, for context economy | sonnet
  - Current: reflect skill applies fixes in-session (Exit Path 1) consuming context budget
  - Better: produce tasks in session.md for separate session execution
- [ ] **Strengthen vet-fix-agent delegation pattern** — Add execution context provision and UNFIXABLE detection | sonnet
  - Sub-tasks:
    1. Add execution context to vet-fix-agent prompts (include phase dependencies, state transitions)
    2. Add UNFIXABLE detection to orchestrator (read report, grep for markers, escalate if found)
    3. Document vet-fix-agent limitations in memory-index.md (context-blind by default)
    4. Evaluate meta-review necessity (when should vet output be vetted?)
  - Analysis: plans/reflect-rca-sequential-task-launch/rca.md
- [ ] **Update tool-batching.md for Task tool parallelization** — Add explicit Task tool guidance with examples | sonnet
  - Add "Task Tool Parallelization" section to agent-core/fragments/tool-batching.md
  - Include example: vet 6 phase files in parallel (6 Task calls in single message)
  - Show anti-pattern (sequential launch) vs correct pattern (batched launch)
- [ ] **Run prepare-runbook.py and review** — Assemble phases into runbook.md, validate cycle numbering, review metadata | haiku
  - Command: `edify-plugin/bin/prepare-runbook.py plans/plugin-migration/runbook-outline.md` (requires `dangerouslyDisableSandbox: true`)
  - Ready to execute (vet task complete)

## Blockers / Gotchas

**Vet-fix-agent temporal reasoning limitation:**
- Agent validates against current filesystem state, not execution-time state
- Phase 6 error example: Current state has `agent-core`, but Phase 0 renames to `edify-plugin` before Phase 6 runs
- Mitigation: Provide execution context in delegation prompts (dependencies, state transitions)

**UNFIXABLE detection is manual:**
- Vet reports mark issues as UNFIXABLE but don't escalate
- Orchestrator must read report and grep for markers
- Phase 2 had UNFIXABLE issue (consumer mode TODO format) that went unnoticed until manual review

**Historical plan documentation scope:**
- 41 references in plans/ subdirectories need agent-core → edify-plugin update
- Phase 0 step 12 addresses this but decision needed on whether to update archived plans

## Reference Files

- **plans/plugin-migration/design.md** — Design with 8 components, 8 decisions (D-1 through D-8)
- **plans/plugin-migration/runbook-outline.md** — Complete outline (7 phases, 17 steps)
- **plans/plugin-migration/runbook-phase-{0-6}.md** — All phase files (all vetted)
- **plans/plugin-migration/reports/phase-{0-6}-review.md** — All vet reviews (44 total issues across all phases)
- **plans/reflect-rca-sequential-task-launch/rca.md** — RCA covering both deviations (Task parallelization + vet context issues)
