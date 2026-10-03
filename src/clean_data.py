"""Build the cleaned copy of the Windows 10 data and prove it matches the raw file.

The raw files are never changed. The cleaned copy goes to data/processed/.
Cleaning rules (research plan, Sections 7.2 and 7.6):
  - a whitespace-only cell becomes a missing value (NaN), no row is dropped
  - every feature column becomes a number
  - rows are sorted by ts; source_row keeps the original row position
  - n_blank counts the missing feature values in each row
"""
import sys

import numpy as np
import pandas as pd

from src.data_loader import ROOT, load_main

OUT_DIR = ROOT / "data" / "processed"
OUT_FILE = OUT_DIR / "windows10_clean.csv"
META = ["ts", "label", "type"]


def feature_columns(df):
    """Return the 124 feature column names."""
    return [c for c in df.columns if c not in META]


def to_numbers(df):
    """Return the feature columns as numbers; blanks become NaN, junk raises an error."""
    out = {}
    for col in feature_columns(df):
        text = df[col].astype(str).str.strip().replace("", np.nan)
        out[col] = pd.to_numeric(text, errors="raise").astype("float64")
    return pd.DataFrame(out, index=df.index)


def clean(raw):
    """Return the cleaned DataFrame (sorted by ts, blanks as NaN, source_row added)."""
    numbers = to_numbers(raw)
    cleaned = pd.concat([raw[META], numbers], axis=1)
    cleaned.insert(0, "source_row", np.arange(len(raw)))
    cleaned["n_blank"] = numbers.isna().sum(axis=1).astype("int64")
    cleaned = cleaned.sort_values("ts", kind="stable").reset_index(drop=True)
    # whole-number columns without blanks go back to integers
    for col in feature_columns(raw):
        s = cleaned[col]
        if s.notna().all() and (s == s.round()).all() and s.abs().max() < 2**53:
            cleaned[col] = s.astype("int64")
    return cleaned


def validate(cleaned, raw):
    """Return a dict of checks (True = passed) comparing the cleaned data with the raw file."""
    features = feature_columns(raw)
    expected = to_numbers(raw)
    by_source = cleaned.sort_values("source_row").reset_index(drop=True)
    same_values = all(
        np.array_equal(
            by_source[c].to_numpy(dtype="float64"),
            expected[c].to_numpy(dtype="float64"),
            equal_nan=True,
        )
        for c in features
    )
    return {
        "same row count (35,975)": len(cleaned) == len(raw) == 35975,
        "same columns plus source_row and n_blank": list(cleaned.columns)
        == ["source_row"] + META + features + ["n_blank"],
        "ts unique": bool(cleaned["ts"].is_unique),
        "ts sorted": bool(cleaned["ts"].is_monotonic_increasing),
        "source_row covers every raw row once": sorted(cleaned["source_row"]) == list(range(len(raw))),
        "label counts unchanged": cleaned["label"].value_counts().to_dict() == raw["label"].value_counts().to_dict(),
        "type counts unchanged": cleaned["type"].value_counts().to_dict() == raw["type"].value_counts().to_dict(),
        "label 0 only for normal": bool(((cleaned["label"] == 0) == (cleaned["type"] == "normal")).all()),
        "every feature column is numeric": all(pd.api.types.is_numeric_dtype(cleaned[c]) for c in features),
        "missing values = 3,360 (same as raw blanks)": int(cleaned[features].isna().sum().sum()) == 3360,
        "rows with a missing value = 761": int((cleaned["n_blank"] > 0).sum()) == 761,
        "no infinite values": not np.isinf(cleaned[features].to_numpy(dtype="float64")).any(),
        "every value equals the raw value": bool(same_values),
    }


if __name__ == "__main__":
    raw = load_main()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    clean(raw).to_csv(OUT_FILE, index=False)
    # check the file that was written, not only the DataFrame in memory
    reread = pd.read_csv(OUT_FILE, float_precision="round_trip")
    results = validate(reread, raw)
    print("written:", OUT_FILE, "| rows:", len(reread), "| columns:", reread.shape[1])
    for name, ok in results.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    all_ok = all(results.values())
    print("RESULT:", "PASS" if all_ok else "FAIL")
    sys.exit(0 if all_ok else 1)