# Step 4.2

**Plan**: `plans/learnings-consolidation/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 4.2: Integration Validation

**Objective:** Validate end-to-end workflow integration with manual testing procedures.

**Implementation:**

**1. Unit test integration (automated):**

Already covered by step 4.1 integration test. Run:
```bash
pytest tests/test_learning_ages.py::test_full_pipeline -v
```

Verify:
- Script produces markdown output matching design § D-2
- Summary fields present (file lines, last consolidation, total entries, ≥7 days count)
- Per-entry sections formatted correctly

**2. Manual handoff trigger test:**

Create test scenario to verify handoff step 4c triggers consolidation:

**Option A: Size trigger (>150 lines)**

```bash
# Check current learnings.md size
wc -l agents/learnings.md

# If needed, add temp entries to exceed 150 lines
# (Do this in a test branch)

# Run handoff and verify step 4c executes
# Expected: Script runs, filtered entry list passed to remember-task agent
```

**Option B: Staleness trigger (>14 days)**

```bash
# Check staleness
agent-core/bin/learning-ages.py agents/learnings.md | head -5

# If staleness <14 days, use git manipulation to simulate old entries
# (Or wait for natural staleness)

# Run handoff and verify step 4c executes
```

**Verification steps:**
- [ ] Handoff skill loads without error
- [ ] Step 4c runs learning-ages.py
- [ ] Trigger condition evaluated (size OR staleness)
- [ ] If triggered: filtered entry list logged
- [ ] If triggered: remember-task agent delegated
- [ ] If not triggered: consolidation skipped, continues to step 5
- [ ] If error: logged to stderr, handoff continues (NFR-1)

**3. Agent definition validation:**

**A. Remember-task agent:**

```bash
# Read agent file
cat agent-core/agents/remember-task.md

# Verify frontmatter
head -10 agent-core/agents/remember-task.md | grep -E "(name|description|model|color|tools)"

# Verify source comment
grep "Source: agent-core/skills/remember" agent-core/agents/remember-task.md

# Verify sections present
grep "^##" agent-core/agents/remember-task.md | head -10
```

Expected sections:
- Role statement
- Input Format
- Pre-Consolidation Checks
- Consolidation Protocol
- Reporting
- Return Protocol

Checklist:
- [ ] Protocol embedded faithfully (compare with remember skill steps 1-4a):
  - Verify protocol steps present in same order (Understand → File Selection → Draft → Apply → Discovery)
  - Check terminology matches skill (e.g., "Precision over brevity", "Atomic changes")
  - Confirm routing patterns identical (fragments/ vs decisions/ vs implementation-notes.md)
  - Allow adaptation: agent body uses second-person ("You"), skill uses imperative
- [ ] Source comment present for synchronization tracking
- [ ] Pre-check algorithms concrete (thresholds specified: 50% keyword overlap, 70% redundancy)
- [ ] Report structure documented (6 sections: summary, supersession, redundancy, contradictions, file limits, discovery)
- [ ] Model: sonnet, color: green, tools include Read/Write/Edit/Bash/Grep/Glob
- [ ] Quiet execution pattern (report to file, return filepath)

**B. Memory-refactor agent:**

```bash
# Read agent file
cat agent-core/agents/memory-refactor.md

# Verify sections
grep "^##" agent-core/agents/memory-refactor.md
```

Expected sections:
- Role statement
- Input Format
- Refactoring Process (6 steps)
- Constraints
- Output Format
- Return Protocol

Checklist:
- [ ] Refactoring process has 6 steps with heuristics
- [ ] Validator autofix integration (step 5)
- [ ] Content preservation constraints (no summarization)
- [ ] Model: sonnet, color: yellow, tools include Read/Write/Edit/Grep/Glob
- [ ] Quiet execution pattern (filepaths on success, error on failure)

**4. No automated full workflow test:**

Design specifies no automated end-to-end test for full workflow (complexity too high). Manual validation sufficient:
- Phase 1-3 unit tests pass
- Agent definitions reviewed manually
- Handoff trigger test executed manually

**Expected Outcome:**

Integration validation complete:
- Unit tests pass
- Manual handoff trigger test executed
- Agent definitions validated against specifications
- No full workflow automation (manual validation acceptable per design)

**Validation:**

```bash
# Run all tests
pytest tests/test_learning_ages.py -v

# Verify no test failures
echo $?  # Should be 0
```

**Unexpected Result Handling:**

If tests fail:
- **Parse errors**: Verify preamble skip count (10 lines)
- **Git mock failures**: Check subprocess.run patch syntax
- **Integration test fails**: Verify markdown output format matches design § D-2

If manual trigger test doesn't trigger:
- **Size check**: Verify learnings.md actually >150 lines
- **Staleness check**: Verify staleness >14 days via script output
- **Threshold mismatch**: Compare handoff step 4c thresholds with design D-3

If agent definitions incomplete:
- **Compare against design**: Cross-reference Implementation Components 2 and 3
- **Check protocol embedding**: Compare remember-task protocol with remember skill steps 1-4a
- **Verify structure**: Ensure all required sections present per phase 3 success criteria

**Success Criteria:**

- [ ] All unit tests pass: `pytest tests/test_learning_ages.py`
- [ ] Integration test produces correct markdown format (matches design § D-2)
- [ ] Manual handoff trigger test executed (size OR staleness)
- [ ] Remember-task agent validated (protocol, source comment, pre-checks, reporting)
- [ ] Memory-refactor agent validated (6-step process, autofix integration, constraints)
- [ ] Both agents follow quiet execution pattern
- [ ] No critical issues found in agent definitions

**Report Path:** `plans/learnings-consolidation/reports/phase-4-execution.md`

**Design References:**
- Implementation Component 6: Testing specification
- D-2: Markdown output format (validation target)
- D-3: Trigger thresholds (manual test verification)
- NFR-1: Failure handling (handoff continues on error)
