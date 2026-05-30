"""
app.py  —  AEP Energy Consumption Dashboard
Course : Exploratory Data Analysis
"""

import gradio as gr
import pandas as pd
import matplotlib
matplotlib.use("Agg")

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
    filtered = apply_filters(
        DF,
        year_range=(int(year_start), int(year_end)),
        seasons=seasons if seasons else None,
        months=months_nums,
        mw_range=(mw_low, mw_high),
        day_types=day_types if day_types else None,
        keyword=keyword,
    )
    kpis   = compute_kpis(filtered)
    rec_md = f"Showing **{len(filtered):,}** of **{len(DF):,}** records"
    return (
        _kpi_row(kpis),
        chart_pie(filtered), chart_histogram(filtered),
        chart_line(filtered), chart_area(filtered),
        chart_bar(filtered),  chart_count(filtered),
        chart_yearly_avg(filtered),
        chart_scatter(filtered), chart_box(filtered),
        chart_violin(filtered),  chart_heatmap(filtered),
        rec_md,
    )


def _kpi_card(label, value, border):
    return f"""
    <div style="flex:1;min-width:130px;
                background:linear-gradient(135deg,#2a2a2a,#222222);
                border-top:3px solid {border};
                border-radius:10px;padding:16px 18px;
                box-shadow:0 4px 15px rgba(0,0,0,0.4);">
      <div style="font-size:10px;color:#9ca3af;font-weight:700;
                  letter-spacing:1px;text-transform:uppercase;
                  margin-bottom:6px;">{label}</div>
      <div style="font-size:17px;font-weight:700;color:#ffffff;">{value}</div>
    </div>"""


def _kpi_row(k):
    return f"""
    <div style="display:flex;flex-wrap:wrap;gap:10px;
                padding:10px 0 4px;font-family:'Segoe UI',sans-serif;">
      {_kpi_card("Total Records",  k['total_records'],  "#3b82f6")}
      {_kpi_card("Avg Load",       k['mean_mw'],        "#3b82f6")}
      {_kpi_card("Peak Load",      k['max_mw'],         "#ef4444")}
      {_kpi_card("Min Load",       k['min_mw'],         "#22c55e")}
      {_kpi_card("Peak At",        k['peak_date'],      "#a855f7")}
      {_kpi_card("Lowest At",      k['trough_date'],    "#14b8a6")}
      {_kpi_card("Std Deviation",  k['std_mw'],         "#f97316")}
      {_kpi_card("Period",         k['years_covered'],  "#3b82f6")}
    </div>"""


def reset_filters():
    return (
        YEAR_MIN, YEAR_MAX,
        ALL_SEASONS,
        [MONTH_NAMES[m] for m in ALL_MONTHS],
        MW_MIN, MW_MAX,
        ["Weekday", "Weekend"],
        "",
    )


CSS = """
/* ── global ── */
*, body, .gradio-container {
    font-family: 'Segoe UI', system-ui, sans-serif !important;
}
body, .gradio-container {
    background: #1a1a1a !important;
    color: #ffffff !important;
    max-width: 100% !important;
    width: 100% !important;
    padding-left: 8px !important;
    padding-right: 8px !important;
    margin: 0 !important;
}
.gradio-container > .main > .wrap {
    max-width: 100% !important;
    padding: 0 16px !important;
}

/* ── header ── */
#dash-header {
    background: linear-gradient(135deg, #1e1e1e 0%, #111111 100%);
    border: 1px solid #333333;
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05);
}
#dash-header h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.3px;
}
#dash-header p {
    margin: 6px 0 0;
    color: #9ca3af;
    font-size: 13px;
}

/* ── filter accordion ── */
.filter-panel > div:first-child {
    background: #2a2a2a !important;
    border-radius: 10px !important;
    border: 1px solid #3a3a3a !important;
}
.filter-panel .label-wrap span {
    color: #ffffff !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

/* ── remove all inner black boxes ── */
.gradio-container .gr-box,
.gradio-container .gr-form,
.gradio-container .block,
.gradio-container .form,
div[data-testid="block"],
.block.svelte-1f354aw,
.block.svelte-90oupt,
.wrap.svelte-1hnfib2,
.gradio-container .wrap,
.gradio-container fieldset,
.gradio-container .label-wrap,
.gradio-slider, .gr-slider,
.gr-checkbox-group,
.gr-form > div,
.gradio-container > div > div > div > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}
/* keep accordion panel itself dark */
.filter-panel > div:first-child {
    background: #2a2a2a !important;
    border: 1px solid #3a3a3a !important;
    border-radius: 10px !important;
    padding: 24px 32px !important;
    width: 100% !important;
}
.filter-panel {
    width: 100% !important;
}

/* ── section titles inside filters ── */
.section-title {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    letter-spacing: 1.2px !important;
    text-transform: uppercase !important;
    margin: 0 0 8px 0 !important;
    padding-bottom: 6px !important;
    border-bottom: 1px solid #3a3a3a !important;
}

/* ── labels on all inputs ── */
label span, .gr-checkbox-group label span,
.gradio-container label {
    color: #d1d5db !important;
    font-size: 13px !important;
}

/* ── sliders ── */
input[type=range]::-webkit-slider-thumb { background: #3b82f6 !important; }
input[type=range]::-webkit-slider-runnable-track { background: #374151 !important; }

/* ── checkboxes ── */
input[type=checkbox]:checked { accent-color: #3b82f6; }

/* ── textbox ── */
.gradio-container input[type=text],
.gradio-container textarea {
    background: #2a2a2a !important;
    border: 1px solid #3a3a3a !important;
    color: #ffffff !important;
    border-radius: 8px !important;
}

/* ── dropdown ── */
.gradio-container .wrap {
    background: #2a2a2a !important;
    border-color: #3a3a3a !important;
}
.gradio-container .multiselect {
    background: #2a2a2a !important;
}
.gradio-container .token {
    background: #1d4ed8 !important;
    color: #ffffff !important;
}

/* ── buttons ── */
.btn-apply {
    background: #1d4ed8 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    box-shadow: 0 4px 12px rgba(59,130,246,0.4) !important;
}
.btn-apply:hover {
    background: #2563eb !important;
}
.btn-reset {
    background: #2a2a2a !important;
    color: #ffffff !important;
    border: 1.5px solid #4b5563 !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
}
.btn-reset:hover {
    background: #374151 !important;
}

/* ── KPI heading ── */
#kpi-heading {
    font-size: 18px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    letter-spacing: .5px;
    text-transform: uppercase;
    margin: 20px 0 8px !important;
    padding-left: 4px;
    border-left: 4px solid #3b82f6;
}

/* ── VISUALIZATIONS heading ── */
#viz-heading {
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    letter-spacing: .5px;
    margin: 24px 0 12px !important;
    padding-left: 4px;
    border-left: 4px solid #3b82f6;
}

/* ── TABS ── */
.gradio-tabitem,
div[data-testid="tab"],
.tabs > div > button,
button[role="tab"],
.tab-nav button {
    font-size: 15px !important;
    font-weight: 400 !important;
    color: #ffffff !important;
    background: #2a2a2a !important;
    border: none !important;
    padding: 12px 22px !important;
    border-radius: 8px 8px 0 0 !important;
    letter-spacing: 0.2px !important;
}
button[role="tab"]:hover,
.tab-nav button:hover {
    background: #3b82f6 !important;
    color: #ffffff !important;
}
button[role="tab"][aria-selected="true"],
.tab-nav button.selected {
    background: #1d4ed8 !important;
    color: #ffffff !important;
    border-bottom: 3px solid #60a5fa !important;
    font-weight: 500 !important;
}

/* ── chart cards ── */
.gradio-plot, .gr-plot {
    background: #242424 !important;
    border-radius: 12px !important;
    border: 1px solid #333333 !important;
    padding: 16px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.35) !important;
    margin: 4px !important;
}

/* ── hide chart floating labels ── */
.gradio-plot > .label-wrap,
.gr-plot > .label-wrap,
.plot-container > .label-wrap {
    display: none !important;
}

/* ── tabs container ── */
.tabs {
    background: #1a1a1a !important;
    border-radius: 12px !important;
    padding: 8px !important;
}

/* ── record count text ── */
.gradio-markdown p { color: #9ca3af !important; font-size: 13px !important; }



/* ── wider side columns padding ── */
.filter-panel .gr-row > div:first-child,
.filter-panel .gr-row > div:last-child {
    padding-left: 12px !important;
    padding-right: 12px !important;
}
input[type=range] {
    width: 100% !important;
    min-width: 200px !important;
}
/* ── aggressive box removal for Gradio 4.x ── */
.svelte-1f354aw, .svelte-90oupt, .svelte-1hnfib2,
.svelte-1gfkn6u, .svelte-1ed2p3z,
[class*="svelte-"] > .block,
.prose, .gap,
.padded,
.container > .block > .block,
div.block { 
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
input[type=number] {
    background: #2a2a2a !important;
    border: 1px solid #3a3a3a !important;
    color: #ffffff !important;
    border-radius: 6px !important;
}
html, body { overflow-x: hidden !important; }
.gradio-container { overflow-x: hidden !important; max-width: 100vw !important; }
footer { display: none !important; }
"""

with gr.Blocks(
    theme=gr.themes.Base(primary_hue="blue"),
    css=CSS,
    title="AEP Energy Dashboard"
) as demo:

    # HEADER
    gr.HTML("""
    <div id="dash-header">
      <h1>AEP Hourly Energy Consumption &mdash; Analytics Dashboard</h1>
      <p>American Electric Power grid load data &nbsp;&bull;&nbsp;
         2004 &ndash; 2018 &nbsp;&bull;&nbsp;
         121,273 hourly records &nbsp;&bull;&nbsp;
         Exploratory Data Analysis</p>
    </div>""")

    # FILTERS
    with gr.Accordion("Filters & Controls", open=True,
                      elem_classes=["filter-panel"]):
        with gr.Row(equal_height=True):
            with gr.Column(min_width=280):
                gr.HTML('<div class="section-title">Date Range</div>')
                year_start = gr.Slider(YEAR_MIN, YEAR_MAX, value=YEAR_MIN,
                                       step=1, label="Start Year")
                year_end   = gr.Slider(YEAR_MIN, YEAR_MAX, value=YEAR_MAX,
                                       step=1, label="End Year")

            with gr.Column(min_width=200):
                gr.HTML('<div class="section-title">Category Filters</div>')
                seasons_cb  = gr.CheckboxGroup(ALL_SEASONS, value=ALL_SEASONS,
                                               label="Season")
                day_type_cb = gr.CheckboxGroup(["Weekday","Weekend"],
                                               value=["Weekday","Weekend"],
                                               label="Day Type")

            with gr.Column(min_width=200):
                gr.HTML('<div class="section-title">Month Selection</div>')
                months_ms = gr.Dropdown(
                    choices=[MONTH_NAMES[m] for m in ALL_MONTHS],
                    value=[MONTH_NAMES[m] for m in ALL_MONTHS],
                    multiselect=True, label="Months (multi-select)")

            with gr.Column(min_width=280):
                gr.HTML('<div class="section-title">Load Range (MW)</div>')
                mw_low  = gr.Slider(MW_MIN, MW_MAX, value=MW_MIN,
                                    step=100, label="Min MW")
                mw_high = gr.Slider(MW_MIN, MW_MAX, value=MW_MAX,
                                    step=100, label="Max MW")

        with gr.Row():
            keyword_box = gr.Textbox(
                placeholder="e.g.  2010-07   or   2015",
                label="Text Search (keyword in date)",
                scale=4)
            apply_btn = gr.Button("Apply Filters", variant="primary",
                                  elem_classes=["btn-apply"], scale=1)
            reset_btn = gr.Button("Reset All", variant="secondary",
                                  elem_classes=["btn-reset"], scale=1)

    # KPI
    gr.HTML('<div id="kpi-heading">Key Performance Indicators</div>')
    kpi_display  = gr.HTML()
    record_count = gr.Markdown()

    # CHARTS
    gr.HTML('<div id="viz-heading">Visualizations</div>')

    with gr.Tabs():
        with gr.Tab("Distribution & Composition"):
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
    import os
    port = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=port, share=False)