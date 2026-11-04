# Data providers & provenance (Russia-first; global transfer test)

## Sources to fetch, not to assume

| Family | Direct owner / URL | Use | Gaps / rights |
|---|---|---|---|
| MOEX ISS | https://www.moex.com/a2920 and https://iss.moex.com/iss/ | daily trade history, candles, board metadata, index families MCFTR/RGBITR/RUCBITR | historical window, calendar/board and license; index not security |
| MOEX indexes | https://www.moex.com/ru/index/ | index methodology, changes and rebalancing | TR vs price, bonds accrued interest |
| Bank of Russia | https://www.cbr.ru/hd_base/KeyRate/ ; https://www.cbr.ru/ | key rate, official FX, rates, reporting | quote vs investable return, day count and lags |
| Simulacre AI MCP | https://simulacre-ai.ru/site/ | available agent-side access layer for MOEX / CBR data | endpoint response schema, source timestamp, partial history, fail closed |
| RUONIA | https://www.cbr.ru/hd_base/ruonia/ | overnight risk-free proxy | annualized quote, not automatically fund NAV |
| MSCI | https://www.msci.com/indexes/group/minimum-volatility-indexes | global methodology / controlled external validation | licensing, constituent survivorship |
| Kenneth French | https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html | global factor evidence | factors ≠ direct investability |
| CRSP / WRDS | https://www.crsp.org/ ; https://wrds-www.wharton.upenn.edu/ | survivorship-aware US stocks | paid licenses, adjustments |

## Source acceptance checks

For each instrument, store: source URL/identifier, provider query/endpoint, raw fields & units, trading board, timezone, `as_of`, `retrieved_at`, `first_last_observed`, count, stale days, missing fraction, checksum, dividend/coupon treatment, corporate action basis, licensing and trading restrictions. If the owner makes revisions, preserve immutable `dataset_snapshot` with a known cutoff.

**Index substitution is a new experiment**: a shorter-duration corporate bond index replacing broad bonds changes the economic exposure. Never concatenate these into a purported same underlying.

**Historical data only if actual fetch succeeded.** Confirm external rows against source of record; an MCP tool being available does not prove each endpoint's response is complete, current or licensable.
