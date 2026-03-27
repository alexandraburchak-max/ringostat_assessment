"""Data processing utilities for the RevOps Streamlit dashboard."""

from __future__ import annotations

import re
from typing import Iterable, Optional

import numpy as np
import pandas as pd


EXPECTED_COLUMNS = [
    "deal_id",
    "created_date",
    "closing_date",
    "client_country",
    "client_crm",
    "source",
    "stage",
    "ppc_budget",
]


_ALIAS_TO_CANONICAL = {
    "deal_id": "deal_id",
    "id": "deal_id",
    "aql_date": "created_date",
    "created_date": "created_date",
    "created_at": "created_date",
    "closing_date": "closing_date",
    "close_date": "closing_date",
    "client_country": "client_country",
    "country": "client_country",
    "client_crm": "client_crm",
    "crm": "client_crm",
    "source": "source",
    "stage": "stage",
    "ppc_budget_usd": "ppc_budget",
    "ppc_budget": "ppc_budget",
    "budget": "ppc_budget",
}


def _normalize_col_name(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", str(name).strip().lower())
    return re.sub(r"_+", "_", cleaned).strip("_")


def parse_ppc_budget(value: object) -> Optional[float]:
    """Parse PPC budget values from scalar/range strings into numeric."""
    if pd.isna(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    text = text.replace("$", "").replace(",", "")
    if text.lower() in {"na", "n/a", "none", "null", "nan"}:
        return None

    if "-" in text:
        parts = text.split("-", 1)
        try:
            low, high = float(parts[0]), float(parts[1])
            return (low + high) / 2
        except ValueError:
            return None

    try:
        return float(text)
    except ValueError:
        return None


def standardize_columns(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Map source columns to canonical analytics columns."""
    df = raw_df.copy()
    rename_map: dict[str, str] = {}

    for col in df.columns:
        normalized = _normalize_col_name(col)
        if normalized in _ALIAS_TO_CANONICAL:
            canonical = _ALIAS_TO_CANONICAL[normalized]
            if canonical not in rename_map.values():
                rename_map[col] = canonical

    df = df.rename(columns=rename_map)

    if "deal_id" not in df.columns:
        df["deal_id"] = np.arange(1, len(df) + 1, dtype=int)

    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan

    for col in ["client_country", "client_crm", "source", "stage"]:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"": np.nan, "nan": np.nan, "None": np.nan})

    df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
    df["closing_date"] = pd.to_datetime(df["closing_date"], errors="coerce")

    df["ppc_budget_raw"] = df["ppc_budget"]
    df["ppc_budget"] = df["ppc_budget"].apply(parse_ppc_budget)

    return df


def apply_filters(
    df: pd.DataFrame,
    countries: Optional[Iterable[str]] = None,
    crms: Optional[Iterable[str]] = None,
    date_range: Optional[tuple[pd.Timestamp, pd.Timestamp]] = None,
    date_field: str = "created_date",
) -> pd.DataFrame:
    """Filter dataframe by country, CRM, and date range."""
    filtered = df.copy()

    if countries:
        filtered = filtered[filtered["client_country"].isin(countries)]

    if crms:
        filtered = filtered[filtered["client_crm"].isin(crms)]

    if date_range and date_field in filtered.columns:
        start_date, end_date = date_range
        date_series = pd.to_datetime(filtered[date_field], errors="coerce")
        filtered = filtered[(date_series >= start_date) & (date_series <= end_date)]

    return filtered


def closed_only(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["stage"].isin(["Closed Won", "Closed Lost"])].copy()


def win_rate_by_dimension(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Return win rate by a categorical dimension."""
    closed_df = closed_only(df)
    if closed_df.empty:
        return pd.DataFrame(columns=[dimension, "won", "total_closed", "win_rate"])

    agg = (
        closed_df.assign(is_won=closed_df["stage"].eq("Closed Won").astype(int))
        .groupby(dimension, dropna=False)
        .agg(won=("is_won", "sum"), total_closed=("is_won", "count"))
        .reset_index()
    )

    agg[dimension] = agg[dimension].fillna("Unknown")
    agg["win_rate"] = np.where(agg["total_closed"] > 0, agg["won"] / agg["total_closed"], np.nan)
    return agg.sort_values(["win_rate", "total_closed"], ascending=[False, False])


def stage_distribution(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.assign(stage=df["stage"].fillna("Unknown"))
        .groupby("stage", dropna=False)
        .size()
        .reset_index(name="deal_count")
        .sort_values("deal_count", ascending=False)
    )


def source_distribution(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.assign(source=df["source"].fillna("Unknown"))
        .groupby("source", dropna=False)
        .size()
        .reset_index(name="deal_count")
        .sort_values("deal_count", ascending=False)
    )


def win_rate_vs_ppc(df: pd.DataFrame) -> pd.DataFrame:
    closed_df = closed_only(df).copy()
    if closed_df.empty:
        return pd.DataFrame(columns=["ppc_bucket", "avg_budget", "win_rate", "closed_deals"])

    labels = ["0", "1-500", "501-1000", "1001-2000", "2001-5000", "5000+"]
    bins = [-0.1, 0, 500, 1000, 2000, 5000, np.inf]
    closed_df["ppc_bucket"] = pd.cut(closed_df["ppc_budget"], bins=bins, labels=labels)
    closed_df["ppc_bucket"] = closed_df["ppc_bucket"].astype(str).replace("nan", "Unknown")
    closed_df["is_won"] = closed_df["stage"].eq("Closed Won").astype(int)

    agg = (
        closed_df.groupby("ppc_bucket", dropna=False)
        .agg(
            avg_budget=("ppc_budget", "mean"),
            win_rate=("is_won", "mean"),
            closed_deals=("is_won", "count"),
        )
        .reset_index()
    )
    return agg.sort_values("avg_budget", na_position="last")


def data_issues(df: pd.DataFrame) -> pd.DataFrame:
    """Run data quality validations and return issue rows."""
    issues_frames: list[pd.DataFrame] = []

    closed_without_date = df[df["stage"].isin(["Closed Won", "Closed Lost"]) & df["closing_date"].isna()]
    if not closed_without_date.empty:
        chunk = closed_without_date.copy()
        chunk["issue_type"] = "Closed stage without closing date"
        issues_frames.append(chunk)

    missing_country = df[df["client_country"].isna()]
    if not missing_country.empty:
        chunk = missing_country.copy()
        chunk["issue_type"] = "Missing client country"
        issues_frames.append(chunk)

    missing_crm = df[df["client_crm"].isna() | df["client_crm"].str.lower().eq("no crm")]
    if not missing_crm.empty:
        chunk = missing_crm.copy()
        chunk["issue_type"] = "Missing CRM"
        issues_frames.append(chunk)

    non_positive_budget = df[df["ppc_budget"].notna() & (df["ppc_budget"] <= 0)]
    if not non_positive_budget.empty:
        chunk = non_positive_budget.copy()
        chunk["issue_type"] = "Negative or zero PPC budget"
        issues_frames.append(chunk)

    duplicates = df[df["deal_id"].duplicated(keep=False)]
    if not duplicates.empty:
        chunk = duplicates.copy()
        chunk["issue_type"] = "Duplicate deal_id"
        issues_frames.append(chunk)

    if not issues_frames:
        return pd.DataFrame(columns=["issue_type", *df.columns.tolist()])

    issues_df = pd.concat(issues_frames, ignore_index=True)
    display_cols = [
        "issue_type",
        "deal_id",
        "created_date",
        "closing_date",
        "client_country",
        "client_crm",
        "source",
        "stage",
        "ppc_budget_raw",
        "ppc_budget",
    ]
    available = [col for col in display_cols if col in issues_df.columns]
    return issues_df[available]


def kpi_snapshot(df: pd.DataFrame) -> dict[str, float]:
    closed_df = closed_only(df)
    won_count = int((closed_df["stage"] == "Closed Won").sum())
    lost_count = int((closed_df["stage"] == "Closed Lost").sum())
    total_closed = won_count + lost_count
    win_rate = won_count / total_closed if total_closed else 0.0

    return {
        "total_deals": int(len(df)),
        "closed_deals": int(total_closed),
        "won_deals": won_count,
        "win_rate": float(win_rate),
        "avg_ppc_budget": float(df["ppc_budget"].mean()) if df["ppc_budget"].notna().any() else 0.0,
    }


def generate_revops_summary(df: pd.DataFrame) -> str:
    """Generate a 5-7 sentence analytical summary from filtered data."""
    if df.empty:
        return (
            "The selected filters returned no deals, so performance trends cannot be evaluated. "
            "Broaden country, CRM, or date filters to restore enough volume for reliable RevOps insights."
        )

    kpi = kpi_snapshot(df)
    stage_df = stage_distribution(df)
    source_df = source_distribution(df)
    country_df = win_rate_by_dimension(df, "client_country")
    crm_df = win_rate_by_dimension(df, "client_crm")

    open_stages = stage_df[~stage_df["stage"].isin(["Closed Won", "Closed Lost"])]
    bottleneck = (
        open_stages.iloc[0]["stage"]
        if not open_stages.empty
        else "No open-stage bottleneck (most deals are already closed)"
    )

    best_country = country_df[country_df["total_closed"] >= 5].head(1)
    weak_country = country_df[country_df["total_closed"] >= 5].tail(1)
    best_crm = crm_df[crm_df["total_closed"] >= 5].head(1)
    weak_crm = crm_df[crm_df["total_closed"] >= 5].tail(1)
    top_source = source_df.head(1)

    sentence_1 = (
        f"The dataset contains {kpi['total_deals']} deals, with {kpi['closed_deals']} closed outcomes "
        f"and an overall win rate of {kpi['win_rate']:.1%}."
    )
    sentence_2 = (
        f"Pipeline volume is concentrated in the '{stage_df.iloc[0]['stage']}' stage "
        f"({int(stage_df.iloc[0]['deal_count'])} deals), while '{bottleneck}' is the largest active bottleneck."
    )
    sentence_3 = (
        f"The largest acquisition source is '{top_source.iloc[0]['source']}' "
        f"with {int(top_source.iloc[0]['deal_count'])} deals."
        if not top_source.empty
        else "Source distribution is too sparse to identify a leading acquisition channel."
    )
    sentence_4 = (
        f"Country performance is strongest in {best_country.iloc[0]['client_country']} "
        f"({best_country.iloc[0]['win_rate']:.1%} win rate) and weakest in "
        f"{weak_country.iloc[0]['client_country']} ({weak_country.iloc[0]['win_rate']:.1%})."
        if not best_country.empty and not weak_country.empty
        else "There are not enough closed deals per country to compare geography performance reliably."
    )
    sentence_5 = (
        f"Across CRM systems, {best_crm.iloc[0]['client_crm']} currently converts best "
        f"({best_crm.iloc[0]['win_rate']:.1%}), while {weak_crm.iloc[0]['client_crm']} underperforms "
        f"({weak_crm.iloc[0]['win_rate']:.1%})."
        if not best_crm.empty and not weak_crm.empty
        else "CRM-level conversion trends are directional only because closed volumes are limited in some systems."
    )
    sentence_6 = (
        "Recommended actions: prioritize enablement for low-converting countries/CRMs, "
        "audit qualification quality in early stages, and reallocate PPC spend toward segments "
        "with above-average closed-win conversion."
    )

    return " ".join([sentence_1, sentence_2, sentence_3, sentence_4, sentence_5, sentence_6])
