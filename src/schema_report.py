"""Build a data dictionary for the raw Windows 10 file. Reads only, changes nothing."""
import numpy as np
import pandas as pd

from src.data_loader import ROOT, load_main

OUT_FILE = ROOT / "docs" / "data_dictionary.csv"
GROUPS = ["Processor", "Process", "Network", "Memory", "LogicalDisk"]


def column_group(name):
    """Name the feature group from the start of the column name."""
    if name in ("ts", "label", "type"):
        return "meta"
    for group in GROUPS:
        if name.startswith(group):
            return group
    return "other"


def build_dictionary(df):
    """One row per column: type, blanks, number check, distinct values, range."""
    rows = []
    for position, col in enumerate(df.columns, start=1):
        text = df[col].astype(str).str.strip()
        blank = text.eq("")
        if col == "type":
            numeric = None
            values = text
        else:
            values = pd.to_numeric(text.replace("", np.nan), errors="coerce")
            numeric = bool((values.notna() | blank).all())
        distinct = int(values.nunique())
        rows.append(
            {
                "position": position,
                "column": col,
                "group": column_group(col),
                "raw_dtype": str(df[col].dtype),
                "blank_cells": int(blank.sum()),
                "all_numeric_after_cleaning": numeric,
                "distinct_values": distinct,
                "is_constant": distinct <= 1,
                "min": None if col == "type" else values.min(),
                "max": None if col == "type" else values.max(),
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    dictionary = build_dictionary(load_main())
    dictionary.to_csv(OUT_FILE, index=False)
    print("rows:", len(dictionary), "->", OUT_FILE)
    print(dictionary["group"].value_counts().to_dict())
    print("blank cells:", int(dictionary["blank_cells"].sum()),
          "| columns with blanks:", int((dictionary["blank_cells"] > 0).sum()))
    print("constant columns:", int(dictionary["is_constant"].sum()))
    print("non-numeric feature columns:",
          int((dictionary["all_numeric_after_cleaning"] == False).sum()))