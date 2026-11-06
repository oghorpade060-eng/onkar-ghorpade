"""Classify one message without running the dashboard."""
import argparse
import json
from pathlib import Path

import joblib

from model import predict_message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify a short English SMS locally.")
    parser.add_argument("text", help="A short English message, in quotes")
    args = parser.parse_args()
    artifact = Path(__file__).parent / "artifacts" / "model.joblib"
    if not artifact.exists():
        parser.error("Run download_data.py and train.py first.")
    try:
        print(json.dumps(predict_message(joblib.load(artifact), args.text), indent=2))
    except ValueError as error:
        parser.error(str(error))
