"""Check that the ground-truth file matches the attack rows of the main file."""
import sys

from src.data_loader import load_ground_truth, load_main


def run_check():
    """Return a dict of counts that compare the two raw files."""
    main = load_main()
    truth = load_ground_truth()
    attacks = main.loc[main["label"] == 1, ["ts", "type"]]
    normal_ts = main.loc[main["label"] == 0, "ts"]
    merged = truth.merge(
        attacks, on="ts", how="outer", suffixes=("_truth", "_main"), indicator=True
    )
    both = merged[merged["_merge"] == "both"]
    return {
        "ground-truth rows": len(truth),
        "attack rows in main file": len(attacks),
        "timestamps matched": len(both),
        "only in ground truth": int((merged["_merge"] == "left_only").sum()),
        "only in main file": int((merged["_merge"] == "right_only").sum()),
        "type mismatches": int((both["type_truth"] != both["type_main"]).sum()),
        "ground-truth timestamps on normal rows": int(truth["ts"].isin(normal_ts).sum()),
        "duplicate timestamps in ground truth": int(truth["ts"].duplicated().sum()),
    }


if __name__ == "__main__":
    results = run_check()
    for name, value in results.items():
        print(f"{name}: {value}")
    passed = (
        results["ground-truth rows"]
        == results["attack rows in main file"]
        == results["timestamps matched"]
        and results["only in ground truth"] == 0
        and results["only in main file"] == 0
        and results["type mismatches"] == 0
        and results["ground-truth timestamps on normal rows"] == 0
        and results["duplicate timestamps in ground truth"] == 0
    )
    print("RESULT:", "PASS" if passed else "FAIL")
    sys.exit(0 if passed else 1)