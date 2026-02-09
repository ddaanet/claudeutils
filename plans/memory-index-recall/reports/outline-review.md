# Outline Review: memory-index-recall

**Artifact**: plans/memory-index-recall/outline.md
**Date**: 2026-02-07T21:30:00Z
**Mode**: review + fix-all

## Summary

The outline proposes a well-reasoned retrospective analysis approach using transcript mining to measure memory-index effectiveness. The core methodology is sound: extract tool usage from existing JSONL sessions, correlate Read calls with memory-index entries, and measure recall rates. However, the outline has critical gaps in requirements traceability, lacks concrete success criteria, and needs clearer articulation of the research hypothesis.

**Overall Assessment**: Needs Iteration

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| Do agents consult the index when needed? | Key Decisions | Partial | Method infers from Read calls, not direct observation |
| Do they find the right entries? | Implementation Sketch #4 | Partial | Relevance scoring planned but not detailed |
| Do they read the referenced files? | Implementation Sketch #5 | Complete | Primary metric defined |
| What's the recall rate vs. baseline? | Open Questions | Partial | Baseline definition unclear, comparison method missing |

**Traceability Assessment**: Gaps identified and fixed

## Review Findings

### Critical Issues

1. **Baseline comparison method undefined**
   - Location: Requirements implicitly ask for recall rate "vs. baseline" but outline lacks comparison strategy
   - Problem: Fourth requirement (baseline comparison) addressed only as "Open Question" without proposed resolution
   - Fix: Added baseline approach to Approach section, specified historical session comparison method
   - **Status**: FIXED

2. **Success criteria missing**
   - Location: Entire outline lacks acceptance criteria
   - Problem: No definition of what constitutes "index is effective" or when to iterate on design
   - Fix: Added Success Criteria section with quantitative thresholds
   - **Status**: FIXED

### Major Issues

1. **Research hypothesis not explicit**
   - Location: Core question stated but hypothesis structure missing
   - Problem: "Does agent read file when entry is relevant?" is observation, not testable hypothesis with null/alternative
   - Fix: Added Research Hypothesis section with H0/H1 framing
   - **Status**: FIXED

2. **Relevance mapping underspecified**
   - Location: Key Decisions mentions keyword matching, Open Questions asks about threshold
   - Problem: Critical methodology component left open-ended without proposed calibration strategy
   - Fix: Added Relevance Calibration subsection to Implementation Sketch with validation approach
   - **Status**: FIXED

3. **Temporal ordering ambiguity**
   - Location: Open Questions — "Should Read happen AFTER prompt?"
   - Problem: Core validity threat left unresolved
   - Fix: Specified temporal constraint in Recall Calculator step — Read must follow prompt
   - **Status**: FIXED

4. **Discovery method distinction vague**
   - Location: In-scope item "Distinguish direct reads from search-then-read"
   - Problem: No algorithm specified for how to detect search-then-read pattern
   - Fix: Added Discovery Pattern Detection to Implementation Sketch with sequence analysis
   - **Status**: FIXED

### Minor Issues

1. **Sub-agent handling deferred**
   - Location: Open Questions — "Should we track reads by sub-agents?"
   - Problem: Legitimate scope question but leans toward excluding them without rationale
   - Fix: Clarified in Out of Scope with justification (index not re-loaded in sub-agents)
   - **Status**: FIXED

2. **Sample size not specified**
   - Location: Session.md Design Questions asks about sample size, outline doesn't address
   - Problem: No target number of sessions or sessions-per-category
   - Fix: Added Sample Selection section with size and diversity targets
   - **Status**: FIXED

3. **Report format undefined**
   - Location: Implementation Sketch #6 mentions "summary statistics" but no structure
   - Problem: Unclear what the deliverable report will contain
   - Fix: Expanded Report Generator step with concrete output structure
   - **Status**: FIXED

## Fixes Applied

- **Section 1 (Approach)**: Added baseline comparison strategy (historical sessions pre-index)
- **Section 1 (Approach)**: Added Research Hypothesis with H0/H1 framing
- **Section 1 (Approach)**: Added Success Criteria section with recall thresholds
- **Section 2 (Scope, Out of Scope)**: Clarified sub-agent exclusion with rationale
- **Section 3 (Open Questions)**: Removed temporal ordering question (resolved in implementation)
- **Section 3 (Open Questions)**: Removed baseline definition question (resolved in approach)
- **Section 4 (Implementation Sketch)**: Added Sample Selection step with size targets
- **Section 4 (Implementation Sketch, #4)**: Added Relevance Calibration subsection
- **Section 4 (Implementation Sketch, #5)**: Added temporal constraint (Read after prompt)
- **Section 4 (Implementation Sketch, #5)**: Added Discovery Pattern Detection for search-then-read
- **Section 4 (Implementation Sketch, #6)**: Expanded Report Generator with output structure

## Positive Observations

- **Pragmatic methodology**: Retrospective analysis is well-justified over expensive controlled experiments
- **Reusable infrastructure**: Tool extraction capability has value beyond this experiment (good generalization)
- **Clear scope boundaries**: In-scope vs out-of-scope distinctions are mostly well-defined
- **Honest about limitations**: Acknowledges correlation vs causation constraint upfront
- **Feasible implementation**: Sketch breaks work into tractable parsing/analysis steps

## Recommendations

- **Pilot with manual review**: Before full automation, manually review 5-10 sessions to validate relevance scoring calibration
- **Consider false positives**: Index entry may be relevant but agent doesn't need that specific file (already knows the pattern). Define how to score this.
- **Discovery method patterns**: Search-then-read may indicate index failure OR valid exploratory workflow. Report should distinguish these cases qualitatively.
- **Versioning sensitivity**: Memory-index content evolves. Report should note which version of the index was loaded in each analyzed session.
- **User discussion on thresholds**: Success criteria thresholds (50% recall) are initial proposals — discuss with user before committing to specific numbers.

---

**Ready for user presentation**: Yes
