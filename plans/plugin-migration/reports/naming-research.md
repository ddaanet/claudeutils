# Plugin Naming Research

## Hard Constraints

- Obvious spelling — hear once, spell correctly
- Transparent purpose — developer guesses what it does
- Googlable — NOT an existing software project
- 5-8 characters
- Works as namespace: `/name:commit`, `/name:design`
- Not abbreviated, not generic, not Claude-specific

## Identity (all five dimensions)

1. **Opinionated** — strong conventions about how work should be done
2. **Automated production** — requirements + outline → working software
3. **Corrective feedback** — built-in vet/fix/re-check cycles
4. **Quality at reasonable cost** — systematic, not artisan
5. **Institutional memory** — learns, remembers, carries context

## Aesthetic

- Unpretentious, plain, professional
- Subtle wit welcome, not a punchline
- Not geeky culture references
- Not pretentious (no Latin, Welsh, mythology)

## Rejected Names

| Name | Reason |
|------|--------|
| `ac` | Abbreviation |
| `agent-core` | Internal codename |
| `cadwyn` | Pretentious (Welsh for "chain") |
| `praxium` | Pretentious (fake Latin) |
| `steward` | Not googlable (too common) |
| `forge` | Not googlable (Electron Forge, Atlassian Forge, etc.) |
| `navi` | Too geeky (Zelda) |
| `pylons` | Too geeky, Python framework collision |
| `clippy` | Too geeky |
| `rigor` | Rigor mortis negative connotation |
| `praxis` | Taken — Ruby API framework, PM framework, EMR software |
| `creed` | Assassin's Creed search pollution |
| `cadence` | Cadence Design Systems (NASDAQ: CDNS) collision |
| `ledger` | Crypto hardware wallet collision |
| `primer` | Primer.ai collision |
| `loom` | Loom video tool collision |
| `runward` | Not transparent enough |
| `condukt` | Looks like a typo |
| `squire` | Slightly RPG, incomplete identity coverage |
| `drills` | Good but identity coverage weak |
| `runbook` | Too narrow — undersells broader scope |
| `govern` | Enterprise/bureaucratic connotation |

## Liked But Incomplete

| Name | Chars | Strengths | Gaps |
|------|-------|-----------|------|
| `rebar` | 5 | Good vibe, invisible reinforcement, googlable | Purpose not transparent from name |
| `tenet` | 5 | Opinionated, principled, googlable | Misses production/automation dimension |
| `lathe` | 5 | Spec in → quality out, feedback loops, googlable | Weaker on beliefs/opinions dimension |

## Scoring Matrix (best candidates)

| Name | Opinionated | Production | Feedback | Quality/Cost | Memory | Total /15 | Googlable |
|------|-------------|-----------|----------|-------------|--------|-----------|-----------|
| `tenet` | 3 | 1 | 1 | 2 | 1 | 8 | ✓ |
| `lathe` | 2 | 3 | 3 | 3 | 1 | 12 | ✓ |
| `rebar` | 1 | 2 | 1 | 2 | 1 | 7 | ✓ |

## Brainstorm Rounds

7 rounds completed across Opus subagents. Progression:
1. Meaningful names (steward, rigging, forge) — too common
2. Googlable fabrications (cadwyn, runward, praxium) — pretentious
3. Down-to-earth tools (rebar, runlog, rigging) — rebar liked
4. Geek culture (navi, pylons, squire) — too geeky
5. Transparent/plain (rigor, runbook, drills) — rigor liked but death connotation
6. Production metaphors (lathe, reify, forge) — lathe liked
7. Multi-dimensional (praxis, govern, steward) — praxis taken

## Next Steps

Name not yet chosen. Continue brainstorming with full constraint set above. Consider exploring:
- Compound words that naturally combine "opinionated" + "production"
- Words from quality engineering / lean manufacturing
- Words that describe the overall system behavior pattern
- Less common but real English words with the right connotations
