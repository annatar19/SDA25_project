import pandas as pd
import glob
import re


def load_tennis_data(
    path_pattern="../data/tennis_atp_data/unaltered_data/*",
    regex_pattern=r"/atp_matches_\d{4}.csv",
    usecols=None,
):
    """
    Load ATP match CSV files matching the supplied patterns and columns.

    Parameters
    ----------
    path_pattern : str
        Path for locating csv files.

    year_pattern : str
        Regex pattern that filters which 'atp_matches_XXXX.csv' files to load.

    usecols : list or None
        Columns to load from each CSV. If None, all columns will be loaded.

    Returns
    -------
    pandas.DataFrame
        Concatenated dataset containing all matching CSVs.
    """

    ATP_PATH = path_pattern

    # Matches atp_matches_XXXX.csv
    match_fn_pattern = re.compile(regex_pattern)

    # Will make a list of strings like:
    # '../data/tennis_atp/atp_matches_qual_chall_1996.csv'
    atp_csv_fns = glob.glob(path_pattern)

    csvs = []
    for fn in atp_csv_fns:
        match = re.search(match_fn_pattern, fn)
        if match:
            # https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
            # My ide gives an error but it works fine.
            df = pd.read_csv(fn, usecols=usecols)
            csvs.append(df)

    if not csvs:
        raise ValueError(f"No matching CSV files found for path pattern: {path_pattern} or regex pattern: {regex_pattern}")
    
    # All the .csv into 1, the loaded columns that is.
    return pd.concat(csvs, ignore_index=True)