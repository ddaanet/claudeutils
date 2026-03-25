# Review Skip: FR-1 SessionStart TMPDIR fix

**Changed:** `agent-core/hooks/sessionstart-health.sh` — 1 line added

**Change:** `TMPDIR="${TMPDIR:-/tmp}"` added after `set -euo pipefail`, before any TMPDIR access.

**Why review adds no value:**
- 1 net line added, no deletions
- Identical pattern to `stop-health-fallback.sh` line 4 (sibling script, proven working)
- Additive initialization, no control flow altered
- No contract or interface changes

**Verification performed:**
- Reproduced root cause: `env -i` test confirmed "TMPDIR: unbound variable" on line 9 without fix
- Confirmed fix resolves unbound variable error
- Confirmed pattern matches `stop-health-fallback.sh` exactly (diff verified)
- No other TMPDIR accesses in the script — all downstream uses are safe once initialized
