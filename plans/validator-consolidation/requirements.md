# Validator Consolidation

## Requirements

### Functional Requirements

**FR-1: Unified command**
Single claudeutils entry point for all validation: `claudeutils validate [targets]`

**FR-2: Learnings validation**
- Title format: semantic marker + title text
- Max word count per title (5 words)
- No duplicate titles
- No empty titles

**FR-3: Memory index validation**
- Each entry matches a semantic header in indexed files
- Each entry resolves unambiguously (single source)
- No duplicate index entries

**FR-4: Task key validation**
- Task keys unique within session.md, todo.md, shelved tasks
- New task keys (in current commit) unique across git history
- Task keys disjoint from learning keys

**FR-5: Orphan detection**
- Semantic headers (marked with prefix) that aren't in index = orphan
- Report orphans as warnings

**FR-6: Precommit integration**
Single `just precommit` call runs all validators.

### Non-Functional Requirements

**NFR-1: Test coverage**
Full test suite for validators as claudeutils package components.

**NFR-2: Clear error messages**
Line numbers, file paths, specific issue description.

**NFR-3: Fast execution**
Validators run in <1s for typical project size.

### Constraints

**C-1: Merge commit handling**
For task key uniqueness, check against all parents after first (not just HEAD~1).

**C-2: CLAUDE.md as root marker**
Scripts use CLAUDE.md to find project root, not agents/ directory.

---

## Design Decisions

**D-1: Consolidate to claudeutils package**
Current: standalone scripts in agent-core/bin/. Proposed: src/claudeutils/validation.py with CLI entry point.

**D-2: Shared patterns extracted**
Title extraction, file discovery, uniqueness checking shared between validators.

**D-3: Test suite required**
As claudeutils components, validators must have tests. Write post-hoc for existing logic.

---

## Current Scripts

| Script | Location | Function |
|--------|----------|----------|
| validate-learnings.py | agent-core/bin/ | Title format, word count, uniqueness |
| validate-memory-index.py | agent-core/bin/ | Entry existence, ambiguity, duplicates |
| task-token.py | agent-core/bin/ | Token expansion, will become key validation |

---

## Migration Path

1. Create `src/claudeutils/validation.py` with shared utilities
2. Port validator logic with tests
3. Add CLI entry point in pyproject.toml
4. Update justfile to use new command
5. Deprecate agent-core/bin/ scripts
