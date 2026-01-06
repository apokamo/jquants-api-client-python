# ClientV2 Core Design

## Scope

Behavior that is shared across endpoints:
config resolution, request/retry, pagination, DataFrame shaping, rate limiting, and range helpers.

## Source of truth

- Implementation: `jquants/client_v2.py`, `jquants/exceptions.py`, `jquants/pacer.py`
- Design rationale (Reference): Issues #9, #12, #15

## API key & config resolution

Resolved in this priority (later wins):

1. Colab config (implicit)
2. User default config (implicit): `${HOME}/.jquants-api/jquants-api.toml`
3. CWD config (implicit): `jquants-api.toml`
4. Explicit config file (fail-fast): `JQUANTS_API_CLIENT_CONFIG_FILE`
5. Environment variable (overrides even if empty): `JQUANTS_API_KEY`
6. Constructor arg (highest): `ClientV2(api_key=...)`

TOML schema:

```toml
[jquants-api-client]
api_key = "your_api_key"
```

## Rate limiting (Pacer)

- `ClientV2(rate_limit=..., max_workers=...)` controls pacing and parallel fetch behavior.
- **Pacer Behavior:** Enforces a minimum interval between requests based on `rate_limit` (requests per minute).
  - Formula: `interval = 60.0 / rate_limit`
  - Defaults: `rate_limit=5` (Free plan), `max_workers=1` (Sequential).
- Pacing is enforced via `Pacer.wait()` before every request, including 429 retries.

## Request / retry / errors

### Transient Errors (5xx)
- Uses `requests.Session` + `urllib3.Retry`.
- **Strategy:** 3 retries for status codes `[500, 502, 503, 504]`.
- **Backoff:** `backoff_factor=0.5`.
- **Allowed Methods:** `["HEAD", "GET", "OPTIONS"]` (POST is excluded to prevent side effects).

### Rate Limit Errors (429)
- Handled via custom logic in `ClientV2._request()`.
- **Parameters:**
  - `retry_on_429`: bool (Default: `True`)
  - `retry_wait_seconds`: int (Default: `310`)
  - `retry_max_attempts`: int (Default: `3`)
- **Wait Policy:** Uses `time.sleep(retry_wait_seconds)` between attempts.

### Exceptions
All custom exceptions inherit from `jquants.exceptions.JQuantsAPIError`.

| Exception | HTTP Status | Description |
| :--- | :--- | :--- |
| `JQuantsForbiddenError` | 403 | Invalid API key, plan limit, or invalid path. |
| `JQuantsRateLimitError` | 429 | Rate limit exceeded after exhausted retries. |
| `JQuantsAPIError` | Other/None | Other API errors or client-side contract violations (e.g., pagination loop). |

**Note:** Network-layer exceptions (`requests.Timeout`, `requests.ConnectionError`) are NOT wrapped.

## DataFrame contract

Endpoints generally follow this pattern:

- `*_raw()` (or equivalent internal call): fetch JSON and handle pagination.
- Public `get_*()`: return a DataFrame, typed/ordered, and consistently sorted.
- `*_range()`: date-range helper with optional parallelization (max workers controlled by `max_workers`).

Column lists in `constants_v2.py` are treated as a recommended order; missing columns in the response are tolerated.

## Range helpers

Some endpoints have an accompanying `*_range()` helper that fetches per-day data and concatenates it.

Examples in this codebase:

- `ClientV2.get_price_range()` (equities daily quotes)
- `ClientV2.get_summary_range()` (financials summary)
- `ClientV2.get_options_225_daily_range()` (derivatives options 225 daily)

Common contract:

- Inputs accept `YYYY-MM-DD` strings, `date`, or `datetime` and are normalized via `_normalize_date()`.
- Date strings are treated as `YYYY-MM-DD` (not `YYYYMMDD`); invalid formats raise `ValueError` during date-range generation.
- The date range is inclusive and validated (`start_dt` must not be after `end_dt`).
- Fetch strategy depends on `ClientV2.max_workers`:
  - `max_workers == 1`: sequential (default, safest)
  - `max_workers > 1`: parallel via `ThreadPoolExecutor` under Pacer control
- Results are concatenated and re-sorted using the endpoint’s natural sort keys.
- If there is no data across the requested dates, return an empty `DataFrame` with the expected column set.
