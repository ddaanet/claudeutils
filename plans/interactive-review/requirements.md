# Interactive Review (Proof Enhancement)

Extend `/proof` with item-by-item review mode. Currently /proof reviews an artifact as a whole — user reads, gives feedback, changes accumulate. This adds structured iteration over discrete items within an artifact, with per-item recall context.

## Requirements

### Functional Requirements

**FR-1: Item-by-item iteration mode**
When invoked on an artifact containing enumerable items, present items one at a time. User gives verdict per item (approve, revise, kill, discuss). Apply verdict immediately before advancing.
- Acceptance: `/proof plans/foo/requirements.md` with 5 FRs → presents FR-1, waits for verdict, applies, presents FR-2, etc.
- Acceptance: Existing whole-artifact mode preserved — item-by-item activates based on artifact structure or explicit flag

**FR-2: Artifact-type granularity**
Adapt item granularity to artifact type:
- `requirements.md` → individual FRs/NFRs/constraints
- Diff output → individual hunks or files
- Source files → individual functions/classes/sections
- Plan files → individual steps or phases
- Acceptance: Granularity detection is automatic based on artifact structure
- Acceptance: User can override granularity (e.g., "review by file" vs "review by hunk")

**FR-3: Per-item recall pass**
Before presenting each item, resolve domain-relevant recall entries for that item's topic. Surface related work, prior decisions, absorptions — context the reviewer needs to make an informed verdict.
- Acceptance: Reviewing FR about fuzzy matching → recall surfaces ar-threshold-calibration before presenting
- Acceptance: No relevant recall → item presented without delay (null recall is silent)

**FR-4: Verdict vocabulary**
Structured verdicts with immediate application:
- **approve** (a) → strip review markers if present, advance
- **revise** (r) → user states revision, edit applied, advance
- **kill** (k) → remove item from artifact, advance
- **discuss** (d) → enter discussion sub-loop (d: semantics), then return to verdict
- **absorb** → kill item, note absorption target, update target artifact
- Acceptance: Single-letter shortcuts work
- Acceptance: Revision edits applied to the artifact file immediately

**FR-5: Verdict application as direct edits**
Verdicts produce immediate file edits — not accumulated for later sync. Killed items removed, revisions written, absorptions update both source and target. Artifact is always current.
- Acceptance: After reviewing 3 of 5 FRs, the file on disk reflects all 3 verdicts
- Acceptance: Interruption at item 4 preserves items 1-3 verdicts (no lost work)

**FR-6: Cross-item outputs**
Review may produce outputs beyond the artifact itself:
- **Learnings** from discussion → appended to learnings.md
- **Pending tasks** from discussion → captured for handoff
- **New plan artifacts** from absorb/kill decisions → created immediately
- Acceptance: Discussion that surfaces a task → `p:` semantics applied inline

**FR-7: Review summary**
After all items reviewed, produce summary: N approved, N revised, N killed, N absorbed. List any cross-item outputs (tasks, learnings, new artifacts).
- Acceptance: Summary shown after last item

### Constraints

**C-1: Extension, not replacement**
Item-by-item is a new mode within /proof. Existing whole-artifact review (reword-accumulate-sync) unchanged. Mode selection based on artifact structure or user flag.

**C-2: Proof loop mechanics preserved**
Discussion sub-loop (d verdict) uses existing reword-accumulate-sync within a single item's scope. The per-item loop wraps the existing proof mechanics.

### Out of Scope

- Automated review (agent-driven verdicts) — this is human-in-the-loop review
- Multi-artifact review in single invocation (review one artifact at a time)
- Persistent review state across sessions (resume from item N) — session handoff captures progress naturally

### References

- `agent-core/skills/proof/SKILL.md` — existing proof skill (enhancement target)
- This session's requirements review walkthrough — direct evidence of the pattern working manually

### Skill Dependencies (for /design)

- Load `plugin-dev:skill-development` before design (modifying /proof skill)
