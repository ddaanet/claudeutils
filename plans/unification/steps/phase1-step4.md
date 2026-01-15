# Phase 1: Step 4

**Context**: Read `phase1-execution-context.md` for full context before executing this step.

---

### Step 4: Extract Rule Fragments

**Objective**: Extract shared agent behavior rules as markdown fragments.

**Fragments to Create** (design.md:273-283):

#### 4a. communication.md
**Content from**: AGENTS.md:10-16 (Communication Rules)
- Stop on unexpected results
- Wait for explicit instruction
- Be explicit (ask clarifying questions)
- Stop at boundaries

**Technical Note**: This is a direct extraction, verbatim.

#### 4b. delegation.md
**Content from**: AGENTS.md:19-52 (Delegation Principle, Model Selection, Quiet Execution)
- Delegation principle (orchestrator coordinates, doesn't implement)
- Model selection rules (Haiku/Sonnet/Opus)
- Quiet execution pattern (write to files, not context)

**Technical Note**: Includes examples from current AGENTS.md

#### 4c. tool-preferences.md
**Content from**: AGENTS.md:56-68 (Task Agent Tool Usage)
- Use specialized tools instead of Bash
- Specific mapping: LS, Grep, Glob, Read, Write, Edit
- Critical reminder about including in task prompts

**Source Note**: Also informed by Claude Code system prompt fragment (design.md:493)

#### 4d. hashtags.md
**Content**: Restored from old rules (design.md:285-289)
- `#stop` — Stop on unexpected results
- `#delegate` — Delegate to specialized agents
- `#tools` — Use specialized tools over Bash
- `#quiet` — Report to files, minimal context return

**Note**: Select hashtags that add value; avoid over-engineering with too many

**Actions**:
1. Create each fragment in `agent-core/fragments/`
2. Use markdown headers for section organization
3. Include concrete examples where helpful
4. Keep language concise and directive (agent instructions)
5. Add brief header comment explaining fragment purpose

**Validation**:
- [ ] Each fragment is self-contained and readable
- [ ] Examples included where they clarify behavior
- [ ] Language is directive ("Do X", not "Consider doing X")

---


---

**Execution Instructions**:
1. Read phase1-execution-context.md for prerequisites and validation patterns
2. Execute this step following the actions listed above
3. Perform validation checks
4. Document results in execution report
5. Stop on any unexpected results per communication rules
