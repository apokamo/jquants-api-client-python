# ClientV2 Design (V2)

## Scope

Design notes for `jquants.ClientV2` (V2 API client). This is for contributors/agents working on the library.

## When to read

- Before adding/changing endpoints or DataFrame shaping logic.
- Before changing request/response error handling, retry, pagination, or rate limiting.

## Source of truth

- **Implementation:** `jquants/*.py` (The code itself)
- **Design Docs:** `docs/design/v2/**` (This directory)
- **Reference (Read-only):** Closed Issues (for historical context/rationale only)
  - Core/auth/config: Issue #9
  - Infra/Retry/Pacer: Issues #12, #15
  - Endpoint designs: #17 (Equities), #19 (Markets), #20 (Indices), #21 (Financials), #25 (Derivatives)

## Index

### Core
- `docs/design/v2/core.md`: Auth, config, retry, pagination, DataFrame rules, and range helpers.

### Equities (`/v2/equities/*`)
- `docs/design/v2/endpoints/equities/master.md`: Listed info (`get_listed_info`)
- `docs/design/v2/endpoints/equities/bars_daily.md`: Daily quotes (`get_prices_daily_quotes`)
- `docs/design/v2/endpoints/equities/earnings_calendar.md`: Earnings calendar (`get_fins_announcement`)

### Markets (`/v2/markets/*`)
- `docs/design/v2/endpoints/markets/calendar.md`: Trading calendar (`get_markets_trading_calendar`)
- `docs/design/v2/endpoints/markets/margin_interest.md`: Weekly margin interest (`get_markets_trades_spec`)
- `docs/design/v2/endpoints/markets/short_ratio.md`: Short selling ratio (`get_markets_short_ratio`)
- `docs/design/v2/endpoints/markets/breakdown.md`: Transaction breakdown (`get_markets_breakdown`)
- `docs/design/v2/endpoints/markets/short_sale_report.md`: Short sale balance (`get_markets_short_sale_positions`)

### Indices (`/v2/indices/*`)
- `docs/design/v2/endpoints/indices/bars_daily.md`: Index prices (`get_indices_topix_daily_quotes` etc.)
- `docs/design/v2/endpoints/indices/bars_daily_topix.md`: TOPIX prices (deprecated path, same schema)

### Financials (`/v2/fins/*`)
- `docs/design/v2/endpoints/financials/summary.md`: Financial statements (`get_fins_statements`)

### Derivatives (`/v2/derivatives/*`)
- `docs/design/v2/endpoints/derivatives/options_225_daily.md`: Nikkei 225 Options (`get_options_225_daily`)

## Contribution Checklist

When adding or changing an endpoint:

1. [ ] **Update Implementation:**
   - Add method to `ClientV2` in `jquants/client_v2.py`.
   - Add columns to `jquants/constants_v2.py`.
2. [ ] **Create/Update Endpoint Doc:**
   - Create `docs/design/v2/endpoints/<category>/<name>.md`.
   - Include: Scope, When to read, API signature, DataFrame contract (Sort key + Major columns).
3. [ ] **Update Index:**
   - Add link to `docs/design/v2/README.md` (this file).
4. [ ] **Verify Core:**
   - If using `*_range()` helper, ensure it follows `docs/design/v2/core.md` patterns.
