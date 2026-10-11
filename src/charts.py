"""Plotly charts. Every chart answers one question; the numbers come from src/chart_data.py.

Run `python -m src.charts` to write the charts as HTML files to data/processed/charts/
and open them in a browser.
"""
import sys

import plotly.graph_objects as go

from src.chart_data import load_index, rows_per_day_by_type
from src.data_loader import ROOT

OUT_DIR = ROOT / "data" / "processed" / "charts"

# One colour per row type (a colour-blind-friendly palette); normal rows are grey.
COLORS = {
    "normal": "#B0B7C3",
    "scanning": "#E69F00",
    "dos": "#56B4E9",
    "injection": "#009E73",
    "ddos": "#D55E00",
    "password": "#CC79A7",
    "xss": "#0072B2",
    "mitm": "#333333",
}


def attacks_per_day_figure(table):
    """Question: when do the attacks happen? Stacked bars: rows per day, split by row type."""
    fig = go.Figure()
    days = [str(day) for day in table.index]
    for row_type in table.columns:
        fig.add_trace(
            go.Bar(
                x=days,
                y=[int(value) for value in table[row_type]],
                name=row_type,
                marker_color=COLORS[row_type],
            )
        )
    fig.update_layout(
        barmode="stack",
        template="plotly_white",
        title_text="When do the attacks happen? Rows per day by row type",
        xaxis_title_text="Day (UTC). Days without data are not shown: 2019-04-05 to 04-22 and 04-28",
        yaxis_title_text="Rows",
        legend_title_text="Row type",
    )
    fig.update_xaxes(type="category")
    return fig


def build_all():
    """Return every chart as {file name: figure}."""
    table = rows_per_day_by_type(load_index())
    return {"attacks_per_day": attacks_per_day_figure(table)}


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    figures = build_all()
    checks = {}
    for name, fig in figures.items():
        path = OUT_DIR / f"{name}.html"
        fig.write_html(str(path), include_plotlyjs="cdn")
        print("written:", path)
        checks[f"{name}: file written"] = path.exists() and path.stat().st_size > 1000
    checks["attacks_per_day: one bar series for each of the 8 row types"] = len(figures["attacks_per_day"].data) == 8
    for name, ok in checks.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    sys.exit(0 if all(checks.values()) else 1)