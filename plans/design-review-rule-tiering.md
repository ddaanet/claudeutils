# Design Review: Rule Tiering & Module System Open Questions

**Status**: Pending Opus review
**Created**: 2025-12-26
**Context**: Module system implementation - critical design gaps identified
**Reviewer**: Requires Opus (claude-opus-4-5-20251101)

---

## Confirmed Decisions

✅ **Marker-based rule counting**
- Opus inserts `[RULE]` markers during variant generation
- Markers placed wherever semantically appropriate (full formatting freedom)
- Script counts markers, validates budget
- Markers removed in final composed roles (clean agent context)

✅ **Validation approach**
- Budget violations generate warnings, not failures
- Enables iterative refinement

✅ **Opus autonomy**
- No constraints on rule formatting
- Opus decides what constitutes a rule (prose, bullets, nested items, etc.)
- Marker syntax: `- [RULE] Text` or `[RULE] Text` anywhere

---

## CRITICAL GAP: Rule Tiering Within Modules

### The Problem

Design specifies tier assignment at module level:
```yaml
# roles/configs/planning.yaml
modules:
  cross_cutting:
    - communication: tier1
    - tool-batching: tier2
```

**But**: `communication.weak.md` contains ~15 rules. How do these distribute to sections?

```markdown
# Role output structure
## CRITICAL_RULES     # Tier 1 - primacy position
## GUIDELINES         # Tier 2 - middle
## PREFERENCES        # Tier 3 - recency position
```

**Current design ambiguity**: Does `communication: tier1` mean:
- A) Put ALL communication rules in CRITICAL_RULES section?
- B) Communication module has internal tiers, extract tier1 rules only?
- C) Something else?

---

### Option A: Module-Level Tier (Simple)

**Mechanism**:
- `communication: tier1` → entire module content goes in CRITICAL_RULES section
- `tool-batching: tier2` → entire module content goes in GUIDELINES section

**Example output**:
```markdown
## CRITICAL_RULES

### Communication Module (15 rules)
- [RULE] Stop on unexpected results
- [RULE] Wait for explicit instruction
... (13 more rules)

## GUIDELINES

### Tool Batching Module (8 rules)
- [RULE] Batch reads when needed soon
... (7 more rules)
```

**Advantages**:
- ✅ Simple composition logic
- ✅ Clear role config semantics
- ✅ No complex filtering

**Disadvantages**:
- ❌ Violates position bias principle: All 15 communication rules get primacy position
- ❌ Design intent: tier1 should be ~20% of rules, not entire modules
- ❌ No granular priority control
- ❌ 20/60/20 distribution impossible (DESIGN_MODULE_SYSTEM.md line 122)

**Assessment**: Contradicts core design principle (position bias exploitation).

---

### Option B: Intra-Module Tier Markers

**Mechanism**:
- Modules contain rules with tier markers
- Role config filters rules based on tier

**Semantic source**:
```markdown
# communication.semantic.md
---
rules:
  - tier: 1
    content: "Stop on unexpected results"
  - tier: 2
    content: "Request validation every 3 cycles"
---
```

**Generated weak variant**:
```markdown
# communication.weak.md

- [RULE:T1] Stop on unexpected results
- [RULE:T1] Wait for explicit instruction
- [RULE:T2] Request validation every 3 cycles
... (more rules with tier markers)
```

**Role composition**:
```python
# Load communication.weak.md
# Extract rules where marker matches T1 → CRITICAL_RULES section
# Extract rules where marker matches T2 → GUIDELINES section
```

**Advantages**:
- ✅ Granular priority control
- ✅ Enables 20/60/20 distribution
- ✅ Role config can include subset: `communication: [tier1, tier2]`

**Disadvantages**:
- ⚠️ Complex marker syntax: `[RULE:T1]`, `[RULE:T2]`, `[RULE:T3]`
- ⚠️ Opus must tier every rule during generation
- ⚠️ Role config semantics change: `communication: tier1` means "include tier1 rules from communication"
- ⚠️ Filtering logic in composer

**Questions for Opus**:
1. Can Opus reliably assign tiers during variant generation?
2. Should tier assignment be in semantic source (guidance) or variant-specific?
3. Does tier assignment change between strong/weak variants?

---

### Option C: Section-Based Modules

**Mechanism**:
- Modules have internal section structure mirroring role sections
- Composer merges same sections from multiple modules

**Generated weak variant**:
```markdown
# communication.weak.md

## Critical Rules
- [RULE] Stop on unexpected results
- [RULE] Wait for explicit instruction

## Guidelines
- [RULE] Request validation every 3 cycles
- [RULE] Be explicit with questions

## Preferences
- [RULE] Stop at task boundaries
```

**Role composition**:
```python
# Merge all "Critical Rules" sections from included modules
# Merge all "Guidelines" sections from included modules
# Merge all "Preferences" sections from included modules
```

**Role config**:
```yaml
modules:
  cross_cutting:
    - communication  # All sections included
    - tool-batching
```

**Advantages**:
- ✅ Clear structure in modules
- ✅ Simple composition (concatenate sections)
- ✅ Visual tiering in module files
- ✅ No filtering logic needed

**Disadvantages**:
- ⚠️ Duplicates section structure in every module (13 modules × 3 sections)
- ⚠️ Role config can't selectively include tiers
- ⚠️ Module files longer (section headers add overhead)

---

### Option D: Tier Hints in Semantic Sources

**Mechanism**:
- Semantic sources group rules by conceptual priority
- Opus generates variants with tier markers based on hints
- Allows tier adjustment between variants if needed

**Semantic source**:
```markdown
# communication.semantic.md
---
tier_structure:
  critical:
    - stop_on_unexpected
    - wait_for_instruction
  important:
    - request_validation
    - ask_clarifying_questions
  preferred:
    - stop_at_boundaries
---

## Critical Behaviors

Agent must stop on unexpected results. If something fails OR succeeds unexpectedly,
describe expected vs observed, then STOP.

Agent must wait for explicit instruction before proceeding with plans.

## Important Behaviors

Request validation every 3 test cycles...

## Preferred Behaviors

Complete assigned task then stop (no scope creep)...
```

**Generated weak variant** (Opus interprets hints):
```markdown
# communication.weak.md

- [RULE:T1] ⚠️ STOP if results unexpected (fail OR succeed)
- [RULE:T1] Describe expected vs observed when stopping
- [RULE:T1] ⚠️ WAIT for explicit instruction before proceeding with plans
- [RULE:T1] DO NOT assume "continue" is implied

- [RULE:T2] Request validation every 3 test cycles
- [RULE:T2] Ask clarifying questions if requirements unclear
... (more T2 rules)

- [RULE:T3] Complete assigned task then stop
- [RULE:T3] No scope creep beyond task boundaries
... (more T3 rules)
```

**Advantages**:
- ✅ Semantic source preserves intent without rigid structure
- ✅ Opus flexibility: can adjust tier distribution per variant
- ✅ Example: Strong variant might have 1-2-1 (T1-T2-T3), weak variant 4-8-3
- ✅ Human-readable semantic sources
- ✅ Supports variant-specific tier adjustment

**Disadvantages**:
- ⚠️ Requires Opus to interpret tier hints (LLM task)
- ⚠️ Less deterministic than explicit tier markers
- ⚠️ Validation: how to verify tier distribution matches intent?

---

### Opus Analysis Needed

**Questions**:

1. **Which option best balances simplicity and design goals?**
   - 20/60/20 tier distribution requirement
   - Position bias exploitation
   - Composition complexity
   - Module reusability

2. **Should tier assignment change between variants?**
   - Strong variant: fewer rules, mostly tier1/tier2?
   - Weak variant: more rules, more tier2/tier3 (elaboration)?
   - Or: tier distribution same, just more rules per tier?

3. **How should tier assignment work in role configs?**
   ```yaml
   # Current proposal (ambiguous):
   modules:
     - communication: tier1

   # Option 1: Module goes in tier1 section (Option A)
   # Option 2: Include tier1 rules from module (Option B)
   # Option 3: Include entire module (Option C/D)
   ```

4. **What's the authoring workflow?**
   - User writes semantic source with tier hints?
   - Opus assigns tiers during generation?
   - Manual tier markers in semantic source?

5. **Recommendation**: Which option (A/B/C/D) or hybrid approach?

---

## Open Question 1: Module Extraction Process

### Context

Current plan treats module extraction as implementation task. But extraction requires:
- Analyzing 6 role files for cross-cutting concerns
- Identifying semantic groupings
- Creating module taxonomy
- Writing semantic sources

**This is planning, not implementation.**

### Proposal: Module Extraction as Planning Phase

**Process**:
1. **Opus loads current role files** (planning role task)
2. **Identifies duplication patterns**:
   - Communication rules appear in planning.md, code.md, execute.md
   - Tool batching appears in planning.md, refactor.md
   - TDD cycle in code.md, planning.md
3. **Extracts to semantic sources**:
   - Writes `modules/src/communication.semantic.md`
   - Includes tier hints (critical/important/preferred groupings)
   - Marks expansion sensitivity
4. **User reviews** extracted modules
5. **Opus refines** based on feedback

**Deliverable**: Complete `modules/src/*.semantic.md` inventory

**Advantages**:
- ✅ Leverages Opus strength (pattern recognition, semantic grouping)
- ✅ Creates clean starting point for implementation
- ✅ User validates module boundaries before building pipeline

**Questions for Opus**:
1. Is module extraction appropriate for planning role?
2. What's the output format for semantic sources?
3. Should extraction happen before or after tier design decision?

---

## Open Question 2: Target Rule Count Determination

### Context

Design specified expansion ratios:
```yaml
low:      1x : 1.2x : 1.5x
medium:   1x : 2x   : 3x
high:     1x : 3x   : 5x
```

**User clarification**: "Expansion ratio can be removed if rule counting done by Opus"

### Options

**Option A**: Keep ratios as guidance
```yaml
# Semantic source
---
base_rules: 3
expansion_sensitivity: high
---
```
- Script calculates: weak target = 3 × 5 = 15
- Opus prompt: "Generate weak variant with target ~15 rules"
- **Pro**: Predictable budget planning
- **Con**: Rigid, Opus might need different counts

**Option B**: Explicit targets (no calculation)
```yaml
# Semantic source
---
target_rules:
  strong: 3
  standard: 9
  weak: 15
---
```
- **Pro**: No calculation, explicit intent
- **Con**: Manual math, harder to adjust globally

**Option C**: Opus decides (no targets)
```yaml
# Semantic source
---
semantic_complexity: high
---
```
- Opus prompt: "Generate weak variant (explicit, step-by-step)"
- Opus determines how many rules needed for "explicit"
- **Pro**: Maximum flexibility
- **Con**: Unpredictable counts, budget planning hard

**Option D**: Target ranges
```yaml
# Semantic source
---
target_rules:
  strong: 3-5
  weak: 12-18
---
```
- Gives Opus flexibility within bounds
- **Pro**: Balance predictability + flexibility
- **Con**: Still manual specification

### Questions for Opus

1. **Budget planning**: How important is predictable module rule counts?
   - Need to estimate total budget before generation
   - Or: generate, validate, refine iteratively?

2. **Semantic complexity**: Can Opus infer target count from semantic content?
   - "This concept requires N rules to explain to weak model"
   - Or: needs explicit target?

3. **Recommendation**: Which option balances flexibility and budget control?

---

## Open Question 3: Validation Warnings

### Context

User specified: "Rule count violations must be warning, not failure"

**When should warnings trigger?**

### Scenarios

**Scenario 1**: Module generation exceeds target
- Semantic source: `target_rules.weak: 15`
- Opus generates: 18 rules
- **Warn?** If yes, at what threshold? (±10%, ±2 rules, any deviation?)

**Scenario 2**: Role composition exceeds budget
- Role config: `rule_budget: 45`
- Composed role: 48 rules
- **Warn?** Presumably yes.

**Scenario 3**: Global budget exceeded
- Global budget: 150 rules
- All roles total: 155 rules
- **Warn?** Presumably yes.

**Scenario 4**: Tier distribution skewed
- Role config implies 20/60/20 distribution
- Actual: 40/40/20 (too many tier1 rules)
- **Warn?** Should tier distribution be validated?

### Questions for Opus

1. **Warning thresholds**: Define for each scenario
2. **Tier distribution**: Should this be validated? How?
3. **Action on warnings**: Regenerate? Adjust targets? Accept and document?

---

## Open Question 4: Module Granularity

### Current Inventory

From DESIGN_MODULE_SYSTEM.md:

**Cross-cutting** (3):
- communication
- tool-batching
- checkpoint-obedience

**Project context** (3):
- context-overview
- context-datamodel
- context-commands

**Workflow** (5):
- tdd-cycle
- plan-creation
- plan-adherence
- code-quality
- memory-management

**Skills** (2):
- commit
- handoff

**Total**: 13 modules

### Analysis Questions

1. **Is this appropriate granularity?**
   - 150 rules ÷ 13 modules ≈ 11.5 rules/module average
   - Actual range might be 5-25 rules per module (weak variants)

2. **Should modules be split/merged?**
   - Example: `checkpoint-obedience` splits to `checkpoint-insertion` + `checkpoint-following`?
   - Example: `code-quality` merges with `tdd-cycle`?

3. **Should extraction validate granularity?**
   - Opus extracts, then reviews module sizes
   - Recommends splits if modules >30 rules weak variant?
   - Recommends merges if modules <5 rules?

### Questions for Opus

1. Validate 13-module inventory appropriate?
2. Suggest splits/merges based on semantic cohesion?
3. Should granularity be validated during extraction phase?

---

## Open Question 5: Marker Removal Implementation

### Context

Markers removed during final composition (confirmed: Option C from Decision 1).

### Implementation Complexity

**Simple approach**:
```python
# Remove all rule markers
content = re.sub(r'\[RULE(?::T\d)?\]\s*', '', content)
```

**Preserves formatting**: Just removes marker, keeps text

**Edge cases**:
- Marker on own line: `[RULE] Text` → `Text`
- Marker in list: `- [RULE] Text` → `- Text`
- Marker with tier: `[RULE:T1] Text` → `Text`
- Multiple markers per line: unlikely, but possible?

### Questions for Opus

1. Is simple regex sufficient?
2. Any edge cases that need special handling?
3. Should removal be validated (no `[RULE` strings remain)?

---

## Summary of Required Opus Decisions

### CRITICAL (Blocking Implementation)

1. **Rule tiering within modules**: Option A/B/C/D or hybrid?
2. **Module extraction**: Planning task vs implementation task?
3. **Target count determination**: Keep ratios, explicit targets, or Opus decides?

### Important (Affects Quality)

4. **Validation warnings**: When to warn, at what thresholds?
5. **Module granularity**: Validate 13 modules or suggest adjustments?

### Minor (Can Defer)

6. **Marker removal**: Simple regex sufficient?

---

## Recommended Review Process

1. **Opus loads**:
   - This document
   - `plans/DESIGN_MODULE_SYSTEM.md`
   - `agents/role-planning.md` (current role file for context)

2. **Opus analyzes** each open question

3. **Opus provides**:
   - Decision + rationale for each question
   - Identify any missing considerations
   - Recommended implementation order

4. **Deliverable**: Updated design decisions document

---

**END OF REVIEW REQUEST**
