# Learnings Consolidation: Requirements

Replace manual `/remember` invocation with automated consolidation during handoff.

## Current State

- learnings.md: append-only, 80-line soft limit
- Manual: user runs `/remember` when approaching limit
- `/remember` consolidates to permanent docs (fragments/, decisions/)

## Design Discussion (2026-02-05)

### Trigger Condition

**Rejected: "Separate periodic task"** — Not actionable. No scheduler/cron in Claude Code.

**Accepted: Conditional during handoff** — Check threshold, consolidate only if exceeded.

### Time Unit: Git-Active Days

**Problem with calendar days:**
- 22-hour manic coding sprint with 12 `/clear`s = still one logical session
- Two-week vacation shouldn't age learnings
- **Critical:** Operator can take vacation — calendar time is meaningless

**Solution: Git-active days**
- A calendar day with at least one commit = 1 active day
- Measurement: `git log --format='%ad' --date=short | sort -u`
- Immune to: context resets, vacations, weekends, sporadic work

**For learning age:**
1. `git blame -C -C` → date learning was added (follows renames)
2. Count git-active days since that date
3. Age = active days, not calendar days

### Two-Test Model

**Trigger test:** Should we start consolidation?
- File size threshold (150+ lines)
- Active days since last consolidation (14+ active days = staleness)
- Minimum batch available (3+ entries meeting freshness)

**Freshness test:** Should this specific learning be consolidated?
- Entry age ≥ 7 active days (proven validity)
- Applied per-entry, independent of trigger

**Separation rationale:** Trigger decides IF to consolidate. Freshness decides WHAT to consolidate. Different concerns, different thresholds.

### Threshold Values

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Size trigger | 150 lines | Safety valve for burst periods |
| Staleness trigger | 14 active days | Forgotten maintenance detection |
| Freshness threshold | 7 active days | Learnings prove validity over time |
| Minimum batch | 3 entries | Below this, overhead not worth it |

**Constraint:** Staleness (14) > freshness (7) to avoid immediate re-triggering.

### Aging Period Purpose

Learnings need time to prove themselves:
- Some learnings turn out wrong or situational
- Tuesday's learning may be invalidated by Thursday's work
- Aging filter: only learnings that remain relevant get promoted

## Resolved Questions

| Question | Resolution |
|----------|------------|
| Model selection | Sonnet — sufficient for consolidation judgment |
| Batch size minimum | 3 entries — below this, overhead exceeds value |
| Cooldown period | Replaced with staleness trigger (14 active days) |
| Failure handling | Escalate, don't silently fail |

## Sub-Agent Pattern

**Constraint:** Sub-agents cannot use Skill tool.

**Solution:** Agent references skill via prolog. Skill content injected into agent system prompt at runtime (not embedded in agent definition).

**Report location:** `tmp/consolidation-report.md` (not plan-specific path)

**Output format:** Markdown (cheaper, better for agent consumption than JSON)

## Pre-Consolidation Checks

**Supersession detection:**
- Newer entry contradicts older on same topic → drop older
- Implementation: keyword overlap + negation patterns
- Only consolidate final state

**Contradiction detection:**
- Entry contradicts existing content in target file → escalate
- Safety check — contradictions require human judgment

**Redundancy detection:**
- Entry brings no new information → drop from batch
- Implementation: agent-based keyword scoring
- **Fallback:** Embedding model if agent detection unreliable

## Memory Refactoring

**Anti-pattern:** "Make room" by archiving/deleting old content. Leads to progressive information loss.

**Correct pattern:**
1. Remember agent encounters target file at 400-line limit
2. Remember continues with other entries, reports limit to orchestrator
3. Orchestrator spawns refactor agent
4. Refactor agent splits file (creates new headers/files)
5. Memory-index validator autofixes entry locations
6. Remember processes remaining entries

**Key insight:** Only need to create headers for new files. Memory-index validation script handles index consistency automatically.

**In scope:** Memory refactoring agent is part of this design.

## Git Handling

**Merge commits:** Normal workflow, not edge case. Script must handle multi-parent commits.

**File renames:** Handled via `git blame -C -C` flag.

## Handoff Review Gap

**Gap:** Step 4 of handoff appends learnings without validation. Incomplete/incident-specific learnings can enter staging without review.

**Partial safety:** Pre-consolidation checks (contradiction, redundancy) catch some issues.

**Full solution:** Deferred to `handoff-validation` plan.

## Implementation Components

1. **`agent-core/bin/learning-ages.py`** — Age calculation (git blame + active days)
2. **`agent-core/agents/remember-task.md`** — Consolidation agent (prolog skill reference)
3. **`agent-core/agents/memory-refactor.md`** — File splitting agent
4. **Handoff skill update** — Trigger test + delegation
5. **Remember skill update** — Learnings quality criteria
6. **Tests** — Age calculation, triggers, detection checks

## Required Skills for Planning

Load before planning phase:
- `plugin-dev:skill-development` — Remember skill update
- `plugin-dev:agent-development` — Agent definitions (remember-task, memory-refactor)

## Related

- Pending task in session.md: "Automate learnings consolidation"
- Current manual process: `/remember` skill
- Target files: `agent-core/fragments/*.md`, `agents/decisions/*.md`
- Dependency: `handoff-validation` plan (for upstream learnings quality)
