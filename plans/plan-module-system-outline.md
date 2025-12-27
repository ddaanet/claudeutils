# Agent Module System Implementation Plan

**Status**: Phase 2 complete (module extraction), ready for Phase 1 (tooling)
**Created**: 2025-12-26
**Last Updated**: 2025-12-26
**Design Authority**: DESIGN_MODULE_SYSTEM.md, opus-review-module-tiering.md
**Target**: Composable module system with ≤150 rule budget
**Modules Extracted**: 14 semantic sources in agents/modules/src/

---

## Overview

Transform monolithic agent role files into composable module system with semantic sources and generated variants per model class (strong/standard/weak). Key goals:
- Reduce token costs (especially Opus planning output)
- Enable module reuse across roles
- Maintain ≤150 total rule budget
- Provide model-appropriate wording

---

## Phase 1: Foundation & Testing

**Objective**: Validate expansion quality and establish tooling foundation.

### 1.1 Test Expansion Quality

**Purpose**: Empirically compare Sonnet vs Opus for variant generation quality.

**Note**: Opus recommends Opus for quality, but user wants empirical validation.

**Test module**: `agents/modules/src/checkpoint-obedience.semantic.md` (already exists)

**Process**:

1. Generate weak variant with Sonnet → `agents/modules/gen/checkpoint-obedience.weak.sonnet.md`
   - Prompt: Generate weak variant with tier markers
   - Target: 12-16 rules based on frontmatter
   - Include tier markers `[RULE:T1]`, `[RULE:T2]`, `[RULE:T3]`

2. Generate weak variant with Opus → `agents/modules/gen/checkpoint-obedience.weak.opus.md`
   - Same prompt and target
   - Same tier marker requirements

3. Compare variants on:
   - **Rule count accuracy**: Within 12-16 target range?
   - **Tier distribution**: Close to 20/60/20?
   - **Explicitness**: Concrete, actionable rules for weak models?
   - **Tier assignment quality**: Does tier match criticality?
   - **Formatting**: ⚠️ markers, "DO NOT" examples, consequence framing?

4. Manual evaluation:
   - Which variant would work better for Haiku?
   - Does Sonnet under-expand or mis-tier?
   - Is quality difference worth cost difference?

**CHECKPOINT 1**: Report comparison results → final decision on generator (Sonnet vs Opus)

**Expected outcome**: Opus likely superior, but quantify the difference.

---

### 1.2 Rule Counter Implementation

**Purpose**: Count `[RULE]` and `[RULE:Tn]` markers for budget validation.

**Requirements** (from opus-review-module-tiering.md):
- Count `[RULE]` markers (basic rule count)
- Count `[RULE:T1]`, `[RULE:T2]`, `[RULE:T3]` markers (tier-specific counts)
- No parsing needed - simple marker counting
- Validate marker removal (ensure no markers remain in final output)

**Test sequence**:

1. Count `[RULE]` markers → simple count
   - **INPUT**: `"[RULE] Text\n[RULE] More text"`
   - **OUTPUT**: `2`
   - **NEW**: Basic marker counting

2. Count `[RULE:T1]` markers → tier-specific count
   - **INPUT**: `"[RULE:T1] A\n[RULE:T2] B\n[RULE:T1] C"`
   - **OUTPUT**: `{T1: 2, T2: 1, total: 3}`
   - **NEW**: Tier marker parsing

3. Count mixed markers → handles both formats
   - **INPUT**: `"[RULE] A\n[RULE:T1] B\n[RULE:T2] C"`
   - **OUTPUT**: `{untiered: 1, T1: 1, T2: 1, total: 3}`
   - **NEW**: Mixed format handling

4. Validate marker removal → no markers remain
   - **INPUT**: After removal, content should not contain `[RULE`
   - **NEW**: Removal validation

5. Calculate tier distribution → percentage check
   - **INPUT**: `{T1: 3, T2: 9, T3: 3}`
   - **OUTPUT**: `{T1: 20%, T2: 60%, T3: 20%}` (within 20/60/20 target)
   - **NEW**: Distribution calculation

**Implementation**: `src/claudeutils/module_system/rule_counter.py`

**CHECKPOINT 2**: Rule counter passes all tests → ready for variant generation

---

### 1.3 Module Directory Structure

**Status**: ✅ COMPLETE (directories already exist from module extraction)

Existing structure:
```
agents/
  roles/            # Role configs (✅ location decided by Opus)
    planning.yaml   # To be created in Phase 5
    code.yaml
    lint.yaml
    execute.yaml
    refactor.yaml
    review.yaml
    remember.yaml
  modules/
    src/            # 14 semantic sources (✅ complete)
    gen/            # Generated variants (empty, to be created)
    MODULE_INVENTORY.md
  role-planning.md      # Current production roles
  role-planning.next.md # Development outputs (Phase 7)
  role-code.md
  role-code.next.md
  role-lint.md
  role-execute.md
  role-refactor.md
  role-review.md
  role-remember.md
  rules-commit.md   # Skills (already exist)
  rules-handoff.md

Note: .next.md files prevent overwriting during development.
```

**CHECKPOINT 3**: Directory structure confirmed → ready for variant generation

---

## Phase 2: Variant Generation Pipeline

**Objective**: Build automated variant generation system.

### 2.1 Variant Generator Script

**Implementation**: `src/claudeutils/module_system/generator.py`

**Test sequence**:

1. Load semantic source → parsed frontmatter + content
   - **NEW**: Frontmatter parser, semantic content extraction
   - **EXTRACT**: `target_rules.{strong,standard,weak}` ranges

2. Build Opus prompt → includes tier hints and target range
   - **NEW**: Prompt construction with tier section guidance
   - **PROMPT**: "Generate {variant} variant with {min}-{max} rules, mark each with [RULE:T1/T2/T3] based on tier sections"
   - **INPUT**: Semantic source with Critical/Important/Preferred sections
   - **OUTPUT**: Prompt text for Opus

3. Generate variant via Opus → formatted markdown with tier markers
   - **NEW**: Opus API invocation
   - **OUTPUT**: Variant with `[RULE:T1]`, `[RULE:T2]`, `[RULE:T3]` markers

4. Validate variant rule count → warn if outside target range
   - **NEW**: Use rule_counter from Phase 1.2
   - **REQUIREMENT**: Warn (don't fail) if outside range

5. Validate tier distribution → warn if skewed from 20/60/20
   - **NEW**: Check T1/T2/T3 distribution
   - **REQUIREMENT**: Warn if >30% deviation

6. Write to `agents/modules/gen/` → versioned output
   - **NEW**: File write with atomic replacement

**CHECKPOINT 4**: Variant generator produces valid outputs → ready for batch generation

---

### 2.2 Batch Generate All Variants

1. For each module in `agents/modules/src/*.semantic.md`:
   - Generate strong variant
   - Generate standard variant
   - Generate weak variant
   - Validate all variants

2. Store in `agents/modules/gen/{module}.{strong,standard,weak}.md`

3. Report generation statistics:
   - Rule counts per variant
   - Expansion ratios achieved
   - Validation failures

**CHECKPOINT 5**: All module variants generated → ready for role composition

---

## Phase 3: Role Configuration & Composition

**Objective**: Build role composition system with budget validation.

### 3.1 Configuration Schema Implementation

**Implementation**: `src/claudeutils/module_system/config.py`

**Test sequence**:

1. Parse YAML config → validated schema
   - **NEW**: Pydantic models for role config
   - **FIELDS**: role, target_class, rule_budget, modules, sections

2. Validate module references → all modules exist
   - **NEW**: Check `agents/modules/gen/{module}.{target_class}.md` files

3. Load tier-to-section mapping → ordered structure
   - **NEW**: Section template (CRITICAL_RULES, GUIDELINES, PREFERENCES, CONTEXT)

4. Validate budget allocation → warn on overflow
   - **NEW**: Sum module rule counts ≤ role budget
   - **REQUIREMENT**: Handle overflow_strategy (warn/fail/truncate_tier3)

**CHECKPOINT 6**: Config schema validated → ready for composer

---

### 3.2 Role Composer Script

**Implementation**: `src/claudeutils/module_system/composer.py`

**Test sequence**:

1. Load role config → parsed YAML
   - **NEW**: Use config.py from 4.1

2. Select variants by target_class → collect module contents
   - **NEW**: Read `agents/modules/gen/{module}.{target_class}.md`

3. Extract rules by tier marker → organize by T1/T2/T3
   - **NEW**: Parse `[RULE:T1]`, `[RULE:T2]`, `[RULE:T3]` markers
   - **GROUP**: All T1 rules → CRITICAL_RULES section
   - **GROUP**: All T2 rules → GUIDELINES section
   - **GROUP**: All T3 rules → PREFERENCES section

4. Remove tier markers → clean rule text
   - **NEW**: Regex replace `[RULE:Tn]` markers
   - **VALIDATE**: No `[RULE` strings remain in output

5. Validate total rule count → ≤ role budget
   - **NEW**: Use rule_counter, check budget constraint
   - **WARN**: If exceeded (don't fail)

6. Write composed role → `agents/role-{role}.next.md` (development)
   - **NEW**: Formatted output with frontmatter, clean rules (no markers)
   - **NOTE**: Use .next.md suffix to avoid overwriting existing roles during development

**CHECKPOINT 7**: Role composer generates valid role files → ready for validation

---

### 3.3 Budget Validator

**Implementation**: `src/claudeutils/module_system/validator.py`

**Test sequence**:

1. Validate single role → rule count ≤ budget
   - **INPUT**: `agents/role-planning.md` with budget=45
   - **NEW**: Parse role, count rules, check budget

2. Validate all roles → total ≤ 150
   - **NEW**: Sum all role rule counts
   - **REQUIREMENT**: Warn if total > 150

3. Validate tier distribution per role → ~20/60/20
   - **NEW**: Check T1/T2/T3 percentages
   - **WARN**: If >30% deviation from target

4. Check required modules → present in role
   - **NEW**: Verify critical modules included (e.g., communication)

5. Check orphan modules → unused by any role
   - **NEW**: Warn if module not referenced in any config

**CHECKPOINT 8**: All validation passes → composition system complete

---

## Phase 4: Makefile Integration

**Objective**: Automated rebuild on source/model changes.

### 4.1 Makefile Rules

Create `agents/Makefile`:

```makefile
# Config directory (Opus decision: agents/roles/)
CONFIG_DIR := agents/roles

# Variant generation (depends on source + model ID)
agents/modules/gen/%.strong.md: agents/modules/src/%.semantic.md .model-id
    python -m claudeutils.module_system.generator --class=strong $< > $@

agents/modules/gen/%.standard.md: agents/modules/src/%.semantic.md .model-id
    python -m claudeutils.module_system.generator --class=standard $< > $@

agents/modules/gen/%.weak.md: agents/modules/src/%.semantic.md .model-id
    python -m claudeutils.module_system.generator --class=weak $< > $@

# Model ID sentinel (triggers rebuild on model change)
.model-id: FORCE
    @echo $(OPUS_MODEL_ID) | cmp -s - $@ || echo $(OPUS_MODEL_ID) > $@

# Role composition - development output (.next.md suffix)
agents/role-%.next.md: $(CONFIG_DIR)/%.yaml agents/modules/gen/*.md
    python -m claudeutils.module_system.composer $< > $@

# Generate all development outputs
next: $(patsubst $(CONFIG_DIR)/%.yaml,agents/role-%.next.md,$(wildcard $(CONFIG_DIR)/*.yaml))

# Cutover: move .next.md to .md (atomic rename)
cutover:
    @for f in agents/role-*.next.md; do \
        base=$${f%.next.md}; \
        mv "$$base.md" "agents/archive/$$(basename $$base).old.md" 2>/dev/null || true; \
        mv "$$f" "$$base.md"; \
    done

# Validation
validate: agents/role-*.next.md
    python -m claudeutils.module_system.validator

.PHONY: FORCE validate next cutover
```

**Test**:
1. Touch semantic source → variants rebuild
2. Change .model-id → all variants rebuild
3. Change role config → role rebuilds
4. Run `make validate` → passes

**CHECKPOINT 9**: Makefile automation working → ready for role configs

---

## Phase 5: Role Configuration Creation

**Objective**: Create YAML configs for all existing roles.

### 5.1 Planning Role Config

Create `agents/roles/planning.yaml`:

```yaml
role: planning
target_class: strong
rule_budget: 45

modules:
  - communication
  - tool-batching
  - plan-creation
  - tdd-cycle
  - context-overview
  - context-datamodel
  - context-commands

sections:
  - ROLE_IDENTITY
  - CRITICAL_RULES       # T1 rules from all modules
  - GUIDELINES           # T2 rules from all modules
  - PREFERENCES          # T3 rules from all modules
  - CONTEXT              # Project context (no tiers)

overflow_strategy: warn
```

**Note**: Tier assignment is in module variants (via `[RULE:Tn]` markers), not in role config.

**Generate**: `make agents/role-planning.next.md` (development)
**Validate**: Rule count ≤ 45

---

### 5.2 Code Role Config

Create `agents/roles/code.yaml`:

- target_class: weak (Haiku)
- Includes: communication, checkpoint-obedience, tdd-cycle, context-datamodel
- Excludes: plan-creation, full context (token optimization)
- rule_budget: 35

---

### 5.3 Remaining Role Configs

1. `lint.yaml` → minimal context, tool-batching focus
2. `execute.yaml` → plan-adherence, checkpoint-obedience
3. `refactor.yaml` → code-quality, plan-creation
4. `review.yaml` → code-quality, communication
5. `remember.yaml` → memory-management, communication

**CHECKPOINT 10**: All role configs created → validate total budget ≤ 150

---

## Phase 6: Skill Module Migration

**Objective**: Convert skill files to module format.

### 6.1 Skill Module Handling

**Status**: ✅ Skills already extracted as semantic sources (commit.semantic.md, handoff.semantic.md)

**Opus Decision**: Skills use weak-only wording, no variant generation needed.

**Rationale** (from opus-review-module-tiering.md):
- Skills loaded at session end (low context pressure)
- Weak wording works universally for all models
- Marginal token savings (~50 lines × 2 files) doesn't justify pipeline complexity
- Avoid maintaining 6 additional files (2 skills × 3 variants)

**Implementation**:
- Skills remain as single weak-optimized files
- Use tier markers for internal structure (primacy/recency within skill)
- Don't count against role budget (loaded separately)
- No generation pipeline for skills

**CHECKPOINT 11**: Skill handling decided (no-op for implementation) → ready for testing

---

## Phase 7: Side-by-Side Testing & Migration

**Objective**: Validate new system before cutover.

### 7.1 Parallel Testing

1. Create test task requiring planning → code → review cycle

2. Run with OLD system:
   - Load current `agents/role-planning.md`
   - Execute task, measure token usage
   - Note adherence to rules

3. Run with NEW system:
   - Load new `agents/role-planning.next.md` (generated from modules)
   - Execute same task, measure token usage
   - Note adherence to rules

4. Compare:
   - Token reduction (input + output)
   - Rule adherence quality
   - Composition correctness

**CHECKPOINT 12**: New system performs equivalent or better → ready for cutover

---

### 7.2 Cutover & Cleanup

1. Atomic cutover using Makefile:
   ```bash
   mkdir -p agents/archive
   make -C agents cutover
   ```
   This renames: `.next.md` → `.md`, old `.md` → `archive/*.old.md`

2. Verify all roles load correctly with new files

3. Update documentation:
   - `AGENTS.md` → reference new role system
   - `START.md` → point to new locations
   - `README.md` → update if needed
   - Remove "BEFORE STARTING" sections (plans loaded by user)

4. After 1-2 weeks validation: `rm -rf agents/archive/`

**CHECKPOINT 13**: Migration complete → module system live

---

## Phase 8: AGENTS.md Regeneration (OPEN QUESTION)

**Objective**: Decide AGENTS.md handling strategy.

**Options**:
1. Manual maintenance (fallback for non-role-primed agents only)
2. Include in composition pipeline (auto-generated)
3. Hybrid (template + composed modules)

**Decision criteria**:
- Frequency of changes
- Fallback usage patterns
- Maintenance burden

**CHECKPOINT 14**: AGENTS.md strategy decided → implement if automated

---

## Success Criteria

- [x] All modules extracted to semantic sources (14 modules)
- [ ] Rule counter counts `[RULE:Tn]` markers
- [ ] Variant generator creates variants with tier markers
- [ ] All variants generated with valid rule counts
- [ ] Role composer extracts by tier and removes markers
- [ ] All 7 role configs created
- [ ] Total rule budget ≤ 150 (warn if exceeded)
- [ ] Tier distribution ~20/60/20 (warn if >30% deviation)
- [ ] Makefile automation working (rebuild on changes)
- [ ] Side-by-side testing shows equivalent/better performance
- [ ] Token cost reduction measured (Opus planning)
- [ ] Documentation updated

---

## Resolved Questions (from Opus Review)

See `plans/opus-review-module-tiering.md` and Opus agent (a8ddc9f) for detailed analysis.

1. ✅ **Expansion generator**: Opus (quality over cost)
2. ✅ **Rule counting**: Marker-based (`[RULE:Tn]`), not parsing
3. ✅ **Tier assignment**: Hybrid - markers in variants, hints in sources
4. ✅ **Target counts**: Ranges in frontmatter, not computed ratios
5. ✅ **Overflow strategy**: Warn only (never fail, never auto-regenerate)
6. ✅ **Skill handling**: Weak-only, no variant generation
7. ✅ **Module granularity**: 14 modules appropriate
8. ✅ **Config location**: `agents/roles/` - clear purpose, discoverable
9. ✅ **Development naming**: `.next.md` suffix prevents overwriting during development
10. ⏳ **AGENTS.md pipeline**: Defer to Phase 9

---

## Dependencies

- Existing agent role files (`agents/role-*.md`)
- Design specification (`plans/DESIGN_MODULE_SYSTEM.md`)
- Python tooling (Pydantic, PyYAML)
- LLM access (Sonnet/Opus for generation)
- uv package manager
- just task runner (optional: Makefile integration)

---

## Estimated Complexity

- **Phase 1**: 10-12 tests (foundation + expansion quality)
- **Phase 2-3**: 20-25 tests (generation + composition)
- **Phase 4-6**: 10-15 tests (automation + configs + skills)
- **Phase 7-8**: Integration testing + migration

**Total**: ~40-50 test cases (reduced from parsing complexity), 14 modules (✅ complete), 7 role configs

---

## Next Steps

1. ✅ Review outline with user
2. ✅ Resolve design questions via Opus review
3. ✅ Module extraction complete (14 semantic sources in agents/modules/src/)
4. ✅ Config location decided: `agents/roles/` with `.next.md` development pattern
5. **NEXT**: Begin Phase 1.1 - Test expansion quality (Sonnet vs Opus comparison)
6. Proceed incrementally with checkpoints

## Implementation Order (from Opus Review)

Recommended 3-week timeline:

**Week 1: Foundation**
- Day 1-2: Rule counter script
- Day 3-4: Variant generator script
- Day 5: Test generation on pilot module

**Week 2: Generation Pipeline**
- Day 1-2: Generate weak variants for all 14 modules
- Day 3-4: Validation testing
- Day 5: User review of generated variants

**Week 3: Composition**
- Day 1-2: Role composer script
- Day 3: Compose all role files
- Day 4: Side-by-side testing (old vs new)
- Day 5: Cutover + archive old files

---

**END OF OUTLINE**
