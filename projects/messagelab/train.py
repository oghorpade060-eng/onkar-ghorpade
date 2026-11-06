"""Compare fixed candidates on validation F1; evaluate the winner on untouched test data."""
import json
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

from download_data import DATA_PATH, DATA_SHA256
from model import candidates, partition_record, partitions, read_data

ROOT = Path(__file__).parent


def evaluate(model, frame):
    prediction = model.predict(frame.text)
    return {"accuracy": float(accuracy_score(frame.label, prediction)),
            "spam_precision": float(precision_score(frame.label, prediction, pos_label="spam", zero_division=0)),
            "spam_recall": float(recall_score(frame.label, prediction, pos_label="spam", zero_division=0)),
            "spam_f1": float(f1_score(frame.label, prediction, pos_label="spam", zero_division=0)),
            "confusion_matrix": confusion_matrix(frame.label, prediction, labels=["ham", "spam"]).tolist()}


def train():
    from hashlib import sha256
    if sha256(DATA_PATH.read_bytes()).hexdigest() != DATA_SHA256:
        raise ValueError("Dataset checksum mismatch. Run download_data.py with the original corpus.")
    frame, audit = read_data(DATA_PATH)
    training, validation, test = partitions(frame)
    reports = {}
    for name, model in candidates().items():
        model.fit(training.text, training.label)
        reports[name] = {"validation": evaluate(model, validation)}
    selected = max(reports, key=lambda name: (reports[name]["validation"]["spam_f1"],
                                             reports[name]["validation"]["spam_precision"]))
    development = pd.concat([training, validation])
    final_models = candidates()
    for name, model in final_models.items():
        model.fit(development.text, development.label)
        reports[name]["test"] = evaluate(model, test)
    result = {"dataset": audit, "data_sha256": DATA_SHA256, "seed": 42,
              "splits": {name: partition_record(data) for name, data in
                         [("train", training), ("validation", validation), ("test", test)]},
              "selected_model": selected, "selection_rule": "Highest validation spam F1; precision breaks ties",
              "threshold": "Estimator default; no threshold tuning on the test set",
              "confusion_matrix_order": ["ham", "spam"], "models": reports,
              "sklearn_version": sklearn.__version__}
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "artifacts").mkdir(exist_ok=True)
    (ROOT / "reports" / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    joblib.dump(final_models[selected], ROOT / "artifacts" / "model.joblib")
    print(json.dumps({"selected": selected, "data": audit, "test": reports[selected]["test"]}, indent=2))
    return result


if __name__ == "__main__":
    train()
