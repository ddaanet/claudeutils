# Learnings Consolidation: Design

Automate learnings consolidation during handoff, replacing manual `/remember` invocation.

## Requirements

**Source:** `plans/learnings-consolidation/requirements.md`

**Functional:**
- FR-1: Trigger consolidation conditionally during handoff — addressed by handoff skill modification (§ Implementation Component 4)
- FR-2: Calculate learning age in git-active days — addressed by `learning-ages.py` script (§ Implementation Component 1)
- FR-3: Two-test model (trigger + freshness) — addressed by trigger logic in handoff skill (§ D-3, Implementation Component 4)
- FR-4: Supersession detection (newer contradicts older) — addressed by remember-task agent (§ D-5)
- FR-5: Contradiction detection (entry vs target file) — addressed by remember-task agent (§ D-5)
- FR-6: Redundancy detection (entry duplicates existing) — addressed by remember-task agent (§ D-5)
- FR-7: Memory refactoring when target file at limit — addressed by memory-refactor agent (§ Implementation Component 3, D-6)
- FR-8: Sub-agent with skill reference pattern — addressed by remember-task agent with embedded protocol (§ Implementation Component 2)
- FR-9: Learnings quality criteria in remember skill — addressed by skill update (§ Implementation Component 5)

**Non-functional:**
- NFR-1: Failure = skip consolidation, handoff continues — handoff catches exceptions, logs, proceeds
- NFR-2: Consolidation model = Sonnet — remember-task agent uses sonnet
- NFR-3: Report to `tmp/consolidation-report.md` — quiet execution pattern

**Out of scope:**
- Embedding-based redundancy detection — explore if agent detection insufficient
- Full handoff validation — deferred to `handoff-validation` plan

## Architecture

### Component Overview

```
Handoff Skill (modified)
  Step 4: Append learnings (unchanged)
  Step 4b: Check invalidated learnings (unchanged)
  NEW Step 4c: Consolidation trigger test
    ├── Run learning-ages.py → age data (markdown)
    ├── Check trigger conditions (size OR staleness)
    ├── Filter entries by freshness (≥7 active days)
    ├── Check minimum batch (≥3 entries)
    └── If triggered: delegate to remember-task agent
  Step 5: Session size check (unchanged)

learning-ages.py (new script)
  Input: agents/learnings.md
  Output: Markdown with entry headers, ages, last-consolidation staleness

remember-task agent (new)
  Protocol: Embeds /remember skill consolidation steps
  Input: Filtered entry list with age metadata
  Pre-checks: Supersession, contradiction, redundancy
  Execution: Consolidate qualifying entries per /remember protocol
  Output: Report to tmp/consolidation-report.md

memory-refactor agent (new)
  Input: Target file path at 400-line limit
  Execution: Split file into logical sections
  Post: memory-index validator autofixes entries
```

### Data Flow

1. Handoff reaches step 4c → runs `learning-ages.py agents/learnings.md`
2. Script outputs markdown table: `## Entry Title` → `age: N active days`
3. Handoff skill evaluates trigger conditions against thresholds
4. If triggered, builds filtered entry list (entries ≥7 active days, oldest first)
5. Delegates to `remember-task` agent with entry list + age metadata
6. Agent runs pre-consolidation checks, consolidates, writes report
7. Handoff reads report filepath, continues to step 5

## Key Design Decisions

### D-1: Insertion Point in Handoff

**Decision:** New step 4c between existing step 4b (invalidated learnings check) and step 5 (session size check).

**Rationale:** Learnings are finalized after step 4/4b. Consolidation before size check ensures size advice reflects post-consolidation state. Step numbering: 4c avoids renumbering existing steps.

**Alternative rejected:** After step 5 — size check would give stale advice.

### D-2: Script Output Format

**Decision:** Markdown output from `learning-ages.py`, not JSON.

**Rationale:** Agent consumption is the primary use case. Markdown is cheaper to parse, doesn't need escaping, and agents process it natively. Matches pattern established by other bin scripts.

**Format:**
```markdown
# Learning Ages Report

**File lines:** 101
**Last consolidation:** 12 active days ago
**Total entries:** 15
**Entries ≥7 active days:** 8

## Tool batching unsolved
- Age: 22 active days
- Added: 2026-01-14

## "Scan" triggers unnecessary tools
- Age: 18 active days
- Added: 2026-01-18

...
```

### D-3: Trigger Evaluation in Skill vs Script

**Decision:** Script calculates ages. Handoff skill evaluates trigger conditions.

**Rationale:** Threshold values are policy decisions that belong in the skill (easy to tune, visible in skill definition). The script is a data provider — it computes ages, the skill decides what to do with them.

**Threshold values (configured in handoff skill step 4c):**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Size trigger | 150 lines | Safety valve for burst periods |
| Staleness trigger | 14 active days | Forgotten maintenance detection |
| Freshness threshold | 7 active days | Learnings prove validity over time |
| Minimum batch | 3 entries | Below this, overhead not worth it |

### D-4: Agent Pattern — Embedded Skill Protocol

**Decision:** Remember-task agent embeds the relevant `/remember` skill protocol sections directly in its agent definition body. Agent body contains both the consolidation protocol and execution-specific instructions.

**Rationale:** Sub-agents spawned via Task tool may have "Skill" listed in their tools (e.g., `quiet-task.md`, `tdd-plan-reviewer.md` include it), but the Skill tool's reliability in sub-agent context is unverified for this use case. Embedding the protocol directly avoids this uncertainty and ensures the agent always has the consolidation logic available without runtime skill loading.

**Constraint from requirements:** Requirements specify "prolog skill reference" as the intent. Since Claude Code has no formal prolog injection mechanism, the implementation embeds the relevant protocol sections directly in the agent definition, keeping them synchronized manually with the remember skill.

**Synchronization risk:** When the remember skill changes, the embedded protocol in `remember-task.md` must be updated manually. Planner should add a comment in the agent definition noting the source skill and version.

**Agent structure:**
```markdown
---
name: remember-task
description: ...
model: sonnet
color: green
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---

# Consolidation Protocol
[Extracted from /remember skill steps 1-4a]
<!-- Source: agent-core/skills/remember/SKILL.md -->

# Context
[Injected: filtered entry list with age metadata]

# Additional Instructions
[Pre-consolidation checks, batch handling, reporting]
```

### D-5: Pre-Consolidation Check Strategy

**Decision:** Agent-based semantic analysis with conservative matching. Prefer escalation over silent errors.

**Checks (in order):**

| Check | Input | Action on match | Implementation |
|-------|-------|-----------------|----------------|
| Supersession | Entry pairs in batch | Drop older entry | Keyword overlap + negation patterns |
| Contradiction | Entry vs target file content | Escalate to orchestrator | Agent reads target, compares semantics |
| Redundancy | Entry vs target file content | Drop from batch | Keyword/phrase overlap scoring |

**Conservative bias:** When uncertain, escalate rather than silently dropping or consolidating.

**Rationale:** False negatives (missing a conflict) are worse than false positives (unnecessary escalation). Human judgment resolves ambiguity cheaply; silent data corruption is expensive.

### D-6: Memory Refactoring Trigger

**Decision:** Refactoring is reactive, not preemptive. Triggered only when remember-task encounters a target file at the 400-line limit.

**Flow:**
1. Remember-task attempts to consolidate entry to target file
2. Target file at 400-line limit → remember-task skips that entry, continues with others, reports limit in `tmp/consolidation-report.md`
3. Handoff skill reads report, identifies file-limit escalation
4. Handoff skill spawns memory-refactor agent for the specific target file
5. Refactor agent splits file, creates new headers
6. `validate-memory-index.py` autofix handles index consistency
7. Handoff skill spawns a second remember-task invocation with only the skipped entries (those that failed due to file limit)

**Retry scope:** Only entries that were skipped due to the file-limit condition are retried. Entries that were successfully consolidated or dropped (superseded/redundant) in the first pass are not re-processed.

**Rationale:** Preemptive splitting adds complexity without clear benefit. The reactive pattern leverages existing infrastructure (memory-index validator autofix).

### D-7: Failure Handling

**Decision:** Fail gracefully — consolidation failure must not block handoff.

**Implementation:** Handoff step 4c wraps delegation in try/catch. On failure:
1. Log error to stderr
2. Note in handoff output: "Consolidation skipped: [reason]"
3. Continue to step 5

**Failure modes:**

| Failure | Handling |
|---------|----------|
| `learning-ages.py` fails | Skip consolidation, log error |
| No entries meet freshness | Skip (not a failure, just no work) |
| Batch < minimum | Skip (threshold not met) |
| Remember-task agent error | Skip, report in handoff output |
| Target file contradiction | Agent escalates in report |
| Target file at limit | Trigger refactor flow |

## Implementation Components

### 1. `agent-core/bin/learning-ages.py`

**Purpose:** Calculate git-active-day age per learning entry.

**Interface:**
```
Input:  agents/learnings.md (path argument, default)
Output: Markdown report to stdout
Exit:   0 on success, 1 on error (to stderr)
```

**Algorithm:**
1. Parse learnings.md — extract H2 headers (entries) after preamble (skip first 10 lines, matching `validate-learnings.py` pattern)
2. For each H2 header line:
   - `git blame -C -C -- agents/learnings.md` → extract commit hash + date for that line
   - Handle: merge commits (multi-parent), file renames (via `-C -C` flag)
3. Count git-active days from entry date to today:
   - `git log --format='%ad' --date=short` → set of dates with commits
   - Active days = count of unique commit dates between entry date and today
4. Calculate staleness: active days since most recent consolidation
   - Heuristic: Find most recent commit where H2 headers were removed from learnings.md (consolidation evidence — entries get removed when consolidated to permanent docs)
   - Method: Walk `git log -p -- agents/learnings.md` looking for diffs with `-## ` lines (removed H2 headers)
   - Fallback: If no consolidation evidence found, report staleness as "unknown (no prior consolidation detected)"

**Output format:** See D-2 above.

**Testing considerations:**
- Mock git operations for unit tests
- Test with merge commits (multi-parent)
- Test freshness calculation edge cases (0 active days, entry added today)
- Test staleness when no previous consolidation exists

### 2. `agent-core/agents/remember-task.md`

**Purpose:** Autonomous consolidation agent that follows the remember protocol.

**Agent definition:**

```yaml
name: remember-task
description: |
  Use this agent when delegating learnings consolidation during handoff.
  Executes the /remember protocol on a filtered set of learnings entries.
  Reports results to tmp/consolidation-report.md.
model: sonnet
color: green
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
```

**System prompt content (body):**
- Role: Consolidation agent executing the remember protocol
- Input specification: Receives filtered entry list with age metadata in task prompt
- Pre-consolidation checks: Supersession, contradiction, redundancy (see D-5)
- Consolidation protocol: Extracted from remember skill steps 1-4a (understand, route, draft, apply+verify)
- Discovery mechanism updates: Memory index, CLAUDE.md/@-refs, rules entries
- Retention: Keep 3-5 most recent learnings in staging
- Report format: Write detailed report to `tmp/consolidation-report.md`
- Return: Filepath on success, error message on failure
- Escalation: Report contradictions and target-file limits in report

**Key difference from interactive `/remember`:** This agent operates on a pre-filtered batch (only entries meeting freshness threshold), not the entire learnings file. It doesn't need to evaluate what to consolidate — that decision is already made by the handoff trigger logic.

### 3. `agent-core/agents/memory-refactor.md`

**Purpose:** Split oversized documentation files into logical sections.

**Agent definition:**

```yaml
name: memory-refactor
description: |
  Use this agent when a documentation target file exceeds 400 lines
  and needs to be split into logical sections. Triggered by remember-task
  when it encounters a file at the limit.
model: sonnet
color: yellow
tools: ["Read", "Write", "Edit", "Grep", "Glob"]
```

**System prompt content (body):**
- Role: Documentation refactoring agent
- Input: Target file path at/near 400-line limit
- Process:
  1. Read target file, analyze content sections
  2. Identify logical split points (by H2/H3 topic boundaries)
  3. Create new files with appropriate headers
  4. Move content to new files, preserving formatting
  5. Update original file with cross-references to new files
  6. Run `validate-memory-index.py` (autofix mode) to update index entries
- Constraints:
  - Create headers for new files only (index validator handles consistency)
  - Preserve all content (splitting, not summarizing)
  - New files should be 100-300 lines each (balanced split)
- Output: List of files created/modified

### 4. Handoff Skill Modification

**Location:** `agent-core/skills/handoff/SKILL.md`

**Change:** Insert step 4c between existing steps 4b and 5.

**Step 4c content:**

```markdown
### 4c. Consolidation Trigger Check

Run `agent-core/bin/learning-ages.py agents/learnings.md` to get age data.

**Trigger conditions (any one sufficient):**
- File exceeds 150 lines (size trigger)
- 14+ active days since last consolidation (staleness trigger)

**If triggered:**
1. Filter entries with age ≥ 7 active days
2. Check batch size ≥ 3 entries
3. If sufficient: delegate to remember-task agent with filtered entry list
4. Read report from returned filepath
5. If report contains escalations (contradictions, file limits):
   - Note contradictions in handoff output under Blockers/Gotchas
   - For file limits: delegate to memory-refactor agent for the target file, then re-invoke remember-task with only the skipped entries

**If not triggered or batch insufficient:**
- Skip consolidation (no action needed)
- Continue to step 5

**On error:**
- Log to stderr, note in handoff output
- Continue to step 5 (consolidation failure must not block handoff)
```

**Tool constraints update:** Current handoff `allowed-tools`: `Read, Write, Edit, Bash(wc:*), Skill`. Add `Bash(agent-core/bin/learning-ages.py:*)` for age script and `Task` for agent delegation (remember-task, memory-refactor).

### 5. Remember Skill Update

**Location:** `agent-core/skills/remember/SKILL.md`

**Changes:**

**Add section: "Learnings Quality Criteria"**

```markdown
### Learnings Quality Criteria

**Principle-level (consolidate):** ✅
- States a general constraint or pattern
- Applies beyond the specific incident
- Example: "Always load skill context before editing"

**Incident-specific (reject/revise):** ❌
- Describes what happened, not what to do
- Narrow to one case, not generalizable
- Example: "Edited skill without loading it" → revise to principle

**Meta-learnings (use sparingly):**
- Rules about rules — only when behavioral constraint required
- Example: "Soft limits normalize deviance" → consolidate if recurrent
```

**Add section: "Staging Retention Guidance"**

```markdown
### Staging Retention Guidance

**Keep in staging (do not consolidate):**
- Entries < 7 active days old (insufficient validation)
- Entries with pending cross-references (depend on other work)
- Entries under active investigation

**Consolidate:**
- Entries ≥ 7 active days with proven validity
- Entries that have been applied consistently
- Entries referenced by multiple sessions

**Drop (remove from staging):**
- Superseded by newer entry on same topic
- Contradicted by subsequent work
- Incident-specific without generalizable principle
```

### 6. Tests

**Location:** `tests/test_learning_ages.py`

**Test categories:**

| Category | Tests |
|----------|-------|
| Parsing | Extract H2 headers from learnings.md, skip preamble (first 10 lines) |
| Age calculation | Mock git blame → extract dates, count active days between dates |
| Staleness | No prior consolidation (fallback), recent consolidation, edge cases |
| Trigger logic | Size threshold (149 vs 150 vs 151), staleness threshold, batch minimum |
| Freshness filter | Include ≥7, exclude <7, exactly 7 boundary |
| Integration | Full pipeline with mock git repo (including merge commits) |
| Error handling | Missing file, git not available, malformed learnings.md |

**Testing approach:** Mock git operations via subprocess patching. Create temporary learnings.md files with known content. Avoid dependency on real git history.

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agent-core/skills/handoff/SKILL.md` — current handoff protocol (insertion point)
- `agent-core/skills/remember/SKILL.md` — remember protocol (agent must embed)
- `agent-core/skills/remember/references/consolidation-patterns.md` — routing guidance
- `agent-core/bin/validate-learnings.py` — existing learnings validation patterns
- `agent-core/bin/validate-memory-index.py` — autofix patterns for index maintenance
- `plans/learnings-consolidation/reports/explore-current-workflow.md` — workflow map
- `plans/learnings-consolidation/reports/explore-agent-patterns.md` — agent definition patterns

**Required skills (planner must load):**
- `plugin-dev:skill-development` — remember skill update guidance
- `plugin-dev:agent-development` — agent definition structure (remember-task, memory-refactor)

**Additional research allowed:** Planner may explore `agent-core/agents/quiet-task.md` and `agent-core/agents/vet-agent.md` for agent body patterns.

## Requirements Traceability

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Yes | Implementation Component 4 (Handoff Skill Modification) |
| FR-2 | Yes | Implementation Component 1 (learning-ages.py), D-2 |
| FR-3 | Yes | D-3 (Trigger Evaluation), Implementation Component 4 |
| FR-4 | Yes | D-5 (Pre-Consolidation Check Strategy) |
| FR-5 | Yes | D-5 (Pre-Consolidation Check Strategy) |
| FR-6 | Yes | D-5 (Pre-Consolidation Check Strategy) |
| FR-7 | Yes | D-6 (Memory Refactoring Trigger), Implementation Component 3 |
| FR-8 | Yes | D-4 (Embedded Skill Protocol), Implementation Component 2 |
| FR-9 | Yes | Implementation Component 5 (Remember Skill Update) |
| NFR-1 | Yes | D-7 (Failure Handling) |
| NFR-2 | Yes | Implementation Component 2 (model: sonnet) |
| NFR-3 | Yes | Implementation Component 2 (report to tmp/consolidation-report.md) |

## Next Steps

Route to `/plan-adhoc` (general workflow — this is infrastructure/automation, not feature TDD).

Load `plugin-dev:skill-development` and `plugin-dev:agent-development` before planning.
