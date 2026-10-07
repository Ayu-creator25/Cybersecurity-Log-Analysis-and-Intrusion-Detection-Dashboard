"""EDA 2: does normal behaviour change between the early period and the attack period?

Early normal = normal rows before the first attack (2019-04-02 to 2019-04-23).
Late normal  = normal rows from the first attack on (2019-04-23 to 2019-04-29).
For each feature we measure how many late-normal values fall outside the range
that holds the middle 98% (1st to 99th percentile) of early-normal values.
With no change in behaviour that share would be about 2%.
A second comparison does the same inside the attack period: normal rows of
2019-04-23/24 against normal rows of 2019-04-25 to 2019-04-29.
"""
import pandas as pd

from src.clean_data import OUT_FILE, feature_columns

HELPER_COLUMNS = ("source_row", "n_blank")  # added by clean_data, not measurements
SPLIT_TS = pd.Timestamp("2019-04-25", tz="UTC").timestamp()  # splits the attack period in two


def split_normal():
    """Return (early_normal, late_normal) DataFrames with the feature columns."""
    full = pd.read_csv(OUT_FILE, float_precision="round_trip")
    first_attack = full.loc[full["label"] == 1, "ts"].min()
    normal = full[full["label"] == 0]
    return normal[normal["ts"] < first_attack], normal[normal["ts"] >= first_attack]


def group_of(name):
    """Feature group from the start of the column name."""
    for group in ["Processor", "Process", "Network", "Memory", "LogicalDisk"]:
        if name.startswith(group):
            return group
    return "other"


def drift_table(early, late):
    """One row per non-constant feature: median shift and share outside the early range."""
    rows = []
    for col in [c for c in feature_columns(early) if c not in HELPER_COLUMNS]:
        a, b = early[col].dropna(), late[col].dropna()
        if pd.concat([a, b]).nunique() <= 1:
            continue  # constant column, carries no information
        low, high = a.quantile(0.01), a.quantile(0.99)
        rows.append(
            {
                "feature": col,
                "group": group_of(col),
                "early_median": a.median(),
                "late_median": b.median(),
                "percent_outside_early_range": round(100 * ((b < low) | (b > high)).mean(), 1),
            }
        )
    return pd.DataFrame(rows).sort_values("percent_outside_early_range", ascending=False)


if __name__ == "__main__":
    early, late = split_normal()
    print("early normal rows:", len(early), "| late normal rows:", len(late))
    table = drift_table(early, late)
    pct = table["percent_outside_early_range"]
    print("features compared (constant columns skipped):", len(table))
    print("features with more than 10% outside the early range:", int((pct > 10).sum()))
    print("features with more than 50% outside the early range:", int((pct > 50).sum()))
    print("median of the percent outside:", round(float(pct.median()), 1), "(about 2 means no change)")
    print()
    print("by feature group (average percent outside):")
    print(table.groupby("group")["percent_outside_early_range"].agg(["count", "mean"]).round(1).to_string())
    print()
    print("top 12 features that changed most:")
    print(table.head(12).to_string(index=False))

    print()
    print("second comparison, normal rows inside the attack period (04-23/24 against 04-25 to 04-29)")
    first_days, last_days = late[late["ts"] < SPLIT_TS], late[late["ts"] >= SPLIT_TS]
    inner = drift_table(first_days, last_days)["percent_outside_early_range"]
    print("rows:", len(first_days), "against", len(last_days))
    print("features with more than 10% outside the first range:", int((inner > 10).sum()))
    print("features with more than 50% outside the first range:", int((inner > 50).sum()))
    print("median of the percent outside:", round(float(inner.median()), 1))