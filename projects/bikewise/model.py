"""Shared feature contract: no target-derived columns enter any model."""
from datetime import date
import math

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CATEGORICAL = ["season", "yr", "mnth", "hr", "holiday", "weekday", "workingday", "weathersit"]
NUMERIC = ["temp", "hum", "windspeed"]
FEATURES = CATEGORICAL + NUMERIC
TARGET = "cnt"
VAL_START = "2012-07-01"
TEST_START = "2012-10-01"
DATA_SHA256 = "e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f"


def chronological_split(df):
    """Keep whole days together; never randomly shuffle future observations."""
    train = df.loc[df.dteday < VAL_START].copy()
    validation = df.loc[(df.dteday >= VAL_START) & (df.dteday < TEST_START)].copy()
    test = df.loc[df.dteday >= TEST_START].copy()
    if min(len(train), len(validation), len(test)) == 0:
        raise ValueError("All chronological splits must contain data.")
    return train, validation, test


def make_models():
    def pipeline(estimator):
        return Pipeline([
            ("features", ColumnTransformer([
                ("categories", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
                ("numeric", StandardScaler(), NUMERIC),
            ], remainder="drop")),
            ("regressor", estimator),
        ])
    return {
        "Mean baseline": pipeline(DummyRegressor(strategy="mean")),
        "Ridge regression": pipeline(Ridge(alpha=10.0)),
        "Gradient boosting": pipeline(HistGradientBoostingRegressor(
            loss="poisson", max_iter=250, learning_rate=0.07,
            max_leaf_nodes=31, l2_regularization=1.0,
            early_stopping=False, random_state=42,
        )),
    }


def nonnegative_predict(model, frame):
    return np.maximum(0.0, model.predict(frame[FEATURES]))


def scenario_features(payload, calendar):
    """Reject malformed/unbounded inputs and use the archive's actual calendar."""
    expected = {"date", "hour", "weather", "temperature", "humidity", "wind"}
    if not isinstance(payload, dict) or set(payload) != expected:
        raise ValueError("Provide exactly date, hour, weather, temperature, humidity and wind.")
    day = payload["date"]
    if not isinstance(day, str):
        raise ValueError("Date must be YYYY-MM-DD.")
    try:
        if date.fromisoformat(day).isoformat() != day or day not in calendar:
            raise ValueError
    except ValueError as exc:
        raise ValueError("Choose an archive date from 2011-01-01 to 2012-12-31.") from exc

    limits = {"hour": (0, 23), "weather": (1, 3), "temperature": (-8, 39), "humidity": (0, 100), "wind": (0, 67)}
    for key, (lower, upper) in limits.items():
        value = payload[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{key} must be a finite number.")
        if not lower <= value <= upper or (key in {"hour", "weather"} and value != int(value)):
            raise ValueError(f"{key} must be between {lower} and {upper}" + (" and an integer." if key in {"hour", "weather"} else "."))
    row = dict(calendar[day])
    row.update(hr=int(payload["hour"]), weathersit=int(payload["weather"]),
               temp=(payload["temperature"] + 8) / 47,
               hum=payload["humidity"] / 100, windspeed=payload["wind"] / 67)
    return pd.DataFrame([row], columns=FEATURES)

