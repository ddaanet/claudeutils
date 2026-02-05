# Learnings Consolidation: Outline

## Approach

Integrate automated consolidation check into `/handoff` skill. During handoff, check learnings.md against thresholds. If triggered, delegate to a consolidation sub-agent that runs `/remember` logic.

**Key insight:** This is NOT a new consolidation mechanism — it's automated invocation of existing `/remember` logic with scoped input (only entries meeting freshness criteria).

**Agent pattern:** Sub-agent references skill via prolog. Skill content injected into agent system prompt at runtime (not embedded in agent definition).

## Key Decisions

1. **Trigger location:** Insert check between handoff step 4 (learnings append) and step 5 (size check)
   - Rationale: Learnings are finalized, natural point before session size advice

2. **Age calculation mechanism:** Python script using git blame + git log
   - `git blame -C -C` per learning header line (follows renames)
   - Git log --date=short → unique active days since commit date
   - **Output format:** Markdown (cheaper, better for agent consumption than JSON)
   - **Time unit:** Always "active days" (calendar days with commits), never calendar days
   - **Merge commits:** Normal workflow, not edge case — script must handle multi-parent commits

3. **Consolidation model:** Sonnet (current `/remember` model)
   - Sonnet has been sufficient for consolidation judgment
   - Keep consistency with existing skill

4. **Sub-agent pattern:** Prolog skill reference + quiet execution
   - Agent definition references skill via prolog (skill content injected at runtime)
   - Writes report to `tmp/consolidation-report.md`
   - Returns filepath on success, escalation message on issue

5. **Minimum batch size:** 3 entries
   - Below 3: Overhead not worth it (agent spawn + context switch)

## Two-Test Model

**Trigger test:** Should we start consolidation?
- File size threshold (line count)
- Active days since last consolidation (staleness)
- Minimum batch available

**Freshness test:** Should this specific learning be consolidated?
- Entry age in active days (proven validity)
- Applied per-entry, independent of trigger

**Separation rationale:** Trigger decides IF to consolidate. Freshness decides WHAT to consolidate. Different concerns, different thresholds.

## Threshold Behavior

**Size-triggered consolidation (150+ lines):**
- Trigger: File exceeds size limit
- Freshness filter: Select entries with age ≥ 7 active days
- Batch: Oldest entries first, up to batch size that reduces below threshold
- If insufficient aged entries: escalate (don't consolidate young entries)

**Staleness-triggered consolidation (14+ active days since last consolidation):**
- Trigger: File unchanged for N active days (suggests forgotten maintenance)
- Freshness filter: Same (≥ 7 active days)
- Batch: All qualifying entries
- **Note:** Staleness threshold (14) > freshness threshold (7) to avoid immediate re-triggering

**Freshness threshold:** 7 active days minimum age before consolidation eligible

## Pre-Consolidation Checks

**Supersession detection:**
- Before consolidating, scan entries for semantic overlap
- If newer entry contradicts older entry on same topic, drop the older (it's been corrected)
- Implementation: keyword overlap + negation patterns ("don't", "not", "instead of")
- Only consolidate final state, not superseded entries

**Contradiction detection:**
- Check if entry contradicts existing content in target file
- If contradiction detected: escalate (don't silently overwrite)
- Safety check — contradictions require human judgment

**Redundancy detection:**
- Check if entry brings no new information (semantically equivalent to existing knowledge)
- If redundant: drop from batch (no value in consolidating duplicates)
- Implementation options:
  - Keyword/phrase overlap scoring (agent-based)
  - Embedding similarity threshold (if agent detection unreliable)
- **Open question:** Can agents reliably detect redundancy? If not, embedding model may be needed.

## Partial Failure Handling

Remember agent may need to escalate for some learnings:

| Situation | Handling |
|-----------|----------|
| Target file at 400-line limit | Triggers refactoring flow (not a blocker to remember) |
| Learning too vague/incident-specific | Escalate — bad learning passed through handoff review |
| Learning contradicts existing doc | Escalate — requires human judgment |
| Superseded by newer learning | Drop from batch (not a failure, just filtering) |
| Redundant with existing knowledge | Drop from batch (no value added) |

**Pattern:** Remember reports escalations. Orchestrator handles coordination.

## Memory Refactoring Flow

**Anti-pattern:** "Make room" by archiving/deleting old content from target file. Leads to progressive information loss.

**Correct pattern (part of consolidation process):**
1. Remember agent encounters target file at 400-line limit
2. Remember continues with other entries, reports target limit to orchestrator
3. Orchestrator spawns refactor agent for the full target file
4. Refactor agent splits file into logical sections (creates new headers/files)
5. Memory-index validator autofixes entry locations to match new file structure
6. Remember agent processes remaining entries with updated targets

**Key insight:** Only need to create headers for new files. Memory-index validation script handles index consistency automatically.

## Scope Boundaries

**In scope:**
- Age calculation script (git blame -C -C + git log, active days)
- Handoff skill modification (trigger test + delegation)
- Remember-task agent definition (prolog skill reference)
- Memory-refactor agent definition (split files, create headers)
- Threshold configuration (size, staleness, freshness)
- Batch size determination (count entries meeting freshness threshold)
- Remember skill update (guidance on learnings to keep in staging)
- Supersession detection (drop outdated entries)
- Contradiction detection (escalation safety check)
- Redundancy detection (drop duplicates)
- Handoff review gap and recovery pattern (documented below)

**Out of scope:**
- Embedding-based redundancy detection (explore if agent detection insufficient)

## Handoff Review Gap and Recovery Pattern

**Gap identified:** Step 4 of handoff appends new learnings without validation. Incomplete/incident-specific learnings can enter staging without review.

**Recommended handoff modification:**
1. Insert validation before append: Check new learnings for completeness
   - Principle-level: Does it apply beyond specific case?
   - General rule: State the constraint, not the incident
   - Example bad: "Edited skill without loading it" → Example good: "Always load skill context before editing"

2. Remember agent's pre-consolidation checks provide partial safety (catches conflicts, redundancy)

3. Full solution deferred to `handoff-validation` plan (requires continuation-passing architecture)

**For this plan:** Document pattern in Remember skill update section, include examples of learnings that should be rejected/revised before append.

## Implementation Components

1. **`agent-core/bin/learning-ages.py`** — Calculate active-day age per learning, active days since last consolidation
   - Input: learnings.md file path
   - Output: Markdown with learning headers and ages (agent-friendly)
   - Algorithm: `git blame -C -C` per H2 header → extract commit date → count active days since
   - Handles: merge commits (normal workflow), file renames (via -C flag)

2. **`agent-core/agents/remember-task.md`** — Sub-agent with prolog skill reference
   - Prolog: References `/remember` skill (content injected at runtime)
   - Input: Filtered learnings list with age metadata
   - Output: Report to `tmp/consolidation-report.md` OR escalation message
   - Includes: supersession detection, contradiction detection, redundancy detection

3. **`agent-core/agents/memory-refactor.md`** — Sub-agent for file splitting
   - Input: Target file path at limit
   - Process: Analyze content, identify logical sections, create new files with headers
   - Output: List of new files created
   - Relies on: memory-index validator to autofix index entries

4. **Handoff skill update** — Insert trigger test, delegate on threshold
   - Location: Between step 4 (learnings append) and step 5 (size check)
   - Logic: Call learning-ages.py, check thresholds, filter by freshness, delegate if batch ≥ 3

5. **Remember skill update** — Guidance on staging vs consolidation + learnings quality validation
   - Add section: "Learnings quality criteria" with examples:
     - Principle-level learnings (apply broadly) ✅
     - Incident-specific learnings (narrow case, not generalizable) ❌
     - Meta-learnings (rules about rules) → avoid unless behavioral constraint required
   - Add section: "Learnings to keep in staging" (recency, cross-references, pending validation)
   - Add section: "Learnings to reject before append" (incident-specific, contradicts existing, too narrow)
   - Clarify: When to consolidate vs when to defer

6. **Tests** — Age calculation, trigger logic, freshness filtering, detection checks
   - Test age calculation with mock git repo (including merge commits)
   - Test trigger conditions (size, staleness, minimum batch)
   - Test freshness filtering (exclude entries < 7 active days)
   - Test supersession detection (newer contradicts older)
   - Test contradiction detection (entry vs target file)
   - Test redundancy detection (entry equivalent to existing)

## Parameters Summary

| Parameter | Purpose | Measurement | Default |
|-----------|---------|-------------|---------|
| File line count | Size trigger | `wc -l` | 150 lines |
| Entry count | Batch sizing | Count `## ` headers | N/A |
| Active days since last consolidation | Staleness trigger | Git log on learnings.md | 14 active days |
| Entry age (per entry) | Freshness filter | Git blame per header | 7 active days |
| Minimum batch size | Overhead threshold | Config | 3 entries |

## Risk Assessment

**Low risk:** Automates existing manual process; failure = skip consolidation (handoff continues)

**Git handling:** Merge commits are normal workflow — script must handle multi-parent commits correctly. File renames handled via `git blame -C -C` flag.

**Semantic analysis risk:** Supersession/contradiction/redundancy detection relies on agent judgment. May have false positives/negatives. Mitigation: conservative matching (prefer escalation over silent errors). Embedding model fallback for redundancy if agent detection insufficient.

## Requirements Traceability

| Requirement | Component |
|-------------|-----------|
| Automated consolidation during handoff | Handoff skill modification |
| Git-active days measurement | learning-ages.py script |
| Tiered thresholds (size + staleness) | Trigger test logic |
| Freshness threshold (7 active days) | Freshness filter |
| Minimum batch size (3 entries) | Batch threshold check |
| Sub-agent with skill reference | remember-task.md prolog pattern |
| Supersession detection | Pre-consolidation check |
| Contradiction detection | Pre-consolidation safety check |
| Redundancy detection | Pre-consolidation check |
| Memory refactoring | memory-refactor.md agent |
| Handoff review gap (noted) | Handoff Review Gap section + Remember skill quality criteria |

**All requirements mapped to implementation components.**
