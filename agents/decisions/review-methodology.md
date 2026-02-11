# Review Methodology

Systematic approach for evaluating production deliverables.

## .Scope Definition

**Deliverables** = Production artifacts that ship with the system:
- Code (implementation, tests)
- Skills and agents
- Fragments (behavioral rules)
- User-facing documentation
- Configuration files

**Not deliverables:**
- Design documents
- Plans and runbooks
- Execution reports
- Diagnostic artifacts
- Temporary files (tmp/)

## .Review Process

### .1. Inventory Phase

List all modified/created files excluding non-deliverables:
```bash
git diff --name-only <start>..<end> | grep -v "^plans/" | grep -v "^tmp/"
```

Group by type: implementation, tests, documentation, configuration.

### .2. Verification Phase

For each deliverable, verify against requirements:
- Design spec alignment
- Requirement coverage
- Cross-reference consistency (paths, names, APIs)

### .3. Evaluation Phase

Apply type-specific evaluation axes (see below).

### .4. Issue Classification

- **Critical**: Incorrect behavior, spec violations, security issues
- **Major**: Missing validation, poor error handling, broken references
- **Minor**: Style issues, verbose code, suboptimal clarity

## .Evaluation Axes

### .Code Implementation

1. **Correctness** — Matches design spec, implements requirements accurately
2. **Completeness** — All specified features present, no requirement gaps
3. **Robustness** — Error handling, edge cases, input validation
4. **Clarity** — Readable, maintainable, appropriate naming
5. **Efficiency** — Suitable algorithms, no wasteful operations
6. **Cohesion** — Focused responsibilities, single-purpose functions
7. **Coupling** — Minimal dependencies, clean interfaces
8. **Vacuity** — No trivial wrappers, dead code, or empty abstractions
9. **Testability** — Structured for verification, mockable dependencies
10. **Consistency** — Follows project patterns and conventions

### .Tests

1. **Expressiveness** — Clear intent, communicates what's being tested
2. **Concision** — Focused scope, minimal duplication, no bloat
3. **Specificity** — Precise assertions, tests exact behaviors
4. **Pertinence** — Validates requirements, not implementation details
5. **Vacuity** — No tautological tests, redundant checks, or tests that can't fail
6. **Coverage** — All requirements and edge cases represented

### .Documentation (Skills, Fragments, Guides)

1. **Clarity** — Unambiguous instructions, no vague criteria
2. **Actionability** — Agent can execute without guessing
3. **Efficiency** — Deslop compliant, no explanatory bloat
4. **Correctness** — Accurate paths, commands, references
5. **Completeness** — All modes/scenarios covered
6. **Consistency** — Matches implementation, no contradictions

### .Configuration Files

1. **Correctness** — Valid syntax, correct values
2. **Completeness** — All required entries present
3. **Consistency** — Matches referenced files/paths

## .Cross-Cutting Checks

Apply to all deliverables:

**Path consistency:**
- Directory references match actual structure
- No obsolete paths from previous designs

**Name consistency:**
- Function/class names match documentation
- Command names consistent across docs/implementation

**API contracts:**
- Signatures match between caller and callee
- Return values match documentation

**Requirement traceability:**
- Each FR-N requirement maps to deliverable(s)
- No deliverable without requirement justification

## .Quality Gates

Before approval:
- [ ] All deliverables inventoried
- [ ] Critical issues: 0
- [ ] Major issues: documented with mitigation plan
- [ ] Cross-references validated
- [ ] Requirement coverage complete

## .Anti-Patterns

**Review process failures:**
- Trusting vet reports without primary source verification
- Evaluating tests without reading implementation
- Checking file presence without content validation
- Assuming documentation matches code

**Evaluation shortcuts:**
- "Tests pass" ≠ "tests are good"
- "Vet approved" ≠ "deliverable is correct"
- "Code works" ≠ "code is maintainable"
- Negative tests without positive validation = vacuous coverage
