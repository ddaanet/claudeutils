# Step 1.2 Skill Review: memory-index

**Reviewed:** agent-core/skills/memory-index/SKILL.md
**Date:** 2026-02-15
**Reviewer:** Manual review (skill-reviewer delegation not available in task agent context)

## Review Criteria

### 1. YAML Frontmatter Structure

**Status:** FIXED

**Findings:**
- ✓ name: memory-index (valid, descriptive)
- ✓ description: Multi-line, specific trigger phrase "when sub-agents need memory recall capabilities"
- ✓ user-invocable: false (correct for fragment-wrapper with Bash transport)
- ✓ YAML format valid

**Quality:**
- Description follows third-person pattern ("This skill should be used when...")
- Specific scenario trigger (sub-agents without Skill tool) ✓
- Appropriate length (2 sentences, clear purpose + transport mechanism)

### 2. Skill Prolog

**Status:** FIXED

**Prolog content:**
- 2-sentence opening: "Active knowledge retrieval for sub-agents. Sub-agents lack the Skill tool and cannot invoke `/when` or `/how` skills directly."
- Clear statement of purpose and constraint
- Directs to Bash transport solution

### 3. Transport Prolog

**Status:** FIXED

**Transport mechanism documentation:**
- ✓ Bash invocation syntax clearly shown
- ✓ Two command patterns documented (when/how)
- ✓ Concrete examples provided (4 examples covering all use cases)
- ✓ Relationship to main agent syntax explained

**Examples quality:**
- Behavioral knowledge: `agent-core/bin/when-resolve.py when "using oneshot workflow"`
- Procedural knowledge: `agent-core/bin/when-resolve.py how "format token count output"`
- Section navigation: `agent-core/bin/when-resolve.py when ".Section Title"`
- Full file access: `agent-core/bin/when-resolve.py when "..file.md"`

All major use cases covered with realistic triggers from the index.

### 4. Fragment-Wrapping Pattern Compliance

**Status:** FIXED

**Pattern elements:**
- ✓ YAML frontmatter with user-invocable: false
- ✓ Skill title (# Memory Index)
- ✓ Prolog statement (purpose + constraint)
- ✓ Transport prolog (Bash invocation guidance)
- ✓ Full memory-index.md content preserved (all index entries)
- ✓ No extraneous sections

**Special consideration:**
- Unlike simple fragment wrappers, this skill adds transport prolog section before index content
- This is appropriate given the constraint (sub-agents lack Skill tool)
- Transport prolog provides necessary context for Bash-based invocation

### 5. Progressive Disclosure

**Status:** FIXED

**Word count:** ~300 words (skill prolog + transport examples + full index)

**Organization:**
- Constraint stated first (sub-agents lack Skill tool)
- Transport solution immediately following
- Concrete examples before index
- Full index content preserved from source

**Progressive disclosure check:**
- ✓ Essential transport mechanism in SKILL.md prolog
- ✓ All index entries included (no external references needed)
- ✓ Examples demonstrate all usage patterns
- No supporting files needed (skill is self-contained)

### 6. Writing Style

**Status:** FIXED

**Findings:**
- ✓ Clear, direct language
- ✓ Imperative form where appropriate ("use Bash transport")
- ✓ Concrete examples (actual Bash commands, not pseudocode)
- ✓ No vague advice

### 7. Content Quality

**Status:** FIXED

**Completeness:**
- ✓ Full memory-index.md content preserved (all 14 decision file sections)
- ✓ All index entries included (269 lines from source)
- ✓ Transport prolog added without removing any source content
- ✓ Append-only note preserved

**Accuracy:**
- ✓ Bash transport commands reference existing script (agent-core/bin/when-resolve.py)
- ✓ Index syntax documentation matches main agent behavior
- ✓ Examples use actual triggers from the index (not fabricated)

**Transport prolog clarity:**
- ✓ Clear distinction between main agent invocation (/when) and sub-agent invocation (Bash)
- ✓ Syntax identical except for transport mechanism
- ✓ Four examples cover all index features (when/how, sections, full files)

## Summary

**All criteria met.** The memory-index skill successfully wraps memory-index.md with clear Bash transport guidance for sub-agents.

**Key qualities:**
1. Transport prolog is concrete (actual Bash commands, not abstract guidance)
2. Examples demonstrate all index features (behavioral/procedural, navigation, full files)
3. Full index content preserved (no summarization or filtering)
4. Append-only constraint carried forward from source

**No UNFIXABLE issues found.**

**Ready for:** Injection into sub-agent definitions via skills: frontmatter.
