"""Local educational inference service. No accounts or secret API keys required."""
import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request
import joblib
import pandas as pd
from threadpoolctl import threadpool_limits
from werkzeug.exceptions import HTTPException

from model import DATA_SHA256, TEST_START, nonnegative_predict, scenario_features

ROOT = Path(__file__).resolve().parent


def create_app(root=ROOT):
    app = Flask(__name__)
    app.config.update(MAX_CONTENT_LENGTH=4096, JSON_SORT_KEYS=False)
    artifact = root / "artifacts/model.joblib"
    # Only load artifacts generated locally by train.py. There is no model-upload endpoint.
    bundle = joblib.load(artifact) if artifact.exists() else None
    if bundle and bundle.get("dataset_sha256") != DATA_SHA256:
        raise ValueError("Model provenance does not match this dataset.")

    @app.after_request
    def headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/health")
    def health():
        return jsonify(status="ready" if bundle else "training_required", model_loaded=bundle is not None)

    @app.get("/api/report")
    def report():
        path = root / "reports/dashboard.json"
        if not path.exists():
            return jsonify(error="Run python train.py first to create the report."), 503
        return jsonify(json.loads(path.read_text()))

    @app.post("/api/predict")
    def predict():
        if not request.is_json:
            return jsonify(error="Send an application/json request."), 415
        payload = request.get_json()
        if bundle is None:
            return jsonify(error="Run python train.py first to create the model."), 503
        try:
            frame = scenario_features(payload, bundle["calendar"])
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        full_day = pd.concat([frame] * 24, ignore_index=True)
        full_day["hr"] = range(24)
        with threadpool_limits(limits=1):
            curve = nonnegative_predict(bundle["model"], full_day)
        hour = int(payload["hour"])
        return jsonify(prediction=round(float(curve[hour])), model=bundle["model_name"],
                       test_mae=bundle["test_metrics"]["mae"],
                       date=payload["date"], hour=hour,
                       fitting_period=payload["date"] < TEST_START,
                       curve=[{"hour": index, "predicted": round(float(value), 1)} for index, value in enumerate(curve)],
                       note="Historical scenario, not a live forecast. The 24-hour curve holds weather inputs constant.")

    @app.errorhandler(HTTPException)
    def http_error(error):
        if request.path.startswith("/api/"):
            return jsonify(error=error.description), error.code
        return error

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)

