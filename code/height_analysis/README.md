This folder contains the code for the height analysis of the data, as well as all of the results.

For know it is a mess. The most important are the scripts with 'plot' and their name. If you run them they should tell you what is missing.

Their outputs are in the directories with 'stats' in their name.

- `clean_height_data.py` Extracts and cleans the data used in the height analysis. The results are stored in `filtered_heights`

- `height_stats.py` Gets the means and stds for all the heights in the dataset. The results are stored in `height_stats/height_stats.csv`
- `plot_height_stats.py` Plots the statistics of the heights over the years along with the trent. The results are stored in `height_stats/height_mean_plot.png` and `height_stats/height_std.png`


- `ht_logit_csv.py` Builds the win=1 win=0 csvs used in logistic regression and stores it in `logit_csv`
- `ht_logit_plot.py` Creates heatmaps for the data in `logit_csv`.
- `height_logit_test.py` Is meant to test which formula predicts the best.

- TODO rest of unused.
- `unused/atp_mean_height.py` Was used for early tests.
- `unused/height_matchup_classify.py` Was used for an early attempt to use heights in buckets.
