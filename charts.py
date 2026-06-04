"""
charts.py — All visualization functions for the Ember Electricity Dashboard
Charts: Pie, Histogram, Line, Bar, Scatter, Box, Heatmap, Area, Count, Violin
Bonus : Bubble Chart
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# GLOBAL STYLE
# ─────────────────────────────────────────────

PALETTE = [
    "#2563EB", "#16A34A", "#DC2626", "#D97706", "#7C3AED",
    "#0891B2", "#DB2777", "#65A30D", "#EA580C", "#6366F1",
]

BACKGROUND  = "#0F172A"   # dark navy
CARD_BG     = "#1E293B"   # slightly lighter card
TEXT_COLOR  = "#F1F5F9"
GRID_COLOR  = "#334155"
ACCENT      = "#38BDF8"   # sky blue


def _base_layout(**kwargs) -> dict:
    """Return a base Plotly layout dict matching the original dark theme."""
    layout = dict(
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT_COLOR, family="DejaVu Sans", size=11),
        title_font=dict(color=TEXT_COLOR, size=13, family="DejaVu Sans"),
        legend=dict(
            bgcolor=CARD_BG,
            bordercolor=GRID_COLOR,
            borderwidth=1,
            font=dict(color=TEXT_COLOR, size=9),
        ),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            linecolor=GRID_COLOR,
            tickfont=dict(color=TEXT_COLOR, size=9),
            title_font=dict(color=TEXT_COLOR, size=11),
            zerolinecolor=GRID_COLOR,
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            linecolor=GRID_COLOR,
            tickfont=dict(color=TEXT_COLOR, size=9),
            title_font=dict(color=TEXT_COLOR, size=11),
            zerolinecolor=GRID_COLOR,
        ),
        margin=dict(l=60, r=40, t=60, b=60),
    )
    layout.update(kwargs)
    return layout


def _empty_fig(msg: str = "No data available") -> go.Figure:
    """Return a blank figure with a centred message — mirrors the original ax.text() fallback."""
    fig = go.Figure()
    fig.add_annotation(
        text=msg, xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(color=TEXT_COLOR, size=13),
    )
    fig.update_layout(**_base_layout())
    return fig


# ─────────────────────────────────────────────
# 1. PIE CHART — Energy mix proportions
# ─────────────────────────────────────────────

def chart_pie(df: pd.DataFrame, country: str, year: int):
    """
    Proportional electricity generation mix for a single country & year.
    """
    fuel_vars = ["Coal", "Gas", "Nuclear", "Hydro", "Wind", "Solar",
                 "Bioenergy", "Other renewables", "Other fossil"]
    sub = df[
        (df["Area"] == country) &
        (df["Year"] == year) &
        (df["Variable"].isin(fuel_vars)) &
        (df["Unit"] == "%")
    ].dropna(subset=["Value"])

    if sub.empty:
        fig = _empty_fig("No data available")
        fig.update_layout(title=dict(text=f"Energy Mix — {country} ({year})", x=0.5))
        return fig

    sub = sub.groupby("Variable")["Value"].sum().reset_index()
    sub = sub[sub["Value"] > 0].sort_values("Value", ascending=False)

    fig = go.Figure(go.Pie(
        labels=sub["Variable"],
        values=sub["Value"],
        marker=dict(
            colors=PALETTE[:len(sub)],
            line=dict(color=BACKGROUND, width=1.5),
        ),
        textinfo="label+percent",
        textfont=dict(size=9, color=TEXT_COLOR),
        insidetextfont=dict(size=8, color=BACKGROUND),
        hovertemplate="<b>%{label}</b><br>Share: %{percent}<br>Value: %{value:.1f}%<extra></extra>",
        rotation=140,
        pull=[0.02] * len(sub),
    ))
    fig.update_layout(
        **_base_layout(
            title=dict(
                text=f"Electricity Generation Mix — {country} ({year})",
                x=0.5, font=dict(size=14, color=TEXT_COLOR),
            ),
            showlegend=True,
            legend=dict(
                bgcolor=CARD_BG, bordercolor=GRID_COLOR, borderwidth=1,
                font=dict(color=TEXT_COLOR, size=8),
                orientation="v", x=1.02, y=0.5,
            ),
            width=700, height=500,
        )
    )
    return fig


# ─────────────────────────────────────────────
# 2. HISTOGRAM — CO2 intensity distribution
# ─────────────────────────────────────────────

def chart_histogram(df: pd.DataFrame):
    """Frequency distribution of CO2 intensity across countries & years."""
    sub = df[df["Variable"] == "CO2 intensity"].dropna(subset=["Value"])

    if sub.empty:
        return _empty_fig("No CO2 intensity data")

    mean_val   = sub["Value"].mean()
    median_val = sub["Value"].median()

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=sub["Value"],
        nbinsx=40,
        marker=dict(color=ACCENT, line=dict(color=BACKGROUND, width=0.6)),
        opacity=0.85,
        name="CO₂ Intensity",
        hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>",
    ))
    # Mean line — mirrors ax.axvline(..., label=f"Mean: {mean:.0f}")
    fig.add_vline(
        x=mean_val, line=dict(color="#F59E0B", dash="dash", width=1.8),
        annotation_text=f"Mean: {mean_val:.0f}",
        annotation_font=dict(color="#F59E0B"),
        annotation_position="top right",
    )
    # Median line — mirrors ax.axvline(..., label=f"Median: {median:.0f}")
    fig.add_vline(
        x=median_val, line=dict(color="#34D399", dash="dot", width=1.8),
        annotation_text=f"Median: {median_val:.0f}",
        annotation_font=dict(color="#34D399"),
        annotation_position="top left",
    )
    fig.update_layout(
        **_base_layout(
            title=dict(
                text="Distribution of CO₂ Intensity Across Countries & Years",
                x=0.5,
            ),
            xaxis=dict(
                title=dict(text="CO₂ Intensity (gCO₂e per kWh)", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
            yaxis=dict(
                title=dict(text="Frequency", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
            bargap=0.05,
        )
    )
    return fig


# ─────────────────────────────────────────────
# 3. LINE CHART — Trend over time
# ─────────────────────────────────────────────

def chart_line(df: pd.DataFrame, countries: list, variable: str, unit: str = None):
    """Line chart of a chosen variable over time for selected countries."""
    sub = df[(df["Variable"] == variable) & (df["Area"].isin(countries))].copy()
    if unit:
        sub = sub[sub["Unit"] == unit]
    sub = sub.dropna(subset=["Year", "Value"])

    if sub.empty:
        fig = _empty_fig("No data for selection")
        fig.update_layout(title=dict(text=f"{variable} — Trend Over Time", x=0.5))
        return fig

    unit_label = sub["Unit"].iloc[0] if not sub.empty else ""

    fig = go.Figure()
    for i, country in enumerate(countries):
        data = sub[sub["Area"] == country].sort_values("Year")
        if data.empty:
            continue
        fig.add_trace(go.Scatter(
            x=data["Year"], y=data["Value"],
            mode="lines+markers",
            name=country,
            line=dict(color=PALETTE[i % len(PALETTE)], width=2),
            marker=dict(size=3),
            hovertemplate=f"<b>{country}</b><br>Year: %{{x}}<br>{variable}: %{{y:.2f}} {unit_label}<extra></extra>",
        ))

    fig.update_layout(
        **_base_layout(
            title=dict(
                text=f"{variable} Trend — {', '.join(countries[:5])}",
                x=0.5,
            ),
            xaxis=dict(
                title=dict(text="Year", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
                dtick=1,
            ),
            yaxis=dict(
                title=dict(text=f"{variable} ({unit_label})", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
            hovermode="x unified",
            legend=dict(
                bgcolor=CARD_BG, bordercolor=GRID_COLOR, borderwidth=1,
                font=dict(color=TEXT_COLOR, size=9),
                orientation="v",
            ),
        )
    )
    return fig


# ─────────────────────────────────────────────
# 4. BAR CHART — Country comparison
# ─────────────────────────────────────────────

def chart_bar(df: pd.DataFrame, variable: str, year: int, top_n: int = 15):
    """Horizontal bar chart comparing countries for a variable in a given year."""
    sub = df[
        (df["Variable"] == variable) &
        (df["Year"] == year) &
        df["is_country"]
    ].dropna(subset=["Value"])
    sub = sub.groupby("Area")["Value"].mean().nlargest(top_n).reset_index()
    sub = sub.sort_values("Value")

    if sub.empty:
        return _empty_fig("No data")

    unit_str = df[df["Variable"] == variable]["Unit"].dropna().iloc[0] \
        if not df[df["Variable"] == variable].empty else ""

    colors = [PALETTE[i % len(PALETTE)] for i in range(len(sub))]

    fig = go.Figure(go.Bar(
        x=sub["Value"],
        y=sub["Area"],
        orientation="h",
        marker=dict(color=colors, line=dict(color=BACKGROUND, width=0.5)),
        text=sub["Value"].round(1),
        textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=8),
        hovertemplate="<b>%{y}</b><br>" + variable + ": %{x:.1f} " + unit_str + "<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(
            title=dict(text=f"Top {top_n} Countries — {variable} ({year})", x=0.5),
            xaxis=dict(
                title=dict(text=f"{variable} ({unit_str})", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
            yaxis=dict(
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
            height=max(350, len(sub) * 28),
        )
    )
    return fig


# ─────────────────────────────────────────────
# 5. SCATTER PLOT — Two variables relationship
# ─────────────────────────────────────────────

def chart_scatter(df: pd.DataFrame, year: int):
    """Scatter: Renewables % vs CO2 intensity per country."""
    ren = df[
        (df["Variable"] == "Renewables") & (df["Unit"] == "%") &
        (df["Year"] == year) & df["is_country"]
    ][["Area", "Value"]].rename(columns={"Value": "Renewables_%"})

    co2 = df[
        (df["Variable"] == "CO2 intensity") &
        (df["Year"] == year) & df["is_country"]
    ][["Area", "Value"]].rename(columns={"Value": "CO2_intensity"})

    merged = ren.merge(co2, on="Area").dropna()

    if merged.empty:
        return _empty_fig("No data for scatter")

    # Trend line — mirrors np.polyfit logic
    z = np.polyfit(merged["Renewables_%"], merged["CO2_intensity"], 1)
    p = np.poly1d(z)
    xs = np.linspace(merged["Renewables_%"].min(), merged["Renewables_%"].max(), 100)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=merged["Renewables_%"], y=merged["CO2_intensity"],
        mode="markers+text",
        text=merged["Area"],
        textposition="top center",
        textfont=dict(size=7, color=TEXT_COLOR),
        marker=dict(
            size=10,
            color=merged["CO2_intensity"],
            colorscale="RdYlGn_r",
            showscale=True,
            colorbar=dict(
                title=dict(text="CO₂ Intensity (gCO₂e/kWh)", font=dict(color=TEXT_COLOR)),
                tickfont=dict(color=TEXT_COLOR),
            ),
            line=dict(color=BACKGROUND, width=0.8),
            opacity=0.9,
        ),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Renewables: %{x:.1f}%<br>"
            "CO₂: %{y:.1f} gCO₂e/kWh<extra></extra>"
        ),
        name="Countries",
    ))
    # Trend line — dashed yellow, mirrors ax.plot(..., "--", color="#F59E0B")
    fig.add_trace(go.Scatter(
        x=xs, y=p(xs),
        mode="lines",
        line=dict(color="#F59E0B", dash="dash", width=1.5),
        name="Trend",
        hoverinfo="skip",
    ))
    fig.update_layout(
        **_base_layout(
            title=dict(text=f"Renewables vs CO₂ Intensity — {year}", x=0.5),
            xaxis=dict(
                title=dict(text="Renewables Share (%)", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
            yaxis=dict(
                title=dict(text="CO₂ Intensity (gCO₂e per kWh)", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
        )
    )
    return fig


# ─────────────────────────────────────────────
# 6. BOX PLOT — Distribution per region group
# ─────────────────────────────────────────────

def chart_box(df: pd.DataFrame, variable: str):
    """Box plot of variable distribution by EU membership."""
    sub = df[
        (df["Variable"] == variable) & df["is_country"]
    ].dropna(subset=["Value"]).copy()

    sub["Group"] = sub["EU"].map({1: "EU Member", 0: "Non-EU"})

    if sub.empty:
        return _empty_fig("No data")

    unit_str = sub["Unit"].dropna().iloc[0] if not sub.empty else ""

    fig = go.Figure()
    # Mirrors sns.boxplot palette — EU Member = PALETTE[0], Non-EU = PALETTE[2]
    for group, color in [("EU Member", PALETTE[0]), ("Non-EU", PALETTE[2])]:
        vals = sub[sub["Group"] == group]["Value"]
        fig.add_trace(go.Box(
            y=vals,
            name=group,
            marker=dict(color=color, outliercolor=ACCENT, size=4),
            line=dict(color=color),
            boxmean="sd",
            hovertemplate=f"<b>{group}</b><br>Value: %{{y:.1f}} {unit_str}<extra></extra>",
        ))
    fig.update_layout(
        **_base_layout(
            title=dict(
                text=f"{variable} — EU vs Non-EU Distribution (All Years)", x=0.5,
            ),
            xaxis=dict(
                title=dict(text="Country Group", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
            yaxis=dict(
                title=dict(text=f"{variable} ({unit_str})", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
        )
    )
    return fig


# ─────────────────────────────────────────────
# 7. HEATMAP — Correlation matrix
# ─────────────────────────────────────────────

def chart_heatmap(df: pd.DataFrame, year: int):
    """
    Correlation heatmap of key electricity variables across countries for a year.
    """
    key_vars = ["Demand", "Renewables", "Fossil", "Nuclear",
                "CO2 intensity", "Solar", "Wind", "Hydro"]
    sub = df[
        (df["Year"] == year) & df["is_country"] &
        (df["Variable"].isin(key_vars))
    ].dropna(subset=["Value"])

    pivot = sub.pivot_table(index="Area", columns="Variable", values="Value", aggfunc="mean")
    pivot = pivot.dropna(thresh=3)

    if pivot.empty or pivot.shape[1] < 2:
        return _empty_fig("Not enough data for heatmap")

    corr = pivot.corr()
    # mask — mirrors np.triu: keep only lower triangle
    mask = np.triu(np.ones_like(corr, dtype=bool))
    corr_masked = corr.where(~mask).round(2)

    fig = go.Figure(go.Heatmap(
        z=corr_masked.values,
        x=corr_masked.columns.tolist(),
        y=corr_masked.index.tolist(),
        colorscale="RdBu",
        zmid=0,
        text=corr_masked.values.round(2),
        texttemplate="%{text}",
        textfont=dict(size=9, color=TEXT_COLOR),
        hovertemplate="<b>%{y} × %{x}</b><br>r = %{z:.2f}<extra></extra>",
        colorbar=dict(
            tickfont=dict(color=TEXT_COLOR),
            title=dict(text="r", font=dict(color=TEXT_COLOR)),
        ),
    ))
    fig.update_layout(
        **_base_layout(
            title=dict(
                text=f"Correlation Matrix of Electricity Variables ({year})",
                x=0.5,
            ),
            xaxis=dict(
                tickangle=30,
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
            yaxis=dict(
                autorange="reversed",
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
            height=500,
        )
    )
    return fig


# ─────────────────────────────────────────────
# 8. AREA CHART — Cumulative trends
# ─────────────────────────────────────────────

def chart_area(df: pd.DataFrame, countries: list, variable: str = "Renewables"):
    """
    Stacked area chart showing cumulative variable over time for top countries.
    """
    sub = df[
        (df["Variable"] == variable) &
        (df["Unit"] == "%") &
        (df["Area"].isin(countries)) &
        df["is_country"]
    ].dropna(subset=["Year", "Value"])

    pivot = sub.pivot_table(index="Year", columns="Area", values="Value", aggfunc="mean")
    pivot = pivot.sort_index().ffill().fillna(0)

    if pivot.empty:
        return _empty_fig("No data for area chart")

    cols = pivot.columns.tolist()[:10]

    fig = go.Figure()
    for i, col in enumerate(cols):
        hex_c = PALETTE[i % len(PALETTE)].lstrip("#")
        r, g, b = int(hex_c[0:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16)
        fig.add_trace(go.Scatter(
            x=pivot.index.tolist(),
            y=pivot[col].tolist(),
            mode="lines",
            name=col,
            # alpha=0.35 mirrors plot.area(alpha=0.35)
            fill="tozeroy",
            fillcolor=f"rgba({r},{g},{b},0.35)",
            line=dict(color=PALETTE[i % len(PALETTE)], width=1.5),
            hovertemplate=f"<b>{col}</b><br>Year: %{{x}}<br>{variable}: %{{y:.1f}}%<extra></extra>",
        ))
    fig.update_layout(
        **_base_layout(
            title=dict(text=f"{variable} Share Over Time — Selected Countries", x=0.5),
            xaxis=dict(
                title=dict(text="Year", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
                dtick=1,
            ),
            yaxis=dict(
                title=dict(text=f"{variable} (%)", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
            hovermode="x unified",
            legend=dict(
                bgcolor=CARD_BG, bordercolor=GRID_COLOR, borderwidth=1,
                font=dict(color=TEXT_COLOR, size=8),
                orientation="h", x=0, y=1.05,
            ),
        )
    )
    return fig


# ─────────────────────────────────────────────
# 9. COUNT PLOT — Frequency of categorical data
# ─────────────────────────────────────────────

def chart_count(df: pd.DataFrame):
    """Count plot: number of data entries per Category."""
    sub = df[df["is_country"]].copy()

    if sub.empty:
        return _empty_fig("No data")

    # Mirrors sns.countplot with value_counts order
    order  = sub["Category"].value_counts().index.tolist()
    counts = sub["Category"].value_counts().reindex(order).reset_index()
    counts.columns = ["Category", "Count"]

    colors = [PALETTE[i % len(PALETTE)] for i in range(len(counts))]

    fig = go.Figure(go.Bar(
        x=counts["Category"],
        y=counts["Count"],
        marker=dict(color=colors, line=dict(color=BACKGROUND, width=0.5)),
        text=counts["Count"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=9),
        hovertemplate="<b>%{x}</b><br>Records: %{y:,}<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(
            title=dict(text="Record Count by Electricity Data Category", x=0.5),
            xaxis=dict(
                title=dict(text="Data Category", font=dict(color=TEXT_COLOR, size=11)),
                tickangle=15,
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
            yaxis=dict(
                title=dict(text="Number of Records", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
        )
    )
    return fig


# ─────────────────────────────────────────────
# 10. VIOLIN PLOT — Distribution & density
# ─────────────────────────────────────────────

def chart_violin(df: pd.DataFrame, variable: str):
    """Violin plot of a variable across decades."""
    sub = df[
        (df["Variable"] == variable) & df["is_country"]
    ].dropna(subset=["Year", "Value"]).copy()

    sub["Decade"] = (sub["Year"] // 10 * 10).astype(str) + "s"

    if sub.empty or sub["Decade"].nunique() < 2:
        return _empty_fig("Not enough data for violin")

    unit_str     = sub["Unit"].dropna().iloc[0] if not sub.empty else ""
    decade_order = sorted(sub["Decade"].unique())

    fig = go.Figure()
    for i, decade in enumerate(decade_order):
        vals = sub[sub["Decade"] == decade]["Value"]
        # inner="quartile" mirrors sns.violinplot(inner="quartile")
        fig.add_trace(go.Violin(
            y=vals,
            name=decade,
            box_visible=True,
            meanline_visible=True,
            fillcolor=PALETTE[i % len(PALETTE)],
            line_color=PALETTE[i % len(PALETTE)],
            opacity=0.75,
            hovertemplate=f"<b>{decade}</b><br>Value: %{{y:.1f}} {unit_str}<extra></extra>",
        ))
    fig.update_layout(
        **_base_layout(
            title=dict(text=f"{variable} Distribution by Decade", x=0.5),
            xaxis=dict(
                title=dict(text="Decade", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
            yaxis=dict(
                title=dict(text=f"{variable} ({unit_str})", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
            violinmode="overlay",
        )
    )
    return fig


# ─────────────────────────────────────────────
# BONUS — BUBBLE CHART
# ─────────────────────────────────────────────

def chart_bubble(df: pd.DataFrame, year: int):
    """
    Bubble chart: Renewables (x) vs CO2 (y) with bubble size = Demand.
    """
    ren = df[(df["Variable"] == "Renewables") & (df["Unit"] == "%") &
             (df["Year"] == year) & df["is_country"]
             ][["Area", "Value"]].rename(columns={"Value": "Ren"})
    co2 = df[(df["Variable"] == "CO2 intensity") & (df["Year"] == year) &
             df["is_country"]
             ][["Area", "Value"]].rename(columns={"Value": "CO2"})
    dem = df[(df["Variable"] == "Demand") & (df["Year"] == year) &
             df["is_country"]
             ][["Area", "Value"]].rename(columns={"Value": "Demand"})

    merged = ren.merge(co2, on="Area").merge(dem, on="Area").dropna()

    if merged.empty:
        return _empty_fig("No data")

    # Mirrors original: sizes = (Demand / max) * 1500 + 100  → scaled to Plotly marker px
    sizes = (merged["Demand"] / merged["Demand"].max()) * 60 + 10

    fig = go.Figure(go.Scatter(
        x=merged["Ren"],
        y=merged["CO2"],
        mode="markers+text",
        text=merged["Area"],
        textposition="top center",
        textfont=dict(size=7, color=TEXT_COLOR),
        marker=dict(
            size=sizes,
            color=merged["CO2"],
            colorscale="RdYlGn_r",
            showscale=True,
            colorbar=dict(
                title=dict(text="CO₂ Intensity (gCO₂e/kWh)", font=dict(color=TEXT_COLOR)),
                tickfont=dict(color=TEXT_COLOR),
            ),
            line=dict(color=TEXT_COLOR, width=0.6),
            opacity=0.85,
        ),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Renewables: %{x:.1f}%<br>"
            "CO₂: %{y:.1f} gCO₂e/kWh<br>"
            "Demand (scaled): %{marker.size:.1f}<extra></extra>"
        ),
    ))
    fig.update_layout(
        **_base_layout(
            title=dict(
                text=f"Bubble Chart — Renewables vs CO₂ (bubble = Demand) [{year}]",
                x=0.5,
            ),
            xaxis=dict(
                title=dict(text="Renewables Share (%)", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
            yaxis=dict(
                title=dict(text="CO₂ Intensity (gCO₂e per kWh)", font=dict(color=TEXT_COLOR, size=11)),
                gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                tickfont=dict(color=TEXT_COLOR, size=9),
            ),
        )
    )
    return fig
