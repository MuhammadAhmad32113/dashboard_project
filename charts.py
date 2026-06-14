mkdir -p /home/claude/dashboard_project && cat > /home/claude/dashboard_project/charts.py << 'PYEOF'
"""
charts.py  —  AEP Energy Dashboard
Libraries:
  - Plotly    : pie, histogram, line, bar, scatter, area, count, yearly (interactive + downloadable)
  - Seaborn   : heatmap, violin, box (statistical charts)
  - Matplotlib: backend for seaborn charts
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import plotly.graph_objects as go
from matplotlib.ticker import FuncFormatter

# ─────────────────────────────────────────────
#  COLOR PALETTE
# ─────────────────────────────────────────────
BG       = "#0d1c2d"
CARD_BG  = "#122131"
GRID     = "#1c2b3c"
TEXT     = "#d4e4fa"
TEXT_SUB = "#8899aa"
BLUE     = "#3b82f6"
EMERALD  = "#10b981"
AMBER    = "#f59e0b"
CORAL    = "#f87171"
VIOLET   = "#8b5cf6"
CYAN     = "#06b6d4"

SEASON_COLORS = {"Winter":BLUE,"Spring":EMERALD,"Summer":CORAL,"Autumn":AMBER}
MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
DAY_ORDER   = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

# ─────────────────────────────────────────────
#  PLOTLY DARK LAYOUT
# ─────────────────────────────────────────────
def _plotly_layout(fig, title):
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=CARD_BG,
        font=dict(color=TEXT, family="Inter, Segoe UI, sans-serif", size=12),
        title=dict(text=title, x=0, xanchor="left",
                   font=dict(color=TEXT, size=13)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
        xaxis=dict(gridcolor=GRID, linecolor=GRID,
                   tickfont=dict(color=TEXT_SUB)),
        yaxis=dict(gridcolor=GRID, linecolor=GRID,
                   tickfont=dict(color=TEXT_SUB)),
        margin=dict(l=50, r=20, t=50, b=50),
        hoverlabel=dict(bgcolor=CARD_BG, font_color=TEXT),
    )
    return fig

# ─────────────────────────────────────────────
#  SEABORN/MATPLOTLIB THEME
# ─────────────────────────────────────────────
sns.set_theme(style="darkgrid", rc={
    "axes.facecolor":BG, "figure.facecolor":BG,
    "grid.color":GRID, "grid.linewidth":0.5,
    "axes.edgecolor":GRID, "axes.labelcolor":TEXT_SUB,
    "xtick.color":TEXT_SUB, "ytick.color":TEXT_SUB,
    "text.color":TEXT, "axes.spines.top":False, "axes.spines.right":False,
})

def _mpl_title(ax, text):
    ax.set_title(text, fontsize=12, fontweight="600", color=TEXT, pad=14, loc="left")

def _mpl_labels(ax, xlabel="", ylabel=""):
    ax.set_xlabel(xlabel, fontsize=10, color=TEXT_SUB, labelpad=7)
    ax.set_ylabel(ylabel, fontsize=10, color=TEXT_SUB, labelpad=7)

def _mw(x, _): return f"{x/1000:.0f}k"

def _empty_plotly(msg="No data for selected filters."):
    fig = go.Figure()
    fig.add_annotation(text=msg, xref="paper", yref="paper",
                       x=0.5, y=0.5, showarrow=False,
                       font=dict(color=TEXT_SUB, size=13))
    return _plotly_layout(fig, "")

def _empty_mpl(msg="No data for selected filters."):
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(CARD_BG)
    ax.text(0.5, 0.5, msg, ha="center", va="center",
            fontsize=11, color=TEXT_SUB, transform=ax.transAxes)
    ax.axis("off")
    return fig


# 1. PIE — Plotly
def chart_pie(df):
    if df.empty: return _empty_plotly()
    data = df.groupby("Season")["AEP_MW"].sum().reset_index()
    colors = [SEASON_COLORS.get(s, BLUE) for s in data["Season"]]
    fig = go.Figure(go.Pie(
        labels=data["Season"], values=data["AEP_MW"], hole=0.35,
        marker=dict(colors=colors, line=dict(color=BG, width=3)),
        textinfo="label+percent", textfont=dict(color=TEXT, size=11),
    ))
    return _plotly_layout(fig, "Pie Chart: Energy Share by Season")


# 2. HISTOGRAM — Plotly
def chart_histogram(df):
    if df.empty: return _empty_plotly()
    mean_val = df["AEP_MW"].mean()
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df["AEP_MW"], nbinsx=55,
        marker_color=BLUE, opacity=0.85,
        marker_line=dict(color=BG, width=0.3), name="Frequency"))
    fig.add_vline(x=mean_val, line_dash="dash", line_color=AMBER, line_width=2,
                  annotation_text=f"Mean: {mean_val:,.0f} MW",
                  annotation_font_color=AMBER)
    _plotly_layout(fig, "Histogram: Hourly Consumption — Frequency Distribution")
    fig.update_xaxes(title_text="Energy (MW)")
    fig.update_yaxes(title_text="Frequency")
    return fig


# 3. LINE — Plotly
def chart_line(df):
    if df.empty: return _empty_plotly()
    monthly = df.groupby(["Year","Month"])["AEP_MW"].mean().reset_index()
    monthly["Period"] = pd.to_datetime(monthly[["Year","Month"]].assign(day=1))
    monthly.sort_values("Period", inplace=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["Period"], y=monthly["AEP_MW"], mode="lines",
        line=dict(color=BLUE, width=2),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.08)", name="Monthly Avg"))
    _plotly_layout(fig, "Line Chart: Monthly Average Energy Consumption")
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Avg MW")
    return fig


# 4. BAR — Plotly
def chart_bar(df):
    if df.empty: return _empty_plotly()
    hourly = df.groupby("Hour")["AEP_MW"].mean().reset_index()
    peak_h = hourly.loc[hourly["AEP_MW"].idxmax(), "Hour"]
    low_h  = hourly.loc[hourly["AEP_MW"].idxmin(), "Hour"]
    colors = [CORAL if h==peak_h else EMERALD if h==low_h else BLUE for h in hourly["Hour"]]
    fig = go.Figure(go.Bar(
        x=[f"{h:02d}:00" for h in hourly["Hour"]], y=hourly["AEP_MW"],
        marker=dict(color=colors, line=dict(color=BG, width=0.3)), name="Avg MW"))
    _plotly_layout(fig, "Bar Chart: Average Consumption by Hour of Day")
    fig.update_xaxes(title_text="Hour of Day")
    fig.update_yaxes(title_text="Avg MW")
    return fig


# 5. SCATTER — Plotly
def chart_scatter(df):
    if df.empty: return _empty_plotly()
    sample = df.sample(min(4000, len(df)), random_state=42)
    fig = go.Figure()
    for season in ["Winter","Spring","Summer","Autumn"]:
        grp = sample[sample["Season"]==season]
        if grp.empty: continue
        fig.add_trace(go.Scatter(
            x=grp["Hour"], y=grp["AEP_MW"], mode="markers",
            marker=dict(color=SEASON_COLORS[season], size=4, opacity=0.3),
            name=season))
    _plotly_layout(fig, "Scatter Plot: Hour of Day vs Energy — by Season")
    fig.update_xaxes(title_text="Hour of Day", dtick=2)
    fig.update_yaxes(title_text="Energy (MW)")
    return fig


# 6. BOX — Seaborn + Matplotlib
def chart_box(df):
    if df.empty: return _empty_mpl()
    df2 = df.copy()
    df2["MonthName"] = pd.Categorical(df2["MonthName"], categories=MONTH_ORDER, ordered=True)
    df2.sort_values("MonthName", inplace=True)
    fig, ax = plt.subplots(figsize=(10, 4.5))
    sns.boxplot(data=df2, x="MonthName", y="AEP_MW", color=BLUE, linewidth=1.0,
                medianprops=dict(color=AMBER, linewidth=2),
                whiskerprops=dict(color=TEXT_SUB), capprops=dict(color=TEXT_SUB),
                flierprops=dict(marker="o", markersize=2, alpha=0.25, color=TEXT_SUB),
                boxprops=dict(alpha=0.6), ax=ax)
    _mpl_title(ax, "Box Plot: Energy Distribution by Month")
    _mpl_labels(ax, "Month", "Energy (MW)")
    ax.yaxis.set_major_formatter(FuncFormatter(_mw))
    plt.tight_layout()
    return fig


# 7. HEATMAP — Seaborn + Matplotlib
def chart_heatmap(df):
    if df.empty or df["Month"].nunique() < 2: return _empty_mpl()
    pivot = df.pivot_table(values="AEP_MW", index="Hour", columns="Month", aggfunc="mean")
    pivot.columns = [MONTH_ORDER[c-1] for c in pivot.columns]
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "modern", ["#0f172a","#1e3a5f",BLUE,CYAN,EMERALD,AMBER,CORAL])
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.heatmap(pivot, ax=ax, cmap=cmap, linewidths=0.4, linecolor=BG,
                annot=False, cbar_kws={"label":"Avg MW","shrink":0.7})
    ax.set_facecolor(CARD_BG)
    fig.patch.set_facecolor(BG)
    _mpl_title(ax, "Heatmap: Avg Energy (MW) — Hour × Month")
    _mpl_labels(ax, "Month", "Hour of Day")
    ax.tick_params(colors=TEXT_SUB, labelsize=9)
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.label.set_color(TEXT_SUB)
    cbar.ax.tick_params(colors=TEXT_SUB)
    plt.tight_layout()
    return fig


# 8. AREA — Plotly
def chart_area(df):
    if df.empty: return _empty_plotly()
    daily = df.groupby("Date")["AEP_MW"].mean().reset_index()
    daily["Date"]  = pd.to_datetime(daily["Date"])
    daily.sort_values("Date", inplace=True)
    daily["Roll7"]  = daily["AEP_MW"].rolling(7,  min_periods=1).mean()
    daily["Roll30"] = daily["AEP_MW"].rolling(30, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily["Date"], y=daily["AEP_MW"],
        fill="tozeroy", fillcolor="rgba(6,182,212,0.07)",
        line=dict(color=CYAN, width=0.6), opacity=0.5, name="Daily Avg"))
    fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Roll7"],
        line=dict(color=AMBER, width=2), name="7-Day Avg"))
    fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Roll30"],
        line=dict(color=VIOLET, width=2.5, dash="dash"), name="30-Day Avg"))
    _plotly_layout(fig, "Area Chart: Daily Consumption with Rolling Averages")
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Energy (MW)")
    return fig


# 9. COUNT PLOT — Plotly
def chart_count(df):
    if df.empty: return _empty_plotly()
    df2 = df.copy()
    df2["DayName"] = pd.Categorical(df2["DayName"], categories=DAY_ORDER, ordered=True)
    counts = df2["DayName"].value_counts().reindex(DAY_ORDER).reset_index()
    counts.columns = ["Day","Count"]
    colors = [VIOLET if d in {"Sat","Sun"} else BLUE for d in counts["Day"]]
    fig = go.Figure(go.Bar(x=counts["Day"], y=counts["Count"],
        marker=dict(color=colors, line=dict(color=BG, width=0.3)), name="Records"))
    _plotly_layout(fig, "Count Plot: Record Count by Day of Week")
    fig.update_xaxes(title_text="Day")
    fig.update_yaxes(title_text="Number of Records")
    return fig


# 10. VIOLIN — Seaborn + Matplotlib
def chart_violin(df):
    if df.empty: return _empty_mpl()
    season_order = [s for s in ["Winter","Spring","Summer","Autumn"]
                    if s in df["Season"].unique()]
    palette = {s: SEASON_COLORS[s] for s in season_order}
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.violinplot(data=df, x="Season", y="AEP_MW", order=season_order,
                   palette=palette, hue="Season", legend=False,
                   inner="box", linewidth=1.0, alpha=0.75, cut=0, ax=ax)
    _mpl_title(ax, "Violin Plot: Energy Distribution by Season")
    _mpl_labels(ax, "Season", "Energy (MW)")
    ax.yaxis.set_major_formatter(FuncFormatter(_mw))
    plt.tight_layout()
    return fig


# BONUS — YEARLY — Plotly
def chart_yearly_avg(df):
    if df.empty: return _empty_plotly()
    yearly = df.groupby("Year")["AEP_MW"].mean().reset_index()
    peak_y = yearly.loc[yearly["AEP_MW"].idxmax(), "Year"]
    low_y  = yearly.loc[yearly["AEP_MW"].idxmin(), "Year"]
    colors = [CORAL if y==peak_y else EMERALD if y==low_y else BLUE for y in yearly["Year"]]
    fig = go.Figure(go.Bar(
        x=yearly["Year"].astype(str), y=yearly["AEP_MW"],
        marker=dict(color=colors, line=dict(color=BG, width=0.3)),
        text=[f"{v:,.0f}" for v in yearly["AEP_MW"]],
        textposition="outside", textfont=dict(color=TEXT_SUB, size=9),
        name="Avg MW"))
    _plotly_layout(fig, "Bar Chart (Bonus): Average Annual Energy Consumption")
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text="Avg MW")
    return fig
