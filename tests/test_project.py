"""Automatic tests. Run them from the project folder with:  python -m pytest -q

Tests that need the large files in data/processed/ are skipped when those files are
missing (run the steps in the README first).
"""
import hashlib

import numpy as np
import pandas as pd
import pytest
from dash import dcc

from src.baseline import average_precision, roc_auc
from src.check_ground_truth import run_check
from src.data_loader import GROUND_TRUTH_FILE, MAIN_FILE, ROOT, load_ground_truth, load_main

RESULTS = ROOT / "results"
FEATURES_FILE = ROOT / "data" / "processed" / "features.csv"
needs_features = pytest.mark.skipif(not FEATURES_FILE.exists(), reason="run python -m src.build_features first")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_raw_files_are_unchanged():
    assert sha256(MAIN_FILE) == "b66bef4541ad3b4a3c934633b517cf05b29be47d6fd72482d09425b2fff05210"
    assert sha256(GROUND_TRUTH_FILE) == "57ab1bf2dd63a64ca82c91ab1592b53eb2fdbcdeced5cf8552b2914516eec171"


def test_loader_shapes_and_first_column():
    main, truth = load_main(), load_ground_truth()
    assert main.shape == (35975, 127)
    assert truth.shape == (11104, 2)
    assert main.columns[0] == "ts" and truth.columns[0] == "ts"  # no byte-order mark in the name


def test_ground_truth_matches_the_attack_rows():
    r = run_check()
    assert r["ground-truth rows"] == r["attack rows in main file"] == r["timestamps matched"] == 11104
    assert r["only in ground truth"] == 0 and r["only in main file"] == 0
    assert r["type mismatches"] == 0


def test_roc_auc_on_small_examples():
    assert roc_auc(pd.Series([3, 4, 5]), pd.Series([1, 2, 3])) == pytest.approx(8.5 / 9)
    assert roc_auc(pd.Series([5, 6]), pd.Series([1, 2])) == pytest.approx(1.0)
    assert roc_auc(pd.Series([1, 2]), pd.Series([1, 2])) == pytest.approx(0.5)


def test_average_precision_on_small_examples():
    assert average_precision(pd.Series([0.9, 0.8]), pd.Series([0.7, 0.1])) == pytest.approx(1.0)
    assert average_precision(pd.Series([0.9, 0.5]), pd.Series([0.8, 0.1])) == pytest.approx(5 / 6)


def test_feature_decision_list():
    table = pd.read_csv(ROOT / "docs" / "feature_set.csv")
    assert len(table) == 124 and table["column"].is_unique
    assert not {"ts", "label", "type", "source_row", "n_blank"} & set(table["column"])
    assert (table["status"] == "kept").sum() == 80
    reason = table["reason"].fillna("")
    assert reason.str.startswith("constant").sum() == 19
    assert reason.str.startswith("near-copy").sum() == 18
    assert reason.str.startswith("time proxy").sum() == 7


def test_saved_results_match_the_documented_numbers():
    overall = pd.read_csv(RESULTS / "detector_overall.csv")
    assert overall["roc_auc"].tolist() == [0.535, 0.563]
    drift = pd.read_csv(RESULTS / "drift_test.csv")
    assert len(drift) == 8 and drift["attack_rows"].sum() == 10252
    for name, expected in (("baseline", 0.702), ("forest", 0.738)):
        mean = np.average(drift[f"{name}_same_day"], weights=drift["attack_rows"])
        assert round(float(mean), 3) == expected


def test_dashboard_tables_have_the_right_totals():
    per_day = pd.read_csv(RESULTS / "rows_per_day.csv", index_col=0)
    assert len(per_day) == 9
    assert int(per_day.to_numpy().sum()) == 35975
    assert int(per_day["normal"].sum()) == 24871
    assert int(per_day.drop(columns="normal").to_numpy().sum()) == 11104
    series = pd.read_csv(RESULTS / "feature_series.csv")
    assert len(series) == 8994


def test_dashboard_builds_with_four_tabs():
    from src.dashboard import make_app

    layout = make_app().layout
    tabs = [child for child in layout.children if isinstance(child, dcc.Tabs)]
    assert len(tabs) == 1 and len(tabs[0].children) == 4


def test_requirements_are_pinned():
    lines = [l.strip() for l in (ROOT / "requirements.txt").read_text().splitlines() if l.strip()]
    assert lines and all("==" in line for line in lines)


def test_readme_lists_every_runnable_module():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for path in sorted((ROOT / "src").glob("*.py")):
        if '__name__ == "__main__"' in path.read_text(encoding="utf-8"):
            assert f"python -m src.{path.stem}" in readme, f"README does not list src/{path.name}"


@needs_features
def test_train_test_split_counts():
    from src.split import load_index, split_masks

    data = load_index()
    train, test, left_out = split_masks(data)
    assert int(train.sum()) == 5580
    assert int((test & (data["label"] == 0)).sum()) == 2534
    assert int((test & (data["label"] == 1)).sum()) == 10252
    assert not bool((train & test).any())
    assert (data.loc[train, "label"] == 0).all()