# Remember Skill Update

## Requirements

### Functional Requirements

**FR-1: Titles use When/How prefix**
Every learning title in `agents/learnings.md` must start with "When" or "How to" — matching the decision file heading convention and `/when`/`/how` operator format.

Acceptance criteria:
- Title starts with `## When ` or `## How to `
- Title reads naturally as a trigger: `/when <rest of title>` or `/how <rest of title>`
- Title describes the **situation an agent encounters**, not root cause or jargon

Examples from existing decision files:
- `### When Placing Deliverable Artifacts`
- `### When Launching Task Agents In Parallel`
- `### How to End Workflow With Handoff And Commit`

**FR-2: Titles comply with validation rules**
Titles must pass existing learnings.py validation and be compatible with planned validation:

- Max 5 words (enforced, includes "When"/"How to")
- Unique (enforced)
- Min 2 words (planned — Workstream 1 Phase 1)
- No special characters beyond alphanumeric + spaces (planned): no hyphens, colons, slashes, dots, camelCase exceptions only for actual setting/API names

**FR-3: Structural validation enforced at precommit**
learnings.py updated with:
- Min 2 words check
- Special character detection
- When/How prefix check
- Existing checks preserved (max 5 words, uniqueness, H2 format)

**FR-4: Consolidation pipeline is mechanical**
Consolidation pipeline: `## When X` → `### When X` (decision heading, title case) → `/when x` (index trigger, lowercased). No agent rephrasing step. Remember skill Step 4a and remember-task agent updated to derive triggers directly from title.

**FR-5: Semantic guidance in skill and handoff docs**
Update remember SKILL.md, remember-task agent, and handoff skill with:
- Title must start with "When" or "How to"
- Anti-pattern/correct-pattern examples
- Reject jargon/root-cause titles with suggested rephrase

**FR-6: Frozen-domain recall analysis**
Evaluate alternatives to rule files for proactive knowledge recall:
- Options: status quo, PreToolUse hook, inline code comments, UserPromptSubmit topic detection
- Criteria: agent-independence, token cost, false positive rate, maintenance burden
- Output: analysis with recommendation (not implementation)

**FR-7: Migrate existing learning titles**
Apply When/How prefix format to 64 entries introduced after last consolidation (commit `8a62c85`). The 6 retained entries from consolidation are out of scope. Fix formatting defect at line 378 (heading concatenated to previous bullet).

### Constraints

**C-1: Title IS the trigger — no rephrasing during consolidation**
The learning title must be directly usable as a memory-index trigger without agent judgment at consolidation time.

**C-2: Word count includes prefix**
"When" and "How to" count toward the 5-word max. Effective content words: 4 (for When) or 3 (for How to).

**C-3: Migration preserves body content**
Title migration changes only `## ` lines. Body text (anti-pattern, correct pattern, rationale, evidence) remains unchanged.

### Out of Scope

- `/when` runtime resolution changes
- Memory index validation pipeline changes
- Hook implementation for frozen-domain (separate task if recommended by FR-6)
- `agent-core/bin/compress-key.py` changes
- Body content rewrites during migration

### Dependencies

- Phase 1 (validation) should precede Phase 2 (documentation) — docs reference validation constraints
- Phase 3 (frozen-domain analysis) is independent
- FR-7 (migration) can execute before or after validation enforcement

### Open Questions

- Q-1: Hyphen handling — allow in learning titles or enforce no-hyphens? Recommend: no hyphens (aligns with memory-index trigger format)
