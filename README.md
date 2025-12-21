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
│   ├── atp_archetype_analysis
│   ├── atp_hand_analysis
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
│   ├── archetype
│   ├── hand
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

## Clarifying answers to questions from the presentation

**Q1: Why don't the win rates in the archetype graphs add up to 100% ?**  
**A1:** The win rates don't add up to 100% because they're independent win probabilities, not part
of a single total. Each value answers: "What is the chance this archetype wins a match?"
Percentages only sum up to 100% when they describe all possible outcomes of the same event.
Example: A sprinter win rate of 40% means sprinters win 40% of their matches. A balanced win rate
of 38% means balanced players win 38% of their matches. These refer to different groups of matches,
so adding them together is pointless.

