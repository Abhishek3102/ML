import pandas as pd
import os

BASE_DIR = r"c:\ML REPO GITHUB\IPL-RR-DATASET"

def check(file):
    path = os.path.join(BASE_DIR, file)
    try:
        df = pd.read_csv(path, nrows=2)
        print(f"--- {file} ---")
        print(df.columns.tolist())
        print(df.iloc[0].to_dict())
    except Exception as e:
        print(f"Error reading {file}: {e}")

    with open("cols.txt", "w") as f:
        pass # Clear file

def check(file):
    path = os.path.join(BASE_DIR, file)
    try:
        df = pd.read_csv(path, nrows=2)
        with open("cols.txt", "a") as f:
            f.write(f"--- {file} ---\n")
            f.write(str(df.columns.tolist()) + "\n")
            f.write(str(df.iloc[0].to_dict()) + "\n\n")
    except Exception as e:
        with open("cols.txt", "a") as f:
            f.write(f"Error reading {file}: {e}\n")

check("matches.csv")
check("player_match_stats.csv")
check("players.csv")
check("player_competition_team_mapping.csv")
