"""Tables behind the charts. Plain Pandas, so that the dashboard can use them too."""
import sys

import pandas as pd

from src.build_features import OUT_FEATURES

TYPE_ORDER = ["normal", "scanning", "dos", "injection", "ddos", "password", "xss", "mitm"]


def load_index():
    """ts, label and type of every row (sorted by ts)."""
    return pd.read_csv(OUT_FEATURES, usecols=["ts", "label", "type"])


def rows_per_day_by_type(index):
    """Number of rows for every UTC day (rows) and row type (columns)."""
    day = pd.to_datetime(index["ts"], unit="s", utc=True).dt.strftime("%Y-%m-%d")
    table = pd.crosstab(day, index["type"])
    return table.reindex(columns=TYPE_ORDER, fill_value=0)


if __name__ == "__main__":
    index = load_index()
    table = rows_per_day_by_type(index)
    print(table.to_string())
    checks = {
        "9 days with data": len(table) == 9,
        "8 row types": list(table.columns) == TYPE_ORDER,
        "35,975 rows in total": int(table.to_numpy().sum()) == 35975,
        "24,871 normal rows": int(table["normal"].sum()) == 24871,
        "11,104 attack rows": int(table.drop(columns="normal").to_numpy().sum()) == 11104,
    }
    for name, ok in checks.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    sys.exit(0 if all(checks.values()) else 1)