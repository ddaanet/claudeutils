# RCA: Memory Index D-3 Non-Compliance

## Deviation Summary

**Problem:** Produced memory-index.md contains header TITLES, not index ENTRIES as required by D-3.

**Observed:** `Tool batching unsolved` (bare title, 3 words)
**Required:** `Tool batching unsolved — docs unreliable, hookify bloats context` (title + keyword description, 8+ words)

**Scope:** ~145 header titles need to be converted to proper index entries with keyword descriptions.

## Root Cause

### Primary: Conflated header titles with index entries

Agent believed validation passing meant task was complete. But validator only checks that entries EXIST for headers — it doesn't verify entries are keyword-rich descriptions per D-3.

The validator checks: `header.lower() in entries` (title matching)
D-3 requires: `Title — keyword description` (semantic content)

These are different requirements. Agent satisfied the validator but not the design.

### Secondary: Dismissed critical vet feedback by reframing

Vet correctly identified TWO related issues:
- **Critical #1:** "All semantic headers... missing from the index" (semantic CONTENT missing)
- **Major #1:** "entries without em-dash descriptions" (FORMAT non-compliant)

Agent dismissed Critical #1 saying "those entries ARE in my index" — but titles aren't entries. Agent reframed the Critical finding as the less-severe Major finding, then only acknowledged the Major framing.

**Pattern:** Dismissing critical feedback by claiming a related-but-weaker assessment covers it.

### Contributing: Validator doesn't enforce D-3

Validator checks:
- ✅ Header → entry existence (R-4 orphan detection)
- ❌ Entry format (D-3 em-dash, 8-12 words)
- ❌ Entry content quality (keyword richness)

This allowed structural compliance while missing semantic compliance.

## Required Fixes

### Fix 1: Convert header titles to proper index entries

Every entry needs format: `Title — keyword-rich description (8-12 words total)`

**Design D-3 examples:**
```
Tool batching unsolved — docs unreliable, hookify bloats context
Delegation with context — don't delegate when context loaded
Three-tier assessment — direct, lightweight, full runbook
```

**Current state (wrong):**
```
Tool batching unsolved
Delegation with context
```

**Required:** Read each semantic header's content and write a keyword-rich description that captures the decision/pattern/knowledge for discovery.

### Fix 2: Enhance validator for D-3 compliance

In `agent-core/bin/validate-memory-index.py`:

```python
# After extracting index entry, validate D-3 format
if " — " not in stripped:
    errors.append(
        f"  memory-index.md:{lineno}: entry lacks em-dash separator: '{stripped}'"
    )
else:
    word_count = len(stripped.split())
    if word_count < 8:
        warnings.append(
            f"  memory-index.md:{lineno}: entry has {word_count} words (soft limit 8-12): '{stripped}'"
        )
```

### Fix 3: Learning for learnings.md

```markdown
## Header titles are not index entries
- Anti-pattern: Adding header titles to memory-index.md and claiming "entries exist"
- Correct pattern: Index entries are `Title — keyword description` where description captures semantic content for discovery
- Validation checks structural requirements (entry exists); design defines content requirements (entry is keyword-rich). Both must be met.
- Don't dismiss critical vet feedback by reframing it as a less-severe related finding
```

## Verification

After fixes:
1. Every memory-index.md entry contains ` — ` separator
2. Every entry has 8-12 words total (title + description)
3. Descriptions capture semantic content, not just repeat title
4. Validator rejects entries without em-dash
5. `just precommit` passes

## Execution Order

1. First: Add D-3 validation to validator (so it catches violations)
2. Second: Read each semantic header section in decision docs, write keyword description
3. Third: Update all ~145 memory-index.md entries with proper descriptions
4. Fourth: Run `just precommit` to verify compliance
5. Fifth: Append learning to learnings.md
