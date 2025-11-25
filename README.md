SDA25 project repository for group 3

## About the project

This project analyzes professional tennis data to explore ...

The repository is organized into modular folders:

- `code/`: Scripts for data processing, analysis, and modeling.
- `data/`: Unaltered and altered tennis datasets, organized for clarity.

## Project structure

```plaintext

├── code/                   # Processing and analysis scripts
├── data/                   # Contains ATP (men's tennis) and WTA (women's tennis) data
├── .gitignore              # Files git should ignore
├── README.md               # Project overview (you're here now)
└── requirements.txt        # Python dependencies
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

