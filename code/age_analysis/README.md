This folder contains the code for the age analysis as well as the output files of that code. The output files however will not be pushed to GitHub, interessting data will be manually transferred to ../graphs

`clean_age_data.py` Extracts the relevant data from our dataset. So the winner and loser ages in this case. The output is stored in `filtered_ages/`

`basic_stats.py` Prints basic stats of the extracted data.

`age_diff.py` computes the mean different in age between the winner and loser of all matches, and stores it in TODO. `age_diff_plot.py` Creates plots based on this output.

`2025-rulebook-chapter-7_the-competition_23dec.pdf` Should probably be moved. It was used to confirm that the minimum age is 14.

`age_heatmap.py` Is a test to use logistic regression on the entire `filtered_ages/` folder. It looks promising, but it mirrors the `age_diff_plot.py` observations in that age difference has an effect, but a small one. Looking at the heatmap it mostly shows very young and very old players having a disadvantage.

`age_logit_csv.py` The majority of the runtime of `age_heatmap.py` is used to build the dataframes. There is no reason for this, especially since it is unflexible, so this script builds the win=1 win=0 csvs and stores it in `logit_csv`

`age_logit_plot.py` Creates heatmaps for the data in `logit_csv`.
