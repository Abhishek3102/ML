from fastapi import APIRouter
import pandas as pd
import os

router = APIRouter()

BASE_DIR = r"c:\ML REPO GITHUB\IPL-RR-DATASET"
STATS_DIR = os.path.join(BASE_DIR, "UPDATED CSV", "insights")

@router.get("/leaders/{category}")
def get_leaders(category: str, limit: int = 10):
    """
    Categories: runs, wickets, mvp, strike_rate
    """
    files_map = {
        "runs": "highest_run_getters.csv",
        "wickets": "highest_wicket_takers.csv",
        "mvp": "mvp_leaders.csv",
        "strike_rate": "highest_strike_rate_batters.csv",
        "sixes": "highest_boundary_pct_batters.csv" # Approx
    }
    
    filename = files_map.get(category)
    if not filename:
        return {"error": "Invalid category"}
        
    try:
        df = pd.read_csv(os.path.join(STATS_DIR, filename))
        return df.head(limit).to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}
