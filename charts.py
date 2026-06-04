"""
charts.py  —  AEP Energy Dashboard
Same colors + dark theme, now using Plotly for all charts.
Plotly gives a built-in toolbar with PNG/SVG download on every chart.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
#  PALETTE — unchanged from original
# ─────────────────────────────────────────────
BG        = "#0d1c2d"
CARD_BG   = "#122131"
GRID      = "#1c2b3c"
TEXT      = "#d4e4fa"
TEXT_SUB  = "#8899aa"

BLUE    = "#3b82f6"
EMERALD = "#10b981"
AMBER   = "#f59e0b"
CORAL   = "#f87171"
VIOLET  = "#8b5cf6"
CYAN    = "#06b6d4"

SEASON_COLORS = {
    "Winter": BLUE,
    "Spring": EMERALD,
    "Summer": CORAL,
    "Autumn": AMBER,
}

MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]
DAY_ORDER   = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]


# ─────────────────────────────────────────────
#  SHARED LAYOUT HELPER
# ─────────────────────────────────────────────
def _base_layout(title="", xaxis_title="", yaxis_title="",
                 height=420, margin=None):
    if margin is None:
        margin = dict(l=55, r=20, t=50, b=50)
    return dict(
        title=dict(text=f"<b>{title}</b>", font=dict(size=13, color=TEXT), x=0.01),
        paper_bgcolor=BG,
        plot_bgcolor=CARD_BG,
        font=dict(family="Inter, Segoe UI, sans-serif", color=TEXT_SUB),
        height=height,
        margin=margin,
        xaxis=dict(
            title=xaxis_title,
            gridcolor=GRID, gridwidth=0.5,
            linecolor=GRID, tickfont=dict(color=TEXT_SUB),
            title_font=dict(color=TEXT_SUB),
        ),
        yaxis=dict(
            title=yaxis_title,
            gridcolor=GRID, gridwidth=0.5,
            linecolor=GRID, tickfont=dict(color=TEXT_SUB),
            title_font=dict(color=TEXT_SUB),
        ),
        legend=dict(
            bgcolor=CARD_BG, bordercolor=GRID, borderwidth=1,
            font=dict(color=TEXT, size=10),
        ),
        hoverlabel=dict(bgcolor="#1e3a5f", font_color=TEXT),
    )

def _mw_fmt(val):
    return f"{val/1000:.1f}k MW"

def _empty(msg="No data for selected filters."):
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, showarrow=False,
                       font=dict(size=13, color=TEXT_SUB),
                       xref="paper", yref="paper")
    fig.update_layout(**_base_layout())
    return fig


# ══════════════════════════════════════════════
# 1. PIE CHART
# ══════════════════════════════════════════════
def chart_pie(df):
    if df.empty: return _empty()
    data = df.groupby("Season")["AEP_MW"].sum().reset_index()
    colors = [SEASON_COLORS.get(s, BLUE) for s in data["Season"]]

    fig = go.Figure(go.Pie(
        labels=data["Season"],
        values=data["AEP_MW"],
        marker=dict(colors=colors, line=dict(color=BG, width=3)),
        textinfo="percent",
        textfont=dict(size=11, color="white"),
        hole=0,
        hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>",
    ))
    layout = _base_layout("Energy Share by Season", height=420)
    layout["legend"] = dict(
        orientation="h", yanchor="bottom", y=-0.08, xanchor="center", x=0.5,
        bgcolor=CARD_BG, bordercolor=GRID, borderwidth=1,
        font=dict(color=TEXT, size=10),
    )
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# 2. HISTOGRAM
# ══════════════════════════════════════════════
def chart_histogram(df):
    if df.empty: return _empty()
    mean_val = df["AEP_MW"].mean()

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df["AEP_MW"], nbinsx=55,
        marker=dict(color=BLUE, line=dict(color=BG, width=0.3)),
        opacity=0.85,
        name="Frequency",
        hovertemplate="Energy: %{x:.0f} MW<br>Count: %{y}<extra></extra>",
    ))
    fig.add_vline(x=mean_val, line=dict(color=AMBER, width=2, dash="dash"),
                  annotation_text=f"Mean  {mean_val:,.0f} MW",
                  annotation_font=dict(color=AMBER, size=10),
                  annotation_position="top right")
    layout = _base_layout("Hourly Consumption — Frequency Distribution",
                          "Energy (MW)", "Frequency", height=420)
    layout["xaxis"]["tickformat"] = ".0s"
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# 3. LINE CHART
# ══════════════════════════════════════════════
def chart_line(df):
    if df.empty: return _empty()
    monthly = df.groupby(["Year","Month"])["AEP_MW"].mean().reset_index()
    monthly["Period"] = pd.to_datetime(monthly[["Year","Month"]].assign(day=1))
    monthly.sort_values("Period", inplace=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["Period"], y=monthly["AEP_MW"],
        mode="lines",
        line=dict(color=BLUE, width=2),
        fill="tozeroy", fillcolor=f"rgba(59,130,246,0.08)",
        name="Avg MW",
        hovertemplate="%{x|%b %Y}: %{y:,.0f} MW<extra></extra>",
    ))
    layout = _base_layout("Monthly Average Energy Consumption",
                          "Date", "Avg MW", height=420)
    layout["yaxis"]["tickformat"] = ".2s"
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# 4. BAR CHART — hourly
# ══════════════════════════════════════════════
def chart_bar(df):
    if df.empty: return _empty()
    hourly = df.groupby("Hour")["AEP_MW"].mean().reset_index()
    peak_h = hourly.loc[hourly["AEP_MW"].idxmax(), "Hour"]
    low_h  = hourly.loc[hourly["AEP_MW"].idxmin(), "Hour"]
    colors = [CORAL if h == peak_h else EMERALD if h == low_h else BLUE
              for h in hourly["Hour"]]

    fig = go.Figure(go.Bar(
        x=[f"{h:02d}:00" for h in hourly["Hour"]],
        y=hourly["AEP_MW"],
        marker=dict(color=colors, line=dict(color=BG, width=0.3)),
        hovertemplate="Hour %{x}: %{y:,.0f} MW<extra></extra>",
        name="",
    ))
    # legend items
    for label, color in [("Peak Hour", CORAL), ("Lowest Hour", EMERALD), ("Other", BLUE)]:
        fig.add_trace(go.Bar(x=[None], y=[None], marker_color=color, name=label,
                             showlegend=True))
    layout = _base_layout("Average Consumption by Hour of Day",
                          "Hour", "Avg MW", height=420)
    layout["yaxis"]["tickformat"] = ".2s"
    layout["xaxis"]["tickangle"] = -45
    layout["barmode"] = "overlay"
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# 5. SCATTER PLOT
# ══════════════════════════════════════════════
def chart_scatter(df):
    if df.empty: return _empty()
    sample = df.sample(min(4000, len(df)), random_state=42)

    fig = go.Figure()
    for season in ["Winter", "Spring", "Summer", "Autumn"]:
        sub = sample[sample["Season"] == season]
        if sub.empty: continue
        fig.add_trace(go.Scatter(
            x=sub["Hour"], y=sub["AEP_MW"],
            mode="markers",
            marker=dict(color=SEASON_COLORS[season], size=4, opacity=0.25),
            name=season,
            hovertemplate=f"<b>{season}</b><br>Hour: %{{x}}<br>%{{y:,.0f}} MW<extra></extra>",
        ))
    layout = _base_layout("Hour of Day vs Energy — by Season",
                          "Hour of Day", "Energy (MW)", height=420)
    layout["yaxis"]["tickformat"] = ".2s"
    layout["xaxis"]["dtick"] = 2
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# 6. BOX PLOT
# ══════════════════════════════════════════════
def chart_box(df):
    if df.empty: return _empty()
    df2 = df.copy()
    df2["MonthName"] = pd.Categorical(df2["MonthName"],
                                       categories=MONTH_ORDER, ordered=True)
    df2.sort_values("MonthName", inplace=True)

    fig = go.Figure()
    for month in MONTH_ORDER:
        sub = df2[df2["MonthName"] == month]
        if sub.empty: continue
        fig.add_trace(go.Box(
            y=sub["AEP_MW"], name=month,
            marker=dict(color=BLUE, size=2, opacity=0.3),
            line=dict(color=AMBER, width=1.5),
            fillcolor="rgba(59,130,246,0.5)",
            boxpoints="outliers",
            showlegend=False,
            hovertemplate=f"<b>{month}</b><br>%{{y:,.0f}} MW<extra></extra>",
        ))
    layout = _base_layout("Energy Distribution by Month — Box Plot",
                          "Month", "Energy (MW)", height=420)
    layout["yaxis"]["tickformat"] = ".2s"
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# 7. HEATMAP
# ══════════════════════════════════════════════
def chart_heatmap(df):
    if df.empty or df["Month"].nunique() < 2: return _empty()
    pivot = df.pivot_table(values="AEP_MW", index="Hour",
                           columns="Month", aggfunc="mean")
    month_labels = [MONTH_ORDER[c-1] for c in pivot.columns]

    colorscale = [
        [0.0,  "#0f172a"], [0.2,  "#1e3a5f"],
        [0.4,  BLUE],      [0.55, CYAN],
        [0.7,  EMERALD],   [0.85, AMBER],
        [1.0,  CORAL],
    ]
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=month_labels,
        y=pivot.index,
        colorscale=colorscale,
        colorbar=dict(
            title=dict(text="Avg MW", font=dict(color=TEXT_SUB)),
            tickfont=dict(color=TEXT_SUB),
        ),
        hovertemplate="Hour: %{y}<br>Month: %{x}<br>%{z:,.0f} MW<extra></extra>",
    ))
    layout = _base_layout("Avg Energy (MW) — Hour × Month",
                          "Month", "Hour of Day", height=480,
                          margin=dict(l=55, r=80, t=50, b=50))
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# 8. AREA CHART  — rolling averages
# ══════════════════════════════════════════════
def chart_area(df):
    if df.empty: return _empty()
    daily = df.groupby("Date")["AEP_MW"].mean().reset_index()
    daily["Date"]   = pd.to_datetime(daily["Date"])
    daily.sort_values("Date", inplace=True)
    daily["Roll7"]  = daily["AEP_MW"].rolling(7,  min_periods=1).mean()
    daily["Roll30"] = daily["AEP_MW"].rolling(30, min_periods=1).mean()

    fig = go.Figure()
    # shaded area (daily)
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["AEP_MW"],
        mode="lines", line=dict(color=CYAN, width=0.6),
        fill="tozeroy", fillcolor="rgba(6,182,212,0.07)",
        name="Daily Avg", opacity=0.45,
        hovertemplate="%{x|%Y-%m-%d}: %{y:,.0f} MW<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["Roll7"],
        mode="lines", line=dict(color=AMBER, width=2),
        name="7-Day Avg",
        hovertemplate="7d avg %{x|%Y-%m-%d}: %{y:,.0f} MW<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["Roll30"],
        mode="lines", line=dict(color=VIOLET, width=2.5, dash="dash"),
        name="30-Day Avg",
        hovertemplate="30d avg %{x|%Y-%m-%d}: %{y:,.0f} MW<extra></extra>",
    ))
    layout = _base_layout("Daily Consumption with Rolling Averages",
                          "Date", "Energy (MW)", height=420)
    layout["yaxis"]["tickformat"] = ".2s"
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# 9. COUNT PLOT — by day of week
# ══════════════════════════════════════════════
def chart_count(df):
    if df.empty: return _empty()
    df2 = df.copy()
    df2["DayName"] = pd.Categorical(df2["DayName"],
                                     categories=DAY_ORDER, ordered=True)
    counts = df2.groupby("DayName", observed=True).size().reindex(DAY_ORDER).fillna(0)
    colors = [VIOLET if d in {"Sat","Sun"} else BLUE for d in DAY_ORDER]

    fig = go.Figure(go.Bar(
        x=list(counts.index), y=counts.values,
        marker=dict(color=colors, line=dict(color=BG, width=0.3)),
        hovertemplate="<b>%{x}</b>: %{y:,} records<extra></extra>",
        name="",
    ))
    for label, color in [("Weekday", BLUE), ("Weekend", VIOLET)]:
        fig.add_trace(go.Bar(x=[None], y=[None], marker_color=color,
                             name=label, showlegend=True))
    layout = _base_layout("Record Count by Day of Week",
                          "Day", "Records", height=420)
    layout["barmode"] = "overlay"
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# 10. VIOLIN PLOT
# ══════════════════════════════════════════════
def chart_violin(df):
    if df.empty: return _empty()
    season_order = [s for s in ["Winter","Spring","Summer","Autumn"]
                    if s in df["Season"].unique()]

    fig = go.Figure()
    for season in season_order:
        sub = df[df["Season"] == season]
        fig.add_trace(go.Violin(
            y=sub["AEP_MW"], name=season,
            fillcolor=SEASON_COLORS[season],
            line=dict(color=SEASON_COLORS[season], width=1),
            opacity=0.75,
            box_visible=True,
            meanline_visible=True,
            hoverinfo="y+name",
        ))
    layout = _base_layout("Energy Distribution by Season",
                          "Season", "Energy (MW)", height=420)
    layout["yaxis"]["tickformat"] = ".2s"
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# BONUS — YEAR-OVER-YEAR BAR
# ══════════════════════════════════════════════
def chart_yearly_avg(df):
    if df.empty: return _empty()
    yearly = df.groupby("Year")["AEP_MW"].mean().reset_index()
    peak_y = yearly.loc[yearly["AEP_MW"].idxmax(), "Year"]
    low_y  = yearly.loc[yearly["AEP_MW"].idxmin(), "Year"]
    colors = [CORAL if y == peak_y else EMERALD if y == low_y else BLUE
              for y in yearly["Year"]]

    fig = go.Figure(go.Bar(
        x=yearly["Year"].astype(str), y=yearly["AEP_MW"],
        marker=dict(color=colors, line=dict(color=BG, width=0.3)),
        hovertemplate="<b>%{x}</b>: %{y:,.0f} MW<extra></extra>",
        name="",
    ))
    for label, color in [("Highest Year", CORAL), ("Lowest Year", EMERALD), ("Other", BLUE)]:
        fig.add_trace(go.Bar(x=[None], y=[None], marker_color=color,
                             name=label, showlegend=True))
    layout = _base_layout("Average Annual Energy Consumption",
                          "Year", "Avg MW", height=420)
    layout["yaxis"]["tickformat"] = ".2s"
    layout["xaxis"]["tickangle"] = -45
    layout["barmode"] = "overlay"
    fig.update_layout(**layout)
    return fig
