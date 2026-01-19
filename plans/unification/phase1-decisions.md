# Phase 1: Technical Decisions and Review Outcomes

**Date**: 2026-01-15
**Planning Authority**: Opus 4.5
**Review Authority**: Sonnet 4.5
**Status**: Ready for Haiku execution
**Related Documents**:
- plans/unification/design.md (design authority)
- plans/unification/phase1-execution-plan.md (execution plan)
- plans/unification/reports/phase1-plan-review.md (detailed review)

---

## Executive Summary

Phase 1 execution plan has been created, reviewed, and approved for execution. All Priority 1 review recommendations have been applied. Priority 2 and 3 recommendations are documented for future phases. The plan is executable by Haiku with 90% estimated success probability.

---

## Applied Fixes (Priority 1)

These changes were made to the execution plan based on Sonnet review:

### 1. Composition Mechanism Clarified

**Issue**: Conflicting instructions about marker-based vs simple concatenation approach.

**Fix Applied**:
- Removed marker-based composition mention from Step 5
- Clarified that fragments are complete markdown documents
- Step 6 uses simple bash concatenation (no insertion markers)

**Location**: Step 5, line 217 (execution plan)

**Rationale**: Matches design.md:162-169, simpler implementation for Phase 1.

**Code Impact**:
```bash
# Simple concatenation approach (confirmed)
for fragment in "${FRAGMENTS[@]}"; do
  cat "$fragment" >> "$OUTPUT"
done
```

---

### 2. Framework Content Boundary Defined

**Issue**: Unclear what content belongs in AGENTS-framework.md vs extracted fragments.

**Fix Applied**: Added explicit content boundary specification to Step 5.

**Include in AGENTS-framework.md**:
- File header explaining CLAUDE.md purpose (current CLAUDE.md:1-7)
- Section structure (## headers only, not content)
- Roles/Rules/Skills tables (CLAUDE.md:91-114)
- Loading mechanism (CLAUDE.md:116-120)

**Exclude from AGENTS-framework.md**:
- Specific communication rules → communication.md
- Delegation content → delegation.md
- Tool preferences content → tool-preferences.md
- Hashtag definitions → hashtags.md

**Location**: Step 5, after line 213 (execution plan)

**Rationale**: Framework provides structure/scaffold; fragments provide rule content. Prevents duplication.

**Expected Result**: AGENTS-framework.md ~50-80 lines (structure only), fragments contain actual rules.

---

### 3. Error Handling Protocol Added

**Issue**: No guidance for failure scenarios during execution.

**Fix Applied**: Added comprehensive error handling protocol to "Execution Notes for Haiku" section.

**Protocol Details**:

**Git operation failures**:
- Report exact error message
- Do not retry automatically
- STOP if in Steps 1-6 (foundation required)
- Continue if in Steps 7-9 (test phase, document failure)

**File operation failures**:
- Verify parent directory exists
- Check file permissions
- Report specific missing prerequisite

**Validation failures**:
- Document specific failure in execution report
- Continue to next step (accumulate results)
- Mark step as incomplete in report

**Critical step failures (Steps 1-6)**:
- STOP execution
- Report: "Critical failure in Step N: <description>"
- Do not proceed to test repository integration

**Location**: After line 573 (execution plan)

**Rationale**: Provides clear decision points for executor, prevents cascading failures.

---

### 4. Common Settings Algorithm Added

**Issue**: Ambiguous criteria for determining "common" settings in ruff/mypy extraction.

**Fix Applied**: Added explicit algorithm to Step 3.

**Algorithm**:
1. Parse [tool.ruff] from all available pyproject.toml files
2. For each setting key:
   - If present in ALL files with IDENTICAL value → Include in shared fragment
   - If present in some files or values differ → Exclude, document in comment
3. For list settings (e.g., select, ignore):
   - Include only items present in ALL projects
   - Document: "# Local projects may add: E501, F401, etc."
4. Create ruff.toml with intersection of settings
5. Add header comment: "# Shared ruff configuration - extend locally as needed"

**Location**: Step 3, after line 119 (execution plan)

**Rationale**: Intersection approach ensures only truly common settings, prevents false sharing.

**Example**:
```toml
# Shared ruff configuration - extend locally as needed
# All projects use these settings identically

line-length = 88  # Present in all projects
target-version = "py312"  # Present in all projects

# Local projects may add: extend-select, per-file-ignores, etc.
```

---

## Postponed Fixes (Priority 2)

These recommendations are deferred to later phases or execution time:

### 1. Generated CLAUDE.md Comparison Criteria

**Issue**: Step 6 says "compare with existing CLAUDE.md" without defining acceptable differences.

**Recommendation** (from review):
- Structure should match (same sections in same order)
- Content may differ (extracting, not reproducing)
- Acceptable: Reordered sections, reformatted examples, simplified wording
- Unacceptable: Missing sections, contradictory rules, broken markdown
- Action: Document differences, don't require exact match

**Deferral Rationale**: Executor can use judgment during execution. If issues arise, document in execution report for Phase 2 refinement.

**Risk**: Low - Comparison is for validation, not acceptance criteria.

---

### 2. Tool Requirements Check

**Issue**: Validation assumes just/ruff/mypy installed.

**Recommendation** (from review):
- Check tool availability before validation steps
- Document in execution report if tool missing
- Skip tool-specific validation gracefully

**Deferral Rationale**: User environment likely has these tools. If missing during execution, executor will encounter and report naturally.

**Risk**: Low - Missing tools will cause clear error messages.

---

### 3. Submodule Validation Details

**Issue**: Could be more specific about submodule verification.

**Recommendation** (from review):
- Check .gitmodules file exists and contains correct path
- Verify agent-core directory exists and is not empty
- Check git submodule status shows commit hash
- Verify agent-core/.git file exists (not directory)

**Deferral Rationale**: Current validation "Submodule added successfully" is sufficient for Phase 1. Detailed checks can be added if issues arise.

**Risk**: Very low - Git submodule add either succeeds or fails clearly.

---

## Postponed Enhancements (Priority 3)

Nice-to-have improvements deferred to future phases:

### 1. justfile Recipe Extraction Criteria

**Suggestion**: Add explicit algorithm for determining "shared" recipes.

**Deferred**: Pattern list in Step 2 is sufficient. Executor will use judgment during extraction.

---

### 2. Measurable Success Metrics

**Suggestion**: Add quantified success criteria (file counts, line counts, recipe counts).

**Deferred**: Checkbox criteria adequate for Phase 1. Metrics can be added in retrospective if useful.

---

### 3. Documentation Content Templates

**Suggestion**: Provide example README content or templates.

**Deferred**: Minimum content requirements specified. Executor can create appropriate documentation.

---

## Technical Decisions Summary

All technical decisions made during planning phase:

| Decision | Choice | Rationale | Recorded In |
|----------|--------|-----------|-------------|
| **Repository model** | Separate shared repo as git submodule | Clean separation, agent-friendly | design.md:26 |
| **agent-core location** | `/Users/david/code/agent-core` | Sibling to consuming projects | execution-plan.md:31 |
| **Initial remote** | Local only (GitHub later) | Faster iteration, push when stable | execution-plan.md:30 |
| **Submodule location** | Project root (`agent-core/`) | Cleaner than vendor/, matches design | execution-plan.md:320 |
| **Test repository** | scratch/emojipack (preferred) | Simpler for initial validation | execution-plan.md:317 |
| **Fallback test repo** | scratch/pytest-md | More representative if emojipack unavailable | execution-plan.md:318 |
| **Composition approach** | Simple concatenation, no markers | Simplest implementation, matches design | execution-plan.md:238 |
| **Generation script** | Bash with hardcoded fragment array | YAML parsing deferred to future | execution-plan.md:234 |
| **Script location** | Consumer project (`agents/compose.sh`) | Local control over composition | execution-plan.md:235 |
| **Fragment granularity** | Single justfile-base.just | Can split by concern in Phase 3 if needed | execution-plan.md:83 |
| **Python version** | py312 baseline, document override | Reasonable baseline, design notes variable handling | execution-plan.md:137 |
| **Config extraction** | Intersection algorithm (all projects, identical values) | Only truly common settings | execution-plan.md:120-132 |
| **Per-file ignores** | Exclude from shared fragment | Project-specific by nature | execution-plan.md:138 |
| **pyproject composition** | Manual copy for Phase 1 | Automation deferred to Phase 3/prompt-composer | execution-plan.md:375 |
| **Hashtag principles** | Include 4 core: #stop, #delegate, #tools, #quiet | Restored from old rules, emphasis mechanism | execution-plan.md:185 |
| **Framework content** | Structure/tables only, no rule content | Prevents duplication with fragments | This document, Fix #2 |
| **Error handling** | Explicit protocol with stop conditions | Robust execution, clear decision points | This document, Fix #3 |
| **Submodule URL** | Local path `/Users/david/code/agent-core` | Testing phase, can change to GitHub URL later | execution-plan.md:323 |
| **CLAUDE.md comparison** | Document differences, don't require exact match | Extraction, not reproduction | This document, Postponed #1 |

---

## Design Constraints and Boundaries

Constraints that guided decision-making:

### 1. Phase 1 Scope Limitation

**Constraint**: Phase 1 focuses on foundation only - repository setup, extraction, basic generation.

**Excluded from Phase 1**:
- Agent definitions (QuietExplore, QuietTask, Summarize) → Phase 2
- Sync tooling (sync-check, sync-update, sync-manifest.yaml) → Phase 3
- .claude/ integration and hooks → Phase 4
- YAML parsing in compose script → Future enhancement
- Automated pyproject.toml composition → Phase 3 or prompt-composer

**Impact**: Kept plan focused and executable. Each phase builds on previous.

---

### 2. Haiku Execution Target

**Constraint**: Plan must be executable by Haiku (lowest capability model) without clarification.

**Design Choices**:
- Explicit file paths (absolute, not relative)
- Step-by-step actions with commands
- Clear validation checkboxes
- Algorithm specifications (not "use judgment")
- Error handling protocol
- Report structure defined

**Impact**: Higher detail level, more explicit instructions, less ambiguity.

---

### 3. Design.md Authority

**Constraint**: Execution plan must align with design.md decisions.

**Verification**: Review checklist confirmed alignment on:
- Repository structure (design.md:29-56)
- Composition model (design.md:115-148)
- Fragment types (design.md:273-283)
- Phase 1 deliverables (design.md:358-365)
- All 18 decision points from Decision Summary (design.md:397-417)

**Impact**: No design choices made during planning that contradict design.md.

---

### 4. Test-Before-Rollout

**Constraint**: Test in scratch repository before touching claudeutils.

**Implementation**: Steps 7-9 focus on emojipack integration and validation.

**Success Criteria**: Test repository must successfully:
- Add submodule
- Generate CLAUDE.md
- Import justfile recipes
- Use extracted configs

**Impact**: Safer rollout, issues caught in test environment.

---

## Open Questions Resolution

Questions raised in execution plan and their resolutions:

### 1. Fragment Granularity (justfile)

**Question**: Single file or split by concern?

**Resolution**: Single file for Phase 1, split in later phases if needed.

**Rationale**: Simpler to start, justfile native `import` works for whole files. Can refactor when usage patterns emerge.

**Monitor During Execution**: If justfile-base.just exceeds 300 lines or has distinct audiences, document as candidate for splitting.

---

### 2. Python Version Handling

**Question**: Template variable or hardcoded baseline?

**Resolution**: Hardcode py312 as baseline, document override mechanism in comments.

**Rationale**: All current projects use 3.11+, py312 is reasonable common ground. Template variables add complexity deferred to prompt-composer.

**Future Work**: prompt-composer can implement version parameterization if needed.

---

### 3. compose.yaml Parsing

**Question**: Bash hardcoding or YAML parser?

**Resolution**: Hardcode fragment array for Phase 1.

**Rationale**: Bash arrays are simple and working. YAML parsing adds dependency (yq or Python). Can enhance when needed.

**Future Work**: Phase 3 or later can add yq-based parsing if compose.yaml format evolves.

---

### 4. AGENTS-framework.md Composition Points

**Question**: Marker-based insertion or simple concatenation?

**Resolution**: Simple concatenation (no markers).

**Rationale**: Matches design.md:162-169. Markers add complexity without clear benefit for Phase 1.

**Note**: Fixed in Priority 1 (see Applied Fixes #1).

---

### 5. justfile Variable Naming

**Question**: What variables should be parameterized?

**Resolution**: Identify during extraction (Step 2), likely `SRC_DIR`, `TEST_DIR`, `VENV`.

**Rationale**: Data-driven approach - see what paths appear in recipes, parameterize those.

**Execution Guidance**: Document any hardcoded paths found and why they couldn't be parameterized.

---

## Success Criteria

Phase 1 is complete when:

### Deliverables Created

- [ ] agent-core repository exists with documented structure
- [ ] 8+ files in agent-core (fragments + README)
- [ ] justfile-base.just extracted with shared recipes
- [ ] ruff.toml extracted with common settings
- [ ] mypy.toml extracted with common settings
- [ ] 4 rule fragments extracted (communication, delegation, tool-preferences, hashtags)
- [ ] AGENTS-framework.md created
- [ ] compose.sh generation script created
- [ ] compose.yaml template created

### Test Repository Integration

- [ ] agent-core added as submodule to test repo
- [ ] CLAUDE.md generated from fragments (100+ lines)
- [ ] Generated CLAUDE.md is valid markdown
- [ ] Generated CLAUDE.md contains all fragment contents
- [ ] justfile imports agent-core recipes
- [ ] `just --list` shows 5+ imported recipes
- [ ] Imported recipes execute without errors
- [ ] pyproject.toml uses extracted tool configs
- [ ] ruff/mypy run without config errors

### Documentation

- [ ] agent-core/README.md explains purpose, structure, usage
- [ ] agents/README.md explains composition workflow
- [ ] Execution report documents all steps and decisions

### Quality

- [ ] All validation checkboxes passed (or failures documented)
- [ ] No critical steps failed
- [ ] Technical decisions documented in execution report
- [ ] Deviations from plan justified in execution report

---

## Execution Readiness Assessment

### Plan Quality: ✅ APPROVED

**Strengths**:
- Complete coverage of Phase 1 deliverables
- Concrete technical decisions with rationale
- Clear validation criteria
- Explicit error handling
- Well-structured for Haiku execution

**Review Score**: 90/100 (Sonnet review)

**Confidence Level**: 90% success probability with Priority 1 fixes applied

---

### Prerequisites: ✅ MET

**Required**:
- claudeutils repository on `unification` branch ✅
- Access to scratch repositories (emojipack, pytest-md) ✅
- Git available ✅
- File system write access ✅

**Optional** (validation only):
- just command (for justfile validation)
- ruff command (for config validation)
- mypy command (for config validation)

**Note**: Missing optional tools will skip specific validations, not block execution.

---

### Context Available: ✅ COMPLETE

**Required Context**:
- plans/unification/design.md ✅
- plans/unification/phase1-execution-plan.md ✅
- CLAUDE.md (current format) ✅
- justfile (for extraction) ✅
- pyproject.toml (for extraction) ✅

**Reference Context**:
- plans/unification/reports/phase1-plan-review.md ✅
- plans/unification/phase1-decisions.md (this file) ✅

---

### Handoff Status: ✅ READY

**Handoff Package**:
1. **Execution plan**: plans/unification/phase1-execution-plan.md
2. **Design authority**: plans/unification/design.md
3. **Review report**: plans/unification/reports/phase1-plan-review.md
4. **Decisions log**: plans/unification/phase1-decisions.md (this file)

**Handoff Instructions for Haiku**:
- Read execution plan fully before starting
- Follow steps 1-10 sequentially
- Use specialized tools (Read/Write/Edit/Glob/Grep, not Bash equivalents)
- Write detailed execution report to plans/unification/reports/phase1-execution.md
- Stop on unexpected results (error handling protocol)
- Return: `report: plans/unification/reports/phase1-execution.md` on success

**Estimated Execution Time**: 2-3 hours

**Success Probability**: 90%

---

## Post-Execution Actions

After Haiku completes Phase 1:

### Immediate

1. Review execution report (plans/unification/reports/phase1-execution.md)
2. Verify success criteria met
3. Test generated artifacts (CLAUDE.md, justfile imports, configs)
4. Document any unexpected issues or learnings

### Phase 2 Planning

1. Use Phase 1 learnings to refine Phase 2 plan
2. Apply postponed fixes if issues arose
3. Proceed with agent definitions (QuietExplore, QuietTask, Summarize)

### Backlog

- Consider Priority 2 fixes if relevant issues emerged
- Document patterns for prompt-composer integration
- Evaluate if fragment splitting needed (justfile, configs)

---

## Design Rationale Log

Key "why" decisions for future reference:

### Why git submodule instead of copy-paste?

**Decision**: Use git submodule for shared content distribution.

**Rationale**:
- Agents handle git submodules well (human pain points don't apply)
- Single source of truth
- Automatic updates via git pull
- Enables open-source distribution
- No "drift" concept (local template is source)

**Trade-off**: Submodule complexity vs drift management. Chose submodule because agents mitigate complexity.

---

### Why bash concatenation instead of proper templating?

**Decision**: Simple bash script with hardcoded array, not YAML parsing or templating engine.

**Rationale**:
- Works now, no dependencies
- YAML parsing adds yq dependency
- Templating engines (jinja, envsubst) add complexity
- Can evolve to sophisticated solution when needed
- Phase 1 goal: working foundation, not perfect solution

**Trade-off**: Flexibility vs simplicity. Chose simplicity for faster value.

---

### Why intersection algorithm for configs?

**Decision**: Only include settings present in ALL projects with IDENTICAL values.

**Rationale**:
- Conservative approach prevents false sharing
- Clear algorithm, no judgment calls
- Documents divergences explicitly
- Easy to extend locally (add back project-specific settings)
- Matches "truly shared" principle

**Alternative Considered**: Include most common settings (2+ projects). Rejected because ambiguous and risks incorrect assumptions about intent.

---

### Why test in scratch repo first?

**Decision**: Steps 7-9 test in emojipack before touching claudeutils.

**Rationale**:
- claudeutils is canonical source (becoming consumer via this project)
- Safer to test in disposable environment
- Easier to debug issues in simpler codebase
- Can reset/retry without losing work
- Pattern for future projects

**Alternative Considered**: Test directly in claudeutils. Rejected because higher risk if extraction incorrect.

---

### Why manual pyproject.toml copy for Phase 1?

**Decision**: Defer automated composition to Phase 3 or prompt-composer.

**Rationale**:
- pyproject.toml composition is complex (section merging, list extension, override semantics)
- justfile has native `import` (easy)
- CLAUDE.md is full-file composition (simple concatenation)
- pyproject.toml needs sophisticated merging logic
- Phase 1 goal: prove concept, not solve all problems
- prompt-composer may provide better solution

**Trade-off**: Manual work vs implementation time. Chose manual for faster Phase 1 completion.

---

## References

- **Design Document**: plans/unification/design.md
- **Execution Plan**: plans/unification/phase1-execution-plan.md
- **Detailed Review**: plans/unification/reports/phase1-plan-review.md
- **Design Session**: Session reset on 2025-01-14 (per git log 9576b68)
- **CLAUDE.md Format**: Current CLAUDE.md in repository root
- **Related Work**: plans/prompt-composer/design.md (future integration)

---

**Document Status**: Complete and ready for handoff
**Last Updated**: 2026-01-15
**Next Action**: Hand off to Haiku for execution
