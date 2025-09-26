# Macro Dashboard Engine

A composable engine that fetches macro data (FRED, NMDB), stores it in a SQLite database with period-aware metadata, and renders reusable components (overview table, spread charts).

## Key Ideas
- SQLite with ORM models preserving:
  - `frequency` (D,W,M,Q,A)
  - `is_periodic` (period vs instant values)
  - `period_start` and `period_end` per observation
- Data loaders upsert latest values; revisions overwrite the same `period_start` row and track `as_of`.
- Chart functions do no processing. A query service returns SeriesPayloads with `x`, `y`, and `line_shape` (e.g., `hv` for quarterly series).
- Imperative composition via a small factory that creates table + spread components by alias.

## CLI
- Build and update everything locally:
  - `macro-dashboard`

Artifacts are written to `output/` and the DB to `data/macro_dashboard.db`.

## GitHub Actions
A workflow runs on a schedule to update the DB and commit it back to the repo. Configure `FRED_API_KEY` as a repository secret.

## Extending
- Add new series in `src/macro_dashboard/config/settings.py`.
- Register new components in `src/macro_dashboard/charts/components/` using `@register_component`.
- Use the query service to prepare payloads with frequency/period semantics.

