# Consolidation: Phase 1

**Context**: Read `consolidation-context.md` for full context before executing this phase.

---

## Phase 1: Copy Files to Scratch

Copy out-of-tree files into scratch/ for sandbox-safe work:

```
scratch/consolidation/
  emojipack/
    compose.sh                # /Users/david/code/emojipack/agents/
    compose.yaml              # /Users/david/code/emojipack/agents/

  tuick/
    build.py                  # /Users/david/code/tuick/agents/
    Makefile                  # /Users/david/code/tuick/agents/
    src/                      # ALL .md files from /Users/david/code/tuick/agents/src/
      *.md                    # 17 fragment files

  pytest-md/
    CLAUDE.md                 # /Users/david/code/pytest-md/CLAUDE.md
    skills/                   # /Users/david/code/pytest-md/.claude/skills/
      commit/SKILL.md
      execute-tdd/SKILL.md
      handoff/SKILL.md
      plan-design/SKILL.md
      plan-tdd/SKILL.md
      review-analysis/SKILL.md
      review-updates/SKILL.md

  configs/
    justfile-claudeutils     # /Users/david/code/claudeutils/justfile
    justfile-pytest-md        # /Users/david/code/pytest-md/justfile
    justfile-tuick            # /Users/david/code/tuick/justfile
    pyproject-claudeutils.toml  # /Users/david/code/claudeutils/pyproject.toml
    pyproject-pytest-md.toml    # /Users/david/code/pytest-md/pyproject.toml
    pyproject-tuick.toml        # /Users/david/code/tuick/pyproject.toml
```

**Total files**: ~35 files to copy

---


---

**Execution Instructions**:
1. Read consolidation-context.md for prerequisites, critical files, and execution notes
2. Execute this phase following the actions listed above
3. Perform validation checks as specified
4. Document results in execution report
5. Stop on any unexpected results per communication rules
