# Python Router — Core LLM Entry Point

**Purpose:** Provide a single, controlled interface for all AI/LLM calls, ensuring cost tracking, retry logic, and offload compliance.

---

## 1. Import Example

```python
from agents.checks.router import should_offload, offload_to_gemini
```

All generators, agents, or runners must call these functions instead of any direct SDK client.

## 2. Core Functions

**`should_offload(prompt: str, est_sec: int | None = None) -> bool`**

Estimates token count and decides if the task should offload to Gemini.

Returns `True` if:
- estimated tokens ≥ `MAX_TOKENS` (default: 12000)
- or estimated runtime ≥ `HEAVY_TIMEOUT_SEC` (default: 90s)

Returns `False` otherwise.

**`offload_to_gemini(prompt: str, model: str | None = None) -> str`**

Dispatches the prompt to the `offload_gemini.yml` workflow.

- Base64-encodes the prompt
- Generates unique `request_id`
- Calls GitHub Action using `gh workflow run`
- Writes proof into `docs/LAST_OFFLOAD.json`

## 3. Example Usage

```python
from agents.checks.router import should_offload, offload_to_gemini

def generate_script(prompt: str):
    if should_offload(prompt, est_sec=60):
        offload_to_gemini(prompt)
        return "Offloaded to Gemini — check docs/LAST_OFFLOAD.json"
    else:
        # lightweight local generation
        result = local_llm(prompt)
        return result
```

## 4. Design Philosophy

- **Safety**: No direct SDKs (OpenAI, Anthropic, Google) in main code.
- **Traceability**: Every offload logged in `docs/LAST_OFFLOAD.json`.
- **Auditability**: Guardrails block PRs missing router imports.
- **Scalability**: Routes heavy jobs to cloud actions, keeping runtime light.

## 5. Related Configs

**Environment variables / GitHub Vars:**

```
OFFLOAD_MODEL = gemini-1.5-pro-latest
MAX_TOKENS = 12000
HEAVY_TIMEOUT_SEC = 90
BUDGET_NZD_MONTHLY = 20
BUDGET_ALERT_NZD = 20
```

**Secrets:**

- `GEMINI_API_KEY`

## 6. Testing Checklist

- ☑ Trigger router with 3 sample prompts (light, medium, heavy)
- ☑ Confirm heavy prompt triggers workflow and prints "Offloaded to Gemini"
- ☑ Verify artifact `docs/LAST_OFFLOAD.json` updates
- ☑ Ensure guardrails workflow passes

## 7. Notes

- Heavy rule ensures cost ≤ NZD 20/mo.
- All token-heavy or slow tasks exit locally; nothing runs outside router.
- Router can be extended later for multi-model balancing or analytics.
