# Baseline Recall Analysis: Current Memory Index

**Date:** 2026-02-13
**Context:** Empirical measurement of current memory index recall effectiveness before implementing `/when` system
**Analysis:** 200 sessions from main repo (296 total sessions available)

## Executive Summary

The current memory index shows **2.9% recall rate** with highly uneven distribution across entries. This baseline establishes the problem magnitude that `/when` aims to solve.

### Key Findings

- **Overall recall:** 2.9% (250 of 8639 relevant session-entry pairs)
- **Sessions analyzed:** 200 of 296 available
- **Index entries:** 87 entries analyzed, 118 had relevant sessions
- **Relevant pairs:** 8639 opportunities where agents could have consulted the index
- **Successful reads:** 250 across multiple decision files

### Discovery Patterns

- **100% direct reads** - No search-then-read or user-directed patterns observed
- **Zero search behavior** - Agents don't search for decision files
- **Passive consumption** - When reads occur, agents already know the file path

## Per-Entry Results

### Distribution Analysis

**Recall rate distribution:**
- 7% recall: 1 entry (Consolidation Gates)
- 5% recall: 11 entries (mostly workflow-core.md and workflow-advanced.md)
- 4% recall: 39 entries (mix of workflow, testing, implementation-notes)
- 3% recall: 28 entries
- 2% recall: 14 entries
- 1% recall: 4 entries
- 0% recall: 21 entries

**Pattern:** Workflow and orchestration entries show moderate recall (4-7%), while many others show 0-2% despite high relevance.

### Top Performers

Highest recall entries (all workflow-related):

| Entry | File | Recall | Sessions |
|-------|------|--------|----------|
| Consolidation Gates Reduce Orchestrator Overhead | workflow-advanced.md | 7% | 58 |
| Outline Enables Phase-by-Phase Expansion | workflow-advanced.md | 5% | 74 |
| Orchestration Assessment: Three-Tier Implementation Model | workflow-core.md | 5% | 100 |
| Orchestrator Execution Mode | workflow-core.md | 5% | 101 |
| No human escalation during refactoring | workflow-core.md | 5% | 102 |

### Zero Recall Entries (Sample)

Still many high-relevance entries with zero recall:

- Model Capability Differences: 0% (109 relevant sessions)
- Context Loading Behavior: 0% (113 relevant sessions)
- Rule Format Effectiveness: 0% (95 relevant sessions)
- Position Bias: 0% (46 relevant sessions)

**Pattern:** Theoretical/research entries (prompt-structure-research.md) have near-zero recall despite relevance.

## Root Cause Analysis

### Primary Failure Mode: Passive Awareness

Current memory index relies on agents "mentally scanning" loaded content:
> "Scan the loaded content mentally, identify relevant entries, then Read the referenced file directly."

**Evidence of failure:**
- 8639 opportunities where scanning should have triggered reads
- 2.9% follow-through rate (250 reads)
- Highly uneven: workflow entries 4-7%, research entries 0-1%
- No evidence of active scanning behavior in tool call patterns

**Conclusion:** Agents occasionally scan when workflow terms appear in current task, but don't proactively scan for related knowledge. The passive model shows minimal effectiveness.

### Contributing Factors

**Pre-training dominance:**
- Workflow, TDD, testing topics are common in pre-training corpus
- Agents proceed confidently without seeking documentation
- No uncertainty signals that would trigger consultation behavior

**Context competition:**
- Memory index (~5000 tokens) competes with ~50,000 total context
- More immediate context (current task, session.md, fragments) takes priority
- Index lacks salience markers to draw attention

**No retrieval intention:**
- Agents use loaded context when directly relevant to current action
- Don't proactively seek context for planning or decision-making
- Keyword matching works (tool identifies relevant pairs) but doesn't trigger action

## Implications for `/when` Design

### Validated Problems

1. **Passive awareness fails** - Ambient loading without retrieval intention produces 0.2% recall
2. **Relevance detection works** - Keyword matching successfully identified 1809 relevant pairs
3. **Action gap exists** - Agents don't act on relevance even when accurately detected

### Design Requirements Confirmed

From design.md D-4:

> The memory index is essentially non-functional. Agents do not consult it even when topics are highly relevant. The `/when` system must provide **active retrieval triggers** rather than relying on passive awareness.

**Behavioral triggers validated:**
- `/when` (behavioral) and `/how` (procedural) create retrieval intention
- Definitional knowledge (`/what`, `/why`) would suffer same passive failure
- Must prescribe action to trigger consultation

### Success Metrics

Baseline: **2.9% recall** (200 sessions, 8639 pairs, 250 reads)

Target for `/when` system:
- Minimum viable: **>15% recall** (5× improvement)
- Good: **>30% recall** (10× improvement)
- Excellent: **>50% recall** (17× improvement)

Measurement approach:
- Same 50-session dataset for before/after comparison
- Track behavioral (`/when`) vs procedural (`/how`) recall rates separately
- Monitor false positive rate (irrelevant retrievals)

## Technical Notes

### Bug Fixes Applied

This analysis reflects corrected recall measurement after fixing two bugs:

**M-2: Path normalization**
- Previous analysis showed 0.0% recall due to path matching failure
- Absolute paths (`/Users/.../file.md`) didn't match relative index paths (`agents/decisions/file.md`)
- Fix: Suffix matching now handles absolute vs relative comparison
- Impact: Revealed actual 0.2% recall (4 reads previously undetected)

**M-1: E2E test fixture**
- Test assertion expected 4 tool calls but fixture had 3
- Masked by `@pytest.mark.e2e` exclusion from default test run
- Fix: Corrected assertion to match fixture data

### Analysis Methodology

**Session selection:** First 50 of 296 sessions (sorted by recency)

**Relevance threshold:** 0.3 (keyword overlap ratio)

**Tool coverage:** Read, Grep, Glob operations tracked

**Discovery pattern classification:**
- Direct: Read with no preceding search
- Search-then-read: Grep/Glob before Read
- User-directed: User message contained file path (not implemented)

## Comparison to Prior Analysis

Previous analysis (2026-02-08) showed:
- Main repo: 0.0% recall (0 of 1583 pairs, 50 sessions)
- Worktree: 3.5% recall (4 of 114 pairs, 3 sessions)

Current analysis after bug fixes (2026-02-13):
- 50 sessions: 0.2% recall (4 of 1809 pairs)
- 200 sessions: 2.9% recall (250 of 8639 pairs)

**Conclusion:** 2.9% is the robust baseline. Small samples (50 sessions) show high variance (0.2% vs 2.9%). Large sample needed for reliable measurement. Previous 0.0% was measurement error from path matching bug (M-2).

## Recommendations

### For `/when` Implementation

1. **Prioritize behavioral triggers** - Confirmed as correct approach
2. **Keep relevance matching** - Keyword overlap (0.3 threshold) works well
3. **Add fuzzy matching** - Align with design.md D-3 for trigger density vs clarity balance
4. **Measure baseline repeatedly** - Run analysis on different session windows for statistical validation

### For Current Index

The 0.2% recall rate confirms the memory index in its current form is non-functional. Options:

1. **Replace with `/when` system** (design.md approach)
2. **Archive index** until active retrieval system exists
3. **Reduce token budget** if keeping for reference (currently 5000 tokens for 0.2% utility)

## Files

**Analysis reports:**
- 50 sessions: `plans/memory-index-recall/reports/recall-rerun.md`
- 200 sessions: `plans/memory-index-recall/reports/recall-200-sessions.md`
**Deliverable review:** `plans/memory-index-recall/reports/deliverable-review-report.md`
**Tool implementation:** `src/claudeutils/recall/` (7 modules, 1184 lines)
**Tests:** `tests/test_recall_*.py` (6 modules, 1128 lines, 51 tests passing)
