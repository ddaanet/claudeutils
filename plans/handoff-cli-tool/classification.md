## Fix RC13 — Composite Task Classification

**18 actionable items** (4 dismissed: m-4, m-20, m-21, m-22)

- **Classification:** Moderate (composite)
- **Implementation certainty:** High — all fixes have clear specs (findings + outline)
- **Requirement stability:** High — findings stable, design complete
- **Behavioral code check:** Yes — m-1, m-2, m-3, m-5, m-6, m-7 change logic paths
- **Work type:** Production
- **Artifact destination:** production
- **Evidence:** 6 of 7 code items modify conditional branches/data flow. Outline.md provides design spec.

### Actionable Items

**Code (6):** m-1, m-2, m-3, m-5, m-6, m-7 — all Moderate (behavioral)
**Test (10):** m-8, m-9, m-10, m-11, m-12, m-13, m-14, m-15, m-16, m-17 — mix Simple/Moderate
**Prose (2):** m-18, m-19 — Simple

### Dismissed

- **m-4:** Defensive `len > 3` guard — removing harmless defensive code is net negative
- **m-20:** Scope observation (standalone bugfix) — not actionable
- **m-21:** Trailing newline only — trivial config churn
- **m-22:** .gitignore broadening — reasonable change, scope note only
