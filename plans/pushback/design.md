# Pushback Design

## Problem Statement

LLM agents are sycophantic — they agree with user proposals rather than evaluating them critically. In design discussions (`d:` mode), this produces yes-manning that degrades decision quality. The agent should push back with genuine evaluation: articulating costs, risks, and unconsidered alternatives before agreeing, and articulating specifically WHY when it does agree.

## Requirements

**Source:** `plans/pushback/requirements.md`

**Functional:**
- FR-1: Structural pushback in design discussions — addressed by fragment behavioral rules + hook counterfactual injection
- FR-2: Detect agreement momentum — addressed by fragment self-monitoring rule
- FR-3: Model selection evaluation — addressed by fragment model tier evaluation rule

**Non-functional:**
- NFR-1: Not sycophancy inversion (genuine evaluation, not reflexive disagreement) — addressed by evaluator framing, "articulate WHY" rules
- NFR-2: Lightweight mechanism — addressed by zero-cost fragment + string-only hook modification

**Out of scope:**
- Adversary agent / second-opinion pattern (cost, per requirements)
- External state tracking for agreement momentum
- Precommit enforcement of model selection (circumventable)
- Inline code span detection in hook (depends on pending markdown parser task)

## Research Grounding

**Model-level baseline:** Claude 4.5 is 70-85% less sycophantic than 4.1 (Anthropic Petri evaluation). This intervention amplifies existing model capability.

**Validated prompt-level techniques:**

| Technique | Evidence | Application |
|-----------|----------|-------------|
| Counterfactual prompting | SparkCo, ICLR 2025 SSM | Hook injection: "What assumptions? What would need to be true for this to fail?" |
| Context/motivation | Anthropic docs: Claude generalizes better with WHY | Fragment explains sycophancy harm, not just rules |
| Evaluator framing | Multiple sources: evaluator > devil's advocate | Fragment uses "evaluate critically" not "play devil's advocate" |
| Confidence calibration | SparkCo, practitioner guides | Fragment: "State confidence, what would change assessment" |
| Non-leading design | SparkCo: frame for evaluation not validation | Hook frames discussion as evaluation, not confirmation |

**Fundamental limitation:** LLMs lack persistent world models for principled disagreement. Prompt-level mitigation is amplification, not cure. Success is empirical.

**Sources:**
- [Reducing LLM Sycophancy: 69% Improvement Strategies](https://sparkco.ai/blog/reducing-llm-sycophancy-69-improvement-strategies)
- [Anthropic: Protecting Well-Being of Users](https://www.anthropic.com/news/protecting-well-being-of-users)
- [Claude 4 Prompting Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
- [The "Yes Sir" Problem](https://danialamin.com/pages/articles/2025-06-29-yes-man.html)
- [Structured Sycophancy Mitigation (ICLR 2025)](https://proceedings.iclr.cc/paper_files/paper/2025/file/a52b0d191b619477cc798d544f4f0e4b-Paper-Conference.pdf)

## Architecture

### Two-Layer Mechanism

```
Layer 1: Fragment (ambient)                Layer 2: Hook (targeted)
┌──────────────────────────┐              ┌──────────────────────────┐
│ pushback.md              │              │ userpromptsubmit hook    │
│ - Loaded via CLAUDE.md @ │              │ - Fires on d:/discuss:   │
│ - Always in context      │              │ - Injects evaluation     │
│ - Behavioral rules       │              │   structure via          │
│ - Agreement monitoring   │              │   additionalContext      │
│ - Model selection        │              │ - Targeted reinforcement │
│ - 100% ambient recall    │              │ - Zero latency cost      │
└──────────────────────────┘              └──────────────────────────┘
         ↕                                         ↕
    ALL conversations                     discuss: conversations only
```

**Why two layers:**
- Fragment provides 100% ambient recall (Vercel study: ambient 100% vs invoked 79%)
- Hook provides targeted reinforcement at the decision point (discussion mode entry)
- Fragment alone: lacks salience when discussion mode activates
- Hook alone: no presence outside `d:` mode — agent can yes-man in regular conversation

### Layer 1: Fragment (`agent-core/fragments/pushback.md`)

The fragment provides behavioral rules loaded via CLAUDE.md `@`-reference. Always in context, zero per-turn cost.

**Content structure:**

```markdown
## Pushback

[Motivation: WHY sycophancy is harmful — Claude generalizes better with context]

### Design Discussion Evaluation

[Rules for evaluating proposals in discussion mode]
- Before agreeing: articulate what assumptions the proposal makes
- Identify what would need to be true for the proposal to fail
- Name at least one unconsidered alternative
- If the idea IS good: articulate specifically WHY (not vague agreement)
- State confidence level and what evidence would change the assessment

### Agreement Momentum

[Self-monitoring rule for consecutive agreements]
- Track agreement patterns within a conversation
- If 3+ consecutive agreements without substantive pushback: flag explicitly
- "I notice I've agreed with several proposals in a row — let me re-evaluate..."

### Model Selection

[Rules for evaluating model tier when creating pending tasks]
- Evaluate cognitive requirements against model capability
- Opus: design, architecture, nuanced reasoning, synthesis from complex discussions
- Sonnet: balanced work, implementation planning, standard execution
- Haiku: mechanical execution, repetitive patterns
- Do not default to sonnet — assess each task
```

**Design principles applied:**
- Motivation before rules (research: Claude generalizes better with WHY)
- Evaluator framing, never devil's advocate (research: DA is performative)
- Counterfactual structure ("what would need to be true for this to fail")
- Confidence calibration ("state confidence, what would change assessment")
- Self-monitoring for agreement runs (ambient awareness mechanism)

### Layer 2: Hook Enhancement (`agent-core/hooks/userpromptsubmit-shortcuts.py`)

#### Enhanced `d:` Directive

Current injection:
```python
'd': (
    '[DIRECTIVE: DISCUSS] Discussion mode. Analyze and discuss only — '
    'do not execute, implement, or invoke workflow skills. '
    "The user's topic follows in their message."
),
```

Enhanced injection:
```python
'd': (
    '[DIRECTIVE: DISCUSS] Discussion mode — evaluate critically, do not execute. '
    'Before agreeing with any proposal: (1) identify assumptions it makes, '
    '(2) articulate what would need to be true for it to fail, '
    '(3) name at least one unconsidered alternative. '
    'If the idea is good, state specifically WHY — not vague agreement. '
    'State your confidence level.'
),
```

The hook reinforces the fragment's behavioral rules at the exact moment discussion mode activates. This is the "targeted salience" layer.

#### Long-Form Directive Aliases

Add `'discuss'` and `'pending'` as keys in `DIRECTIVES` dict pointing to same expansions:

```python
DIRECTIVES = {
    'd': DISCUSS_EXPANSION,
    'discuss': DISCUSS_EXPANSION,
    'p': PENDING_EXPANSION,
    'pending': PENDING_EXPANSION,
}
```

Both short and long forms map to identical behavior. Self-documenting for new users, muscle memory preserved.

#### Any-Line Directive Matching

**Current:** `re.match(r'^(\w+):\s+(.+)', prompt)` — matches only at prompt start.

**New:** Scan all lines for directive patterns, excluding lines inside fenced code blocks.

```python
def find_directive(prompt: str) -> Optional[tuple[str, str]]:
    """Find first directive in prompt, skipping fenced code blocks.

    Returns (directive_key, rest_of_line) or None.
    """
    in_fence = False
    fence_pattern = None

    for line in prompt.split('\n'):
        stripped = line.strip()

        # Track fenced code blocks (3+ backticks or tildes)
        fence_match = re.match(r'^(`{3,}|~{3,})', stripped)
        if fence_match:
            if not in_fence:
                in_fence = True
                fence_pattern = fence_match.group(1)[0]  # ` or ~
                fence_min_len = len(fence_match.group(1))
                continue
            elif stripped.startswith(fence_pattern * fence_min_len) and \
                 stripped.rstrip(fence_pattern) == '':
                in_fence = False
                fence_pattern = None
                continue

        if in_fence:
            continue

        # Match directive pattern on this line
        match = re.match(r'^(\w+):\s+(.+)', stripped)
        if match:
            key = match.group(1)
            if key in DIRECTIVES:
                return (key, match.group(2))

    return None
```

**Fenced block handling:**
- Tracks opening fence (3+ backticks or tildes)
- Closing fence must use same character and at least same count
- Lines inside fenced blocks are skipped entirely

**Inline code spans:** Not handled initially. Depends on pending markdown parser task. Low risk — directives inside inline backticks in chat messages is an exotic edge case.

**Tier 1 commands (exact match) remain unchanged.** Only Tier 2 directive matching is updated.

### Wiring

**CLAUDE.md change:** Add `@agent-core/fragments/pushback.md` reference in the Core Behavioral Rules section, after `@agent-core/fragments/execute-rule.md`.

**Symlink sync:** Run `just sync-to-parent` after hook changes (hook lives in agent-core, symlinked to `.claude/hooks/`).

**Restart required:** Hook changes require session restart to take effect.

## Key Design Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| D-1 | Fragment over skill | Ambient (100%) beats invoked (79%). Pushback needed in ALL modes. |
| D-2 | Enhance existing `d:` hook | Zero infrastructure cost — extend string, don't create new hook. |
| D-3 | Self-monitoring over external state | Hook is stateless. State files add complexity. Fragment makes concern salient. |
| D-4 | Model selection in fragment | Applies beyond discussion mode. Always available. |
| D-5 | Long-form directive aliases | `discuss:` / `pending:` alongside `d:` / `p:`. Self-documenting. |
| D-6 | Any-line directive matching | Users type multi-line messages. Directives shouldn't require first-line placement. |
| D-7 | Fenced block exclusion, inline deferred | Fenced: reuse existing preprocessor code. Inline: depends on pending parser task. |

## Implementation Notes

### Affected Files

| File | Change |
|------|--------|
| `agent-core/fragments/pushback.md` | NEW — behavioral rules fragment |
| `agent-core/hooks/userpromptsubmit-shortcuts.py` | MODIFY — enhanced directive, aliases, any-line matching |
| `CLAUDE.md` | MODIFY — add `@agent-core/fragments/pushback.md` reference |
| Symlinks via `just sync-to-parent` | UPDATE — sync after hook changes |

### Testing Strategy

Manual validation with four scenarios:
1. **Good idea evaluation:** Propose a genuinely good design idea in `d:` mode. Verify agent articulates specifically WHY it's good, not vague agreement.
2. **Flawed idea pushback:** Propose a flawed idea. Verify agent identifies assumptions, failure conditions, alternatives before agreeing.
3. **Agreement momentum:** Make 3+ consecutive proposals in `d:` mode that the agent agrees with. Verify agent flags the agreement run.
4. **Model selection:** Create a pending task requiring opus-level reasoning. Verify agent evaluates model tier against cognitive requirements.

Hook unit tests:
- Long-form aliases produce same output as short forms
- Any-line matching finds directives on non-first lines
- Fenced code blocks are excluded from directive search
- Tier 1 exact-match behavior unchanged

### Phase Typing

All phases are **general** (not TDD). This is behavioral rule creation and hook string modification — not code with testable behavioral contracts.

### Dependencies

- **Fenced block detection:** Existing markdown preprocessor code — refactoring opportunity to shared utility
- **Inline code span detection:** Pending markdown parser task — deferred, added when parser lands

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agent-core/fragments/communication.md` — existing behavioral rules (avoid conflict)
- `agent-core/fragments/deslop.md` — writing style for fragment
- `agent-core/fragments/execute-rule.md` — directive vocabulary, shortcut definitions
- `agent-core/hooks/userpromptsubmit-shortcuts.py` — current hook implementation
- `plans/pushback/reports/explore-hooks.md` — hook exploration results

**Additional research allowed:** Planner may do additional exploration for markdown fenced block detection patterns in the existing preprocessor.

## Next Steps

1. `/runbook plans/pushback/design.md` — create execution runbook
2. **Skill loading for planning:** `plugin-dev:hook-development` if planner needs hook API details
3. **Execution model:** Sonnet for all phases (behavioral rules + hook modification, no architectural decisions remaining)
4. **Restart required** after hook changes land — note in runbook
