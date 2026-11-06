"""Behavior tests for data separation, API validation, and real-model inference."""
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import create_app
from model import FEATURES, chronological_split, scenario_features


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def payload():
    return {"date": "2012-10-15", "hour": 8, "weather": 1, "temperature": 20, "humidity": 55, "wind": 10}


def test_chronological_holdout_and_no_missing_or_duplicate_hours():
    df = pd.read_csv(ROOT / "data/hour.csv")
    train, val, test = chronological_split(df)
    assert train.dteday.max() < val.dteday.min() < test.dteday.min()
    assert val.dteday.max() < test.dteday.min()
    assert len(train) + len(val) + len(test) == 17379
    assert set(train.instant).isdisjoint(val.instant)
    assert set(val.instant).isdisjoint(test.instant)
    assert not df[FEATURES + ["cnt"]].isna().any().any()
    assert not df.duplicated(["dteday", "hr"]).any()
    assert {"cnt", "casual", "registered", "instant", "dteday"}.isdisjoint(FEATURES)


def test_feature_normalization_and_real_calendar(payload):
    calendar = {"2012-10-15": {"season": 4, "yr": 1, "mnth": 10, "holiday": 0, "weekday": 1, "workingday": 1}}
    frame = scenario_features(payload, calendar)
    assert frame.iloc[0].temp == pytest.approx(28/47)
    assert frame.iloc[0].hum == .55
    assert frame.iloc[0].windspeed == pytest.approx(10/67)
    assert frame.iloc[0].weekday == 1


def test_real_prediction_and_curve_consistency(client, payload):
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data["prediction"], int) and data["prediction"] >= 0
    assert len(data["curve"]) == 24
    assert [point["hour"] for point in data["curve"]] == list(range(24))
    assert all(np.isfinite(point["predicted"]) and point["predicted"] >= 0 for point in data["curve"])
    assert abs(data["prediction"] - data["curve"][8]["predicted"]) <= 1
    assert data["fitting_period"] is False
    assert client.post("/api/predict", json=payload).get_json() == data


@pytest.mark.parametrize("key,value", [("hour", 24), ("hour", -1), ("hour", 8.5), ("weather", 4),
    ("humidity", 101), ("wind", -1), ("temperature", 40), ("temperature", "hot"), ("hour", True),
    ("date", "2026-01-01"), ("date", "2012-02-30"), ("date", 20121015), ("temperature", float("nan"))])
def test_invalid_inputs_are_rejected(client, payload, key, value):
    payload[key] = value
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"]


@pytest.mark.parametrize("body", [[], None, {}, {"path": "../../etc/passwd"}])
def test_invalid_payload_shapes(client, body):
    response = client.post("/api/predict", data=json.dumps(body), content_type="application/json")
    assert response.status_code == 400


def test_unexpected_fields_and_request_size(client, payload):
    assert client.post("/api/predict", json={**payload, "model_path": "untrusted.joblib"}).status_code == 400
    assert client.post("/api/predict", data="plain text").status_code == 415
    assert client.post("/api/predict", data="{oops", content_type="application/json").status_code == 400
    assert client.post("/api/predict", data="x" * 5000, content_type="application/json").status_code == 413


def test_dashboard_assets_and_report(client):
    assert client.get("/").status_code == 200
    for asset in ["/static/style.css", "/static/app.js"]:
        assert client.get(asset).status_code == 200
    response = client.get("/api/report")
    assert response.status_code == 200
    report = response.get_json()
    assert report["metrics"]["selected_model"] == min(report["metrics"]["models"], key=lambda item:item["validation"]["mae"])["model"]
    assert report["metrics"]["splits"]["test"]["rows"] == 2168
    assert len(report["sample"]) == 168
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_missing_artifacts_fail_helpfully(tmp_path, payload):
    client = create_app(tmp_path).test_client()
    assert client.get("/api/health").get_json()["model_loaded"] is False
    assert client.get("/api/report").status_code == 503
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 503 and "train.py" in response.get_json()["error"]

