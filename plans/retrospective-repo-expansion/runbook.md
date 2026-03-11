# Runbook: Retrospective Repo Expansion

Extend retrospective evidence base with git history from 16 additional repos. Investigation work — output is markdown reports.

**Input:** `plans/retrospective-repo-expansion/brief.md` (repo inventory, evidence value, hazards)
**Output:** Extended topic reports and new cross-repo pattern report in `plans/retrospective-repo-expansion/reports/`
**Existing format:** `plans/retrospective/reports/topic-*.md` (git timeline tables, session excerpts, decision snapshots)

## Step 1: Repo inventory validation and evidence extraction script

**Goal:** Validate all 16 repos are git repos with expected commit counts, then extract agentic-relevant commits from each.

**Actions:**
- For each repo in brief.md inventory, run `git -C <path> log --oneline | wc -l` to validate commit count is in expected range
- For each repo, extract agentic-evidence commits using targeted searches:
  - `git -C <path> log --all --oneline --grep="AGENTS" --grep="CLAUDE" --grep="agent" --grep="skill" --grep="recall" --grep="pushback" --grep="review" --grep="gating" --grep="hook"` (union, case-insensitive)
  - `git -C <path> log --all --oneline -S "AGENTS.md" -S "CLAUDE.md"` (file introduction/modification)
  - `git -C <path> log --all --oneline -- "AGENTS.md" "CLAUDE.md" ".claude/" "agents/"` (path-based)
- Write raw extraction to `plans/retrospective-repo-expansion/reports/repo-inventory.md` — per-repo section with commit count, date range, and list of agentic-relevant commits with hashes and dates

**Verification:** Each repo has a non-empty section. Repos with zero agentic commits are noted (expected for `celebtwin`, `calendar-cli`).

## Step 2: Pre-claudeutils evolution timeline

**Goal:** Trace agent instruction evolution through the 6 pre-claudeutils repos (chronological order).

**Repos:** `rules` → `oklch-theme` → `scratch/box-api` → `scratch/emojipack` → `scratch/home` → `scratch/pytest-md`

**Actions:**
- For each repo, `git show` the earliest and latest versions of AGENTS.md (or equivalent agent instruction file)
- Extract key evolution signals:
  - When was the agent instruction file created? What was its initial content?
  - What sections/rules were added over time?
  - What patterns appear that later show up in claudeutils?
- Build a chronological evolution table (same format as existing topic reports): Date | Hash | Repo | Event
- Write to `plans/retrospective-repo-expansion/reports/pre-claudeutils-evolution.md`

**Verification:** Timeline covers Oct 2025 – Jan 2026 with entries from all 6 repos.

## Step 3: Parallel project evidence extraction

**Goal:** Extract evidence from 8 parallel agentic projects showing pattern propagation and agent-core adoption.

**Repos:** `pytest-md`, `home`, `tuick`, `jobsearch`, `devddaanet`, `deepface`, `emojipack`, `ddaanet`

**Actions:**
- For each repo, extract:
  - AGENTS.md → CLAUDE.md migration point (if both exist, like `tuick`)
  - Agent-core adoption point (submodule addition, `.claude/` directory creation)
  - Worktree usage, skill invocation, deliverable-review patterns
  - Any commit messages referencing claudeutils patterns
- Special attention to `pytest-md/agent-core` nested repo (204 commits) — this is agent-core's origin before submodule extraction
- Write to `plans/retrospective-repo-expansion/reports/parallel-projects.md`

**Verification:** Each of 8 repos has a section with date-stamped evidence.

## Step 4: Topic cross-reference — map new evidence to existing 5 topics

**Goal:** Connect the new repo evidence to the existing 5 retrospective topics.

**Actions:**
- Read existing topic reports (`plans/retrospective/reports/topic-{1..5}-*.md`) for topic scope
- For each new repo's extracted evidence, tag which of the 5 topics it informs:
  1. Memory system — early AGENTS.md content (proto-memory), memory-index in agent-core
  2. Pushback — pre-pushback state visible in early AGENTS.md, evolution of anti-sycophancy rules
  3. Deliverable-review — review patterns in parallel projects
  4. Ground skill — methodology patterns, external research references
  5. Structural enforcement — gating patterns, delegation rules, enforcement evolution
- Write to `plans/retrospective-repo-expansion/reports/topic-cross-reference.md` — per-topic section listing new evidence with repo, commit hash, date, and relevance note

**Verification:** Each topic has at least 2 new evidence entries from the expanded repos.

## Step 5: New cross-repo patterns report

**Goal:** Document patterns not captured by existing 5 topics — the "new cross-repo patterns" from the brief.

**Actions:**
- Synthesize from Steps 2-4 to document:
  - **Agent instruction evolution arc:** `rules` (flat rules.md) → `oklch-theme` (AGENTS.md) → `scratch/*` (specialized) → claudeutils (CLAUDE.md + fragments + decisions)
  - **Pattern propagation timeline:** which claudeutils practices appeared in parallel projects and when (from Step 3)
  - **Agent-core extraction story:** `scratch/pytest-md` → `pytest-md/agent-core` → claudeutils submodule (from Step 3 special attention)
- Write to `plans/retrospective-repo-expansion/reports/cross-repo-patterns.md`

**Verification:** Each of the 3 pattern categories has a chronological evidence trail with commit hashes.

## Step 6: Pre-agentic baseline

**Goal:** Document the pre-agentic Claude-assisted state for contrast.

**Repos:** `celebtwin`, `calendar-cli`

**Actions:**
- Extract any Claude-related patterns (gitmoji usage, commit style, GitHub Actions)
- Document what was present BEFORE agentic patterns emerged — this is the "before" baseline
- Note absence of AGENTS.md, CLAUDE.md, agent instructions
- Write to `plans/retrospective-repo-expansion/reports/pre-agentic-baseline.md`

**Verification:** Report establishes clear contrast between pre-agentic and agentic periods.
