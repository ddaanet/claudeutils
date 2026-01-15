# Phase 1: Step 6

**Context**: Read `phase1-execution-context.md` for full context before executing this step.

---

### Step 6: Implement Template-Based AGENTS.md Generation

**Objective**: Create simple composition script to generate AGENTS.md from fragments.

**Approach**: Start with bash script (simple concatenation), can evolve to Python if needed.

**Technical Decisions**:
- Script location: `agent-core/scripts/compose-agents.sh` or in consuming project?
  - **Recommendation**: Consumer project controls composition (`agents/compose.sh`)
  - Rationale: Local template defines order and customization
- Template format: Simple marker-based or full template?
  - **Recommendation**: Simple bash concatenation for Phase 1
  - Example from design.md:162-169

**compose.yaml Structure** (design.md:122-148):
```yaml
sources:
  core: &core agent-core/fragments

fragments:
  - *core/AGENTS-framework.md
  - *core/communication.md
  - *core/delegation.md
  - *core/tool-preferences.md
  - *core/hashtags.md

output: AGENTS.md
```

**Generation Script** (simple version):
```bash
#!/bin/bash
# agents/compose.sh
# Generates AGENTS.md from fragments defined in compose.yaml

FRAGMENTS=(
  "agent-core/fragments/AGENTS-framework.md"
  "agent-core/fragments/communication.md"
  "agent-core/fragments/delegation.md"
  "agent-core/fragments/tool-preferences.md"
  "agent-core/fragments/hashtags.md"
)

OUTPUT="AGENTS.md"

# Clear output
> "$OUTPUT"

# Concatenate fragments
for fragment in "${FRAGMENTS[@]}"; do
  if [ -f "$fragment" ]; then
    cat "$fragment" >> "$OUTPUT"
    echo "" >> "$OUTPUT"  # Blank line between fragments
  else
    echo "ERROR: Fragment not found: $fragment" >&2
    exit 1
  fi
done

echo "Generated $OUTPUT from ${#FRAGMENTS[@]} fragments"
```

**Actions**:
1. Create `agents/compose.yaml` in claudeutils
2. Create `agents/compose.sh` generation script
3. Make script executable
4. Add to justfile: `generate-agents: agents/compose.sh`
5. Run generation and compare with existing AGENTS.md
6. Document usage in agents/README.md (if it doesn't exist, create it)

**Validation**:
- [ ] Script runs without errors
- [ ] Generated AGENTS.md is valid markdown
- [ ] Content matches expected composition
- [ ] Generation is repeatable (same input → same output)

**Open Decision Points**:
- **YAML parsing in bash**: Phase 1 uses hardcoded array; future can parse YAML
- **Fragment order**: Does order matter? (Yes, framework should come first)

---


---

**Execution Instructions**:
1. Read phase1-execution-context.md for prerequisites and validation patterns
2. Execute this step following the actions listed above
3. Perform validation checks
4. Document results in execution report
5. Stop on any unexpected results per communication rules
