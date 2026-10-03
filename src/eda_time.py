"""EDA 1: how normal and attack rows are spread over time (UTC). Reads the cleaned file."""
import pandas as pd

from src.clean_data import OUT_FILE


def load_clean():
    """Return ts, label and type with a UTC datetime column and a date column."""
    df = pd.read_csv(OUT_FILE, usecols=["ts", "label", "type"])
    time = pd.to_datetime(df["ts"], unit="s", utc=True)
    return df.assign(time=time, date=time.dt.strftime("%Y-%m-%d"))


def rows_per_day(df):
    """Normal rows, attack rows and attack share for each date."""
    table = pd.crosstab(df["date"], df["label"]).rename(columns={0: "normal", 1: "attack"})
    table["total"] = table["normal"] + table["attack"]
    table["attack_percent"] = (100 * table["attack"] / table["total"]).round(1)
    return table


def type_spans(df):
    """First time, last time, number of days and rows for each attack type."""
    attacks = df[df["label"] == 1]
    spans = attacks.groupby("type").agg(
        rows=("ts", "size"),
        first=("time", "min"),
        last=("time", "max"),
        days=("date", "nunique"),
    )
    spans["first"] = spans["first"].dt.strftime("%m-%d %H:%M")
    spans["last"] = spans["last"].dt.strftime("%m-%d %H:%M")
    return spans.sort_values("rows", ascending=False)


def long_gaps(df, seconds=3600):
    """Gaps between neighbouring rows that are longer than the given number of seconds."""
    t = df["time"]
    gap = t.diff().dt.total_seconds()
    out = pd.DataFrame(
        {
            "from": t.shift(1)[gap > seconds].dt.strftime("%m-%d %H:%M"),
            "to": t[gap > seconds].dt.strftime("%m-%d %H:%M"),
            "hours": (gap[gap > seconds] / 3600).round(1),
        }
    )
    return out.reset_index(drop=True)


def two_periods(df):
    """Compare the normal-only period with the period that contains attacks."""
    first_attack = df.loc[df["label"] == 1, "ts"].min()
    before = df[df["ts"] < first_attack]
    after = df[df["ts"] >= first_attack]
    return {
        "first attack (UTC)": str(pd.to_datetime(first_attack, unit="s", utc=True)),
        "rows before first attack (all normal)": len(before),
        "normal rows before": int((before["label"] == 0).sum()),
        "attack rows before": int((before["label"] == 1).sum()),
        "rows from first attack on": len(after),
        "normal rows from first attack on": int((after["label"] == 0).sum()),
        "attack rows from first attack on": int((after["label"] == 1).sum()),
        "attack percent from first attack on": round(100 * (after["label"] == 1).mean(), 1),
    }


if __name__ == "__main__":
    data = load_clean()
    print("rows per UTC day"); print(rows_per_day(data).to_string()); print()
    print("attack types: when they occur"); print(type_spans(data).to_string()); print()
    print("gaps longer than 1 hour"); print(long_gaps(data).to_string()); print()
    for name, value in two_periods(data).items():
        print(f"{name}: {value}")