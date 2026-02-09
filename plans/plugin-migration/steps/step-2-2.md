# Step 2.2

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Step 2.2: Verify skill structure

Verify `agent-core/skills/` contains 16 skill subdirectories with `SKILL.md`:

```bash
skill_count=$(find agent-core/skills -mindepth 1 -maxdepth 1 -type d | wc -l)
skill_md_count=$(find agent-core/skills -name "SKILL.md" | wc -l)
echo "Skill directory count: $skill_count"
echo "SKILL.md count: $skill_md_count"
[ "$skill_count" -eq 16 ] && [ "$skill_md_count" -eq 16 ] || echo "ERROR: Expected 16 skills"
```

---
