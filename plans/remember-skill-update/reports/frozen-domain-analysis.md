# Frozen-Domain Recall Analysis

**Date:** 2026-02-23
**Requirement:** FR-6 (deferred to Phase 7 per KD-4)

## Problem Statement

Decision file knowledge is "frozen" — written once during consolidation, rarely retrieved during execution. Measured recall rate: 2.9% (pre-FR-13 via always-loaded memory-index) and 4.1% (post-merge via `/when` skill). The recognition bottleneck — knowing when to look something up — limits all voluntary recall mechanisms.

## Evaluation Criteria

- **Agent-independence**: Works without requiring the agent to recognize it needs knowledge
- **Token cost**: Always-loaded vs on-demand cost profile
- **False positive rate**: Injected content relevance to actual task
- **Maintenance burden**: Manual upkeep, drift risk, coupling to codebase changes

## Options Evaluated

### Option 1: Status Quo (`/when` skill, voluntary invocation)

**Mechanism:** Agent recognizes uncertainty → invokes `/when <trigger>` → resolver returns decision content.

**Measured data:**
- 801 sessions analyzed, 22 `/when` invocations in 8/193 post-merge sessions (4.1%)
- Direct decision file reads unchanged (21.2% → 21.8%)
- 1.1x improvement — noise level
- Baseline skill activation: ~20%. `/when` at 4.1% is below baseline, suggesting metacognitive triggers (knowing you're uncertain) have additional activation penalty vs procedural triggers (knowing you need to run a command)

**Assessment:**
- Agent-independence: None. Requires same metacognitive recognition step as passive index
- Token cost: Zero when not invoked (~96% of sessions)
- False positive rate: N/A (voluntary)
- Maintenance burden: Low (memory-index entries maintained via `/codify` pipeline)

### Option 2: PreToolUse Hook (file path → entry injection)

**Mechanism:** When agent reads/edits a file, hook maps file path to relevant memory-index entries and injects via `additionalContext`.

**Analysis:**
- Agent-independence: High — triggers mechanically on file access, no recognition needed
- Token cost: Per-tool-call injection. ~25 tokens per entry × N matched entries per file access. Most files map to 2-5 entries (~50-125 tokens). Only injected on relevant file operations
- False positive rate: Depends on path→entry mapping quality. Broad mappings (all of `src/claudeutils/`) inject many entries; narrow mappings (specific files) miss novel code paths
- Maintenance burden: High — requires maintaining file→entry mapping table. New files, renamed files, and moved files break mappings. Coupling: changes to codebase structure require mapping updates

**Key risk:** Mapping table maintenance. The memory-index already has 200+ entries across ~15 decision files. Building and maintaining a file→entry reverse index is significant ongoing work.

### Option 3: Inline Code Comments (`# See: /when X`)

**Mechanism:** Embed recall hints directly in source code at decision points.

**Analysis:**
- Agent-independence: Moderate — requires agent to read the file (which it does anyway for edits), but hint is passive and may be overlooked
- Token cost: Minimal (~10 tokens per comment, always loaded when file is read)
- False positive rate: Low (co-located with relevant code)
- Maintenance burden: Moderate — comments drift as code changes. No enforcement mechanism to keep comments current. Dead comments when decisions change

**Key risk:** Comment blindness. Agents process code comments but don't reliably act on embedded instructions. No measured data on compliance rate for inline recall hints.

### Option 4: UserPromptSubmit Topic Detection (keyword scan → injection)

**Mechanism:** Hook scans user prompt for topic keywords, injects matching decision content via `additionalContext`.

**Measured data (analogous mechanism):**
- Forced-eval UserPromptSubmit hook reaches 84% activation vs 20% baseline for skill scanning
- Hook mechanism bypasses recognition bottleneck entirely

**Analysis:**
- Agent-independence: High — keyword matching is mechanical, no agent recognition needed
- Token cost: Per-prompt injection. Risk of over-injection if keyword matching is broad. Topic detection must balance precision (few false positives) vs recall (don't miss relevant topics)
- False positive rate: Depends on keyword design. Simple substring matching ("mock", "test") fires on many prompts. Phrase matching ("writing mock tests") is more precise but less comprehensive
- Maintenance burden: Moderate — keyword table needs updating as new decisions are documented. But keyword→entry mapping is simpler than file→entry mapping (Option 2) because it's semantic, not structural

## Recommendation

**Option 4 (UserPromptSubmit topic detection)** is the strongest candidate.

**Rationale:**
- Only options 2 and 4 bypass the recognition bottleneck (the proven failure mode)
- Option 4 has lower maintenance burden than Option 2 (semantic keywords vs structural file mappings)
- Option 4 has a measured analog (skill-scanning hook) showing 84% activation — 20x improvement over status quo
- Keyword mapping scales naturally: each `/codify` consolidation adds keywords alongside the memory-index entry

**Implementation scope (separate task):**
- UserPromptSubmit hook scans prompt for topic keywords from a mapping table
- Matching entries injected via `additionalContext` with decision content or `/when` invocation hint
- Keyword table seeded from existing memory-index triggers (200+ entries)
- Precision tuning: start with phrase-level matching, measure false positive rate, adjust

**Risk:** False positive injection cost. If hook injects on 50%+ of prompts, token overhead negates the value. Keyword specificity must be calibrated empirically.

## Summary Matrix

| Criterion | Status Quo | PreToolUse Hook | Code Comments | UserPromptSubmit |
|-----------|-----------|-----------------|---------------|-----------------|
| Agent-independence | None | High | Moderate | High |
| Token cost | Zero (unused) | Per-tool-call | Minimal | Per-prompt |
| False positive rate | N/A | Mapping-dependent | Low | Keyword-dependent |
| Maintenance burden | Low | High | Moderate | Moderate |
| Measured effectiveness | 4.1% | No data | No data | 84% (analog) |
| **Recommendation** | Baseline | Not recommended | Not recommended | **Recommended** |
