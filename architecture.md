You are a senior Data Analyst and Python developer specializing in RevOps analytics, Streamlit dashboards, and data quality validation.

Your task is to build a complete analytical solution based on a CRM deals dataset.

## GENERAL REQUIREMENTS

- Use Python
- Use Streamlit for the dashboard
- Use pandas, numpy, plotly (or altair) for data processing and visualization
- Code must be clean, modular, and production-ready
- Include comments and clear structure
- Assume dataset is in CSV format

---

## PART 1 — STREAMLIT DASHBOARD

Build a Streamlit dashboard that includes the following:

### Metrics & Visualizations:

1. Win rate by country
   - Win rate = Closed Won / (Closed Won + Closed Lost)

2. Win rate by CRM

3. Distribution of deals by Stage
   - Bar chart or funnel chart

4. Number of deals by Source
   - Bar chart

5. Relationship between win rate and PPC budget
   - Scatter plot or aggregated trend

---

### Filters (must be interactive in Streamlit):

- Client country (multi-select)
- Client CRM (multi-select)
- Date range (based on deal creation or closing date)

---

### UX Requirements:

- Clean layout (use columns, containers)
- Titles and descriptions for each chart
- Use caching for performance
- Handle missing values gracefully

---

## PART 2 — DATA QUALITY CHECKS

Implement validation logic and display results in a table called:

### "Data Issues"

Include at least these checks:

1. Stage is "Closed Won" or "Closed Lost" BUT Closing Date is NULL
2. Missing Client Country
3. Missing CRM
4. Negative or zero PPC budget (if applicable)
5. Duplicate deals (based on ID)

Display:

- Rows with issues
- Column indicating issue type

---

## PART 3 — REVOPS INSIGHTS SUMMARY

Generate a short analytical summary (5–7 sentences):

Include:

- What is performing well
- What is underperforming
- Bottlenecks in pipeline
- Trends across countries/CRM/source
- Actionable recommendations

This should be generated dynamically from the data if possible, otherwise provide a template with placeholders.

---

## PART 4 — AI USAGE DOCUMENTATION

Create a separate markdown file explaining:

1. Which AI tools were used (Codex, Cursor, etc.)
2. Which prompts were most effective
3. What parts were AI-generated vs manual
4. Challenges encountered and how they were solved

---

## OUTPUT REQUIREMENTS

Generate:

1. Full Streamlit app (`app.py`)
2. Sample data schema (expected columns)
3. Requirements.txt
4. README.md with:
   - Setup instructions
   - How to run Streamlit

5. Separate markdown file:
   - "AI_Usage_Report.md"

6. Optional:
   - Jupyter notebook for exploration

---

## DATA ASSUMPTIONS

Dataset should include columns like:

- deal_id
- client_country
- client_crm
- stage
- source
- ppc_budget
- created_date
- closing_date

---

## CODING STYLE

- Use functions for each chart
- Separate data processing layer from UI
- Use clear naming conventions
- Avoid hardcoding values
- Ensure scalability

---

## BONUS (if possible)

- Add KPI cards (total deals, win rate, revenue)
- Add download button for filtered data
- Add basic anomaly detection

---

Produce the full working solution with all files and code.
