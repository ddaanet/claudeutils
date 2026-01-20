---
name: test-tdd
type: tdd
model: sonnet
---

# Test TDD Runbook

**Context**: Integration test for TDD runbook processing.

---

## Common Context

**Objective**: Test TDD cycle format support in prepare-runbook.py.

**Conventions**:
- Use RED-GREEN-REFACTOR cycle
- Document stop conditions
- Track dependencies

---

## Cycle 1.1: First Feature

**Dependencies**: None (first cycle)

**Objective**: Implement initial feature.

### RED Phase

Write failing test for feature:
```python
def test_feature():
    assert feature_works() == True
```

### GREEN Phase

Implement minimal logic to pass test:
```python
def feature_works():
    return True
```

### REFACTOR Phase

Clean up code:
- Extract constants
- Add documentation
- Remove duplication

**Stop Conditions**:
- All tests pass
- Code coverage > 80%
- No pylint warnings

---

## Cycle 1.2: Feature Enhancement

**Dependencies**: Cycle 1.1 complete

**Objective**: Enhance existing feature.

### RED Phase

Write test for enhancement:
```python
def test_enhancement():
    assert enhanced_feature() == expected
```

### GREEN Phase

Implement enhancement:
```python
def enhanced_feature():
    return expected
```

### REFACTOR Phase

Optimize implementation:
- Improve performance
- Simplify logic

**Stop Conditions**:
- All tests pass
- Performance benchmarks met
- Code review complete

---

## Cycle 2.1: New Component

**Dependencies**: Cycle 1.2 complete

**Objective**: Add new independent component.

### RED Phase

Write component tests:
```python
def test_component():
    component = Component()
    assert component.validate()
```

### GREEN Phase

Implement component:
```python
class Component:
    def validate(self):
        return True
```

### REFACTOR Phase

Extract reusable logic:
- Create base class
- Add utilities

**Stop Conditions**:
- All tests pass
- Integration tests pass
- Documentation updated
