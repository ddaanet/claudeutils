# Handoff Entry Point

## Current Task: Module System Implementation

**Status:** Design complete, ready for Phase 1 (tooling implementation)

**Goal:** Transform monolithic agent role files into composable module system with semantic
sources and generated variants (strong/standard/weak). Target: ≤150 total rules.

### What's Done

- ✅ **Design decisions** - All Opus reviews complete (tier markers, config location, dev workflow)
- ✅ **Module extraction** - 14 semantic sources in `agents/modules/src/*.semantic.md`
- ✅ **Module inventory** - `agents/modules/MODULE_INVENTORY.md`
- ✅ **Directory structure** - `agents/roles/` for configs, `.next.md` pattern for safe development
- ✅ **Implementation plan** - Detailed Phase 1 plan ready for Haiku execution

### What's Next

**NEXT:** Phase 1.1 - Test expansion quality (Sonnet vs Opus comparison)

Then:
1. **Phase 1.2: Rule Counter** - Build script to count `[RULE:Tn]` markers
2. **Phase 2: Variant Generator** - Generate variants from semantic sources
3. **Phase 3: Role Composer** - Compose role files from module variants
4. **Phase 7: Testing & Cutover** - A/B test, then atomic rename via `make cutover`

### Key Files to Read

| File | Purpose |
|------|---------|
| `plans/PLAN_PHASE1_MODULE_SYSTEM.md` | Detailed Phase 1 plan for Haiku (ready to execute) |
| `plans/plan-module-system-outline.md` | Full 8-phase implementation plan |
| `plans/opus-review-module-tiering.md` | Tier marker design decisions |
| `plans/design-question-role-config-location.md` | Config location decision (agents/roles/) |
| `plans/DESIGN_MODULE_SYSTEM.md` | Complete design specification |
| `agents/modules/MODULE_INVENTORY.md` | Summary of 14 extracted modules |

### Key Design Decisions (from Opus Reviews)

1. **Tier markers**: `[RULE:T1]`, `[RULE:T2]`, `[RULE:T3]` in generated variants
2. **Semantic sources**: Tier hints via section groupings (Critical/Important/Preferred)
3. **Target counts**: Ranges in frontmatter (e.g., `weak: 12-18`)
4. **Config location**: `agents/roles/{role}.yaml` - clear purpose, discoverable
5. **Development naming**: `.next.md` suffix prevents overwriting during development
6. **Skills**: Weak-only, no variants (loaded at session end)
7. **Validation**: Warnings not failures for budget overflow
8. **Cutover**: Atomic via `make cutover` - safe migration from old to new

### Directory Structure

```
agents/
├── roles/                      # Role configs (to be created in Phase 5)
│   ├── planning.yaml
│   ├── code.yaml
│   ├── lint.yaml
│   ├── execute.yaml
│   ├── refactor.yaml
│   ├── review.yaml
│   └── remember.yaml
├── modules/
│   ├── src/                    # 14 semantic sources (✅ complete)
│   │   ├── communication.semantic.md
│   │   ├── tool-batching.semantic.md
│   │   ├── checkpoint-obedience.semantic.md
│   │   ├── plan-adherence.semantic.md
│   │   ├── plan-creation.semantic.md
│   │   ├── context-overview.semantic.md
│   │   ├── context-datamodel.semantic.md
│   │   ├── context-commands.semantic.md
│   │   ├── tdd-cycle.semantic.md
│   │   ├── code-quality.semantic.md
│   │   ├── code-review.semantic.md
│   │   ├── memory-management.semantic.md
│   │   ├── commit.semantic.md
│   │   └── handoff.semantic.md
│   ├── gen/                    # Generated variants (empty)
│   └── MODULE_INVENTORY.md
├── role-planning.md            # Current production roles
├── role-planning.next.md       # Development outputs (Phase 7)
├── role-code.md
├── ...
└── archive/                    # Old files after cutover

Note: .next.md files prevent overwriting during development
```

### Pipeline Flow

```
agents/roles/planning.yaml
    ↓
[Variant Selection] → agents/modules/gen/*.weak.md
    ↓
[Tier Extraction] → CRITICAL_RULES/GUIDELINES/PREFERENCES
    ↓
[Marker Removal] → Clean output
    ↓
agents/role-planning.next.md (dev) → role-planning.md (after cutover)
```

---

## Core Context

1. `AGENTS.md` - Project overview, user preferences, role/rule definitions
2. `agents/DESIGN_DECISIONS.md` - Architectural and implementation decisions
3. `agents/TEST_DATA.md` - Data types and sample entries

## Roles (Load at Session Start)

- `agents/role-planning.md` - Design test specifications (opus/sonnet)
- `agents/role-code.md` - TDD implementation (haiku)
- `agents/role-lint.md` - Fix lint/type errors (haiku)
- `agents/role-refactor.md` - Plan refactoring (sonnet)
- `agents/role-execute.md` - Execute planned changes (haiku)
- `agents/role-review.md` - Code review and cleanup (sonnet)
- `agents/role-remember.md` - Update agent documentation (opus)

## Rules (Load Before Action)

- `agents/rules-commit.md` - **Read before any `git commit`**
- `agents/rules-handoff.md` - Read before ending a session

## Quick Reference

See `README.md` for usage examples and development commands.

Run `just dev` to verify all tests pass.
