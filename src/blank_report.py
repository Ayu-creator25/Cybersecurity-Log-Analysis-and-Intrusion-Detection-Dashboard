"""Show how the blank (single-space) cells are spread across classes and columns."""
import pandas as pd

from src.data_loader import load_main


def run_report():
    """Return blank-cell counts by class, feature group and column."""
    df = load_main()
    features = [c for c in df.columns if c not in ("ts", "label", "type")]
    blank = df[features].apply(lambda s: s.astype(str).str.strip().eq(""))
    row_blank = blank.sum(axis=1)
    has_blank = row_blank > 0
    by_type = pd.DataFrame(
        {
            "rows": df["type"].value_counts(),
            "rows_with_blank": df.loc[has_blank, "type"].value_counts(),
        }
    ).fillna(0).astype(int)
    by_type["percent_with_blank"] = (100 * by_type["rows_with_blank"] / by_type["rows"]).round(2)
    by_label = df.groupby("label")[[]].size().to_frame("rows")
    by_label["rows_with_blank"] = has_blank.groupby(df["label"]).sum()
    by_label["percent_with_blank"] = (100 * by_label["rows_with_blank"] / by_label["rows"]).round(2)
    return {
        "rows_with_blank": int(has_blank.sum()),
        "blank_cells": int(blank.sum().sum()),
        "blank_cells_per_row_counts": row_blank[has_blank].value_counts().sort_index().to_dict(),
        "by_label": by_label,
        "by_type": by_type,
        "top_columns": blank.sum().sort_values(ascending=False).head(8),
    }


if __name__ == "__main__":
    r = run_report()
    print("rows with a blank:", r["rows_with_blank"], "| blank cells:", r["blank_cells"])
    print("blank cells per affected row (cells: rows):", r["blank_cells_per_row_counts"])
    print()
    print(r["by_label"].to_string())
    print()
    print(r["by_type"].to_string())
    print()
    print("columns with most blanks:")
    print(r["top_columns"].to_string())