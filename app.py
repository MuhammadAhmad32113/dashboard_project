"""
app.py  —  AEP Energy Consumption Dashboard
Course : Exploratory Data Analysis
"""

import gradio as gr
import pandas as pd

from filters import load_and_clean, apply_filters, compute_kpis
from charts import (
    chart_pie, chart_histogram, chart_line, chart_bar,
    chart_scatter, chart_box, chart_heatmap, chart_area,
    chart_count, chart_violin, chart_yearly_avg,
)

DF = load_and_clean("data/AEP_hourly.csv")

YEAR_MIN    = int(DF["Year"].min())
YEAR_MAX    = int(DF["Year"].max())
MW_MIN      = float(DF["AEP_MW"].min())
MW_MAX      = float(DF["AEP_MW"].max())
ALL_SEASONS = ["Winter", "Spring", "Summer", "Autumn"]
ALL_MONTHS  = list(range(1, 13))
MONTH_NAMES = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}


def update_dashboard(year_start, year_end, seasons, months_sel,
                     mw_low, mw_high, day_types, keyword):
    name_to_num = {v: k for k, v in MONTH_NAMES.items()}
    months_nums = [name_to_num[m] for m in months_sel] if months_sel else None

    dff = apply_filters(DF, year_start, year_end, seasons, months_nums,
                        mw_low, mw_high, day_types, keyword)

    kpi_md = compute_kpis(dff)

    f_pie      = chart_pie(dff)
    f_hist     = chart_histogram(dff)
    f_line     = chart_line(dff)
    f_area     = chart_area(dff)
    f_bar      = chart_bar(dff)
    f_count    = chart_count(dff)
    f_yearly   = chart_yearly_avg(dff)
    f_scatter  = chart_scatter(dff)
    f_box      = chart_box(dff)
    f_violin   = chart_violin(dff)
    f_heatmap  = chart_heatmap(dff)

    count_str = f"Showing {len(dff):,} matching hourly data rows."

    return (kpi_md, f_pie, f_hist, f_line, f_area, f_bar, f_count,
            f_yearly, f_scatter, f_box, f_violin, f_heatmap, count_str)


def reset_filters():
    return [YEAR_MIN, YEAR_MAX, ALL_SEASONS,
            [MONTH_NAMES[m] for m in ALL_MONTHS],
            MW_MIN, MW_MAX, ["Weekday", "Weekend"], ""]


# ─────────────────────────────────────────────────────────────────────────────
#  GRADIO DASHBOARD INTERFACE LAYOUT (Exactly as your original file)
# ─────────────────────────────────────────────────────────────────────────────
with gr.Blocks(title="AEP Energy Analytics Hub", theme=gr.themes.Dark()) as demo:
    gr.Markdown("## ⚡ Advanced AEP Hourly Energy Analytics Hub")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🎛️ Filter Control Desk")
            
            with gr.Row():
                year_start = gr.Number(value=YEAR_MIN, label="Start Year", precision=0)
                year_end   = gr.Number(value=YEAR_MAX, label="End Year", precision=0)

            seasons_cb = gr.CheckboxGroup(choices=ALL_SEASONS, value=ALL_SEASONS, label="Seasons")
            months_ms  = gr.Dropdown(choices=[MONTH_NAMES[m] for m in ALL_MONTHS],
                                    value=[MONTH_NAMES[m] for m in ALL_MONTHS],
                                    multiselect=True, label="Months")

            with gr.Row():
                mw_low  = gr.Slider(minimum=MW_MIN, maximum=MW_MAX, value=MW_MIN, label="Min MW")
                mw_high = gr.Slider(minimum=MW_MIN, maximum=MW_MAX, value=MW_MAX, label="Max MW")

            day_type_cb = gr.CheckboxGroup(choices=["Weekday", "Weekend"], value=["Weekday", "Weekend"], label="Day Period")
            keyword_box = gr.Textbox(value="", label="SQL Log Filter (Keyword Search)", placeholder="e.g., peak, anomaly...")

            with gr.Row():
                apply_btn = gr.Button("Apply Filters", variant="primary")
                reset_btn = gr.Button("Reset Settings")

        with gr.Column(scale=2):
            gr.Markdown("### 📈 Real-Time KPI Insights")
            kpi_display = gr.Markdown()
            record_count = gr.Markdown("Loading metric counts...")

            # 📊 Navigation Dashboard Tabs
            with gr.Tab("Energy Composition"):
                with gr.Row():
                    pie_plot  = gr.Plot(label="")
                    hist_plot = gr.Plot(label="")

            with gr.Tab("Trends Over Time"):
                with gr.Row():
                    line_plot = gr.Plot(label="")
                with gr.Row():
                    area_plot = gr.Plot(label="")

            with gr.Tab("Categorical Comparisons"):
                with gr.Row():
                    bar_plot   = gr.Plot(label="")
                    count_plot = gr.Plot(label="")
                with gr.Row():
                    yearly_plot = gr.Plot(label="")

            with gr.Tab("Statistical Analysis"):
                with gr.Row():
                    scatter_plot = gr.Plot(label="")
                    box_plot     = gr.Plot(label="")
                with gr.Row():
                    violin_plot  = gr.Plot(label="")
                    heatmap_plot = gr.Plot(label="")

    inputs  = [year_start, year_end, seasons_cb, months_ms,
               mw_low, mw_high, day_type_cb, keyword_box]
    outputs = [kpi_display,
               pie_plot, hist_plot, line_plot, area_plot,
               bar_plot, count_plot, yearly_plot,
               scatter_plot, box_plot, violin_plot, heatmap_plot,
               record_count]

    apply_btn.click(fn=update_dashboard, inputs=inputs, outputs=outputs)
    reset_btn.click(fn=reset_filters,   inputs=[],     outputs=inputs)
    demo.load(fn=update_dashboard,      inputs=inputs, outputs=outputs)


if __name__ == "__main__":
    demo.launch()
