# Session Handoff: 2026-01-31

**Status:** Commit RCA fixes implemented and committed. Two pending design tasks added for plan workflow improvements.

## Completed This Session

**Commit RCA fixes — implemented directly (bypassed runbook creation):**
- Design refinement: moved `git add` from plan skills to prepare-runbook.py (single fix point, script owns artifact knowledge)
- Design refinement: removed "agent-core:" prefix from submodule commits (redundant inside submodule repo)
- Design refinement: clean-tree contract in prepare-runbook.py (appended to generated agents, not baseline templates — quiet-task serves dual purpose)
- Point 0 assessment: 5 edits across 4 files, all surgical and independent → implement directly
- Implementation: all 5 fixes applied exactly as designed
  - Fix 1: Submodule awareness in commit skill (agent-core/skills/commit/SKILL.md)
  - Fix 2: Artifact staging in prepare-runbook.py (subprocess import, git add before return)
  - Fix 3: Orchestrator stop rule strengthened (agent-core/skills/orchestrate/SKILL.md, contradictory scenario deleted)
  - Design doc updated with revision trail
  - learnings.md updated with correct pattern
- Vet review: 0 critical, 0 major, 0 minor issues — ready
- Commits: 17d78d7 (submodule), 69885be (parent) — Fix 1 applied successfully (submodule first, pointer staged, parent committed)

**Lightweight delegation discussion:**
- User observation: commit-rca-fixes was good case for lightweight delegation
- Middle tier need identified: between direct execution and full runbook
- Discovery problem: quiet-task/tdd-task exist but no workflow surfaces them as option
- Pending task added: design lightweight delegation tier

**Plan workflow fast paths discussion:**
- User noted: direct implementation path should be formalized in plan-adhoc and plan-tdd
- Pattern demonstrated: Point 0 assessment → implement → vet → fixes → commit
- Pending tasks added: design updates for both plan skills

## Pending Tasks

- [ ] **Design plan-adhoc: formalize direct implementation fast path** — Point 0 → implement → vet → fixes → handoff/commit. Update skill with explicit pattern | opus
- [ ] **Design plan-tdd: add direct execution and lightweight delegation fast paths** — Similar to plan-adhoc, plus lightweight delegation option. Update skill with patterns | opus
- [ ] **Resume workflow-controls orchestration (steps 2-7)** — `/orchestrate workflow-controls` | sonnet | restart
- [ ] **Implement ambient awareness** — `/plan-adhoc plans/ambient-awareness/design.md` | sonnet
- [ ] **Create /reflect skill** — deviation detection → RCA → fix → handoff/commit automation. Load plugin-dev skills first | opus
- [ ] **Insert skill loading in design docs** — design skill should load relevant plugin-dev skills when topic involves hooks/agents/skills | sonnet
- [ ] **Update workflow skills: pbcopy next command** — commit/handoff STATUS display copies next command to clipboard | sonnet
- [ ] **Add "go read the docs" checkpoints** — partially addressed by design-work.md rule | sonnet
- [ ] **Design runbook identifier solution** — `/design plans/runbook-identifiers/problem.md` | opus
- [ ] **Create design-vet-agent** — dedicated opus agent for design review, artifact-return pattern | opus
- [ ] **Add execution metadata to step files** — step files declare dependencies and execution mode | sonnet
- [ ] **Orchestrator scope consolidation** — delegate checkpoint phases in orchestrate skill | sonnet
- [ ] **Design lightweight delegation tier** — surface quiet-task/tdd-task as middle ground between direct execution and full runbook. Discovery problem: capability exists but no workflow/skill presents it as an option | opus

## Blockers / Gotchas

**Commit-rca-fixes now active:**
- Fix 3 (orchestrator stop rule) prevents dirty-state rationalization
- Fix 2 (artifact staging) ensures prepare-runbook.py artifacts are staged
- Fix 1 (submodule awareness) prevents submodule pointer drift

**Hook changes require session restart:**
- UserPromptSubmit hook (Step 7 of workflow-controls runbook) won't activate until Claude Code restarts
- Test all shortcuts after restart: `s`, `x`, `xc`, `r`, `h`, `hc`, `ci`, `d:`, `p:`

**UserPromptSubmit hook input field name unverified:**
- Design doc says `prompt`, hook-dev skill docs say `user_prompt`
- Runbook currently uses `prompt` — may need correction during execution

## Next Steps

Two design tasks for workflow improvements (plan-adhoc and plan-tdd fast paths), then resume workflow-controls orchestration from step 2.

---
*Handoff by Sonnet. Commit RCA fixes implemented and active.*
