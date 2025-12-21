import pandas as pd

DATA_PATH = "../../data/tennis_atp_data/altered_data/archetype/"


def apply_length_bins(df_matches, df_bins):
    # merge thresholds per year
    df = df_matches.merge(
        df_bins[["year", "short_threshold", "long_threshold"]],
        on="year",
        how="left"
    )

    # Default bin
    df["length_bin"] = "medium"

    # Assign short and long based on thresholds
    df.loc[df["minutes"] < df["short_threshold"], "length_bin"] = "short"
    df.loc[df["minutes"] > df["long_threshold"],  "length_bin"] = "long"

    return df


if __name__ == "__main__":
    print("Loading clean matches...")
    df_matches = pd.read_csv(DATA_PATH + "clean_matches.csv")

    print("Loading match length bin thresholds...")
    df_bins = pd.read_csv(DATA_PATH + "match_length_bins_by_year.csv")

    print("Applying bins to matches...")
    df = apply_length_bins(df_matches, df_bins)

    print(f"Saving matches: {DATA_PATH}matches_with_bins.csv")
    df.to_csv(DATA_PATH + "matches_with_bins.csv", index=False)

    print("Done.")
