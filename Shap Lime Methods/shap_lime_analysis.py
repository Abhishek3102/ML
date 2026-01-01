import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.metrics.pairwise import cosine_similarity
import shap
import lime
import lime.lime_tabular

# Setup
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def main():
    print("## 1. Load Data & EDA")
    df = pd.read_csv('train_data.csv')
    print(f"Shape: {df.shape}")
    
    # Analyzing multiple reviews per user
    reviews_per_user = df.groupby('user_id').size()
    print("\nReviews per user stats:")
    print(reviews_per_user.describe())
    
    # 2. Feature Engineering: Semantic Sentiment Extraction
    print("\n## 2. Feature Engineering")
    
    api_key = os.environ.get('GOOGLE_API_KEY')
    if api_key:
        print("Gemini API Key found. Configuring...")
        genai.configure(api_key=api_key)
        
        def get_embedding(text):
            try:
                result = genai.embed_content(
                    model="models/embedding-001",
                    content=text,
                    task_type="semantic_similarity"
                )
                return result['embedding']
            except Exception as e:
                print(f"Error embedding: {e}")
                return None

        print("Generating embeddings (sampling first 50 for sampling verification to save quota/time)...")
        # For verification, we sample. In PROD, remove .head(50)
        df_sample = df.head(50).copy() 
        df_sample['embedding'] = df_sample['review'].apply(get_embedding)
        df_sample = df_sample.dropna(subset=['embedding'])
        
        pos_anchor = get_embedding("Positive restaurant experience, delicious food, great service, loved it")
        neg_anchor = get_embedding("Negative restaurant experience, bad food, terrible service, not recommended")
        
        def get_sentiment(embedding):
            pos_sim = cosine_similarity([embedding], [pos_anchor])[0][0]
            neg_sim = cosine_similarity([embedding], [neg_anchor])[0][0]
            return 1 if pos_sim > neg_sim else 0
            
        df_sample['Sentiment'] = df_sample['embedding'].apply(get_sentiment)
        df = df_sample # Use sample for modeling
        print("Sentiment distribution (Sample):")
        print(df['Sentiment'].value_counts())
        
    else:
        print("WARNING: GOOGLE_API_KEY not found. MOCKING Embeddings/Sentiment for verification.")
        # Mock logic: "Good", "Delicious", "Loved", "Amazing" -> 1
        def mock_sentiment(text):
            text = text.lower()
            if any(x in text for x in ['good', 'delicious', 'loved', 'amazing', 'perfect', 'recommend']):
                return 1
            return 0
        df['Sentiment'] = df['review'].apply(mock_sentiment)
        print("Mock Sentiment distribution:")
        print(df['Sentiment'].value_counts())

    # 3. Modeling
    print("\n## 3. Modeling: Random Forest")
    le_gender = LabelEncoder()
    le_meal = LabelEncoder()
    
    # Check for unseen labels in future potential splits, but here we transform whole df first for simplicity in this script
    df['Gender_Code'] = le_gender.fit_transform(df['gender'])
    df['Meal_Code'] = le_meal.fit_transform(df['meal_category'])
    
    X = df[['age', 'Gender_Code', 'Meal_Code']]
    y = df['Sentiment']
    
    # If class is imbalanced or single text, standard split might fail in tiny samples.
    if len(np.unique(y)) < 2:
        print("Error: Only one class present in target. Cannot train classifier.")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # 4. SHAP
    print("\n## 4. SHAP Analysis")
    try:
        explainer = shap.TreeExplainer(clf)
        # shap_values is a list for classifier [negative_shap, positive_shap]
        shap_values = explainer.shap_values(X_test)
        
        # Determine which class we are explaining. Usually class 1.
        class_idx = 1
        if isinstance(shap_values, list):
            vals = shap_values[class_idx]
        else:
            vals = shap_values
            
        print("SHAP Summary Plot generated (saving to shap_summary.png)")
        plt.figure()
        shap.summary_plot(vals, X_test, feature_names=['Age', 'Gender', 'Meal_Category'], show=False)
        plt.savefig('shap_summary.png')
        plt.close()
    except Exception as e:
        print(f"SHAP Error: {e}")

    # 5. LIME
    print("\n## 5. LIME Analysis")
    try:
        lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=np.array(X_train),
            feature_names=['Age', 'Gender', 'Meal_Category'],
            class_names=['Negative', 'Positive'],
            mode='classification'
        )
        
        idx = 0
        # Safe check if X_test is empty
        if len(X_test) > 0:
            exp = lime_explainer.explain_instance(X_test.iloc[idx].values, clf.predict_proba, num_features=3)
            # exp.save_to_file('lime_explanation.html')
            print("LIME explanation generated (log text output below):")
            print(exp.as_list())
    except Exception as e:
        print(f"LIME Error: {e}")

if __name__ == "__main__":
    main()
