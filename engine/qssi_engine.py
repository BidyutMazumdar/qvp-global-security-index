import pandas as pd
import os

# =========================
# CONFIG
# =========================
DATA_PATH = "data/qssi_dataset.csv"
OUTPUT_PATH = "data/qssi_ranking.csv"

WEIGHTS = {
    "PQC": 0.25,
    "AI": 0.25,
    "LEGAL": 0.25,
    "RES": 0.25
}

# =========================
# CORE FUNCTIONS
# =========================
def compute_qssi(row):
    return (
        WEIGHTS["PQC"] * row["PQC"] +
        WEIGHTS["AI"] * row["AI"] +
        WEIGHTS["LEGAL"] * row["LEGAL"] +
        WEIGHTS["RES"] * row["RES"]
    )

def risk_adjust(score, risk):
    return score * (1 - risk)

def assign_tier(score):
    if score >= 90:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 50:
        return "C"
    return "D"

# =========================
# MAIN PIPELINE
# =========================
def main():
    # Check file exists
    if not os.path.exists(DATA_PATH):
        print("❌ Dataset not found:", DATA_PATH)
        return

    df = pd.read_csv(DATA_PATH)

    # Compute scores
    df["QSSI"] = df.apply(compute_qssi, axis=1)
    df["QSSI_scaled"] = df["QSSI"] * 100

    # Risk adjustment
    df["QSSI_adj"] = df.apply(lambda x: risk_adjust(x["QSSI"], x["Risk"]), axis=1)
    df["QSSI_adj_scaled"] = df["QSSI_adj"] * 100

    # Ranking
    df = df.sort_values(by="QSSI_adj_scaled", ascending=False)
    df["Rank"] = range(1, len(df) + 1)

    # Tier classification
    df["Tier"] = df["QSSI_scaled"].apply(assign_tier)

    # Save output
    df.to_csv(OUTPUT_PATH, index=False)

    # Display top 10
    print("\n🌍 TOP 10 COUNTRIES:\n")
    print(df[["Rank", "Country", "QSSI_adj_scaled", "Tier"]].head(10))

    print(f"\n✅ Ranking saved to: {OUTPUT_PATH}")

# =========================
if __name__ == "__main__":
    main()
