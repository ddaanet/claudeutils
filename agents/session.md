# Session: Worktree — Domain-specific validation design

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Design support for domain-specific and optional project-specific validation** — Start with plugin-dev review agents | opus

## Context

Design a system that supports:
- **Domain-specific validation:** Validation rules that apply to specific types of work (plugin development, skill development, etc.)
- **Optional project-specific validation:** Projects can opt into additional validation beyond standard checks
- **Starting point:** Plugin-dev review agents as first use case

## Design Questions

- How do agents discover which validations apply to current work?
- Where do validation rules live? (fragments, dedicated directory, plugin-specific?)
- How do projects opt into optional validations?
- Integration with existing vet/review workflows?
- Extensibility model for new domains?

## Reference Files

- **agent-core/fragments/vet-requirement.md** — Current vet workflow
- **.claude/plugins/** — Existing plugin structure
