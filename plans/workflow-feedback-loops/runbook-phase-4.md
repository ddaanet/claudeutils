## Phase 4: Infrastructure

### Step 4.1: Update prepare-runbook.py

**Objective:** Add Phase metadata to step file frontmatter

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/bin/prepare-runbook.py`:

1. Extract phase number from step headers:
   - Parse `## Phase N` headers in runbook
   - Track current phase as steps are processed
   - For flat runbooks (no phase headers), use phase 1

2. Add Phase field to step file frontmatter:
   - Each step file gets `phase: N` in YAML frontmatter
   - Enables orchestrator phase boundary detection

3. Validation:
   - Warn if phase numbers have gaps
   - Error if phase numbers decrease (non-monotonic)

**Reference:** Design Section "Implementation Notes" line 540

**Expected Outcome:** Step files include phase metadata for orchestrator

**Success Criteria:**
- Step files have `phase: N` in frontmatter
- Phase extraction handles both flat and grouped runbooks
- Validation catches phase ordering issues

---

### Step 4.2: Update workflows.md

**Objective:** Document runbook outline format for discoverability

**Execution Model:** Sonnet

**Implementation:**

Edit `agents/decisions/workflows.md`:

1. Add new section "Runbook Artifacts":
   - Document runbook outline format from design
   - Include template structure
   - Explain requirements mapping table
   - Explain phase structure format

2. Reference the format:
   - Cross-reference from plan-adhoc Point 0.75
   - Cross-reference from plan-tdd Phase 1.5

**Content to add (from design lines 196-228):**

```markdown
## Runbook Outline Format

**Location:** `plans/<job>/runbook-outline.md`

**Structure:**
- Header with design reference and type (tdd | general)
- Requirements mapping table
- Phase structure with objectives and step titles
- Key decisions reference

**Template:**
[Include format from design FP-3 section]
```

**Reference:** Design Section "Implementation Notes" line 539

**Expected Outcome:** Runbook outline format is documented and discoverable

**Success Criteria:**
- New "Runbook Artifacts" section exists
- Complete format template included
- Cross-references from /plan-adhoc Point 0.75 and /plan-tdd Phase 1.5 exist
