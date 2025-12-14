# THIS FILE USES load_data.py. (DATA IS FROM 1997-2024)
# This file creates a dataset with the players surface winrates for each match they play, calculated individually
# for each match. It does it for the following surfaces: clay, hard and grass. The dataset is then used in
# surface_winrate_analysis.py to analyze the effect of surface winrate on accuracy.
import pandas as pd
from load_data import load_tennis_data

# class to keep track of matches wins/losses per surface for each tenisser, chronologically.
class Tenisser:
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

    def get_winrate(self, surface):
        # calculate historical winrate before the current match. 
        # minimum matches of 15 needed, else the data would be too noisy.
        total_matches = self.surface_matches[surface]["wins"] + self.surface_matches[surface]["losses"]

        # MOET EEN FIX VOOR DIT
        if total_matches < 15:
            return 0.5
        
        return self.surface_matches[surface]["wins"] / total_matches


def main():
    # data is from 1997 to 2024
    data = load_tennis_data(path_pattern="../../../data/tennis_atp_data/unaltered_data/*",
                            regex_pattern=r"/atp_matches_(199[7-9]|20[0-1][0-9]|202[0-4])\.csv")
    data = data[data['surface'].isin(['Hard','Clay','Grass'])]
    # print(1, len(data))

    # sorting as it wasnt in chronological order, which would ruin the winrate calculation
    data = data.sort_values('tourney_date').reset_index(drop=True)

    # loop in which constantly recalculate the winrate for each individual match
    # for each match i get the winrates of the tenissers. store it in the dataset,
    # and then update the winrate with after this match
    # since logistic regression needs 2 target classes, i decided to temporarily
    # store each row from both the winners and losers perspective. i plan to research
    # this later if there are better options if time allows.
    tenissers = {}
    new_rows = []
    for _, row in data.iterrows():
        if row['winner_id'] not in tenissers:
            tenissers[row['winner_id']] = Tenisser(row['winner_id'])

        if row['loser_id'] not in tenissers:
            tenissers[row['loser_id']] = Tenisser(row['loser_id'])

        winner_winrate = tenissers[row['winner_id']].get_winrate(row['surface'])
        loser_winrate = tenissers[row['loser_id']].get_winrate(row['surface'])

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
            'rank_diff': row['loser_rank'] - row['winner_rank'],
            'winrate_diff': winner_winrate - loser_winrate,
            'player1_won': 1
        }

        new_row_loss = {
            'tourney_date': row['tourney_date'],
            'surface': row['surface'],
            'p1_id': row['loser_id'],
            'p2_id': row['winner_id'],
            'p1_name': row['winner_name'],
            'p2_name': row['loser_name'],
            'p1_surface_winrate': loser_winrate,
            'p2_surface_winrate': winner_winrate,
            'p1_rank': row['loser_rank'],
            'p2_rank': row['winner_rank'],
            'rank_diff': row['winner_rank'] - row['loser_rank'],
            'winrate_diff': loser_winrate - winner_winrate,
            'player1_won': 0
        }
        
        new_rows.append(new_row_win)
        new_rows.append(new_row_loss)

        tenissers[row['winner_id']].update_winrate(row['surface'], 1)
        tenissers[row['loser_id']].update_winrate(row['surface'], 0)

    data = pd.DataFrame(new_rows)
    data = data.dropna(subset=['p1_rank', 'p2_rank', 'p1_surface_winrate', 'p2_surface_winrate'])
    # print(2, len(data)//2)
    data.to_csv("surface_winrate_dataset.csv", index=False)
    print(f"data size: {len(data)}")

    # quick overview of how rows look like                                                                                                                                                                                                
    print(data.iloc[200:206])


if __name__=="__main__":
    main()
