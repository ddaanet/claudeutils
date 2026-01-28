# Prompt Composer System - Implementation Plans

## Overview

The Prompt Composer System transforms monolithic agent role files into a composable,
modular architecture. This directory contains all design documents, implementation
plans, research findings, and integration work for this system.

**Key Innovation**: Semantic source files with tier hints + generated variants per model
class with `[RULE:Tn]` markers for budget tracking and composition.

**Target**: ≤150 total rules, reduced token costs, reusable cross-cutting concerns,
target-appropriate wording (strong vs weak models).

---

## Quick Start

### For Understanding the System

1. Start here: **`design.md`** - Master design specification covering all decisions
2. Then: **`opus-review-tiering.md`** - Detailed design review with tier marker
   rationale
3. Architecture guide: **`plan-outline.md`** - Full 8-phase roadmap

### For Implementation

- **`plan-phase1.md`** - Detailed Phase 1 plan (ready to execute)
- **`sysprompt-integration/`** - System prompt pattern extraction

### For Decisions

- **`design-question-config-location.md`** - Config location reasoning (agents/roles/)
- **`opus-consultation.md`** - Initial design consultation with Opus
- **`design-review-tiering.md`** - Critical gap analysis (obsoleted by opus-review)

### For Research

- **`existing-tools-research.md`** - Research on existing variant generation tools

---

## File Guide

### Core Design Documents

| File                                   | Purpose                                                      | Status        |
| -------------------------------------- | ------------------------------------------------------------ | ------------- |
| **design.md**                          | Master design spec - ALL decisions, constraints, terminology | Authority     |
| **opus-review-tiering.md**             | Opus review of tier markers, tiering strategy                | Design Review |
| **opus-consultation.md**               | Initial consultation notes with Opus                         | Historical    |
| **design-review-tiering.md**           | Critical gap analysis (OBSOLETE - resolved in opus-review)   | Superseded    |
| **design-question-config-location.md** | Config location decision with reasoning                      | Decision      |

### Implementation Plans

| File                | Phase | Purpose                             | Audience       |
| ------------------- | ----- | ----------------------------------- | -------------- |
| **plan-outline.md** | 0-8   | Full 8-phase roadmap                | Everyone       |
| **plan-phase1.md**  | 1     | Detailed Phase 1 (TDD, checkpoints) | Haiku executor |

### Supporting Materials

| File                           | Purpose                                         |
| ------------------------------ | ----------------------------------------------- |
| **existing-tools-research.md** | Variant generation tool research                |
| **sysprompt-integration/**     | System prompt pattern extraction (subdirectory) |

---

## Implementation Status

### Current Phase

**Phase 1: Foundation & Testing** - Ready for execution

Design complete ✅, Module extraction complete ✅, Implementation plan ready ✅

### Completed Work

- ✅ Design decisions finalized (all Opus reviews complete)
- ✅ Tier marker strategy defined (`[RULE:T1/T2/T3]`)
- ✅ 14 semantic sources extracted in `agents/modules/src/`
- ✅ Module inventory documented
- ✅ Directory structure defined
- ✅ Phase 1 plan ready for Haiku
- ✅ Token counter implemented (`claudeutils tokens` command)

### Next Steps

1. **Phase 1.1**: Test expansion quality (Sonnet vs Opus comparison)
2. **Phase 2**: Variant generator implementation
3. **Phase 3**: Role composer
4. **Phases 4-8**: Integration, testing, cutover

---

## Key Concepts

### Semantic Sources

- Location: `agents/modules/src/*.semantic.md`
- 14 modules: communication, tool-batching, checkpoint-obedience, plan-adherence,
  plan-creation, context-overview, context-datamodel, context-commands, tdd-cycle,
  code-quality, code-review, memory-management, commit, handoff
- Include tier hints via section groupings (Critical/Important/Preferred)
- Target ranges in frontmatter (e.g., `weak: 12-18`)

### Generated Variants

- Location: `agents/modules/gen/*.{weak,standard,strong}.{sonnet,opus}.md`
- Each variant has `[RULE:Tn]` markers:
  - `[RULE:T1]`: Critical rules (~20%)
  - `[RULE:T2]`: Important rules (~60%)
  - `[RULE:T3]`: Preferred rules (~20%)
- Target-appropriate wording per model class

### Tier Markers

- Markers embedded in generated variants
- Used for budget tracking and composition
- Extracted during role composition
- Removed in final output files

### Role Composition

Pipeline: `agents/roles/{role}.yaml` → Variant Selection → Tier Extraction → Marker
Removal → `agents/role-{role}.next.md`

### Naming Conventions

- **Semantic sources**: `{module}.semantic.md`
- **Generated variants**: `{module}.{variant-type}.{model-class}.md`
  - Variant types: `weak`, `standard`, `strong`
  - Model classes: `sonnet`, `opus`
- **Role configs**: `agents/roles/{role}.yaml`
- **Composed roles**: `agents/role-{role}.next.md` (dev) → `role-{role}.md` (after
  cutover)
- **Dev convention**: `.next.md` prevents overwriting during development

---

## Critical Decisions

1. **Tier markers**: `[RULE:Tn]` in generated variants (not in sources)
2. **Semantic sources**: Tier hints via section groupings, not encoded
3. **Target counts**: Ranges in frontmatter (e.g., `weak: 12-18`)
4. **Config location**: `agents/roles/{role}.yaml`
5. **Development naming**: `.next.md` suffix
6. **Skills**: Weak-only, no variants (loaded at session end)
7. **Validation**: Warnings not failures for budget overflow
8. **Cutover**: Atomic via `make cutover` - safe migration

---

## Integration with Module System

The prompt composer system sits at the core of the broader agent instruction
architecture:

```
agents/modules/src/ (14 semantic sources)
    ↓
[Variant Generator] → agents/modules/gen/ (weak/standard/strong per model)
    ↓
agents/roles/{role}.yaml (variant selection)
    ↓
[Role Composer] → agents/role-{role}.next.md (dev output)
    ↓
[Testing & Validation]
    ↓
make cutover → agents/role-{role}.md (production)
```

---

## File Organization

```
plans/prompt-composer/
├── README.md (this file)
├── design.md (AUTHORITY - master design spec)
├── opus-review-tiering.md (design review)
├── opus-consultation.md (consultation notes)
├── design-review-tiering.md (obsolete gap analysis)
├── design-question-config-location.md (decision rationale)
├── plan-outline.md (8-phase roadmap)
├── plan-phase1.md (detailed Phase 1)
├── existing-tools-research.md (tool research)
└── sysprompt-integration/
    ├── design.md (system prompt patterns)
    ├── tasks-opus.md (opus tasks)
    ├── tasks-delegable.md (delegable tasks)
    └── drafts.md (draft notes)
```

---

## Related Files Outside This Directory

- `agents/session.md` - Current work context with links to active plans
- `agents/modules/MODULE_INVENTORY.md` - Module inventory and status
- `agents/modules/src/` - 14 semantic sources (read-only, created in Phase 0)
- `agents/roles/` - Role configuration files (to be created in Phase 5)
- `agents/role-*.md` - Generated role files (created in Phase 3-4)

---

## How to Use This Directory

1. **Understanding the system**: Read in order: design.md → opus-review-tiering.md →
   plan-outline.md
2. **Planning implementation**: Refer to plan-outline.md for phases, plan-phase1.md for
   execution details
3. **During implementation**: Check plan-phase1.md for checkpoints, design.md for
   terminology
4. **Design questions**: Check design-*.md files for decision rationale
5. **Research**: See existing-tools-research.md and sysprompt-integration/

---

## Status Indicators

- ✅ Complete - Ready to use or reference
- 🔄 In Progress - Being worked on
- ⏸️ Blocked - Waiting on dependencies
- 📋 Pending - Not yet started
- ⚠️ Review Needed - Needs verification
- ❌ Obsolete - Superseded by newer work

---

- **Last Updated**: 2025-12-29
- **Directory Created**: Phase 0 consolidation
- **Authority**: Opus (claude-opus-4-5-20251101) for design decisions
