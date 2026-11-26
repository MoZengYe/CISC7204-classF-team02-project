# Macao Visitor Flows

**Long-run Economic Coupling and Monthly Recovery Dynamics, 1995–2026**

CISC7204 Data Science and Data Visualization — Class F Team 02

**Team members:** WANG HAOYU (MC644384), MoZengYe (MC659583), Gao Sihan (MC660725),
HE MENGLEI (MC660743), WANG HE (MC660942), HE SHIHAO (MC662189)

## Overview

This project analyses official Macao visitor-flow data with four goals:

1. estimate the long-run association between annual visitor arrivals and GDP per capita;
2. measure monthly seasonality and the 2020–2022 disruption;
3. compare 2023–July 2026 visitor volume with the same months in 2019;
4. examine source-market, entry-checkpoint and district concentration.

The submission includes a fully executed research notebook, six processed CSV tables, eight core
figures, seven supplementary figures, an interactive entry-point map, a Dash dashboard and complete
data documentation.

The formatted submission report is `reports/Project_Report.docx`. It contains 15 embedded figures,
9 tables, a contents page, captions, source notes and a reference list.

## Key results

- Annual arrivals fell from **39,406,181** in 2019 to **5,896,848** in 2020 (**−85.03%**), then rose
  to **40,069,360** in 2025 (**+14.72%** year over year).
- January–July 2026 recorded **24,486,664** arrivals, or **102.82%** of the same 2019 period.
- The 1995–2020 annual OLS fit has **R² = 0.817 (n = 26)**; excluding 2020 gives
  **R² = 0.860 (n = 25)**. These are associations, not causal effects.
- The additive seasonal decomposition peaks in **August** and has troughs in **June** and
  **September**.
- 2025 HHI is **0.5594 on a 0–1 scale (5,594 on the 0–10,000 scale)**. Mainland China supplied
  **72.42%** of 2025 arrivals.
- Land checkpoints handled **82.6%** of 2025 visitor arrivals; Border Gate accounted for **41.6%**.

## Directory layout

```text
project/
├── data/
│   ├── raw/                  # untouched official downloads
│   ├── processed/            # analysis-ready CSVs
│   └── external/             # GeoJSON and coordinate data
├── notebooks/
│   ├── Macao_Visitor_Flows_Analysis.ipynb
│   └── executed_analysis.ipynb
├── figures/
│   ├── core/                 # eight required 300 DPI figures + interactive map
│   └── supplementary/        # seven supporting 300 DPI figures
├── dashboard/
│   ├── app.py
│   └── assets/style.css
├── reports/
│   ├── Project_Report.docx   # submission-ready report, 22 pages
│   └── Project_Report.md     # editable text source
├── documentation/
│   ├── Data_Dictionary.csv
│   ├── Data_Source_Register.csv
│   └── Decision_Log.md
├── .vscode/settings.json
├── requirements.txt
└── README.md
```

## Environment

The verified environment is:

- macOS on Apple Silicon;
- Python **3.13.18**;
- the course virtual environment
  `/Users/wangkele/Documents/课程/研一上/数据可视化/.venv-cisc7204`;
- the project-level `.vscode/settings.json` selects that interpreter automatically.
- pandas 3.1, NumPy 2.5, statsmodels 0.15, scikit-learn 1.9, Matplotlib 3.11, Seaborn 0.13,
  Plotly 7.1, Dash 4.5, GeoPandas 1.2 and PyWaffle 1.2.

No GPU or remote compute server is required. The project uses only small tabular data and CPU-based
statistical analysis, rendering and a local Dash server.

### Install dependencies

From the project root (the directory containing this README):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If using the existing course environment:

```bash
/Users/wangkele/Documents/课程/研一上/数据可视化/.venv-cisc7204/bin/python -m pip install -r requirements.txt
```

## Run the notebook

The submitted notebook is already executed and contains all tables and figures. To re-execute it
from a clean kernel, run the following from the project root:

```bash
cd "/Users/wangkele/Documents/课程/研一上/数据可视化/project-6人/project"
MPLCONFIGDIR=/tmp/mplconfig \
  /Users/wangkele/Documents/课程/研一上/数据可视化/.venv-cisc7204/bin/jupyter \
  nbconvert --to notebook --execute notebooks/Macao_Visitor_Flows_Analysis.ipynb \
  --output executed_analysis.ipynb --ExecutePreprocessor.timeout=1200
```

The notebook locates the project root by walking up from the current directory until it finds
`data/raw/` and `notebooks/`. It reads the preserved raw files, rewrites all processed CSVs and
regenerates every figure.

## Run the dashboard

```bash
cd "/Users/wangkele/Documents/课程/研一上/数据可视化/project-6人/project"
/Users/wangkele/Documents/课程/研一上/数据可视化/.venv-cisc7204/bin/python dashboard/app.py
```

Open <http://127.0.0.1:8050>. The app reads only `data/processed/*.csv` and does not require
network access.

Dashboard features:

- KPI cards for total arrivals, average monthly arrivals, latest-month YoY, latest recovery index
  and number of source markets;
- year-range, month, phase and source-market filters;
- monthly trend, recovery index, source-market composition, year × month heatmap and
  visitor–GDP relationship charts.

## Data provenance

Retrieved **9 November 2026**:

- DSEC monthly visitor arrivals and hotel guests via data.gov.mo API;
- World Bank `ST.INT.ARVL` and `NY.GDP.PCAP.CD` for Macao SAR;
- DSEC 2024 and 2025 annual visitor-arrival releases;
- MGTO Tourism Highlights January–December 2025;
- DSEC district visitor data for 2026;
- `ngsiolei/macau-map-data` statistics-zone GeoJSON;
- OpenStreetMap/Nominatim checkpoint coordinates.

See `documentation/Data_Source_Register.csv`, `documentation/Data_Dictionary.csv` and
`documentation/Decision_Log.md` for detailed definitions, transformations and limitations.

## Important limitations

- World Bank annual arrivals are missing for **2021–2025** and are never interpolated.
- The annual regression uses the actual overlap, **1995–2020**, not synthetic later observations.
- DSEC monthly and World Bank annual arrival definitions are not identical.
- The 2026 monthly series ends in **July**; August–December are not generated.
- Recovery index 100 means equal visitor **volume**, not complete economic recovery.
- District data are **visitor person-times**, not unique visitors.
- The source-market HHI is a lower bound because small origins are grouped as “Other”.
- The checkpoint map uses proportional point symbols because checkpoints are facilities, not
  administrative polygons. A district choropleth is supplied as Supplementary Figure S7.
- No supplied `tmp8017` XLS was present; the official DSEC API response is used and preserved.

## Verification completed

- Notebook: 100 cells (31 code cells), clean-kernel execution completed with **0 errors**;
  15 figures embedded in the executed notebook.
- Monthly data: **223 rows**, **2008-01 to 2026-07**, no duplicate or missing months, no
  non-positive values.
- Regression: **n = 26**, years **1995–2020**, R² **0.817062**.
- Figures: **8 core + 7 supplementary** PNGs, each with **300 DPI** metadata.
- Dashboard: HTTP 200 for `/` and `/_dash-layout`; callback returned five KPI cards and five
  Plotly figures; default total arrivals **503,072,493** and average monthly arrivals
  **2,255,930**.
