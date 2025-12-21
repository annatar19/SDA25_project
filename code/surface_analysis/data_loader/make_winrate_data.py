# This file cleans the raw data, for winrate analysis. Historic wins and losses are stored
# for tennis players. Winrate is calculated individually for each match, based on all past
# matches.
# INPUT: raw csv's (using load_data.py)
# OUTPUT: preprocessed csv with winrates added for each players per match
import pandas as pd
from load_data import load_tennis_data


# Class to keep up with match histories
class Player:
    def __init__(self, tenisser_id):
        self.id = tenisser_id
        self.surface_matches = {"Grass": {"wins": 0, "losses": 0},
                                "Hard":  {"wins": 0, "losses": 0},
                                "Clay":  {"wins": 0, "losses": 0}}

    def update_winrate(self, surface, won):
        if won:
            self.surface_matches[surface]["wins"] += 1
        else:
            self.surface_matches[surface]["losses"] += 1

    # Uses laplace smoothing to avoid extremes for newer players
    def get_winrate(self, surface):
        total_matches = self.surface_matches[surface]["wins"] + \
                        self.surface_matches[surface]["losses"]
        return (self.surface_matches[surface]["wins"] + 1) / (total_matches + 2)


# IMPORTANT, we load 1980-2024, but use 1991-2024 as train/test. 1980-1991
# is used to initialize winrates for players. This way for the first part of the training data
# we dont start with 0 matches for all players, avoiding extreme values. We will still get new
# players throughout the years 1991 onwards, for those we rely on laplace.
def main():
    data = load_tennis_data(
        path_pattern="../../../data/tennis_atp_data/unaltered_data/*",
        regex_pattern=r"/atp_matches_(198[0-9]|199[0-9]|20[0-1][0-9]|202[0-4])\.csv")
    data = data[data['surface'].isin(['Hard', 'Clay', 'Grass'])]
    data = data.sort_values('tourney_date').reset_index(drop=True)

    tenissers = {}
    new_rows = []
    for _, row in data.iterrows():
        if row['winner_id'] not in tenissers:
            tenissers[row['winner_id']] = Player(row['winner_id'])

        if row['loser_id'] not in tenissers:
            tenissers[row['loser_id']] = Player(row['loser_id'])

        winner_winrate = tenissers[row['winner_id']].get_winrate(row['surface'])
        loser_winrate = tenissers[row['loser_id']].get_winrate(row['surface'])

        # See note above main()
        if row['tourney_date'] >= 19910101:
            new_row_win = {
                'tourney_date': row['tourney_date'],
                'surface': row['surface'],
                'p1_id': row['winner_id'],
                'p2_id': row['loser_id'],
                'p1_name': row['winner_name'],
                'p2_name': row['loser_name'],
                'p1_surface_winrate': winner_winrate,
                'p2_surface_winrate': loser_winrate,
                'p1_rank': row['winner_rank'],
                'p2_rank': row['loser_rank'],
                'player1_won': 1
            }

            new_row_loss = {
                'tourney_date': row['tourney_date'],
                'surface': row['surface'],
                'p1_id': row['loser_id'],
                'p2_id': row['winner_id'],
                'p1_name': row['loser_name'],
                'p2_name': row['winner_name'],
                'p1_surface_winrate': loser_winrate,
                'p2_surface_winrate': winner_winrate,
                'p1_rank': row['loser_rank'],
                'p2_rank': row['winner_rank'],
                'player1_won': 0
            }

            new_rows.append(new_row_win)
            new_rows.append(new_row_loss)

        tenissers[row['winner_id']].update_winrate(row['surface'], 1)
        tenissers[row['loser_id']].update_winrate(row['surface'], 0)

    data = pd.DataFrame(new_rows)
    data = data.dropna(
        subset=['p1_rank', 'p2_rank', 'p1_surface_winrate', 'p2_surface_winrate'])
    data.to_csv("../../../data/tennis_atp_data/altered_data/surface_analysis/"
                "surface_winrate_1991_2024.csv", index=False)

    # quick check if the rows look good, and data size seems realistic
    print(f"data size: {len(data)}")
    print(data.iloc[200:206])


if __name__ == "__main__":
    main()
