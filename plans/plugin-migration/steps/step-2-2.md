# Step 2.2

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 2.2: Verify skill structure

**Objective:** Confirm `edify-plugin/skills/` contains 16 skill subdirectories, each with `SKILL.md` file.

**Execution Model:** Haiku (inline verification)

**Implementation:**

Verify skill structure:

```bash
# Count skill directories
skill_count=$(find edify-plugin/skills -mindepth 1 -maxdepth 1 -type d | wc -l)
echo "Skill directory count: $skill_count"

# Count SKILL.md files
skill_md_count=$(find edify-plugin/skills -name "SKILL.md" | wc -l)
echo "SKILL.md count: $skill_md_count"

# List skill directories
find edify-plugin/skills -mindepth 1 -maxdepth 1 -type d | sort

# Verify each directory has SKILL.md
for dir in edify-plugin/skills/*/; do
  if [ ! -f "$dir/SKILL.md" ]; then
    echo "Missing SKILL.md in: $dir"
  fi
done
```

**Expected counts:**
- 16 skill subdirectories
- 16 `SKILL.md` files (one per directory)

**Design Reference:**
- Design outline: "16 skills symlinked via `just sync-to-parent`"
- Plugin auto-discovery: "All `SKILL.md` files in skill subdirectories load automatically"

**Validation:**
- Skill directory count: `[ "$skill_count" -eq 16 ]`
- SKILL.md count: `[ "$skill_md_count" -eq 16 ]`
- Every directory has SKILL.md file

**Expected Outcome:** 16 skill subdirectories confirmed, each with `SKILL.md`.

**Error Conditions:**
- Count mismatch → Investigate missing or extra skills
- Missing SKILL.md → Skill won't auto-discover (must be named exactly `SKILL.md`)
- Skills at root level (not in subdirectories) → Won't auto-discover

**Success Criteria:**
- Exactly 16 subdirectories in `edify-plugin/skills/`
- Every subdirectory contains `SKILL.md`
- No orphan SKILL.md files outside skill directories

---
