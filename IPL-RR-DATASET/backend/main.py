from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import predictions, players, analytics, venues, fantasy

app = FastAPI(title="IPL Advanced Analytics Platform", version="2.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(predictions.router, prefix="/api/v1/predict", tags=["Predictions"])
app.include_router(players.router, prefix="/api/v1/players", tags=["Players"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(venues.router, prefix="/api/v1/venues", tags=["Venues"])
app.include_router(fantasy.router, prefix="/api/v1/fantasy", tags=["Fantasy"])

@app.get("/")
def home():
    return {
        "message": "Welcome to IPL Analytics Phase 3 API",
        "docs": "/docs",
        "modules": ["Predictions", "Players", "Analytics"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
