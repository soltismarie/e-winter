# e-Winter

A prototype web app giving displaced and at-risk people in Ukraine a personalized winter safety risk assessment for their hromada (and, where available, their specific settlement), plus safer relocation recommendations — voiced by an AI guide persona, "Marusya" (Маруся). Bilingual: Ukrainian and English.

This is a private, unlisted repository kept for version history and authorship record. It is not published or distributed.

## Live prototype

The current build is published as a Claude Artifact (private, viewable only by the owner unless explicitly shared):
https://claude.ai/artifact/CoJYtgzYwmE7JnNgDFtkGN

## What's in this repo

- `welcome.html` — the entire client-side app: UI, styling, i18n (EN/UK translation dictionary + transliteration fallback), and all per-hromada/per-settlement risk data embedded directly in the page (no backend).
- `methodology.html` — a reference page documenting the four risk-score components (X1 attack risk, X2 outage risk, X3 front-line/border proximity, X4 logistics risk), their normalization, and sourcing.
- `hromada_combined_v1.csv` … `v6.csv` — successive versions of the core per-hromada dataset as each risk component was added/refined. `v6` is current.
- `oblast_clusters.json`, `cpi_by_oblast.json`, `schools_by_hromada.json`, `settlements_by_hromada.json`, `hromada_embedded.json` — derived datasets embedded into the app (oblast-level k-means clustering, CPI by oblast, school counts by hromada, settlement-to-hromada crosswalk).
- `documented_powerplant_damage.csv` — hand-curated list of documented power-infrastructure strikes feeding the X2 (outage risk) score.
- `hromada_frontline_distance.csv` — computed front-line distance per hromada (X3 input).
- `build_*.py`, `add_*.py`, `compute_*.py`, `assemble.py` — the data-processing pipeline that produces the combined dataset from raw sources.

## Data sources and licensing note

Several inputs are pulled from third-party sources and are **not** included in this repo (excluded via `.gitignore` due to size — see below):

- **KSE-Loc-Data-Hub** (Kyiv School of Economics, MIT license) — hromada attributes (population, OSBB counts, distance to EU/Russia-Belarus, etc.), the settlement-to-hromada crosswalk, and the EDEBO school registry.
- **cyterat/deepstate-map-data** (GitHub mirror of DeepState occupied-territory shapes, GPL-3.0, daily-updated) — used to compute front-line distance per hromada via point-to-polygon geometry.

The GPL-3.0 licensing on the DeepState-derived front-line-distance component needs to be resolved (licensing review / data-sharing agreement) before any commercial or government-scale deployment — flagged as an open item in the project roadmap.

Other sourced inputs (ACLED event data, Kaggle missile-attack data, LUN.ua rental prices, Ukrzaliznytsia/Ministry for Communities & Territories rail-strike reporting, hromada budget CPI series) are cited inline in the app and in `methodology.html`.

## Status

Working clickable prototype, not production software. Data marked "indicative" or "not yet connected" in the app is exactly that — this project avoids inventing figures it hasn't sourced.
