"""
app.py  —  AEP Energy Consumption Dashboard
Layout: Fixed left sidebar (filters) + main content area (charts)
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
    rec_md = f"**{len(filtered):,}** of **{len(DF):,}** records"
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
    <div style="background:linear-gradient(135deg,#2a2a2a,#222);
                border-top:3px solid {border};border-radius:10px;
                padding:14px 16px;box-shadow:0 4px 15px rgba(0,0,0,0.4);
                margin-bottom:6px;">
      <div style="font-size:10px;color:#9ca3af;font-weight:700;
                  letter-spacing:1px;text-transform:uppercase;
                  margin-bottom:4px;">{label}</div>
      <div style="font-size:15px;font-weight:700;color:#fff;">{value}</div>
    </div>"""

def _kpi_row(k):
    return f"""
    <div style="font-family:'Segoe UI',sans-serif;">
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
        YEAR_MIN, YEAR_MAX, ALL_SEASONS,
        [MONTH_NAMES[m] for m in ALL_MONTHS],
        MW_MIN, MW_MAX, ["Weekday", "Weekend"], "",
    )


CSS = """
/* ── GLOBAL ── */
*, body, .gradio-container {
    font-family: 'Segoe UI', system-ui, sans-serif !important;
    box-sizing: border-box;
}
body, .gradio-container {
    background: #141414 !important;
    color: #e5e7eb !important;
    max-width: 100% !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow-x: hidden !important;
}
.gradio-container > .main > .wrap,
.gradio-container > .main {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* ── SIDEBAR ── */
#sidebar {
    position: fixed;
    top: 0; left: 0;
    width: 270px;
    height: 100vh;
    background: #1c1c1c;
    border-right: 1px solid #2e2e2e;
    overflow-y: auto;
    padding: 0;
    z-index: 100;
    box-shadow: 4px 0 20px rgba(0,0,0,0.4);
}
#sidebar-logo {
    background: linear-gradient(135deg,#1d4ed8,#1e40af);
    padding: 22px 20px;
    border-bottom: 1px solid #2e2e2e;
}
#sidebar-logo h2 {
    margin: 0;
    font-size: 15px;
    font-weight: 700;
    color: #fff;
    letter-spacing: 0.3px;
}
#sidebar-logo p {
    margin: 4px 0 0;
    font-size: 11px;
    color: #93c5fd;
}
#sidebar-content {
    padding: 16px;
}
.sidebar-section {
    margin-bottom: 20px;
}
.sidebar-label {
    font-size: 10px;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid #2e2e2e;
}

/* ── prevent horizontal scroll ── */
html, body {
    overflow-x: hidden !important;
    width: 100% !important;
}
.gradio-container .gr-row,
.gradio-container > div {
    max-width: 100% !important;
    overflow-x: hidden !important;
}
/* ── MAIN CONTENT ── */
#main-content {
    margin-left: 270px;
    padding: 20px 16px;
    min-height: 100vh;
    background: #141414;
    max-width: calc(100% - 270px);
    overflow-x: hidden;
    box-sizing: border-box;
}

/* ── TOP HEADER BAR ── */
#top-header {
    background: linear-gradient(135deg,#1e1e1e,#111);
    border: 1px solid #2e2e2e;
    border-radius: 12px;
    padding: 20px 26px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
#top-header h1 {
    margin: 0;
    font-size: 20px;
    font-weight: 700;
    color: #fff;
}
#top-header p {
    margin: 5px 0 0;
    color: #9ca3af;
    font-size: 12px;
}

/* ── KPI HEADING ── */
.section-heading {
    font-size: 12px;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 20px 0 10px;
    padding-left: 10px;
    border-left: 3px solid #3b82f6;
}

/* ── TABS ── */
button[role="tab"],
.tab-nav button {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #9ca3af !important;
    background: transparent !important;
    border: none !important;
    padding: 10px 18px !important;
}
button[role="tab"]:hover,
.tab-nav button:hover {
    color: #ffffff !important;
    background: #2a2a2a !important;
    border-radius: 6px !important;
}
button[role="tab"][aria-selected="true"],
.tab-nav button.selected {
    color: #3b82f6 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #3b82f6 !important;
    background: transparent !important;
}

/* ── CHART CARDS ── */
.gradio-plot {
    background: #1e1e1e !important;
    border-radius: 10px !important;
    border: 1px solid #2e2e2e !important;
    padding: 12px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3) !important;
}
.gradio-plot > .label-wrap { display: none !important; }

/* ── SIDEBAR INPUTS ── */
.gradio-container label span { color: #d1d5db !important; font-size: 12px !important; }
.gradio-container input[type=text],
.gradio-container textarea {
    background: #2a2a2a !important;
    border: 1px solid #374151 !important;
    color: #fff !important;
    border-radius: 7px !important;
    font-size: 13px !important;
}
.gradio-container .wrap { background: #2a2a2a !important; border-color: #374151 !important; }
.gradio-container .token { background: #1d4ed8 !important; color: #fff !important; }
input[type=checkbox]:checked { accent-color: #3b82f6; }
input[type=range] { accent-color: #3b82f6; }
input[type=number] { background: #2a2a2a !important; border: 1px solid #374151 !important; color: #fff !important; border-radius: 6px !important; }

/* ── remove default boxes ── */
.gradio-container .gr-box,
.gradio-container .gr-form,
div.block, .padded, .gap {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* ── BUTTONS ── */
.btn-apply {
    background: #1d4ed8 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    width: 100% !important;
    margin-bottom: 6px !important;
}
.btn-reset {
    background: #2a2a2a !important;
    color: #d1d5db !important;
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    width: 100% !important;
}

/* ── record badge ── */
.gradio-markdown p { color: #6b7280 !important; font-size: 12px !important; }


/* ── remove horizontal scrollbar ── */
html { overflow-x: hidden !important; }
body { overflow-x: hidden !important; }
.gradio-container { overflow-x: hidden !important; max-width: 100vw !important; }
.gr-row { overflow-x: hidden !important; flex-wrap: wrap !important; }
.gradio-plot { max-width: 100% !important; overflow: hidden !important; }
.gradio-plot canvas, .gradio-plot img { max-width: 100% !important; }
.tabs { max-width: 100% !important; overflow-x: hidden !important; }
.tab-content { max-width: 100% !important; overflow-x: hidden !important; }

footer { display: none !important; }
"""


with gr.Blocks(
    theme=gr.themes.Base(primary_hue="blue"),
    css=CSS,
    title="AEP Energy Dashboard"
) as demo:

    with gr.Row(elem_id="layout-root"):

        # ══════════════════════════════
        #  LEFT SIDEBAR
        # ══════════════════════════════
        with gr.Column(scale=0, min_width=270, elem_id="sidebar"):

            gr.HTML("""
            <div id="sidebar-logo">
              <h2>⚡ AEP Dashboard</h2>
              <p>Energy Analytics  •  2004–2018</p>
            </div>
            <div id="sidebar-content">
            """)

            gr.HTML('<div class="sidebar-label">Date Range</div>')
            year_start = gr.Slider(YEAR_MIN, YEAR_MAX, value=YEAR_MIN,
                                   step=1, label="Start Year")
            year_end   = gr.Slider(YEAR_MIN, YEAR_MAX, value=YEAR_MAX,
                                   step=1, label="End Year")

            gr.HTML('<div class="sidebar-label" style="margin-top:16px;">Season</div>')
            seasons_cb = gr.CheckboxGroup(ALL_SEASONS, value=ALL_SEASONS,
                                          label="", show_label=False)

            gr.HTML('<div class="sidebar-label" style="margin-top:16px;">Day Type</div>')
            day_type_cb = gr.CheckboxGroup(["Weekday","Weekend"],
                                           value=["Weekday","Weekend"],
                                           label="", show_label=False)

            gr.HTML('<div class="sidebar-label" style="margin-top:16px;">Months</div>')
            months_ms = gr.Dropdown(
                choices=[MONTH_NAMES[m] for m in ALL_MONTHS],
                value=[MONTH_NAMES[m] for m in ALL_MONTHS],
                multiselect=True, label="", show_label=False)

            gr.HTML('<div class="sidebar-label" style="margin-top:16px;">Load Range (MW)</div>')
            mw_low  = gr.Slider(MW_MIN, MW_MAX, value=MW_MIN,
                                step=100, label="Min MW")
            mw_high = gr.Slider(MW_MIN, MW_MAX, value=MW_MAX,
                                step=100, label="Max MW")

            gr.HTML('<div class="sidebar-label" style="margin-top:16px;">Search</div>')
            keyword_box = gr.Textbox(placeholder="e.g. 2010-07 or 2015",
                                     label="", show_label=False)

            gr.HTML('<div style="margin-top:20px;">')
            apply_btn = gr.Button("Apply Filters", variant="primary",
                                  elem_classes=["btn-apply"])
            reset_btn = gr.Button("Reset All", variant="secondary",
                                  elem_classes=["btn-reset"])
            gr.HTML('</div></div>')

        # ══════════════════════════════
        #  MAIN CONTENT
        # ══════════════════════════════
        with gr.Column(scale=1, elem_id="main-content"):

            gr.HTML("""
            <div id="top-header">
              <h1>AEP Hourly Energy Consumption &mdash; Analytics Dashboard</h1>
              <p>American Electric Power grid load data &nbsp;&bull;&nbsp;
                 2004 &ndash; 2018 &nbsp;&bull;&nbsp;
                 121,273 hourly records &nbsp;&bull;&nbsp;
                 Exploratory Data Analysis</p>
            </div>""")

            gr.HTML('<div class="section-heading">Key Performance Indicators</div>')
            kpi_display  = gr.HTML()
            record_count = gr.Markdown()

            gr.HTML('<div class="section-heading" style="margin-top:24px;">Visualizations</div>')

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
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False
    )