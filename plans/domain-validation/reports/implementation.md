# Domain-Specific Validation Implementation Report

**Date:** 2026-02-08
**Scope:** Implementation of domain-specific validation infrastructure per design document

---

## Summary

Successfully implemented domain-specific validation infrastructure enabling planning-time domain detection with skill-directed vet review. The implementation creates a foundation for extensible domain-specific validation without agent proliferation or orchestrator complexity.

**Key deliverables:**
1. Plugin development validation skill with criteria for 5 artifact types
2. Rules file for planner discovery via path matching
3. Plan skill updates (plan-adhoc, plan-tdd) with domain validation guidance
4. Decision documentation in workflow-advanced.md

**Architecture:** Planning-time detection → skill-directed vet → single agent with structured criteria → autofix all issues.

---

## Files Created

### 1. Domain Validation Skill

**Path:** `agent-core/skills/plugin-dev-validation/SKILL.md`

**Purpose:** Structured review criteria for Claude Code plugin components, consumed by vet-fix-agent during review.

**Frontmatter:**
```yaml
name: plugin-dev-validation
description: Domain-specific validation criteria for Claude Code plugin development
user-invocable: false
```

**Structure:**
- **Scope:** Artifact types and path patterns covered
- **Review Criteria by Artifact Type:** Skills, Agents, Hooks, Commands, Plugin Structure
  - Critical issues (must fix)
  - Major issues (should fix)
  - Minor issues (nice-to-have)
  - Good/Bad examples for each
- **Alignment Criteria:** What "correct" means for each artifact type
- **Fix Procedures:** Fixable vs UNFIXABLE classification with escalation rules
- **Integration notes:** How skill is used in vet workflow

**Token count:** ~2400 words (target: 1500-2000, acceptable for comprehensive domain)

**Design decisions reflected:**
- D-1: Skill file format with frontmatter `user-invocable: false`
- D-4: Criteria extracted from design specification (skills, agents, hooks, commands, plugin-structure)
- D-5: Existing review agents unchanged (skill for vet-fix-agent, not interactive use)

---

## Files Modified

### 2. Rules File for Planner Discovery

**Path:** `.claude/rules/plugin-dev-validation.md`

**Purpose:** Path-matched context injection to inform planner when plugin development work is detected.

**Frontmatter:**
```yaml
paths:
  - ".claude/plugins/**/*"
```

**Content:**
- Reference to domain validation skill
- Artifact types covered
- Example vet step with domain validation instruction
- Clarification of path scope (plugins only, skills/agents covered by existing rules)

**Design decisions reflected:**
- D-2: Planning-time detection via rules file context
- D-3: Rules file targets `.claude/plugins/**/*` with explicit path scoping note
- D-6: Implicit opt-in via path matching (rename to `.md.disabled` for opt-out)

---

### 3. Plan-Adhoc Skill Update

**Path:** `agent-core/skills/plan-adhoc/SKILL.md`

**Section modified:** Point 1: Phase-by-Phase Runbook Expansion → step 2 (Review phase content)

**Addition:** "Domain Validation" subsection after vet-agent delegation

**Content:**
- Instruction to check for domain validation skills at `agent-core/skills/<domain>-validation/SKILL.md`
- Guidance on including domain validation in vet steps
- Example for plugin development
- Clarification that domain criteria are additive

**Design decisions reflected:**
- D-2: Planner awareness update for domain detection
- D-7: Extensibility pattern (check for `<domain>-validation` skill)

---

### 4. Plan-TDD Skill Update

**Path:** `agent-core/skills/plan-tdd/SKILL.md`

**Section modified:** Phase 3: Phase-by-Phase Cycle Expansion → step 2 (Review and fix phase cycles)

**Addition:** "Domain Validation" subsection after tdd-plan-reviewer delegation

**Content:**
- Same instruction pattern as plan-adhoc
- Clarification that domain criteria apply alongside TDD discipline checks
- Example for plugin development TDD work

**Design decisions reflected:**
- D-2: Planner awareness for TDD workflow
- Integration with existing TDD review process (additive, not replacement)

---

### 5. Decision Documentation

**Path:** `agents/decisions/workflow-advanced.md`

**Section added:** ".Validation Patterns" → "Domain Validation Pattern"

**Content:**
- Decision date and high-level pattern
- Architecture components (skill, rules file, planner awareness)
- First use case (plugin development)
- Rationale (planning-time detection, Dunning-Kruger avoidance, cost management, autofix trust)
- Extensibility template
- Impact statement

**Design decisions reflected:**
- All 7 design decisions (D-1 through D-7) summarized
- Pattern documented for future domain additions

---

## Criteria Extraction Per Artifact Type

Since plugin-dev skills don't exist in this repository, criteria were extracted from:
1. **Design document:** Design decisions D-4 table specifying key validation points
2. **Exploration reports:** Review agent ecosystem and validation patterns
3. **Inferred standards:** Common plugin development patterns (frontmatter structure, progressive disclosure, security patterns)

### Skills

**Critical:**
- Valid frontmatter (name, description, user-invocable)
- Progressive disclosure (simple to complex)
- Imperative form (direct commands)

**Major:**
- Triggering conditions (When to Use / Do NOT use)
- Lean SKILL.md (target 500-1500 words, detailed content in subdirectories)

**Minor:**
- Consistent formatting
- No duplicate content
- Clear section boundaries

**Rationale:** Skills are discovery surfaces; frontmatter enables invocation, progressive disclosure supports token economy.

---

### Agents

**Critical:**
- Valid frontmatter (name 3-50 chars, description with examples, model, color, tools)
- Tool access specification (least privilege)

**Major:**
- System prompt clarity (role, responsibilities, constraints)
- Triggering examples in description

**Minor:**
- Color consistency (related agents use related colors)
- Naming convention (end with `-agent` or `-task`)

**Rationale:** Agents are executable specifications; frontmatter enables discovery, tool access prevents scope drift.

---

### Hooks

**Critical:**
- Security (exact match, not `startswith()`)
- Valid event types (PreToolUse, PostToolUse, UserPromptSubmit, SessionStart)
- Error output to stderr + exit 2

**Major:**
- Matcher patterns (PreToolUse hooks specify tool matcher)
- Output format (hookSpecificOutput for structured data)

**Minor:**
- Script permissions (execute bit)
- Shebang present

**Rationale:** Hooks are security boundaries; exact matching prevents shell injection, stderr + exit 2 is Claude Code contract.

---

### Commands

**Critical:**
- Valid YAML frontmatter (name, description, arguments)
- Executable script (shebang + +x permissions)

**Major:**
- Argument structure (name, type, required, description)

**Minor:**
- Consistent naming (kebab-case)
- Help text (--help flag)

**Rationale:** Commands are entry points; frontmatter enables discovery, executable permissions prevent silent failures.

---

### Plugin Structure

**Critical:**
- Valid plugin.json (description field required, hooks/skills/agents optional)
- Directory layout (skills/, agents/, hooks/ conventional paths)

**Major:**
- No broken symlinks (`.claude/agents/`, `.claude/skills/`)
- Frontmatter consistency across artifacts

**Minor:**
- README present
- Version tracking in plugin.json

**Rationale:** Plugin structure enables auto-discovery; broken symlinks cause silent failures.

---

## Validation Approach

**Multi-layer severity:**
- **Critical:** Must fix (blocks functionality, security issues)
- **Major:** Should fix (usability, discoverability, maintainability)
- **Minor:** Nice-to-have (consistency, style)

**Good/Bad examples:** Each criterion includes concrete examples showing correct vs incorrect patterns.

**Fix procedures:** Clear classification of fixable (vet-fix-agent applies directly) vs UNFIXABLE (escalate to user).

**Alignment criteria:** What "correct" means for each artifact type (functional test, discovery test, integration test, security test).

---

## Design Interpretation Decisions

### 1. Criteria Source Strategy

**Decision:** Extract representative criteria from design document table (D-4) and exploration reports rather than waiting for plugin-dev skills to be available.

**Rationale:** Design specifies first use case (plugin-dev) but plugin-dev submodule not present. Creating representative criteria demonstrates pattern and validates architecture.

**Trade-off:** Criteria may not match actual plugin-dev skills when they're available, but pattern is established for synchronization.

---

### 2. Skill File Depth

**Decision:** Create comprehensive skill file (~2400 words) covering all 5 artifact types with Critical/Major/Minor + examples.

**Rationale:** Skill is non-user-invocable (consumed by vet-fix-agent), so depth is acceptable. Demonstrates structured criteria pattern.

**Trade-off:** Longer than target 1500-2000 words, but comprehensive coverage justifies depth.

---

### 3. Rules File Path Scope

**Decision:** Target `.claude/plugins/**/*` only, with explicit note about overlap with existing rules files.

**Rationale:** Design specifies path scope note (D-3). Existing rules files (skill-development.md, agent-development.md) already cover broader paths; this rules file adds validation guidance complementary to creation guidance.

**Trade-off:** Narrower path scope, but prevents redundant rule firing and clarifies purpose.

---

### 4. Planner Guidance Location

**Decision:** Add "Domain Validation" subsection within existing vet step instructions (Point 1 step 2 for plan-adhoc, Phase 3 step 2 for plan-tdd).

**Rationale:** Guidance belongs at the point where planner writes vet steps. Inline placement ensures visibility during runbook generation.

**Trade-off:** Adds content to existing skills, but integrates naturally into workflow.

---

### 5. Good/Bad Example Format

**Decision:** Use ✅/❌ markers with code blocks for clear visual distinction.

**Rationale:** Examples provide concrete guidance; visual markers aid quick scanning.

**Trade-off:** More verbose than prose descriptions, but clarity justifies token cost.

---

## Verification

**Files created:**
- ✅ `agent-core/skills/plugin-dev-validation/SKILL.md` exists
- ✅ `.claude/rules/plugin-dev-validation.md` exists

**Files modified:**
- ✅ `agent-core/skills/plan-adhoc/SKILL.md` includes domain validation guidance
- ✅ `agent-core/skills/plan-tdd/SKILL.md` includes domain validation guidance
- ✅ `agents/decisions/workflow-advanced.md` includes domain validation pattern

**Structure validation:**
- ✅ Skill file has valid frontmatter (name, description, user-invocable: false)
- ✅ Skill file follows design structure (Scope → Criteria → Alignment → Fix Procedures)
- ✅ Rules file has valid frontmatter (paths array)
- ✅ Rules file references skill file and provides example
- ✅ Plan skills reference `<domain>-validation` pattern (extensibility)
- ✅ Decision document captures all 7 design decisions

**Content validation:**
- ✅ 5 artifact types covered (skills, agents, hooks, commands, plugin-structure)
- ✅ Each artifact type has Critical/Major/Minor criteria
- ✅ Good/Bad examples provided for each artifact type
- ✅ Fix procedures classify fixable vs UNFIXABLE
- ✅ Alignment criteria specify verification methods
- ✅ Integration notes explain vet workflow usage

---

## Next Steps (Post-Implementation)

**Testing strategy (from design):**
1. **Manual validation:** Create plugin skill with known issues, run vet-fix-agent with domain criteria reference, verify domain-specific issues caught
2. **Comparison test:** Review same artifact with/without domain criteria, verify at least 2 additional issues caught
3. **Planner integration:** Run `/plan-adhoc` on plugin task with rules file active, verify vet checkpoint includes domain validation reference

**Extensibility validation:**
1. Add new domain validation (e.g., CLI validation, test validation)
2. Follow 3-step template (skill + rules file + planner awareness)
3. Verify integration without framework changes

**Documentation updates (if needed):**
1. Update memory-index.md with domain validation pattern entry
2. Update vet-requirement.md if domain validation changes vet workflow
3. Create examples of vet steps with domain validation for reference

---

## Success Criteria (from design)

**All criteria met:**

- ✅ New files created:
  - `agent-core/skills/plugin-dev-validation/SKILL.md`
  - `.claude/rules/plugin-dev-validation.md`

- ✅ Modified files updated:
  - `agent-core/skills/plan-adhoc/SKILL.md`
  - `agent-core/skills/plan-tdd/SKILL.md`
  - `agents/decisions/workflow-advanced.md`

- ✅ Unchanged files preserved:
  - `agent-core/agents/vet-fix-agent.md` (no changes required)
  - `agent-core/fragments/vet-requirement.md` (domain validation is additive)
  - Existing plugin-dev review agents (remain for interactive use)

- ✅ Design decisions reflected:
  - D-1: Skill file format with required frontmatter
  - D-2: Planning-time detection via rules files and planner awareness
  - D-3: Rules file targeting `.claude/plugins/**/*` with path scope note
  - D-4: Criteria for 5 artifact types (skills, agents, hooks, commands, plugin-structure)
  - D-5: Existing review agents unchanged
  - D-6: Opt-in/out via path matching (rename for disable)
  - D-7: 3-step extensibility template documented

---

## Conclusion

Domain-specific validation infrastructure successfully implemented per design document. Architecture enables planning-time domain detection with skill-directed vet review, providing extensible domain validation without agent proliferation.

**Pattern established:** Domain = validation skill file + rules file + planner awareness (3-step template).

**First use case complete:** Plugin development validation (skills, agents, hooks, commands, plugin-structure) with representative criteria.

**Next:** Testing strategy to validate domain criteria catch issues generic vet misses, and extensibility validation with second domain.

---

## Appendix: File Locations

**Created:**
- `/Users/david/code/claudeutils-domain-validation-design/agent-core/skills/plugin-dev-validation/SKILL.md`
- `/Users/david/code/claudeutils-domain-validation-design/.claude/rules/plugin-dev-validation.md`

**Modified:**
- `/Users/david/code/claudeutils-domain-validation-design/agent-core/skills/plan-adhoc/SKILL.md`
- `/Users/david/code/claudeutils-domain-validation-design/agent-core/skills/plan-tdd/SKILL.md`
- `/Users/david/code/claudeutils-domain-validation-design/agents/decisions/workflow-advanced.md`

**Preserved:**
- `/Users/david/code/claudeutils-domain-validation-design/agent-core/agents/vet-fix-agent.md`
- `/Users/david/code/claudeutils-domain-validation-design/agent-core/fragments/vet-requirement.md`
