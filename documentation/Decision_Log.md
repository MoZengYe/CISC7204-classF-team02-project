# Decision Log

Project: **Macao Visitor Flows: Long-run Economic Coupling and Monthly Recovery Dynamics, 1995–2026**

Retrieval date: **9 November 2026**

## 1. Analytical window

- The DSEC monthly API returned observations through September 2026, but the project brief
  specifies a monthly window ending in July 2026.
- The monthly analysis is therefore frozen at **January 2008–July 2026**, giving exactly
  **223 monthly observations**.
- August and September 2026 are excluded from all charts, summary statistics and tests. They
  remain available in the untouched raw JSON.

## 2. Missing annual values

- World Bank `ST.INT.ARVL` has observed annual arrivals only through **2020**.
- Values for 2021–2025 are retained as missing. No linear interpolation, forward fill or
  replacement with DSEC totals is used.
- The annual regression uses only years where both World Bank arrivals and GDP per capita are
  present: **1995–2020, n = 26**.
- GDP per capita extends through 2025 and is plotted through 2025 in Figure 1, but it is not
  used to manufacture missing visitor observations.

## 3. Regression specification

- Primary model: ordinary least squares of annual arrivals (millions) on GDP per capita
  (current US$).
- Sensitivity model: the same specification excluding 2020, yielding **n = 25**.
- R², RMSE, MAE, Pearson correlation, slope and intercept are reported.
- The model is interpreted as an association. No causal or policy-effect claim is made.
- The intercept is not interpreted as a meaningful zero-GDP prediction because GDP values near
  zero lie outside the observed range.

## 4. Phase definitions

- **Growth and Baseline:** 2008–2019 for monthly data; 1995–2019 for annual data.
- **Disruption:** 2020–2022.
- **Recovery:** 2023–July 2026 for monthly data; 2023–2025 for complete annual data.
- Phases are descriptive visual groupings, not causal treatment assignments.

## 5. Year-over-year growth

- YoY = (current month / same month previous year − 1) × 100.
- The first 12 months are `NaN` because the prior-year same-month denominator is unavailable.
- Growth rates based on very low pandemic denominators are not treated as comparable to normal
  growth rates.
- Supplementary Figure S3 clips the display at −150% to +300% and marks the 11 observations above
  +300% with triangles. The maximum, July 2023 at +28,177%, remains visible in the annotation.
  This is a display decision only; the processed `yoy_pct` values are not clipped.

## 6. Recovery index

- Recovery Index = current month / **same calendar month in 2019** × 100.
- A value of 100 means equal visitor volume, not full economic recovery.
- The index is computed for 2020 onward. Values before 2019 are set to `NaN` because they are not
  recovery observations.
- 2026 is limited to January–July. No August–December 2026 values are generated.

## 7. Seasonal decomposition

- Method: `statsmodels.tsa.seasonal.seasonal_decompose`.
- Model: additive; period = 12.
- The input is a complete monthly grid with no missing months.
- The full-series trend loses six observations at each end because of the centred 12-month moving
  average. This is expected and is documented in the notebook.
- The seasonal component is compared with a separate 2008–2019 decomposition. The pandemic period
  makes a stable additive seasonal assumption descriptive rather than structural.

## 8. HHI definition and scale

- HHI = Σ(market share²), with shares expressed as decimals.
- The primary scale is **0–1**. The equivalent 0–10,000 scale is obtained by multiplying by
  10,000.
- The source-market file contains the top eight named markets plus an `Other (residual)` group.
- Because the residual is not one market, the reported HHI is a **lower bound** on a fully
  disaggregated market-level HHI.
- Values: 2024 = 0.5357 (5,357); 2025 = 0.5594 (5,594).

## 9. Entry-point geography

- The project brief requests a checkpoint choropleth, but checkpoints are point facilities rather
  than administrative polygons.
- The core Figure 8 is therefore a **proportional-symbol map** on a real Macao statistics-zone
  boundary, plus a checkpoint-volume bar panel.
- The required filename `Figure_08_Entry_Point_Choropleth.png` is retained for deliverable
  compatibility; the chart subtitle and report explain that the cartographic form is proportional
  symbols.
- A true polygon choropleth is provided as Supplementary Figure S7 for the 2026 district
  person-times.
- MGTO January–December 2025 visitor arrivals by checkpoint are used. The DSEC border-crossing
  table is not substituted because it counts all persons, not visitors.

## 10. Source markets and composition

- The latest complete source-market year is 2025.
- Top eight markets are ranked by 2025 arrivals. All remaining origins are collapsed into the
  residual category.
- The waffle uses a 20 × 10 grid (200 blocks). Each block is 0.5 percentage points. A small
  category may receive one minimum-sized block so that it remains visible; exact percentages are
  printed in the legend.

## 11. District data

- The DSEC district file covers January–September 2026; the analysis uses January–July 2026 to
  match the frozen monthly window.
- District values are **visitor person-times**, not unique visitors. One person may be counted in
  more than one district or period.
- District names are matched to the GeoJSON using `DISTRICT_PT` with `&` normalised to `e` and
  case-folding. The Portuguese COTAI name matches `Zona de aterro entre Taipa e Coloane`.
- Two GeoJSON zones without a matching 2026 observation are shown in grey.

## 12. Cartographic data

- Base boundaries come from `ngsiolei/macau-map-data`, assembled into a 26-feature
  `macau_stats_zones.geojson` in EPSG:4326.
- Checkpoint point coordinates were queried from OpenStreetMap/Nominatim and checked against the
  visual boundary. The Macao-side Hengqin Port and HZMB port coordinates are used where the public
  landmark search returned a Zhuhai-side location.
- The heliport coordinate is approximate.
- Map axes include a small buffer beyond the Macao boundary so that Hengqin Port and HZMB can be
  shown without clipping.

## 13. Reproducibility and file handling

- Raw files are never modified. All transformations write to `data/processed/`.
- The Notebook reads the frozen raw files and regenerates all processed CSVs and figures.
- Static figures are exported at 300 DPI. The entry-point map also has a self-contained interactive
  HTML version.
- The Notebook was executed from a clean `cisc7204` kernel with no errors.
- All figures were visually inspected; overlapping annotations in Figures 1, 3 and 5 were corrected
  before final execution.

## 14. Unavailable or non-comparable data

- No supplied `tmp8017` XLS file was present in the project folder. The official DSEC API response
  was used instead and preserved as raw JSON.
- A monthly checkpoint series is not available from the collected public files; the checkpoint
  analysis is therefore annual 2025.
- Monthly source-market data were not available in the downloaded files; the market composition
  analysis is annual 2024/2025.
- No tourism revenue, visitor expenditure or resident-impact series was available, so no claim is
  made about economic welfare or complete recovery.
