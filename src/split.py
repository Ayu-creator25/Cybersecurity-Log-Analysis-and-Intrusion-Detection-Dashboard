"""Train/test split for the detector (decision recorded in docs/eda_findings.md, 6.4).

Train: normal rows from the start of the attack period (first attack) up to the
       end of 2019-04-24. Only normal rows are used for training.
Test:  every row from 2019-04-25 00:00 UTC on (normal rows and attack rows).
Not evaluated: the 852 attack rows of 2019-04-23/24 (scanning and most of dos).
They lie in the training dates, so their normal rows would be in the training set.
Rows before the first attack (the first three days) are not used at all, because
normal behaviour in that period differs from the attack period.
"""
import sys

import pandas as pd

from src.build_features import OUT_FEATURES

TEST_START = pd.Timestamp("2019-04-25", tz="UTC").timestamp()


def load_index():
    """Return ts, label and type of every row (the features are not needed here)."""
    return pd.read_csv(OUT_FEATURES, usecols=["source_row", "ts", "label", "type"])


def split_masks(df):
    """Return boolean masks (train, test, left_out) for the rows of df."""
    first_attack = df.loc[df["label"] == 1, "ts"].min()
    train = (df["label"] == 0) & (df["ts"] >= first_attack) & (df["ts"] < TEST_START)
    test = df["ts"] >= TEST_START
    left_out = ~(train | test)
    return train, test, left_out


def check(df, train, test, left_out):
    """Return a dict of checks (True = passed)."""
    attack_before_test = df[(df["label"] == 1) & (df["ts"] < TEST_START)]
    return {
        "train has only normal rows": bool((df.loc[train, "label"] == 0).all()),
        "no row is in both train and test": not bool((train & test).any()),
        "every row is in exactly one of train, test, left out": bool((train.astype(int) + test.astype(int) + left_out.astype(int) == 1).all()),
        "train ends before the test starts": bool(df.loc[train, "ts"].max() < df.loc[test, "ts"].min()),
        "train has 5,580 rows": int(train.sum()) == 5580,
        "test has 2,534 normal rows": int((test & (df["label"] == 0)).sum()) == 2534,
        "test has 10,252 attack rows": int((test & (df["label"] == 1)).sum()) == 10252,
        "852 attack rows are left out (04-23/24)": len(attack_before_test) == 852,
        "all 11,104 attack rows are accounted for": int((df["label"] == 1).sum()) == 11104 == int((test & (df["label"] == 1)).sum()) + len(attack_before_test),
    }


if __name__ == "__main__":
    data = load_index()
    train, test, left_out = split_masks(data)
    print("rows:", len(data), "| train:", int(train.sum()), "| test:", int(test.sum()), "| left out:", int(left_out.sum()))
    table = pd.DataFrame(
        {
            "train": data.loc[train, "type"].value_counts(),
            "test": data.loc[test, "type"].value_counts(),
            "left_out": data.loc[left_out, "type"].value_counts(),
        }
    ).fillna(0).astype(int)
    print(table.sort_values("test", ascending=False).to_string())
    print()
    print("attack rows of 2019-04-23/24 that are not evaluated:")
    print(data[(data["label"] == 1) & (data["ts"] < TEST_START)]["type"].value_counts().to_string())
    print()
    results = check(data, train, test, left_out)
    for name, ok in results.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    print("RESULT:", "PASS" if all(results.values()) else "FAIL")
    sys.exit(0 if all(results.values()) else 1)