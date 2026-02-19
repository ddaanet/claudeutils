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

**FR-8: Inline execution in clean session — remove remember-task delegation**
The `/remember` skill executes consolidation inline in the calling session rather than delegating to `remember-task` agent. Requires a clean session (fresh start) to keep context manageable — CLAUDE.md + files being edited, not accumulated conversation history. Delegation throws away loaded context and adds agent startup overhead; inline execution in a bloated session is equally wrong.

Acceptance criteria:
- `/remember` skill steps 1-5 execute in the calling session without Task tool delegation
- Invocation requires clean session (skill documents this as a prerequisite)
- `remember-task` agent is deleted
- Handoff skill consolidation step invokes `/remember` skill inline (no agent)

**FR-9: Inline file splitting — remove memory-refactor delegation**
When a target documentation file exceeds 400 lines during consolidation, the skill splits it inline before proceeding. No delegation to `memory-refactor` agent.

Acceptance criteria:
- After each Write/Edit to a decision file, check line count
- If >400 lines: split by H2/H3 boundaries into 100-300 line sections inline
- Run `validate-memory-index.py --fix` after split
- `memory-refactor` agent is deleted

**FR-10: Rename skill**
Select new name for `/remember` skill (test brainstorm-name agent or manual selection). Update all references: skill directory, SKILL.md, agent definitions, handoff skill, session.md mentions, memory-index triggers. Requires restart after rename.

Acceptance criteria:
- New name selected and documented
- All references updated (skill dir, agents, skills, fragments, session.md)
- `just sync-to-parent` run, symlinks verified
- Restart required flag noted

**FR-11: Agent routing for learnings**
When consolidating learnings actionable for sub-agents, route to agent templates (quiet-task.md, tdd-task.md) as additional consolidation target. Deferred until memory redesign (FR-1 through FR-9) completes — redesign may change the routing surface.

Acceptance criteria:
- Consolidation pipeline identifies agent-relevant learnings
- Relevant entries propagated to agent template files
- Does not execute until FR-1–FR-9 redesign is complete

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
