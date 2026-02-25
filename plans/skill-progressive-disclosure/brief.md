# Skill Progressive Disclosure — Brief

**Source:** Discussion session 2026-02-25 (skills-quality-pass context, post-RCA on runbook skill execution momentum)

## Problem

Large skills (/design 521 lines, /runbook 1027 lines) load entirely at invocation. Content for paths never taken competes for attention and creates execution momentum — agent follows loaded procedure instead of assessing task state. Evidence: agent ran full Tier 3 planning phases (0.85-0.95) against already-planned work because the skill procedure was more prominent than session.md task metadata saying "ready for orchestration."

Same pattern class as primitive visibility (execution-routing.md): structural fix (reducing visibility) outperforms rule additions.

## Design: Segment Loading at Gate Boundaries

Load only the segment relevant to the current execution path. Each segment ends at a decision gate; the next segment loads only if that gate routes deeper.

### /design Segments

1. **Initial load (~150 lines):** Triage + classification gate + Simple/Moderate/Complex routing + direct implementation path (fast exit)
2. **`references/write-outline.md`:** Loaded on Moderate/Complex path. Research protocol, outline generation, outline sufficiency gate. Ends with "outline sufficient → direct execution" or "proceed to full design"
3. **`references/write-design.md`:** Loaded only when full design needed. Phases B-C, design content rules, binding constraints

### /runbook Segments

1. **Initial load (~200 lines):** Tier assessment + Tier 1 (direct) / Tier 2 (lightweight delegation) paths + lightweight orchestration exit
2. **Loaded on Tier 3:** Phase 0.5-0.95 (discovery through sufficiency). Includes lightweight orchestration exit from Phase 0.95
3. **Loaded past sufficiency:** Phase 1-4 (expansion, assembly, validation, prepare-runbook.py). Only when outline isn't sufficient

### Segment Naming

Verb-oriented (`write-outline.md`, `write-design.md`) not noun-oriented (`outline.md`, `design.md`) — avoids confusion with plan artifacts they produce.

## Complementary with Quality Pass

The skills-quality-pass FR-3 extraction (Steps 3.1, 3.2) already creates `references/` files for /design and /runbook. Those extractions can be designed with this segmentation in mind — the content being extracted to references/ overlaps significantly with the content that should only load on deeper paths.

## Lightweight Orchestration Exit

Added to runbook skill Phase 0.95 in this session. When outline passes sufficiency AND contains `## Execution Model` section with dispatch protocol → skip promote/prepare-runbook.py, dispatch directly from outline with recall-injected prompts. Codifies the pattern used for skills-quality-pass orchestration.
