# Step 1.1

**Plan**: `plans/learnings-consolidation/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

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
