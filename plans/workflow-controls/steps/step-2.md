# Step 2

**Plan**: `plans/workflow-controls/runbook.md`
**Common Context**: See plan file for context

---

## Step 2: Rewrite execute-rule.md Fragment

**Objective**: Define four session modes and shortcut vocabulary table.

**Script Evaluation**: Prose description (content rewrite)

**Execution Model**: Sonnet

**Implementation**:

Rewrite `agent-core/fragments/execute-rule.md` with new content defining:

1. **Four session modes**:
   - STATUS (default): List tasks, wait
   - EXECUTE (`#execute`, `x`): Resume OR start pending
   - EXECUTE+COMMIT (`#execute --commit`, `xc`): Execute → handoff → commit
   - RESUME (`#resume`, `r`): Resume in-progress only (error if none)

2. **Shortcut vocabulary tables**: Both tier 1 and tier 2

3. **`x` vs `r` behavior matrix**:
   | State | `x` | `r` |
   |-------|-----|-----|
   | In-progress exists | Resume | Resume |
   | No in-progress, pending exists | Start first pending | Error |
   | No tasks | "No pending tasks" | Error |

4. **STATUS display format**: As specified in Common Context

5. **Ambiguous prompt handling**: "next?", "what's next?", startup → default to STATUS

**Expected Outcome**: Fragment contains complete mode definitions and vocabulary.

**Unexpected Result Handling**:
- If file structure unclear → consult design.md section "Files to Modify"

**Error Conditions**:
- Missing required sections → add them

**Validation**:
- File contains all four modes (STATUS, EXECUTE, EXECUTE+COMMIT, RESUME)
- Both shortcut tables present (tier 1 commands, tier 2 directives)
- `x` vs `r` behavior matrix included (table with 3 states)
- STATUS format specified with code block example
- Ambiguous prompt handling documented

**Success Criteria**:
- Fragment is complete and coherent
- All shortcuts documented with semantics
- MODE definitions clear

**Report Path**: `plans/workflow-controls/reports/step-2.md`

---
