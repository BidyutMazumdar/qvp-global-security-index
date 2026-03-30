from fastapi import FastAPI
import pandas as pd
import os

app = FastAPI(title="QVP Global Security Index API")

# =========================
# CONFIG
# =========================
DATA_PATH = "data/qssi_ranking.csv"

# =========================
# ROOT
# =========================
@app.get("/")
def home():
    return {
        "message": "QVP Global Security Index API is running",
        "endpoints": ["/ranking", "/top10"]
    }

# =========================
# FULL RANKING
# =========================
@app.get("/ranking")
def get_ranking():
    if not os.path.exists(DATA_PATH):
        return {
            "error": "Ranking file not found. Please run engine first."
        }

    df = pd.read_csv(DATA_PATH)

    return {
        "total_countries": len(df),
        "data": df.to_dict(orient="records")
    }

# =========================
# TOP 10
# =========================
@app.get("/top10")
def top10():
    if not os.path.exists(DATA_PATH):
        return {
            "error": "Ranking file not found. Please run engine first."
        }

    df = pd.read_csv(DATA_PATH)

    top = df.sort_values(
        by="QSSI_adj_scaled",
        ascending=False
    ).head(10)

    return {
        "count": len(top),
        "top_10": top.to_dict(orient="records")
    }
