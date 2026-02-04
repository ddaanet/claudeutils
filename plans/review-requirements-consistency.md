# Requirements Consistency Review

**Review Date:** 2026-02-03
**Reviewer:** design-vet-agent (opus)

## Summary

Reviewed 7 requirements/design documents for internal consistency, cross-document consistency, and alignment with existing project documentation. Found several critical and major inconsistencies between proposed changes and the current implementation state, as well as format contradictions within the document set itself.

**Overall Assessment:** Needs Significant Changes

---

## Documents Reviewed

| Document | Type |
|----------|------|
| `plans/memory-index-update/requirements.md` | Requirements |
| `plans/memory-index-update/design.md` | Design |
| `plans/validator-consolidation/requirements.md` | Requirements |
| `plans/task-prose-keys/requirements.md` | Requirements |
| `plans/requirements-skill/requirements.md` | Requirements |
| `plans/continuation-passing/requirements.md` | Requirements |
| `plans/handoff-validation/requirements.md` | Requirements |

---

## Critical Issues

### 1. Learnings Format Contradiction: `**Title:**` vs `## Title`

**Problem:** Documents disagree on the learnings format change direction.

| Document | Proposed Format |
|----------|-----------------|
| `memory-index-update/design.md` (D-4) | `## Title` headers (no blank line after) |
| `validator-consolidation/requirements.md` (FR-2) | `## Title` header (semantic, `.` prefix for structural) |

**Current state (learnings.md):** Uses `**Title:**` format (bold with colon).

**Current validator (validate-learnings.py):** Expects `**Title:**` pattern.

**Contradiction:** The design documents propose `## Title` format, but the user's key decisions to verify list states: "Learnings format: `## Title` headers (no blank line after)". However, this contradicts the current implementation which uses `**Title:**`.

**Impact:** If implemented as proposed, requires:
- Rewriting all 20+ learning entries
- Updating validate-learnings.py regex from `^\*\*(.+?):\*\*$` to `^## (.+)$`
- Updating /handoff skill template

**Recommendation:** Confirm the desired direction. The `## Title` format is cleaner and aligns better with markdown semantics, but represents a breaking change from current state.

---

### 2. Memory Index Format: Current vs Proposed Contradiction

**Problem:** Proposed format differs significantly from current implementation.

**Current format (memory-index.md):**
```markdown
## Behavioral Rules

- Tool batching unsolved
- Delegation with context
- Three-tier assessment
```
Uses list markers (`- `) with title-only entries.

**Proposed format (memory-index-update/requirements.md):**
```markdown
## Behavioral Rules
Tool batching unsolved - docs unreliable, hookify bloats context
Delegation with context - don't delegate when context loaded
```
Uses bare lines with keyword phrases.

**Token counts claimed in requirements.md:**
- bare lines: 49 tokens
- pipes: 50 tokens
- list markers: 57 tokens

**Contradiction with session.md:** The session handoff states "Memory-index rewritten as title-only list with 74% token reduction" - implying the current format (list markers, title-only) was the result of optimization, not the starting point.

**Impact:** Changing from list markers to bare lines AND adding keyword phrases simultaneously is two changes, not one. The token analysis appears to compare 8 bare-line entries with keyword phrases vs 8 list-marker entries (presumably with the same content), but the current format has NO keyword phrases.

**Recommendation:** Clarify the baseline:
1. Are we adding keyword phrases to existing list format?
2. Are we removing list markers from title-only format?
3. Are we doing both simultaneously?

Each has different token impact.

---

### 3. Semantic Header Marker: `.` Prefix Scope Ambiguity

**Problem:** Documents are inconsistent about where the `.` prefix structural marker applies.

**memory-index-update/design.md D-1:** States semantic headers include `##`, `###`, `####` - structural headers use `.` prefix on any level.

**validator-consolidation/requirements.md FR-2:** States title format is `## Title` header with "no marker for semantic, `.` prefix for structural" - implies only `##` level.

**Current validators:** Neither validator implements this pattern yet.

**Impact:** If `.` prefix applies to ALL header levels (##, ###, ####), the implementation is more complex. The orphan detection must recursively check nested semantic sections.

**Recommendation:** Explicitly state in requirements whether `.` prefix applies to:
- Only `##` level
- All `##`+ levels
- Specific files only (learnings.md, decisions/*.md, or all markdown)

---

## Major Issues

### 4. Orphan Detection: File Scope Not Specified

**Problem:** design.md D-5 specifies orphan detection for `agents/decisions/*.md` and `agents/learnings.md`, but the memory-index.md header states index entries come from knowledge that "requires on-demand loading".

**Current memory-index.md header:**
> Do not index content already loaded via CLAUDE.md. Fragments referenced by `@` are in every conversation.

**Implication:** Semantic headers in `agent-core/fragments/*.md` should NOT be indexed (they're loaded via `@`), but semantic headers in `agents/decisions/*.md` SHOULD be indexed.

**Missing specification:** The orphan detection rule needs explicit file scope:
- Which files are indexed (require index entries)?
- Which files are exempt (loaded via CLAUDE.md)?

**Recommendation:** Add explicit file scope to requirements:
```
Indexed (orphan check applies):
- agents/decisions/*.md
- agents/learnings.md

Exempt (no orphan check):
- agent-core/fragments/*.md (loaded via CLAUDE.md @)
- CLAUDE.md itself
- session.md (ephemeral)
```

---

### 5. Task Prose Keys: Format Contradiction with Current session.md

**Problem:** task-prose-keys/requirements.md proposes removing hash tokens and using task name as key.

**Current session.md format:**
```markdown
- [ ] **Orchestrator scope consolidation** #E7u8A - delegate checkpoint phases | sonnet
```

**Proposed format:**
```markdown
- [ ] **Orchestrator scope consolidation** - delegate checkpoint phases | sonnet
```

**execute-rule.md fragment states:**
> Token: 5-char base62 identifier (written as `#PNDNG` by handoff, replaced by precommit)

**Contradiction:** The existing `#PNDNG` system and `task-context.sh` script depend on hash tokens for context recovery. The requirements document acknowledges this ("FR-5: Context recovery") but doesn't specify migration path for existing tokens.

**Recommendation:** Add migration requirements:
- How to handle existing tasks with hash tokens?
- Does task-context.sh need rewriting?
- What's the transition period?

---

### 6. Validator Consolidation: Incomplete Migration Path

**Problem:** validator-consolidation/requirements.md proposes consolidating scripts to `src/claudeutils/validation.py` but doesn't address agent-core submodule isolation.

**Current structure:**
- `agent-core/bin/validate-learnings.py` - in submodule
- `agent-core/bin/validate-memory-index.py` - in submodule

**Proposed structure:**
- `src/claudeutils/validation.py` - in main package

**Missing consideration:** agent-core is designed as a reusable submodule. Moving validators to claudeutils package breaks submodule portability.

**Recommendation:** Either:
1. Keep validators in agent-core, have claudeutils import them
2. Accept that validation is claudeutils-specific and document the coupling
3. Create shared validation primitives in agent-core, with claudeutils-specific wiring

---

### 7. Handoff Validation: Dependency on Unimplemented Feature

**Problem:** handoff-validation/requirements.md C-1 states: "Requires continuation passing" and references the pattern `/handoff, /vet-handoff`.

**Status of continuation-passing:** Still in requirements stage (plans/continuation-passing/requirements.md), with open questions about implementation.

**Impact:** Handoff validation cannot be implemented until continuation passing is complete.

**Recommendation:** Either:
1. Remove continuation passing dependency and use explicit two-step invocation
2. Mark handoff-validation as blocked by continuation-passing
3. Add continuation-passing to implementation order prerequisites

---

## Minor Issues

### 8. Requirements Skill: Research Status Not Actionable

**Note:** requirements-skill/requirements.md ends with "Defer implementation until design/plan skill requirements sections are working" but doesn't specify what "working" means.

**Recommendation:** Add success criteria for when this deferred work should be revisited.

---

### 9. Token Count Verification Needed

**Note:** memory-index-update/requirements.md claims "bare lines 14% cheaper than `- ` prefixed (49 vs 57 tokens for 8 entries)".

**Verification needed:** The 8-token difference for 8 entries (1 token per line for `- `) seems plausible but should be verified with actual token counting.

---

### 10. Continuation Passing: Sub-Agent Isolation Complexity

**Note:** continuation-passing/requirements.md FR-6 requires "Continuation directives MUST NOT be injected into sub-agent system prompts" but the mechanism is listed as an open question.

**Recommendation:** Resolve open questions before planning phase.

---

## Consistency with Existing Documentation

### Alignments (Positive)

1. **CLAUDE.md as root marker:** validator-consolidation/requirements.md C-2 correctly specifies CLAUDE.md as root marker, aligning with learnings.md "Root marker for scripts" entry.

2. **Title-words over kebab-case:** memory-index-update approach aligns with learnings.md "Title-words beat kebab-case" finding.

3. **Append-only index:** memory-index-update preserves the append-only pattern documented in architecture.md "Memory index append-only" decision.

4. **Three-tier assessment:** validator-consolidation scope aligns with the three-tier assessment pattern in workflows.md.

### Conflicts Requiring Resolution

1. **Current validators vs proposed format:** Validators expect `**Title:**` but design proposes `## Title`.

2. **Index format:** Current has list markers, design removes them - but both claim to be "optimized".

3. **Task tokens:** execute-rule.md documents `#PNDNG` system, task-prose-keys proposes removing it.

---

## Recommendations

### Priority Order for Resolution

1. ~~**Resolve learnings format decision:** `**Title:**` vs `## Title`~~ — **RESOLVED:** `## Title` validated
2. ~~**Clarify memory index baseline:** What are we comparing against?~~ — **RESOLVED:** Baseline is commit 48f5 (verbose format)
3. ~~**Specify orphan detection file scope:** Which files are indexed?~~ — **RESOLVED:** Consolidated learning files only (decisions/*.md, learnings.md), fragments exempt
4. **Define continuation-passing dependency:** Block or decouple?
5. ~~**Address agent-core submodule isolation:** Validator location decision~~ — **RESOLVED:** claudeutils is dependency of agent-core, validators live in claudeutils

### Implementation Order (if approved)

1. memory-index-update (establishes new formats)
2. validator-consolidation (implements validation for new formats)
3. task-prose-keys (depends on validator infrastructure)
4. continuation-passing (standalone feature)
5. handoff-validation (depends on continuation-passing)
6. requirements-skill (deferred pending evaluation)

---

## Next Steps

1. User review of format decisions (learnings: `**Title:**` vs `## Title`)
2. Clarify memory-index baseline for token comparison
3. Define file scope for orphan detection
4. Decide on agent-core coupling for validators
5. Revise requirements documents with clarifications
6. Re-review revised documents before planning
