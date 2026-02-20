# Session Handoff: 2026-02-20

**Status:** Pipeline improvements task complete. Worktree ready for merge.

## Completed This Session

**Pipeline prose quality fixes:**
- Design skill review gate: changed Phase B step 4 from confidence-gated ("if significant changes made") to transition-gated ("after applying changes") in `agent-core/skills/design/SKILL.md`
- Pending task capture: added "(noun-phrase, not verbatim user text)" to CLAUDE.md pending task notation
- Design-history noise audit: grep scan of fragments/skills found no rejected-alternative noise in directives (all "instead of" / "alternative" hits were legitimate anti-pattern descriptions)
- Deslop pass on skills:
  - `opus-design-question`: removed Purpose (redundant with always-loaded `design-decisions.md`), Integration with Workflows (generic restatement), Benefits, Success Criteria, Notes sections. Net -137 lines.
  - `next`: removed redundant "When NOT to Use", "Important Notes" sections; condensed Purpose; fixed example to reference shelf instead of session.md; fixed constraints check order. Net -25 lines.
  - Added missing `name:` frontmatter to 6 skills: commit, orchestrate, release-prep, requirements, shelve, vet
- Vet-requirement batch decomposition: added paragraph to Proportionality section clarifying per-file triage then per-type routing for multi-file changes

**RCA: Reviewer routing bypass:**
- Deviation: routed skill file changes to vet-fix-agent instead of skill-reviewer
- Root cause (structural): vet-requirement had no batch decomposition guidance; batch framing collapsed per-artifact routing into single reviewer
- Root cause (behavioral): fabricated capability limitation on skill-reviewer
- Fix: added batch decomposition paragraph to `agent-core/fragments/vet-requirement.md`
- Learning appended to learnings.md

## Pending Tasks

(none — worktree task complete)

## Next Steps

Merge worktree back to main via `wt merge pipeline-improvements`.
