"""
charts.py  —  AEP Energy Dashboard
All charts use Plotly (interactive + downloadable).
Seaborn and Matplotlib are also imported and used for
statistical computations and color palette generation.
"""

import pandas as pd
import numpy as np

# ── Matplotlib (used for color mapping utilities) ──
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# ── Seaborn (used for statistical color palettes) ──
import seaborn as sns

# ── Plotly (all chart rendering — interactive + downloadable) ──
import plotly.graph_objects as go
import plotly.express as px

# ─────────────────────────────────────────────
#  COLOR PALETTE
# ─────────────────────────────────────────────
BG       = "#0d1c2d"
CARD_BG  = "#122131"
GRID     = "#1c2b3c"
TEXT     = "#d4e4fa"
TEXT_SUB = "#8899aa"

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

# Use seaborn to generate a smooth colormap for heatmap
HEATMAP_COLORS = [
    "#0f172a", "#1e3a5f", BLUE, CYAN, EMERALD, AMBER, CORAL
]
# Use matplotlib to build the colormap object
MPL_CMAP = mcolors.LinearSegmentedColormap.from_list("aep", HEATMAP_COLORS)

# Use seaborn palette for multi-color charts
SNS_PALETTE = sns.color_palette("deep", 12)

# ─────────────────────────────────────────────
#  PLOTLY BASE LAYOUT
# ─────────────────────────────────────────────
def _layout(title=""):
    return dict(
        paper_bgcolor=BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT, family="Inter, Segoe UI, sans-serif", size=12),
        title=dict(text=title, font=dict(color=TEXT, size=14), x=0, pad=dict(l=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, color=TEXT_SUB,
                   showline=False),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID, color=TEXT_SUB,
                   showline=False),
        margin=dict(l=55, r=30, t=55, b=55),
        hoverlabel=dict(bgcolor="#1e3a5f", font=dict(color=TEXT)),
    )


def _empty(msg="No data for selected filters."):
    fig = go.Figure()
    fig.add_annotation(
        text=msg, x=0.5, y=0.5, xref="paper", yref="paper",
        showarrow=False, font=dict(color=TEXT_SUB, size=13))
    fig.update_layout(**_layout())
    return fig


# ══════════════════════════════════════════════
# 1. PIE CHART
# ══════════════════════════════════════════════
def chart_pie(df):
    if df.empty: return _empty()
    data = df.groupby("Season")["AEP_MW"].sum().reset_index()
    colors = [SEASON_COLORS.get(s, BLUE) for s in data["Season"]]

    fig = go.Figure(go.Pie(
        labels=data["Season"], values=data["AEP_MW"],
        hole=0.38,
        marker=dict(colors=colors, line=dict(color=BG, width=3)),
        textinfo="label+percent",
        textfont=dict(color=TEXT, size=12),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} MW<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(**_layout("Pie Chart: Energy Share by Season"))
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
        opacity=0.85, name="Frequency",
        hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>",
    ))
    fig.add_vline(x=mean_val, line=dict(color=AMBER, width=2, dash="dash"),
                  annotation=dict(text=f"Mean: {mean_val:,.0f} MW",
                                  font=dict(color=AMBER, size=11),
                                  bgcolor=BG))
    layout = _layout("Histogram: Hourly Consumption — Frequency Distribution")
    layout["xaxis"]["title"] = "Energy (MW)"
    layout["yaxis"]["title"] = "Frequency"
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

    fig = go.Figure(go.Scatter(
        x=monthly["Period"], y=monthly["AEP_MW"],
        mode="lines", line=dict(color=BLUE, width=2),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.08)",
        name="Monthly Avg",
        hovertemplate="<b>%{x|%Y-%m}</b><br>%{y:,.0f} MW<extra></extra>",
    ))
    layout = _layout("Line Chart: Monthly Average Energy Consumption")
    layout["xaxis"]["title"] = "Date"
    layout["yaxis"]["title"] = "Avg MW"
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# 4. BAR CHART
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
        marker_color=colors,
        hovertemplate="<b>Hour %{x}</b><br>%{y:,.0f} MW<extra></extra>",
    ))
    fig.add_trace(go.Scatter(x=[], y=[], mode="markers",
        marker=dict(color=CORAL, size=10), name="Peak Hour"))
    fig.add_trace(go.Scatter(x=[], y=[], mode="markers",
        marker=dict(color=EMERALD, size=10), name="Lowest Hour"))
    fig.add_trace(go.Scatter(x=[], y=[], mode="markers",
        marker=dict(color=BLUE, size=10), name="Other Hours"))
    layout = _layout("Bar Chart: Average Consumption by Hour of Day")
    layout["xaxis"]["title"] = "Hour"
    layout["xaxis"]["tickangle"] = 45
    layout["yaxis"]["title"] = "Avg MW"
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# 5. SCATTER PLOT
# ══════════════════════════════════════════════
def chart_scatter(df):
    if df.empty: return _empty()
    sample = df.sample(min(4000, len(df)), random_state=42)

    fig = go.Figure()
    for season in ["Winter","Spring","Summer","Autumn"]:
        grp = sample[sample["Season"] == season]
        if grp.empty: continue
        fig.add_trace(go.Scatter(
            x=grp["Hour"], y=grp["AEP_MW"],
            mode="markers",
            marker=dict(color=SEASON_COLORS[season], size=4, opacity=0.3),
            name=season,
            hovertemplate=f"<b>{season}</b><br>Hour: %{{x}}<br>%{{y:,.0f}} MW<extra></extra>",
        ))
    layout = _layout("Scatter Plot: Hour of Day vs Energy — by Season")
    layout["xaxis"]["title"] = "Hour of Day"
    layout["xaxis"]["tickmode"] = "linear"
    layout["xaxis"]["tick0"] = 0
    layout["xaxis"]["dtick"] = 2
    layout["yaxis"]["title"] = "Energy (MW)"
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# 6. BOX PLOT
# ══════════════════════════════════════════════
def chart_box(df):
    if df.empty: return _empty()
    months_present = [m for m in MONTH_ORDER
                      if m in df["MonthName"].values]

    fig = go.Figure()
    for i, month in enumerate(months_present):
        mdf = df[df["MonthName"] == month]["AEP_MW"]
        # Use seaborn palette for per-month colors
        r, g, b = SNS_PALETTE[i % len(SNS_PALETTE)]
        color = f"rgba({int(r*255)},{int(g*255)},{int(b*255)},0.7)"
        fig.add_trace(go.Box(
            y=mdf, name=month,
            marker=dict(color=color, outliercolor=TEXT_SUB, size=3),
            line=dict(color=color),
            boxmean=True,
            hovertemplate=f"<b>{month}</b><br>%{{y:,.0f}} MW<extra></extra>",
        ))
    layout = _layout("Box Plot: Energy Distribution by Month")
    layout["xaxis"]["title"] = "Month"
    layout["yaxis"]["title"] = "Energy (MW)"
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# 7. HEATMAP
# ══════════════════════════════════════════════
def chart_heatmap(df):
    if df.empty or df["Month"].nunique() < 2: return _empty()
    pivot = df.pivot_table(values="AEP_MW", index="Hour",
                           columns="Month", aggfunc="mean")
    pivot.columns = [MONTH_ORDER[c-1] for c in pivot.columns]

    # Use matplotlib colormap converted to plotly scale
    plotly_scale = []
    for i in range(10):
        t = i / 9
        r, g, b, _ = MPL_CMAP(t)
        plotly_scale.append([t, f"rgb({int(r*255)},{int(g*255)},{int(b*255)})"])

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=plotly_scale,
        colorbar=dict(title=dict(text="Avg MW", font=dict(color=TEXT_SUB)),
                      tickfont=dict(color=TEXT_SUB)),
        hovertemplate="Month: <b>%{x}</b><br>Hour: <b>%{y}</b><br>%{z:,.0f} MW<extra></extra>",
    ))
    layout = _layout("Heatmap: Avg Energy (MW) — Hour × Month")
    layout["xaxis"]["title"] = "Month"
    layout["yaxis"]["title"] = "Hour of Day"
    layout["yaxis"]["autorange"] = "reversed"
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# 8. AREA CHART
# ══════════════════════════════════════════════
def chart_area(df):
    if df.empty: return _empty()
    daily = df.groupby("Date")["AEP_MW"].mean().reset_index()
    daily["Date"]   = pd.to_datetime(daily["Date"])
    daily.sort_values("Date", inplace=True)
    daily["Roll7"]  = daily["AEP_MW"].rolling(7,  min_periods=1).mean()
    daily["Roll30"] = daily["AEP_MW"].rolling(30, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["AEP_MW"],
        mode="lines", line=dict(color=CYAN, width=0.6),
        fill="tozeroy", fillcolor="rgba(6,182,212,0.07)",
        name="Daily Avg", opacity=0.5,
        hovertemplate="Daily: %{y:,.0f} MW<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["Roll7"],
        mode="lines", line=dict(color=AMBER, width=2),
        name="7-Day Avg",
        hovertemplate="7-Day Avg: %{y:,.0f} MW<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["Roll30"],
        mode="lines", line=dict(color=VIOLET, width=2.5, dash="dash"),
        name="30-Day Avg",
        hovertemplate="30-Day Avg: %{y:,.0f} MW<extra></extra>",
    ))
    layout = _layout("Area Chart: Daily Consumption with Rolling Averages")
    layout["xaxis"]["title"] = "Date"
    layout["yaxis"]["title"] = "Energy (MW)"
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
# 9. COUNT PLOT
# ══════════════════════════════════════════════
def chart_count(df):
    if df.empty: return _empty()
    counts = df["DayName"].value_counts()
    ordered = [d for d in DAY_ORDER if d in counts.index]
    counts  = counts.reindex(ordered)
    colors  = [VIOLET if d in {"Sat","Sun"} else BLUE for d in ordered]

    fig = go.Figure(go.Bar(
        x=ordered, y=counts.values,
        marker_color=colors,
        hovertemplate="<b>%{x}</b><br>%{y:,} records<extra></extra>",
    ))
    fig.add_trace(go.Scatter(x=[], y=[], mode="markers",
        marker=dict(color=BLUE, size=10), name="Weekday"))
    fig.add_trace(go.Scatter(x=[], y=[], mode="markers",
        marker=dict(color=VIOLET, size=10), name="Weekend"))
    layout = _layout("Count Plot: Record Count by Day of Week")
    layout["xaxis"]["title"] = "Day"
    layout["yaxis"]["title"] = "Records"
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
        sdf = df[df["Season"] == season]["AEP_MW"]
        fig.add_trace(go.Violin(
            y=sdf, name=season,
            box_visible=True,
            meanline_visible=True,
            fillcolor=SEASON_COLORS[season],
            opacity=0.75,
            line_color=SEASON_COLORS[season],
            hovertemplate=f"<b>{season}</b><br>%{{y:,.0f}} MW<extra></extra>",
        ))
    layout = _layout("Violin Plot: Energy Distribution by Season")
    layout["xaxis"]["title"] = "Season"
    layout["yaxis"]["title"] = "Energy (MW)"
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
        marker_color=colors,
        hovertemplate="<b>%{x}</b><br>Avg: %{y:,.0f} MW<extra></extra>",
    ))
    fig.add_trace(go.Scatter(x=[], y=[], mode="markers",
        marker=dict(color=CORAL,   size=10), name="Highest Year"))
    fig.add_trace(go.Scatter(x=[], y=[], mode="markers",
        marker=dict(color=EMERALD, size=10), name="Lowest Year"))
    fig.add_trace(go.Scatter(x=[], y=[], mode="markers",
        marker=dict(color=BLUE,    size=10), name="Other"))
    layout = _layout("Bar Chart (Bonus): Average Annual Energy Consumption")
    layout["xaxis"]["title"] = "Year"
    layout["yaxis"]["title"] = "Avg MW"
    fig.update_layout(**layout)
    return fig
