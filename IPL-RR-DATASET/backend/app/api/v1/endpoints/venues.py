from fastapi import APIRouter, HTTPException
import pandas as pd
import os
import joblib

router = APIRouter()

BASE_DIR = r"c:\ML REPO GITHUB\IPL-RR-DATASET"
MATCHES_PATH = os.path.join(BASE_DIR, "matches.csv")

# Simple In-Memory Cache for aggregated venue stats
_venue_stats_cache = None

def load_venue_stats():
    global _venue_stats_cache
    if _venue_stats_cache is not None:
        return _venue_stats_cache
        
    try:
        df = pd.read_csv(MATCHES_PATH)
        
        # Filter for IPL matches if possible? Or use all T20s. 
        # Dataset seems to be mostly IPL/T20. Let's use all for robust stats.
        
        # Aggregation Logic
        # 1. Total Matches per Venue
        venue_counts = df['venue_name'].value_counts()
        
        # 2. Win % Batting First vs Chasing
        # We need to determine if the winner batted first or second.
        # matches.csv has 'first_inn_bat_team_id', 'toss_win_team_id', 'toss_opted', 'win_team_id'
        
        # Create a derived column: Did Batting First Team Win?
        # If win_team_id == first_inn_bat_team_id -> Bat 1st Won.
        
        df['bat_first_win'] = df['win_team_id'] == df['first_inn_bat_team_id']
        
        # Group by Venue
        stats = []
        for venue in df['venue_name'].unique():
            v_df = df[df['venue_name'] == venue]
            total = len(v_df)
            if total < 5: continue # Skip venues with too few matches
            
            bat_first_wins = v_df['bat_first_win'].sum()
            bat_second_wins = total - bat_first_wins # Approximation (ignoring ties/NR)
            
            # Toss Bias: How often does Toss Winner win the match?
            toss_wins = (v_df['toss_win_team_id'] == v_df['win_team_id']).sum()
            
            stats.append({
                "venue_name": venue,
                "total_matches": int(total),
                "bat_first_win_pct": float(bat_first_wins / total * 100),
                "toss_win_impact": float(toss_wins / total * 100)
            })
            
        _venue_stats_cache = pd.DataFrame(stats).set_index("venue_name")
        return _venue_stats_cache
        
    except Exception as e:
        print(f"Error loading venue stats: {e}")
        return pd.DataFrame()

@router.get("/{venue_name}")
def get_venue_stats(venue_name: str):
    stats_df = load_venue_stats()
    
    if venue_name not in stats_df.index:
        # Fuzzy match or return generic error
        # Try finding closest match? For now, strict.
        raise HTTPException(status_code=404, detail="Venue not found")
        
    data = stats_df.loc[venue_name]
    return {
        "venue": venue_name,
        "total_matches": int(data['total_matches']),
        "bat_first_win_pct": round(data['bat_first_win_pct'], 1),
        "chasing_win_pct": round(100 - data['bat_first_win_pct'], 1),
        "toss_win_impact": round(data['toss_win_impact'], 1),
        "avg_score_estimate": 165 # Hardcoded for now, computing from player_match_stats is heavy
    }
