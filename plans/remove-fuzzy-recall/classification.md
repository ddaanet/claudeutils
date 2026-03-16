# Classification: Remove Fuzzy Recall

- **Classification:** Moderate
- **Implementation certainty:** High — approach specified in brief, code locations confirmed
- **Requirement stability:** High — FRs mechanism-specified (differentiated error messages for keyword-form vs artifact-form)
- **Behavioral code check:** Yes — removes `_get_suggestions()`, `_handle_no_match()`, changes `_resolve_trigger()` from fuzzy to exact matching
- **Work type:** Production — behavioral change to agent CLI tooling
- **Artifact destination:** production (`src/claudeutils/when/resolver.py`)
- **Evidence:** "When Triaging Behavioral Code Changes As Simple" recall entry confirms Moderate minimum. `fuzzy.py` stays — used by compress.py, validation modules.

## Open Design Question

`_find_heading()` (resolver.py:259-294) also uses `fuzzy.rank_matches` as fallback for heading lookup in decision files. Brief specifies `_get_suggestions()` and `_handle_no_match()` removal but doesn't mention `_find_heading()`. Second fuzzy path — scope TBD during runbook planning.
