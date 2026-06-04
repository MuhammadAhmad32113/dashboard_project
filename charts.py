"""
charts.py  —  AEP Energy Dashboard
Same colors + dark theme, completely upgraded to Plotly for interactive downloads.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────────────────────
#  EXACT SAME COLOR PALETTE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
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

# Global download configuration settings for your framework components
CHART_CONFIG = {
    'displayModeBar': True,
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'aep_energy_chart',
        'height': 500,
        'width': 900,
        'scale': 2
    }
}

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL PLOTLY THEME APPLIER (Preserves Dark Theme Layout)
# ─────────────────────────────────────────────────────────────────────────────
def _apply_theme(fig, title_text="", xlabel="", ylabel="", show_legend=True):
    """Applies your exact dashboard visual theme to any Plotly figure."""
    fig.update_layout(
        title=dict(
            text=title_text,
            x=0.01,
            font=dict(color=TEXT, size=14, family="sans-serif")
        ),
        paper_bgcolor=BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT),
        margin=dict(l=55, r=25, t=55, b=50),
        showlegend=show_legend,
        xaxis=dict(
            title=dict(text=xlabel, font=dict(color=TEXT_SUB, size=11)),
            tickfont=dict(color=TEXT_SUB, size=10),
            gridcolor=GRID,
            gridwidth=0.5,
            showgrid=True,
            linecolor=GRID,
            zeroline=False
        ),
        yaxis=dict(
            title=dict(text=ylabel, font=dict(color=TEXT_SUB, size=11)),
            tickfont=dict(color=TEXT_SUB, size=10),
            gridcolor=GRID,
            gridwidth=0.5,
            showgrid=True,
            linecolor=GRID,
            zeroline=False,
            tickformat="~s"
        ),
        legend=dict(
            bgcolor=CARD_BG,
            bordercolor=GRID,
            borderwidth=1,
            font=dict(color=TEXT, size=10),
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        )
    )
    return fig

def _empty(msg="No data for selected filters."):
    """Returns a styled empty placeholder figure matching your layout style."""
    fig = go.Figure()
    fig.add_annotation(
        text=msg, x=0.5, y=0.5, showarrow=False,
        font=dict(color=TEXT_SUB, size=12)
    )
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=CARD_BG,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    return fig

# ═════════════════════════════════════════════════════════════════════════════
# 1. PIE CHART
# ═════════════════════════════════════════════════════════════════════════════
def chart_pie(df):
    if df.empty: return _empty()
    data = df.groupby("Season")["AEP_MW"].sum().reset_index()
    colors = [SEASON_COLORS.get(s, BLUE) for s in data["Season"]]

    fig = px.pie(
        data, names="Season", values="AEP_MW",
        color_discrete_sequence=colors,
        hole=0.0
    )
    fig.update_traces(
        texttemplate="%1.1f%%",
        textposition="inside",
        textfont=dict(size=11, color="white"),
        marker=dict(line=dict(color=BG, width=3))
    )
    _apply_theme(fig, "Energy Share by Season", show_legend=True)
    return fig

# ═════════════════════════════════════════════════════════════════════════════
# 2. HISTOGRAM
# ═════════════════════════════════════════════════════════════════════════════
def chart_histogram(df):
    if df.empty: return _empty()
    
    fig = px.histogram(
        df, x="AEP_MW", nbins=55,
        color_discrete_sequence=[BLUE]
    )
    fig.update_traces(marker=dict(line=dict(color=BG, width=0.3), opacity=0.85))
    
    mean_val = df["AEP_MW"].mean()
    fig.add_vline(
        x=mean_val, line_dash="dash", line_color=AMBER, line_width=2,
        annotation_text=f"Mean {mean_val:,.0f} MW",
        annotation_position="top right",
        annotation_font=dict(color=TEXT, size=10)
    )
    
    _apply_theme(fig, "Hourly Consumption — Frequency Distribution", "Energy (MW)", "Frequency", show_legend=False)
    return fig

# ═════════════════════════════════════════════════════════════════════════════
# 3. LINE CHART
# ═════════════════════════════════════════════════════════════════════════════
def chart_line(df):
    if df.empty: return _empty()
    monthly = df.groupby(["Year","Month"])["AEP_MW"].mean().reset_index()
    monthly["Period"] = pd.to_datetime(monthly[["Year","Month"]].assign(day=1))
    monthly.sort_values("Period", inplace=True)

    fig = px.line(monthly, x="Period", y="AEP_MW", color_discrete_sequence=[BLUE])
    fig.update_traces(fill="tozeroy", fillcolor="rgba(59, 130, 246, 0.08)", line=dict(width=2))
    
    _apply_theme(fig, "Monthly Average Energy Consumption", "Date", "Avg MW", show_legend=False)
    fig.update_xaxes(dtick="M12", tickformat="%Y")
    return fig

# ═════════════════════════════════════════════════════════════════════════════
# 4. BAR CHART
# ═════════════════════════════════════════════════════════════════════════════
def chart_bar(df):
    if df.empty: return _empty()
    hourly = df.groupby("Hour")["AEP_MW"].mean().reset_index()
    peak_h  = hourly.loc[hourly["AEP_MW"].idxmax(), "Hour"]
    low_h   = hourly.loc[hourly["AEP_MW"].idxmin(), "Hour"]
    
    colors  = [CORAL if h == peak_h else EMERALD if h == low_h else BLUE for h in hourly["Hour"]]

    fig = px.bar(hourly, x="Hour", y="AEP_MW", color="Hour",
                 color_discrete_sequence=colors, category_orders={"Hour": list(range(24))})
    
    fig.update_traces(marker=dict(line=dict(color=BG, width=0.3)))
    _apply_theme(fig, "Average Consumption by Hour of Day", "Hour", "Avg MW", show_legend=False)
    
    fig.update_xaxes(
        tickmode="array",
        tickvals=list(range(24)),
        ticktext=[f"{h:02d}:00" for h in range(24)],
        tickangle=45
    )
    return fig

# ═════════════════════════════════════════════════════════════════════════════
# 5. SCATTER PLOT
# ═════════════════════════════════════════════════════════════════════════════
def chart_scatter(df):
    if df.empty: return _empty()
    sample = df.sample(min(4000, len(df)), random_state=42)
    
    fig = px.scatter(
        sample, x="Hour", y="AEP_MW", color="Season",
        color_discrete_map=SEASON_COLORS,
        category_orders={"Season": ["Winter", "Spring", "Summer", "Autumn"]}
    )
    fig.update_traces(marker=dict(opacity=0.22, size=5))
    _apply_theme(fig, "Hour of Day vs Energy — by Season", "Hour of Day", "Energy (MW)", show_legend=True)
    
    fig.update_xaxes(tickmode="linear", tick0=0, dtick=2)
    return fig

# ═════════════════════════════════════════════════════════════════════════════
# 6. BOX PLOT
# ═════════════════════════════════════════════════════════════════════════════
def chart_box(df):
    if df.empty: return _empty()
    df2 = df.copy()
    df2["MonthName"] = pd.Categorical(df2["MonthName"], categories=MONTH_ORDER, ordered=True)
    df2.sort_values("MonthName", inplace=True)

    fig = px.box(df2, x="MonthName", y="AEP_MW", color_discrete_sequence=[BLUE])
    fig.update_traces(
        line=dict(width=1),
        marker=dict(size=2, opacity=0.25, color=TEXT_SUB),
        fillcolor="rgba(59, 130, 246, 0.6)"
    )
    _apply_theme(fig, "Energy Distribution by Month — Box Plot", "Month", "Energy (MW)", show_legend=False)
    return fig

# ═════════════════════════════════════════════════════════════════════════════
# 7. HEATMAP
# ═════════════════════════════════════════════════════════════════════════════
def chart_heatmap(df):
    if df.empty or df["Month"].nunique() < 2: return _empty()
    pivot = df.pivot_table(values="AEP_MW", index="Hour", columns="Month", aggfunc="mean")
    pivot.columns = [MONTH_ORDER[c-1] for c in pivot.columns]

    colors = ["#0f172a", "#1e3a5f", BLUE, CYAN, EMERALD, AMBER, CORAL]
    
    fig = px.imshow(pivot, labels=dict(x="Month", y="Hour of Day", color="Avg MW"),
                    x=pivot.columns, y=pivot.index, color_continuous_scale=colors)
    
    fig.update_traces(xgap=1, ygap=1)
    _apply_theme(fig, "Avg Energy (MW) — Hour × Month", "Month", "Hour of Day", show_legend=False)
    
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Avg MW",
            titlefont=dict(color=TEXT_SUB, size=10),
            tickfont=dict(color=TEXT_SUB, size=9),
            thickness=15,
            len=0.7
        )
    )
    return fig

# ═════════════════════════════════════════════════════════════════════════════
# 8. AREA CHART
# ═════════════════════════════════════════════════════════════════════════════
def chart_area(df):
    if df.empty: return _empty()
    daily = df.groupby("Date")["AEP_MW"].mean().reset_index()
    daily["Date"] = pd.to_datetime(daily["Date"])
    daily.sort_values("Date", inplace=True)
    daily["Roll7"]  = daily["AEP_MW"].rolling(7,  min_periods=1).mean()
    daily["Roll30"] = daily["AEP_MW"].rolling(30, min_periods=1).mean()

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["AEP_MW"], name="Daily Avg",
        line=dict(color=CYAN, width=0.6), opacity=0.4,
        fill='tozeroy', fillcolor="rgba(6, 182, 212, 0.07)"
    ))
    
    fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Roll7"], name="7-Day Avg", line=dict(color=AMBER, width=1.8)))
    fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Roll30"], name="30-Day Avg", line=dict(color=VIOLET, width=2.2, dash="dash")))
    
    _apply_theme(fig, "Daily Consumption with Rolling Averages", "Date", "Energy (MW)", show_legend=True)
    fig.update_xaxes(tickformat="%Y")
    return fig

# ═════════════════════════════════════════════════════════════════════════════
# 9. COUNT PLOT
# ═════════════════════════════════════════════════════════════════════════════
def chart_count(df):
    if df.empty: return _empty()
    df2 = df.copy()
    df2["DayName"] = pd.Categorical(df2["DayName"], categories=DAY_ORDER, ordered=True)
    
    counts = df2["DayName"].value_counts().reindex(DAY_ORDER).reset_index()
    colors = [VIOLET if d in {"Sat","Sun"} else BLUE for d in DAY_ORDER]

    fig = px.bar(counts, x="DayName", y="count", color="DayName", color_discrete_sequence=colors)
    fig.update_traces(marker=dict(line=dict(color=BG, width=0.3)))
    
    _apply_theme(fig, "Record Count by Day of Week", "Day", "Records", show_legend=False)
    return fig

# ═════════════════════════════════════════════════════════════════════════════
# 10. VIOLIN PLOT
# ═════════════════════════════════════════════════════════════════════════════
def chart_violin(df):
    if df.empty: return _empty()
    season_order = [s for s in ["Winter","Spring","Summer","Autumn"] if s in df["Season"].unique()]

    fig = px.violin(df, x="Season", y="AEP_MW", color="Season",
                    color_discrete_map=SEASON_COLORS, category_orders={"Season": season_order},
                    box=True, points=False)
    
    fig.update_traces(line=dict(width=1.0), opacity=0.75)
    _apply_theme(fig, "Energy Distribution by Season", "Season", "Energy (MW)", show_legend=False)
    return fig

# ═════════════════════════════════════════════════════════════════════════════
# BONUS — YEAR-OVER-YEAR
# ═════════════════════════════════════════════════════════════════════════════
def chart_yearly_avg(df):
    if df.empty: return _empty()
    yearly = df.groupby("Year")["AEP_MW"].mean().reset_index()
    peak_y = yearly.loc[yearly["AEP_MW"].idxmax(), "Year"]
    low_y  = yearly.loc[yearly["AEP_MW"].idxmin(), "Year"]
    
    colors = [CORAL if y == peak_y else EMERALD if y == low_y else BLUE for y in yearly["Year"]]
    yearly["YearStr"] = yearly["Year"].astype(str)

    fig = px.bar(yearly, x="YearStr", y="AEP_MW", color="YearStr", color_discrete_sequence=colors)
    fig.update_traces(marker=dict(line=dict(color=BG, width=0.3)))
    
    _apply_theme(fig, "Average Annual Energy Consumption", "Year", "Avg MW", show_legend=False)
    fig.update_xaxes(tickangle=45)
    return fig
