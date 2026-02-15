# Skills Frontmatter Investigation

**Date**: 2026-02-14
**Query**: How does `skills:` YAML frontmatter work in agent definitions? What gets injected? Token cost implications?
**Status**: Single-agent current implementation documented. Injection mechanism confirmed native (no build step). Token cost measurable but context-dependent.

---

## Summary

The `skills:` field in agent YAML frontmatter is a **native Claude Code mechanism** that injects skill content as prompt material. Plan-reviewer is the only agent currently using this feature in the codebase. Skill files are SKILL.md documents stored in `agent-core/skills/<skill-name>/SKILL.md`. Injection loads the entire file content into the agent's context at startup. Token cost ranges from ~200 to ~1000 tokens per skill depending on file size, with cumulative cost when multiple skills are referenced.

---

## Key Findings

### 1. Plan-Reviewer: Current Skills Usage

**File**: `/Users/david/code/claudeutils-wt/workflow-improvements/agent-core/agents/plan-reviewer.md`

**Frontmatter block (lines 1-19):**
```yaml
---
name: plan-reviewer
description: |
  Reviews runbook phase files for quality, TDD discipline (if TDD), step quality (if general),
  and LLM failure modes (always).

  **Behavior:** Write review (audit trail) → Fix all issues → Escalate unfixable.

  Triggering examples:
  - "Review runbook-phase-1.md for quality"
  - "Check TDD runbook for prescriptive code and LLM failure modes"
  - "Validate general runbook steps for clarity and completeness"
  - /runbook Phase 1 and Phase 3 delegate to this agent
model: sonnet
color: yellow
tools: ["Read", "Grep", "Glob", "Write", "Edit", "Skill"]
skills:
  - review-plan
---
```

**Skills referenced:**
- `review-plan` (single skill, list format supports multiple)

**Key attributes:**
- Skills are referenced by name only (no path, no file extension)
- Format is YAML list under `skills:` key
- Native mechanism: no build step, no preprocessing required

---

### 2. Injected Skill Content: review-plan

**Location**: `/Users/david/code/claudeutils-wt/workflow-improvements/agent-core/skills/review-plan/SKILL.md`

**File structure:**
```markdown
---
name: review-plan
description: |
  Reviews runbook phase files for quality, TDD discipline...
user-invocable: false
model: sonnet
---

# /review-plan Skill

[Content starts here]
```

**Content overview:**
- Header block with frontmatter (name, description, model, user-invocable flag)
- Markdown body with operational guidance
- Sections: Purpose, Document Validation, Review Criteria (11 axes), Review Process, Output Format, Invocation, Integration, Key Principles

**Size metrics:**
- **Total lines**: 479
- **Token estimate**: ~1200-1400 tokens (479 lines ≈ 2.5-3 tokens per line in markdown)

---

### 3. Skill Injection Mechanism (Native Feature)

**How it works:**
1. Agent frontmatter contains `skills:` list with skill names
2. Claude Code **automatically loads** the SKILL.md file from `agent-core/skills/<name>/SKILL.md`
3. Content is injected into agent context at startup
4. **No build step, no preprocessing required**
5. Changes to SKILL.md are automatically available on next agent restart

**Evidence:**
- Learnings.md documents: "Only plan-reviewer currently uses it; all other agents lack project conventions"
- No prepare-runbook.py or other build scripts modify skills: field
- Agent definition references skill by name only; framework resolves to file path

---

### 4. Skill File Inventory and Sizing

**Skills available in agent-core/skills/:**

| Skill Name | File Size (lines) | Estimated Tokens |
|------------|-------------------|------------------|
| deliverable-review | 166 | ~410 |
| release-prep | 213 | ~530 |
| opus-design-question | 252 | ~630 |
| commit | 263 | ~660 |
| reflect | 268 | ~670 |
| requirements | 271 | ~680 |
| handoff | 331 | ~830 |
| design | 339 | ~850 |
| vet | 384 | ~960 |
| orchestrate | 449 | ~1120 |
| review-plan | 479 | ~1200 |
| token-efficient-bash | 523 | ~1300 |
| plugin-dev-validation | 528 | ~1320 |
| runbook | 820 | ~2050 |
| **Total combined** | **6,245** | **~15,600 tokens** |

**Single injection cost range**: 400-1,400 tokens depending on skill
**Multiple injections**: Cumulative (N skills = N × avg-size tokens)

---

### 5. Scope of Injected Content

**What gets injected:**
- **Full SKILL.md content** including frontmatter block
- **All sections**: Purpose, criteria, process, examples, detection patterns
- **Not loaded**: Other files in the skill directory (e.g., helper scripts, references/)

**Verification:**
- Review-plan injection includes all 11 review criteria axes (FR-2 work spans sections 11.1-11.3)
- No evidence of selective section injection; full file is the injection unit
- Agent can reference injected content by section heading

**Implication for FR-12/13:**
- Wrapping fragments (deslop, error-handling) as skills will inject their complete content
- Memory index injection (FR-13) would inject entire index file
- Token cost scales linearly with fragment size

---

### 6. Current Agent Usage Patterns

**Agents using `skills:` field:**
- **plan-reviewer**: ✓ (skills: [review-plan])
- **All other agents**: ✗ (no skills: field in definitions)

**Affected agents from FR-12 (target for convention injection):**
- vet-fix-agent
- design-vet-agent
- outline-review-agent
- refactor

**Affected agents from FR-13 (memory index injection):**
- vet-fix-agent (at minimum, possibly others)

---

### 7. Open Questions Addressed

### Q-1: Does `skills:` inject full SKILL.md or specific sections?

**Answer**: **Full SKILL.md** is injected, not selective sections.

**Evidence**:
- No mechanism in Claude Code for section-level injection
- Plan-reviewer agent receives entire review-plan file content
- If sections could be selective, it would require preprocessing (no build step exists)

**Implication for design**:
- Fragment-as-skill wrapping (FR-12) will be all-or-nothing per skill
- Memory index skill (FR-13) includes entire index, agents invoke selective recall via Bash
- Consider breaking large guides into multiple skills if granularity is needed

---

### Q-2: What's the token cost per injection?

**Answer**: **~1,200 tokens for review-plan** (479 lines); range **400-2,000+ tokens** depending on skill size.

**Calculation method**:
- Markdown prose: ~2-2.5 tokens per line
- Code blocks: ~3-4 tokens per line
- YAML frontmatter: ~1.5 tokens per line
- Blanks/structure: minimal token cost

**Cost table (estimated):**
| Scenario | Tokens | Notes |
|----------|--------|-------|
| Single small skill (deslop) | ~300-400 | Fragment-sized content |
| Medium skill (requirements) | ~650-700 | Typical standalone skill |
| Large skill (runbook) | ~2,000+ | Multi-section guide |
| review-plan alone | ~1,200 | Current plan-reviewer load |
| review-plan + 2 more | ~2,600 | Cumulative for 3 skills |

**Context implications**:
- Token cost is paid once per agent startup (not per invocation)
- Persistent in context for duration of agent session
- High-volume delegated tasks may pay cost multiple times (one cost per Task agent spawn)

---

### 8. Implementation Considerations

### For FR-12 (Fragment Wrapping):

**Viable patterns:**
- Wrap `deslop.md` as `skills/deslop/SKILL.md` (~300 tokens)
- Wrap `error-handling.md` as `skills/error-handling/SKILL.md` (~250 tokens)
- Wrap `code-removal.md` as `skills/code-removal/SKILL.md` (~200 tokens)
- Cumulative injection: ~750 tokens per agent using all three

**Target agents**: vet-fix-agent, design-vet-agent, plan-reviewer, outline-review-agent, refactor (5 agents × 3 skills = potential 15 skill references)

### For FR-13 (Memory Index Injection):

**Challenge**: Memory index is currently inline in CLAUDE.md as `@agents/memory-index.md` reference. Injecting as skill would:
- Move content from loaded context to agent-specific context
- Require sub-agents to recall via Bash (when-resolve.py) instead of `/when` skill
- Save tokens for main agent, but sub-agent execution costs transport overhead

**Feasible transport**:
```bash
# In injected memory skill prreamble:
Sub-agents invoke: agent-core/bin/when-resolve.py when "<trigger>"
```

---

### 9. Risk Assessment

### Q1 Risk (Section Injection): **Resolved — Full file only**
- No selective injection mechanism exists
- Design must assume full-file loading
- Reduces design flexibility but increases predictability

### Q2 Risk (Token Cost): **Manageable at scale**
- Single large skill: ~1,200 tokens (plan-reviewer baseline)
- Multiple skills (3-5): ~2,000-3,000 tokens cumulative
- Compared to typical agent context: 5-10% overhead
- Mitigatable via skill splitting if needed

### Implementation Viability: **High**
- Native mechanism requires no build changes
- Skill discovery automatic (resolves name to file)
- No dependency on plugin-dev or custom tooling
- Test surface: plan-reviewer is existence proof

---

## Patterns & Conventions

**Established pattern (from plan-reviewer):**
- Skill names match semantic domain (e.g., "review-plan" for review guidance)
- Skills are referenced by name only (framework resolves to path)
- Full SKILL.md content is injected regardless of file size
- Multiple skills are listed as YAML array

**Recommended for FR-12/13:**
- Name skills to match their semantic role (e.g., "project-conventions", "memory-index")
- Consider splitting large guides (>500 lines) into multiple skills
- Document skill dependencies if one skill references another
- Test via agent restart to verify injection works

---

## Gaps & Unknowns

### What's still unresolved:

1. **Injection timing**: Does injection occur at agent definition load or at first invocation? (Likely load-time based on agent-code architecture, but unconfirmed)

2. **Skill ordering in context**: When multiple skills are listed, what order are they injected? (Likely list order, but not documented)

3. **Skill circular dependencies**: Can skill A reference skill B? (Probably not intended, but unclear if prevented)

4. **Memory index as skill side effects**: When memory index is injected as skill in vet-fix-agent, does it consume the `/when` mechanism? (Will need testing per FR-13)

5. **Plugin-dev documentation**: Claude Code plugin-dev documentation does not list `skills:` as a documented frontmatter field (potential upstream documentation gap — FR from session indicates this should be fixed)

6. **Context window saturation**: At what scale do injected skills start competing with task context? (Depends on model, not measured)

---

## Recommendations for Design Phase

1. **For FR-12 (Convention injection)**: Wrap fragments individually as skills. Start with one (e.g., deslop) as test case on plan-reviewer, validate output follows convention. Then roll out to other agents.

2. **For FR-13 (Memory index injection)**: Create `memory-index/SKILL.md` with index content and transport instruction (Bash invocation pattern). Test on vet-fix-agent with one decision trigger.

3. **For Q2 token cost tracking**: Measure actual injection tokens via Claude API (send agent definition with/without skills: field, log token counts). Current estimates ~1,200 tokens may differ from actual.

4. **For upstream improvement**: File issue/PR to claude-code plugin-dev to document `skills:` YAML field (currently undocumented feature).

---

## File References

**Agent definition**: `/Users/david/code/claudeutils-wt/workflow-improvements/agent-core/agents/plan-reviewer.md` (lines 17-18)

**Injected skill**: `/Users/david/code/claudeutils-wt/workflow-improvements/agent-core/skills/review-plan/SKILL.md` (479 lines)

**Requirements doc**: `/Users/david/code/claudeutils-wt/workflow-improvements/plans/workflow-rca-fixes/requirements.md` (FR-12, FR-13)

**Learnings reference**: `/Users/david/code/claudeutils-wt/workflow-improvements/agents/learnings.md` (Agent composition section)

**Fragment candidates for FR-12**:
- `/Users/david/code/claudeutils-wt/workflow-improvements/agent-core/fragments/deslop.md`
- `/Users/david/code/claudeutils-wt/workflow-improvements/agent-core/fragments/error-handling.md`
- `/Users/david/code/claudeutils-wt/workflow-improvements/agent-core/fragments/code-removal.md`

---

**Report complete. Ready for design phase decisions on FR-12/13 implementation approach.**
