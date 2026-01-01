import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os

# Paths
DATA_DIR = r"c:\ML REPO GITHUB\IPL-RR-DATASET"
INPUT_FILE = os.path.join(DATA_DIR, "UPDATED CSV", "enriched_player_season_stats_v1.csv")
OUTPUT_DIR = os.path.join(DATA_DIR, "analysis_modules", "2_Player_Clustering")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_clustering():
    print("Loading Season Stats for Clustering...")
    df = pd.read_csv(INPUT_FILE)
    
    # Select features for clustering
    # We want to identify playing styles: Aggressive vs Anchor, Eco Bowler vs Wicket Taker
    features = ['batting_avg', 'true_strike_rate', 'bowling_avg', 'economy', 'consistency_score']
    
    # Metrics cleaning
    # A bowler with 0 wickets has infinite avg. Let's replace inf with a high number (e.g., 100)
    # A batter with 0 outs has infinite avg. But here avg is usually not inf if matches > 0.
    
    cluster_df = df[features].copy()
    
    # Handling Infinity and NaNs
    cluster_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    cluster_df['bowling_avg'] = cluster_df['bowling_avg'].fillna(60) # High avg for non-bowlers
    cluster_df['economy'] = cluster_df['economy'].fillna(12) # High econ for non-bowlers? Or 0?
    # If they haven't bowled, economy is 0 in previous script. Let's keep it 0 or max?
    # Actually, for clustering, 0 economy for a non-bowler is misleading (looks like best bowler).
    # Let's set non-bowlers (0 overs) to have "Average" economy or separate them?
    # Simpler: Just fill 0s with mean or max?
    # Let's assume 0 economy means didn't bowl.
    
    cluster_df = cluster_df.fillna(0)
    
    print("Scaling Features...")
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(cluster_df)
    
    print("Running K-Means (K=5)...")
    kmeans = KMeans(n_clusters=5, random_state=42)
    clusters = kmeans.fit_predict(scaled_features)
    
    df['cluster_label'] = clusters
    
    # PCA for Visualization
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(scaled_features)
    
    df['pca_1'] = pca_result[:, 0]
    df['pca_2'] = pca_result[:, 1]
    
    print("Generating Cluster Plot...")
    plt.figure(figsize=(12, 8))
    sns.scatterplot(
        x='pca_1', y='pca_2', 
        hue='cluster_label', 
        palette='viridis', 
        data=df, 
        style='cluster_label',
        s=100, alpha=0.8
    )
    plt.title('Player Performance Clusters (PCA Projection)')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.savefig(os.path.join(OUTPUT_DIR, 'player_clusters_pca.png'))
    plt.close()
    
    # Save CSV with Labels
    output_csv = os.path.join(OUTPUT_DIR, 'player_clusters.csv')
    df.to_csv(output_csv, index=False)
    print(f"Clustering Complete. Saved to {output_csv}")
    
    # Interpretation Print
    print("\nCluster Averages:")
    print(df.groupby('cluster_label')[features].mean())

if __name__ == "__main__":
    run_clustering()
