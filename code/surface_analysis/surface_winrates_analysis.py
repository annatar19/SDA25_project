# This file uses ..
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.metrics import accuracy_score, roc_auc_score

def load_data_wr(path):
    data = pd.read_csv(path)
    # this to check only for close matches, so rank difference of only 50 or lower
    # so i can check the effect of winrate better
    return data[data['rank_diff'].abs() <= 50]

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
    # print(model.summary()) # too much for now so commented out

    y_test = test_data['player1_won']
    y_pred_prob = model.predict(test_data)
    y_pred_class = (y_pred_prob >= 0.5).astype(int)

    # acc and roc acc
    print("\nmetrics:")
    print("Accuracy:", accuracy_score(y_test, y_pred_class))
    print("ROC AUC:", roc_auc_score(y_test, y_pred_prob))
    return model

def main():
    data = load_data_wr("data_loader/surface_winrate_dataset.csv")

    # model on each surface. Check for imrpovementscle
    surfaces = ['Hard', 'Clay', 'Grass']
    for s in surfaces:
        data_surf = data[data['surface'] == s]
        train_data, test_data = split_train_test(data_surf)

        fitlogit("player1_won ~ rank_diff",
            train_data, test_data,
            f"Rank diff only (surface is {s})")

        fitlogit("player1_won ~ winrate_diff",
            train_data, test_data,
            f"Winrate diff only (surface is {s})")

        fitlogit("player1_won ~ rank_diff + winrate_diff",
            train_data, test_data,
            f"rank and winrate diff (surface is {s})")


if __name__ == "__main__":
    main()