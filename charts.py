"""
charts.py  —  AEP Energy Dashboard
Same colors + dark theme, now using Seaborn for all charts.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib.ticker import FuncFormatter

# ─────────────────────────────────────────────
#  SAME PALETTE — unchanged
# ─────────────────────────────────────────────
BG        = "#1e1e1e"
CARD_BG   = "#252525"
GRID      = "#2e2e2e"
TEXT      = "#e5e7eb"
TEXT_SUB  = "#9ca3af"

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
#  SEABORN GLOBAL THEME
# ─────────────────────────────────────────────
sns.set_theme(style="darkgrid", rc={
    "axes.facecolor":       CARD_BG,
    "figure.facecolor":     BG,
    "grid.color":           GRID,
    "grid.linewidth":       0.5,
    "axes.edgecolor":       GRID,
    "axes.labelcolor":      TEXT_SUB,
    "xtick.color":          TEXT_SUB,
    "ytick.color":          TEXT_SUB,
    "text.color":           TEXT,
    "axes.spines.top":      False,
    "axes.spines.right":    False,
})


def _title(ax, text):
    ax.set_title(text, fontsize=12, fontweight="600",
                 color=TEXT, pad=14, loc="left")

def _labels(ax, xlabel="", ylabel=""):
    ax.set_xlabel(xlabel, fontsize=10, color=TEXT_SUB, labelpad=7)
    ax.set_ylabel(ylabel, fontsize=10, color=TEXT_SUB, labelpad=7)

def _legend(ax):
    leg = ax.get_legend()
    if leg:
        leg.get_frame().set_facecolor("#2a2a2a")
        leg.get_frame().set_edgecolor(GRID)
        for t in leg.get_texts():
            t.set_color(TEXT)
        title = leg.get_title()
        if title:
            title.set_color(TEXT_SUB)

def _mw(x, _): return f"{x/1000:.0f}k"

def _empty(msg="No data for selected filters."):
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(CARD_BG)
    ax.text(0.5, 0.5, msg, ha="center", va="center",
            fontsize=11, color=TEXT_SUB, transform=ax.transAxes)
    ax.axis("off")
    return fig


# ══════════════════════════════════════════════
# 1. PIE CHART  (matplotlib — seaborn has no pie)
# ══════════════════════════════════════════════
def chart_pie(df):
    if df.empty: return _empty()
    data = df.groupby("Season")["AEP_MW"].sum()
    colors = [SEASON_COLORS.get(s) for s in data.index]

    fig, ax = plt.subplots(figsize=(6, 5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    wedges, _, autos = ax.pie(
        data, labels=None, autopct="%1.1f%%",
        startangle=140, colors=colors, pctdistance=0.75,
        wedgeprops=dict(edgecolor=BG, linewidth=3),
    )
    for a in autos:
        a.set_fontsize(10); a.set_fontweight("600"); a.set_color("white")
    ax.legend(data.index, loc="lower center", ncol=4, fontsize=9,
              framealpha=0, labelcolor=TEXT, bbox_to_anchor=(0.5, -0.05))
    _title(ax, "Energy Share by Season")
    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════
# 2. HISTOGRAM  — sns.histplot
# ══════════════════════════════════════════════
def chart_histogram(df):
    if df.empty: return _empty()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.histplot(data=df, x="AEP_MW", bins=55,
                 color=BLUE, edgecolor=BG, linewidth=0.3,
                 alpha=0.85, ax=ax)
    mean_val = df["AEP_MW"].mean()
    ax.axvline(mean_val, color=AMBER, linewidth=1.8,
               linestyle="--", label=f"Mean  {mean_val:,.0f} MW")
    ax.legend(fontsize=9); _legend(ax)
    _title(ax, "Hourly Consumption — Frequency Distribution")
    _labels(ax, "Energy (MW)", "Frequency")
    ax.xaxis.set_major_formatter(FuncFormatter(_mw))
    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════
# 3. LINE CHART  — sns.lineplot
# ══════════════════════════════════════════════
def chart_line(df):
    if df.empty: return _empty()
    monthly = df.groupby(["Year","Month"])["AEP_MW"].mean().reset_index()
    monthly["Period"] = pd.to_datetime(
        monthly[["Year","Month"]].assign(day=1))
    monthly.sort_values("Period", inplace=True)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    sns.lineplot(data=monthly, x="Period", y="AEP_MW",
                 color=BLUE, linewidth=1.8, ax=ax)
    ax.fill_between(monthly["Period"], monthly["AEP_MW"],
                    alpha=0.08, color=BLUE)
    _title(ax, "Monthly Average Energy Consumption")
    _labels(ax, "Date", "Avg MW")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.yaxis.set_major_formatter(FuncFormatter(_mw))
    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════
# 4. BAR CHART  — sns.barplot
# ══════════════════════════════════════════════
def chart_bar(df):
    if df.empty: return _empty()
    hourly = df.groupby("Hour")["AEP_MW"].mean().reset_index()
    hourly.columns = ["Hour","AEP_MW"]
    peak_h  = hourly.loc[hourly["AEP_MW"].idxmax(), "Hour"]
    low_h   = hourly.loc[hourly["AEP_MW"].idxmin(), "Hour"]
    colors  = [CORAL if h == peak_h
               else EMERALD if h == low_h
               else BLUE
               for h in hourly["Hour"]]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    sns.barplot(data=hourly, x="Hour", y="AEP_MW",
                hue="Hour", palette=dict(zip(hourly["Hour"], colors)),
                legend=False, edgecolor=BG, linewidth=0.3, ax=ax)
    ax.set_xticks(range(24))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(24)],
                       rotation=45, ha="right", fontsize=8)
    ax.legend(handles=[
        plt.Rectangle((0,0),1,1, color=CORAL,   label="Peak Hour"),
        plt.Rectangle((0,0),1,1, color=EMERALD, label="Lowest Hour"),
        plt.Rectangle((0,0),1,1, color=BLUE,    label="Other"),
    ], fontsize=9); _legend(ax)
    _title(ax, "Average Consumption by Hour of Day")
    _labels(ax, "Hour", "Avg MW")
    ax.yaxis.set_major_formatter(FuncFormatter(_mw))
    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════
# 5. SCATTER PLOT  — sns.scatterplot
# ══════════════════════════════════════════════
def chart_scatter(df):
    if df.empty: return _empty()
    sample = df.sample(min(4000, len(df)), random_state=42)
    palette = {s: SEASON_COLORS[s] for s in sample["Season"].unique()}

    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.scatterplot(data=sample, x="Hour", y="AEP_MW",
                    hue="Season", palette=palette,
                    alpha=0.22, s=10, ax=ax,
                    hue_order=[s for s in SEASON_COLORS if s in sample["Season"].unique()])
    _title(ax, "Hour of Day vs Energy — by Season")
    _labels(ax, "Hour of Day", "Energy (MW)")
    ax.set_xticks(range(0, 24, 2))
    ax.yaxis.set_major_formatter(FuncFormatter(_mw))
    ax.legend(title="Season", fontsize=9,
              title_fontsize=9, markerscale=2)
    _legend(ax)
    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════
# 6. BOX PLOT  — sns.boxplot
# ══════════════════════════════════════════════
def chart_box(df):
    if df.empty: return _empty()
    df2 = df.copy()
    df2["MonthName"] = pd.Categorical(
        df2["MonthName"], categories=MONTH_ORDER, ordered=True)
    df2.sort_values("MonthName", inplace=True)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    sns.boxplot(data=df2, x="MonthName", y="AEP_MW",
                color=BLUE, linewidth=1.0,
                medianprops=dict(color=AMBER, linewidth=2),
                whiskerprops=dict(color=TEXT_SUB),
                capprops=dict(color=TEXT_SUB),
                flierprops=dict(marker="o", markersize=2,
                                alpha=0.25, color=TEXT_SUB),
                boxprops=dict(alpha=0.6),
                ax=ax)
    _title(ax, "Energy Distribution by Month — Box Plot")
    _labels(ax, "Month", "Energy (MW)")
    ax.yaxis.set_major_formatter(FuncFormatter(_mw))
    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════
# 7. HEATMAP  — sns.heatmap
# ══════════════════════════════════════════════
def chart_heatmap(df):
    if df.empty or df["Month"].nunique() < 2: return _empty()
    pivot = df.pivot_table(values="AEP_MW", index="Hour",
                           columns="Month", aggfunc="mean")
    pivot.columns = [MONTH_ORDER[c-1] for c in pivot.columns]

    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "modern", ["#0f172a", "#1e3a5f", BLUE,
                   CYAN, EMERALD, AMBER, CORAL])
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.heatmap(pivot, ax=ax, cmap=cmap,
                linewidths=0.4, linecolor=BG, annot=False,
                cbar_kws={"label": "Avg MW", "shrink": 0.7})
    ax.set_facecolor(CARD_BG)
    fig.patch.set_facecolor(BG)
    _title(ax, "Avg Energy (MW) — Hour × Month")
    _labels(ax, "Month", "Hour of Day")
    ax.tick_params(colors=TEXT_SUB, labelsize=9)
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.label.set_color(TEXT_SUB)
    cbar.ax.tick_params(colors=TEXT_SUB)
    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════
# 8. AREA CHART  — sns.lineplot + fill
# ══════════════════════════════════════════════
def chart_area(df):
    if df.empty: return _empty()
    daily = df.groupby("Date")["AEP_MW"].mean().reset_index()
    daily["Date"]   = pd.to_datetime(daily["Date"])
    daily.sort_values("Date", inplace=True)
    daily["Roll7"]  = daily["AEP_MW"].rolling(7,  min_periods=1).mean()
    daily["Roll30"] = daily["AEP_MW"].rolling(30, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.fill_between(daily["Date"], daily["AEP_MW"],
                    alpha=0.07, color=CYAN)
    sns.lineplot(data=daily, x="Date", y="AEP_MW",
                 color=CYAN, linewidth=0.6, alpha=0.4,
                 label="Daily Avg", ax=ax)
    sns.lineplot(data=daily, x="Date", y="Roll7",
                 color=AMBER, linewidth=1.8,
                 label="7-Day Avg", ax=ax)
    sns.lineplot(data=daily, x="Date", y="Roll30",
                 color=VIOLET, linewidth=2.2,
                 linestyle="--", label="30-Day Avg", ax=ax)
    _title(ax, "Daily Consumption with Rolling Averages")
    _labels(ax, "Date", "Energy (MW)")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.yaxis.set_major_formatter(FuncFormatter(_mw))
    ax.legend(fontsize=9); _legend(ax)
    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════
# 9. COUNT PLOT  — sns.countplot
# ══════════════════════════════════════════════
def chart_count(df):
    if df.empty: return _empty()
    df2 = df.copy()
    df2["DayName"] = pd.Categorical(
        df2["DayName"], categories=DAY_ORDER, ordered=True)
    day_palette = {d: VIOLET if d in {"Sat","Sun"} else BLUE
                   for d in DAY_ORDER}

    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.countplot(data=df2, x="DayName", order=DAY_ORDER,
                  hue="DayName", palette=day_palette, legend=False,
                  edgecolor=BG, linewidth=0.3, ax=ax)
    ax.legend(handles=[
        plt.Rectangle((0,0),1,1, color=BLUE,   label="Weekday"),
        plt.Rectangle((0,0),1,1, color=VIOLET, label="Weekend"),
    ], fontsize=9); _legend(ax)
    _title(ax, "Record Count by Day of Week")
    _labels(ax, "Day", "Records")
    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════
# 10. VIOLIN PLOT  — sns.violinplot
# ══════════════════════════════════════════════
def chart_violin(df):
    if df.empty: return _empty()
    season_order = [s for s in ["Winter","Spring","Summer","Autumn"]
                    if s in df["Season"].unique()]
    palette = {s: SEASON_COLORS[s] for s in season_order}

    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.violinplot(data=df, x="Season", y="AEP_MW",
                   order=season_order, palette=palette,
                   hue="Season", legend=False,
                   inner="box", linewidth=1.0,
                   alpha=0.75, cut=0, ax=ax)
    _title(ax, "Energy Distribution by Season")
    _labels(ax, "Season", "Energy (MW)")
    ax.yaxis.set_major_formatter(FuncFormatter(_mw))
    plt.tight_layout()
    return fig


# ══════════════════════════════════════════════
# BONUS — YEAR-OVER-YEAR  — sns.barplot
# ══════════════════════════════════════════════
def chart_yearly_avg(df):
    if df.empty: return _empty()
    yearly = df.groupby("Year")["AEP_MW"].mean().reset_index()
    peak_y = yearly.loc[yearly["AEP_MW"].idxmax(), "Year"]
    low_y  = yearly.loc[yearly["AEP_MW"].idxmin(), "Year"]
    colors = [CORAL   if y == peak_y
              else EMERALD if y == low_y
              else BLUE
              for y in yearly["Year"]]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    yearly["YearStr"] = yearly["Year"].astype(str)
    color_map = dict(zip(yearly["YearStr"], colors))
    sns.barplot(data=yearly, x="YearStr", y="AEP_MW",
                hue="YearStr", palette=color_map, legend=False,
                edgecolor=BG, linewidth=0.3, ax=ax)
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=9)
    ax.legend(handles=[
        plt.Rectangle((0,0),1,1, color=CORAL,   label="Highest Year"),
        plt.Rectangle((0,0),1,1, color=EMERALD, label="Lowest Year"),
        plt.Rectangle((0,0),1,1, color=BLUE,    label="Other"),
    ], fontsize=9); _legend(ax)
    _title(ax, "Average Annual Energy Consumption")
    _labels(ax, "Year", "Avg MW")
    ax.yaxis.set_major_formatter(FuncFormatter(_mw))
    plt.tight_layout()
    return fig