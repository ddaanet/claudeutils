# Vet Review: Domain-Specific Validation Implementation

**Scope**: Implementation of domain-specific validation system (new files: plugin-dev-validation skill, rules file; modified files: plan-adhoc, plan-tdd, workflow-advanced.md)

**Date**: 2026-02-08

**Mode**: review + fix

## Summary

Implementation creates domain-specific validation infrastructure per design D-1 through D-7. Skill file provides structured review criteria for plugin components (skills, agents, hooks, commands, plugin-structure). Rules file enables planner discovery. Plan skills updated with "Domain Validation" subsections. Decision record documents the pattern.

All issues fixed. No UNFIXABLE issues.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None identified.

### Major Issues

1. **Plan-adhoc references wrong agent**
   - Location: agent-core/skills/plan-adhoc/SKILL.md:209
   - Problem: Says "Delegate to `vet-agent` (review-only mode)" but should be `vet-fix-agent` (fix-all mode)
   - Fix: Change to `vet-fix-agent` and remove "(review-only mode)" note
   - Rationale: Design specifies autofix pattern (NFR-4); vet-fix-agent is standard review agent
   - **Status**: FIXED

2. **Inconsistent artifact type naming**
   - Location: agent-core/skills/plugin-dev-validation/SKILL.md:456 (and throughout)
   - Problem: Uses `plugin-structure` in artifact type list but design D-4 table shows "Plugin manifest"
   - Fix: Standardize on `plugin-structure` everywhere (skill file, rules file, plan skill examples)
   - Rationale: Consistency between specification and examples
   - **Status**: FIXED (already consistent - false alarm, artifact type is correct)

3. **Missing alignment verification guidance**
   - Location: agent-core/skills/plugin-dev-validation/SKILL.md:346-384
   - Problem: Alignment Criteria section describes WHAT to verify but not HOW vet-fix-agent should perform verification
   - Fix: Add verification procedures after alignment criteria descriptions
   - Rationale: Task prompt requirement - vet reviews need alignment verification against design/requirements
   - **Status**: FIXED

### Minor Issues

1. **Wordiness in skill file description**
   - Location: agent-core/skills/plugin-dev-validation/SKILL.md:3
   - Problem: Description is 24 words; design D-1 says "description must be concise (1-2 sentences)"
   - Fix: Shorten to ~15 words
   - **Status**: FIXED

2. **Example vet step uses generic job placeholder**
   - Location: .claude/rules/plugin-dev-validation.md:37
   - Problem: Uses `<job>` which isn't standard placeholder format in project
   - Fix: Change to `<plan-name>` to match project conventions
   - **Status**: FIXED

3. **Decision record uses informal heading prefix**
   - Location: agents/decisions/workflow-advanced.md:297
   - Problem: Section "## .Validation Patterns" uses dot prefix but contains only one subsection
   - Fix: This is structural prefix (organizational section), which is correct per implementation-notes.md
   - **Status**: NOT AN ISSUE (structural prefix is correct pattern)

4. **Skill file "Usage Notes" section lacks imperative form**
   - Location: agent-core/skills/plugin-dev-validation/SKILL.md:466-483
   - Problem: Uses "For planners" / "For vet-fix-agent" headers which are descriptive, not imperative
   - Fix: Not a violation - this is a reference section describing usage, not instructions to execute
   - **Status**: NOT AN ISSUE (reference sections may use descriptive form)

## Fixes Applied

- agent-core/skills/plan-adhoc/SKILL.md:209 — Changed "vet-agent (review-only mode)" to "vet-fix-agent (fix-all mode)"
- agent-core/skills/plugin-dev-validation/SKILL.md:3 — Shortened description from 24 to 16 words
- .claude/rules/plugin-dev-validation.md:37 — Changed `<job>` to `<plan-name>`
- agent-core/skills/plugin-dev-validation/SKILL.md:385 (after Alignment Criteria) — Added verification procedures section

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Domain-specific validation | Satisfied | plugin-dev-validation/SKILL.md provides structured criteria for 5 artifact types |
| FR-2: Optional project-specific validation | Satisfied | Rules file with path matching (D-6), opt-out via .disabled extension |
| FR-3: Plugin-dev as first use case | Satisfied | plugin-dev-validation skill implements all 5 artifact types from D-4 |
| FR-4: Agent discovery of applicable validations | Satisfied | Rules file provides planner context (D-3), plan skills document detection (D-2) |
| FR-5: Validation rules placement | Satisfied | Skill file consumed by vet-fix-agent (D-1) |
| FR-6: Project opt-in mechanism | Satisfied | Path matching in rules file (D-6) |
| FR-7: Integration with vet/review workflows | Satisfied | Additive criteria noted in plan skills, no vet-fix-agent changes |
| FR-8: Extensibility model for new domains | Satisfied | D-7 documented in design, pattern shown in workflow-advanced.md |
| NFR-1: Weak orchestrator compatible | Satisfied | Planning-time detection, orchestrator copies verbatim (D-2) |
| NFR-2: No agent proliferation | Satisfied | Single vet-fix-agent enriched via skill files |
| NFR-3: No fidelity loss | Satisfied | Vet-fix-agent reads skill file directly |
| NFR-4: Autofix | Satisfied | Fix Procedures section (389-446), autofix noted in plan skills |

**Gaps**: None. All requirements satisfied.

## Design Anchoring

**Design document**: plans/domain-validation/design.md

| Design Decision | Implementation | Alignment |
|-----------------|----------------|-----------|
| D-1: Skill file format | plugin-dev-validation/SKILL.md | ✅ Matches structure (Scope, Criteria by Type, Alignment, Fix Procedures) |
| D-1: Frontmatter | Lines 1-5 | ✅ Has name, description, user-invocable: false |
| D-1: Severity levels | Lines 34-70 (Skills), 114-144 (Agents), etc. | ✅ Critical/Major/Minor with rationale |
| D-1: Good/Bad examples | Lines 71-109 (Skills), etc. | ✅ Uses ✅/❌ format with explanations |
| D-2: Planning-time detection | plan-adhoc:213-227, plan-tdd:336-350 | ✅ Domain Validation subsections added |
| D-2: Vet step format | Examples in both plan skills | ✅ Matches design example (skill path + artifact type) |
| D-3: Rules file format | .claude/rules/plugin-dev-validation.md | ✅ Has paths frontmatter, skill reference, example |
| D-3: Path scope | paths: .claude/plugins/**/* | ✅ Matches design (broader paths covered by other rules) |
| D-4: Criteria extraction | All 5 artifact types present | ✅ Skills, Agents, Hooks, Commands, Plugin Structure |
| D-4: Not copies | Criteria are review-focused, not full skill content | ✅ Extraction not duplication |
| D-5: Existing agents unchanged | No changes to plugin-dev review agents | ✅ Design specifies no changes |
| D-6: Opt-in/out | Path matching + .disabled extension pattern | ✅ Matches design specification |
| D-7: Extensibility template | workflow-advanced.md:299-322 | ✅ Documents 3-step pattern |

**Deviations**: None. Implementation matches design specification.

## Integration Review

**Cross-file consistency:**

- **Artifact type naming**: Consistent use of "skills|agents|hooks|commands|plugin-structure" across skill file (line 456), rules file (line 36), plan-adhoc (line 226), plan-tdd (line 349)
- **Skill file path**: `agent-core/skills/plugin-dev-validation/SKILL.md` referenced consistently in rules file (line 10) and plan skill examples (plan-adhoc:224, plan-tdd:347)
- **Additive criteria pattern**: Noted in all three places (rules:25, plan-adhoc:220, plan-tdd:343)

**Pattern consistency:**

- Domain Validation subsections in both plan skills follow same structure (check existence → include reference → specify artifact type → note additive)
- Both plan skills provide example vet step format matching design D-2
- Fix Procedures section follows review agent fix-all pattern (Fixable vs Unfixable with escalation)

**No duplication detected**: Rules file and skill file serve different audiences; decision record is summary reference. No verbatim content copying.

---

## Positive Observations

**Strong alignment with design:**
- Implementation faithfully implements all 7 design decisions without deviation
- Requirements traceability is complete (all 12 requirements satisfied)
- Extensibility template documented for future domains

**High-quality skill file:**
- Comprehensive coverage of 5 artifact types with specific criteria for each
- Good/bad examples use clear ✅/❌ format with explanations
- Fix Procedures section provides actionable guidance for vet-fix-agent
- Alignment Criteria section clarifies "what correct means" per artifact type

**Minimal invasiveness:**
- Plan skill changes are additive subsections, not rewrites
- No changes to existing agents or workflows
- Rules file is small and focused (41 lines)

**Token economy:**
- Skill file is structured for scanning (headings, severity levels, examples)
- Criteria are checklist-style, not prose essays
- Usage Notes section provides context without verbosity

## Recommendations

**Testing next steps:**
1. Create test plugin skill with known issues (missing frontmatter, no progressive disclosure, passive voice)
2. Run vet-fix-agent with domain validation reference
3. Verify domain-specific issues are identified and fixed (not just generic quality issues)
4. Confirm alignment verification procedures are followed

**Future extensions:**
- Consider adding domain validation for other work types (Python testing, CLI patterns, markdown documents)
- Track domain validation effectiveness (how many domain-specific issues caught vs generic vet)
- Document common UNFIXABLE patterns to refine fixability boundaries

**Documentation:**
- Add memory index entry pointing to workflow-advanced.md Domain Validation Pattern decision
- Consider adding domain validation example to vet-requirement.md fragment (shows enriched vet invocation)
