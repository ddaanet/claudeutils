# Consolidation: Phase 4

**Context**: Read `consolidation-context.md` for full context before executing this phase.

---

## Phase 4: Integrate Content into agent-core

Update agent-core repository structure:

### 4.1 Skills Directory (NEW)

```
agent-core/skills/
  handoff/SKILL.md               # From pytest-md (context management)
  commit/SKILL.md                # From pytest-md (generic parts only)
  plan-design/SKILL.md           # From pytest-md (generic core)
  plan-tdd/SKILL.md              # From pytest-md (TDD cycle structure)
  review-analysis/SKILL.md       # From pytest-md (generic analysis)
```

**Project-specific skills stay local**:
- pytest-md/execute-tdd (pytest-specific)
- pytest-md/review-updates (project-specific file refs)

### 4.2 Configs Directory (NEW)

```
agent-core/configs/
  justfile-base.just             # Common recipes (help, dev, test, check, format, lint, release)
  ruff-base.toml                 # Common ruff ignores and settings
  mypy-base.toml                 # Strict mode + common overrides
  docformatter-base.toml         # Common docformatter settings
```

### 4.3 Fragments Directory (expand existing)

```
agent-core/fragments/
  # Existing (from Phase 1):
  AGENTS-framework.md
  communication.md
  delegation.md
  tool-batching.md
  roles-rules-skills.md
  hashtags.md

  # NEW from pytest-md CLAUDE.md:
  context-management.md          # Session.md protocol, handoff patterns
  documentation-organization.md  # File naming conventions, directory structure
  orchestration-patterns.md      # Opus orchestration, sub-agent usage, model selection

  # NEW from tuick:
  code-style.md                  # Python conventions, typing, 88-char limit
  planning-principles.md         # Data-first architecture, design patterns
```

---


---

**Execution Instructions**:
1. Read consolidation-context.md for prerequisites, critical files, and execution notes
2. Execute this phase following the actions listed above
3. Perform validation checks as specified
4. Document results in execution report
5. Stop on any unexpected results per communication rules
