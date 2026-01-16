# Consolidation: Phase 6

**Context**: Read `consolidation-context.md` for full context before executing this phase.

---

## Phase 6: Client Project Integration

### 6.1 emojipack Migration

**Current**: compose.sh + compose.yaml (shell-based)
**Target**: claudeutils compose (Python-based)

```toml
# Add to pyproject.toml
[dependency-groups]
dev = ["claudeutils>=0.1.0"]
```

```bash
# Update workflow
claudeutils compose agents/compose.yaml
```

### 6.2 tuick Migration

**Current**: build.py + Makefile (Python local)
**Target**: claudeutils compose + Makefile delegation

```makefile
# agents/Makefile
BUILD = claudeutils compose role

roles/high-level-planner.md: $(ROLEDEF_PLANNER_HIGH) $(CORE) $(PLANNING)
	$(BUILD) --output $@ --title "High-Level Planner" $^
```

### 6.3 pytest-md Migration

**Current**: Manual CLAUDE.md
**Target**: Generated from fragments + local project rules

1. Create `pytest-md/agents/` directory
2. Fragment CLAUDE.md:
   - Keep project-specific sections in `agents/src/pytest-md-rules.md`
   - Reference agent-core fragments for reusable content
3. Create `agents/compose.yaml`
4. Generate: `claudeutils compose agents/compose.yaml`

---


---

**Execution Instructions**:
1. Read consolidation-context.md for prerequisites, critical files, and execution notes
2. Execute this phase following the actions listed above
3. Perform validation checks as specified
4. Document results in execution report
5. Stop on any unexpected results per communication rules
