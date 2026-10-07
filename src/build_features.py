"""Build the feature table that the detector reads: data/processed/features.csv.

It holds the 80 kept features (docs/feature_set.csv) plus four columns that are
never features: source_row (row id), ts (for ordering and charts), label and type
(for evaluation only). Missing values stay missing; filling them is a detector
step, so that it can use training rows only.
"""
import sys

import numpy as np
import pandas as pd

from src.clean_data import OUT_FILE
from src.data_loader import ROOT

FEATURE_LIST = ROOT / "docs" / "feature_set.csv"
OUT_FEATURES = ROOT / "data" / "processed" / "features.csv"
NOT_FEATURES = ["source_row", "ts", "label", "type"]


def kept_features():
    """Names of the kept features, in file order, from the decision list."""
    table = pd.read_csv(FEATURE_LIST)
    return table.loc[table["status"] == "kept", "column"].tolist()


def build(cleaned, features):
    """Return the cleaned data reduced to NOT_FEATURES + the kept features."""
    return cleaned[NOT_FEATURES + features].copy()


def validate(table, cleaned, features):
    """Return a dict of checks (True = passed)."""
    same_values = all(
        np.array_equal(
            table[c].to_numpy(dtype="float64"),
            cleaned[c].to_numpy(dtype="float64"),
            equal_nan=True,
        )
        for c in features
    )
    return {
        "80 features": len(features) == 80,
        "columns = 4 non-feature columns + 80 features": list(table.columns) == NOT_FEATURES + features,
        "same row count as the cleaned file (35,975)": len(table) == len(cleaned) == 35975,
        "ts, label, type, source_row are not features": not set(NOT_FEATURES) & set(features),
        "ts sorted": bool(table["ts"].is_monotonic_increasing),
        "label counts unchanged (24,871 / 11,104)": table["label"].value_counts().to_dict() == {0: 24871, 1: 11104},
        "every feature column is numeric": all(pd.api.types.is_numeric_dtype(table[c]) for c in features),
        "missing values equal the cleaned file": int(table[features].isna().sum().sum()) == int(cleaned[features].isna().sum().sum()),
        "every value equals the cleaned value": bool(same_values),
    }


if __name__ == "__main__":
    cleaned = pd.read_csv(OUT_FILE, float_precision="round_trip")
    features = kept_features()
    build(cleaned, features).to_csv(OUT_FEATURES, index=False)
    # check the file that was written, not only the DataFrame in memory
    reread = pd.read_csv(OUT_FEATURES, float_precision="round_trip")
    results = validate(reread, cleaned, features)
    missing = int(reread[features].isna().sum().sum())
    print("written:", OUT_FEATURES, "| rows:", len(reread), "| columns:", reread.shape[1])
    print("missing values left in the features:", missing,
          "| rows with a missing value:", int(reread[features].isna().any(axis=1).sum()))
    for name, ok in results.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    all_ok = all(results.values())
    print("RESULT:", "PASS" if all_ok else "FAIL")
    sys.exit(0 if all_ok else 1)