# Handoff Validation

## Requirements

### Functional Requirements

**FR-1: Full handoff validation**
Validate entire handoff output, not just task specificity:

| Section | Validation |
|---------|------------|
| Completed | Matches actual work done? Artifacts exist? |
| Blockers | Actionable? Specific enough to unblock? |
| Learnings | Novel? Not duplicate? Properly formatted? |
| Pending | Actionable? Has context? Not underspecified? |

**FR-2: Dual validation experiment**
Initially perform both inline validation (during /handoff) AND delegated validation (vet-handoff agent).

**FR-3: Validation tally**
Track accepted review feedback to compare effectiveness of inline vs agent validation.

**FR-4: Non-user-accessible skill**
`vet-handoff` skill should not appear in user-facing skill list (no trigger conditions).

**FR-5: Agent with skill reference**
`vet-handoff` agent references skill via YAML frontmatter.

**FR-6: Requirements capture**
Validation must compare handoff against requirements captured since conversation start.

**FR-7: Decision point**
After N handoffs, make data-driven decision: keep inline, keep agent, or keep both.

### Non-Functional Requirements

**NFR-1: Sonnet-class validation**
Agent validation requires Sonnet (judgment on actionability, consistency).

**NFR-2: Inline validation scope**
Inline validation limited to format/syntax checks (Haiku-equivalent).

**NFR-3: Minimal overhead**
Inline validation adds ≤500 tokens to handoff.

### Constraints

**C-1: Requires continuation passing**
Uses `/handoff, /vet-handoff` chain pattern.

**C-2: Tally persistence**
Tally stored in session.md or dedicated file, survives across sessions.

---

## Design Outline (from discussion)

### Architecture

```
vet-handoff/
  SKILL.md      # Non-user-accessible (empty trigger conditions)

.claude/agents/
  vet-handoff.md  # Agent with skill reference in frontmatter
```

### Validation Flow

```
/handoff
  → Inline self-validation (format, syntax)
  → Write session.md
  → Tail-call: delegate to vet-handoff agent
  → Agent validates (semantic, consistency)
  → Agent appends to tally
  → Return to user
```

### Tally Format

```markdown
## Handoff Validation Tally

| Date | Inline | Agent | Agent-only | Verdict |
|------|--------|-------|------------|---------|
| 02-03 | 2 | 4 | 2 | Agent wins |
| 02-04 | 1 | 2 | 1 | Agent wins |
```

### Agent vs Inline Scope

| Check | Inline | Agent |
|-------|--------|-------|
| Section headers present | Yes | Yes |
| Markdown syntax valid | Yes | Yes |
| Tasks have descriptions | Yes | Yes |
| Tasks are actionable | No | Yes |
| Completed matches artifacts | No | Yes |
| Learnings are novel | No | Yes |
| Blockers are specific | No | Yes |

### Open Questions

1. Where to store tally? session.md section vs dedicated file?
2. Exit criteria: How many handoffs before decision? 10? 20?
3. Should agent validation block handoff or run async?
4. How to capture "requirements since conversation start" for comparison?

---

## Analysis

**Hypothesis:** Inline catches ~30% of issues (format). Agent catches ~80% (semantic + format).

**Expected outcome:** Agent validation significantly outperforms inline for semantic issues.

**Fallback:** If parity, keep only inline (cheaper).

**Dependencies:** Continuation passing skill chaining (FR-1, C-1).

**Token cost:**
- Inline: ~500 tokens added to /handoff
- Agent: ~2000-4000 tokens for Sonnet delegation

**Risk:** Agent validation adds latency. May be acceptable if findings are valuable.
