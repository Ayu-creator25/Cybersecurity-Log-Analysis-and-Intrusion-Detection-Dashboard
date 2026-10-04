"""Feature selection: decide which of the 124 measurement columns a detector may use.

Rules (evidence in docs/eda_findings.md):
  1. constant columns are dropped (they carry no information)
  2. near-copy features (absolute Spearman correlation >= 0.99) form a group;
     from each group one feature is kept: the one with the fewest blank cells,
     and on a tie the one that comes first in the file
  3. time-proxy features are dropped: a feature whose absolute Spearman
     correlation with ts is at least TIME_LIMIT among NORMAL rows, in the early
     period or in the late period, works like a clock (for example disk free
     space shrinks steadily). A detector could use it to read the time, and the
     time gives away the attack type. This rule uses the label only to pick
     the normal rows, which is the training data of an unsupervised detector.
  4. ts, label, type, source_row and n_blank are never features
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
TIME_LIMIT = 0.7


def time_trend(full, columns):
    """Spearman correlation of each column with ts among normal rows: (early, late)."""
    normal = full[full["label"] == 0]
    first_attack = full.loc[full["label"] == 1, "ts"].min()
    early = normal[normal["ts"] < first_attack]
    late = normal[normal["ts"] >= first_attack]
    results = []
    for part in (early, late):
        ts_rank = part["ts"].rank()
        values = {}
        for c in columns:
            column = part[c]
            # a column that does not change inside the period has no trend
            values[c] = column.rank().corr(ts_rank) if column.nunique() > 1 else np.nan
        results.append(pd.Series(values))
    return results[0], results[1]


def select_features():
    """Return (table, kept, full, corr): one table row per measurement column and the kept names."""
    full, non_constant = load_features()
    all_columns = [c for c in feature_columns(full) if c not in HELPER_COLUMNS + ("date",)]
    blanks = full[all_columns].isna().sum()
    corr = correlation_matrix(full, non_constant)
    groups = near_duplicate_groups(corr, LIMIT)
    position = {c: i for i, c in enumerate(all_columns)}
    trend_early, trend_late = time_trend(full, non_constant)
    trend = pd.concat([trend_early, trend_late], axis=1).abs().max(axis=1)  # NaN is skipped

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
        elif trend[c] >= TIME_LIMIT:
            status, instead = "dropped", ""
            reason = "time proxy (|correlation with ts| >= %.1f among normal rows)" % TIME_LIMIT
        else:
            status, instead, reason = "kept", "", ""
        rows.append(
            {
                "position": position[c] + 1,
                "column": c,
                "group": group_of(c),
                "blank_cells": int(blanks[c]),
                "trend_with_ts_early": round(float(trend_early.get(c, np.nan)), 2),
                "trend_with_ts_late": round(float(trend_late.get(c, np.nan)), 2),
                "status": status,
                "kept_instead": instead,
                "reason": reason,
            }
        )
    table = pd.DataFrame(rows)
    return table, table.loc[table["status"] == "kept", "column"].tolist(), full, corr


def check(table, kept, corr):
    """Return a dict of checks (True = passed)."""
    near_copy = [c for c in kept if c in corr.columns]
    sub = corr.loc[near_copy, near_copy].abs().to_numpy()
    off_diagonal = sub[np.triu_indices(len(near_copy), k=1)]
    trend = table.set_index("column")[["trend_with_ts_early", "trend_with_ts_late"]].abs().max(axis=1)
    return {
        "124 columns in the table": len(table) == 124,
        "kept + dropped = 124": len(kept) + int((table["status"] == "dropped").sum()) == 124,
        "19 constant columns dropped": int((table["reason"] == "constant column").sum()) == 19,
        "no kept feature is constant": not table.loc[table["status"] == "kept", "reason"].eq("constant column").any(),
        "every kept_instead points to a feature in the table": set(table["kept_instead"]) - {""} <= set(table["column"]),
        "no two kept features have |correlation| >= 0.99": bool((off_diagonal < LIMIT).all()),
        "no kept feature is a time proxy": bool((trend[kept].fillna(0) < TIME_LIMIT).all()),
        "ts, label, type, helper columns not in the table": not set(["ts", "label", "type", *HELPER_COLUMNS]) & set(table["column"]),
    }


if __name__ == "__main__":
    table, kept, full, corr = select_features()
    table.to_csv(OUT_CSV, index=False)
    print("written:", OUT_CSV)
    print("kept:", len(kept))
    print("dropped, constant:", int((table["reason"] == "constant column").sum()))
    print("dropped, near-copy:", int(table["kept_instead"].ne("").sum()))
    proxies = table[table["reason"].str.startswith("time proxy")]
    print("dropped, time proxy:", len(proxies))
    print("kept per group:", table[table["status"] == "kept"]["group"].value_counts().to_dict())
    print()
    print("time-proxy features (trend with ts among normal rows, early / late):")
    for _, r in proxies.iterrows():
        print(f"  {r['column']}: {r['trend_with_ts_early']} / {r['trend_with_ts_late']}")
    print()
    results = check(table, kept, corr)
    for name, ok in results.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    print("RESULT:", "PASS" if all(results.values()) else "FAIL")