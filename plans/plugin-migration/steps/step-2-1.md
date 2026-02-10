# Step 2.1

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 2.1: Verify agent structure

**Objective:** Confirm `edify-plugin/agents/` contains 14 agent `.md` files and structure matches plugin auto-discovery requirements.

**Execution Model:** Haiku (inline verification)

**Implementation:**

Verify agent structure:

```bash
# Count agent .md files
agent_count=$(find edify-plugin/agents -maxdepth 1 -name "*.md" -type f | wc -l)
echo "Agent count: $agent_count"

# List agent files
find edify-plugin/agents -maxdepth 1 -name "*.md" -type f | sort
```

**Expected count:** 14 agent files

**Design Reference:**
- Design Component 1: "Plugin agents are discovered from `edify-plugin/agents/`. Plan-specific agents (`*-task.md`) live in `.claude/agents/` as regular files."
- Plugin auto-discovery: All `.md` files in `agents/` directory load automatically

**Validation:**
- Agent count equals 14: `[ "$agent_count" -eq 14 ]`
- All files are `.md` extension
- Files are at `agents/` root level (not nested in subdirectories)

**Expected Outcome:** 14 agent `.md` files confirmed at `edify-plugin/agents/`.

**Error Conditions:**
- Count mismatch → Investigate missing or extra files
- Nested subdirectories found → Agents must be at root level for auto-discovery

**Success Criteria:**
- Exactly 14 `.md` files in `edify-plugin/agents/`
- All agents at root level (no subdirectories)

---
