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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@600&display=swap');

*, html, body, .gradio-container {
    font-family: "Inter", "Segoe UI", sans-serif !important;
    box-sizing: border-box !important;
}
*:focus, *:focus-visible { outline: none !important; box-shadow: none !important; }
html, body { overflow-x: hidden !important; width: 100% !important; }
body, .gradio-container {
    background: #051424 !important;
    background-image:
        radial-gradient(ellipse at 10% 0%, rgba(124,58,237,0.2) 0%, transparent 40%),
        radial-gradient(ellipse at 90% 100%, rgba(99,102,241,0.12) 0%, transparent 40%) !important;
    color: #d4e4fa !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow-x: hidden !important;
}
.gradio-container > .main > .wrap { max-width: 100% !important; padding: 0 20px !important; }

#dash-header {
    background: linear-gradient(135deg, rgba(124,58,237,0.2) 0%, rgba(5,20,36,0.97) 50%, rgba(99,102,241,0.12) 100%) !important;
    border: 1px solid rgba(210,187,255,0.2) !important;
    border-radius: 20px !important;
    padding: 28px 36px !important;
    margin-bottom: 20px !important;
    position: relative !important;
    overflow: hidden !important;
    box-shadow: 0 0 80px rgba(124,58,237,0.12), 0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.07) !important;
}
#dash-header::before {
    content: "" !important; position: absolute !important;
    top: -80px !important; right: -60px !important;
    width: 280px !important; height: 280px !important;
    background: radial-gradient(circle, rgba(124,58,237,0.2) 0%, transparent 65%) !important;
    border-radius: 50% !important; pointer-events: none !important;
}
#dash-header h1 {
    margin: 0 !important; font-size: 24px !important; font-weight: 700 !important;
    background: linear-gradient(135deg, #ffffff 0%, #d2bbff 60%, #a5b4fc 100%) !important;
    -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; background-clip: text !important;
}
#dash-header p { margin: 8px 0 0 !important; color: #94a3b8 !important; font-size: 13px !important; }

.filter-panel > div:first-child {
    background: rgba(30,30,46,0.5) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 20px !important; padding: 24px 24px !important;
    box-shadow: 0 4px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    width: 100% !important;
}
.filter-panel .label-wrap span { color: #d4e4fa !important; font-weight: 600 !important; }

.section-title {
    font-family: "JetBrains Mono", monospace !important;
    font-size: 11px !important; font-weight: 600 !important;
    color: #d2bbff !important; text-transform: uppercase !important;
    letter-spacing: 0.05em !important; margin: 0 0 14px 0 !important;
    padding-bottom: 8px !important; border-bottom: 1px solid rgba(210,187,255,0.15) !important;
}

.gradio-container .block, .gradio-container .gr-box,
.gradio-container .gr-form, .gradio-container fieldset,
div.block, .padded, .gap, .svelte-1f354aw, .svelte-90oupt,
.svelte-1hnfib2, .svelte-1gfkn6u,
.gradio-container > div > div > div > div {
    background: transparent !important; border: none !important; box-shadow: none !important;
}
.filter-panel > div:first-child {
    background: rgba(30,30,46,0.5) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 20px !important; padding: 24px 24px !important;
}

input[type=range] { accent-color: #7c3aed !important; width: 100% !important; }
input[type=range]::-webkit-slider-thumb { -webkit-appearance: none !important; height: 18px !important; width: 18px !important; border-radius: 50% !important; background: #ffffff !important; cursor: pointer !important; box-shadow: 0 0 10px rgba(210,187,255,0.5) !important; }
input[type=range]::-webkit-slider-runnable-track { height: 4px !important; background: rgba(255,255,255,0.1) !important; border-radius: 2px !important; }
input[type=number] { background: #122131 !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #d2bbff !important; border-radius: 6px !important; min-width: 72px !important; font-size: 13px !important; padding: 4px 8px !important; font-family: "JetBrains Mono", monospace !important; }
input[type=checkbox]:checked { accent-color: #7c3aed !important; }
.gradio-container label span { color: #ccc3d8 !important; font-weight: 500 !important; }
.gradio-container input[type=text], .gradio-container textarea { background: rgba(1,15,31,0.5) !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #d4e4fa !important; border-radius: 10px !important; }
.gradio-container .wrap, .gradio-container .multiselect { background: rgba(5,20,36,0.5) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 10px !important; }
.gradio-container .token { background: #7c3aed !important; color: #ede0ff !important; border-radius: 6px !important; font-size: 12px !important; }

.btn-apply { background: #7c3aed !important; color: #ede0ff !important; border: none !important; border-radius: 14px !important; font-weight: 700 !important; font-size: 14px !important; box-shadow: 0 0 20px rgba(124,58,237,0.4), 0 4px 15px rgba(0,0,0,0.3) !important; }
.btn-apply:hover { background: #6d28d9 !important; box-shadow: 0 0 30px rgba(124,58,237,0.6) !important; }
.btn-reset { background: rgba(255,255,255,0.04) !important; color: #958da1 !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 14px !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; }

#kpi-heading, #viz-heading {
    font-size: 18px !important; font-weight: 700 !important;
    color: #d2bbff !important; letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
    margin: 24px 0 14px !important; padding-left: 14px !important;
    border-left: 4px solid #7c3aed !important;
}

.tabs { background: transparent !important; border-bottom: 1px solid rgba(255,255,255,0.07) !important; margin-bottom: 16px !important; overflow-x: hidden !important; }
button[role="tab"], .tab-nav button { font-weight: 500 !important; color: #4a4455 !important; background: transparent !important; border: none !important; padding: 12px 20px !important; white-space: nowrap !important; outline: none !important; font-size: 14px !important; }
button[role="tab"] svg, .tab-nav button svg { display: none !important; }
button[role="tab"]:hover, .tab-nav button:hover { color: #d2bbff !important; background: rgba(124,58,237,0.08) !important; border-radius: 8px 8px 0 0 !important; }
button[role="tab"][aria-selected="true"], .tab-nav button.selected { color: #d2bbff !important; font-weight: 600 !important; border-bottom: 2px solid #7c3aed !important; }

.gradio-plot, .gr-plot {
    background: rgba(18,33,49,0.7) !important; backdrop-filter: blur(20px) !important;
    border-radius: 20px !important; border: 1px solid rgba(255,255,255,0.07) !important;
    padding: 20px !important; box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    max-width: 100% !important; overflow: hidden !important;
    transition: border 0.3s, box-shadow 0.3s, transform 0.2s !important;
}
.gradio-plot:hover, .gr-plot:hover { border: 1px solid rgba(124,58,237,0.35) !important; box-shadow: 0 16px 48px rgba(124,58,237,0.15) !important; transform: translateY(-2px) !important; }
.gradio-plot > .label-wrap, .gr-plot > .label-wrap, .gradio-plot .icon-buttons, .gradio-plot button { display: none !important; }

.gradio-container .gr-row, .gradio-container > div { max-width: 100% !important; overflow-x: hidden !important; }
.gradio-markdown p { color: #4a4455 !important; }



/* ── restore glass tiles per filter column ── */
.filter-panel .gr-row > div > div {
    background: rgba(18,33,49,0.6) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    padding: 16px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
}

/* ── remove small nested boxes inside tiles ── */
.filter-panel .gr-row > div > div > div,
.filter-panel .gr-row > div > div .block,
.filter-panel .gr-row > div > div .gap,
.filter-panel .gr-row > div > div fieldset {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

/* ── section titles bigger ── */
.section-title {
    font-size: 13px !important;
    font-weight: 700 !important;
    color: #d2bbff !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    margin: 0 0 12px 0 !important;
    padding-bottom: 8px !important;
    border-bottom: 1px solid rgba(210,187,255,0.2) !important;
}


/* ── restore big glass tiles ── */
.filter-panel > div:first-child {
    background: rgba(30,30,46,0.5) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 20px !important;
    padding: 24px 24px !important;
    box-shadow: 0 4px 30px rgba(0,0,0,0.4) !important;
}

/* ── remove ONLY the small inner dark boxes ── */
.filter-panel .wrap,
.filter-panel .wrap.svelte-1hnfib2,
.filter-panel .gap,
.filter-panel .padded {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

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