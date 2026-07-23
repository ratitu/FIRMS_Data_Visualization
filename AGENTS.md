# AGENTS.md

## What this is

Streamlit app for visualizing NASA FIRMS fire data. Single-package Python project, no build system, no tests, no linting config.

## Run

```bash
pip install -r requirements.txt
streamlit run main.py
```

Requires a FIRMS MAP_KEY for online mode. Set via `export FIRMS_MAP_KEY="..."` or enter in the UI sidebar.

## Structure

- `main.py` — Streamlit entry point, orchestrates sidebar/rendering
- `config.py` — constants (API URLs, defaults, source lists)
- `data.py` — FIRMS API calls + local CSV loading; uses `@st.cache_data` with 1h TTL
- `ui.py` — sidebar form rendering, session state init
- `visualization.py` — Plotly charts (map, line, bar) and shields.io badge helpers
- `modis/` — local data directory (CSVs gitignored except `modis_empty.csv` placeholder)

## Gotchas

- No linter, formatter, typechecker, or test suite exists. Don't assume one.
- `modis/` data files are large and gitignored. Local mode gracefully falls back to `modis_empty.csv` when files are missing.
- The `key` file (gitignored) may contain a MAP_KEY — never commit secrets.
- All API functions use Streamlit caching (`@st.cache_data`). Changes to data-fetching logic must account for cache invalidation.
- Country data has a fallback dict baked into `data.py` (~250 countries) used when the FIRMS API is unreachable.
