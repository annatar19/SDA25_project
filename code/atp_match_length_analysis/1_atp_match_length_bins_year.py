import pandas as pd
import glob
import re
import os


def compute_match_length_bins(
    path_pattern="../../data/tennis_atp_data/unaltered_data/*",
    regex_pattern=r"atp_matches_(199[1-9]|20[0-1][0-9]|202[0-4])\.csv$",
):
    """
    For each ATP match file:
    - calculate avg duration
    - calculate std duration
    - compute bins (short, medium, long)
    - count matches in each bin
    Returns summary DataFrame.
    """

    file_pattern = re.compile(regex_pattern)
    files = glob.glob(path_pattern)
    results = []

    for fn in files:
        m = file_pattern.search(os.path.basename(fn))
        if not m:
            continue

        year = int(m.group(1))

        # Read only minutes
        try:
            df = pd.read_csv(fn, usecols=["minutes"])
        except ValueError:
            print(f"Skipping {fn}: missing 'minutes'")
            continue

        df["minutes"] = pd.to_numeric(df["minutes"], errors="coerce")
        df = df.dropna(subset=["minutes"])

        if df.empty:
            continue

        avg = df["minutes"].mean()
        std = df["minutes"].std()

        short_t = avg - std
        long_t = avg + std

        # Classify each match
        df["bin"] = pd.cut(
            df["minutes"],
            bins=[-float("inf"), short_t, long_t, float("inf")],
            labels=["short", "medium", "long"]
        )

        short_count = (df["bin"] == "short").sum()
        medium_count = (df["bin"] == "medium").sum()
        long_count = (df["bin"] == "long").sum()
        total_matches = len(df)

        results.append({
            "year": year,
            "avg_minutes": avg,
            "std_minutes": std,
            "short_threshold": short_t,
            "long_threshold": long_t,
            "short_count": short_count,
            "medium_count": medium_count,
            "long_count": long_count,
            "total_matches": total_matches
        })

    summary = pd.DataFrame(results).sort_values("year")
    return summary


if __name__ == "__main__":
    summary = compute_match_length_bins()

    print("\n=== Match Duration Bins by Year ===")
    print(summary)

    summary.to_csv("match_length_bins_by_year.csv", index=False)
