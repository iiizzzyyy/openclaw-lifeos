---
name: test-driven-development
description: Drives development with tests. Use when implementing any logic, fixing any bug, or changing any behavior. Use when you need to prove that code works, when a bug report arrives, or when you're about to modify existing functionality.
---

# Test-Driven Development

## Overview

Write a failing test before writing the code that makes it pass. For bug fixes, reproduce the bug with a test before attempting a fix. Tests are proof — "seems right" is not done. A codebase with good tests is an AI agent's superpower; a codebase without tests is a liability.

## When to Use

- Implementing any new logic or behavior
- Fixing any bug (the Prove-It Pattern)
- Modifying existing functionality
- Adding edge case handling
- Any change that could break existing behavior

**When NOT to use:** Pure configuration changes, documentation updates, or static content changes that have no behavioral impact.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over.

## The TDD Cycle

```
    RED                GREEN              REFACTOR
 Write a test    Write minimal code    Clean up the
 that fails  ──→  to make it pass  ──→  implementation  ──→  (repeat)
      │                  │                    │
      ▼                  ▼                    ▼
   Test FAILS        Test PASSES         Tests still PASS
```

### Step 1: RED — Write a Failing Test

Write the test first. It must fail. A test that passes immediately proves nothing.

```python
# RED: This test fails because create_task doesn't exist yet
def test_creates_task_with_title_and_default_status():
    task = task_service.create_task(title="Buy groceries")

    assert task.id is not None
    assert task.title == "Buy groceries"
    assert task.status == "pending"
    assert isinstance(task.created_at, datetime)
```

### Step 2: GREEN — Make It Pass

Write the minimum code to make the test pass. Don't over-engineer:

```python
# GREEN: Minimal implementation
def create_task(title: str) -> Task:
    return Task(
        id=generate_id(),
        title=title,
        status="pending",
        created_at=datetime.now(),
    )
```

### Step 3: REFACTOR — Clean Up

With tests green, improve the code without changing behavior:

- Extract shared logic
- Improve naming
- Remove duplication
- Optimize if necessary

Run tests after every refactor step to confirm nothing broke.

## The Prove-It Pattern (Bug Fixes)

When a bug is reported, **do not start by trying to fix it.** Start by writing a test that reproduces it.

```
Bug report arrives
       │
       ▼
  Write a test that demonstrates the bug
       │
       ▼
  Test FAILS (confirming the bug exists)
       │
       ▼
  Implement the fix
       │
       ▼
  Test PASSES (proving the fix works)
       │
       ▼
  Run full test suite (no regressions)
```

**Example:**

```python
# Bug: "Completing a task doesn't update the completed_at timestamp"

# Step 1: Write the reproduction test (it should FAIL)
def test_sets_completed_at_when_task_is_completed():
    task = task_service.create_task(title="Test")
    completed = task_service.complete_task(task.id)

    assert completed.status == "completed"
    assert isinstance(completed.completed_at, datetime)  # This fails → bug confirmed

# Step 2: Fix the bug
def complete_task(task_id: str) -> Task:
    return db.tasks.update(
        task_id,
        status="completed",
        completed_at=datetime.now(),  # This was missing
    )

# Step 3: Test passes → bug fixed, regression guarded
```

## The Test Pyramid

Invest testing effort according to the pyramid — most tests should be small and fast, with progressively fewer tests at higher levels:

```
          ╱╲
         ╱  ╲         E2E Tests (~5%)
        ╱    ╲        Full user flows, real browser
       ╱──────╲
      ╱        ╲      Integration Tests (~15%)
     ╱          ╲     Component interactions, API boundaries
    ╱────────────╲
   ╱              ╲   Unit Tests (~80%)
  ╱                ╲  Pure logic, isolated, milliseconds each
 ╱──────────────────╲
```

**The Beyonce Rule:** If you liked it, you should have put a test on it. Infrastructure changes, refactoring, and migrations are not responsible for catching your bugs — your tests are.

## Test Sizes

| Size | Constraints | Speed | Example |
|------|------------|-------|---------|
| **Small** | Single process, no I/O, no network, no database | Milliseconds | Pure function tests, data transforms |
| **Medium** | Multi-process OK, localhost only, no external services | Seconds | API tests with test DB, component tests |
| **Large** | Multi-machine OK, external services allowed | Minutes | E2E tests, performance benchmarks |

## Writing Good Tests

### Test State, Not Interactions

Assert on the *outcome* of an operation, not on which methods were called internally.

```python
# Good: Tests what the function does (state-based)
def test_returns_tasks_sorted_by_creation_date_newest_first():
    tasks = list_tasks(sort_by="created_at", sort_order="desc")
    assert tasks[0].created_at > tasks[1].created_at

# Bad: Tests how the function works internally (interaction-based)
def test_calls_db_query_with_order_by():
    list_tasks(sort_by="created_at", sort_order="desc")
    db.query.assert_called_with(expect.string_containing("ORDER BY created_at DESC"))
```

### DAMP Over DRY in Tests

In production code, DRY (Don't Repeat Yourself) is usually right. In tests, **DAMP (Descriptive And Meaningful Phrases)** is better.

```python
# DAMP: Each test is self-contained and readable
def test_rejects_tasks_with_empty_titles():
    with pytest.raises(ValidationError, match="Title is required"):
        create_task(title="")

def test_trims_whitespace_from_titles():
    task = create_task(title="  Buy groceries  ")
    assert task.title == "Buy groceries"

# Over-DRY: Shared setup obscures what each test actually verifies
```

### Prefer Real Implementations Over Mocks

```
Preference order (most to least preferred):
1. Real implementation  → Highest confidence
2. Fake                 → In-memory version of a dependency
3. Stub                 → Returns canned data, no behavior
4. Mock (interaction)   → Verifies method calls — use sparingly
```

**Use mocks only when:** the real implementation is too slow, non-deterministic, or has side effects you can't control.

### Use the Arrange-Act-Assert Pattern

```python
def test_marks_overdue_tasks_when_deadline_has_passed():
    # Arrange: Set up the test scenario
    task = create_task(title="Test", deadline=datetime(2025, 1, 1))

    # Act: Perform the action being tested
    result = check_overdue(task, current_time=datetime(2025, 1, 2))

    # Assert: Verify the outcome
    assert result.is_overdue is True
```

### One Assertion Per Concept

```python
# Good: Each test verifies one behavior
def test_rejects_empty_titles(): ...
def test_trims_whitespace_from_titles(): ...
def test_enforces_maximum_title_length(): ...

# Bad: Everything in one test
def test_validates_titles_correctly():
    assert create_task(title="").title is None
    assert create_task(title="  hi  ").title == "hi"
```

## Test Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Testing implementation details | Tests break on refactor even if behavior is unchanged | Test inputs and outputs |
| Flaky tests | Erode trust in the test suite | Use deterministic assertions |
| Mocking everything | Tests pass but production breaks | Prefer real implementations |
| No test isolation | Tests pass individually but fail together | Each test sets up its own state |

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll write tests after the code works" | You won't. |
| "This is too simple to test" | Simple code gets complicated. |
| "Tests slow me down" | Tests slow you down now. They speed you up later. |
| "I tested it manually" | Manual testing doesn't persist. |

## Verification Checklist

- [ ] Every new behavior has a corresponding test
- [ ] Watched each test fail before implementing
- [ ] Wrote minimal code to pass each test
- [ ] All tests pass
- [ ] Bug fixes include a reproduction test
- [ ] Edge cases covered
