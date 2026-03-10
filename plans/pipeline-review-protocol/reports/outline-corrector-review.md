# Outline Corrector Review

**Artifact:** agent-core/agents/outline-corrector.md
**Date:** 2026-03-10
**Scope:** Recent additions — scope-to-component traceability and cross-component interface compatibility checks

## Summary

The new criteria were functionally correct but had four structural gaps: the two checks were conflated into one dimension, the Response Protocol and Verification steps were not updated to include the new checks, and the Critical Constraints traceability section was incomplete. All issues fixed.

## Findings

### Minor — Conflated dimensions in section 3

**Location:** Section 3, "Scope-to-Component Traceability" criterion

**Problem:** One named dimension covered two distinct verification modes — membership check (is every Scope IN item assigned to a component?) and type-compatibility check (do producer/consumer interfaces match?). Different logic, different fix actions, different severity triggers. Conflating them makes it ambiguous which check produced a finding and harder to track independently.

**Fix:** Split into two named dimensions — "Scope-to-Component Traceability" (orphan detection only) and "Cross-Component Interface Compatibility" (type-compatibility check). Each now has its own bullet list and severity guidance.

**Status:** FIXED

### Minor — Response Protocol step 3 incomplete

**Location:** Response Protocol, step 3

**Problem:** "Build traceability matrix (every FR-* maps to outline)" — no mention of scope-to-component mapping table. Agent could build only the requirements matrix, satisfy the protocol, and skip scope-to-component mapping.

**Fix:** Updated to "Build traceability matrices (FR-* → outline sections; Scope IN items → components)"

**Status:** FIXED

### Minor — Response Protocol step 4 missing new dimensions

**Location:** Response Protocol, step 4

**Problem:** "Review against criteria (soundness, completeness, feasibility, clarity, scope)" — new dimensions absent. Agent following the protocol literally would skip them.

**Fix:** Appended "scope-to-component traceability, cross-component interface compatibility" to the criteria list.

**Status:** FIXED

### Minor — Critical Constraints traceability section incomplete

**Location:** Critical Constraints, "Traceability" subsection

**Problem:** Only listed FR-* → outline mapping. The scope-to-component and interface checks were not listed as required, making them optional in the agent's constraint model.

**Fix:** Added two bullets: "Every Scope IN item must map to a component or standalone implementation section" and "Cross-component interfaces must be verified for type compatibility."

**Status:** FIXED

### Minor — Review report template missing Scope-to-Component section

**Location:** Section 6, review report template

**Problem:** Template had Requirements Traceability table but no Scope-to-Component Traceability table. Agent would build the table in section 4 but have no structured place to report it.

**Fix:** Added "Scope-to-Component Traceability" section to report template with table and assessment line.

**Status:** FIXED

### Minor — Verification step 2 incomplete

**Location:** Verification, item 2

**Problem:** "Verify traceability matrix includes all requirements" — scope-to-component mapping not in the verification checklist. Agent could pass verification without having built it.

**Fix:** Added item 3: "Verify scope-to-component mapping table covers all Scope IN items" (renumbered subsequent items).

**Status:** FIXED

## Positive Observations

- Fix-all policy (section 5) is correctly scoped to document review — rationale is sound
- Recall context loading (section 2, item 4) handles artifact-absent and resolve-fails gracefully
- Merge-don't-append rule in section 5 prevents duplicate section creation
- Input validation (artifact type + requirements existence) is thorough
- Response Protocol ordering is logical — matrices built before criteria review, fixes before report

## Summary Counts

- Critical: 0
- Major: 0
- Minor: 6 (all fixed)
