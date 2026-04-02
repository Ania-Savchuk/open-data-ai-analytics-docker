import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import json
from datetime import datetime

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "analytics_db")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
TABLE_NAME = os.getenv("TABLE_NAME", "dataset")


def get_data():
    conn_str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(conn_str)
    return pd.read_sql(TABLE_NAME, engine)


def run_visualization():
    try:
        df = get_data()
    except Exception as e:
        print(f"Помилка: {e}")
        return

    os.makedirs("/app/plots", exist_ok=True)
    os.makedirs("/app/reports", exist_ok=True)

    df["D_REG"] = pd.to_datetime(df["D_REG"], format="%d.%m.%y", errors="coerce")
    df["MAKE_YEAR"] = pd.to_numeric(df["MAKE_YEAR"], errors="coerce")
    df["CAPACITY"] = pd.to_numeric(df["CAPACITY"], errors="coerce")
    df["OWN_WEIGHT"] = pd.to_numeric(df["OWN_WEIGHT"], errors="coerce")
    df["TOTAL_WEIGHT"] = pd.to_numeric(df["TOTAL_WEIGHT"], errors="coerce")

    sns.set(style="whitegrid")

    plt.figure(figsize=(12, 8))
    top_brands = df["BRAND"].value_counts().head(20)
    sns.barplot(x=top_brands.values, y=top_brands.index, palette="viridis")
    plt.title("Top 20 Car Brands")
    plt.savefig("/app/plots/01_top_brands.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.histplot(df["MAKE_YEAR"].dropna(), bins=30, kde=True, color="blue")
    plt.title("Distribution of Car Manufacturing Year")
    plt.savefig("/app/plots/02_make_year_dist.png")
    plt.close()

    plt.figure(figsize=(12, 6))
    fuel_counts = df["FUEL"].value_counts().head(10)
    sns.barplot(x=fuel_counts.index, y=fuel_counts.values, palette="magma")
    plt.title("Fuel Type Distribution")
    plt.xticks(rotation=45)
    plt.savefig("/app/plots/03_fuel_dist.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.histplot(df[df["CAPACITY"] < 6000]["CAPACITY"].dropna(), bins=40, color="orange")
    plt.title("Engine Capacity Distribution (up to 6000cc)")
    plt.savefig("/app/plots/04_capacity_dist.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.histplot(df["OWN_WEIGHT"].dropna(), bins=40, color="green")
    plt.title("Vehicle Weight Distribution")
    plt.savefig("/app/plots/05_weight_dist.png")
    plt.close()

    plt.figure(figsize=(12, 7))
    top_models = df["MODEL"].value_counts().head(15)
    sns.barplot(x=top_models.values, y=top_models.index, palette="rocket")
    plt.title("Top 15 Car Models")
    plt.savefig("/app/plots/06_top_models.png")
    plt.close()

    plt.figure(figsize=(12, 7))
    body_counts = df["BODY"].value_counts().head(15)
    sns.barplot(x=body_counts.values, y=body_counts.index, palette="cubehelix")
    plt.title("Body Type Distribution")
    plt.savefig("/app/plots/07_body_dist.png")
    plt.close()

    plt.figure(figsize=(10, 8))
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    corr = df[numeric_cols].corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix")
    plt.savefig("/app/plots/08_correlation_matrix.png")
    plt.close()

    plt.figure(figsize=(14, 7))
    sns.boxplot(x="FUEL", y="CAPACITY", data=df[df["CAPACITY"] < 6000])
    plt.xticks(rotation=45)
    plt.title("Engine Capacity by Fuel Type (Filtered < 6000cc)")
    plt.tight_layout()
    plt.savefig("/app/plots/09_capacity_by_fuel.png")
    plt.close()

    summary_report = {
        "report_name": "Comprehensive Visualization Report",
        "timestamp": datetime.now().isoformat(),
        "dataset_size": len(df),
        "statistics": {
            "avg_make_year": round(df["MAKE_YEAR"].mean(), 1) if "MAKE_YEAR" in df.columns else None,
            "avg_capacity": round(df["CAPACITY"].mean(), 1) if "CAPACITY" in df.columns else None,
            "avg_weight": round(df["OWN_WEIGHT"].mean(), 1) if "OWN_WEIGHT" in df.columns else None
        },
        "top_market_leaders": top_brands.head(5).to_dict(),
        "generated_plots": [
            "01_top_brands.png", "02_make_year_dist.png", "03_fuel_dist.png",
            "04_capacity_dist.png", "05_weight_dist.png", "06_top_models.png",
            "07_body_dist.png", "08_correlation_matrix.png", "09_capacity_by_fuel.png"
        ]
    }

    with open("/app/reports/visualization_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=4, ensure_ascii=False)

    print(f"--- Visualization complete! 9 graphs and JSON report generated. ---")


if __name__ == "__main__":
    run_visualization()