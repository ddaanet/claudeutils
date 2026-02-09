# Step 3.5

**Plan**: `plans/continuation-passing/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 3.5: Empirical Validation Against Session Corpus

**Execution Model:** Sonnet

**Objective:** Validate parser accuracy against real user inputs (FR-5, D-7)

**Procedure:**
1. Extract unique user prompts containing `/` from `~/.claude/projects/*/` session transcripts
2. Run parser against each prompt
3. Manual review: classify as correct/false-positive/false-negative
4. Calculate metrics:
   - False positive rate (args misidentified as continuations)
   - False negative rate (explicit continuations missed)

**Target metrics:**
- False positives: 0% (critical — corrupts skill args)
- False negatives: <5% (acceptable — user retypes)

**Report Path:** `plans/continuation-passing/reports/step-3-5-empirical-validation.md`

---
