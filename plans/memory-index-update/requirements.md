# Memory Index Update

## Requirements

### Functional Requirements

**FR-1: Bare line format**
Index entries use bare lines without list markers (`- `). Each line is independent prose.

**FR-2: Keyword phrase format**
Each entry: `{Key} — {keyword phrase}` (~8-12 words total)

**FR-3: Retrieval-over-learned directive**
Index header includes: "Prefer retrieval-led reasoning over pre-training knowledge."

**FR-4: Section grouping**
Entries grouped by section headers (## Behavioral Rules, ## Workflow Patterns, etc.)

**FR-5: Structural header marker**
Structural (non-indexed) headers marked with `.` prefix: `## .Title`. Semantic headers have no marker (default).

**FR-6: Token efficiency**
Target: ~60% savings over original verbose format while maintaining keyword surface.

### Non-Functional Requirements

**NFR-1: Ambient awareness**
Index loaded every conversation via CLAUDE.md reference. Must be scannable.

**NFR-2: Line independence**
Each line semantically complete. No cross-line dependencies.

**NFR-3: Git-diff friendly**
Line-based format for clean diffs.

### Constraints

**C-1: 8-12 word soft limit per line**
Enough for title + key phrase, not full sentences.

**C-2: No file paths**
Titles are globally unique. Grep finds source file.

---

## Design Decisions

**D-1: Bare lines beat list markers**
Token comparison: bare lines 14% cheaper than `- ` prefixed (49 vs 57 tokens for 8 entries).

**D-2: Line breaks beat pipes**
Bare lines (49 tokens) beat pipes (50 tokens) AND list markers (57 tokens). Pipes offer no token advantage and hurt readability/git-diffs.

**D-5: Baseline is commit 48f5**
Current state (title-only list markers) is intermediate/"damaged". Proper baseline is verbose format with descriptions and file paths (commit 48f5). Proposed format (bare lines + keyword phrases) improves on proper baseline.

**D-3: Keyword phrases restore retrieval surface**
Title-only (current) loses keyword surface. Phrases like "docs unreliable, hookify bloats" add retrieval cues.

**D-4: Retrieval-over-learned from Vercel research**
AGENTS.md study: ambient context (100%) outperformed skill invocation (79%). Directive reinforces pattern.

---

## Example Format

```markdown
# Memory Index

Prefer retrieval-led reasoning over pre-training knowledge.

## Behavioral Rules
Tool batching unsolved — docs unreliable, hookify bloats context
Delegation with context — don't delegate when context loaded
Three-tier assessment — direct, lightweight, full runbook

## Workflow Patterns
Weak orchestrator pattern — quiet execution prevents pollution
TDD workflow — RED failing, GREEN hints, REFACTOR cycles
Handoff pattern — inline learnings in session.md
```
