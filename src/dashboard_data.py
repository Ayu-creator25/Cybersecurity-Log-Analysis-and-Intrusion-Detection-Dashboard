"""Readers for the small result tables in results/ and docs/, so that the dashboard needs no large file."""
import pandas as pd

from src.data_loader import ROOT

RESULTS = ROOT / "results"
FEATURE_LIST = ROOT / "docs" / "feature_set.csv"


def rows_per_day():
    """Rows per UTC day (index) and row type (columns)."""
    return pd.read_csv(RESULTS / "rows_per_day.csv", index_col=0)


def feature_series():
    """Every 4th row (time order) with ts, label, type, day and eight features."""
    return pd.read_csv(RESULTS / "feature_series.csv")


def detector_overall():
    """Overall results of the two detectors on the test rows."""
    return pd.read_csv(RESULTS / "detector_overall.csv")


def detector_by_type():
    """ROC-AUC of each detector per attack type."""
    return pd.read_csv(RESULTS / "detector_by_type.csv")


def drift_pairs():
    """ROC-AUC with the far and the same-day reference per day and attack type."""
    return pd.read_csv(RESULTS / "drift_test.csv")


def features_used():
    """Number of features that the detectors use."""
    return int((pd.read_csv(FEATURE_LIST)["status"] == "kept").sum())