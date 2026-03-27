# RevOps Deals Analytics (Streamlit)

Production-ready analytical solution for CRM deals data with:
- interactive Streamlit dashboard
- data quality validation table
- dynamic RevOps insights summary

## Project Structure

- `app.py` — Streamlit dashboard entrypoint
- `src/data_processing.py` — data normalization, KPI logic, validations, insights
- `sample_data_schema.md` — expected schema and supported aliases
- `requirements.txt` — Python dependencies
- `AI_Usage_Report.md` — AI usage documentation

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

## Data Input

By default, the app points to:

`test_data/Alexandra Byrchak _ Revenue Operations Specialist at Ringostat – копія - база угод.csv`

You can change the CSV path in the Streamlit sidebar.

## Implemented Requirements

### Dashboard

- Win rate by country
- Win rate by CRM
- Deal distribution by stage
- Number of deals by source
- Relationship between win rate and PPC budget
- Filters:
  - client country (multi-select)
  - client CRM (multi-select)
  - date range (created or closing date)

### Data Quality Checks (`Data Issues`)

- Closed Won/Closed Lost without closing date
- Missing client country
- Missing CRM
- Negative or zero PPC budget
- Duplicate deals by `deal_id`

### Bonus

- KPI cards (total, closed, win rate, avg PPC budget)
- Download button for filtered data

## Current Dataset Snapshot

Based on the provided CSV (895 rows):
- Closed Won: 216
- Closed Lost: 431
- Overall win rate (closed-only): 33.4%
- Most frequent stages: Closed Lost (431), Closed Won (216), Negotiations (158)
- Top sources by volume: Partner (274), Inbound call (187), Registration (124)
- Observed data issues: Missing CRM (366 rows), Non-positive PPC budget (85 rows)

## Notes

- If `deal_id` is missing in source data, the app creates a synthetic sequential ID for processing.
- PPC budget ranges like `500-1000` are converted to midpoint numeric values for trend analysis.
