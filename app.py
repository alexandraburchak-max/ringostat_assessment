from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_processing import (
    apply_filters,
    data_issues,
    generate_revops_summary,
    kpi_snapshot,
    source_distribution,
    stage_distribution,
    standardize_columns,
    win_rate_by_dimension,
    win_rate_vs_ppc,
)


st.set_page_config(page_title="RevOps Deals Dashboard", page_icon="📊", layout="wide")

DEFAULT_DATA_PATH = (
    Path(__file__).parent
    / "test_data"
    / "Alexandra Byrchak _ Revenue Operations Specialist at Ringostat – копія - база угод.csv"
)


@st.cache_data(show_spinner=False)
def load_data(file_path: str) -> pd.DataFrame:
    raw_df = pd.read_csv(file_path)
    return standardize_columns(raw_df)


def inject_ui_overrides() -> None:
    """Hide Streamlit header action buttons (Deploy / Share / Edit)."""
    st.markdown(
        """
        <style>
        /* Header action area */
        [data-testid="stHeaderActionElements"],
        [data-testid="stAppDeployButton"],
        .stAppDeployButton,
        button[title="Deploy this app"],
        button[title="Share this app"],
        button[title="Edit"],
        button[aria-label*="Deploy"],
        button[aria-label*="Share"],
        button[aria-label*="Edit"] {
            display: none !important;
            visibility: hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _plot_win_rate_bar(df: pd.DataFrame, dimension: str, title: str):
    if df.empty:
        st.info("No closed deals for this selection.")
        return
    fig = px.bar(
        df,
        x=dimension,
        y="win_rate",
        color="total_closed",
        text=df["win_rate"].map(lambda x: f"{x:.1%}"),
        labels={"win_rate": "Win rate", "total_closed": "Closed deals", dimension: dimension.replace("_", " ").title()},
        title=title,
    )
    fig.update_layout(yaxis_tickformat=".0%", xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)


def _plot_stage_distribution(df: pd.DataFrame):
    if df.empty:
        st.info("No data available for stage distribution.")
        return
    fig = px.bar(
        df,
        x="stage",
        y="deal_count",
        color="deal_count",
        title="Deal Distribution by Stage",
        labels={"deal_count": "Number of deals", "stage": "Stage"},
    )
    fig.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)


def _plot_source_distribution(df: pd.DataFrame):
    if df.empty:
        st.info("No data available for source distribution.")
        return
    fig = px.bar(
        df,
        x="source",
        y="deal_count",
        color="deal_count",
        title="Number of Deals by Source",
        labels={"deal_count": "Number of deals", "source": "Source"},
    )
    fig.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)


def _plot_win_rate_vs_ppc(df: pd.DataFrame):
    if df.empty:
        st.info("No closed deals available for PPC analysis.")
        return
    fig = px.scatter(
        df,
        x="avg_budget",
        y="win_rate",
        size="closed_deals",
        color="ppc_bucket",
        hover_data={"closed_deals": True, "avg_budget": ":.0f", "win_rate": ":.1%"},
        title="Relationship Between Win Rate and PPC Budget",
        labels={"avg_budget": "Average PPC budget (USD)", "win_rate": "Win rate"},
    )
    fig.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)


def main():
    inject_ui_overrides()
    st.title("RevOps Deals Dashboard")
    st.caption("Interactive performance dashboard with quality checks and auto-generated insights.")

    data_file = st.sidebar.text_input("CSV path", value=str(DEFAULT_DATA_PATH))

    if not Path(data_file).exists():
        st.error(f"Data file not found: {data_file}")
        st.stop()

    df = load_data(data_file)

    st.sidebar.header("Filters")
    countries = sorted(df["client_country"].dropna().unique().tolist())
    crms = sorted(df["client_crm"].dropna().unique().tolist())

    selected_countries = st.sidebar.multiselect("Client country", options=countries, default=countries)
    selected_crms = st.sidebar.multiselect("Client CRM", options=crms, default=crms)
    date_field = st.sidebar.selectbox(
        "Date field",
        options=["created_date", "closing_date"],
        format_func=lambda x: "Created Date" if x == "created_date" else "Closing Date",
    )

    date_series = pd.to_datetime(df[date_field], errors="coerce").dropna()
    if date_series.empty:
        min_date, max_date = pd.Timestamp("1970-01-01"), pd.Timestamp("1970-01-01")
    else:
        min_date, max_date = date_series.min(), date_series.max()
    selected_dates = st.sidebar.date_input(
        "Date range",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_ts, end_ts = pd.Timestamp(selected_dates[0]), pd.Timestamp(selected_dates[1])
    else:
        start_ts, end_ts = min_date, max_date

    filtered_df = apply_filters(
        df,
        countries=selected_countries,
        crms=selected_crms,
        date_range=(start_ts, end_ts),
        date_field=date_field,
    )

    kpi = kpi_snapshot(filtered_df)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total deals", f"{kpi['total_deals']:,}")
    c2.metric("Closed deals", f"{kpi['closed_deals']:,}")
    c3.metric("Win rate", f"{kpi['win_rate']:.1%}")
    c4.metric("Avg PPC budget", f"${kpi['avg_ppc_budget']:.0f}")

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Win Rate by Country")
        _plot_win_rate_bar(win_rate_by_dimension(filtered_df, "client_country"), "client_country", "Closed Win Rate by Country")
    with col_right:
        st.subheader("Win Rate by CRM")
        _plot_win_rate_bar(win_rate_by_dimension(filtered_df, "client_crm"), "client_crm", "Closed Win Rate by CRM")

    col_left, col_right = st.columns(2)
    with col_left:
        _plot_stage_distribution(stage_distribution(filtered_df))
    with col_right:
        _plot_source_distribution(source_distribution(filtered_df))

    st.subheader("Win Rate vs PPC Budget")
    _plot_win_rate_vs_ppc(win_rate_vs_ppc(filtered_df))

    st.subheader("Data Issues")
    issues_df = data_issues(filtered_df)
    st.dataframe(issues_df, use_container_width=True, height=320)

    st.subheader("RevOps Insights Summary")
    st.write(generate_revops_summary(filtered_df))

    csv_export = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered data",
        data=csv_export,
        file_name="filtered_deals.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
