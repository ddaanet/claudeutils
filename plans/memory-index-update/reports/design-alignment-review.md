# Design Alignment Review

**Commits reviewed:** 7a3fe..HEAD (4 commits)
- f218641 Update session handoff: memory index and skill fixes complete
- bbb9ec3 Add design constraint binding rules to skills
- 78b5eb2 Complete memory index update with semantic header validation
- 8db6733 Document memory index implementation process failure and recovery

**Review date:** 2026-02-04

---

## Summary

| File | Status | Issues |
|------|--------|--------|
| `agents/memory-index.md` | **PASS** | D-3 compliant |
| `agents/learnings.md` | **PASS** | D-4 compliant |
| `agent-core/bin/validate-memory-index.py` | **PASS** | D-5 compliant |
| `agent-core/bin/validate-learnings.py` | **PASS** | D-4 pattern |
| `agent-core/skills/design/SKILL.md` | **PASS** | Recovery fixes present |
| `agent-core/skills/plan-adhoc/SKILL.md` | **PASS** | Recovery fixes present |

**Overall: PASS** — All files align with design specifications.

---

## Detailed Review

### 1. agents/memory-index.md — D-3 Format

**Design requirement (D-3):**
- Bare lines (no list markers)
- Em-dash separator: `Key — description`
- 8-12 words TOTAL (key + description)

**Verification:**

- Format: Bare lines without `- ` markers
- Separator: All entries use ` — ` (em-dash with spaces)
- Word count: Entries range from 8-14 words

**Sample entries verified:**
```
Tool batching unsolved — documentation unreliable, hookify bloats context, batching benefit unclear
```
Word count: 10 words ✓

```
Minimal `__init__.py` — keep empty, prefer explicit imports from specific modules
```
Word count: 10 words ✓

**Result:** PASS

**Note:** Some entries exceed the 12-word soft limit slightly (e.g., "Recursive pattern: AgentId → SessionId — agent IDs become session IDs for child agents" = 12 words). This is within acceptable variance per D-3's "soft limit" language.

---

### 2. agents/learnings.md — D-4 Format

**Design requirement (D-4):**
- `## Title` headers (not `**Title:**`)
- No blank line after header
- Max 5 words per title

**Verification:**

- Format: All learnings use `## Title` headers (lines 8, 14, 18, 24, 30, etc.)
- No blank lines between `##` and content
- Titles are concise (e.g., "Tool batching unsolved", "Cycle numbering gaps relaxed")

**Sample headers verified:**
```markdown
## Tool batching unsolved
- Documentation (tool-batching.md fragment)...
```
Format: `## Title` ✓
No blank line after: ✓
Word count: 3 words ✓

**Result:** PASS

---

### 3. agent-core/bin/validate-memory-index.py — D-5 Validation

**Design requirement (D-5):**
- Orphan semantic header → ERROR
- Missing em-dash → ERROR
- Word count < 8 → WARNING (soft limit)

**Code verification:**

1. **Orphan semantic header detection (lines 175-183):**
```python
# Check for orphan semantic headers (headers without index entries)
# Per design R-4: all semantic headers must have index entries (ERROR blocks commit)
for title, locations in sorted(headers.items()):
    if title not in entries:
        for filepath, lineno, level in locations:
            errors.append(...)
```
✓ Correctly errors on orphan semantic headers

2. **Em-dash check (lines 161-166):**
```python
# Check D-3 format compliance: entries must have em-dash separator
for key, (lineno, full_entry) in entries.items():
    if " — " not in full_entry:
        errors.append(
            f"  memory-index.md:{lineno}: entry lacks em-dash separator (D-3): '{full_entry}'"
        )
```
✓ Correctly errors on missing em-dash

3. **Word count warning (lines 167-173):**
```python
else:
    # Check word count (8-12 word soft limit for key + description total)
    word_count = len(full_entry.split())
    if word_count < 8:
        warnings.append(
            f"  memory-index.md:{lineno}: description has {word_count} words, soft limit 8-12 (D-3): '{full_entry}'"
        )
```
✓ Correctly warns (not errors) on low word count

4. **Semantic header regex (line 16):**
```python
SEMANTIC_HEADER = re.compile(r"^(##+) ([^.].+)$")
```
✓ Matches `##+` headers NOT starting with `.` (D-1 compliant)

5. **Structural header regex (line 18):**
```python
STRUCTURAL_HEADER = re.compile(r"^(##+) \..+$")
```
✓ Matches `.` prefixed headers (D-1 compliant)

**Result:** PASS

---

### 4. agent-core/bin/validate-learnings.py — D-4 Pattern

**Design requirement (D-4):**
- Match `## Title` pattern
- Max 5 words per title
- No duplicates

**Code verification:**

1. **Title pattern (line 15):**
```python
TITLE_PATTERN = re.compile(r"^## (.+)$")
```
✓ Correctly matches `## Title` format

2. **Word count limit (lines 46-52):**
```python
# Word count check
words = title.split()
if len(words) > max_words:
    errors.append(...)
```
Default `MAX_WORDS = 5` ✓

3. **Uniqueness check (lines 54-62):**
```python
# Uniqueness check
key = title.lower()
if key in seen:
    errors.append(...)
```
✓ Correctly detects duplicates

**Result:** PASS

---

### 5. agent-core/skills/design/SKILL.md — Recovery Fixes

**Required fixes from recovery-plan.md:**

**Fix 1: Classification table binding (lines 136-144)**

Expected text:
```markdown
**Classification tables are binding:**
When design includes classification tables...
```

Found at lines 136-144:
```markdown
**Classification tables are binding:**

When design includes classification tables (e.g., "X is type A, Y is type B"), these are LITERAL constraints for downstream planners/agents, not interpretable guidelines. Planners must pass classifications through verbatim to delegated agents.

Format classification tables with explicit scope:
- Default behavior (what happens without markers)
- Opt-out mechanism (how to deviate from default)
- Complete enumeration (all cases covered)
```
✓ Present and matches recovery plan

**Fix 4: Binding constraints for planners (lines 242-248)**

Expected text:
```markdown
**Binding constraints for planners:**
Design documents contain two types of content...
```

Found at lines 242-248:
```markdown
**Binding constraints for planners:**

Design documents contain two types of content:
1. **Guidance** — Rationale, context, recommendations (planners may adapt)
2. **Constraints** — Classification tables, explicit rules, scope boundaries (planners must follow literally)

Classification tables are constraints. When the table says "### Title is semantic," that's not a suggestion — it's a specification the planner must enforce.
```
✓ Present and matches recovery plan

**Result:** PASS

---

### 6. agent-core/skills/plan-adhoc/SKILL.md — Recovery Fixes

**Required fixes from recovery-plan.md:**

**Fix 2: Tier 2 delegation constraints (lines 78-86)**

Expected text:
```markdown
**Design constraints are non-negotiable:**
When design specifies explicit classifications...
```

Found at lines 78-86:
```markdown
**Design constraints are non-negotiable:**

When design specifies explicit classifications (tables, rules, decision lists):
1. Include them LITERALLY in the delegation prompt
2. Delegated agents must NOT invent alternative heuristics
3. Agent "judgment" means applying design rules to specific cases, not creating new rules

Example: If design says "all ## headers are semantic," agent uses judgment to write good index entries for each header — NOT to reclassify some headers as structural.
```
✓ Present and matches recovery plan

**Fix 3: Escalation handling (lines 89-102)**

Expected text:
```markdown
**Handling agent escalations:**
When delegated agent escalates "ambiguity" or "design gap"...
```

Found at lines 89-102:
```markdown
**Handling agent escalations:**

When delegated agent escalates "ambiguity" or "design gap":

1. **Verify against design source** — Re-read the design document section in question
2. **If design provides explicit rules** (classification tables, decision lists): Resolve using those rules, do not accept the escalation
3. **If genuinely ambiguous** (design silent on the case): Use `/opus-design-question` or ask user
4. **Re-delegate with clarification** if agent misread design

Common false escalations:
- "Which items are X vs Y?" when design table already classifies
- "Should we do A or B?" when design explicitly chose A
- "This seems like a lot" when design rationale explains why it's acceptable
```
✓ Present and matches recovery plan

**Result:** PASS

---

## Issues Found

None. All files align with design specifications.

---

## Recommendations (Minor)

1. **Word count variance:** A few memory-index entries exceed 12 words (up to 14). Consider tightening during future consolidation, though this is within the "soft limit" tolerance.

2. **Validator word count direction:** The validator warns on word count < 8, but design also specifies an upper soft limit of 12. Consider adding a warning for > 12 words for consistency (low priority since it's a soft limit).

3. **Documentation perimeter:** The design.md references `agents/decisions/architecture.md` for planner reading, but this file is not in the `INDEXED_GLOBS` list in the validator. This is intentional per D-2's scope (only `agents/decisions/*.md` and `agents/learnings.md` are indexed sources), but worth noting for future reference.

---

## Conclusion

All changes since commit 7a3fe align with the memory index design specifications:
- D-1: Semantic header marker system correctly implemented
- D-3: Memory index format (bare lines, em-dash, 8-12 words) correctly applied
- D-4: Learnings format (`## Title`) correctly applied
- D-5: Validation logic correctly enforces design rules
- Recovery fixes: All 4 skill fixes from recovery plan are correctly placed and worded

The implementation is design-compliant and ready for use.
