"""Reproduce every published metric and create a trusted local model artifact."""
import hashlib
import json
from pathlib import Path
import platform

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from threadpoolctl import threadpool_limits

from model import DATA_SHA256, FEATURES, TARGET, chronological_split, make_models, nonnegative_predict

ROOT = Path(__file__).resolve().parent


def score(truth, predictions):
    return {"mae": round(float(mean_absolute_error(truth, predictions)), 3),
            "rmse": round(float(np.sqrt(mean_squared_error(truth, predictions))), 3),
            "r2": round(float(r2_score(truth, predictions)), 4)}


def train(root=ROOT):
    path = root / "data/hour.csv"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != DATA_SHA256:
        raise ValueError("Dataset checksum mismatch. Restore the original data/hour.csv before training.")
    df = pd.read_csv(path).sort_values(["dteday", "hr"]).reset_index(drop=True)
    if df[FEATURES + [TARGET]].isna().any().any() or df.duplicated(["dteday", "hr"]).any():
        raise ValueError("Unexpected missing values or duplicate hours.")
    train_df, val_df, test_df = chronological_split(df)
    models = make_models()
    evaluations = []
    # Fix the selection criterion before evaluating the test set.
    with threadpool_limits(limits=1):
        for name, estimator in models.items():
            estimator.fit(train_df[FEATURES], train_df[TARGET])
            evaluations.append({"model": name, "validation": score(val_df[TARGET], nonnegative_predict(estimator, val_df))})
        winner = min(evaluations, key=lambda item: item["validation"]["mae"])["model"]
        importance = permutation_importance(models[winner], val_df[FEATURES], val_df[TARGET],
                                            scoring="neg_mean_absolute_error", n_repeats=3, random_state=42, n_jobs=1)
        fitting = pd.concat([train_df, val_df], ignore_index=True)
        final_models = {}
        for item in evaluations:
            name = item["model"]
            fitted = clone(models[name]).fit(fitting[FEATURES], fitting[TARGET])
            item["test"] = score(test_df[TARGET], nonnegative_predict(fitted, test_df))
            final_models[name] = fitted
        final_model = final_models[winner]
        predictions = nonnegative_predict(final_model, test_df)

    def period(frame):
        return {"rows": len(frame), "start": frame.dteday.min(), "end": frame.dteday.max()}
    metrics = {"selected_model": winner, "selection_rule": "Lowest validation MAE; test set never used to choose a model.",
               "dataset_rows": len(df), "dataset_sha256": digest, "features": FEATURES,
               "excluded_columns": ["instant", "dteday", "atemp", "casual", "registered", "cnt"],
               "splits": {"train": period(train_df), "validation": period(val_df), "test": period(test_df)},
               "final_fit": period(fitting), "models": evaluations,
               "versions": {"python": platform.python_version(), "sklearn": sklearn.__version__, "pandas": pd.__version__, "numpy": np.__version__},
               "method": {"seed": 42, "clamp_negative_predictions": True, "early_stopping": False,
                          "importance": "Permutation importance on validation set, before refitting. Increase in MAE; association, not causation."}}
    selected_metrics = next(item["test"] for item in evaluations if item["model"] == winner)
    calendar_columns = ["season", "yr", "mnth", "holiday", "weekday", "workingday"]
    calendar = df.drop_duplicates("dteday").set_index("dteday")[calendar_columns].astype(int).to_dict(orient="index")
    by_hour = df.groupby(["hr", "workingday"])[TARGET].mean()
    hourly = [{"hour": hour, "working": round(float(by_hour.get((hour, 1), 0)), 1),
               "nonworking": round(float(by_hour.get((hour, 0), 0)), 1)} for hour in range(24)]
    sample = test_df.iloc[:168]
    residuals = test_df.assign(prediction=predictions).groupby("hr").apply(
        lambda group: float(np.mean(np.abs(group[TARGET] - group.prediction))), include_groups=False)
    dashboard = {"metrics": metrics, "selected_test": selected_metrics,
                 "total_rentals": int(df[TARGET].sum()), "hourly": hourly,
                 "test_hour_mae": [{"hour": int(hour), "mae": round(value, 2)} for hour, value in residuals.items()],
                 "sample": [{"time": f"{row.dteday} {int(row.hr):02}:00", "actual": int(row.cnt), "predicted": round(float(predictions[i]), 1)}
                            for i, row in enumerate(sample.itertuples())],
                 "importance": sorted([{"feature": name, "increase_mae": round(float(mean), 3), "std": round(float(std), 3)}
                                       for name, mean, std in zip(FEATURES, importance.importances_mean, importance.importances_std)],
                                      key=lambda item: item["increase_mae"], reverse=True)}
    for directory in ["reports", "artifacts"]:
        (root / directory).mkdir(parents=True, exist_ok=True)
    (root / "reports/metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    (root / "reports/dashboard.json").write_text(json.dumps(dashboard, indent=2) + "\n")
    joblib.dump({"model": final_model, "calendar": calendar, "model_name": winner,
                 "test_metrics": selected_metrics, "dataset_sha256": digest}, root / "artifacts/model.joblib")
    print(json.dumps({"selected_model": winner, "rows": len(df), "test": selected_metrics,
                      "splits": metrics["splits"]}, indent=2))
    return metrics


if __name__ == "__main__":
    train()

