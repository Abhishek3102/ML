from fastapi import APIRouter, HTTPException
import pandas as pd
import os

router = APIRouter()

BASE_DIR = r"c:\ML REPO GITHUB\IPL-RR-DATASET"
CLUSTERS_FILE = os.path.join(BASE_DIR, "analysis_modules", "2_Player_Clustering", "player_clusters.csv")

# Cache
_players_df = None

def get_players_df():
    global _players_df
    if _players_df is None:
        try:
            _players_df = pd.read_csv(CLUSTERS_FILE)
        except:
            _players_df = pd.DataFrame()
    return _players_df

@router.get("/")
def list_players(search: str = None, skip: int = 0, limit: int = 20):
    df = get_players_df()
    if df.empty:
        return []
        
    if search:
        # Case insensitive search
        filtered = df[df['player_name'].str.contains(search, case=False, na=False)]
    else:
        filtered = df
        
    # Return select columns
    res = filtered[['player_id', 'player_name', 'cluster_label', 'batting_avg', 'true_strike_rate', 'total_mvp']].iloc[skip : skip+limit]
    return res.to_dict(orient="records")

@router.get("/{player_id}")
def get_player_profile(player_id: int):
    df = get_players_df()
    player = df[df['player_id'] == player_id]
    if player.empty:
        raise HTTPException(status_code=404, detail="Player not found")
        
    return player.iloc[0].to_dict()

@router.get("/{player_id}/similar")
def get_similar_players(player_id: int, limit: int = 5):
    """
    Return players from the same cluster with similar MVP scores.
    """
    df = get_players_df()
    player = df[df['player_id'] == player_id]
    if player.empty:
        raise HTTPException(status_code=404, detail="Player not found")
        
    cluster = player.iloc[0]['cluster_label']
    score = player.iloc[0]['total_mvp']
    
    # Filter same cluster, exclude self
    peers = df[(df['cluster_label'] == cluster) & (df['player_id'] != player_id)].copy()
    
    # Sort by closest MVP score
    peers['score_diff'] = abs(peers['total_mvp'] - score)
    similar = peers.sort_values('score_diff').head(limit)
    
    return similar[['player_name', 'cluster_label', 'total_mvp']].to_dict(orient="records")
