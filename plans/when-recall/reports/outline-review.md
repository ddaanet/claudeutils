# Outline Review: when-recall

**Artifact**: plans/when-recall/outline.md
**Date**: 2026-02-08T00:15:00-08:00
**Mode**: review + fix-all

## Summary

Outline presents a comprehensive approach to replacing passive memory index with active `/when` skill invocation. Design is sound, addresses root cause (passive catalog format), and leverages existing infrastructure. Initial version had 7 critical/major issues around unresolved decisions and missing traceability. All issues fixed with inline recommendations and explicit decisions.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| `/when` skill with recursive navigation | Section 1 | Complete | SKILL.md + scripts/when.py, detailed flow |
| Format: `/when <learning-name> \| <inline-rule>` | Sections 1, 2, 4 | Complete | Three-field format with rationale |
| Script resolves trigger → section → content | Section 1 | Complete | Core flow documented with 6 steps |
| Output includes related `/when` entries | Section 1 | Complete | Sibling/parent/file navigation |
| Navigation: entry/section/file levels | Section 1 | Complete | Examples + prefix semantics clarified |
| Batching: `/when\n- foo\n- bar` | Section 1 | Complete | Deduplication noted |
| Companion to existing infrastructure | Approach | Complete | FIXED — added explicit infrastructure context |
| Validator updates | Section 3 | Complete | Three-field parsing, word count adjustment |
| `/remember` skill updates | Section 6 | Complete | Step 4a changes + trigger guidelines |
| Measurement via recall analysis | Approach | Complete | FIXED — success criteria (>10% recall in 30 sessions) |

**Traceability Assessment**: All requirements covered with explicit implementation approach.

## Review Findings

### Critical Issues

1. **Mapping strategy unresolved**
   - Location: Section 4 (original)
   - Problem: Listed 3 options (A/B/C) without recommending one, blocking implementation
   - Fix: Selected Option A (inline three-field format), added rationale section documenting why Option B was rejected
   - **Status**: FIXED

2. **Missing success criteria**
   - Location: Approach section (original)
   - Problem: Requirements mention "measurement after 30+ sessions" but no definition of what recall % indicates success
   - Fix: Added explicit success criteria: ">10% recall rate (vs 0% baseline) within 30 sessions"
   - **Status**: FIXED

3. **No infrastructure context**
   - Location: Approach section (original)
   - Problem: Requirements mention "companion to existing index generation and decisions refactoring agents" but outline didn't explain relationship
   - Fix: Added infrastructure context paragraph explaining how `/when` complements existing validator, `/remember` skill, and recall analysis tool
   - **Status**: FIXED

### Major Issues

1. **Structural navigation syntax ambiguity**
   - Location: Section 1 vs Key Decisions (original)
   - Problem: Section 1 described `.` and `..` prefixes but "Key Decisions" listed this as open question
   - Fix: Moved decision to "Key Decisions Made" section, clarified examples in Section 1 with semantic explanations
   - **Status**: FIXED

2. **Exempt sections handling unclear**
   - Location: Section 3 (original)
   - Problem: Asked if "Behavioral Rules" and "Technical Decisions" sections keep current format, no guidance provided
   - Fix: Made explicit decision — "Behavioral Rules" section removed entirely (fragments already @-loaded), "Technical Decisions" converted to standard `/when` format
   - **Status**: FIXED

3. **Word count validation unspecified**
   - Location: Section 3 (original)
   - Problem: Noted "word count limits apply differently" but didn't specify how
   - Fix: Specified 8-20 words (increased from 8-15) to accommodate three-field format
   - **Status**: FIXED

4. **Vague scope boundary**
   - Location: Scope section (original)
   - Problem: "Decision file content changes (format change only, not content)" conflicts with Risks concern about trigger naming quality
   - Fix: Clarified scope — headers/content unchanged, only index format changes; trigger phrase optimization deferred to post-measurement iteration
   - **Status**: FIXED

### Minor Issues

1. **Consumption header example missing**
   - Location: Section 5 (original)
   - Problem: Said "replace passive with active" but didn't show what the new guidance would be
   - Fix: Added before/after comparison with explicit invocation examples and navigation syntax
   - **Status**: FIXED

2. **`/remember` skill changes vague**
   - Location: Section 6 (original)
   - Problem: Only mentioned "update to produce `/when` format" without specifying what changes needed
   - Fix: Added Step 4a changes, trigger naming guidelines, and examples showing good/acceptable/poor trigger phrases
   - **Status**: FIXED

3. **Output format for `/when` skill unspecified**
   - Location: Section 1 (original)
   - Problem: Described what the script does but not what the output looks like
   - Fix: Added "Output format" subsection with example showing section content + related commands formatting
   - **Status**: FIXED

4. **Risk categorization flat**
   - Location: Risks section (original)
   - Problem: Listed risks without distinguishing implementation vs effectiveness concerns
   - Fix: Grouped into "Implementation Risks" (validator, migration) vs "Effectiveness Risks" (trigger naming, attention problem), added mitigation strategies
   - **Status**: FIXED

## Fixes Applied

All fixes applied to plans/when-recall/outline.md:

- **Approach section** — Added infrastructure context (4 bullet points), success criteria (>10% recall in 30 sessions)
- **Section 1 (when.py)** — Expanded core flow from bullet list to 6-step process, added output format example, clarified navigation prefix semantics
- **Section 2 (Index migration)** — Updated examples to three-field format, added exempt sections handling decision (remove Behavioral Rules, convert Technical Decisions)
- **Section 3 (Validator)** — Changed to three-field parsing, specified 8-20 word limit (from 8-15), clarified which field gets strict validation
- **Section 4 (Mapping)** — Replaced "Open question" with "Recommendation: Option A", added rationale for rejecting Option B, documented three-field format benefits
- **Section 5 (Consumption header)** — Added before/after comparison, invocation examples, navigation syntax explanation
- **Section 6 (/remember skill)** — Added current vs updated behavior, trigger naming guidelines with examples
- **Key Decisions section** — Renamed to "Key Decisions Made" + "Open Questions for Implementation", moved 5 decisions to "Made", left 3 implementation details as "Open"
- **Scope section** — Added explicit items (Behavioral Rules removal, trigger optimization deferral)
- **Risks section** — Grouped into Implementation vs Effectiveness, added mitigation strategies for each risk

## Positive Observations

**Strong problem diagnosis:**
- Clearly identifies root cause (passive catalog format vs active invocation)
- References empirical data (0% recall across 200 sessions) to justify approach

**Leverages existing infrastructure:**
- Reuses existing validator (validate-memory-index.py) with format updates
- Extends existing `/remember` skill rather than creating new tooling
- Uses existing recall analysis tool for measurement

**Comprehensive scope definition:**
- Covers all 6 components (skill, index migration, validator, consumption header, `/remember` update, mapping strategy)
- Explicit in-scope vs out-of-scope boundaries
- Defers hook-based injection to future enhancement (correct prioritization)

**Three-field format is well-reasoned:**
- Balances discovery optimization (flexible triggers) with validation needs (strict header-title matching)
- Self-contained (no separate mapping file)
- Enables validator to catch mismatches at precommit

**Navigation levels are intuitive:**
- Entry/section/file hierarchy matches mental model
- Prefix syntax (`.` for section, `..` for file) is consistent with filesystem conventions
- Recursive discovery via related commands supports exploration

## Recommendations

**Implementation phase:**
1. **Validator first:** Update validate-memory-index.py before index migration to catch errors during rewrite
2. **Incremental migration:** Convert one decision file section at a time, validate after each, reduces risk of mass errors
3. **Test coverage for when.py:** Script has complex logic (fuzzy matching, navigation, deduplication) — test-first approach recommended

**Post-implementation:**
1. **Monitor trigger quality:** After 30 sessions, analyze which triggers led to invocations vs which were never used — refine naming guidelines
2. **Measure success strictly:** If recall remains <10% after 30 sessions, escalate to hook-based injection (outlined in Out of Scope)
3. **Document open questions:** Implementation will resolve 3 open questions (trigger naming prescriptiveness, prefix resolution location, batching deduplication) — capture decisions in agents/decisions/

**Future enhancement consideration:**
- Hook-based injection (UserPromptSubmit) could suggest `/when` commands when keywords match triggers — significantly increases visibility beyond format change alone

---

**Ready for user presentation**: Yes

All requirements traced, all critical/major/minor issues fixed, approach is sound and feasible. Outline provides sufficient detail for planning phase.
