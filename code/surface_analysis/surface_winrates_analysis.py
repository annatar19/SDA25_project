# This file uses ..
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.metrics import accuracy_score, roc_auc_score

def load_data_wr(path):
    data = pd.read_csv(path)
    # this to check only for close matches
    # so i can check the effect of winrate better
    return data[(data['p2_rank'] - data['p1_rank']).abs() <= 100]

def split_train_test(data):
    # splitting in chronological order as its a timer series
    train_data = data[data['tourney_date'] < data['tourney_date'].quantile(0.8)]
    test_data = data[data['tourney_date'] >= data['tourney_date'].quantile(0.8)]
    return train_data, test_data

def fitlogit(formule, train_data, test_data, model_name):
    # fitting logregression 
    model = smf.logit(formule, train_data).fit(disp=0)
    print(f"\n{model_name}")
    # prints pvalue
    print(model.summary()) # too much for now so commented out

    y_test = test_data['player1_won']
    y_pred_prob = model.predict(test_data)
    y_pred_class = (y_pred_prob >= 0.5).astype(int)

    # acc and roc acc
    print("\nmetrics:")
    print("Accuracy:", accuracy_score(y_test, y_pred_class))
    print("ROC AUC:", roc_auc_score(y_test, y_pred_prob))
    return model

def main():
    data = load_data_wr("../../data/tennis_atp_data/altered_data/surface_winrate_dataset.csv")

    # model on each surface. Check for imrpovements
    # can remove this if u want only overall
    surfaces = ['Hard', 'Clay', 'Grass']
    for s in surfaces:
        data_surf = data[data['surface'] == s]
        train_data, test_data = split_train_test(data_surf)

        # formula_rank = "player1_won ~ I(p2_rank - p1_rank)"
        # fitlogit(formula_rank, train_data, test_data, f"Rank difference only (surface={s})")

        # formula_winrate = "player1_won ~ I(p1_surface_winrate - p2_surface_winrate)"
        # fitlogit(formula_winrate, train_data, test_data, f"Surface winrate difference only (surface={s})")

        formula = "player1_won ~ I(p2_rank - p1_rank) + I(p1_surface_winrate - p2_surface_winrate)"
        fitlogit(formula, train_data, test_data, f"Rank & Winrate differences (surface={s})")


if __name__ == "__main__":
    main()
