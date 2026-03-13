# Brief: Outline template trim

## 2026-03-13: Remove Decision References from outline template

During /proof review of handoff-cli-tool outline, "Decision References" section was killed. The section listed recall entries relevant to implementation — but that's the recall artifact's job (`plans/<job>/recall-artifact.md`), not the outline's.

**Scope:**
- Remove Decision References from `/design` skill's outline generation template
- Update `design-corrector` to not require/expect the section
- Phase Notes section stays — consumed by agent definitions via outline cache

**Evidence:** Recall artifact already exists in the pipeline (`prepare-runbook.py` resolves it). Decision References in the outline is redundant infrastructure that duplicates the recall system's function.
