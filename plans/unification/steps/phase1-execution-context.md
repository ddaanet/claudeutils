# Phase 1: Foundation - Execution Plan

**Status**: Ready for review
**Target**: Haiku execution
**Date**: 2026-01-15

---

## Overview

Phase 1 establishes the foundation for the rules unification system by creating the `agent-core` repository, extracting shared fragments, and implementing template-based generation for AGENTS.md. This phase will be tested in one scratch repository before broader rollout.

---

## Prerequisites

- [ ] claudeutils repository on `unification` branch
- [ ] Access to scratch repositories for testing (emojipack or pytest-md)
- [ ] Current AGENTS.md variants available for extraction

---

## Execution Steps


---

## Common Context

This file contains shared context for all execution steps.
Each step file references this context and should be executed with both files in context.

---

## Technical Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **agent-core location** | `/Users/david/code/agent-core` | Sibling to consuming projects |
| **Initial remote** | Local only (GitHub later) | Faster iteration, can push when stable |
| **Test repository** | scratch/emojipack | Simpler for initial validation |
| **Generation script** | Bash with hardcoded fragments | Simplest implementation, YAML parsing deferred |
| **Script location** | Consumer project (`agents/compose.sh`) | Local control over composition |
| **Fragment granularity** | Single justfile-base.just | Can split later if needed |
| **Python version in configs** | py312 baseline | Document override mechanism |
| **pyproject composition** | Manual copy for Phase 1 | Automation deferred to later phases |
| **Hashtag principles** | Include 4 core tags | #stop, #delegate, #tools, #quiet |
| **Submodule URL** | Local path for testing | `/Users/david/code/agent-core` |

---

## Open Questions for Review

1. **Fragment granularity**: Is single justfile-base.just sufficient, or should we split by concern immediately?
   - Recommendation: Start single file, split in Phase 3 if needed

2. **Python version handling**: Template variable or hardcoded baseline?
   - Recommendation: Hardcode py312, document override in comments

3. **compose.yaml parsing**: Bash hardcoding or lightweight YAML parser?
   - Recommendation: Hardcode for Phase 1, parser when needed

4. **AGENTS-framework.md composition points**: Comment markers or simpler full-fragment approach?
   - Recommendation: Start without markers (simple concatenation), add if customization points emerge

5. **justfile variable naming**: What variables should be parameterized for project-specific paths?
   - Recommendation: Identify during extraction (Step 2), likely `SRC_DIR`, `TEST_DIR`, `VENV`

---

## Success Criteria

Phase 1 is complete when:

- [ ] agent-core repository exists with documented structure
- [ ] Shared fragments extracted (justfile, ruff, mypy, rule fragments)
- [ ] Template-based AGENTS.md generation works
- [ ] One test repository (emojipack or pytest-md) successfully:
  - [ ] Has agent-core as submodule
  - [ ] Generates AGENTS.md from fragments
  - [ ] Imports justfile recipes
  - [ ] Uses extracted tool configs
- [ ] Documentation explains usage and customization
- [ ] All technical decisions documented

---

## Dependencies for Execution

**Required by haiku executor**:
- Access to file system for reading/writing
- Git operations (init, submodule add, commit)
- Bash execution for testing scripts
- just command for validating justfile syntax
- ruff and mypy for validating config

**Context files for reference**:
- plans/unification/design.md (this document provides full context)
- Current AGENTS.md (claudeutils/AGENTS.md)
- Current justfile (claudeutils/justfile)
- Current pyproject.toml (claudeutils/pyproject.toml)

---

## File Outputs

This plan will result in:

**New repository**: `/Users/david/code/agent-core/`
- fragments/justfile-base.just
- fragments/ruff.toml
- fragments/mypy.toml
- fragments/communication.md
- fragments/delegation.md
- fragments/tool-preferences.md
- fragments/hashtags.md
- fragments/AGENTS-framework.md
- README.md

**Modified in test repo** (e.g., scratch/emojipack):
- .gitmodules (new submodule)
- agent-core/ (submodule directory)
- agents/compose.yaml (new)
- agents/compose.sh (new)
- agents/README.md (new)
- AGENTS.md (regenerated)
- justfile (add import statement)

**Reports**:
- plans/unification/reports/phase1-execution.md (execution log from haiku)
- plans/unification/reports/phase1-test-results.md (validation results)

---

## Execution Notes for Haiku

**Use specialized tools**:
- Read/Write/Edit for file operations (not cat/echo)
- Glob for finding files (not find/ls)
- Grep for searching content (not grep command)

**Report structure**:
Write findings to `plans/unification/reports/phase1-stepN-execution.md` with:
- Step-by-step progress
- Technical decisions made during execution
- Any deviations from plan (with rationale)
- Validation results
- Issues encountered and resolutions

**Temporary files**:
- Use `tmp/` directory in current project (e.g., `tmp/test-output.txt`)
- NEVER use `/tmp` - always use project-local `tmp/` directory

**Return format**:
- Success: `report: plans/unification/reports/phase1-stepN-execution.md`
- Failure: `error: <description>`

**Error Handling:**

If git operation fails:
- Report exact error message
- Do not retry automatically
- STOP if in Steps 1-6 (foundation required)
- Continue if in Steps 7-9 (test phase, can document failure)

If file operation fails:
- Verify parent directory exists
- Check file permissions
- Report specific missing prerequisite

If validation fails:
- Document specific failure in execution report
- Continue to next step (accumulate results)
- Mark step as incomplete in report

If critical step fails (Steps 1-6):
- STOP execution
- Report: "Critical failure in Step N: <description>"
- Do not proceed to test repository integration

**Critical**: Follow communication.md rules - stop on unexpected results and report.

---

## Review Checklist for Sonnet

When reviewing this plan:

- [ ] All Phase 1 steps from design.md:358-365 addressed
- [ ] Technical decisions are concrete and actionable
- [ ] No ambiguous instructions remain
- [ ] Validation criteria clear and measurable
- [ ] Dependencies identified
- [ ] Success criteria complete
- [ ] Plan is executable by haiku without further clarification
- [ ] Open questions have recommendations
- [ ] Report structure defined

---

## References

- plans/unification/design.md — Full design context
- AGENTS.md — Current agent instruction format (line references throughout)
- claudeutils/justfile — Source for recipe extraction
- claudeutils/pyproject.toml — Source for config extraction

