# Phase 1: Step 8

**Context**: Read `phase1-execution-context.md` for full context before executing this step.

---

### Step 8: Test justfile Import in Test Repository

**Objective**: Verify justfile import mechanism works with submodule.

**Technical Details**:
- justfile native import: `import 'path/to/file.just'`
- Import path: `agent-core/fragments/justfile-base.just`

**Actions**:
1. In test repository justfile, add at top: `import 'agent-core/fragments/justfile-base.just'`
2. Add project-specific recipes after import
3. Run `just --list` to verify imported recipes visible
4. Test one imported recipe (e.g., `just format` if format recipe exists)
5. Verify project-specific recipes still work

**Validation**:
- [ ] Import syntax accepted by just
- [ ] Imported recipes visible in `just --list`
- [ ] Imported recipes execute correctly
- [ ] Local recipes can override imported ones (if tested)

**Error Cases to Handle**:
- Import path incorrect
- Circular import (shouldn't occur in Phase 1)
- Variable conflicts between imported and local

---


---

**Execution Instructions**:
1. Read phase1-execution-context.md for prerequisites and validation patterns
2. Execute this step following the actions listed above
3. Perform validation checks
4. Document results in execution report
5. Stop on any unexpected results per communication rules
