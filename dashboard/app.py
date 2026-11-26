"""Interactive Dash dashboard for the Macao visitor-flow project."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA = PROJECT_ROOT / "data" / "processed"

PHASE_COLORS = {
    "Growth and Baseline": "#4C72B0",
    "Disruption": "#C44E52",
    "Recovery": "#55A868",
}
MARKET_COLORS = [
    "#355C7D",
    "#6C5B7B",
    "#C06C84",
    "#F8B195",
    "#4E937A",
    "#D9A441",
    "#8C6D46",
    "#B56576",
    "#9A9A9A",
]
NEUTRAL = "#6E6E6E"
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    monthly = pd.read_csv(DATA / "monthly_visitor_arrivals.csv", parse_dates=["month"])
    annual = pd.read_csv(DATA / "annual_tourism_gdp.csv")
    source = pd.read_csv(DATA / "source_markets_2024_2025.csv")
    hotel = pd.read_csv(DATA / "monthly_hotel_guests.csv", parse_dates=["month"])
    monthly["month_label"] = monthly["month"].dt.strftime("%Y-%m")
    monthly["month_name"] = monthly["month_number"].map(lambda value: MONTH_NAMES[value - 1])
    return monthly, annual, source, hotel


MONTHLY, ANNUAL, SOURCE, HOTEL = load_data()


def base_layout(fig: go.Figure, height: int = 350) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=44, r=24, t=54, b=44),
        font=dict(family="Arial, sans-serif", color="#303030", size=12),
        title_font=dict(size=16, color="#202020"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#E8E8E8", zeroline=False)
    return fig


def empty_figure(title: str, message: str = "No observations match the current filters.") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=14, color=NEUTRAL),
    )
    fig.update_layout(
        template="plotly_white",
        height=350,
        title=title,
        margin=dict(l=44, r=24, t=54, b=44),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def filter_monthly(year_range: list[int], months: list[int], phase: str) -> pd.DataFrame:
    frame = MONTHLY.loc[MONTHLY["year"].between(year_range[0], year_range[1])].copy()
    if months:
        frame = frame.loc[frame["month_number"].isin(months)]
    else:
        return frame.iloc[0:0]
    if phase != "All phases":
        frame = frame.loc[frame["phase"].eq(phase)]
    return frame.sort_values("month")


def kpi_card(label: str, value: str, detail: str, accent: str) -> html.Div:
    return html.Div(
        [
            html.Div(label, className="kpi-label"),
            html.Div(value, className="kpi-value", style={"color": accent}),
            html.Div(detail, className="kpi-detail"),
        ],
        className="kpi-card",
    )


def kpi_cards(frame: pd.DataFrame) -> list[html.Div]:
    total = frame["visitor_arrivals"].sum() if len(frame) else 0
    average = frame["visitor_arrivals"].mean() if len(frame) else np.nan
    latest = frame.sort_values("month").iloc[-1] if len(frame) else None
    yoy = latest["yoy_pct"] if latest is not None else np.nan
    recovery = latest["recovery_index"] if latest is not None else np.nan
    latest_label = f"{latest['month']:%Y-%m}" if latest is not None else "No data"
    yoy_text = f"{yoy:+.2f}%" if pd.notna(yoy) else "n/a"
    recovery_text = f"{recovery:.1f}" if pd.notna(recovery) else "n/a"
    return [
        kpi_card("Total visitor arrivals", f"{total:,.0f}", f"{len(frame)} selected months", "#355C7D"),
        kpi_card("Average monthly arrivals", f"{average:,.0f}" if pd.notna(average) else "n/a", "Selected monthly mean", "#4E937A"),
        kpi_card("Latest-month YoY", yoy_text, latest_label, "#DD8452"),
        kpi_card("Latest recovery index", recovery_text, "2019 same-month volume = 100", "#6C5B7B"),
        kpi_card("Source markets", f"{len(SOURCE)}", "Top 8 plus Other residual", "#C06C84"),
    ]


def monthly_figure(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return empty_figure("Monthly visitor trend")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frame["month"],
            y=frame["visitor_arrivals"] / 1e6,
            mode="lines",
            name="Monthly arrivals",
            line=dict(color="#4C72B0", width=2),
            hovertemplate="%{x|%Y-%m}<br>%{y:.3f} million arrivals<extra></extra>",
        )
    )
    fig.add_vrect(
        x0="2020-01-01",
        x1="2022-12-31",
        fillcolor=PHASE_COLORS["Disruption"],
        opacity=0.08,
        line_width=0,
        layer="below",
    )
    fig.add_vline(x="2023-01-01", line_dash="dash", line_color=PHASE_COLORS["Recovery"], line_width=1)
    fig.update_layout(title="Monthly visitor arrivals", xaxis_title="Month", yaxis_title="Visitor arrivals (millions)")
    fig.update_yaxes(rangemode="tozero")
    return base_layout(fig, height=360)


def recovery_figure(frame: pd.DataFrame) -> go.Figure:
    recovery = frame.loc[frame["year"] >= 2023].copy()
    if recovery.empty:
        return empty_figure("Recovery index")
    colors = {2023: "#DD8452", 2024: "#8C8C8C", 2025: "#4C72B0", 2026: "#55A868"}
    fig = go.Figure()
    for year in sorted(recovery["year"].unique()):
        sub = recovery.loc[recovery["year"].eq(year)].sort_values("month_number")
        fig.add_trace(
            go.Scatter(
                x=sub["month_number"],
                y=sub["recovery_index"],
                mode="lines+markers",
                name=str(year),
                line=dict(color=colors.get(year, "#333333"), width=2),
                marker=dict(size=6),
                customdata=sub["month_name"],
                hovertemplate="%{customdata} " + str(year) + "<br>Index: %{y:.1f}<extra></extra>",
            )
        )
    fig.add_hline(y=100, line_dash="dash", line_color="#333333", line_width=1)
    fig.add_annotation(
        x=0.02,
        y=102,
        text="2019 volume = 100",
        showarrow=False,
        font=dict(size=10, color="#333333"),
    )
    fig.update_layout(
        title="Recovery relative to the same 2019 month",
        xaxis=dict(title="Calendar month", tickmode="array", tickvals=list(range(1, 13)), ticktext=MONTH_NAMES),
        yaxis_title="Recovery index",
    )
    return base_layout(fig, height=360)


def source_figure(selected_market: str) -> go.Figure:
    frame = SOURCE.sort_values("share_2025_pct", ascending=True).copy()
    colors = [
        "#355C7D" if selected_market in ("All markets", row.market) else "#D0D0D0"
        for row in frame.itertuples(index=False)
    ]
    hhi = float(((SOURCE["share_2025_pct"] / 100) ** 2).sum())
    fig = go.Figure(
        go.Bar(
            x=frame["share_2025_pct"],
            y=frame["market"],
            orientation="h",
            marker_color=colors,
            text=[f"{value:.2f}%" for value in frame["share_2025_pct"]],
            textposition="outside",
            customdata=np.stack(
                [frame["arrivals_2025"], frame["yoy_pct"]],
                axis=-1,
            ),
            hovertemplate="<b>%{y}</b><br>Share: %{x:.2f}%<br>2025 arrivals: %{customdata[0]:,.0f}<br>YoY: %{customdata[1]:+.1f}%<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"2025 source-market composition · HHI {hhi:.4f}",
        xaxis_title="Share of 2025 visitor arrivals (%)",
        yaxis_title="",
        showlegend=False,
    )
    fig.update_xaxes(range=[0, max(80, frame["share_2025_pct"].max() * 1.14)])
    return base_layout(fig, height=410)


def heatmap_figure(frame: pd.DataFrame) -> go.Figure:
    if frame.empty:
        return empty_figure("Year × month heatmap")
    pivot = (
        frame.pivot_table(index="year", columns="month_number", values="visitor_arrivals", aggfunc="sum")
        .reindex(columns=range(1, 13))
        .sort_index()
        / 1e6
    )
    text = pivot.map(lambda value: "" if pd.isna(value) else f"{value:.2f}")
    fig = go.Figure(
        go.Heatmap(
            z=pivot.to_numpy(),
            x=MONTH_NAMES,
            y=[str(year) for year in pivot.index],
            colorscale="YlGnBu",
            colorbar=dict(title="Millions"),
            text=text.to_numpy(),
            texttemplate="%{text}",
            textfont=dict(size=9),
            hovertemplate="Year %{y}, %{x}<br>%{z:.3f} million arrivals<extra></extra>",
        )
    )
    fig.update_layout(title="Monthly arrivals heatmap", xaxis_title="Calendar month", yaxis_title="Year")
    return base_layout(fig, height=410)


def gdp_figure(year_range: list[int]) -> go.Figure:
    frame = ANNUAL.dropna(subset=["visitor_arrivals_wb", "gdp_pc_usd"]).copy()
    frame = frame.loc[frame["year"].between(year_range[0], year_range[1])]
    if len(frame) < 3:
        return empty_figure("Annual visitor–GDP association", "The selected range has fewer than three overlap years.")
    x = frame[["gdp_pc_usd"]].to_numpy()
    y = frame["visitor_arrivals_wb"].to_numpy() / 1e6
    model = LinearRegression().fit(x, y)
    prediction = model.predict(x)
    r2 = r2_score(y, prediction)
    corr = pearsonr(frame["gdp_pc_usd"], frame["visitor_arrivals_wb"])[0]
    x_grid = np.linspace(frame["gdp_pc_usd"].min(), frame["gdp_pc_usd"].max(), 100)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frame["gdp_pc_usd"] / 1000,
            y=frame["visitor_arrivals_wb"] / 1e6,
            mode="markers",
            marker=dict(
                size=9,
                color=[
                    PHASE_COLORS["Disruption"] if year == 2020 else PHASE_COLORS["Growth and Baseline"]
                    for year in frame["year"]
                ],
                line=dict(color="white", width=1),
            ),
            customdata=frame["year"],
            hovertemplate="%{customdata}: GDP US$%{x:.1f}k<br>%{y:.2f} million arrivals<extra></extra>",
            name="Observed years",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_grid / 1000,
            y=model.predict(x_grid.reshape(-1, 1)),
            mode="lines",
            line=dict(color="#8172B2", width=2),
            name="OLS fit",
        )
    )
    fig.add_annotation(
        x=0.02,
        y=0.96,
        xref="paper",
        yref="paper",
        text=f"n={len(frame)} · R²={r2:.3f} · r={corr:.3f}",
        showarrow=False,
        align="left",
        bgcolor="white",
        bordercolor="#D0D0D0",
        borderpad=6,
    )
    fig.update_layout(
        title="Annual visitor arrivals and GDP per capita",
        xaxis_title="GDP per capita (thousand current US$)",
        yaxis_title="Visitor arrivals (millions)",
    )
    return base_layout(fig, height=410)


def build_dashboard(
    year_range: list[int],
    months: list[int],
    phase: str,
    selected_market: str,
) -> tuple[list[html.Div], go.Figure, go.Figure, go.Figure, go.Figure, go.Figure]:
    frame = filter_monthly(year_range, months, phase)
    return (
        kpi_cards(frame),
        monthly_figure(frame),
        recovery_figure(frame),
        source_figure(selected_market),
        heatmap_figure(frame),
        gdp_figure(year_range),
    )


YEAR_MIN = min(int(MONTHLY["year"].min()), int(ANNUAL["year"].min()))
YEAR_MAX = int(MONTHLY["year"].max())

app = Dash(__name__, title="Macao Visitor Flows Dashboard", suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div(
    [
        html.Header(
            [
                html.Div("CISC7204 · CLASS F TEAM 02", className="eyebrow"),
                html.H1("Macao Visitor Flows"),
                html.P(
                    "Long-run economic coupling and monthly recovery dynamics, 1995–2026",
                    className="subtitle",
                ),
            ],
            className="hero",
        ),
        html.Section(
            [
                html.Div(
                    [
                        html.Label("Year range", className="filter-label"),
                        dcc.RangeSlider(
                            id="year-range",
                            min=YEAR_MIN,
                            max=YEAR_MAX,
                            step=1,
                            value=[YEAR_MIN, YEAR_MAX],
                            marks={year: str(year) for year in [YEAR_MIN, 2010, 2015, 2020, YEAR_MAX]},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                    ],
                    className="filter-control filter-wide",
                ),
                html.Div(
                    [
                        html.Label("Months", className="filter-label"),
                        dcc.Dropdown(
                            id="month-filter",
                            options=[{"label": name, "value": index + 1} for index, name in enumerate(MONTH_NAMES)],
                            value=list(range(1, 13)),
                            multi=True,
                            clearable=False,
                        ),
                    ],
                    className="filter-control",
                ),
                html.Div(
                    [
                        html.Label("Phase", className="filter-label"),
                        dcc.Dropdown(
                            id="phase-filter",
                            options=[
                                {"label": "All phases", "value": "All phases"},
                                {"label": "Growth and Baseline", "value": "Growth and Baseline"},
                                {"label": "Disruption", "value": "Disruption"},
                                {"label": "Recovery", "value": "Recovery"},
                            ],
                            value="All phases",
                            clearable=False,
                        ),
                    ],
                    className="filter-control",
                ),
                html.Div(
                    [
                        html.Label("Source market", className="filter-label"),
                        dcc.Dropdown(
                            id="source-filter",
                            options=[{"label": "All markets", "value": "All markets"}]
                            + [{"label": value, "value": value} for value in SOURCE["market"]],
                            value="All markets",
                            clearable=False,
                        ),
                    ],
                    className="filter-control",
                ),
            ],
            className="filter-panel",
        ),
        html.Section(id="kpi-container", className="kpi-grid"),
        html.Section(
            [
                html.Div(
                    dcc.Graph(id="monthly-chart", config={"displayModeBar": False}),
                    className="chart-card chart-wide",
                ),
                html.Div(
                    dcc.Graph(id="recovery-chart", config={"displayModeBar": False}),
                    className="chart-card",
                ),
                html.Div(
                    dcc.Graph(id="source-chart", config={"displayModeBar": False}),
                    className="chart-card",
                ),
                html.Div(
                    dcc.Graph(id="heatmap-chart", config={"displayModeBar": False}),
                    className="chart-card chart-wide",
                ),
                html.Div(
                    dcc.Graph(id="gdp-chart", config={"displayModeBar": False}),
                    className="chart-card chart-full",
                ),
            ],
            className="chart-grid",
        ),
        html.Footer(
            [
                html.P(
                    "Sources: DSEC monthly visitor arrivals and hotel guests; World Bank ST.INT.ARVL and "
                    "NY.GDP.PCAP.CD; DSEC annual releases; MGTO Tourism Highlights 2025. "
                    "Retrieved 9 November 2026."
                ),
                html.P(
                    "Visitor volume is not the same as tourist spending, employment or complete economic "
                    "recovery. The 2026 monthly window ends in July."
                ),
            ],
            className="footer",
        ),
    ],
    className="app-shell",
)


@app.callback(
    Output("kpi-container", "children"),
    Output("monthly-chart", "figure"),
    Output("recovery-chart", "figure"),
    Output("source-chart", "figure"),
    Output("heatmap-chart", "figure"),
    Output("gdp-chart", "figure"),
    Input("year-range", "value"),
    Input("month-filter", "value"),
    Input("phase-filter", "value"),
    Input("source-filter", "value"),
)
def update_dashboard(year_range, months, phase, selected_market):
    return build_dashboard(year_range, months, phase, selected_market)


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)
