# Merge Artifact: Orphaned Learnings Bullets

**Date:** 2026-02-23
**Source:** Manual audit of last 3 merges on main

## Observed Issue

Merge `6086650e` (quality-infra-reform into main) produced orphaned bullet points in `agents/learnings.md`. Six lines (anti-patterns, correct patterns, evidence) from three distinct learnings entries were appended under the wrong heading ("When selecting reviewer for artifact review") without their `## When` headings.

## Affected Commits

- `6086650e` — `Merge quality-infra-reform` (merge commit where orphans appeared)
- Merge parents: `8bc9377a` (main), `7694be3f` (quality-infra-reform branch)
- Merge base: `22434a5b`
- `37f2ab32` — post-merge fix commit (did not catch this issue)

## Root Cause

The quality-infra-reform branch had learnings entries that duplicated content already present under proper headings on main (lines 120, 148, 156, 164). During 3-way merge, git resolved the append-only file by keeping both sides' additions. The branch's duplicates lost their `## When` headings during conflict resolution, leaving orphaned bullets under the preceding entry.

## Orphaned Content (now removed)

Lines 211-216 (pre-fix) were orphaned duplicates of:
- "When all work is prose edits with pre-resolved decisions" (line 120)
- "When review gates feel redundant after user-validated changes" (line 148)
- "When assessing fragment demotion from always-loaded context" (line 156)
- "When batch changes span multiple artifact types" (line 164)

## Relation to Existing Diagnostic

`plans/worktree-merge-resilience/diagnostic.md` already documents the general class: "Merge resolution produces orphaned lines in append-only files." This is a concrete instance confirming the diagnostic's predictions. The orphans were headingless bullets rather than duplicated full entries — a variant not yet covered.

## Detection Gap

The existing blocker note says "Manual post-merge check required until worktree-merge-resilience automated." No automated check caught this. The `just precommit` pass doesn't validate learnings.md structural integrity (every bullet under a `## When` heading).
