# Step 5.1

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Step 5.1: Remove symlinks

**Objective:** Remove all symlinks from `.claude/skills/`, `.claude/agents/`, `.claude/hooks/` directories.

**Implementation:**

1. **Count symlinks before removal (baseline):**
```bash
echo "Symlinks before removal:"
find .claude -type l | wc -l
find .claude/skills -type l | wc -l
find .claude/agents -type l | wc -l
find .claude/hooks -type l | wc -l
```

**Expected counts (based on current state):**
- Total: ~32 symlinks (may vary by project)
- `.claude/skills/`: ~16 symlinks
- `.claude/agents/`: ~12 symlinks (preserve `*-task.md` regular files)
- `.claude/hooks/`: ~4 symlinks

2. **Remove symlinks from .claude/skills/:**
```bash
# Remove all symlinks (all skills/ entries are symlinks)
find .claude/skills -type l -delete
```

3. **Remove symlinks from .claude/agents/:**
```bash
# Remove only symlinks, preserve *-task.md regular files
find .claude/agents -type l -delete
```

**Preservation note:** Plan-specific agents (`*-task.md`) are regular files (type f), not symlinks. The `-type l` filter ensures only symlinks are removed.

4. **Remove symlinks from .claude/hooks/:**
```bash
# Remove all symlinks (all hooks/ entries are symlinks)
find .claude/hooks -type l -delete
```

5. **Verify counts after removal:**
```bash
echo "Symlinks after removal:"
find .claude -type l | wc -l  # Should be 0

echo "Regular files preserved:"
find .claude/agents -type f -name "*-task.md" | wc -l  # Should be 6+
```

**Expected Outcome:**
- All symlinks removed from `.claude/` subdirectories
- Plan-specific `*-task.md` agents preserved (regular files)
- 0 symlinks remain in `.claude/`

**Unexpected Result Handling:**
- If symlinks remain: check deletion command succeeded, verify no permission errors
- If *-task.md files deleted: ERROR - these should be regular files (type f), not symlinks
- If count mismatch from expected: investigate unexpected symlinks or missing entries

**Validation:**
- `find .claude -type l | wc -l` returns 0
- `find .claude/agents -type f -name "*-task.md"` shows 6+ files (plan-specific agents intact)
- `.claude/skills/`, `.claude/agents/`, `.claude/hooks/` directories exist but contain no symlinks

**Success Criteria:**
- All symlinks removed (0 remaining)
- Plan-specific agents preserved
- Directories intact (not deleted, just emptied of symlinks)

---
