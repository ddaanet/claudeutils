# Memory Index Update — Recovery Plan

## Process Failure Summary

**Information loss:** Design D-1 explicitly defines ALL `##`, `###`, `####` as semantic (indexed) by default. The `.` prefix is an opt-out for genuinely structural content. Agent and planner misread this as "need to decide which are structural" and proposed marking all subsections as structural — contradicting the design.

**Correct interpretation:** Index should be extensive. 146 semantic headers → 146 index entries. Only genuinely structural headers (TOCs, meta-sections, revision history) get `.` prefix.

---

## Recovery Steps

### Step 1: Revert Agent's Format Changes (if needed)

Check current state of modified files. The agent's format migrations (bare lines, `## Title` learnings) are correct. The error was in NOT adding extensive index entries.

### Step 2: Collect All Semantic Headers

Scan indexed files for all `##`, `###`, `####` headers (excluding `.` prefixed):
- `agents/decisions/*.md` — architecture, cli, testing, workflows
- `agents/learnings.md` — learning titles

### Step 3: Apply Judgment — Mark Genuinely Structural

**Structural (mark with `.` prefix):**
- Table of contents sections
- Revision history sections
- "Files Modified" tables (meta, not knowledge)
- "Implementation" sections that are procedure, not knowledge
- Navigation headers within a topic

**Semantic (leave as-is, add to index):**
- Knowledge units (decisions, patterns, rationale)
- Anti-patterns and correct patterns
- Technical details worth discovering
- Workflow descriptions

### Step 4: Add Index Entries

For each semantic header, add bare line entry to `agents/memory-index.md`:
```
Header title — keyword phrase (8-12 words)
```

Group by source file section or create new sections as needed.

### Step 5: Update Remember Skill

File: `agent-core/skills/handoff/SKILL.md`
- Change template from `**[Learning title]:**` to `## [Learning title]`

File: `agent-core/skills/remember/SKILL.md` (if format shown)
- Update any template examples

### Step 6: Validate

```bash
just precommit
```

All semantic headers should have index entries. Orphan detection should pass.

### Step 7: Vet Review

Delegate to vet-agent:
- Verify index entries match semantic headers
- Verify structural markers applied correctly
- Verify format changes are consistent

---

## Judgment Criteria for Structural vs Semantic

| Pattern | Classification | Rationale |
|---------|---------------|-----------|
| Decision with rationale | Semantic | Knowledge worth discovering |
| Anti-pattern / correct pattern | Semantic | Behavioral guidance |
| "Implementation" (procedure list) | Structural | Steps, not knowledge |
| "Files Modified" | Structural | Meta-information |
| "Revision History" | Structural | Changelog, not knowledge |
| Subsection explaining a concept | Semantic | Knowledge content |
| Navigation header (e.g., "Details below") | Structural | Pointer, not content |

**Default:** Semantic. Only mark structural if clearly meta/navigation.

---

## Process Learning

```markdown
## Design table supersedes heuristics
- Anti-pattern: Inventing classification heuristics when design provides explicit rules
- Correct pattern: Read design classification tables literally. Apply judgment only where design says "use judgment"
- Rationale: Design decisions are intentional. Overriding them based on assumptions (e.g., "extensive index = bad") contradicts the designer's intent
```

---

## Skill Fixes Required

### Fix 1: `/design` skill — Classification table binding

**Location:** `agent-core/skills/design/SKILL.md`, Phase C.1 (Generate Design), after "Content principles"

**Add:**
```markdown
**Classification tables are binding:**

When design includes classification tables (e.g., "X is type A, Y is type B"), these are LITERAL constraints for downstream planners/agents, not interpretable guidelines. Planners must pass classifications through verbatim to delegated agents.

Format classification tables with explicit scope:
- Default behavior (what happens without markers)
- Opt-out mechanism (how to deviate from default)
- Complete enumeration (all cases covered)
```

**Rationale:** The D-1 table was explicit but planner treated it as negotiable. Making binding nature explicit prevents downstream reinterpretation.

---

### Fix 2: `/plan-adhoc` skill — Tier 2 delegation constraints

**Location:** `agent-core/skills/plan-adhoc/SKILL.md`, Tier 2 section, after sequence list

**Add:**
```markdown
**Design constraints are non-negotiable:**

When design specifies explicit classifications (tables, rules, decision lists):
1. Include them LITERALLY in the delegation prompt
2. Delegated agents must NOT invent alternative heuristics
3. Agent "judgment" means applying design rules to specific cases, not creating new rules

Example: If design says "all ## headers are semantic," agent uses judgment to write good index entries for each header — NOT to reclassify some headers as structural.
```

**Rationale:** My delegation prompt said "add `.` to structural headers" without specifying that design already defines what's structural (only explicitly marked ones).

---

### Fix 3: `/plan-adhoc` skill — Escalation handling

**Location:** `agent-core/skills/plan-adhoc/SKILL.md`, new subsection after Tier 2 sequence

**Add:**
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

**Rationale:** I accepted "design ambiguity" escalation without verifying the design table already answered the question.

---

### Fix 4: `/design` skill — Downstream binding note

**Location:** `agent-core/skills/design/SKILL.md`, "Output Expectations" section (line ~223)

**Add:**
```markdown
**Binding constraints for planners:**

Design documents contain two types of content:
1. **Guidance** — Rationale, context, recommendations (planners may adapt)
2. **Constraints** — Classification tables, explicit rules, scope boundaries (planners must follow literally)

Classification tables are constraints. When the table says "### Title is semantic," that's not a suggestion — it's a specification the planner must enforce.
```

**Rationale:** Makes the binding nature explicit at the handoff point between design and planning.

---

## Estimated Scope

- ~20-40 genuinely structural headers (to mark with `.`)
- ~100-120 semantic headers (to add to index)
- Index grows from ~24 to ~140-150 entries
- Token cost: ~3500 tokens (acceptable per design rationale)
