# Requirements Skill (Research)

## Requirements

### Functional Requirements

**FR-1: Conversational collection**
Skill guides user through requirements elicitation via structured questions.

**FR-2: Flexible follow-up**
Can be followed by: /handoff, /design, /plan-adhoc, /plan-tdd.

**FR-3: Requirements artifact**
Produces requirements document that downstream skills consume.

### Non-Functional Requirements

**NFR-1: Lightweight**
Should not duplicate exploration/doc-search phases of design and plan skills.

**NFR-2: Standalone value**
Useful even when user doesn't proceed to design/plan immediately.

---

## Open Questions (Research Needed)

**Q-1: Scope overlap**
Design skill Phase A does exploration + outline. Plan skills do context collection. How does /requirements differ?

**Q-2: Context collection depth**
Options:
- Minimal: Just user requirements, no codebase exploration
- Medium: Requirements + relevant file discovery
- Full: Requirements + exploration + doc search (duplicates design)

**Q-3: Artifact format**
- Inline in conversation?
- Separate requirements.md file?
- YAML frontmatter in design.md?

**Q-4: When to use**
- Before any implementation work?
- Only for complex/unclear requirements?
- As alternative to design for moderate tasks?

---

## Analysis

**User hunch:** Complete exploration may be overkill, duplicates collection in design/plan skills.

**Possible positioning:**
- /requirements = pure user intent capture (no codebase)
- /design = requirements + architecture (with exploration)
- /plan-* = requirements + execution steps (with context)

**Trade-off:** If /requirements does exploration, design/plan must detect and skip. If /requirements is minimal, value-add over just talking to user is unclear.

---

## Recommendation

Defer implementation until design/plan skill requirements sections are working. Evaluate whether separate /requirements skill provides value beyond in-skill requirements capture.
