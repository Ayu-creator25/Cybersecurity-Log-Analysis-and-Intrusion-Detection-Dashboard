"""EDA 4: which features are near-copies of each other?

Spearman correlation (correlation of ranks) between all non-constant features.
Features whose absolute correlation is at least LIMIT are put in one group,
because they carry almost the same information. One feature per group is enough
for a simple detector.
"""
import numpy as np
import pandas as pd

from src.eda_separation import load_features

LIMIT = 0.99


def correlation_matrix(full, features):
    """Spearman correlation: rank each column, then take the ordinary correlation."""
    return full[features].rank().corr()


def near_duplicate_groups(corr, limit=LIMIT):
    """Group features that are linked by absolute correlation >= limit (connected groups)."""
    names = list(corr.columns)
    parent = {n: n for n in names}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    strong = corr.abs() >= limit
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if strong.loc[a, b]:
                parent[find(a)] = find(b)
    groups = {}
    for n in names:
        groups.setdefault(find(n), []).append(n)
    return sorted(groups.values(), key=len, reverse=True)


if __name__ == "__main__":
    full, features = load_features()
    corr = correlation_matrix(full, features)
    n = len(features)
    pairs = corr.abs().to_numpy()[np.triu_indices(n, k=1)]  # each pair once
    print("features:", n, "| feature pairs:", len(pairs))
    print("pairs with |correlation| >= 0.99:", int(np.sum(pairs >= 0.99)))
    print("pairs with |correlation| >= 0.90:", int(np.sum(pairs >= 0.90)))
    groups = near_duplicate_groups(corr)
    sizes = pd.Series([len(g) for g in groups]).value_counts().sort_index()
    print("groups of near-copies (|r| >= %.2f): %d" % (LIMIT, len(groups)))
    print("group size -> how many groups:", sizes.to_dict())
    print()
    print("largest groups:")
    for g in groups[:6]:
        if len(g) > 1:
            print(f"  {len(g)} features: " + "; ".join(g[:4]) + (" ..." if len(g) > 4 else ""))