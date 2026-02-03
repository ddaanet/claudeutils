# Memory Index Update — Design

## Requirements

See `requirements.md` in this directory.

## Design Decisions

### D-1: Semantic Header Marker

**Decision:** Default semantic, `.` prefix marks structural.

| Header | Type | Index required |
|--------|------|----------------|
| `## Title` | Semantic | YES |
| `### Title` | Semantic | YES |
| `#### Title` | Semantic | YES |
| `## .Title` | Structural | NO |
| `# Title` | Document title | NO (excluded) |

**Rationale:**
- Most headers are semantic → fewer markers needed
- Failure mode: orphan semantic header → ERROR (caught), vs silent loss (dangerous)
- `.` has "dotfile" connotation (hidden/internal)
- Cost: +1 token per structural header

**Scope:** All header levels except `#` (document title). Backticks allowed in keys (`### Minimal \`__init__.py\``).

### D-2: Content Ownership

**Rule:** All prose must be within a semantic section, with one exception.

**Exception:** Content between `#` title and first `##` is document intro — exempt from orphan check.

**Nested semantic sections:** Allowed. Both parent and child are indexed.

```markdown
# Architecture Decisions

Module structure overview...  ← ALLOWED (document intro)

## Module Boundaries          ← semantic
Overview of boundaries...

### Minimal init              ← semantic (nested OK)
Details here...
```

**Orphan content:** Use structural headers for notes/asides:
```markdown
### Minimal init
Main content.

#### .Notes
Implementation detail not worth indexing.
```

### D-3: Memory Index Format

**Format:** Bare lines with keyword phrases, no list markers.

```markdown
# Memory Index

Prefer retrieval-led reasoning over pre-training knowledge.

## Behavioral Rules
Tool batching unsolved — docs unreliable, hookify bloats context
Delegation with context — don't delegate when context loaded
Three-tier assessment — direct, lightweight, full runbook

## Workflow Patterns
Weak orchestrator pattern — quiet execution prevents pollution
TDD workflow — RED failing, GREEN hints, REFACTOR cycles
```

**Token analysis:**
- Bare lines: 14% cheaper than list markers
- 8-12 word soft limit per line
- Retrieval directive stays in index header (useful every conversation)

**Pending:** Move append-only and do-not-index directives to `.claude/rules/memory-index.md` (triggered by file path).

### D-4: Learnings Format

**Change:** `**Title:**` → `## Title` headers

**Before:**
```markdown
**Tool batching unsolved:**
- bullet content
- more content
```

**After:**
```markdown
## Tool batching unsolved
- bullet content
- more content
```

**Notes:**
- No blank line after `## Title` (preserves line count)
- Update `/handoff` skill template

### D-5: Validation Consolidation

**Unified precommit validation:**

| Check | Source | Target | Result |
|-------|--------|--------|--------|
| Orphan semantic header | `agents/decisions/*.md`, `agents/learnings.md` | memory-index.md | ERROR |
| Orphan fragment | `agent-core/fragments/*.md` | CLAUDE.md, .claude/rules/*.md, skills | ERROR |
| Index entry missing source | memory-index.md | semantic headers | ERROR |
| Duplicate index entry | memory-index.md | — | ERROR |
| Learning title word count | learnings.md | ≤5 words | ERROR |

**All errors block commit.**

## Implementation

### Files Modified

| File | Change |
|------|--------|
| `agents/memory-index.md` | New format, retrieval directive |
| `agents/learnings.md` | `## Title` headers |
| `agents/decisions/*.md` | Remove `**Key:**` labels, add `.` to structural headers |
| `agent-core/bin/validate-memory-index.py` | New format, orphan detection |
| `agent-core/bin/validate-learnings.py` | `## Title` pattern |
| `agent-core/skills/handoff/SKILL.md` | Update template for `## Title` format |

### Validation Regex

```python
# Semantic header (##+ without . prefix, excludes #)
SEMANTIC_HEADER = re.compile(r'^(#{2,})\s+(?!\.)(.+)$')

# Structural header (. prefix)
STRUCTURAL_HEADER = re.compile(r'^(#{2,})\s+\.(.+)$')

# Index entry: key — description (description optional)
INDEX_ENTRY = re.compile(r'^([^—\n]+?)(?:\s+—\s+.+)?$')
```

### Workflow

1. Agent adds `## New concept` to learnings.md (via /handoff)
2. `/remember` routes to documentation, creates section `### New concept`
3. `/remember` adds index entry `New concept — brief description`
4. Precommit validates all semantic headers have index entries
5. Orphan → ERROR → commit blocked

## Pending

- [ ] Validate /remember flexibility to create new sections/files
- [ ] Add line-count limit check for archive files in /remember
- [ ] Move append-only directive to `.claude/rules/memory-index.md`

## Documentation Perimeter

**Required reading for implementation:**
- `agents/memory-index.md` — current format
- `agents/learnings.md` — current format
- `agents/decisions/architecture.md` — decision doc structure
- `agent-core/bin/validate-memory-index.py` — current validator
- `agent-core/skills/handoff/SKILL.md` — handoff template

## Next Steps

1. Update memory-index.md format (bare lines, retrieval directive)
2. Convert learnings.md to `## Title` format
3. Update /handoff skill template
4. Migrate decision doc headers (remove `**Key:**`, add `.` to structural)
5. Update validators for new patterns
6. Add orphan fragment check
7. Test with `just precommit`
