### Phase 3: Conflict Resolution Utilities (~4 cycles)

**Model:** sonnet (implementation)
**Checkpoint:** light
**Files:** `src/claudeutils/worktree/conflicts.py`, `tests/test_worktree_conflicts.py`
**Parallel:** Can run parallel to Phases 0-2 (no CLI dependencies, pure functions)

**Requirements mapping:** FR-3 (session conflict resolution), NFR-2 (deterministic resolution)

**Phase notes:**
- Four pure functions for deterministic merge conflict resolution
- No git operations, no agent judgment — testable with string inputs
- Session conflict: critical fix for FR-3 (extract worktree-created tasks before resolution)
- Learnings: keep-both append strategy (append-only file)
- Jobs: status advancement via ordering (requirements < designed < outlined < planned < complete)
- This phase forms parallel group B (independent of CLI implementation)

---

## Cycle 3.1: Session conflict resolution with task extraction

**FR-3: Extract new tasks from worktree side before applying keep-ours merge resolution.**

**RED: Test behavior**

Create test fixture with two session.md versions:
- **Ours:** Base session with tasks "Implement feature X" and "Design feature Y" in Pending Tasks
- **Theirs:** Same base plus new task "Plan feature Z TDD runbook" in Pending Tasks

Call `resolve_session_conflict(ours, theirs)` and assert:
- Result contains all three tasks in Pending Tasks section
- New task "Plan feature Z TDD runbook" includes full task block with metadata (command, model, notes)
- Order: ours tasks first, then new theirs tasks
- All other sections unchanged (Blockers, Reference Files, handoff footer)

**Expected failure:** Function doesn't exist yet, ImportError.

**GREEN: Implement behavior**

Create `src/claudeutils/worktree/conflicts.py` with `resolve_session_conflict(ours: str, theirs: str) -> str`:

**Algorithm hints:**
1. Parse task names from both versions using regex `^- \[ \] \*\*(.+?)\*\*` with `re.MULTILINE` flag
2. Compute new tasks: set difference on task names (theirs - ours)
3. For each new task name, extract full task block from theirs (task line + any indented continuation lines using multi-line regex)
4. Locate insertion point in ours: find Pending Tasks section, identify line before next `## ` heading
5. Insert new task blocks before the next section heading
6. Return merged content with ours as base, new tasks appended

**Approach notes:**
- Task block extraction must capture metadata lines (indented with spaces, containing plan/status/notes)
- Use regex lookahead to stop extraction at next non-indented line or EOF
- Preserve exact formatting (indentation, blank lines within task blocks)

---

## Cycle 3.2: Session conflict removes merged worktree entry

**FR-3: Remove worktree task entry from Worktree Tasks section after extracting it.**

**RED: Test behavior**

Create test fixture where theirs has a Worktree Tasks section:
- **Ours:** Pending Tasks only (no Worktree Tasks section)
- **Theirs:** Same Pending Tasks plus Worktree Tasks section with entry `- [ ] **Execute plugin migration** → wt/plugin-migration`

Call `resolve_session_conflict(ours, theirs, slug="plugin-migration")` and assert:
- Result has no Worktree Tasks section
- Pending Tasks section includes "Execute plugin migration" task (extracted and moved)
- No reference to `wt/plugin-migration` remains

**Expected failure:** Function signature doesn't accept `slug` parameter, worktree entry not removed.

**GREEN: Implement behavior**

Update `resolve_session_conflict` signature to accept optional `slug: str | None = None`:

**Algorithm hints:**
1. After extracting new tasks from theirs, scan theirs for Worktree Tasks section
2. If `slug` provided: match line containing `→ wt/{slug}` pattern using regex
3. Extract task name from matched worktree entry (same task name regex as Pending Tasks)
4. If task name matches one of the newly extracted tasks, include it in new tasks list
5. Do NOT include Worktree Tasks section in final result (section is omitted entirely)
6. Return merged content with new tasks in Pending Tasks, no Worktree Tasks

**Approach notes:**
- Worktree entry removal happens automatically by taking ours as base (which lacks the section)
- Task name from worktree entry must match against extracted new tasks
- Edge case: if worktree task name doesn't match any new task, it's not critical (merge can proceed)

---

## Cycle 3.3: Learnings conflict keep-both

**NFR-2: Deterministic learnings.md conflict resolution with append strategy.**

**RED: Test behavior**

Create test fixture with two learnings.md versions:
- **Ours:** Three learning entries with `## Title` headings: "Tool batching unsolved", "Scan triggers unnecessary tools", "Structural header dot syntax"
- **Theirs:** Same three entries plus new entry "## Vet-fix-agent confabulation from design docs"

Call `resolve_learnings_conflict(ours, theirs)` and assert:
- Result contains all four learning entries
- New entry appended at end (after "Structural header dot syntax")
- All entries preserve exact content (multi-paragraph text, code blocks, bullet lists)
- No duplication of shared entries

**Expected failure:** Function doesn't exist yet.

**GREEN: Implement behavior**

Create function `resolve_learnings_conflict(ours: str, theirs: str) -> str`:

**Algorithm hints:**
1. Parse both versions into learning entries: split on `## ` heading delimiter (regex `^## `, `re.MULTILINE`)
2. Extract heading text from each entry (first line after split, strip `## ` prefix)
3. Build set of ours headings for comparison
4. Identify new entries in theirs: headings present in theirs but not in ours
5. Append new entry content (full text from `## Title` to next `## ` or EOF) to ours
6. Return merged content with ours entries plus new theirs entries

**Approach notes:**
- Learnings.md is append-only, so theirs additions are always at the end
- No reordering needed: preserve ours order, append theirs new entries
- Handle edge case: preamble text before first `## ` heading (keep from ours, ignore from theirs)

---

## Cycle 3.4: Jobs conflict status advancement

**NFR-2: Deterministic jobs.md conflict resolution with status ordering.**

**RED: Test behavior**

Create test fixture with two jobs.md versions:
- **Ours:** Plans table with "worktree-skill" status = "designed", "plugin-migration" status = "planned"
- **Theirs:** Same table with "worktree-skill" status = "planned", "plugin-migration" status = "planned"

Call `resolve_jobs_conflict(ours, theirs)` and assert:
- Result advances "worktree-skill" to "planned" (theirs has higher status)
- "plugin-migration" remains "planned" (no change, same status)
- Status ordering: requirements < designed < outlined < planned < complete

Additional test: verify "outlined" status ordering (between designed and planned) for plans using that intermediate state.

**Expected failure:** Function doesn't exist yet.

**GREEN: Implement behavior**

Create function `resolve_jobs_conflict(ours: str, theirs: str) -> str`:

**Algorithm hints:**
1. Define status ordering tuple: `("requirements", "designed", "outlined", "planned", "complete")`
2. Parse both versions for plan rows: regex `^\| ([^\|]+) \| ([^\|]+) \|` with `re.MULTILINE` on table body
3. Build plan→status maps for ours and theirs (strip whitespace from captured groups)
4. For each plan in theirs: compare status index (position in ordering tuple)
5. If theirs status index > ours status index: update ours plan's status
6. Reconstruct jobs.md with updated statuses: replace status cells in ours's table rows
7. Return merged content with advanced statuses

**Approach notes:**
- Table parsing must skip header rows (starts after `|------|--------|-------|`)
- Status comparison is index-based (tuple position), not string comparison
- Plans not in ours: ignore (merge doesn't add new plans, only updates existing)
- Preserve notes column exactly (no changes to notes text)
