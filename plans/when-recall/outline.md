# `/when` Memory Recall System — Outline

## Problem

Memory index has 0% recall across 200 sessions. Current format (`Key — description`) is a passive catalog. Agents never form retrieval intentions from reference material.

## Approach

Replace passive index entries with `/when` and `/how` commands — behavioral triggers agents invoke to recall knowledge. Each entry resolves to full decision content + navigational links (ancestors + siblings).

Index format: `/when trigger | extra triggers`

Triggers are fuzzy-compressed keys. Decision file headings stay as clear prose. Fuzzy matching bridges the density gap — index is compact, headings are readable. Prefix word ("when"/"how") is part of the fuzzy query, disambiguating across operators.

This approach complements existing infrastructure:
- Existing validator extended with fuzzy engine for new format
- Existing `/remember` skill updated to produce `/when` entries
- Existing recall analysis tool measures effectiveness after 30+ sessions

**Success criteria:** Achieve >10% recall rate (vs 0% baseline) within 30 sessions.

## Components

### 1. Resolver script

**Invocation:** `resolver.py when auth fails` / `resolver.py how encode paths`
- First positional arg = prefix (when/how)
- Remaining args = trigger text
- Python prototype, eventually incorporated in claudeutils

**Three modes (determined by leading `.`):**

| Mode | Syntax | Resolves to |
|------|--------|-------------|
| Trigger | `/when auth fails` | Fuzzy match against index, output section content |
| Section | `/when .Testing Conventions` | Global unique heading lookup (any H2-Hx level) |
| File | `/when ..testing.md` | File relative to `agents/decisions/` |

**Primary path:** Exact invocation — agent sees `/when auth fails` in context, invokes exactly that. Fuzzy matching is recovery for approximate queries, not the main path.

**Output format:** Script outputs content directly (no file-path indirection).

```
# When authentication fails

<full section content from decision file>

Broader:
/when .Security Conventions
/when ..architecture.md

Related:
/when session token expiry
/when credential validation
```

**Ancestor links (Broader):** Navigate up the heading hierarchy.
- Learning at H3 → link parent H2
- Learning at H4 → link grandparent H2 + parent H3
- Deeper nesting → all ancestors up to H2
- Always include `..file.md` link

**Sibling links (Related):** Other entries under the same parent heading. Computed by mapping entries to containing section in decision file.

**Fuzzy engine:** Custom ~80 lines, fzf-style scoring with boundary bonuses. Plain prose triggers (no hyphens — "auth error" = 2 tokens, "auth-error" = 3). Word-overlap as tiebreaker.

**Error handling:**
- Trigger not found → suggest closest fuzzy matches
- `.section` not found → list available headings
- `..file.md` not found → list available files
- Malformed index entry → skip with warning

### 2. Skill wrappers

Two thin skills, same resolver:
- `/when` skill: invoke `resolver.py when <trigger>`
- `/how` skill: invoke `resolver.py how <trigger>`

Heading prefix changes based on operator:
- `/when auth fails` → heading `When authentication fails`
- `/how encode paths` → heading `How to encode paths`

Discovery surface stays broad (two skills in listings), implementation DRY.

### 3. Index format migration (agents/memory-index.md)

Rewrite all ~122 entries from:
```
Mock patching pattern — patch where object is used not where defined
```
To:
```
/when writing mock tests | mock patch, test doubles
```

Key changes:
- Trigger (left of `|`): fuzzy-compressed behavioral phrase
- Extra triggers (right of `|`): comma-separated synonyms for matching
- Decision file headings renamed to match triggers (with prefix): `### When writing mock tests`
- Trigger text can be compressed — fuzzy matching bridges to full heading
- No description field — if a learning compresses to single-line, promote to fragment

**Exempt sections:**
- "Behavioral Rules (fragments — already loaded)": remove entirely — fragments are @-loaded, indexing is noise
- "Technical Decisions (mixed)": convert to file-grouped sections with `/when` format

**Migration process:** Sonnet agent rephrases entries. Key compression tool suggests minimal unique triggers. Script-assisted heading renames in decision files.

### 4. Fuzzy engine (shared component)

Single implementation, three consumers:
- **Resolver:** Match trigger query to index entries
- **Validator:** Verify entry↔heading fuzzy correspondence
- **Key compression tool:** Suggest minimal unique triggers

**Fuzzy query includes prefix word:** `/how encode path` → query "how encode path" (not "encode path"). Prefix disambiguates when "when" and "how" entries coexist.

### 5. Validator update (agent-core/bin/validate-memory-index.py)

Update to handle new format. Uses fuzzy engine (not exact string match) for all validation:

**Bidirectional integrity:**
- No broken entries: each index trigger fuzzy-expands to exactly one heading
- No orphaned sections: each heading reachable by exactly one index entry
- Collision detection: no two triggers resolve to same heading

**Format validation:**
- Parse `/when trigger | extra triggers` (two fields, pipe-separated)
- Extra triggers: comma-separated, no empty segments
- Primary trigger uniqueness across index

### 6. Key compression tool

Given heading corpus, suggest minimal fuzzy-compressed trigger that uniquely resolves:

```
$ compress-key "How to encode paths"
how encode path        # unique, 3 words
encode path            # ambiguous (also matches "When encoding paths needed")
```

Shares fuzzy engine with resolver and validator.

### 7. Consumption header update (memory-index.md)

Replace passive "scan mentally" instruction with active invocation guidance:
```
When you need knowledge about a topic, invoke `/when <trigger>` or `/how <trigger>`.

Navigation:
/when <trigger>        # section content + related entries
/when .Section Title   # full section by heading name (any level)
/when ..file.md        # entire decision file (relative to agents/decisions/)
```

### 8. `/remember` skill update

Produce `/when` format entries. Add trigger naming guidelines:
- Plain prose, no hyphens or special characters
- Optimize for discovery: what would agent type when facing this problem?
- Keep concise (2-5 words typical)
- Use key compression tool to verify uniqueness

### 9. Fragment promotion rule

Promote learning to fragment when:
```
token_count(fragment_content) ≤ token_count(index_entry) + margin
```
Where margin accounts for `/` (1 token) and `-` (1 token) overhead. If the full content is roughly the same cost as the index entry, it's ambient knowledge — always load it.

## Key Decisions

1. **Two-field format** — `/when trigger | extra triggers` (not three-field). Fuzzy matching eliminates need for exact header-title field
2. **Sections in files** — No file atomization. Read caching research showed prompt prefix caching (not file-level dedup), killing the individual-file rationale
3. **Two operators** — `/when` (behavioral) + `/how` (procedural). Dropped `/what` and `/why` — passive knowledge, LLMs don't probe for it
4. **Fuzzy bridge** — Index triggers compressed for density, headings stay as clear prose, fuzzy matching connects them
5. **Direct content output** — Script outputs content, no file-path indirection for batch Read
6. **Ancestor + sibling navigation** — Both axes in footer: zoom out (ancestors) and lateral (siblings under same parent)
7. **Plain prose triggers** — No hyphens. More token-efficient, same semantic content

## Scope

**In scope:**
- Resolver script (trigger, .section, ..file modes)
- `/when` and `/how` skill wrappers
- Fuzzy engine (shared: resolver, validator, compression tool)
- Index format migration (~122 entries, sonnet-assisted)
- Decision file heading renames (script-assisted)
- Validator update with fuzzy validation
- Key compression tool
- Consumption header rewrite
- `/remember` skill update
- Fragment promotion rule

**Out of scope:**
- Cross-file explicit relations (deferred entirely)
- Hook-based auto-injection (future enhancement)
- Measurement tooling (existing recall analysis works as-is)
- `/what` and `/why` operators (dropped)

## Risks

**Implementation:**
- Validator update is invasive (480-line script) — mitigate with test coverage
- Fuzzy engine correctness critical (three consumers depend on it) — mitigate with extensive test corpus
- Decision file heading renames are large scope (~122 headings) — mitigate with script + precommit validation

**Effectiveness:**
- Trigger quality varies — iterate based on 30-session measurement
- `/when` may not improve recall if problem is attention not format — measurement determines; if <10%, deeper intervention needed

**Migration:**
- Fuzzy-compressed triggers may create ambiguity if corpus grows — compression tool + validator catch this at precommit
- Heading renames may break existing @ references or documentation links — search for references before renaming
