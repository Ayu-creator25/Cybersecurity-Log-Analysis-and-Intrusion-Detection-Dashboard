"""Save the two small tables that the dashboard needs, so that it runs without the large files.

results/rows_per_day.csv   rows per UTC day and row type (9 x 8 numbers)
results/feature_series.csv every 4th row (in time order) of eight features, for the feature chart
"""
import sys

from src.chart_data import RESULTS_DIR, feature_series, load_index, rows_per_day_by_type

SERIES_FEATURES = [
    "Process_Handle Count",
    "Process_Thread Count",
    "Process_Working Set",
    "Memory Available Bytes",
    "Memory Cache Bytes",
    "Memory Pool Nonpaged Bytes",
    "Memory System Driver Total Bytes",
    "LogicalDisk(_Total) pct_ Free Space",
]
FILES = ["rows_per_day.csv", "feature_series.csv"]


if __name__ == "__main__":
    RESULTS_DIR.mkdir(exist_ok=True)
    per_day = rows_per_day_by_type(load_index())
    series = feature_series(SERIES_FEATURES, every=4)
    per_day.to_csv(RESULTS_DIR / FILES[0])
    series.to_csv(RESULTS_DIR / FILES[1], index=False)
    for name in FILES:
        path = RESULTS_DIR / name
        print("written:", path, f"({path.stat().st_size / 1024:.0f} KB)")
    checks = {
        "rows per day: 9 days": len(per_day) == 9,
        "rows per day: 35,975 rows in total": int(per_day.to_numpy().sum()) == 35975,
        "feature series: 8,994 rows and all 8 features": len(series) == 8994 and all(f in series.columns for f in SERIES_FEATURES),
        "both files are small (under 2 MB each)": all((RESULTS_DIR / name).stat().st_size < 2_000_000 for name in FILES),
    }
    for name, ok in checks.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    sys.exit(0 if all(checks.values()) else 1)