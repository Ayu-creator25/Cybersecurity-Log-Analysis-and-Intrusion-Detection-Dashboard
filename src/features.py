"""Feature selection: decide which of the 124 measurement columns a detector may use.

Rules (from docs/eda_findings.md; none of them uses the label):
  1. constant columns are dropped (they carry no information)
  2. near-copy features (absolute Spearman correlation >= 0.99) form a group;
     from each group one feature is kept: the one with the fewest blank cells,
     and on a tie the one that comes first in the file
  3. ts, label, type, source_row and n_blank are never features
The result is written to docs/feature_set.csv so that every choice can be checked.
"""
import numpy as np
import pandas as pd

from src.clean_data import feature_columns
from src.data_loader import ROOT
from src.eda_correlation import LIMIT, correlation_matrix, near_duplicate_groups
from src.eda_drift import HELPER_COLUMNS, group_of
from src.eda_separation import load_features

OUT_CSV = ROOT / "docs" / "feature_set.csv"


def select_features():
    """Return (table, kept, full, corr): one table row per measurement column and the kept names."""
    full, non_constant = load_features()
    all_columns = [c for c in feature_columns(full) if c not in HELPER_COLUMNS + ("date",)]
    blanks = full[all_columns].isna().sum()
    corr = correlation_matrix(full, non_constant)
    groups = near_duplicate_groups(corr, LIMIT)
    position = {c: i for i, c in enumerate(all_columns)}

    kept_for = {}  # dropped near-copy -> the feature kept instead
    kept = set()
    for g in groups:
        best = min(g, key=lambda c: (blanks[c], position[c]))
        kept.add(best)
        for c in g:
            if c != best:
                kept_for[c] = best

    rows = []
    for c in all_columns:
        if c not in non_constant:
            status, instead, reason = "dropped", "", "constant column"
        elif c in kept_for:
            status, instead = "dropped", kept_for[c]
            reason = "near-copy of the kept feature (|correlation| >= %.2f)" % LIMIT
        else:
            status, instead, reason = "kept", "", ""
        rows.append(
            {
                "position": position[c] + 1,
                "column": c,
                "group": group_of(c),
                "blank_cells": int(blanks[c]),
                "status": status,
                "kept_instead": instead,
                "reason": reason,
            }
        )
    table = pd.DataFrame(rows)
    return table, [c for c in all_columns if c in kept], full, corr


def check(table, kept, corr):
    """Return a dict of checks (True = passed)."""
    sub = corr.loc[kept, kept].abs().to_numpy()
    off_diagonal = sub[np.triu_indices(len(kept), k=1)]
    return {
        "124 columns in the table": len(table) == 124,
        "kept + dropped = 124": (table["status"] == "kept").sum() + (table["status"] == "dropped").sum() == 124,
        "19 constant columns dropped": int((table["reason"] == "constant column").sum()) == 19,
        "no kept feature is constant": not table.loc[table["status"] == "kept", "reason"].eq("constant column").any(),
        "every kept_instead points to a kept feature": set(table["kept_instead"]) - {""} <= set(kept),
        "no two kept features have |correlation| >= 0.99": bool((off_diagonal < LIMIT).all()),
        "ts, label, type, helper columns not in the table": not set(["ts", "label", "type", *HELPER_COLUMNS]) & set(table["column"]),
    }


if __name__ == "__main__":
    table, kept, full, corr = select_features()
    table.to_csv(OUT_CSV, index=False)
    print("written:", OUT_CSV)
    print("kept:", len(kept))
    print("dropped, constant:", int((table["reason"] == "constant column").sum()))
    print("dropped, near-copy:", int(table["kept_instead"].ne("").sum()))
    print("kept per group:", table[table["status"] == "kept"]["group"].value_counts().to_dict())
    print()
    for _, r in table[table["kept_instead"] != ""].iterrows():
        print(f"dropped: {r['column']}  ->  kept: {r['kept_instead']}")
    print()
    results = check(table, kept, corr)
    for name, ok in results.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    print("RESULT:", "PASS" if all(results.values()) else "FAIL")