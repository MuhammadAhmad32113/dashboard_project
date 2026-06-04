"""
app.py  —  AEP Energy Consumption Dashboard (Streamlit Version)
Course : Exploratory Data Analysis
"""

import streamlit as st
import pandas as pd

from filters import load_and_clean, apply_filters, compute_kpis
from charts import (
    chart_pie, chart_histogram, chart_line, chart_bar,
    chart_scatter, chart_box, chart_heatmap, chart_area,
    chart_count, chart_violin, chart_yearly_avg,
)

# Force wide dashboard structure layout
st.set_page_config(page_title="AEP Energy Analytics Hub", layout="wide")

# ─────────────────────────────────────────────────────────────────────────────
#  DATA INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────

DF = load_and_clean("data/AEP_hourly.csv")

# Global constants for UI components
YEAR_MIN    = int(DF["Year"].min())
YEAR_MAX    = int(DF["Year"].max())
MW_MIN      = float(DF["AEP_MW"].min())
MW_MAX      = float(DF["AEP_MW"].max())
ALL_SEASONS = ["Winter", "Spring", "Summer", "Autumn"]
ALL_MONTHS  = list(range(1, 13))
MONTH_NAMES = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

# ─────────────────────────────────────────────────────────────────────────────
#  STREAMLIT INTERFACE (THEME & LAYOUT MATCHED EXACTLY)
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("# ⚡ Advanced AEP Hourly Energy Analytics Hub")
st.markdown("Interactive Exploratory Data Analysis of American Electric Power consumption patterns.")

# Split layout into your exact 1:2 Column Ratio
col_left_control, col_right_visuals = st.columns([1, 2])

# --- LEFT COLUMN: CONTROLS ---
with col_left_control:
    st.markdown("### 🎛️ Filter Control Desk")
    
    # Side-by-side Input boxes for Start and End Year
    col_year1, col_year2 = st.columns(2)
    with col_year1:
        year_start = st.number_input("Start Year", min_value=YEAR_MIN, max_value=YEAR_MAX, value=YEAR_MIN, step=1)
    with col_year2:
        year_end = st.number_input("End Year", min_value=YEAR_MIN, max_value=YEAR_MAX, value=YEAR_MAX, step=1)

    seasons_cb = st.multiselect(
        "Seasons Selection", options=ALL_SEASONS, default=ALL_SEASONS
    )

    months_ms = st.multiselect(
        "Months Selection",
        options=[MONTH_NAMES[m] for m in ALL_MONTHS],
        default=[MONTH_NAMES[m] for m in ALL_MONTHS]
    )

    # Streamlit natively handles dual-range tracking in one slider object
    mw_low, mw_high = st.slider(
        "MW Threshold Range", 
        min_value=MW_MIN, 
        max_value=MW_MAX, 
        value=(MW_MIN, MW_MAX)
    )

    day_type_cb = st.multiselect(
        "Day Period", options=["Weekday", "Weekend"], default=["Weekday", "Weekend"]
    )

    keyword_box = st.text_input(
        "SQL Log Filter (Keyword Search)", 
        placeholder="Search notes e.g., 'peak', 'maintenance'..."
    )

    # Action Control Buttons Layout
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        apply_btn = st.button("Apply Filters", type="primary")
    with col_btn2:
        if st.button("Reset Settings"):
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────
#  DATA FILTER PROCESSING & CALCULATION LOGIC
# ─────────────────────────────────────────────────────────────────────────

# Convert month selection strings back to numeric system arrays
name_to_num = {v: k for k, v in MONTH_NAMES.items()}
months_nums = [name_to_num[m] for m in months_ms] if months_ms else None

# Fetch active dataset matrix slice
dff = apply_filters(DF, year_start, year_end, seasons_cb, months_nums,
                    mw_low, mw_high, day_type_cb, keyword_box)

# Extract KPI summary string parameters
kpi_md = compute_kpis(dff)

# --- RIGHT COLUMN: VISUALIZATIONS ---
with col_right_visuals:
    st.markdown("### 📈 Real-Time KPI Insights")
    
    # KPI metrics panel
    st.markdown(kpi_md)
    st.caption(f"Showing {len(dff):,} matching hourly data rows.")

    # 📊 Exact Dashboard Section Tabs Mapping
    tab_comp, tab_trends, tab_cat, tab_stat = st.tabs([
        "Energy Composition", 
        "Trends Over Time", 
        "Categorical Comparisons", 
        "Statistical Analysis"
    ])

    with tab_comp:
        col_comp1, col_comp2 = st.columns(2)
        with col_comp1:
            st.plotly_chart(chart_pie(dff), use_container_width=True)
        with col_comp2:
            st.plotly_chart(chart_histogram(dff), use_container_width=True)

    with tab_trends:
        st.plotly_chart(chart_line(dff), use_container_width=True)
        st.plotly_chart(chart_area(dff), use_container_width=True)

    with tab_cat:
        col_cat1, col_cat2 = st.columns(2)
        with col_cat1:
            st.plotly_chart(chart_bar(dff), use_container_width=True)
        with col_cat2:
            st.plotly_chart(chart_count(dff), use_container_width=True)
        st.plotly_chart(chart_yearly_avg(dff), use_container_width=True)

    with tab_stat:
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.plotly_chart(chart_scatter(dff), use_container_width=True)
        with col_stat2:
            st.plotly_chart(chart_box(dff), use_container_width=True)
        
        col_stat3, col_stat4 = st.columns(2)
        with col_stat3:
            st.plotly_chart(chart_violin(dff), use_container_width=True)
        with col_stat4:
            st.plotly_chart(chart_heatmap(dff), use_container_width=True)
