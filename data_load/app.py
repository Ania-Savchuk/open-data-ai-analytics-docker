import os
import time
import pandas as pd
from sqlalchemy import create_engine
import requests
import zipfile
import io

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "analytics_db")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
TABLE_NAME = os.getenv("TABLE_NAME", "dataset")

DATA_URL = os.getenv("DATA_URL", "https://data.gov.ua/dataset/0ffd8b75-0628-48cc-952a-9302f9799ec0/resource/3f13166f-090b-499e-8e23-e9851c5a5f67/download/reestrtz2026.zip")
CSV_PATH = os.getenv("CSV_PATH", "/app/data/dataset.csv")


def wait_for_db(engine):
    for i in range(10):
        try:
            engine.connect()
            print("--- Database is ready! ---")
            return True
        except Exception:
            print(f"Waiting for database... ({i + 1}/10)")
            time.sleep(5)
    return False


def load_and_import():
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    print("--- Downloading data ---")
    response = requests.get(DATA_URL, stream=True)

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        csv_files = [f for f in z.namelist() if f.endswith('.csv')]
        if csv_files:
            z.extract(csv_files[0], os.path.dirname(CSV_PATH))
            os.rename(os.path.join(os.path.dirname(CSV_PATH), csv_files[0]), CSV_PATH)

    df = pd.read_csv(CSV_PATH, sep=";", encoding="utf-8", low_memory=False)
    print(f"--- Loaded {len(df)} rows from CSV ---")

    conn_str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(conn_str)

    if wait_for_db(engine):
        df.to_sql(TABLE_NAME, engine, if_exists='replace', index=False)
        print(f"--- Success! Data imported into table '{TABLE_NAME}' ---")


if __name__ == "__main__":
    load_and_import()