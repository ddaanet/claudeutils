# Session Handoff: 2026-03-16

**Status:** Conflict policy added to outline. Step 3.2 unblocked. Tmux mechanism design needed before orchestration.

## Completed This Session

**Outline amendment (conflict policy):**
- Added `/edify:update` conflict policy to Component 4: synced-hash tracking in `.edify.yaml`, warn-and-skip for user-edited files, auto-update for unmodified, `--force` for intentional overwrite
- Key design choice: compare consumer file against last-synced hash (not current plugin version) — distinguishes "user edited" from "plugin updated"
- Updated FR-4 validation row for conflict scenarios (safe update, conflict skip, `--force` override, hash update)
- Added "Update conflict policy" to Resolved Questions

## In-tree Tasks

- [x] **Update conflict policy** — `/design plans/plugin-migration/outline.md` | opus
  - Plan: plugin-migration | Conflict policy added to Component 4, FR-4 validation updated, Resolved Questions updated
- [ ] **Tmux verification mechanism** — `/design plans/plugin-migration/brief.md` | opus
  - Plan: plugin-migration | Design how to drive/verify live Claude sessions via tmux for Steps 1.3, 6.3. Gap documented in brief.md
- [ ] **Plugin migration** — `/orchestrate plugin-migration` | opus
  - Plan: plugin-migration | Status: ready (blocked on tmux mechanism design)
  - Note: design.md stale (outline supersedes)

## Blockers / Gotchas

**Tmux verification mechanism unresolved:**
- Steps 1.3, 2.4 (killed), 6.1, 6.3 reference "standard tmux interaction" — mechanism not designed. Brief at `plans/plugin-migration/brief.md`. Executor should treat as manual checkpoints (STOP and report).

**design.md stale:**
- Contains 5 documented errors (see outline Design Corrections section). Outline supersedes design.md for all decisions.

## Reference Files

- `plans/plugin-migration/outline.md` — authoritative outline (now includes conflict policy)
- `plans/plugin-migration/runbook-phase-3.md` — Phase 3 with Step 3.2 (previously blocked, now unblocked)
- `plans/plugin-migration/brief.md` — tmux mechanism design gap
- `plans/plugin-migration/recall-artifact.md` — recall entries for downstream consumers

## Next Steps

`/design plans/plugin-migration/brief.md` — resolve tmux verification mechanism, then `/orchestrate plugin-migration`.
