# Review: Settings triage protocol — SKILL.md implementation

**Scope**: `agent-core/skills/commit/SKILL.md` — step 1c addition + frontmatter Edit tool; follow-up pass addressing deliverable-review minor findings (absent-vs-empty control flow, staging command gitignore constraint)
**Date**: 2026-03-06
**Mode**: review + fix

## Summary

Initial corrector pass fixed the D+B anchor (explicit Read directive), allowlist staging instruction, and misleading permanent examples. This follow-up pass addresses two remaining deliverable-review minor findings: absent-vs-empty control flow collapsed into implicit `or` instead of explicit if/then branches, and staging command previously including `settings.local.json` (gitignored, cannot be staged). The staging command is already correct in current state — only `settings.json` is staged. The absent-vs-empty distinction remains collapsed.

**Overall Assessment**: Ready (all issues fixed)

---

## Issues Found

### Critical Issues

1. **D+B pattern declared but not implemented**
   - Location: `agent-core/skills/commit/SKILL.md` — step 1c (line 132-133)
   - Problem: The heading `**D+B anchor — Read `.claude/settings.local.json`:**` labels the step as D+B but does not instruct the agent to execute a `Read` tool call. The next line immediately branches on prose judgment ("If absent or empty: skip to step 2"). Compare to step 1, which has explicit code blocks directing each Bash call. Without an explicit tool directive, an agent running this step performs prose judgment — exactly the structural anti-pattern C-1 and the recall entry "how prevent skill steps from being skipped" prohibit.
   - Fix: Add explicit `Read(.claude/settings.local.json)` directive before the conditional logic, matching the code-block style used in step 1.
   - **Status**: FIXED

### Major Issues

1. **Staging instruction missing allowlist call pattern**
   - Location: `agent-core/skills/commit/SKILL.md` — step 1c, final line before step 2
   - Problem: "Stage both settings files if modified" omits the explicit `git add` instruction with the allowlist constraint reminder. Step 4 explicitly says "Separate Bash calls: 1. `git add <specific files>`" — step 1c should carry the same pattern for its staging action to avoid agents chaining or skipping it.
   - Fix: Add explicit `git add .claude/settings.local.json .claude/settings.json` instruction with note that it follows the allowlist constraint (separate Bash call).
   - **Status**: FIXED

### Minor Issues

1. **`echo`/`printf` as Permanent examples are misleading**
   - Location: `agent-core/skills/commit/SKILL.md` — step 1c classification table, Permanent row
   - Problem: `echo` and `printf` are shell builtins — they would not typically appear as permission entries in `settings.json`. Listing them as permanent examples could confuse classification of actual tool-allowlist entries. The brief's canonical example is `pbcopy` (a real grant). The examples column should use real grant-category examples.
   - Fix: Replace `echo`, `printf` with more representative examples (`open`, `osascript`, or similar macOS tools that require explicit grants).
   - **Status**: FIXED

2. **Absent-vs-empty control flow collapsed into implicit `or`**
   - Location: `agent-core/skills/commit/SKILL.md` — step 1c, line 138
   - Problem: `- **Read error** (file absent) or **content is `{}`** → skip to step 2` collapses two distinct cases into one branch. D+B convention requires explicit if/then branches — per deliverable review and recall "how prevent skill steps from being skipped." A Read error (file not found) and empty-content `{}` are semantically different outcomes from a Read call; collapsing them with `or` is an implicit control flow that a less attentive agent may read as prose rather than an explicit branch directive.
   - Fix: Separate into two explicit bullet branches: `- **File absent** (Read returns error) → skip to step 2` and `- **Content is `{}`** → skip to step 2`, so both cases are explicit conditional paths.
   - **Status**: FIXED

3. **Staging command correction (settings.local.json is gitignored)**
   - Location: `agent-core/skills/commit/SKILL.md` — step 1c, staging instruction
   - Problem: Prior corrector pass (Major Issue 1 fix) documented adding `git add .claude/settings.local.json .claude/settings.json`. However, `settings.local.json` is gitignored and cannot be staged. Current SKILL.md shows only `git add .claude/settings.json` — this is already correct.
   - **Status**: OUT-OF-SCOPE — current state is correct; no fix needed. The deliverable review finding about "combining two files" was addressed when the prior corrector produced the correct single-file staging instruction.

---

## Fixes Applied

**Initial corrector pass:**
- `agent-core/skills/commit/SKILL.md:132-134` — Added explicit `Read` tool call directive before conditional branch, converting prose judgment to D+B anchor
- `agent-core/skills/commit/SKILL.md:144` — Added explicit `git add` staging instruction with allowlist constraint note
- `agent-core/skills/commit/SKILL.md:140` — Replaced `echo`, `printf` with `open`, `osascript` as more accurate permanent-entry examples

**Deliverable-review follow-up:**
- `agent-core/skills/commit/SKILL.md:138` — Split `Read error or content {}` into two explicit bullet branches (file absent / content is `{}`), making absent-vs-empty control flow explicit per D+B convention

---

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Triage step, D+B pattern, Read anchor | Partial (pre-fix) → Satisfied (post-fix) | Step 1c added; D+B anchor now explicit after fix |
| FR-2: Promote permanent to settings.json, remove from local | Satisfied | Classification table: Permanent row with Edit actions |
| FR-3: Clear session-specific entries | Satisfied | Classification table: Session row with Edit remove action |
| FR-4: Job-specific retained with justification | Satisfied | Classification table: Job-specific row with handoff justification condition |
| FR-5: Classification guidance with examples | Satisfied (post-fix) | Table covers all three types; pbcopy present; echo/printf corrected |
| C-1: D+B pattern required | Satisfied (post-fix) | Read directive now explicit |
| C-3: Existing step numbering | Satisfied | 1 → 1b → 1c → 2 intact |
| C-4: Separate Bash calls for allowlist | Satisfied (post-fix) | Staging instruction now explicit |

**Gaps**: None post-fix.

---

## Positive Observations

- Classification table format is clean — three-column (classification/action/examples) maps directly to the triage decision tree
- "Classification signal" for redundant entries (already in settings.json) is a practical addition not explicitly in FR-5 but closes a real edge case
- Frontmatter `Edit` tool addition is correct and minimal — only what the new step requires
- Step placement (1c after 1b, before 2) matches the design's Q-1 resolution correctly
- "skip to step 2" cross-reference on empty/absent case prevents ambiguity about what happens next
