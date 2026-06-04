# ⚡ AEP Hourly Energy Consumption Dashboard

**Course:** Exploratory Data Analysis  
**Instructor:** Ali Hassan Sherazi  
**Dataset:** `AEP_hourly.csv` (121,273 hourly records, 2004–2018)  
**Framework:** Gradio + Pandas + Matplotlib + Seaborn

---

## 📌 Project Overview

This dashboard provides an interactive, professional-grade analysis of the
American Electric Power (AEP) grid hourly load data. It features **10 required
chart types**, **6 interactive filters**, and **KPI summary cards** — all wired
together so every filter instantly updates every chart.

---

## 🗂️ Project Structure

```
dashboard_project/
├── data/
│   └── AEP_hourly.csv          ← EXACT original filename (do not rename)
├── notebooks/
│   └── analysis.ipynb          ← Exploratory Data Analysis notebook
├── app.py                      ← Main Gradio dashboard (entry point)
├── charts.py                   ← All 10+ chart functions
├── filters.py                  ← Data loading, cleaning, filter logic
├── requirements.txt            ← Python dependencies
└── README.md                   ← This file
```

---

## ⚙️ How to Install & Run

### Step 1 — Clone / unzip the project
```bash
unzip dashboard_project.zip
cd dashboard_project
```

### Step 2 — Create a virtual environment (recommended)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run the dashboard
```bash
python app.py
```

Then open **http://127.0.0.1:7860** in your browser.

---

## 📊 Charts Included

| # | Chart Type   | Insight Shown                          |
|---|-------------|----------------------------------------|
| 1 | Pie Chart    | Energy share by Season                 |
| 2 | Histogram    | Distribution of hourly MW values       |
| 3 | Line Chart   | Monthly average trend over years       |
| 4 | Bar Chart    | Average consumption by hour of day     |
| 5 | Scatter Plot | Hour vs MW coloured by season          |
| 6 | Box Plot     | Spread & outliers by month             |
| 7 | Heatmap      | Hour × Month average energy matrix     |
| 8 | Area Chart   | Daily rolling 7 & 30-day averages      |
| 9 | Count Plot   | Record count by day of week            |
|10 | Violin Plot  | MW distribution shape by season        |
| ★ | Bonus Bar    | Year-over-year average comparison      |

---

## 🔧 Filters Available

| Filter              | Type              | Description                        |
|--------------------|-------------------|------------------------------------|
| Start / End Year   | Range Slider      | Select any sub-period of the data  |
| Season             | Checkbox Group    | Filter by Winter/Spring/Summer/Autumn |
| Month              | Multi-Select Dropdown | Pick specific months            |
| Min / Max MW       | Numerical Slider  | Focus on a consumption range       |
| Day Type           | Checkbox Group    | Weekday vs Weekend                 |
| Text Search        | Textbox           | Search datetime strings (e.g. "2010-07") |
| Reset Button       | Button            | Restore all filters to defaults    |

---

## 💡 Key Insights from the Data

- **Peak loads** consistently occur during **summer afternoons** (June–August,
  hours 14:00–18:00), driven by air conditioning demand.
- **Lowest consumption** happens in **spring nights** (3:00–5:00 AM).
- There is a visible **dip post-2008** (financial crisis, reduced industrial activity).
- **Weekdays** consume on average ~8% more than weekends.
- The **heatmap** reveals two daily peaks: a morning ramp (~7–9 AM) and a
  larger evening peak (~17–20 PM).

---

## 📦 Dependencies

```
gradio>=4.0.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

---

*Submission Date: 05-June-2026 | Individual Project*
