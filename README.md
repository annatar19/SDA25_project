SDA25 project repository for group 3

# Building
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

# Data used
https://github.com/JeffSackmann/tennis_wta

https://github.com/JeffSackmann/tennis_atp (2010-2024)

https://github.com/Tennismylife/TML-Database/blob/master/2008.csv (1991 - 2025)

