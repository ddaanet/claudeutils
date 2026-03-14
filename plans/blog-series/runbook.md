# Blog Series Runbook

**Type:** Investigation (general steps, no TDD)
**Model:** opus throughout
**Input:** 14 raw material files in `plans/retrospective/content/`, brief.md, conversation-full-export.md

## Step 1: Challenge Series Structure

**Goal:** Evaluate the proposed series ordering and produce a final post list.

**Input:**
- Proposed ordering from claude.ai conversation: Remember → Ground → Handoff → Deliverable Review → Pipeline/isolation/worktrees. Pushback as potential standalone.
- Raw materials: `plans/retrospective/content/` (all 14 files)
- Key user framing from brief.md (LLMs don't reason, it's still programming, trial and error not deliberate architecture, skills = stopping reinvention)
- Narrative arcs from `cross-topic-connections.md` §Blog Narrative Implications

**Evaluation criteria:**
- Does the ordering serve a didactic arc (each concept builds on the previous)?
- Does the ordering serve the thesis from `appendix-underlying-model.md` (structural constraint > prose instruction)?
- Where does pushback belong? Is it standalone, or integrated into another post?
- What's the right opening — something visceral (385 tests, 8 visual bugs) or foundational (Remember)?
- Does the audience (devs using AI coding tools, broad) need all 5+ posts or can topics merge?
- Are there raw materials that don't map to any proposed post? Are there proposed posts without sufficient raw materials?

**Output:** `plans/blog-series/series-structure.md`
- Ordered post list with working titles
- Per-post: scope (which topics/arcs), thesis, target length
- Ordering rationale
- Material mapping: which source files feed each post

## Step 2: Per-Post Synthesis

**Goal:** For each post in the finalized structure, create a post-oriented evidence synthesis.

**Input:**
- `plans/blog-series/series-structure.md` (from Step 1)
- Source files mapped per-post in series-structure.md
- User framing corrections from brief.md (must be applied — oklch-theme, proto-pushback, scratch/ repos, devddaanet validation)

**Per-post synthesis contains:**
- Opening hook (concrete failure or surprising finding)
- Core argument with evidence chain (commit refs, measurements, session excerpts)
- Narrative arc within the post
- Connection to series thesis
- Transition to next post

**Constraints:**
- Every claim must cite specific evidence (commit hash, measurement, session ID) or be explicitly marked `[UNGROUNDED]`
- Apply all corrections from brief.md — do not use superseded framings
- Do not write the blog post itself — write the synthesis that a blog writer would use

**Output:** `plans/blog-series/posts/post-N-<slug>.md` for each post

## Step 3: Claims Audit

**Goal:** Systematically identify unsubstantiated claims across all post syntheses.

**Input:** All `plans/blog-series/posts/post-N-*.md` files

**Audit each synthesis for:**
- Claims citing evidence that doesn't exist in the raw materials
- Causal claims ("X caused Y") without temporal/evidential support
- Quantitative claims without measurement source
- Generalization claims ("always", "never", "every") without exhaustive evidence
- Framing claims that contradict user corrections in brief.md

**Output:** `plans/blog-series/claims-audit.md`
- Per-post section
- Each flagged claim: quote, location, reason flagged, research action needed
- Priority: claims central to the post's argument first

## Step 4: Research Flagged Claims

**Goal:** Ground or retract flagged claims through evidence.

**Input:** `plans/blog-series/claims-audit.md`

**Research methods:**
- Codebase: `git -C` on referenced repos to verify commit claims, dates, content
- Raw materials: re-read source files for evidence missed in synthesis
- Web search: external grounding for methodology claims (ISO/IEEE references, established patterns)

**Per-claim resolution:**
- **Grounded:** cite specific evidence found
- **Adjusted:** revised claim with evidence-supported version
- **Retracted:** claim removed, replacement suggested or gap noted

**Output:** Updated `plans/blog-series/claims-audit.md` with resolution column

## Step 5: Adjust Syntheses

**Goal:** Update post syntheses based on research findings.

**Input:**
- `plans/blog-series/claims-audit.md` (resolved)
- `plans/blog-series/posts/post-N-*.md` files

**Actions:**
- Replace ungrounded claims with grounded versions
- Remove retracted claims and adjust narrative flow
- Add evidence found during research that strengthens existing claims
- Verify corrections from brief.md are consistently applied

**Output:** Updated `plans/blog-series/posts/post-N-*.md` files
