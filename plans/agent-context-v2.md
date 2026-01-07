# Agent Context Architecture v2 - Implementation Plan

**Date:** 2026-01-07
**Status:** Ready for implementation
**Audience:** Sonnet agent (careful wording required)

---

## Design Overview

### Files After Migration

| File | Lines | Updates | Contains |
|------|-------|---------|----------|
| AGENTS.md | ~50 | Monthly | Fallback rules, pointers |
| agents/context.md | ≤100 | 12-15×/day | State, handoff, decisions, blockers |
| agents/role-*.md | Varies | Weekly | Domain rules + context.md pointer |
| START.md | **DELETE** | — | Consolidated into context.md |

### Key Decisions

1. **AGENTS.md:** Slim to ~50 lines (rules + pointers only)
2. **agents/context.md:** 100 line hard cap, 4-section structure
3. **START.md:** Eliminate - merge into context.md handoff section
4. **Flushing:** Archive to `agents/archive/{date}-context.md` when >100 lines

### Agent Boot Sequence

```
Role file exists? → Read agents/role-{role}.md : Read AGENTS.md
→ Always read agents/context.md
→ Execute task
→ Update agents/context.md before exit
```

---

## Files Requiring Changes

### Critical Updates (Order Matters)

1. **agents/modules/src/memory-management.semantic.md**
   - Line 18: Update AGENTS.md size estimate (~50 rules)
   - Line 50: Change `START.md` → `agents/context.md`, clarify scope
   - **Why critical:** Instructs agents what files to update

2. **agents/modules/src/handoff.semantic.md**
   - Lines 9, 42: Review "session end" references
   - Line 24: Update completion file guidance if needed
   - **Why critical:** Defines handoff protocol

3. **AGENTS.md**
   - Strip to ~50 lines: core rules + pointers only
   - Add pointer: "Read agents/context.md for current state"
   - Remove: project architecture, current status

4. **agents/context.md** (formerly session.md)
   - Apply 4-section structure:
     - Current State (10-20 lines)
     - Handoff (5-10 lines) ← absorbs START.md content
     - Recent Decisions (20-30 lines)
     - Blockers (5-10 lines)
   - Archive excess content to `agents/archive/2026-01-07-context.md`

5. **START.md**
   - Extract handoff content → agents/context.md#Handoff
   - Delete file

### Role Files (Batch Update)

All 7 files in `agents/role-*.md`:
- Add after frontmatter: "Read agents/context.md for current state."
- Verify no duplication of AGENTS.md fallback rules

Files:
- agents/role-planning.md
- agents/role-code.md
- agents/role-lint.md
- agents/role-refactor.md
- agents/role-execute.md
- agents/role-review.md
- agents/role-remember.md

### Module Sources (Context References)

Review and update if needed:
- agents/modules/src/context-commands.semantic.md (lines 42-43)
- agents/modules/src/context-datamodel.semantic.md (line 36)
- agents/modules/src/context-overview.semantic.md (lines 31-32)
- agents/modules/src/commit.semantic.md (line 9)

### Infrastructure

Create:
- `agents/archive/` directory
- `agents/archive/.gitkeep`

### Reference Updates (Search & Replace)

Search all `.md` files for:
- `START.md` → Update to `agents/context.md#Handoff`
- `session.md` → Update to `agents/context.md`

Likely locations:
- agents/design-decisions.md
- agents/modules/MODULE_INVENTORY.md
- plans/**/*.md

---

## Migration Steps (Sequential)

### Phase 1: Infrastructure Setup
```bash
mkdir -p agents/archive
touch agents/archive/.gitkeep
git add agents/archive/.gitkeep
```
**Checkpoint:** `ls agents/archive/.gitkeep` succeeds

### Phase 2: Archive Current Context
```bash
cp agents/context.md agents/archive/2026-01-07-context.md
git add agents/archive/2026-01-07-context.md
```
**Checkpoint:** Archive file exists with full content

### Phase 3: Update Critical Module Sources

**File:** `agents/modules/src/memory-management.semantic.md`

**Line 18 - Change:**
```diff
-Target: AGENTS.md (~40 rules) + role file, total <= 150 rules. Fewer is better. Budget...
+Target: AGENTS.md (~10 rules fallback) + role file (~100 rules) ≤ 150 total. Fewer is better.
```

**Line 50 - Change:**
```diff
-Update: AGENTS.md, START.md, role files, rule files. Do NOT update: README.md, test...
+Update: AGENTS.md (fallback rules only), agents/context.md (current state), role files, rule files. Do NOT update: README.md, tests, plans.
```

**File:** `agents/modules/src/handoff.semantic.md`

**Line 42 - Change:**
```diff
-- Blockers or questions for next session
+- Blockers or questions for next agent (document in agents/context.md#Blockers)
```

**Checkpoint:** Both files updated, validated with `git diff agents/modules/src/`

### Phase 4: Restructure agents/context.md

**Template to apply:**
```markdown
# Context

## Current State

Continuing from [2026-01-07 archive](agents/archive/2026-01-07-context.md).

Branch: markdown
Current focus: [Extract from old context]

## Handoff

[Merge START.md "Next Steps" section here]

## Recent Decisions

[Keep last 2-3 decisions from old context]

## Blockers

[Carry forward unresolved blockers only]
```

**Action:** Read old context + START.md, compose new structure, enforce ≤100 lines

**Checkpoint:** `wc -l agents/context.md` returns ≤100

### Phase 5: Slim AGENTS.md

**Target structure:**
```markdown
# Agent Instructions

## Communication Rules
- Terse responses (markdown formatted)
- No emojis unless requested
- Code examples in fenced blocks

## Tool Batching
- Parallel: Independent operations
- Sequential: Dependencies (use &&)

## Navigation
- **Role-specific rules:** See agents/role-*.md
- **Current work state:** Read agents/context.md
- **Project decisions:** See agents/design-decisions.md
```

**Extract and move:**
- Project architecture → Appropriate role files
- Data models → Keep pointer, details in design-decisions.md
- Command reference → Keep minimal version or move

**Checkpoint:** `wc -l AGENTS.md` ≤ 60 (target 50, buffer 10)

### Phase 6: Delete START.md
```bash
git rm START.md
```
**Checkpoint:** `ls START.md` fails

### Phase 7: Update Role Files

**For each file in agents/role-*.md:**

Add after YAML frontmatter or intro section:
```markdown
**Current work context:** Read agents/context.md before starting tasks.
```

**Checkpoint:** `grep -l "context.md" agents/role-*.md | wc -l` returns 7

### Phase 8: Global Reference Updates

```bash
# Search for stale references
grep -r "START\.md" --include="*.md" .
grep -r "session\.md" --include="*.md" .

# Update each file found
# Common locations:
# - agents/design-decisions.md
# - agents/modules/MODULE_INVENTORY.md
# - plans/markdown/*.md
# - plans/prompt-composer/*.md
```

**Update pattern:**
- `START.md` → `agents/context.md` (with section anchor if applicable)
- `session.md` → `agents/context.md`

**Checkpoint:** No matches for `grep -r "START\.md\|session\.md" --include="*.md" agents/ plans/` (excluding archive)

### Phase 9: Validation

**Verify structure:**
```bash
# File sizes
wc -l AGENTS.md                    # Should be ~50
wc -l agents/context.md            # Should be ≤100
ls START.md 2>/dev/null            # Should fail

# Content checks
grep "context.md" agents/role-*.md  # All 7 should match
ls agents/archive/2026-01-07-context.md  # Should exist
```

**Verify no broken references:**
```bash
# These should return no results (or only in archive/)
grep -r "START\.md" --include="*.md" agents/ plans/
grep -r "session\.md" --include="*.md" agents/ plans/
```

**Checkpoint:** All validation passes

### Phase 10: Commit

```bash
git add -A
git commit -m "Restructure agent context architecture (v2)

- Slim AGENTS.md to ~50 lines (fallback rules + pointers only)
- Restructure agents/context.md with 4-section template (≤100 lines)
- Delete START.md (consolidated into context.md#Handoff)
- Create agents/archive/ for flushed context
- Update all role files to reference context.md
- Update module sources (memory-management, handoff)
- Update all documentation references

Architecture: Role file OR AGENTS.md → context.md → execute"
```

**Checkpoint:** Clean git status

---

## Validation Checklist

- [ ] agents/archive/ directory exists with .gitkeep
- [ ] agents/archive/2026-01-07-context.md exists (backup)
- [ ] agents/context.md is ≤100 lines with 4-section structure
- [ ] AGENTS.md is ~50 lines (fallback rules only)
- [ ] START.md deleted
- [ ] All 7 role files reference context.md
- [ ] memory-management.semantic.md updated (lines 18, 50)
- [ ] handoff.semantic.md updated (line 42)
- [ ] No stale references to START.md or session.md (outside archive)
- [ ] Git status clean

---

## Rollback Plan

If issues discovered during migration:

```bash
# Restore from git
git checkout HEAD -- AGENTS.md agents/context.md START.md
git checkout HEAD -- agents/role-*.md
git checkout HEAD -- agents/modules/src/memory-management.semantic.md
git checkout HEAD -- agents/modules/src/handoff.semantic.md

# Remove infrastructure
rm -rf agents/archive/

# Reset
git reset --hard HEAD
```

---

## Post-Migration

**Next session agents should:**
1. Read appropriate role file OR AGENTS.md (fallback)
2. Read agents/context.md (always)
3. Start work

**Context maintenance:**
- Update agents/context.md throughout session
- Before handoff: Verify ≤100 lines
- If exceeded: Archive entire file, start fresh with template
- Archive naming: `agents/archive/YYYY-MM-DD-context.md`

**AGENTS.md maintenance:**
- Update only when core behavioral rules change
- Frequency: Monthly or less
- Keep ≤50 lines

---

## Critical Notes for Implementation

1. **Careful wording:** Module source edits require precision - semantic sources generate system prompts
2. **Order matters:** Update memory-management.semantic.md FIRST (prevents agents from updating wrong files)
3. **Context size:** Enforce 100 line limit strictly - prevents unbounded growth
4. **Archive pattern:** Always archive before restructuring - preserves history
5. **Role files:** Simple addition only - don't restructure existing content
6. **Validation:** Run all checks in Phase 9 before committing

---

## Success Criteria

- ✅ AGENTS.md is concise reference (~50 lines)
- ✅ agents/context.md has clear structure (≤100 lines)
- ✅ START.md eliminated (no duplication)
- ✅ All role files point to context.md
- ✅ Module sources updated (no stale references)
- ✅ Archive infrastructure in place
- ✅ No broken documentation links
- ✅ Agent boot sequence clear and documented
