# Phase 1: Script Foundation (learning-ages.py)

**Complexity:** Moderate (git operations, active-day calculation, staleness heuristic)
**Model:** Sonnet
**Scope:** ~150 lines

---

## Step 1.1: Implement learning-ages.py Script

**Objective:** Create git-aware script to calculate learning entry ages in active days and detect consolidation staleness.

**Implementation:**

Create `agent-core/bin/learning-ages.py` with the following implementation:

**1. Script structure:**
```python
#!/usr/bin/env python3
"""Calculate git-active-day age per learning entry.

Usage:
    learning-ages.py [learnings-file]

Default: agents/learnings.md

Output: Markdown report to stdout
Exit: 0 on success, 1 on error (stderr)
"""
```

**2. Parsing logic:**
- Read learnings.md file (default: `agents/learnings.md`, accept argument)
- Skip first 10 lines (preamble) matching `validate-learnings.py` pattern
- Extract H2 headers (`## Title`) as learning entries
- Store (line_number, title_text) pairs

**3. Git blame for entry dates:**
```python
# For each H2 header line:
# git blame -C -C --first-parent -- agents/learnings.md
# Extract commit hash and date for that specific line
# -C -C flags: detect renames and copies across files
# --first-parent: handle merge commits via first-parent chain (matches staleness algorithm)
```

**4. Active-day calculation:**
```python
# For entry with date D:
# Run: git log --format='%ad' --date=short
# Build set of unique commit dates between D and today
# Active days = len(commit_dates_set)
# Edge case: entry added today → 0 active days
```

**5. Staleness detection algorithm:**
```python
# Walk git log -p -- agents/learnings.md looking for removed H2 headers
# Pattern: lines starting with "-## " (removed headers)
# Most recent commit with removed headers = last consolidation
# Calculate active days from that commit to today
# Fallback: if no removed headers found, report "N/A (no prior consolidation detected)"
```

**6. Output markdown format (per design § D-2):**
```markdown
# Learning Ages Report

**File lines:** 101
**Last consolidation:** 12 active days ago
**Total entries:** 15
**Entries ≥7 active days:** 8

## Tool batching unsolved
- Age: 22 active days
- Added: 2026-01-14

## "Scan" triggers unnecessary tools
- Age: 18 active days
- Added: 2026-01-18

...
```

**7. Error handling:**
- Missing file → stderr message, exit 1
- Git not available → stderr message, exit 1
- Malformed headers → skip, log warning to stderr, continue
- Git operations fail → stderr with git error, exit 1

**8. Shebang and permissions:**
```bash
# Add shebang: #!/usr/bin/env python3
chmod +x agent-core/bin/learning-ages.py
```

**Expected Outcome:**

Script executes successfully:
```bash
$ agent-core/bin/learning-ages.py agents/learnings.md
# Learning Ages Report
**File lines:** 103
**Last consolidation:** 12 active days ago
...
```

Output includes:
- Summary metadata (file lines, staleness, total entries, ≥7 days count)
- Per-entry sections with age and added date
- Sorted oldest-first (highest age first) for consolidation priority

**Validation:**

Run on current `agents/learnings.md`:
```bash
agent-core/bin/learning-ages.py agents/learnings.md | head -20
```

Verify:
- [ ] Output format matches design § D-2 exactly
- [ ] Staleness detection works (finds last consolidation or reports "unknown")
- [ ] Active-day count accurate (excludes days without commits)
- [ ] Handles today's entries (0 active days)
- [ ] Error cases produce stderr messages and exit 1

**Unexpected Result Handling:**

If script fails or output incorrect:
- Check git blame output manually: `git blame -C -C agents/learnings.md | grep "^## "`
- Verify staleness heuristic: `git log -p agents/learnings.md | grep "^-## "`
- Test with simple learnings.md (2-3 entries) first
- Escalate: Complex git edge cases (submodules, rebases) may need user guidance

**Error Conditions:**

| Condition | Action |
|-----------|--------|
| File not found | stderr: "Error: File not found: [path]", exit 1 |
| Not a git repo | stderr: "Error: Not a git repository", exit 1 |
| Git blame fails | stderr: "Error: git blame failed: [error]", exit 1 |
| No H2 headers | Warning to stderr, output summary with 0 entries |

**Success Criteria:**

- [ ] Script runs without errors on `agents/learnings.md`
- [ ] Output matches design specification (§ D-2)
- [ ] Summary section includes all 4 fields (lines, last consolidation, total, ≥7 days)
- [ ] Per-entry sections sorted oldest-first (highest age first)
- [ ] Staleness detection functional (finds last consolidation or reports "N/A")
- [ ] Active-day calculation accurate (manual spot-check 2-3 entries)
- [ ] Edge cases handled: entry added today, file renames, merge commits
- [ ] Error messages clear and actionable
- [ ] Test suite passes: `pytest tests/test_learning_ages.py`

**Report Path:** `plans/learnings-consolidation/reports/phase-1-execution.md` (detailed implementation log)

**Design References:**
- D-2: Markdown output format
- Implementation Component 1: Script specification
- Documentation Perimeter: validate-learnings.py (parsing pattern)
