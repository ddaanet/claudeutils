# `/when` Memory Recall System — Outline

## Problem

Memory index has 0% recall across 200 sessions. Current format (`Key — description`) is a passive catalog. Agents never form retrieval intentions from reference material.

## Approach

Replace passive index entries with `/when` commands — behavioral triggers agents invoke to recall knowledge. Each entry is a skill invocation that resolves to full decision content + recursive navigation.

Format: `/when <learning-name> | <inline-rule>`

This approach complements existing infrastructure:
- Existing validator (validate-memory-index.py) extended to handle new format
- Existing `/remember` skill updated to produce `/when` entries
- No new index generation agents needed — current manual workflow continues with new format
- Existing recall analysis tool (src/claudeutils/recall/) measures effectiveness after 30+ sessions

**Success criteria:** Achieve >10% recall rate (vs 0% baseline) within 30 sessions, indicating agents form retrieval intentions from `/when` triggers.

## Components

### 1. `/when` skill (agent-core/skills/when/)

**SKILL.md** — Entry point for knowledge recall:
- Trigger: `/when <trigger>` or `/when\n- <trigger1>\n- <trigger2>` for batching
- Describe recursive navigation with examples
- Explain `§` navigation operator for section/file-level exploration
- Delegate to scripts/when.py for resolution

**scripts/when.py** — Resolution script (new implementation):

**Core flow:**
1. Receive trigger argument + index file path
2. Parse memory-index.md for `/when` entries (three-field format) — script reads structured data, not agent re-reading loaded context
3. Match argument against triggers (left field of `|`)
4. Resolve header title (middle field) → decision file section (via file section heading in index)
5. Read decision file, extract full section content (from header to next same-level header)
5. Discover related entries:
   - Sibling entries: same decision file section
   - Parent section: H2 containing the H3 (if applicable)
   - Parent file: all entries for the same decision file
6. Emit formatted output: section content + related `/when` commands (invocable)

**Navigation levels:**
- **Entry:** `/when writing mock tests` → "Mock patching pattern" section content + sibling `/when` entries from same file/section
- **Section:** `/when § .Mock Patching` → full H2 structural section + all child entries (`§` + existing header title)
- **File:** `/when § testing.md` → full testing.md file + all entries for that file (`§` + filename)

**`§` operator:** Uses existing unique identifiers — structural section titles (`.` prefix) and filenames. Both are already validated unique by precommit. No new naming needed. Avoids collision with `.` prefix notation used for structural headers in decision files.

**Batching:** `/when\n- writing mock tests\n- splitting modules` → combined output with deduplicated related entries (if both are in same section, siblings shown once)

**Output format:**
```
# Mock Patching Pattern

<full section content from decision file>

---

Related:
- /when organizing test files     # Test Module Split Strategy (sibling)
- /when § .Mock Patching          # Full parent section
- /when § testing.md              # Full testing.md file
```

**Error handling:**
- Trigger not found → suggest closest matches (fuzzy match on trigger field)
- `§` navigation on non-existent section/file → clear error with available options
- Malformed index entry → skip with warning, continue processing

### 2. Index format migration (agents/memory-index.md)

Rewrite all ~169 entries from:
```
Mock patching pattern — patch where object is used not where defined
```
To:
```
/when writing mock tests | Mock patching pattern | patch where used, not defined
```

Key changes:
- Trigger (left of first `|`): behavioral phrase (activity verb phrase), not topic title
- Header title (middle field): exact header from decision file for validation and lookup
- Description (right of second `|`): keyword-rich context (similar to current format)
- Separator changes from ` — ` (em-dash) to ` | ` (pipe, twice)
- Entry still maps 1:1 to a semantic header in decisions file
- Three-field format enables validation while preserving discovery-optimized triggers

**Exempt sections handling:**
- "Behavioral Rules (fragments — already loaded)" section: **Remove entirely** — fragments are @-loaded via CLAUDE.md, indexing them is noise
- "Technical Decisions (mixed — check entry for specific file)" section: **Convert to file-grouped sections** with standard `/when` format
- All remaining entries convert to three-field `/when` format

### 3. Validator update (agent-core/bin/validate-memory-index.py)

Update to handle new `/when` format:
- Parse `/when <trigger> | <header-title> | <description>` (three fields) instead of `Key — description`
- Use middle field (header-title) for validation against decision file semantic headers
- Word count validation: **8-20 words total** (increased from 8-15 to accommodate three-field format)
- Trigger field (left): no validation beyond basic format check (discovery-optimized, flexible phrasing)
- Header-title field (middle): **strict validation** — must match semantic header in decision file (case-insensitive)
- Description field (right): keyword-rich context (similar to current validation)
- Autofix for ordering/placement: uses header-title field (middle) for line number lookup
- Orphan detection: based on header-title field matching decision file headers

### 4. Mapping strategy (trigger → header)

**Recommendation: Option A — Inline three-field format**

Format: `/when <trigger> | <header-title> | <description>`

Example:
```
/when writing mock tests | Mock patching pattern | patch where used, not defined
```

**Rationale:**
- Self-contained — no separate mapping file to maintain
- Validator can verify trigger → header mapping at precommit
- Script extracts header-title field (middle) for lookup in decision files
- Trigger field (left) is what agents type, optimized for discovery
- Description field (right) provides keyword-rich context in index

**Alternative considered:** Mapping file (Option B) rejected due to synchronization burden — changes to decision file headers would require updates in two places (decision file + mapping file + index), vs three fields in one place (index only + decision file).

**Mapping validation:**
- Validator checks that middle field (header-title) matches a semantic header in the specified decision file
- Autofix maintains ordering by source file line number (based on header-title lookup)
- Orphan detection works on header-title field

### 5. Consumption header update (memory-index.md)

Replace current passive instruction:
```
Scan the loaded content mentally, identify relevant entries, then Read the referenced file directly.
```

With active invocation guidance:
```
When you need knowledge about a topic, invoke `/when <trigger>` to retrieve the full decision content.
Example: `/when writing mock tests` returns the "Mock patching pattern" section + related entries.

Batching: `/when\n- writing mock tests\n- splitting modules` retrieves multiple sections efficiently.

Navigation (§ operator):
- Entry-level: `/when <trigger>` → single section + sibling entries
- Section-level: `/when § <section-title>` → full H2 section + all child entries
- File-level: `/when § <filename>.md` → entire decision file + all entries
```

**Rationale:** Shifts from passive "scan mentally" (0% effective) to explicit skill invocation with examples and navigation levels.

### 6. `/remember` skill update (agent-core/skills/remember/SKILL.md)

**Current behavior (Step 4a):**
Adds entries in em-dash format: `Key — description`

**Updated behavior:**
Produce three-field `/when` format: `/when <trigger> | <header-title> | <description>`

**Changes required:**
- Step 4a: Add guidance for crafting behavioral triggers (activity verb phrases preferred)
- Examples: "writing mock tests" (good), "mock patching" (acceptable), "mocks" (too vague)
- Use header title (from decision file) as middle field for validation
- Preserve keyword-rich description as right field
- Update examples in skill documentation to show three-field format

**Trigger naming guidelines to add:**
- Prefer activity phrases: "writing X", "configuring Y", "debugging Z"
- Use lowercase, no special characters
- Keep concise (2-5 words typical)
- Optimize for discovery: what would agent search for when facing this problem?

## Key Decisions Made

1. **Mapping strategy** — Inline three-field format: `/when <trigger> | <header-title> | <description>` (Section 4)
2. **Validation strictness** — Header-title field (middle) validated strictly at precommit; trigger field (left) flexible for discovery optimization
3. **Navigation operator** — `§` operator uses existing unique identifiers: `/when § .Section Title` for section-level, `/when § filename.md` for file-level. Reuses validated identifiers, avoids collision with structural `.` prefix
4. **Word count limits** — Increased to 8-20 words total (from 8-15) to accommodate three-field format
5. **Exempt sections** — "Behavioral Rules" section removed entirely; "Technical Decisions" section converted to file-grouped `/when` format

## Open Questions for Implementation

1. **Trigger naming guidelines** — How prescriptive should trigger phrasing be? (Activity verbs preferred, but edge cases unclear)
2. **`§` navigation implementation** — Does `§` resolution happen in when.py script, or via skill logic?
3. **Batching output format** — How are related `/when` entries deduplicated when multiple queries return overlapping siblings?

## Scope

**In scope:**
- `/when` skill (SKILL.md + scripts/when.py)
- Index format migration (all ~169 entries to three-field format)
- Validator update (validate-memory-index.py)
- Consumption header rewrite (memory-index.md header instructions)
- `/remember` skill update (Step 4a: produce three-field format)
- Behavioral Rules section removal (fragments already @-loaded, indexing is noise)

**Out of scope:**
- Hook-based auto-injection (future enhancement — may improve recall by injecting `/when` suggestions at relevant moments)
- Measurement tooling (existing recall analysis tool in src/claudeutils/recall/ works as-is)
- Decision file content changes (headers and content unchanged; only index format changes)
- Trigger phrase optimization (initial migration uses best-effort activity phrasing; iteration based on recall data later)

## Risks

**Implementation Risks:**
- Validator update is invasive (480-line script, heavily relied on) — mitigate with comprehensive test coverage before/after
- All ~169 entries need rewriting (large mechanical change, risk of mapping errors) — mitigate with validator precommit checks catching mismatches

**Effectiveness Risks:**
- Trigger naming quality varies (some entries map naturally to activities, others don't) — mitigate with best-effort initial phrasing, iterate based on 30-session measurement
- `/when` may not improve recall if the problem is attention, not format — measurement after 30 sessions determines success; if <10% recall, deeper intervention needed (e.g., hook-based injection)

**Migration Risks:**
- Three-field format increases verbosity (3 pipes vs 1 em-dash per entry) — adds ~10% tokens to index; acceptable given 5000 token baseline
- Trigger field flexibility may lead to inconsistent phrasing — document trigger naming guidelines in `/remember` skill for consistency
