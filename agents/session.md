# Session Handoff: 2026-01-30

**Status:** Two design documents created for skill improvements and recovery

## Completed This Session

**Diagnosed plan-tdd failure (broken feedback loop):**
- plan-tdd generates weak RED tests (structure-only assertions)
- review-tdd-plan checks GREEN prescriptiveness but not RED test quality
- tdd-task encourages stubs and embeds escalation evaluation at wrong tier
- No phase boundary functional review catches stubs mid-execution
- Vet catches problem but only after all 37 cycles (too late)

**Designed skill improvements across 10 files:**
- plan-tdd: assertion quality, happy path first, integration cycle verification, metadata validation, enhanced checkpoints
- review-tdd-plan: weak RED assertion detection, metadata count validation, empty-first warning
- tdd-task: remove stub guidance, remove escalation evaluation, add post-commit sanity check
- refactor agent (new): sonnet-level escalation table, script-first, architectural → opus
- orchestrate skill: post-step tree check, phase boundary functional review
- vet skill: design conformity and functional completeness dimensions
- plan-adhoc: minor success criteria guidance
- anti-patterns.md, patterns.md: new entries
- prepare-runbook.py: phase boundary markers

**Design documents created:**
- `plans/skill-improvements/design.md` — all skill changes, route: plan-adhoc
- `plans/claude-tools-recovery/design.md` — strengthen tests + wire implementations, route: plan-tdd

**CLAUDE.md updated:**
- Added skill location note: skills live in `agent-core/skills/`, symlinked from `.claude/skills/`, `just sync-to-parent` updates symlinks

## Pending Tasks

- [ ] **Execute skill improvements** — `/plan-adhoc` on `plans/skill-improvements/design.md`, then `/orchestrate`
- [ ] **Execute recovery** — `/plan-tdd` on `plans/claude-tools-recovery/design.md` (depends on skill improvements being applied first)

## Blockers / Gotchas

**Execution order matters:**
- Skill improvements MUST be applied before recovery
- Recovery dogfoods improved plan-tdd — validates the fixes

**Python 3.14 Incompatibility:**
- litellm dependency uvloop doesn't support Python 3.14 yet
- Solution: Reinstall with `uv tool install --python 3.13 'litellm[proxy]'`

**Mock Patching Pattern:**
- Patch at usage location, not definition location
- Example: `patch("claudeutils.account.state.subprocess.run")`

## Key Design Decisions Made

- **No review-adhoc-plan skill** — vet improvements sufficient, plan-adhoc failures less severe
- **No human escalation during refactoring** — design decisions already made, opus handles architectural
- **Escalation moved from haiku to sonnet** — new refactor agent evaluates severity
- **Mandatory phase boundary checkpoints** — catches stubs before they compound
- **Post-commit sanity check in both tdd-task and orchestrate** — defense in depth
- **Happy path first, not empty case** — prevents stub accumulation from degenerate-first ordering
- **Remove stub guidance from tdd-task** — test drives complexity, no permission to stub needed
- **Option 2 for recovery** (strengthen tests) — dogfoods improved skills, provides coverage guarantees

## Reference Files

**New designs:**
- `plans/skill-improvements/design.md` — 10 files to change, infrastructure/refactoring
- `plans/claude-tools-recovery/design.md` — 4 phases (R0-R4), test-first recovery

**Previous analysis:**
- `plans/claude-tools-rewrite/runbook-analysis.md` — root cause analysis
- `plans/claude-tools-rewrite/reports/vet-review-2026-01-30.md` — full vet review
- `plans/claude-tools-rewrite/design.md` — original architecture (still valid)

**Skills to modify:**
- `agent-core/skills/plan-tdd/SKILL.md` + references/
- `agent-core/skills/review-tdd-plan/SKILL.md`
- `agent-core/skills/orchestrate/SKILL.md`
- `agent-core/skills/vet/SKILL.md`
- `agent-core/skills/plan-adhoc/SKILL.md`
- `agent-core/agents/tdd-task.md`
- `agent-core/agents/refactor.md` (new)
- `agent-core/bin/prepare-runbook.py`

---
*Handoff by Opus. Diagnosis complete, two designs created, pending execution.*
