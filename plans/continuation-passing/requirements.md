# Continuation Passing Skill Chaining

## Requirements

### Functional Requirements

**FR-1: Prose continuation syntax**
User can specify skill chain in natural prose: `/skill this, /otherskill and /thirdskill`

**FR-2: Sequential execution**
Skills execute in specified order. Each skill tail-calls the next in the continuation.

**FR-3: Continuation consumption**
Each skill invocation consumes its portion of the continuation and passes remainder to next skill.

**FR-4: Structured continuation**
Support list, paragraph, or section formats for complex continuations with per-skill context:
```
/design
- problem: new feature requirements
- then: /plan-tdd
- finally: /orchestrate with checkpoints
```

**FR-5: Prose-to-explicit translation**
Pure prose in user input must translate to explicit `/skill` references when calling next skill.

**FR-6: Sub-agent isolation**
Continuation directives MUST NOT be injected into sub-agent system prompts when skill spawns agents via Task tool.

**FR-7: Cooperative skill protocol**
First-party skills understand continuation passing without coupling between specific skills.

**FR-8: Uncooperative skill wrapping (optional)**
Mechanism to wrap second/third-party skills with continuation payload for chaining.

### Non-Functional Requirements

**NFR-1: Light cooperation**
Skills only need to understand continuation passing in general, not specific downstream skills.

**NFR-2: Context list for cooperation detection**
Maintain list of cooperative skills to determine whether to include continuation-passing payload.

**NFR-3: Ephemeral continuations**
Continuations are passed through execution, not persisted in agent memory.

### Constraints

**C-1: No sub-agent leakage**
When skill creates sub-agent, continuation context must be stripped from injected system prompt.

**C-2: Explicit stop**
Skill can explicitly terminate chain (no continuation) by completing without tail-call.

---

## Design Outline (from discussion)

### Parsing Model

```
/skill context, /next and /final
       ↓
Skill: "skill"
Context: "context"
Continuation: "/next and /final"
```

After `/skill` completes:
```
/next and /final
     ↓
Skill: "next"
Context: (none)
Continuation: "/final"
```

### Cooperation Levels

| Level | Mechanism | Skills |
|-------|-----------|--------|
| Cooperative | Skill reads continuation, invokes next | First-party |
| Wrapped | Payload explains continuation to unaware skill | Second/third-party |
| Explicit | User manually invokes next skill | Fallback |

### Sub-Agent Isolation

**Problem:** Skill injection into sub-agent system prompt includes continuation directives. Sub-agent might proceed beyond scope.

**Potential solutions:**
- Strip continuation section when building sub-agent prompt
- Gate continuation directives behind `<!-- main-agent-only -->` markers
- Continuation stored in skill invocation context, not skill content

### Open Questions

1. How to detect skill content vs continuation content when parsing?
2. Should continuation be stored as skill metadata or parsed from prose each time?
3. How to handle errors mid-chain (abort vs skip vs retry)?
4. Should cooperative skill list be in CLAUDE.md or separate config?

---

## Analysis

**Token cost:** Minimal. Continuation is already prose the user would write.

**Complexity:** Medium. Parsing is straightforward. Sub-agent isolation is the hard part.

**Dependencies:** None. Can be implemented standalone.

**Risk:** Sub-agent leakage could cause agents to execute beyond intended scope. Requires careful isolation.
