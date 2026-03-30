from fastapi import FastAPI
import pandas as pd
import os

app = FastAPI(title="QVP Global Security Index API")

# =========================
# CONFIG
# =========================
DATA_PATH = "data/qssi_data.csv"

# =========================
# CORE ENGINE
# =========================
def compute_qssi(df):
    # QSSI calculation
    df["QSSI"] = df[["PQC", "AI", "LEGAL", "RES"]].mean(axis=1)

    # Risk adjustment
    df["QSSI_adj"] = df["QSSI"] * (1 - df["Risk"])
    df["QSSI_adj_scaled"] = df["QSSI_adj"] * 100

    # Ranking
    df = df.sort_values(by="QSSI_adj_scaled", ascending=False)
    df["Rank"] = range(1, len(df) + 1)

    # Tier classification
    def tier(x):
        if x >= 90:
            return "A"
        elif x >= 75:
            return "B"
        elif x >= 50:
            return "C"
        else:
            return "D"

    df["Tier"] = df["QSSI_adj_scaled"].apply(tier)

    return df


# =========================
# LOAD DATA (OPTIMIZED)
# =========================
def load_data():
    if not os.path.exists(DATA_PATH):
        return None
    df = pd.read_csv(DATA_PATH)
    return compute_qssi(df)


# =========================
# ROOT
# =========================
@app.get("/")
def home():
    return {
        "system": "QVP Global Security Index",
        "status": "active",
        "endpoints": ["/ranking", "/top10", "/stats", "/country/{name}"]
    }


# =========================
# FULL RANKING
# =========================
@app.get("/ranking")
def get_ranking():
    df = load_data()
    if df is None:
        return {"error": "Dataset not found"}

    return {
        "total_countries": len(df),
        "ranking": df.to_dict(orient="records")
    }


# =========================
# TOP 10
# =========================
@app.get("/top10")
def top10():
    df = load_data()
    if df is None:
        return {"error": "Dataset not found"}

    return df.head(10).to_dict(orient="records")


# =========================
# STATS
# =========================
@app.get("/stats")
def stats():
    df = load_data()
    if df is None:
        return {"error": "Dataset not found"}

    return {
        "mean": float(df["QSSI_adj_scaled"].mean()),
        "variance": float(df["QSSI_adj_scaled"].var())
    }


# =========================
# COUNTRY SEARCH (NEW)
# =========================
@app.get("/country/{name}")
def get_country(name: str):
    df = load_data()
    if df is None:
        return {"error": "Dataset not found"}

    row = df[df["Country"].str.lower() == name.lower()]

    if row.empty:
        return {"error": "Country not found"}

    return row.to_dict(orient="records")
