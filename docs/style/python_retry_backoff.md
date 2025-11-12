# Python Retry + Backoff — Resilience Pattern

**Purpose:** Prevent transient API errors from breaking workflows by adding exponential backoff with jitter.

---

## 1. Decorator Implementation

```python
import random, time, functools

def retry_with_backoff(retries=3, base_delay=0.5, factor=4, jitter=True):
    """Decorator: Retries a function with exponential backoff and optional jitter."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == retries:
                        raise
                    sleep_time = delay * (factor ** (attempt - 1))
                    if jitter:
                        sleep_time += random.uniform(0, 0.3)
                    print(f"[retry_with_backoff] attempt {attempt} failed: {e}. Retrying in {sleep_time:.2f}s")
                    time.sleep(sleep_time)
            return None
        return wrapper
    return decorator
```

## 2. Usage Example

```python
from utils.retry import retry_with_backoff

@retry_with_backoff(retries=3, base_delay=0.5)
def call_api():
    # Simulated API request
    if random.random() < 0.7:
        raise Exception("API timeout")
    return "Success"

print(call_api())
```

## 3. Sequence Table

| Attempt | Delay (s) | Factor | Description |
|---------|-----------|--------|-------------|
| 1       | 0.5       | x1     | Initial try |
| 2       | 2.0       | x4     | 2nd attempt |
| 3       | 5.0       | x10    | Final retry |
| +jitter | ±0.3s     | —      | Adds randomness |

## 4. Integration with Router

Used when calling APIs or LLMs via router or local models:

```python
@retry_with_backoff(retries=3)
def generate_content(prompt):
    if should_offload(prompt):
        offload_to_gemini(prompt)
        return "Offloaded"
    else:
        return local_llm(prompt)
```

## 5. Benefits

✅ Handles temporary network/API instability
✅ Prevents cascading retries from overwhelming APIs
✅ Adds fairness with jitter
✅ Keeps code short and testable

## 6. Tests (pytest)

```python
from utils.retry import retry_with_backoff

def test_retry_success_after_failures(monkeypatch):
    calls = {"n": 0}
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("fail")
        return "ok"
    wrapped = retry_with_backoff(retries=3)(flaky)
    assert wrapped() == "ok"
```

## 7. Notes

- Default retry limit: 3 attempts (configurable)
- Combined with circuit breaker in CI
- Log messages routed via standard logger in production
- Keep retry decorators lightweight; avoid recursion
