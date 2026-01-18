# Phase 2: Step 2

**Context**: Read `phase2-execution-plan.md` for full execution context, metadata, and design decisions.

---

## Step 2.2: Compare Config Files (Justfiles)

**Objective**: Identify common justfile recipes across projects for extraction

**Script Evaluation**: Direct execution (3 diffs, ≤25 lines total)

**Implementation**:
```bash
# Create analysis directory if needed
mkdir -p scratch/consolidation/analysis

# Verify source files exist
for file in /Users/david/code/tuick/justfile \
            /Users/david/code/emojipack/justfile \
            /Users/david/code/pytest-md/justfile; do
    if [ ! -f "$file" ]; then
        echo "ERROR: $file not found" >&2
        exit 1
    fi
done

# Compare all justfiles pairwise to find commonality
diff -u /Users/david/code/tuick/justfile \
        /Users/david/code/emojipack/justfile \
        > scratch/consolidation/analysis/justfile-tuick-vs-emojipack.patch || true

diff -u /Users/david/code/tuick/justfile \
        /Users/david/code/pytest-md/justfile \
        > scratch/consolidation/analysis/justfile-tuick-vs-pytest-md.patch || true

diff -u /Users/david/code/emojipack/justfile \
        /Users/david/code/pytest-md/justfile \
        > scratch/consolidation/analysis/justfile-emojipack-vs-pytest-md.patch || true

# Report results
EMPTY_COUNT=0
for patch in scratch/consolidation/analysis/justfile-*.patch; do
    SIZE=$(wc -c < "$patch")
    if [ "$SIZE" -eq 0 ]; then
        EMPTY_COUNT=$((EMPTY_COUNT + 1))
    fi
    echo "$(basename "$patch"): $SIZE bytes"
done

if [ "$EMPTY_COUNT" -eq 3 ]; then
    echo "UNEXPECTED: All justfiles identical - escalate for review"
else
    echo "SUCCESS: Created 3 pairwise comparison patches, $EMPTY_COUNT empty"
fi
```

**Note**: ruff/mypy configs already analyzed (per consolidation-context.md line 71)

**Expected Outcome**: Patch files show differences, common recipes identifiable

**Unexpected Result Handling**:
- If all files identical: Escalate to sonnet for review (unexpected per design)

**Error Conditions**:
- Source file not found → Report error, escalate to sonnet
- Permission denied → Report error, escalate to sonnet
- Output directory not writable → Report error, escalate to sonnet

**Validation**:
- All 3 patch files exist at expected paths
- At least 1 patch file is non-empty
- File sizes documented in execution report

**Success Criteria**:
- 3 patch files created at `scratch/consolidation/analysis/justfile-*.patch`
- At least 1 file non-empty (shows differences)
- Execution report documents file sizes

**Report Path**: `plans/unification/reports/phase2-step2-execution.md`

---

---

**Execution Instructions**:
1. Read phase2-execution-plan.md for prerequisites, error escalation, and validation patterns
2. Execute this step following the implementation above
3. Perform validation checks as specified
4. Write detailed output to report path specified above
5. Return only: "done: <summary>" or "error: <description>"
6. Stop on any unexpected results per communication rules
