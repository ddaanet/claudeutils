# Consolidation: Phase 7

**Context**: Read `consolidation-context.md` for full context before executing this phase.

---

## Phase 7: Validation

### 7.1 Composition Validation

For each project:
```bash
# Generate CLAUDE.md
claudeutils compose agents/compose.yaml

# Verify output matches expected structure
diff CLAUDE.md.expected CLAUDE.md
```

### 7.2 Config Validation

For justfile includes:
```bash
# Verify justfile imports work
just --list

# Verify recipes execute
just check
```

### 7.3 Skills Validation

For pytest-md skills:
```bash
# Verify skill loading in Claude Code
# Skills should be accessible as /skill-name commands
```

---


---

**Execution Instructions**:
1. Read consolidation-context.md for prerequisites, critical files, and execution notes
2. Execute this phase following the actions listed above
3. Perform validation checks as specified
4. Document results in execution report
5. Stop on any unexpected results per communication rules
