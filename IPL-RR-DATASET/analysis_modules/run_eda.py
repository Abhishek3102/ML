import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set Paths
DATA_DIR = r"c:\ML REPO GITHUB\IPL-RR-DATASET"
INPUT_FILE = os.path.join(DATA_DIR, "UPDATED CSV", "enriched_match_player_stats_v1.csv")
OUTPUT_DIR = os.path.join(DATA_DIR, "analysis_modules", "1_EDA_Plots")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_eda():
    print("Loading data for EDA...")
    df = pd.read_csv(INPUT_FILE)
    
    # Ensure numeric
    numeric_cols = ['runs_scored', 'mvp_score', 'batting_impact', 'bowling_impact', 'wicket_taken', 'consistency_score']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print("Generating Plots...")
    
    # 1. Distribution of MVP Scores
    plt.figure(figsize=(10, 6))
    sns.histplot(df['mvp_score'].dropna(), bins=30, kde=True, color='blue')
    plt.title('Distribution of MVP Scores')
    plt.xlabel('MVP Score')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(OUTPUT_DIR, 'dist_mvp_score.png'))
    plt.close()
    
    # 2. Correlation Heatmap
    plt.figure(figsize=(12, 10))
    corr_cols = ['runs_scored', 'balls_faced', 'strike_rate', 'no_of_fours', 'no_of_sixes', 
                 'wicket_taken', 'runs_conceded', 'economy', 'mvp_score']
    # Filter for columns that actually exist
    valid_corr_cols = [c for c in corr_cols if c in df.columns]
    
    # Correction: 'economy' might not be in match-level stats directly if not calc'd yet (it was in season stats).
    # Let's drop it if not present.
    
    corr_matrix = df[valid_corr_cols].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Heatmap of Key Metrics')
    plt.savefig(os.path.join(OUTPUT_DIR, 'correlation_heatmap.png'))
    plt.close()
    
    # 3. Runs vs Wickets Scatter
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='runs_scored', y='wicket_taken', alpha=0.5)
    plt.title('Runs Scored vs Wickets Taken (All-Rounder Potential)')
    plt.xlabel('Runs Scored')
    plt.ylabel('Wickets Taken')
    plt.savefig(os.path.join(OUTPUT_DIR, 'scatter_runs_wickets.png'))
    plt.close()
    
    # 4. Boxplot of MVP Score by Venue (Top 10 Venues)
    top_venues = df['venue_name'].value_counts().head(10).index
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df[df['venue_name'].isin(top_venues)], x='venue_name', y='mvp_score')
    plt.xticks(rotation=45, ha='right')
    plt.title('MVP Score Distribution by Top 10 Venues')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'boxplot_mvp_venue.png'))
    plt.close()

    print(f"EDA Complete. Plots saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    run_eda()
