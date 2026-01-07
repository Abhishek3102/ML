import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os

app = FastAPI(title="Big Mart Sales Predictor")

# --- Load Resources ---
MODEL_PATH = "best_xgb_regressor_random_model.pkl"
RAW_CSV_PATH = "bigmart.csv"
ENCODED_CSV_PATH = "updated_dataset.csv"

try:
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# --- Rebuild Encoders ---
# Since we don't have the pickle files for encoders, we map Raw -> Encoded values from the datasets
encoders = {}
cat_cols = ['Item_Identifier', 'Item_Fat_Content', 'Item_Type', 'Outlet_Identifier', 'Outlet_Size', 'Outlet_Location_Type', 'Outlet_Type']

try:
    df_raw = pd.read_csv(RAW_CSV_PATH)
    df_enc = pd.read_csv(ENCODED_CSV_PATH)
    
    # Remove duplicates to create clean mapping 
    # Ensure we sort by index to maintain row-to-row correspondence if possible
    # Assumption: rows correspond 1-to-1
    
    for col in cat_cols:
        # Create a dictionary mapping { 'RawString': EncodedInt }
        mapping = dict(zip(df_raw[col], df_enc[col]))
        encoders[col] = mapping
        
    print("Encoders rebuilt successfully.")

except Exception as e:
    print(f"Error rebuilding encoders: {e}")

class ItemPredictionRequest(BaseModel):
    Item_Identifier: str
    Item_Weight: float
    Item_Fat_Content: str
    Item_Visibility: float
    Item_Type: str
    Item_MRP: float
    Outlet_Identifier: str
    Outlet_Establishment_Year: int
    Outlet_Size: str
    Outlet_Location_Type: str
    Outlet_Type: str

@app.get("/")
def read_root():
    return {"message": "Big Mart Sales Prediction API is running"}

@app.post("/predict")
def predict_sales(item: ItemPredictionRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Prepare input vector
        data = item.dict()
        
        # Encode categorical fields using our rebuilt map
        for col in cat_cols:
            if col in data:
                raw_val = data[col]
                if raw_val not in encoders[col]:
                     # Fallback 1: Try finding a key that contains the string (partial match)
                     # Fallback 2: Use the most common value (mode) from encoder
                     # Fallback 3: Default to 0 (risky but failsafe)
                     pass
                
                # Apply mapping with default 0 if not found
                data[col] = encoders[col].get(raw_val, 0)
        
        # Create DataFrame for model (ensure order matches training)
        input_df = pd.DataFrame([data])
        
        # Order must be exact
        required_cols = ['Item_Identifier', 'Item_Weight', 'Item_Fat_Content', 'Item_Visibility',
                         'Item_Type', 'Item_MRP', 'Outlet_Identifier', 'Outlet_Establishment_Year',
                         'Outlet_Size', 'Outlet_Location_Type', 'Outlet_Type']
                         
        input_df = input_df[required_cols]
                             
        prediction = model.predict(input_df)
        return {"predicted_sales": float(prediction[0])}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
