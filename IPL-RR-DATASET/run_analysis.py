import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

# Set paths
DATA_DIR = r"c:\ML REPO GITHUB\IPL-RR-DATASET"
OUTPUT_DIR = os.path.join(DATA_DIR, "UPDATED CSV")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    print("Loading data...")
    matches = pd.read_csv(os.path.join(DATA_DIR, "matches.csv"))
    players = pd.read_csv(os.path.join(DATA_DIR, "players.csv"))
    competitions = pd.read_csv(os.path.join(DATA_DIR, "competitions.csv"))
    
    # encoding='latin1' might be needed for some names, but defaulting to utf-8 first
    try:
        stats = pd.read_csv(os.path.join(DATA_DIR, "player_match_stats.csv"))
    except UnicodeDecodeError:
        stats = pd.read_csv(os.path.join(DATA_DIR, "player_match_stats.csv"), encoding='latin1')
    
    return matches, players, stats, competitions

def process_data(matches, players, stats, competitions):
    print("Processing data...")
    
    # Merge Matches with Competitions to get Season
    matches = pd.merge(matches, competitions[['comp_id', 'season']], on='comp_id', how='left')
    
    # Merge Stats with Matches
    # Ensure column names match. matches.csv has 'match_id', stats has 'match_id'
    # Note: stats might already have match_date, but matches.csv has the authoritative info
    merged = pd.merge(stats, matches[['match_id', 'season', 'venue_name', 'home_team', 'away_team', 'toss_win_team_id', 'toss_opted', 'win_team_id', 'result']], on='match_id', how='left')
    
    # Merge with Players
    # players.csv has 'player_id'. stats has 'player_id'
    merged = pd.merge(merged, players[['player_id', 'batting_type', 'bowling_type', 'nationality']], on='player_id', how='left')
    
    # Cleaning
    # Fill NaN for numeric columns that might be naturally 0
    fill_zeros = ['runs_scored', 'balls_faced', 'no_of_sixes', 'no_of_fours', 'overs_bowled', 'runs_conceded', 'wicket_taken', 'maiden_overs_bowled', 'dot_balls_bowled', 'number_of_catches_taken', 'number_of_stumping']
    for col in fill_zeros:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0)
            
    # --- Metric Calculations ---
    
    # Batting Impact Score
    # Formula: (Runs * SR/100) + (4s * 1) + (6s * 2) + (50 * 5) + (100 * 10) 
    # Note: Strike Rate in CSV might be string or float. Handle conversion.
    merged['strike_rate'] = pd.to_numeric(merged['strike_rate'], errors='coerce').fillna(0)
    
    merged['batting_impact'] = (
        (merged['runs_scored'] * merged['strike_rate'] / 100) + 
        (merged['no_of_fours'] * 1) + 
        (merged['no_of_sixes'] * 2)
    )
    
    # Bowling Impact Score
    # Formula: (Wickets * 20) + (Dots * 1) - (Runs Conceded / (Overs + 0.1)) # + 0.1 to avoid div by zero? Or check overs > 0
    # Let's handle Economy separately
    merged['overs_bowled'] = pd.to_numeric(merged['overs_bowled'], errors='coerce').fillna(0)
    merged['economy_rate'] = pd.to_numeric(merged['economy_rate'], errors='coerce').fillna(0) # Or calc derived
    
    # Helper for Bowling Impact
    # If overs > 0: Impact = Wickets*20 + Dots*1 - (Runs/Overs)
    # Else: 0
    def calc_bowl_impact(row):
        if row['overs_bowled'] > 0:
            return (row['wicket_taken'] * 20) + (row['dot_balls_bowled'] * 1) - (row['runs_conceded'] / row['overs_bowled'])
        return 0
    
    merged['bowling_impact'] = merged.apply(calc_bowl_impact, axis=1)
    
    # Fielding Points
    merged['fielding_points'] = (merged['number_of_catches_taken'] * 8) + (merged['number_of_stumping'] * 12)
    
    # MVP Score
    merged['mvp_score'] = merged['batting_impact'] + merged['bowling_impact'] + merged['fielding_points']
    
    # Boundary Percentage
    merged['boundary_pct'] = np.where(merged['balls_faced'] > 0, (merged['no_of_fours'] + merged['no_of_sixes']) / merged['balls_faced'] * 100, 0)
    
    # Dot Ball Percentage
    # Balls Bowled needs to be converted from Overs (4.1 overs = 25 balls? No, usually overs is e.g. 4.0 or 4.1 in rare cases if match abd? Assuming standard 4.0 = 24 balls)
    # Simplification: Overs * 6. (Fractional overs e.g. 3.2 is 3*6 + 2 = 20 balls). 
    # Let's approximate Overs*6 for now as the 'balls_bowled' column isn't explicitly listed in viewed file, but 'overs_bowled' is.
    merged['balls_bowled_est'] = merged['overs_bowled'] * 6 # Rough approx
    merged['dot_ball_pct'] = np.where(merged['balls_bowled_est'] > 0, merged['dot_balls_bowled'] / merged['balls_bowled_est'] * 100, 0)
    
    return merged

def create_season_stats(match_stats):
    print("Aggregating season stats...")
    
    # Group by Player and Season
    # Using 'batting_type' and 'bowling_type' based on players.csv
    season_grp = match_stats.groupby(['season', 'player_id', 'player_name', 'nationality', 'batting_type', 'bowling_type'])
    
    summary = season_grp.agg(
        matches=('match_id', 'count'),
        total_runs=('runs_scored', 'sum'),
        total_balls_faced=('balls_faced', 'sum'),
        total_fours=('no_of_fours', 'sum'),
        total_sixes=('no_of_sixes', 'sum'),
        total_wickets=('wicket_taken', 'sum'),
        total_overs=('overs_bowled', 'sum'),
        total_runs_conceded=('runs_conceded', 'sum'),
        total_catches=('number_of_catches_taken', 'sum'),
        total_mvp=('mvp_score', 'sum'),
        mvp_std=('mvp_score', 'std') # For Consistency
    ).reset_index()
    
    # Derived Season Metrics
    summary['batting_avg'] = summary['total_runs'] / summary['matches'] # Simplified (assuming Out every match for now, or we'd need Not Out count)
    summary['true_strike_rate'] = np.where(summary['total_balls_faced'] > 0, (summary['total_runs'] / summary['total_balls_faced']) * 100, 0)
    summary['bowling_avg'] = np.where(summary['total_wickets'] > 0, summary['total_runs_conceded'] / summary['total_wickets'], np.inf)
    summary['economy'] = np.where(summary['total_overs'] > 0, summary['total_runs_conceded'] / summary['total_overs'], 0)
    
    # Consistency Score (Inverse of CV or StdDev? User asked for 1/StdDev)
    summary['consistency_score'] = np.where(summary['mvp_std'] > 0, 100 / summary['mvp_std'], 0) # Scaled by 100 for readability
    
    return summary

def print_top_15(season_stats, match_stats):
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    print("\n--- TOP 15: BATTING AVERAGE (Min 10 Matches) ---")
    qualified_bat = season_stats[season_stats['matches'] >= 10]
    print(qualified_bat.sort_values('batting_avg', ascending=False)[['player_name', 'season', 'matches', 'total_runs', 'batting_avg']].head(15))
    
    print("\n--- TOP 15: TRUE STRIKE RATE (Min 100 Balls) ---")
    qualified_sr = season_stats[season_stats['total_balls_faced'] >= 100]
    print(qualified_sr.sort_values('true_strike_rate', ascending=False)[['player_name', 'season', 'total_balls_faced', 'true_strike_rate']].head(15))
    
    print("\n--- TOP 15: BOWLING AVERAGE (Min 10 Wickets) ---")
    qualified_bowl = season_stats[season_stats['total_wickets'] >= 10]
    # Filter out inf
    qualified_bowl = qualified_bowl[qualified_bowl['bowling_avg'] != np.inf]
    print(qualified_bowl.sort_values('bowling_avg', ascending=True)[['player_name', 'season', 'total_wickets', 'bowling_avg']].head(15))

    print("\n--- TOP 15: MVP SCORE (Season) ---")
    print(season_stats.sort_values('total_mvp', ascending=False)[['player_name', 'season', 'matches', 'total_mvp']].head(15))

    print("\n--- TOP 15: CONSISTENCY SCORE (Min 10 Matches) ---")
    print(qualified_bat.sort_values('consistency_score', ascending=False)[['player_name', 'season', 'total_mvp', 'consistency_score']].head(15))


def train_models(match_stats):
    print("\n--- Training ML Models ---")
    
    # --- Model 1: MVP Prediction (Regression) ---
    print("Training Model 1: Player MVP Score Prediction...")
    
    # Feature Selection for Regression
    # Predict MVP score of a player in a match
    # Features: Batting Order, Opposition?, Venue?, Historical Avg?
    
    # Simple features for demonstration
    model_df = match_stats.dropna(subset=['mvp_score', 'batting_order'])
    
    # Encode categorical
    le_venue = LabelEncoder()
    model_df['venue_encoded'] = le_venue.fit_transform(model_df['venue_name'].astype(str))
    
    le_season = LabelEncoder()
    model_df['season_encoded'] = le_season.fit_transform(model_df['season'].astype(str))
    
    le_role = LabelEncoder()
    model_df['style_encoded'] = le_role.fit_transform(model_df['batting_type'].astype(str) + "_" + model_df['bowling_type'].astype(str))
    
    features = ['batting_order', 'venue_encoded', 'style_encoded', 'season_encoded']
    target = 'mvp_score'
    
    X = model_df[features]
    y = model_df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    regressor = RandomForestRegressor(n_estimators=100, random_state=42)
    regressor.fit(X_train, y_train)
    
    y_pred = regressor.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"MVP Prediction - MSE: {mse:.2f}, R2 Score: {r2:.2f}")
    
    # --- Model 2: Match Winner Classification ---
    print("\nTraining Model 2: Match Winner Prediction...")
    
    # Prepare Match Level Data
    # Aggregating team stats per match
    # We need features like: Team Avg MVP, Toss Win
    
    # match_level = match_stats.groupby(['match_id', 'win_team_id']).agg(...) 
    # This is complex because we need Home Team vs Away Team structure.
    # Simplified approach: Predict if Toss Winner wins the match
    
    match_outcomes = match_stats[['match_id', 'toss_win_team_id', 'toss_opted', 'win_team_id', 'venue_name']].drop_duplicates()
    match_outcomes['toss_decision_encoded'] = (match_outcomes['toss_opted'] == 'Batting').astype(int)
    
    # Target: Did Toss Winner Win?
    # Note: win_team_id might be ID, toss_winner might be ID. Check types.
    # Assuming they are comparable.
    match_outcomes['toss_winner_won'] = (match_outcomes['toss_win_team_id'] == match_outcomes['win_team_id']).astype(int)
    
    le_venue_clf = LabelEncoder()
    match_outcomes['venue_encoded'] = le_venue_clf.fit_transform(match_outcomes['venue_name'].astype(str))
    
    X_clf = match_outcomes[['toss_decision_encoded', 'venue_encoded']]
    y_clf = match_outcomes['toss_winner_won']
    
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_clf, y_clf, test_size=0.2, random_state=42)
    
    clf = GradientBoostingClassifier(random_state=42)
    clf.fit(X_train_c, y_train_c)
    
    y_pred_c = clf.predict(X_test_c)
    acc = accuracy_score(y_test_c, y_pred_c)
    print(f"Match Winner Prediction (Based on Toss/Venue) - Accuracy: {acc:.2f}")
    print(classification_report(y_test_c, y_pred_c))

def main():
    matches, players, stats, competitions = load_data()
    
    enriched_match_stats = process_data(matches, players, stats, competitions)
    
    season_stats = create_season_stats(enriched_match_stats)
    
    # Save CSVs
    print(f"Saving enriched CSVs to {OUTPUT_DIR}...")
    enriched_match_stats.to_csv(os.path.join(OUTPUT_DIR, "enriched_match_player_stats_v1.csv"), index=False)
    season_stats.to_csv(os.path.join(OUTPUT_DIR, "enriched_player_season_stats_v1.csv"), index=False)
    
    # Reporting
    print_top_15(season_stats, enriched_match_stats)
    
    # Machine Learning
    train_models(enriched_match_stats)
    
    print("Analysis Complete.")

if __name__ == "__main__":
    main()
