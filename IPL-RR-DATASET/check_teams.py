import pandas as pd
import os

BASE_DIR = r"c:\ML REPO GITHUB\IPL-RR-DATASET"
MAPPING_PATH = os.path.join(BASE_DIR, "player_competition_team_mapping.csv")

try:
    df = pd.read_csv(MAPPING_PATH)
    teams = df['team_name'].unique()
    
    print("Searching for 'Chennai':")
    print([t for t in teams if "Chennai" in str(t)])
    
    print("\nSearching for 'Mumbai':")
    print([t for t in teams if "Mumbai" in str(t)])
except Exception as e:
    print(f"Error: {e}")
