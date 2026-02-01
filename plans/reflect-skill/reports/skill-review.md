# Skill Review: reflect

## Summary

The /reflect skill is **well-structured and adheres to best practices** with no critical issues. The skill demonstrates strong architectural alignment with plugin-dev patterns: effective progressive disclosure (SKILL.md: 1,542 words, references: 1,887 words), excellent trigger phrase coverage, proper imperative writing style, and comprehensive content organization.

**Word counts:**
- SKILL.md: 1,542 words (target range: 1,000-3,000 ✓)
- references/patterns.md: 1,236 words
- references/rca-template.md: 651 words
- Total: 3,429 words

**Rating:** Pass with minor improvements suggested

---

## Description Analysis

**Current:**
```yaml
description: This skill should be used when the user asks to "reflect", "diagnose deviation", "root cause", "why did you do X", "RCA", or after interrupting an agent that deviated from rules. Performs structured root cause analysis of agent behavior deviations within the current session context.
```

**Strengths:**
- ✓ Third-person construction ("This skill should be used when...")
- ✓ Excellent trigger phrase coverage: "reflect", "diagnose deviation", "root cause", "why did you do X", "RCA"
- ✓ Specific triggering scenario: "after interrupting an agent that deviated from rules"
- ✓ Clear purpose statement: "Performs structured root cause analysis..."
- ✓ Appropriate length (319 characters - within reasonable bounds)

**Issues:**
None identified. The description is exemplary.

**Recommendations:**
No changes needed. The description provides both specific trigger phrases and contextual usage, making it highly discoverable.

---

## Content Quality

### SKILL.md Analysis

**Word count:** 1,542 words ✓ (well within 1,000-3,000 target)

**Writing style:** Imperative/infinitive form ✓
- Examples: "Perform structured root cause analysis", "Scan conversation context", "Choose exit path"
- No second-person usage detected
- Consistent command-oriented language

**Organization:** Excellent ✓
- Clear hierarchical structure
- Logical flow: When to Use → Protocol (5 phases) → Tool Constraints → Integration → Key Decisions → Resources → Examples
- Well-scoped sections with clear headers
- Strong progressive disclosure to references/

**Specificity:** High ✓
- Concrete guidance throughout: framing block format, output format templates, exit path criteria
- Explicit tool usage: "Tail-call `/handoff --commit` on all exit paths"
- Clear decision criteria: "Fixes are small (<50 lines total edits)"

### Issues

#### Minor (3)

**1. Line count check instruction ambiguity**
- **Location:** Lines 113, 129, 143 (repeated in all three exit paths)
- **Issue:** "After appending: check learnings.md line count — if approaching 80 lines, note to user: 'Consider running /remember to consolidate'"
- **Problem:** "Approaching" is vague. What threshold? 70? 75? 78?
- **Fix:** Specify threshold: "if ≥70 lines" or "if within 10 lines of 80"

**2. Examples use user-visible numbering**
- **Location:** Lines 230-264 (Examples section)
- **Issue:** Examples prefixed with "Example 1:", "Example 2:", "Example 3:"
- **Problem:** Token economy fragment says "Avoid numbered lists — causes renumbering churn when edited"
- **Fix:** Use bullets instead:
  ```markdown
  **Rule Ambiguity (Fix In-Session)**
  **Upstream Input Error (Partial RCA, Handoff)**
  **Systemic Pattern (RCA Complete, Handoff)**
  ```

**3. RCA report slug generation not specified**
- **Location:** Lines 131, 262 ("slug describes deviation")
- **Issue:** No guidance on slug format/generation
- **Problem:** Inconsistent slug generation could create confusion
- **Fix:** Add brief guidance: "Slug format: kebab-case description of deviation type (e.g., `orchestrator-dirty-tree`, `scope-creep-rationalization`)"

### Recommendations

**Priority 1: Fix line count threshold ambiguity**
Replace all instances of "if approaching 80 lines" with specific threshold:
```markdown
After appending: check learnings.md line count — if ≥70 lines, note to user: "Consider running /remember to consolidate"
```

**Priority 2: Convert examples to bullets**
Remove numbered prefixes, use bold titles instead (preserves structure, eliminates numbering).

**Priority 3: Add slug format guidance**
Insert after line 131:
```markdown
**Slug format:** kebab-case description (e.g., `orchestrator-dirty-tree`, `tool-misuse-grep`)
```

---

## Progressive Disclosure

### Current Structure

```
agent-core/skills/reflect/
├── SKILL.md (1,542 words)
└── references/
    ├── patterns.md (1,236 words)
    └── rca-template.md (651 words)
```

### Assessment

**Effectiveness:** Excellent ✓

**SKILL.md contains:**
- Essential execution protocol (5 phases)
- Decision criteria for exit paths
- Tool constraints and integration points
- Inline examples for immediate pattern recognition

**references/ contains:**
- Detailed pattern catalog (patterns.md) - 4 categories, 11 sub-patterns with diagnostic heuristics
- Structured RCA template (rca-template.md) - complete report format

**Balance:** Optimal. SKILL.md is self-contained for basic usage. References provide depth when diagnosing complex or recurring patterns.

### Recommendations

No changes needed. Progressive disclosure is properly implemented.

---

## Specific Issues

### Critical (0)

None identified.

### Major (0)

None identified.

### Minor (3)

**1. Line count threshold ambiguity**
- **File:** SKILL.md
- **Location:** Lines 113, 129, 143
- **Fix:** Replace "approaching 80 lines" with "≥70 lines"

**2. Numbered examples anti-pattern**
- **File:** SKILL.md
- **Location:** Lines 230-264
- **Fix:** Remove "Example 1/2/3:", use bold titles only

**3. Missing slug format specification**
- **File:** SKILL.md
- **Location:** Line 131 (first mention of slug)
- **Fix:** Add guidance: "Slug format: kebab-case description of deviation type"

---

## Positive Aspects

**Exceptional description quality:**
The frontmatter description is a model example: third-person, specific trigger phrases ("reflect", "RCA", "why did you do X"), contextual triggers ("after interrupting an agent that deviated"), and clear purpose.

**Strong architectural alignment:**
- Framing block pattern (forces cognitive reset)
- Three exit paths with clear criteria
- Universal tail-call to `/handoff --commit`
- Quiet execution principles applied (reports to files)

**Comprehensive reference materials:**
- patterns.md provides actionable diagnostic heuristics for 11 deviation patterns
- rca-template.md offers complete structured format (not a vague outline)
- Both references are dense, focused, useful

**Tool constraints match usage:**
Frontmatter `allowed-tools` precisely matches actual tool usage in skill body. No missing tools, no unused declarations.

**Integration awareness:**
Properly references related skills (/handoff, /remember, /hookify) and workflow position (reactive invocation during execution).

**Examples demonstrate all exit paths:**
Three examples cover the three exit paths with realistic scenarios, showing the decision criteria in action.

---

## Overall Rating

**Pass** - Skill meets quality standards for production use.

---

## Priority Recommendations

### 1. Specify line count threshold (Minor - 2 minutes)

**Change:**
```markdown
After appending: check learnings.md line count — if ≥70 lines, note to user: "Consider running /remember to consolidate"
```

**Locations:** Lines 113, 129, 143

**Why:** Removes ambiguity from "approaching". Agents need concrete thresholds for conditional behavior.

---

### 2. Convert examples to bullet format (Minor - 1 minute)

**Change:**
```markdown
## Examples

**Rule Ambiguity (Fix In-Session)**

User interrupts agent that committed despite dirty submodule...
```

**Location:** Lines 229-264

**Why:** Eliminates numbered list renumbering churn (token economy principle).

---

### 3. Add slug format guidance (Minor - 1 minute)

**Change:**
Insert after line 131:
```markdown
**Slug format:** kebab-case description of deviation type (e.g., `orchestrator-dirty-tree`, `tool-misuse-grep`)
```

**Why:** Provides concrete pattern for consistent RCA report naming.

---

## Additional Observations

**Design fidelity:**
The skill implementation precisely matches the design document requirements:
- ✓ Session-break framing block (design R1)
- ✓ Three exit paths with context budget awareness (design R2)
- ✓ Learnings.md appends with line count check (design R3)
- ✓ Slug-based RCA paths (design R4)
- ✓ user-invocable: true (design R5)
- ✓ /remember line count check (design R6)

**No scope creep:**
Skill correctly avoids implementing:
- Automated deviation detection (out of scope)
- Model switching (user action)
- Hook creation (separate skill: /hookify)

**Fragment integration potential:**
If this skill pattern recurs frequently, consider extracting the "line count check after append" logic into a reusable fragment. Currently appears in 3 locations (acceptable duplication for now).

---

## Metadata

**Review performed by:** Sonnet 4.5
**Date:** 2026-02-01
**Skill version:** Initial implementation
**Design compliance:** Full (6/6 requirements met)
**Files reviewed:**
- `agent-core/skills/reflect/SKILL.md`
- `agent-core/skills/reflect/references/patterns.md`
- `agent-core/skills/reflect/references/rca-template.md`
- `plans/reflect-skill/design.md` (design source)
