# AI Usage Report

## 1) AI tools used

- Codex (GPT-5 based coding agent in terminal mode) for implementation and particular documentation generation.

## 2) Most effective prompts

- "Analyze data from csv and complete tasks from architecture.md."
- Follow-up decomposition into concrete deliverables:
  - Streamlit dashboard with requested KPIs/charts/filters
  - Data quality checks table
  - Dynamic RevOps insights summary
  - Required project documentation files

## 3) AI-generated vs manual work

- AI-generated:
  - `app.py` Streamlit UI and charting logic
  - `src/data_processing.py` data standardization, metrics, validations, insight generation
  - `requirements.txt`, `sample_data_schema.md`, and `README.md` draft
  - This AI usage report
- Manual decisions:
  - Developing the architecture.md file for the agentic-development
  - Mapping source CSV headers to canonical schema
  - Choosing practical assumptions when `deal_id` is absent in source data
  - Reviewing and refining naming, modular boundaries, and UX flow

## 4) Challenges and resolutions

- Challenge: runtime environment lacked installed analytics dependencies (`pandas`, `streamlit`, etc.).
  - Resolution: generated reproducible install/run instructions in `README.md` and `requirements.txt`.
- Challenge: source dataset used non-canonical headers (for example `AQL date`, `Client CRM`, `PPC budget USD`).
  - Resolution: implemented a robust alias-mapping and normalization layer.
- Challenge: `deal_id` was not present in source file.
  - Resolution: generated synthetic sequential IDs to keep duplicate-ID validation operational.
