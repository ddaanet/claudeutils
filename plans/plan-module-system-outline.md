# Agent Module System Implementation Plan

**Status**: Outline ready for review
**Created**: 2025-12-26
**Design Authority**: DESIGN_MODULE_SYSTEM.md
**Target**: Composable module system with ≤150 rule budget

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

### 1.1 Test Expansion Quality (OPEN QUESTION RESOLUTION)

**Purpose**: Determine if Sonnet can generate weak variants, or if Opus required.

1. Create pilot semantic source `modules/src/checkpoint-obedience.semantic.md`
   - Use structure from DESIGN_MODULE_SYSTEM.md example
   - Mark as `expansion_sensitivity: high`
   - Include weak_expansion_notes

2. Generate weak variant with Sonnet → `modules/gen/checkpoint-obedience.weak.sonnet.md`
   - Prompt: target 5x expansion
   - Validate: explicit steps, ⚠️ markers, consequence framing

3. Generate weak variant with Opus → `modules/gen/checkpoint-obedience.weak.opus.md`
   - Same prompt and validation criteria

4. Compare variants
   - Rule count accuracy (±10% of target)
   - Explicitness (enumerated patterns, "do not" examples)
   - Haiku comprehension (run against sample plan)

**CHECKPOINT 1**: Report expansion comparison → decide generator model (Sonnet vs Opus)

---

### 1.2 Rule Counter Implementation

**Purpose**: Automated rule counting for budget validation.

**Requirements** (from DESIGN_DECISIONS.md, Open Question #2):
- Handle itemized lists (bullets, numbered)
- Handle prose paragraphs (count sentences? semantic units?)
- Handle nested lists (2-level max per planning.md)

**Test sequence**:

1. Count simple bullets → `["rule 1", "rule 2"]` = 2
   - **NEW**: Basic itemized list parser

2. Count numbered lists → `["1. rule", "2. rule"]` = 2
   - **NEW**: Numbered format handling

3. Count nested bullets → parent + child rules
   - **NEW**: Nested list traversal
   - **DECISION NEEDED**: Count nesting as separate rules or combine?

4. Count prose paragraph → TBD strategy
   - **DECISION NEEDED**: Sentences? Semantic units? Fixed multiplier?

5. Count mixed document → itemized + prose sections
   - Validates combined logic

**Implementation**: `src/claudeutils/module_system/rule_counter.py`

**CHECKPOINT 2**: Rule counter passes all tests → decision on prose counting strategy

---

### 1.3 Module Directory Structure

1. Create directories:
   ```
   modules/
     src/              # Semantic sources (version controlled)
     gen/              # Generated variants (version controlled)
   roles/
     configs/          # YAML role configurations
     gen/              # Composed role files
   ```

2. Create `.model-id` sentinel for Makefile tracking

3. Add `.gitignore` exceptions (version-control gen/ files)

**CHECKPOINT 3**: Directory structure ready → proceed to module extraction

---

## Phase 2: Module Extraction & Inventory

**Objective**: Extract current role files into semantic module sources.

### 2.1 Identify Cross-Cutting Modules

**Method**: Analyze existing role files for shared concerns.

1. Read current role files → identify duplicated rules
   - `agents/role-planning.md`
   - `agents/role-code.md`
   - `agents/role-lint.md`
   - `agents/role-execute.md`
   - `agents/role-refactor.md`
   - `agents/role-remember.md`

2. Extract communication patterns → `modules/src/communication.semantic.md`
   - Stop patterns, unexpected state handling, wait for instruction
   - **Source**: AGENTS.md Tier 1 Communication Patterns
   - **Expansion sensitivity**: explicit (already weak-optimized)

3. Extract tool batching → `modules/src/tool-batching.semantic.md`
   - Parallel tool calls, efficiency patterns
   - **Source**: AGENTS.md Tool Batching section
   - **Expansion sensitivity**: low (concrete rules)

4. Extract checkpoint patterns:
   - Planning: checkpoint insertion → `modules/src/plan-creation.semantic.md`
   - Code/Execute: checkpoint following → `modules/src/checkpoint-obedience.semantic.md`
   - **Expansion sensitivity**: high (conceptual behavior)

**CHECKPOINT 4**: Cross-cutting modules extracted → validate coverage of shared rules

---

### 2.2 Extract Project Context Modules

1. Create `modules/src/context-overview.semantic.md`
   - **Source**: AGENTS.md Project Overview, Architecture
   - **Format**: Prose (connected project knowledge)

2. Create `modules/src/context-datamodel.semantic.md`
   - **Source**: AGENTS.md Data Model Reference
   - **Format**: Code blocks + explanatory prose

3. Create `modules/src/context-commands.semantic.md`
   - **Source**: AGENTS.md Quick Command Reference
   - **Format**: Itemized with examples

**CHECKPOINT 5**: Context modules ready → selective inclusion testable

---

### 2.3 Extract Workflow Modules

1. Create `modules/src/tdd-cycle.semantic.md`
   - **Source**: `agents/role-code.md` TDD methodology
   - **Expansion sensitivity**: high (conceptual process)

2. Create `modules/src/plan-adherence.semantic.md`
   - **Source**: `agents/role-code.md`, `agents/role-execute.md` scope discipline
   - **Expansion sensitivity**: medium

3. Create `modules/src/code-quality.semantic.md`
   - **Source**: `agents/role-code.md` testing requirements
   - **Expansion sensitivity**: medium

4. Create `modules/src/memory-management.semantic.md`
   - **Source**: `agents/role-remember.md` tiering, documentation patterns
   - **Expansion sensitivity**: medium

**CHECKPOINT 6**: All workflow modules extracted → module inventory complete

---

## Phase 3: Variant Generation Pipeline

**Objective**: Build automated variant generation system.

### 3.1 Variant Generator Script

**Implementation**: `src/claudeutils/module_system/generator.py`

**Test sequence**:

1. Load semantic source → parsed frontmatter + content
   - **NEW**: Frontmatter parser, semantic content extraction

2. Calculate target rule count → expansion_sensitivity × base_count
   - **NEW**: Ratio lookup (low/medium/high/explicit)
   - **INPUT**: Module with `expansion_sensitivity: medium`, 5 rules
   - **OUTPUT**: strong=5, standard=10, weak=15

3. Generate variant via LLM → formatted markdown
   - **NEW**: Prompt construction, LLM invocation
   - **DECISION NEEDED**: Use generator from Phase 1 (Sonnet vs Opus)

4. Validate variant rule count → ±10% of target
   - **NEW**: Use rule_counter from Phase 1.2
   - **REQUIREMENT**: Reject if outside bounds

5. Write to `modules/gen/` → versioned output
   - **NEW**: File write with atomic replacement

**CHECKPOINT 7**: Variant generator produces valid outputs → ready for batch generation

---

### 3.2 Batch Generate All Variants

1. For each module in `modules/src/*.semantic.md`:
   - Generate strong variant
   - Generate standard variant
   - Generate weak variant
   - Validate all variants

2. Store in `modules/gen/{module}.{strong,standard,weak}.md`

3. Report generation statistics:
   - Rule counts per variant
   - Expansion ratios achieved
   - Validation failures

**CHECKPOINT 8**: All module variants generated → ready for role composition

---

## Phase 4: Role Configuration & Composition

**Objective**: Build role composition system with budget validation.

### 4.1 Configuration Schema Implementation

**Implementation**: `src/claudeutils/module_system/config.py`

**Test sequence**:

1. Parse YAML config → validated schema
   - **NEW**: Pydantic models for role config
   - **FIELDS**: role, target_class, rule_budget, modules, sections

2. Validate module references → all modules exist
   - **NEW**: Check `modules/gen/{module}.{target_class}.md` files

3. Load tier-to-section mapping → ordered structure
   - **NEW**: Section template (CRITICAL_RULES, GUIDELINES, PREFERENCES, CONTEXT)

4. Validate budget allocation → warn on overflow
   - **NEW**: Sum module rule counts ≤ role budget
   - **REQUIREMENT**: Handle overflow_strategy (warn/fail/truncate_tier3)

**CHECKPOINT 9**: Config schema validated → ready for composer

---

### 4.2 Role Composer Script

**Implementation**: `src/claudeutils/module_system/composer.py`

**Test sequence**:

1. Load role config → parsed YAML
   - **NEW**: Use config.py from 4.1

2. Select variants by target_class → collect module contents
   - **NEW**: Read `modules/gen/{module}.{target_class}.md`

3. Apply tier→section mapping → ordered document
   - **NEW**: Group modules by tier, insert into sections
   - **POSITION**: Tier 1→start (primacy), Tier 3→end (recency)

4. Validate total rule count → ≤ role budget
   - **NEW**: Use rule_counter, check budget constraint

5. Write composed role → `roles/gen/{role}.md`
   - **NEW**: Formatted output with frontmatter

**CHECKPOINT 10**: Role composer generates valid role files → ready for validation

---

### 4.3 Budget Validator

**Implementation**: `src/claudeutils/module_system/validator.py`

**Test sequence**:

1. Validate single role → rule count ≤ budget
   - **INPUT**: `roles/gen/planning.md` with budget=45
   - **NEW**: Parse role, count rules, check budget

2. Validate all roles → total ≤ 150
   - **NEW**: Sum all role rule counts
   - **REQUIREMENT**: Fail if total > 150

3. Check required modules → present in role
   - **NEW**: Verify critical modules included (e.g., communication)

4. Check orphan modules → unused by any role
   - **NEW**: Warn if module not referenced in any config

**CHECKPOINT 11**: All validation passes → composition system complete

---

## Phase 5: Makefile Integration

**Objective**: Automated rebuild on source/model changes.

### 5.1 Makefile Rules

Create `modules/Makefile`:

```makefile
# Variant generation (depends on source + model ID)
modules/gen/%.strong.md: modules/src/%.semantic.md .model-id
    python -m claudeutils.module_system.generator --class=strong $< > $@

modules/gen/%.standard.md: modules/src/%.semantic.md .model-id
    python -m claudeutils.module_system.generator --class=standard $< > $@

modules/gen/%.weak.md: modules/src/%.semantic.md .model-id
    python -m claudeutils.module_system.generator --class=weak $< > $@

# Model ID sentinel (triggers rebuild on model change)
.model-id: FORCE
    @echo $(OPUS_MODEL_ID) | cmp -s - $@ || echo $(OPUS_MODEL_ID) > $@

# Role composition (depends on config + variants)
roles/gen/%.md: roles/configs/%.yaml modules/gen/*.md
    python -m claudeutils.module_system.composer $< > $@

# Validation
validate: roles/gen/*.md
    python -m claudeutils.module_system.validator

.PHONY: FORCE validate
```

**Test**:
1. Touch semantic source → variants rebuild
2. Change .model-id → all variants rebuild
3. Change role config → role rebuilds
4. Run `make validate` → passes

**CHECKPOINT 12**: Makefile automation working → ready for role configs

---

## Phase 6: Role Configuration Creation

**Objective**: Create YAML configs for all existing roles.

### 6.1 Planning Role Config

Create `roles/configs/planning.yaml`:

```yaml
role: planning
target_class: strong
rule_budget: 45

modules:
  cross_cutting:
    - communication: tier1
    - tool-batching: tier2

  project_context:
    - context-overview: tier2
    - context-datamodel: tier2
    - context-commands: tier3

  workflow:
    - plan-creation: tier1
    - tdd-cycle: tier2

conditionals:
  plan-adherence: false
  checkpoint-obedience: false

sections:
  - ROLE_IDENTITY
  - CRITICAL_RULES
  - GUIDELINES
  - PREFERENCES
  - CONTEXT

overflow_strategy: warn
```

**Generate**: `make roles/gen/planning.md`
**Validate**: Rule count ≤ 45

---

### 6.2 Code Role Config

Create `roles/configs/code.yaml`:

- target_class: weak (Haiku)
- Includes: communication, checkpoint-obedience, tdd-cycle, context-datamodel
- Excludes: plan-creation, full context (token optimization)
- rule_budget: 35

---

### 6.3 Remaining Role Configs

1. `lint.yaml` → minimal context, tool-batching focus
2. `execute.yaml` → plan-adherence, checkpoint-obedience
3. `refactor.yaml` → code-quality, plan-creation
4. `review.yaml` → code-quality, communication
5. `remember.yaml` → memory-management, communication

**CHECKPOINT 13**: All role configs created → validate total budget ≤ 150

---

## Phase 7: Skill Module Migration

**Objective**: Convert skill files to module format.

### 7.1 Commit Skill

1. Extract `agents/rules-commit.md` → `modules/src/commit.skill.semantic.md`
   - **Note**: Currently haiku-optimized, needs semantic source
   - **Expansion sensitivity**: explicit (procedural)

2. Generate weak variant only (skills loaded on-demand)

3. Test: Load before `git commit` → follows workflow

---

### 7.2 Handoff Skill

1. Extract `agents/rules-handoff.md` → `modules/src/handoff.skill.semantic.md`
2. Generate weak variant
3. Test: Load before session end → protocol followed

**CHECKPOINT 14**: Skill modules working → complete module system ready

---

## Phase 8: Side-by-Side Testing & Migration

**Objective**: Validate new system before cutover.

### 8.1 Parallel Testing

1. Create test task requiring planning → code → review cycle

2. Run with OLD system:
   - Load `agents/role-planning.md`
   - Execute task, measure token usage
   - Note adherence to rules

3. Run with NEW system:
   - Load `roles/gen/planning.md`
   - Execute same task, measure token usage
   - Note adherence to rules

4. Compare:
   - Token reduction (input + output)
   - Rule adherence quality
   - Composition correctness

**CHECKPOINT 15**: New system performs equivalent or better → ready for cutover

---

### 8.2 Cutover & Cleanup

1. Archive old role files → `agents/archive/`
2. Update `AGENTS.md` → reference new role system
3. Update `START.md` → point to new locations
4. Update documentation → `README.md`, `agents/DESIGN_DECISIONS.md`
5. Remove "BEFORE STARTING" sections (plans loaded by user)

**CHECKPOINT 16**: Migration complete → module system live

---

## Phase 9: AGENTS.md Regeneration (OPEN QUESTION)

**Objective**: Decide AGENTS.md handling strategy.

**Options**:
1. Manual maintenance (fallback for non-role-primed agents only)
2. Include in composition pipeline (auto-generated)
3. Hybrid (template + composed modules)

**Decision criteria**:
- Frequency of changes
- Fallback usage patterns
- Maintenance burden

**CHECKPOINT 17**: AGENTS.md strategy decided → implement if automated

---

## Success Criteria

- [ ] All modules extracted to semantic sources
- [ ] All variants generated with valid rule counts
- [ ] All 7 role configs created
- [ ] Total rule budget ≤ 150
- [ ] Makefile automation working (rebuild on changes)
- [ ] Side-by-side testing shows equivalent/better performance
- [ ] Token cost reduction measured (Opus planning)
- [ ] Documentation updated

---

## Open Questions for Resolution

1. **Expansion generator** (Phase 1.1): Sonnet vs Opus?
2. **Prose counting** (Phase 1.2): Sentences, semantic units, or fixed multiplier?
3. **Nested list counting** (Phase 1.2): Separate rules or combined?
4. **Overflow strategy** (Phase 4.2): warn, fail, or truncate_tier3?
5. **Commit.md pilot** (Phase 7.1): Rebuild now or defer?
6. **AGENTS.md pipeline** (Phase 9): Manual, automated, or hybrid?

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

- **Phase 1-2**: 15-20 tests (foundation + extraction)
- **Phase 3-4**: 20-25 tests (generation + composition)
- **Phase 5-7**: 10-15 tests (automation + skills)
- **Phase 8-9**: Integration testing + migration

**Total**: ~50-60 test cases, 8-10 modules, 7 role configs

---

## Next Steps

1. Review this outline with user
2. Resolve open questions (especially expansion generator choice)
3. Begin Phase 1.1: Test expansion quality
4. Proceed incrementally with checkpoints

---

**END OF OUTLINE**
