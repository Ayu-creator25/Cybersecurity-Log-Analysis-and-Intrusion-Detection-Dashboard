"""Load the raw TON_IoT Windows 10 files without changing them."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
MAIN_FILE = RAW_DIR / "windows10_dataset.csv"
GROUND_TRUTH_FILE = RAW_DIR / "GroundTruth_Windows10.csv"


def load_main():
    """Return windows10_dataset.csv exactly as stored (127 columns, spaces kept)."""
    return pd.read_csv(MAIN_FILE, encoding="utf-8-sig", low_memory=False)


def load_ground_truth():
    """Return GroundTruth_Windows10.csv (columns: ts, type)."""
    return pd.read_csv(GROUND_TRUTH_FILE, encoding="utf-8-sig")