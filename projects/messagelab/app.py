"""Local demonstration. No account, token, upload or remote inference service."""
import json
from pathlib import Path

import joblib
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge

from model import predict_message

ROOT = Path(__file__).parent


def create_app(model_path=None, report_path=None):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 8192
    model_path = Path(model_path) if model_path is not None else ROOT / "artifacts" / "model.joblib"
    report_path = Path(report_path) if report_path is not None else ROOT / "reports" / "metrics.json"
    # joblib must come only from our own training script; it is not an upload format.
    model = joblib.load(model_path) if model_path.exists() else None
    report = json.loads(report_path.read_text()) if report_path.exists() else None

    @app.get("/")
    def index():
        return render_template("index.html", report=report)

    @app.get("/api/health")
    def health():
        return jsonify(ready=model is not None)

    @app.post("/api/predict")
    def predict():
        if model is None:
            return jsonify(error="Model missing. Run download_data.py and train.py first."), 503
        if not request.is_json:
            return jsonify(error="Send an application/json request."), 415
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or set(body) != {"text"}:
            return jsonify(error="Send exactly one field named text."), 400
        try:
            return jsonify(predict_message(model, body["text"]))
        except ValueError as error:
            return jsonify(error=str(error)), 400

    @app.errorhandler(RequestEntityTooLarge)
    def too_large(_error):
        return jsonify(error="Request is too large."), 413

    @app.after_request
    def headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        return response

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5001, debug=False)
