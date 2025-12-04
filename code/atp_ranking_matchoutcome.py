# correlational analysis of the ranking of two players during a match, and the match outcome
# There are two variables influencing match outcome winner_rank_points and loser_rank_points (nominal)
# one outcome variable: winning type, categorical

import pandas as pd

USE_COLS = ["tourney_id", "tourney_name", "match_num", 
             "winner_id", "winner_rank", "winner_rank_points", 
             "loser_id", "loser_rank", "loser_rank_points"]

def read_atp(filename):
    """
    simple script for single datafile, for testing purposes, to adjusted for the entire dataset, or subset by years
    """
    
    df = pd.read_csv(filename, usecols=USE_COLS)

    return df


def test_linearity_of_logit(df):
    """
    function to test the linearity of logit for 
    """




tennis_df = read_atp("/Users/sebas/Documents/UvA/Jaar 3/ScientificDA/SDA25_project/data/tennis_atp_data/unaltered_data/atp_matches_2000.csv")