# DataGuard Insights

A Streamlit BI dashboard built on top of [DataGuard Core](https://github.com/Lahiru1Niroosh/dataguard-core)'s
reconciliation engine — translating row-level data discrepancies into business-facing
metrics: dollar exposure, affected accounts, integrity trends over time, and a
data-driven executive summary written in plain language.

## Why this exists

DataGuard Core detects and classifies data discrepancies between a banking system and
its downstream reporting replica. That's useful to an engineer, but not to a business
stakeholder staring at a table of row IDs. This dashboard exists to answer the
question a non-technical audience actually asks: *"How bad is it, and who's affected?"*

## Pages

- **Home** — headline integrity gauge, latest-run KPIs, and full run history
- **Trends** — integrity % over time (with rolling average), dollar impact over time,
  and fault-type composition per run
- **Discrepancy Explorer** — filterable discrepancy detail table, dollar impact by
  fault type, and a "Top Accounts at Risk" panel ranked by cumulative exposure
- **Executive Summary** — a single auto-generated sentence describing the latest run
  ("This run flagged 80 discrepancies totaling $208,557.31 across 66 accounts..."),
  plus a health status badge

Every number on every page comes from a live SQL query against DataGuard Core's
`dataguard_meta` schema — nothing here is hardcoded or pre-computed.

## Architecture

- **Read-only by design.** This app connects to Postgres using a dedicated
  `dataguard_readonly` role with `SELECT`-only grants on `dataguard_meta`. It
  physically cannot write to, modify, or corrupt DataGuard Core's data, even if
  there's a bug in this codebase — a deliberate least-privilege decision, not an
  accident of configuration.
- **SQL window functions carry the analytical weight**, not application code:
  `RANK()` for top-accounts-by-impact, `LAG()` for month/day-over-day % change,
  `ROW_NUMBER()` for a stable, chronological run sequence (since the database's raw
  `run_id` is a sequence, not a timeline, and the two can diverge).
- **Visual design**: a deliberate "audit ledger" aesthetic — deep ink-navy
  background, serif headers, restrained teal/red/gold accent colors — built to look
  like a financial document a stakeholder would trust, not a generic dark-mode SaaS
  template.

## Tech stack

Streamlit · Plotly · SQLAlchemy · pandas · PostgreSQL

## Running locally

```bash
# 1. Make sure DataGuard Core's Postgres container is running
#    (see the dataguard-core repo for setup)

# 2. Set up this project
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt
copy .env.example .env           # fill in your read-only DB credentials

# 3. Run it
streamlit run app/Home.py
```

## Live demo

_Coming soon — deployment to Streamlit Community Cloud in progress._

## Companion project

[DataGuard Core](https://github.com/Lahiru1Niroosh/dataguard-core) is the underlying
reconciliation engine this dashboard visualizes: a hierarchical data integrity
platform achieving 100% precision/recall on labeled fault injection and a measured
2.3x–6.4x speedup over naive full-table comparison.