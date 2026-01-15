# Consolidation: Phase 2

**Context**: Read `consolidation-context.md` for full context before executing this phase.

---

## Phase 2: Analyze with diff/patch

Create comparison reports in scratch/consolidation/analysis/:

### 2.1 Compare Compose Scripts

```bash
# Should be identical
diff -u scratch/consolidation/emojipack/compose.sh \
        agents/compose.sh \
        > scratch/consolidation/analysis/compose-sh-diff.patch
```

### 2.2 Compare Config Files

```bash
# Identify common justfile recipes
diff -u scratch/consolidation/configs/justfile-* \
        > scratch/consolidation/analysis/justfile-comparison.patch

# Identify common ruff/mypy settings (already analyzed by explore agent)
```

### 2.3 Analyze pytest-md AGENTS.md Fragmentation

Create `scratch/consolidation/analysis/pytest-md-fragmentation.md`:
- Section 1 (Commands/Environment) → stays in pytest-md (project-specific)
- Section 2 (Persistent vs Temporary) → reusable fragment for agent-core
- Section 3 (Context Management) → handoff skill in agent-core
- Section 4 (Opus Orchestration) → reusable fragment for agent-core
- Section 5 (Testing Guidelines) → stays in pytest-md (project-specific)
- Section 6 (Documentation Organization) → reusable fragment for agent-core

---


---

**Execution Instructions**:
1. Read consolidation-context.md for prerequisites, critical files, and execution notes
2. Execute this phase following the actions listed above
3. Perform validation checks as specified
4. Document results in execution report
5. Stop on any unexpected results per communication rules
