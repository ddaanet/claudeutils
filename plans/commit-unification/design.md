# Design: Unify Commit Skills + Inline Gitmoji

## Problem

Three skills (`/commit`, `/commit-context`, `/gitmoji`) have entangled dependencies that cause workflow interruptions:

1. **Nested skill bug** (GitHub #17351): Both commit skills invoke `/gitmoji` via `Skill` tool, causing context switch that requires user to say "continue"
2. **Duplication**: commit and commit-context share ~70% identical content (message style, validation flags, TDD pattern, constraints, gitmoji step, handoff step)
3. **Same bug with /handoff**: Both commit skills also invoke `/handoff`, creating a second interruption point

## Requirements

**Functional:**
- Merge commit + commit-context into single `/commit` skill with `--context` flag
- Inline gitmoji selection (read index directly, no `/gitmoji` skill invocation)
- Inline handoff execution (read handoff protocol directly, no `/handoff` skill invocation)
- Preserve all existing flags: `--test`, `--lint`, `--no-gitmoji`, `--context`
- Keep `/gitmoji` as standalone user-invocable skill (unchanged)
- Keep `/handoff` as standalone user-invocable skill (unchanged)

**Out of scope:**
- Changing gitmoji skill itself
- Changing handoff skill itself
- Changing any skills that reference `/commit` (orchestrate, plan-tdd, vet, remember)

## Approach

### Unified Commit Skill Structure

```
commit/
├── SKILL.md           (unified skill, ~3K words)
├── references/
│   ├── gitmoji-index.txt   (copy of gitmoji cache)
│   └── handoff-protocol.md (extracted handoff protocol for inline use)
└── scripts/
    └── update-gitmoji-index.sh  (copy or symlink)
```

### Key Design Decisions

**1. Copy gitmoji index vs symlink vs @file reference**

Decision: **Copy the file.** `references/gitmoji-index.txt` is a copy of `gitmoji/cache/gitmojis.txt`.

Rationale:
- Skills can't reliably cross-reference other skill directories
- @file references only work in CLAUDE.md, not within skill bodies
- Symlinks add fragile coupling
- The file is small (3.7K) and rarely changes
- Update script can be shared or duplicated (also small, 944B)

Tradeoff: Two copies to maintain. Mitigated by: infrequent updates (monthly), small file size, both in same agent-core repo.

**2. Handoff: inline protocol vs keep /handoff invocation**

Decision: **Keep `/handoff` invocation.** Don't inline handoff.

Rationale:
- Handoff is complex (6.5K skill + references + examples) — too large to inline
- Handoff interruption is *less disruptive* than gitmoji because it's a meaningful pause (user reviews session.md update)
- Handoff is legitimately a separate concern from committing
- The bug (#17351) affects both, but handoff's interruption is arguably a feature — user sees session context being preserved

Revisit if: Bug #17351 is fixed (then both work seamlessly), or if users report handoff interruption as a problem.

**3. --context flag behavior**

When `--context` is passed:
- Skip git status/diff discovery (step 1 becomes validation-only)
- Use conversation context for file list and change analysis
- Error if agent lacks clear context about what changed

When `--context` is NOT passed (default):
- Run full discovery: `just precommit && git status -vv`
- Analyze staged/unstaged changes from output

**4. Delete commit-context skill**

Decision: **Delete entirely.** Not archive, not deprecate.

Rationale: Code removal principle — git history preserves it. References in other skills use `/commit` not `/commit-context`. The only external reference is in CLAUDE.md's skill list (auto-discovered).

### Execution Flow (Unified)

```
1. Pre-commit validation + discovery (skip discovery if --context)
   just precommit [or --test/--lint variant]
   git status -vv  [skip if --context]

2. Perform /handoff (invoke skill — accepted interruption)

3. Draft commit message (from discovery or conversation context)

4. Select gitmoji (INLINE — read references/gitmoji-index.txt directly)
   Skip if --no-gitmoji

5. Stage, commit, verify (single bash block)
```

### Gitmoji Inline Protocol

Embedded in SKILL.md step 4 (replaces "Invoke `/gitmoji` skill"):

```
Read references/gitmoji-index.txt (~78 entries, format: emoji - name - description).
Analyze commit message semantics (type, scope, impact).
Select most specific emoji matching primary intent.
Prefix commit title with selected emoji.
```

This is ~4 lines vs invoking a full skill. The semantic matching logic is inherent to the model — the gitmoji skill's value was the index file, not the instructions.

## Affected Files

| File | Action |
|------|--------|
| `agent-core/skills/commit/SKILL.md` | Rewrite: merge commit-context content, inline gitmoji |
| `agent-core/skills/commit/references/gitmoji-index.txt` | Create: copy from gitmoji/cache/ |
| `agent-core/skills/commit/scripts/update-gitmoji-index.sh` | Create: adapted from gitmoji/scripts/ |
| `agent-core/skills/commit-context/` | Delete: entire directory |
| `agent-core/justfile` | Update: add stale symlink cleanup to sync-to-parent |
| `agent-core/skills/gitmoji/` | No change (standalone skill preserved) |
| `agent-core/skills/handoff/` | No change |

## Testing Strategy

- Invoke `/commit` (default): verify full discovery + inline gitmoji + no interruption at gitmoji step
- Invoke `/commit --context`: verify discovery skipped, context used
- Invoke `/commit --no-gitmoji`: verify gitmoji step skipped
- Invoke `/commit --test`: verify only `just test` runs
- Invoke `/gitmoji` standalone: verify still works independently

## Next Steps

`/plan-adhoc` → implementation runbook
