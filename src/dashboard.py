"""Dash dashboard: four questions about the data, one tab each, and the limits of the results.

It reads only the small files in results/ and docs/ (src/save_results.py and
src/save_dashboard_data.py write them), so it needs none of the large data files.
Run `python -m src.dashboard` and open http://127.0.0.1:8050 in a browser.
Stop it with Ctrl+C in the terminal.
"""
import numpy as np
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

from src import dashboard_data as data
from src.chart_data import day_ticks
from src.charts import attacks_per_day_figure, detector_by_type_figure, drift_pairs_figure

PAGE = {"fontFamily": "Segoe UI, Arial, sans-serif", "maxWidth": "1300px", "margin": "0 auto", "padding": "16px"}
CARD = {
    "border": "1px solid #d0d7de",
    "borderRadius": "8px",
    "padding": "10px 14px",
    "background": "#f6f8fa",
    "minWidth": "190px",
    "flex": "1",
}
CELL = {"border": "1px solid #d0d7de", "padding": "6px 12px", "textAlign": "left"}
NOTE = {"color": "#57606a", "fontSize": "13px"}
# These four features work like clocks (their value follows the time), so the detectors do not use them.
CLOCK_LIKE = {
    "LogicalDisk(_Total) pct_ Free Space",
    "Memory Cache Bytes",
    "Memory Pool Nonpaged Bytes",
    "Memory System Driver Total Bytes",
}


def card(title, value, note):
    """One key-number card."""
    return html.Div(
        [
            html.Div(title, style={"fontSize": "12px", "color": "#57606a"}),
            html.Div(value, style={"fontSize": "24px", "fontWeight": "bold"}),
            html.Div(note, style=NOTE),
        ],
        style=CARD,
    )


def key_number_cards(per_day, overall, drift):
    """The row of cards at the top."""
    total = int(per_day.to_numpy().sum())
    attacks = int(per_day.drop(columns="normal").to_numpy().sum())
    weights = drift["attack_rows"]
    same_day = {n: float(np.average(drift[f"{n}_same_day"], weights=weights)) for n in ("baseline", "forest")}
    return [
        card("Rows", f"{total:,}", "Windows 10 log rows, 2019-04-02 to 2019-04-29"),
        card("Attack rows", f"{attacks:,}", f"{100 * attacks / total:.1f}% of all rows"),
        card("Features used", str(data.features_used()), "of 124 measurement columns"),
        card(
            "ROC-AUC, reference of 04-23/24",
            f"{overall['roc_auc'].iloc[0]:.3f} / {overall['roc_auc'].iloc[1]:.3f}",
            "baseline / Isolation Forest (0.5 = chance)",
        ),
        card(
            "ROC-AUC, same-day reference",
            f"{same_day['baseline']:.3f} / {same_day['forest']:.3f}",
            "baseline / Isolation Forest (diagnostic only)",
        ),
    ]


def results_table(overall):
    """Overall results of the two detectors on the test rows."""
    head = ["Detector", "ROC-AUC", "Average precision", "False alarms %", "Recall %"]
    rows = [
        [r.detector, f"{r.roc_auc:.3f}", f"{r.average_precision:.3f}", f"{r.false_alarm_percent:.1f}", f"{r.recall_percent:.1f}"]
        for r in overall.itertuples()
    ]
    return html.Table(
        [
            html.Thead(html.Tr([html.Th(h, style=CELL) for h in head])),
            html.Tbody([html.Tr([html.Td(c, style=CELL) for c in row]) for row in rows]),
        ],
        style={"borderCollapse": "collapse", "margin": "8px 0"},
    )


def feature_figure(series, feature):
    """One feature along the row order: normal rows grey, attack rows orange."""
    fig = go.Figure()
    for label, name, color in ((0, "normal", "#B0B7C3"), (1, "attack", "#D55E00")):
        part = series[series["label"] == label]
        fig.add_trace(
            go.Scatter(
                x=[int(v) for v in part["position"]],
                y=[float(v) for v in part[feature]],
                mode="markers",
                marker=dict(size=4, color=color, opacity=0.7),
                name=name,
            )
        )
    positions, labels = day_ticks(series)
    fig.update_xaxes(tickmode="array", tickvals=positions, ticktext=labels, title_text="Day (2019, UTC). Days without data are skipped.")
    fig.update_layout(
        template="plotly_white",
        height=520,
        title_text=f"{feature} over time (every 4th row)",
        yaxis_title_text=feature,
        legend_title_text="Row type",
    )
    return fig


def make_app():
    """Build the dashboard."""
    per_day = data.rows_per_day()
    series = data.feature_series()
    overall = data.detector_overall()
    drift = data.drift_pairs()
    by_type = data.detector_by_type()
    features = [c for c in series.columns if c not in ("position", "ts", "label", "type", "day")]
    options = [
        {"label": f + ("   [clock-like: not used by the detectors]" if f in CLOCK_LIKE else ""), "value": f}
        for f in features
    ]

    tabs = dcc.Tabs(
        [
            dcc.Tab(
                label="1. When do the attacks happen?",
                children=[
                    html.P("Each attack type has its own days. The first three days contain only normal rows. Time alone would give the attack type away, so it is never used as an input to a detector."),
                    dcc.Graph(figure=attacks_per_day_figure(per_day)),
                ],
            ),
            dcc.Tab(
                label="2. Does normal behaviour change?",
                children=[
                    html.P("Yes. Handle and thread counts jump at 2019-04-23, memory swings from day to day, and disk free space shrinks steadily like a clock. Choose a feature to look at it. Features marked clock-like follow the time, so the detectors do not use them."),
                    dcc.Dropdown(id="feature-choice", options=options, value=features[0], clearable=False, style={"maxWidth": "620px"}),
                    dcc.Graph(id="feature-graph", figure=feature_figure(series, features[0])),
                ],
            ),
            dcc.Tab(
                label="3. How well do the detectors work?",
                children=[
                    html.P("Trained on normal rows of 2019-04-23/24 and tested on rows from 2019-04-25, both detectors are only slightly better than chance."),
                    results_table(overall),
                    dcc.Graph(figure=detector_by_type_figure(by_type)),
                ],
            ),
            dcc.Tab(
                label="4. Does a fresh reference help?",
                children=[
                    html.P("With normal rows of the same day as the reference, the ROC-AUC rises to about 0.70 to 0.74. The change in normal behaviour over time is a main reason for the weak results above."),
                    dcc.Graph(figure=drift_pairs_figure(drift)),
                ],
            ),
        ]
    )

    limits = html.Div(
        [
            html.H3("Limits of these results"),
            html.Ul(
                [
                    html.Li("An anomaly is not a confirmed intrusion. The labels of the TON_IoT data are used only to evaluate the detectors."),
                    html.Li("Scanning (447 rows) and most dos rows (405 of 525) lie in the training days and are not evaluated. dos has 120 and mitm only 15 test rows, so their numbers are indicative only."),
                    html.Li("The same-day reference needs normal rows of the same day. It is a diagnostic, not a usable detector."),
                    html.Li("The detectors use fixed settings that were not tuned on the test rows."),
                ]
            ),
            html.P(
                "Data: TON_IoT Windows 10 dataset, UNSW (https://research.unsw.edu.au/projects/toniot-datasets). Details and citations are in the README.",
                style=NOTE,
            ),
        ],
        style={"borderTop": "1px solid #d0d7de", "marginTop": "16px"},
    )

    app = Dash(__name__)
    app.title = "Cybersecurity Log Analysis and Intrusion Detection Dashboard"
    app.layout = html.Div(
        [
            html.H1("Cybersecurity Log Analysis and Intrusion Detection Dashboard"),
            html.P("Project area: Log Analytics, Anomaly Detection. Data: TON_IoT Windows 10 dataset.", style=NOTE),
            html.Div(key_number_cards(per_day, overall, drift), style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "margin": "12px 0"}),
            tabs,
            limits,
        ],
        style=PAGE,
    )

    @app.callback(Output("feature-graph", "figure"), Input("feature-choice", "value"))
    def update_feature_graph(feature):
        return feature_figure(series, feature)

    return app


app = make_app()
server = app.server  # used by a deployment server such as gunicorn

if __name__ == "__main__":
    app.run(debug=False)