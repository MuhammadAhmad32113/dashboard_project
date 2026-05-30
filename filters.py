"""
filters.py
----------
All data loading, cleaning, and filtering logic for the AEP Energy Dashboard.
"""

import pandas as pd
import numpy as np


# ──────────────────────────────────────────────
# 1. LOAD & CLEAN
# ──────────────────────────────────────────────

def load_and_clean(filepath: str = "data/AEP_hourly.csv") -> pd.DataFrame:
    """
    Load the AEP_hourly dataset, parse datetimes, engineer
    all derived time features, and return a clean DataFrame.
    """
    df = pd.read_csv(filepath)

    # Parse datetime
    df["Datetime"] = pd.to_datetime(df["Datetime"])

    # Drop duplicates and nulls
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)

    # Sort chronologically
    df.sort_values("Datetime", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # ── Derived time features ──────────────────
    df["Year"]        = df["Datetime"].dt.year
    df["Month"]       = df["Datetime"].dt.month
    df["MonthName"]   = df["Datetime"].dt.strftime("%b")
    df["Day"]         = df["Datetime"].dt.day
    df["Hour"]        = df["Datetime"].dt.hour
    df["DayOfWeek"]   = df["Datetime"].dt.dayofweek          # 0 = Mon
    df["DayName"]     = df["Datetime"].dt.strftime("%a")
    df["WeekOfYear"]  = df["Datetime"].dt.isocalendar().week.astype(int)
    df["Quarter"]     = df["Datetime"].dt.quarter
    df["IsWeekend"]   = df["DayOfWeek"].isin([5, 6])

    # Season
    df["Season"] = df["Month"].map({
        12: "Winter", 1: "Winter", 2: "Winter",
        3:  "Spring", 4: "Spring", 5: "Spring",
        6:  "Summer", 7: "Summer", 8: "Summer",
        9:  "Autumn", 10: "Autumn", 11: "Autumn",
    })

    # Time of day
    def _tod(h):
        if 5 <= h < 12:  return "Morning"
        if 12 <= h < 17: return "Afternoon"
        if 17 <= h < 21: return "Evening"
        return "Night"

    df["TimeOfDay"] = df["Hour"].apply(_tod)

    # Daily average (used in area / line charts)
    daily = df.groupby(df["Datetime"].dt.date)["AEP_MW"].mean()
    df["Date"]       = df["Datetime"].dt.date
    df["DailyAvg"]   = df["Date"].map(daily)

    return df


# ──────────────────────────────────────────────
# 2. FILTER ENGINE
# ──────────────────────────────────────────────

def apply_filters(
    df: pd.DataFrame,
    year_range:    tuple  = None,
    seasons:       list   = None,
    months:        list   = None,
    mw_range:      tuple  = None,
    day_types:     list   = None,
    keyword:       str    = "",
) -> pd.DataFrame:
    """
    Apply all dashboard filters to the DataFrame and return the result.

    Parameters
    ----------
    df          : full cleaned DataFrame
    year_range  : (min_year, max_year)  inclusive
    seasons     : list of season strings, e.g. ['Summer', 'Winter']
    months      : list of month numbers 1-12
    mw_range    : (min_mw, max_mw)
    day_types   : ['Weekday', 'Weekend'] — either/both
    keyword     : text to search in Datetime string representation
    """
    filtered = df.copy()

    # Date / Year range
    if year_range:
        filtered = filtered[
            (filtered["Year"] >= year_range[0]) &
            (filtered["Year"] <= year_range[1])
        ]

    # Season (category filter)
    if seasons:
        filtered = filtered[filtered["Season"].isin(seasons)]

    # Month multi-select
    if months:
        filtered = filtered[filtered["Month"].isin(months)]

    # MW numerical range slider
    if mw_range:
        filtered = filtered[
            (filtered["AEP_MW"] >= mw_range[0]) &
            (filtered["AEP_MW"] <= mw_range[1])
        ]

    # Day type (Weekday / Weekend)
    if day_types:
        if "Weekday" in day_types and "Weekend" not in day_types:
            filtered = filtered[~filtered["IsWeekend"]]
        elif "Weekend" in day_types and "Weekday" not in day_types:
            filtered = filtered[filtered["IsWeekend"]]

    # Keyword / text search on Datetime
    if keyword and keyword.strip():
        kw = keyword.strip().lower()
        filtered = filtered[
            filtered["Datetime"].astype(str).str.lower().str.contains(kw, na=False)
        ]

    return filtered


# ──────────────────────────────────────────────
# 3. KPI HELPERS
# ──────────────────────────────────────────────

def compute_kpis(df: pd.DataFrame) -> dict:
    """Return a dict of KPI values for the summary cards."""
    if df.empty:
        return {k: "N/A" for k in
                ["total_records", "mean_mw", "max_mw", "min_mw",
                 "peak_hour", "peak_date", "std_mw", "years_covered"]}

    peak_idx  = df["AEP_MW"].idxmax()
    trough_idx = df["AEP_MW"].idxmin()

    return {
        "total_records":  f"{len(df):,}",
        "mean_mw":        f"{df['AEP_MW'].mean():,.1f} MW",
        "max_mw":         f"{df['AEP_MW'].max():,.0f} MW",
        "min_mw":         f"{df['AEP_MW'].min():,.0f} MW",
        "peak_date":      str(df.loc[peak_idx, "Datetime"])[:13] + ":00",
        "trough_date":    str(df.loc[trough_idx, "Datetime"])[:13] + ":00",
        "std_mw":         f"{df['AEP_MW'].std():,.1f} MW",
        "years_covered":  f"{df['Year'].min()} – {df['Year'].max()}",
    }
