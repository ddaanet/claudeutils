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

**Solution: Git-active days**
- A calendar day with at least one commit = 1 active day
- Measurement: `git log --format='%ad' --date=short | sort -u`
- Immune to: context resets, vacations, weekends, sporadic work

**For learning age:**
1. Git blame → date learning was added
2. Count git-active days since that date
3. Age = active days, not calendar days

### Threshold Model: Tiered (Option D)

**Soft trigger:** 50+ lines AND entries > 7 active days
- Normal operation respects aging
- Only consolidates entries that have proven themselves

**Hard cap:** 150 lines regardless of age
- Safety valve for burst periods ("furious manic coding")
- Forces consolidation of oldest entries
- ~3000 tokens worst case (acceptable context cost)

**Rationale:**
- Age-based primary: provides natural filtering (learnings prove validity over time)
- Size-based secondary: prevents unbounded growth during intense work
- Tiered approach: soft threshold for quality, hard threshold for limits

### Aging Period Purpose

Learnings need time to prove themselves:
- Some learnings turn out wrong or situational
- Tuesday's learning may be invalidated by Thursday's work
- Aging filter: only learnings that remain relevant get promoted

**Tunable via limit adjustment** — want more aging? increase limit. Faster consolidation? decrease.

### Arguments Addressed

| Initial Concern | Resolution |
|-----------------|------------|
| Aging period needed | Tunable via size limit, not manual vs automatic |
| Fresh context advantage | Irrelevant — both approaches use clean context (manual runs in new session, automated uses sub-agent) |
| Judgment quality | Previously recommended sonnet — worth reconsidering if opus needed |

### Additional Parameters (Brainstormed)

**Most actionable:**
- Minimum batch size — don't consolidate 1-2 entries (overhead not worth it)
- Supersession detection — newer learning invalidates older, only consolidate final state
- Consolidation cooldown — don't consolidate if last was < N active days ago

**Lower priority:**
- Target file capacity — decision files have 400-line hard limits
- Section grouping — batch learnings going to same destination
- Contradiction detection — requires semantic comparison (expensive)

## Open Questions

1. **Model selection:** Is sonnet sufficient or should consolidation use opus?
2. **Batch size minimum:** What's the threshold below which consolidation isn't worth it?
3. **Cooldown period:** How many active days between consolidation runs?
4. **Failure handling:** What if consolidation agent fails mid-run?

## Implementation Sketch

During `/handoff`:
1. Check learnings.md age via git blame
2. Check learnings.md size via line count
3. If soft trigger (50+ lines AND 7+ active days) OR hard trigger (150+ lines):
   - Spawn consolidation sub-agent
   - Agent reads learnings.md, decision files, fragments
   - Agent moves aged entries to permanent locations
   - Agent removes consolidated entries from learnings.md
4. If below thresholds, skip consolidation

## Related

- Pending task in session.md: "Automate learnings consolidation"
- Current manual process: `/remember` skill
- Target files: `agent-core/fragments/*.md`, `agents/decisions/*.md`
