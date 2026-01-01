from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .predictions import get_models
import pandas as pd
import os
import joblib

router = APIRouter()

BASE_DIR = r"c:\ML REPO GITHUB\IPL-RR-DATASET"
MAPPING_PATH = os.path.join(BASE_DIR, "player_competition_team_mapping.csv")
PLAYERS_PATH = os.path.join(BASE_DIR, "players.csv")

# Cache for rosters
_roster_cache = None
_player_meta_cache = None

class FantasyRequest(BaseModel):
    team_a: str
    team_b: str
    venue: str
    season: str

def load_rosters():
    global _roster_cache, _player_meta_cache
    if _roster_cache is not None:
        return _roster_cache, _player_meta_cache
        
    try:
        # Load Mapping
        df_map = pd.read_csv(MAPPING_PATH)
        
        # Don't filter by latest_comp, as different leagues/years have different IDs.
        # Instead, aggregate ALL players who have ever played for a specific team name.
        # Use set to remove duplicates.
        rosters = df_map.groupby('team_name')['player_name'].apply(lambda x: list(set(x))).to_dict()
        
        # Load Player Metadata (Batting/Bowling Styles)
        df_p = pd.read_csv(PLAYERS_PATH)
        # Handle duplicates in players.csv?
        df_p = df_p.drop_duplicates(subset=['player_name'])
        player_meta = df_p.set_index('player_name')[['batting_type', 'bowling_type']].to_dict('index')
        
        _roster_cache = rosters
        _player_meta_cache = player_meta
        return rosters, player_meta
        
    except Exception as e:
        print(f"Error loading rosters: {e}")
        return {}, {}

@router.post("/generate")
def generate_fantasy_team(req: FantasyRequest):
    """
    Generate Top 11 Players from Team A and Team B for a given Venue.
    """
    team_a = req.team_a
    team_b = req.team_b
    venue = req.venue
    season = req.season
    rosters, player_meta = load_rosters()
    models = get_models()
    reg = models.get('mvp')
    enc = models.get('encoders')
    
    if not reg or not enc:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Fetch Squads
    squad_a = rosters.get(team_a, [])
    squad_b = rosters.get(team_b, [])
    
    all_teams = list(rosters.keys())

    if not squad_a:
         # Fuzzy match A
         matches_a = [t for t in all_teams if team_a in t]
         if matches_a: squad_a = rosters[matches_a[0]]

    if not squad_b:
         # Fuzzy match B
         matches_b = [t for t in all_teams if team_b in t]
         if matches_b: squad_b = rosters[matches_b[0]]

    all_players = squad_a + squad_b
    if not all_players:
        raise HTTPException(status_code=404, detail="Teams not found in roster data")

    predictions = []
    
    # Pre-encode context
    try: v_enc = enc['venue'].transform([venue])[0]
    except: v_enc = 0
    
    try: s_enc = enc['season'].transform([season])[0]
    except: s_enc = 0

    for player in all_players:
        meta = player_meta.get(player, {'batting_type': 'Right-hand bat', 'bowling_type': 'Right-arm medium'})
        
        # Parse styles for encoder (which expects "Right Hand Bat_Right-arm medium" format)
        # Note: metadata might be "Right-hand bat" but encoder expects "Right Hand Bat". Normalization needed?
        # Let's simple-case it or try raw.
        
        b_type = meta.get('batting_type', 'Right Hand Bat') 
        bw_type = meta.get('bowling_type', 'Right-arm medium')
        
        # Normalize simple differences if known, else raw
        style_str = f"{b_type}_{bw_type}"
        
        try: st_enc = enc['style'].transform([style_str])[0]
        except: st_enc = 0 # Fallback to 0 if style not seen in training
        
        # Predict
        # Feature vector: [batting_order, venue, season, cluster, style]
        # Batting order is unknown. Assume average (5).
        feats = [[5, v_enc, s_enc, 0, st_enc]] 
        score = reg.predict(feats)[0]
        
        predictions.append({
            "player": player,
            "team": team_a if player in squad_a else team_b,
            "role": b_type, # Simplification
            "predicted_points": float(score)
        })
        
    # Sort and pick Top 11
    predictions.sort(key=lambda x: x['predicted_points'], reverse=True)
    dream_team = predictions[:11]
    
    return {
        "venue": venue,
        "teams": [team_a, team_b],
        "dream_team": dream_team
    }
