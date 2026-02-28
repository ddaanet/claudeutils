# Pushback Grounding

Add claim verification and recall to the `d:` discussion protocol. The current protocol is purely reasoning-based — it asks "what assumptions does the proposal make?" but never verifies whether those assumptions hold against actual project state.

## Requirements

### Functional Requirements

**FR-1: Claim verification step**
Before agreeing or disagreeing with a factual claim about project state, verify the claim by reading the relevant artifact. Claims in the user's prompt define the verification scope — no separate scoping mechanism needed.

Acceptance criteria:
- Pushback protocol includes a verification step before assessment formation
- "X is resolved by Y" → Read Y before evaluating
- "These two tasks overlap" → Read both task definitions before evaluating
- "Z covers this" → Read Z before evaluating
- Verification is structural (protocol step with tool call), not advisory (prose instruction)
- Absent artifacts are a valid verification result (claim references something that doesn't exist)

**FR-2: Discussion recall pass**
Resolve relevant memory-index entries for the discussion topic before forming assessment. Prior decisions inform whether a proposal conflicts with, duplicates, or extends existing work.

Acceptance criteria:
- Extract topic from the `d:` prompt content
- Scan memory-index for relevant entries
- Resolve via `when-resolve.py` (batch, same infrastructure as `/recall`)
- Loaded decisions available during assessment formation
- Lightweight — not a full `/recall all`, just topic-relevant entries

**FR-3: Integration with existing protocol**
The verification and recall steps precede the existing pushback reasoning steps (form assessment, stress-test, state verdict). The existing protocol steps remain unchanged.

Acceptance criteria:
- New steps run before "Form your assessment" in pushback.md
- Existing reasoning protocol (stress-test, verdict, confidence) preserved
- Agreement momentum tracking unchanged

**FR-4: Hook expansion update**
The `[DISCUSS]` expansion injected by `userpromptsubmit-shortcuts.py` must reference the grounding steps, not just the reasoning steps.

Acceptance criteria:
- `_DISCUSS_EXPANSION` in `userpromptsubmit-shortcuts.py` updated to include claim verification directive
- Expansion remains concise (hook injection is space-constrained)
- Tests in `test_userpromptsubmit_shortcuts.py` updated to match

### Constraints

**C-1: D+B anchoring**
Verification must be anchored with a tool call (Read, Grep, Bash), not a prose judgment about whether verification is needed. The D+B principle: unconditional verification where absence is the negative path. A Read returning file-not-found is cheaper than the risk of uninformed agreement.

**C-2: Scope bounded by claims**
Verification scope derives from claims in the user's prompt. No open-ended exploration. "Is X superseded by Y?" → read Y. "Should we remove Z?" → read Z. The discussion prompt itself names what needs verification.

**C-3: Proportionate recall**
Recall is topic-scoped scan + resolve, not full `/recall all`. The `d:` directive is meant to be responsive — adding 30 seconds of recall loading defeats the purpose.

### Out of Scope

- Changes to `/recall` skill itself
- Hook-based automatic injection of recall content (that's the UserPromptSubmit topic task)
- Changes to non-discussion directives (`p:`, `q:`, `learn:`)
- Pushback protocol changes beyond adding grounding steps (reasoning protocol is working)

### Dependencies

- `agent-core/bin/when-resolve.py` — resolution infrastructure (stable, includes null mode)
- `agents/memory-index.md` — entry scanning target

### References

- `agent-core/fragments/pushback.md` — current discussion protocol (primary edit target)
- `agent-core/hooks/userpromptsubmit-shortcuts.py` — `d:` directive hook expansion
- `agents/decisions/defense-in-depth.md` — D+B anchoring pattern, structural fix over prose
- `agents/decisions/operational-practices.md` — recall effectiveness (4.1% metacognitive activation rate)

### Skill Dependencies (for /design)

- Load `plugin-dev:hook-development` before design (hook expansion in FR-4)
