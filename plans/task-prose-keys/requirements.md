# Task Prose Keys

## Requirements

### Functional Requirements

**FR-1: Prose key format**
Replace hash tokens (#xK9f2) with prose keys embedded in task description.

**FR-2: Near-zero marginal cost**
Key is part of task description text, not additional syntax.

**FR-3: Uniqueness validation**
Task keys unique across:
- session.md
- todo.md
- shelved tasks
- git history (for keys introduced in current commit only)

**FR-4: Namespace separation**
Task keys and learning keys are disjoint sets. Same validation infrastructure, different constraints.

**FR-5: Context recovery**
Prose key enables lookup of session.md from introducing commit (existing task-context.sh functionality).

**FR-6: Merge commit handling**
For uniqueness check, compare against "before" side of diff against all parents after first.

### Non-Functional Requirements

**NFR-1: Precommit validation**
New task keys checked for uniqueness during precommit.

**NFR-2: Collision feedback**
If collision detected, report existing usage location.

**NFR-3: No loaded history**
Don't load all historical keys into context. Use git log -S for targeted search.

### Constraints

**C-1: No syntax decoration**
Task key is plain prose, no markers like `**Key:**` or `{Key}`.

**C-2: Key extraction pattern**
Key extracted from task line format: `- [ ] **Task Name** — description`
Task Name = key.

---

## Design Decisions

**D-1: Task name IS the key**
No separate key field. The bold task name serves as identifier.

**D-2: History search on-demand**
Precommit runs `git log -S "Task Name"` for new tasks only. O(1) per new task, not O(n) for all history.

**D-3: Disjoint from learnings**
Task key "Implement foo" and learning key "Implement foo" would conflict. Validator enforces disjointness.

---

## Task Format

**Current (with hash tokens):**
```markdown
- [ ] **Orchestrator scope consolidation** #E7u8A — delegate checkpoint phases | sonnet
```

**After (prose key = task name):**
```markdown
- [ ] **Orchestrator scope consolidation** — delegate checkpoint phases | sonnet
```

Key = "Orchestrator scope consolidation" (the bold task name, no separate token needed)

---

## Validation Flow

```
precommit
  → extract task names from session.md
  → identify NEW tasks (not in any parent commit)
  → for each new task:
      → git log -S "Task Name" to check history
      → check against current learning keys
  → report collisions
```
