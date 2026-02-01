# Step 6

**Plan**: `plans/design-workflow-enhancement/runbook.md`
**Common Context**: See plan file for context

---

## Step 6: Symlink Management and Validation

**Objective**: Create symlink for quiet-explore agent and validate workflow changes.

**Execution Model**: Sonnet

**Implementation**:

1. **Create symlinks using project recipe:**
   ```bash
   cd /Users/david/code/claudeutils/agent-core && just sync-to-parent
   ```
   (Requires `dangerouslyDisableSandbox: true` - writes to `.claude/agents/`)

2. **Validation checks:**
   - Verify symlink: `ls -la /Users/david/code/claudeutils/.claude/agents/quiet-explore.md`
   - Check YAML parses: Read agent file, confirm no syntax errors
   - Verify skill files: Read each modified skill, check structure is coherent
   - Documentation perimeter: Grep for "Documentation Perimeter" in design skill template

3. **Report findings:**
   - Symlink creation status
   - Any YAML parse errors
   - Structural issues in skill files
   - Missing elements from specification

**Expected Outcome**: Symlink created, all files syntactically valid, workflow changes complete.

**Unexpected Result Handling**:
- If symlink creation fails: Check sandbox bypass, verify paths, escalate if unresolved
- If YAML errors found: Fix syntax and re-run sync
- If skill structure issues: Apply fixes or escalate for complex issues

**Error Conditions**:
- Symlink creation fails → Escalate to user (sandbox/permission issue)
- YAML parse errors → Fix and retry
- Missing specification elements → Escalate to user (implementation incomplete)

**Validation**:
- Symlink exists at `.claude/agents/quiet-explore.md`
- Points to `agent-core/agents/quiet-explore.md`
- All modified skill files have valid YAML frontmatter
- Design skill has three-phase structure
- Planning skills have documentation perimeter loading

**Success Criteria**:
- Symlink created successfully
- No YAML parse errors
- All specification elements implemented
- Files are coherent and follow documented patterns
- quiet-explore agent system prompt includes all core directives (parallel tools, absolute paths, report format, Bash read-only)

**Report Path**: `plans/design-workflow-enhancement/reports/step-6-symlink-validation.md`

---
