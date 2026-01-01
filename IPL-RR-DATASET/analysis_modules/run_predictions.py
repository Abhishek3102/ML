import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.impute import SimpleImputer

# Paths
DATA_DIR = r"c:\ML REPO GITHUB\IPL-RR-DATASET"
MATCH_STATS_FILE = os.path.join(DATA_DIR, "UPDATED CSV", "enriched_match_player_stats_v1.csv")
CLUSTERS_FILE = os.path.join(DATA_DIR, "analysis_modules", "2_Player_Clustering", "player_clusters.csv")
OUTPUT_DIR = os.path.join(DATA_DIR, "analysis_modules", "3_Advanced_Predictions")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_predictions():
    print("Loading Data for Predictions...")
    match_df = pd.read_csv(MATCH_STATS_FILE)
    
    # Try merging with clusters if available
    if os.path.exists(CLUSTERS_FILE):
        clusters_df = pd.read_csv(CLUSTERS_FILE)
        # Merge on player_id
        match_df = pd.merge(match_df, clusters_df[['player_id', 'cluster_label']], on='player_id', how='left')
        print("Merged Player Clusters.")
    else:
        match_df['cluster_label'] = 0
        print("Clusters file not found, skipping cluster feature.")

    # --- TASK 1: MVP Prediction (Regression) ---
    print("\n--- Model Task 1: MVP Score Prediction ---")
    # Predict MVP score based on contextual features (Venue, Batting Order, Season, Cluster)
    # We avoid using 'outcome' features like runs_scored as that makes it trivial.
    
    reg_df = match_df[['mvp_score', 'batting_order', 'venue_name', 'season', 'cluster_label', 'batting_type', 'bowling_type']].copy()
    
    # Encoding
    le = LabelEncoder()
    reg_df['venue_encoded'] = le.fit_transform(reg_df['venue_name'].astype(str))
    reg_df['season_encoded'] = le.fit_transform(reg_df['season'].astype(str))
    reg_df['type_encoded'] = le.fit_transform(reg_df['batting_type'].astype(str) + "_" + reg_df['bowling_type'].astype(str))
    
    features = ['batting_order', 'venue_encoded', 'season_encoded', 'cluster_label', 'type_encoded']
    target = 'mvp_score'
    
    reg_df = reg_df.dropna(subset=[target])
    X = reg_df[features].fillna(0)
    y = reg_df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    models_reg = {
        "Ridge Regression": Ridge(),
        "Random Forest": RandomForestRegressor(n_estimators=50, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=50, random_state=42)
    }
    
    results_reg = []
    
    for name, model in models_reg.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        results_reg.append({"Model": name, "R2": r2, "RMSE": rmse})
        print(f"{name}: R2={r2:.3f}")
        
    # Plot Comparison
    res_reg_df = pd.DataFrame(results_reg)
    plt.figure(figsize=(8, 5))
    sns.barplot(data=res_reg_df, x='Model', y='R2')
    plt.title('MVP Prediction Model Comparison (R2 Score)')
    plt.savefig(os.path.join(OUTPUT_DIR, 'mvp_model_comparison.png'))
    plt.close()

    # --- TASK 2: Match Outcome Prediction (Classification) ---
    print("\n--- Model Task 2: Match Winner Prediction ---")
    # Simplified: Predict if Toss Winner wins based on Venue & Decision
    
    # Prepare Data
    clf_df = match_df[['match_id', 'toss_win_team_id', 'toss_opted', 'win_team_id', 'venue_name', 'season']].drop_duplicates().dropna()
    clf_df['toss_winner_is_winner'] = (clf_df['toss_win_team_id'] == clf_df['win_team_id']).astype(int)
    clf_df['toss_decision_bat'] = (clf_df['toss_opted'] == 'Batting').astype(int)
    clf_df['venue_encoded'] = le.fit_transform(clf_df['venue_name'].astype(str))
    clf_df['season_encoded'] = le.fit_transform(clf_df['season'].astype(str))
    
    features_c = ['toss_decision_bat', 'venue_encoded', 'season_encoded']
    target_c = 'toss_winner_is_winner'
    
    X_c = clf_df[features_c]
    y_c = clf_df[target_c]
    
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_c, y_c, test_size=0.2, random_state=42)
    
    models_clf = {
        "Logistic Regression": LogisticRegression(),
        "Random Forest": RandomForestClassifier(n_estimators=50, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=50, random_state=42) # Using Regressor for probability simulation or just classifier
    }
    # Correction: Use GB Classifier
    from sklearn.ensemble import GradientBoostingClassifier
    models_clf["Gradient Boosting"] = GradientBoostingClassifier(n_estimators=50, random_state=42)
    
    results_clf = []
    
    for name, model in models_clf.items():
        model.fit(X_train_c, y_train_c)
        y_pred_c = model.predict(X_test_c)
        acc = accuracy_score(y_test_c, np.round(y_pred_c)) # Round just in case
        results_clf.append({"Model": name, "Accuracy": acc})
        print(f"{name}: Accuracy={acc:.3f}")

    # Plot Comparison
    res_clf_df = pd.DataFrame(results_clf)
    plt.figure(figsize=(8, 5))
    sns.barplot(data=res_clf_df, x='Model', y='Accuracy')
    plt.title('Match Outcome Prediction Accuracy')
    plt.savefig(os.path.join(OUTPUT_DIR, 'match_outcome_comparison.png'))
    plt.close()
    
    # Save Models using Joblib
    import joblib
    MODELS_DIR = os.path.join(DATA_DIR, "models")
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Selecting Best Models (Assuming Random Forest for both for robustness)
    best_mvp_model = models_reg["Random Forest"]
    best_match_model = models_clf["Random Forest"]
    
    # Save MVP Model
    joblib.dump(best_mvp_model, os.path.join(MODELS_DIR, "mvp_regressor.pkl"))
    print("Saved mvp_regressor.pkl")
    
    # Save Match Model
    joblib.dump(best_match_model, os.path.join(MODELS_DIR, "match_classifier.pkl"))
    print("Saved match_classifier.pkl")
    
    # Save Encoders (We need these to transform input in API)
    # We used 'le' locally, but we re-fit it multiple times. 
    # We need separate encoders for each feature to be correct.
    # Refitting properly for export:
    
    encoders = {}
    
    # MVP Features: venue_name, season ('2022' etc), batting_type_bowling_type
    le_venue = LabelEncoder()
    le_venue.fit(match_df['venue_name'].astype(str))
    encoders['venue'] = le_venue
    
    le_season = LabelEncoder()
    le_season.fit(match_df['season'].astype(str))
    encoders['season'] = le_season
    
    le_style = LabelEncoder()
    style_series = match_df['batting_type'].astype(str) + "_" + match_df['bowling_type'].astype(str)
    le_style.fit(style_series)
    encoders['style'] = le_style
    
    joblib.dump(encoders, os.path.join(MODELS_DIR, "encoders.pkl"))
    print("Saved encoders.pkl")
    
    # Save Results CSV
    res_reg_df['Task'] = 'MVP Prediction'
    res_clf_df['Task'] = 'Match Outcome'
    final_res = pd.concat([res_reg_df, res_clf_df], ignore_index=True)
    final_res.to_csv(os.path.join(OUTPUT_DIR, 'all_model_results.csv'), index=False)
    
    print(f"Predictions Complete. Saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    run_predictions()
