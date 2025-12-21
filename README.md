SDA25 project repository for group 3

## About the project

This project analyzes professional tennis data to explore ...

The repository is organized into modular folders:

- `code/`: Scripts for data processing, analysis, and modeling.
- `data/`: Unaltered and altered tennis datasets, organized for clarity.

## Project structure

```plaintext
SDA25_project
├── code
│   ├── age_analysis
│   ├── atp_hand_analysis
│   ├── atp_match_length_analysis
│   ├── atp_model
│   ├── atp_ranking_analysis
│   ├── atp_win_streak_analysis
│   ├── height_analysis
│   └── surface_analysis
├── data
│   ├── tennis_atp_data
│   ├── tennis_wta_data
│   └── tml_data
├── graphs
│   ├── dominant_hand_winrates.png
│   ├── height_analysis
│   ├── ranking
│   ├── surface
│   └── win_streak
├── matches_with_win_streaks.csv
├── README.md
├── requirements.txt
└── SDA_2025_presentation.pdf
```

## Building
This project only uses Python code. To install the required libraries, do:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
When adding packages do:
```
pip install numpy # For instance
pip freeze > requirements.txt
```
But remember to do `source .venv/bin/activate` beforehand so the `requirements.txt` does not get overwritten with local packages.

## Data used
https://github.com/JeffSackmann/tennis_wta

https://github.com/JeffSackmann/tennis_atp (2010-2024)

https://github.com/Tennismylife/TML-Database/blob/master/2008.csv (1991 - 2025)

