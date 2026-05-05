import os
import json
import pandas as pd
from flask import Flask, render_template, send_from_directory
from prometheus_flask_exporter import PrometheusMetrics  # ДОДАНО
app = Flask(__name__)
# Ініціалізація метрик (автоматично створює ендпоінт /metrics)
metrics = PrometheusMetrics(app)
# Додавання статичної інформації про застосунок для Prometheus
metrics.info('app_info', 'Open Data AI Analytics Web Application', version='1.0.0')

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "analytics_db")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
TABLE_NAME = os.getenv("TABLE_NAME", "dataset")
CSV_PATH = os.getenv("CSV_PATH", "/app/data/dataset.csv")

def get_db_data():
    try:
        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH, nrows=5, low_memory=False)
            return f"CSV файл знайдено. Поля: {', '.join(df.columns[:5])}..."
    except Exception as e:
        return f"Помилка завантаження даних з БД: {e}"

def load_json(filename):
    path = f"/app/reports/{filename}"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

@app.route('/')
def index():
    db_table = get_db_data()
    quality_report = load_json('quality_report.json')
    research_report = load_json('research_report.json')
    viz_report = load_json('visualization_summary.json')

    plots = []
    if os.path.exists("/app/plots"):
        plots = [f for f in os.listdir("/app/plots") if f.endswith(('.png', '.jpg'))]
        plots.sort()

    return render_template('index.html',
                           table=db_table,
                           quality=quality_report,
                           research=research_report,
                           viz=viz_report,
                           plots=plots)

@app.route('/plots/<filename>')
def get_plot(filename):
    return send_from_directory("/app/plots", filename)

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)