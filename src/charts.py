"""Plotly charts. Every chart answers one question; the numbers come from src/chart_data.py.

Run `python -m src.charts` to write the charts as HTML files to data/processed/charts/
and open them in a browser.
"""
import sys

import plotly.graph_objects as go

from src.chart_data import detector_by_type, drift_pairs, load_index, rows_per_day_by_type
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
DETECTOR_COLORS = {"baseline (robust z-score)": "#0072B2", "isolation forest": "#E69F00"}


def add_chance_line(fig):
    """Dashed line at ROC-AUC 0.5 (no better than chance)."""
    fig.add_shape(
        type="line", xref="paper", x0=0, x1=1, yref="y", y0=0.5, y1=0.5,
        line=dict(dash="dash", color="gray"),
    )
    fig.add_annotation(
        text="0.5 = no better than chance", xref="paper", x=1, yref="y", y=0.5,
        showarrow=False, xanchor="right", yanchor="bottom",
    )


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


def detector_by_type_figure(by_type):
    """Question: how well does each detector separate each attack type from normal rows?"""
    fig = go.Figure()
    for detector, part in by_type.groupby("detector", sort=False):
        labels = [f"{t} ({int(n):,})" for t, n in zip(part["type"], part["rows"])]
        fig.add_trace(
            go.Bar(
                x=labels,
                y=[float(v) for v in part["auc_vs_normal"]],
                name=detector,
                marker_color=DETECTOR_COLORS[detector],
            )
        )
    add_chance_line(fig)
    fig.update_layout(
        barmode="group",
        template="plotly_white",
        title_text="How well does each detector find each attack type? (reference: normal rows of 2019-04-23/24)<br><sup>Test rows from 2019-04-25. dos (120 rows) and mitm (15 rows) are too small to read much into; scanning is not evaluated.</sup>",
        xaxis_title_text="Attack type (number of test rows)",
        yaxis_title_text="ROC-AUC against the normal test rows",
        legend_title_text="Detector",
        yaxis_range=[0, 1],
    )
    return fig


def drift_pairs_figure(pairs):
    """Question: does a fresh reference of normal rows (same day) help?"""
    fig = go.Figure()
    labels = [f"{d} {t} ({int(n):,})" for d, t, n in zip(pairs["day"], pairs["type"], pairs["attack_rows"])]
    series = [
        ("baseline_far", "baseline, far reference", "#9ECAE1"),
        ("baseline_same_day", "baseline, same-day reference", "#0072B2"),
        ("forest_far", "isolation forest, far reference", "#FDD49E"),
        ("forest_same_day", "isolation forest, same-day reference", "#E69F00"),
    ]
    for column, name, color in series:
        fig.add_trace(go.Bar(x=labels, y=[float(v) for v in pairs[column]], name=name, marker_color=color))
    add_chance_line(fig)
    fig.update_layout(
        barmode="group",
        template="plotly_white",
        title_text="Does a fresh reference of normal rows help? ROC-AUC per day and attack type<br><sup>Far = normal rows of 2019-04-23/24. Same day = normal rows of that day. The same-day reference needs recent normal data: a diagnostic, not a usable detector.</sup>",
        xaxis_title_text="Day and attack type (attack rows)",
        yaxis_title_text="ROC-AUC against the normal rows of the same day",
        legend_title_text="Detector and reference",
        yaxis_range=[0, 1],
    )
    return fig


def build_all():
    """Return every chart as {file name: figure}."""
    return {
        "attacks_per_day": attacks_per_day_figure(rows_per_day_by_type(load_index())),
        "detector_by_type": detector_by_type_figure(detector_by_type()),
        "drift_pairs": drift_pairs_figure(drift_pairs()),
    }


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
    checks["detector_by_type: one bar series for each of the 2 detectors"] = len(figures["detector_by_type"].data) == 2
    checks["drift_pairs: 4 bar series (2 detectors x 2 references)"] = len(figures["drift_pairs"].data) == 4
    for name, ok in checks.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    sys.exit(0 if all(checks.values()) else 1)