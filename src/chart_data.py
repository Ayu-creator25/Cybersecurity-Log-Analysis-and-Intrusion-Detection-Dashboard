"""Tables behind the charts. Plain Pandas, so that the dashboard can use them too."""
import sys

import pandas as pd

from src.build_features import OUT_FEATURES
from src.clean_data import OUT_FILE
from src.data_loader import ROOT

RESULTS_DIR = ROOT / "results"
DRIFT_FEATURES = [
    "Process_Handle Count",
    "Process_Thread Count",
    "Memory Available Bytes",
    "LogicalDisk(_Total) pct_ Free Space",
]
TYPE_ORDER = ["normal", "scanning", "dos", "injection", "ddos", "password", "xss", "mitm"]


def load_index():
    """ts, label and type of every row (sorted by ts)."""
    return pd.read_csv(OUT_FEATURES, usecols=["ts", "label", "type"])


def rows_per_day_by_type(index):
    """Number of rows for every UTC day (rows) and row type (columns)."""
    day = pd.to_datetime(index["ts"], unit="s", utc=True).dt.strftime("%Y-%m-%d")
    table = pd.crosstab(day, index["type"])
    return table.reindex(columns=TYPE_ORDER, fill_value=0)


def detector_by_type():
    """ROC-AUC of each detector for each attack type, main protocol (written by src.save_results)."""
    return pd.read_csv(RESULTS_DIR / "detector_by_type.csv")


def drift_pairs():
    """ROC-AUC with the far and the same-day reference for each day and attack type."""
    return pd.read_csv(RESULTS_DIR / "drift_test.csv")


def feature_series(features=None, every=4):
    """Every `every`-th row (in time order) with ts, label, type, day and the chosen features.

    position is the row number in the full file, so that the days line up on the x axis.
    """
    features = features or DRIFT_FEATURES
    data = pd.read_csv(OUT_FILE, usecols=["ts", "label", "type"] + features)
    data.insert(0, "position", range(len(data)))
    data["day"] = pd.to_datetime(data["ts"], unit="s", utc=True).dt.strftime("%Y-%m-%d")
    return data.iloc[::every].reset_index(drop=True)


def day_ticks(series):
    """Where each day starts on the position axis: (positions, labels like '04-23')."""
    first = series.groupby("day")["position"].min()
    return [int(v) for v in first.values], [str(day)[5:] for day in first.index]


if __name__ == "__main__":
    index = load_index()
    table = rows_per_day_by_type(index)
    print(table.to_string())
    by_type, pairs = detector_by_type(), drift_pairs()
    series = feature_series()
    positions, labels = day_ticks(series)
    checks = {
        "9 days with data": len(table) == 9,
        "8 row types": list(table.columns) == TYPE_ORDER,
        "35,975 rows in total": int(table.to_numpy().sum()) == 35975,
        "24,871 normal rows": int(table["normal"].sum()) == 24871,
        "11,104 attack rows": int(table.drop(columns="normal").to_numpy().sum()) == 11104,
        "detector results: 2 detectors x 6 attack types": len(by_type) == 12 and by_type["detector"].nunique() == 2,
        "drift test results: 8 pairs of day and attack type": len(pairs) == 8,
        "feature series: every 4th row (8,994 rows) of 4 features": len(series) == 8994 and all(f in series.columns for f in DRIFT_FEATURES),
        "feature series: 9 day labels, the first at position 0": len(labels) == 9 and positions[0] == 0,
    }
    for name, ok in checks.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    sys.exit(0 if all(checks.values()) else 1)