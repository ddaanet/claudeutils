# Baseline Recall Analysis: Current Memory Index

**Date:** 2026-02-13
**Context:** Empirical measurement of current memory index recall effectiveness before implementing `/when` system
**Analysis:** 50 sessions from main repo (296 total sessions available)

## Executive Summary

The current memory index shows **0.2% recall rate** with systematic failure across most entries. This baseline establishes the problem magnitude that `/when` aims to solve.

### Key Findings

- **Overall recall:** 0.2% (4 of 1809 relevant session-entry pairs)
- **Sessions analyzed:** 50 of 296 available
- **Index entries:** 87 entries analyzed
- **Relevant pairs:** 1809 opportunities where agents could have consulted the index
- **Successful reads:** 4 (all from `agents/decisions/testing.md`)

### Discovery Patterns

- **100% direct reads** - No search-then-read or user-directed patterns observed
- **Zero search behavior** - Agents don't search for decision files
- **Passive consumption** - When reads occur, agents already know the file path

## Per-Entry Results

### Non-Zero Recall Entries

Only 4 entries showed any recall, all from the same file:

| Entry | File | Recall | Sessions |
|-------|------|--------|----------|
| Conformance Validation for Migrations | agents/decisions/testing.md | 6% | 18 |
| TDD RED Phase: Behavioral Verification | agents/decisions/testing.md | 4% | 23 |
| TDD Integration Test Gap | agents/decisions/testing.md | 4% | 23 |
| TDD: Presentation vs Behavior | agents/decisions/testing.md | 4% | 23 |

### Zero Recall Entries (Sample)

High-relevance entries with zero recall despite many relevant sessions:

- Model Capability Differences: 0% (23 relevant sessions)
- Phase-by-Phase Review Pattern: 0% (23 relevant sessions)
- Oneshot workflow pattern: 0% (23 relevant sessions)
- TDD Workflow Integration: 0% (23 relevant sessions)
- Handoff Pattern: Inline Learnings: 0% (24 relevant sessions)

**Pattern:** Workflow, TDD, and design decision entries are highly relevant but never consulted.

## Root Cause Analysis

### Primary Failure Mode: Passive Awareness

Current memory index relies on agents "mentally scanning" loaded content:
> "Scan the loaded content mentally, identify relevant entries, then Read the referenced file directly."

**Evidence of failure:**
- 1809 opportunities where scanning should have triggered reads
- 0.2% follow-through rate
- No evidence of active scanning behavior in tool call patterns

**Conclusion:** Agents do not perform proactive mental scanning. The passive model is broken.

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

Baseline: **0.2% recall**

Target for `/when` system:
- Minimum viable: **>10% recall** (50× improvement)
- Good: **>30% recall** (150× improvement)
- Excellent: **>50% recall** (250× improvement)

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
- Main repo: 0.0% recall (0 of 1583 pairs)
- Worktree: 3.5% recall (4 of 114 pairs)

Current analysis (2026-02-13):
- Main repo: 0.2% recall (4 of 1809 pairs)
- More sessions analyzed (50 vs previous)
- Bug fixes reveal actual reads

**Conclusion:** 0.2% is the true baseline. Previous 0.0% was measurement error from path matching bug.

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

**Analysis report:** `plans/memory-index-recall/reports/recall-rerun.md`
**Deliverable review:** `plans/memory-index-recall/reports/deliverable-review-report.md`
**Tool implementation:** `src/claudeutils/recall/` (7 modules, 1184 lines)
**Tests:** `tests/test_recall_*.py` (6 modules, 1128 lines, 51 tests passing)
