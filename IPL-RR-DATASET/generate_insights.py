import pandas as pd
import numpy as np
import os

# Paths
DATA_DIR = r"c:\ML REPO GITHUB\IPL-RR-DATASET"
INPUT_FILE = os.path.join(DATA_DIR, "UPDATED CSV", "enriched_match_player_stats_v1.csv")
OUTPUT_DIR = os.path.join(DATA_DIR, "UPDATED CSV", "insights")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_insights():
    print(f"Loading data from {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    
    # Ensure numeric types
    numeric_cols = ['runs_scored', 'balls_faced', 'no_of_fours', 'no_of_sixes', 'wicket_taken', 'runs_conceded', 'overs_bowled', 'mvp_score']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- Pre-Aggregation Calculations (Match Level Booleans) ---
    df['is_50'] = ((df['runs_scored'] >= 50) & (df['runs_scored'] < 100)).astype(int)
    df['is_100'] = (df['runs_scored'] >= 100).astype(int)
    df['is_3w_haul'] = (df['wicket_taken'] >= 3).astype(int)
    df['is_5w_haul'] = (df['wicket_taken'] >= 5).astype(int)
    
    # Calculate Boundary Runs per match
    df['boundary_runs'] = (df['no_of_fours'] * 4) + (df['no_of_sixes'] * 6)

    # --- Aggregation by Player ---
    print("Aggregating player stats...")
    # Group by Player ID (keep Name for display)
    # Note: A player might have different names/teams, grouping by ID is safest. Taking first name found.
    grp = df.groupby(['player_id', 'player_name', 'batting_type', 'bowling_type']) # Using batting_type/bowling_type if available from merge
    
    player_stats = grp.agg(
        matches_played=('match_id', 'count'),
        total_runs=('runs_scored', 'sum'),
        total_balls=('balls_faced', 'sum'),
        total_boundary_runs=('boundary_runs', 'sum'),
        total_wickets=('wicket_taken', 'sum'),
        total_runs_conceded=('runs_conceded', 'sum'),
        total_overs=('overs_bowled', 'sum'),
        total_mvp=('mvp_score', 'sum'),
        total_50s=('is_50', 'sum'),
        total_100s=('is_100', 'sum'),
        total_3w_hauls=('is_3w_haul', 'sum'),
        total_5w_hauls=('is_5w_haul', 'sum')
    ).reset_index()

    # --- Derived Metrics ---
    # Batting
    player_stats['batting_avg'] = np.where(player_stats['matches_played'] > 0, player_stats['total_runs'] / player_stats['matches_played'], 0) # Simplified avg (runs/matches)
    player_stats['strike_rate'] = np.where(player_stats['total_balls'] > 0, (player_stats['total_runs'] / player_stats['total_balls']) * 100, 0)
    player_stats['boundary_run_pct'] = np.where(player_stats['total_runs'] > 0, (player_stats['total_boundary_runs'] / player_stats['total_runs']) * 100, 0)
    
    # Bowling
    player_stats['bowling_avg'] = np.where(player_stats['total_wickets'] > 0, player_stats['total_runs_conceded'] / player_stats['total_wickets'], 999) # Lower is better
    player_stats['economy'] = np.where(player_stats['total_overs'] > 0, player_stats['total_runs_conceded'] / player_stats['total_overs'], 999)
    
    # --- Generating Specific Tables ---

    # 1. Highest Run Getter
    save_top_n(player_stats, 'total_runs', 'highest_run_getters.csv', ascending=False, 
               cols=['player_name', 'matches_played', 'total_runs', 'batting_avg', 'strike_rate'])

    # 2. Highest Run % in Boundary (Min 200 runs to be significant)
    save_top_n(player_stats[player_stats['total_runs'] >= 200], 'boundary_run_pct', 'highest_boundary_pct_batters.csv', ascending=False,
               cols=['player_name', 'total_runs', 'total_boundary_runs', 'boundary_run_pct'])

    # 3. Highest Wicket Taker
    save_top_n(player_stats, 'total_wickets', 'highest_wicket_takers.csv', ascending=False,
               cols=['player_name', 'matches_played', 'total_wickets', 'bowling_avg', 'economy'])

    # 4. Most 3+ Wicket Hauls
    save_top_n(player_stats, 'total_3w_hauls', 'most_3w_hauls.csv', ascending=False,
               cols=['player_name', 'matches_played', 'total_wickets', 'total_3w_hauls'])

    # 5. Most 50s
    save_top_n(player_stats, 'total_50s', 'most_50s.csv', ascending=False,
               cols=['player_name', 'matches_played', 'total_runs', 'total_50s'])
               
    # 6. Most 100s
    save_top_n(player_stats, 'total_100s', 'most_100s.csv', ascending=False,
               cols=['player_name', 'matches_played', 'total_runs', 'total_100s'])
               
    # 7. Highest Strike Rate (Min 100 balls)
    save_top_n(player_stats[player_stats['total_balls'] >= 100], 'strike_rate', 'highest_strike_rate_batters.csv', ascending=False,
               cols=['player_name', 'total_runs', 'total_balls', 'strike_rate'])
               
    # 8. Best Economy (Min 20 overs)
    save_top_n(player_stats[player_stats['total_overs'] >= 20], 'economy', 'best_economy_bowlers.csv', ascending=True,
               cols=['player_name', 'total_overs', 'total_runs_conceded', 'total_wickets', 'economy'])

    # 9. MVP Leaders
    save_top_n(player_stats, 'total_mvp', 'mvp_leaders.csv', ascending=False,
               cols=['player_name', 'matches_played', 'total_mvp'])

    print("All insights generated and saved.")

def save_top_n(df, sort_col, filename, ascending=False, n=20, cols=None):
    if cols:
        out_df = df[cols]
    else:
        out_df = df
        
    sorted_df = out_df.sort_values(sort_col, ascending=ascending).head(n)
    path = os.path.join(OUTPUT_DIR, filename)
    sorted_df.to_csv(path, index=False)
    print(f"Saved {filename} ({len(sorted_df)} rows)")

if __name__ == "__main__":
    generate_insights()
