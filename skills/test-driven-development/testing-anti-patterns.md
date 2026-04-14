# Testing Anti-Patterns

**Load this reference when:** writing or changing tests, adding mocks, or tempted to add test-only methods to production code.

## The Iron Laws

1. NEVER test mock behavior
2. NEVER add test-only methods to production classes
3. NEVER mock without understanding dependencies

## Anti-Pattern 1: Testing Mock Behavior
Don't assert on mock elements. Test real component behavior.

## Anti-Pattern 2: Test-Only Methods in Production
Put test cleanup in test utilities, not production classes.

## Anti-Pattern 3: Mocking Without Understanding
Understand dependencies before mocking. Mock at the right level.

## Anti-Pattern 4: Incomplete Mocks
Mock the COMPLETE data structure, not just fields your test uses.

## Anti-Pattern 5: Integration Tests as Afterthought
Testing is part of implementation, not optional follow-up.

## Quick Reference

| Anti-Pattern | Fix |
|--------------|-----|
| Assert on mock elements | Test real component or unmock it |
| Test-only methods in production | Move to test utilities |
| Mock without understanding | Understand dependencies first |
| Incomplete mocks | Mirror real API completely |
| Tests as afterthought | TDD - tests first |
