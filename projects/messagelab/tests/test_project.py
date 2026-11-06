import sys
from pathlib import Path

import joblib
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import create_app
from download_data import DATA_PATH, download
from model import candidates, normalize, partitions, predict_message, read_data


@pytest.fixture(scope="module")
def trained():
    return joblib.load(ROOT / "artifacts" / "model.joblib")


@pytest.fixture
def client():
    return create_app().test_client()


def test_deduplication_and_disjoint_partitions():
    frame, audit = read_data(DATA_PATH)
    assert audit["raw_rows"] == 5574
    assert audit["unique_rows"] == 5159
    a, b, c = [set(part.key) for part in partitions(frame)]
    assert a.isdisjoint(b) and a.isdisjoint(c) and b.isdisjoint(c)
    assert len(a | b | c) == len(frame)


def test_conflicting_duplicates_are_excluded(tmp_path):
    corpus = tmp_path / "sample.tsv"
    corpus.write_text("ham\tHello  WORLD\nspam\thello world\nham\tMeet tonight\nham\tMEET tonight\n")
    frame, audit = read_data(corpus)
    assert frame.text.tolist() == ["Meet tonight"]
    assert audit["conflicting_rows_removed"] == 2
    assert audit["duplicate_rows_removed"] == 1


def test_pipeline_does_not_learn_held_out_words():
    pipeline = candidates()["logistic_regression"]
    pipeline.fit(["normal class note", "normal class plan", "win cash prize", "win cash reward"], ["ham", "ham", "spam", "spam"])
    pipeline.predict(["unseenvocabulary uniqueholdout"])
    assert "unseenvocabulary" not in pipeline.named_steps["tfidf"].vocabulary_


def test_checksum_rejects_modified_data(tmp_path):
    path = tmp_path / "corpus"
    path.write_text("modified")
    with pytest.raises(ValueError, match="checksum"):
        download(path)


@pytest.mark.parametrize("text", ["", "   ", None, 7, [], "x" * 2001])
def test_invalid_message(client, text):
    response = client.post("/api/predict", json={"text": text})
    assert response.status_code == 400


@pytest.mark.parametrize("body", [{}, {"text": "hi", "admin": True}, ["hello"]])
def test_invalid_structure(client, body):
    assert client.post("/api/predict", json=body).status_code == 400


def test_request_limits_and_media_type(client):
    assert client.post("/api/predict", data="hello").status_code == 415
    assert client.post("/api/predict", data='{"text":"' + 'x' * 9000 + '"}', content_type="application/json").status_code == 413
    assert client.post("/api/predict", data="{", content_type="application/json").status_code == 400


def test_real_prediction_and_page(client):
    assert client.get("/").status_code == 200
    assert client.get("/api/health").json == {"ready": True}
    result = client.post("/api/predict", json={"text": "Meet me at the library after class."}).json
    assert result["label"] in {"ham", "spam"}
    assert 0 <= result["spam_score"] <= 1
    assert result["terms"]


def test_unknown_vocabulary_is_not_called_safe(trained):
    result = predict_message(trained, "🦜🦜🦜")
    assert result["label"] == "unknown" and result["spam_score"] is None


def test_missing_model_has_clear_error(tmp_path):
    client = create_app(model_path=tmp_path / "missing.joblib").test_client()
    assert client.get("/api/health").json == {"ready": False}
    assert client.post("/api/predict", json={"text": "hello"}).status_code == 503
