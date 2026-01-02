from fastapi import APIRouter, HTTPException
import joblib
import pandas as pd
import numpy as np
import os

router = APIRouter()

# Load models on request or singleton?
# Better to load once. In modular app, we can use a lifespan event or lazy load.
# Accessing global state from main or reloading here.
# For simplicity in this script, we'll reload or use a shared state module if created.
# Let's rely on globals populated in main.py or reload for now. 
# Reloading is safer for independent modules if we don't have a dependency injector setup yet.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
# Path hell: c:\Repo\IPL\backend\app\api\v1\endpoints -> ../../../../.. -> c:\Repo\IPL
# Safer:
BASE_DIR = r"c:\ML REPO GITHUB\IPL-RR-DATASET"
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Lazy Loading Pattern
_models = {}

def get_models():
    if not _models:
        try:
            print("Loading models in Predictions Module...")
            _models['mvp'] = joblib.load(os.path.join(MODELS_DIR, "mvp_regressor.pkl"))
            _models['match'] = joblib.load(os.path.join(MODELS_DIR, "match_classifier.pkl"))
            _models['encoders'] = joblib.load(os.path.join(MODELS_DIR, "encoders.pkl"))
        except Exception as e:
            print(f"Error loading models: {e}")
    return _models

@router.get("/metadata")
def get_metadata():
    models = get_models()
    encoders = models.get('encoders')
    if not encoders:
        raise HTTPException(status_code=503, detail="Models not loaded")
        
    venues = list(encoders['venue'].classes_)
    seasons = list(encoders['season'].classes_)
    
    # Extract Teams from match data? We need a list of teams.
    # We can't get it from encoder if we didn't encode teams (we trained on toss/win flags).
    # But usually we need team names for Match Winner Prediction input.
    # In run_predictions.py, we simplisticly used 'toss_decision_bat' and 'venue'.
    # We didn't actually use Team ID in the simple model?
    # Checking run_predictions.py... 
    #   X_cFeatures: ['toss_decision_bat', 'venue_encoded', 'season_encoded']
    #   Wait, the model doesn't know WHICH teams are playing? That's a flaw in the simplified model.
    #   The user wants "Many things". I should really add Team ID to the model if possible.
    #   But for now, I must stick to what the model expects, OR return the available features.
    
    # Extract Batting and Bowling styles
    style_classes = list(encoders['style'].classes_)
    batting_styles = set()
    bowling_styles = set()
    
    for s in style_classes:
        parts = s.split('_')
        if len(parts) >= 2:
            batting_styles.add(parts[0])
            bowling_styles.add(parts[1])

    # Load Teams, Venues, Seasons strictly from matches.csv (IPL Data)
    try:
        matches_df = pd.read_csv(os.path.join(BASE_DIR, "matches.csv"))
        
        # Teams
        teams_1 = matches_df['team1'].dropna().unique().tolist()
        teams_2 = matches_df['team2'].dropna().unique().tolist()
        all_teams = sorted(list(set(teams_1 + teams_2)))
        
        # Venues
        venues = sorted(matches_df['venue'].dropna().unique().tolist())
        
        # Seasons
        seasons = sorted(matches_df['season'].astype(str).unique().tolist())
        
    except Exception as e:
        print(f"Error loading metadata from matches.csv: {e}")
        all_teams = ["Rajasthan Royals", "Chennai Super Kings", "Mumbai Indians"]
        venues = ["Wankhede Stadium", "Eden Gardens"]
        seasons = ["2023", "2024"]

    return {
        "venues": venues,
        "seasons": seasons,
        "teams": all_teams,
        "batting_styles": sorted(list(batting_styles)),
        "bowling_styles": sorted(list(bowling_styles))
    }

@router.post("/match-winner")
def predict_match_winner(venue: str, toss_decision: str, season: str):
    """
    Predict Match Winner based on Context (Simplified Model).
    Inputs:
    - venue: Name of stadium
    - toss_decision: 'Batting' or 'Fielding'
    - season: Year (e.g. '2022')
    """
    models = get_models()
    clf = models.get('match')
    enc = models.get('encoders')
    
    if not clf or not enc:
        raise HTTPException(status_code=503, detail="Model not loaded")
        
    try:
        venue_id = enc['venue'].transform([venue])[0]
    except:
        venue_id = 0
        
    try:
        season_id = enc['season'].transform([season])[0]
    except:
        season_id = 0
        
    toss_bin = 1 if toss_decision.lower() == 'batting' else 0
    
    # Feature Order: ['toss_decision_bat', 'venue_encoded', 'season_encoded']
    features = [[toss_bin, venue_id, season_id]]
    
    prob = clf.predict_proba(features)[0][1] # Probability of class 1 (Win)
    # The target in training was 'toss_winner_won'.
    # So this probability is: "Probability that the Toss Winner wins the match"
    
    return {
        "prediction_type": "Toss Winner Win Probability",
        "win_probability": float(prob),
        "message": f"Significance: {prob:.1%} chance that the team winning the toss wins match."
    }

@router.post("/fantasy-mvp")
def predict_mvp(venue: str, season: str, batting_type: str, bowling_type: str, batting_order: int):
    models = get_models()
    reg = models.get('mvp')
    enc = models.get('encoders')
    
    if not reg:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Safe Transform
    try: 
        v = enc['venue'].transform([venue])[0] 
    except: v=0
    
    try: 
        s = enc['season'].transform([season])[0] 
    except: s=0
    
    try:
        style = f"{batting_type}_{bowling_type}"
        st = enc['style'].transform([style])[0]
    except: st=0
    
    # Features: ['batting_order', 'venue_encoded', 'season_encoded', 'cluster_label', 'type_encoded']
    # Defaulting Cluster Label to 0 (Average)
    feats = [[batting_order, v, s, 0, st]]
    
    score = reg.predict(feats)[0]
    
    return {
        "predicted_mvp_score": float(score),
        "analysis": "High Score" if score > 50 else "Average Score"
    }
