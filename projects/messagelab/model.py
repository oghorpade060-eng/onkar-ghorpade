"""Text preparation, reproducible partitions and local inference."""
import re
from hashlib import sha256

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

SEED = 42
MAX_CHARACTERS = 2000


def normalize(text):
    return re.sub(r"\s+", " ", text.casefold()).strip()


def read_data(path):
    # Split only at the first tab: message content can contain tabs or quotes.
    rows = [line.split("\t", 1) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if any(len(row) != 2 or row[0] not in {"spam", "ham"} for row in rows):
        raise ValueError("Expected one ham/spam label and message per line.")
    frame = pd.DataFrame(rows, columns=["label", "text"])
    frame["key"] = frame.text.map(normalize)
    if frame.key.eq("").any():
        raise ValueError("Empty message in dataset.")
    conflicts = frame.groupby("key").label.nunique()
    bad_keys = set(conflicts[conflicts > 1].index)
    usable = frame.loc[~frame.key.isin(bad_keys)].drop_duplicates("key").reset_index(drop=True)
    audit = {"raw_rows": len(frame), "conflicting_keys": len(bad_keys),
             "conflicting_rows_removed": int(frame.key.isin(bad_keys).sum()),
             "duplicate_rows_removed": len(frame) - int(frame.key.isin(bad_keys).sum()) - len(usable),
             "unique_rows": len(usable), "labels": {k: int(v) for k, v in usable.label.value_counts().items()}}
    return usable, audit


def partitions(frame):
    development, test = train_test_split(frame, test_size=.2, random_state=SEED, stratify=frame.label)
    train, validation = train_test_split(development, test_size=.25, random_state=SEED, stratify=development.label)
    return train, validation, test


def partition_record(frame):
    return {"rows": len(frame), "spam": int(frame.label.eq("spam").sum()),
            "keys_sha256": sha256("\n".join(sorted(frame.key)).encode()).hexdigest()}


def candidates():
    def pipeline(classifier):
        return Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2,
                                                   sublinear_tf=True, strip_accents="unicode")),
                         ("classifier", classifier)])
    return {"majority_baseline": DummyClassifier(strategy="most_frequent"),
            "naive_bayes": pipeline(MultinomialNB(alpha=.3)),
            "logistic_regression": pipeline(LogisticRegression(C=8, class_weight="balanced", max_iter=1000,
                                                                random_state=SEED, solver="liblinear"))}


def validate_text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Enter a non-empty message.")
    if len(value) > MAX_CHARACTERS:
        raise ValueError(f"Use at most {MAX_CHARACTERS} characters.")
    return value.strip()


def predict_message(model, value):
    text = validate_text(value)
    terms = []
    if isinstance(model, Pipeline):
        vector = model.named_steps["tfidf"].transform([text])
        if vector.nnz == 0:
            return {"label": "unknown", "spam_score": None, "terms": [],
                    "note": "No known words were found. This English-language model cannot assess this input."}
        classifier = model.named_steps["classifier"]
        features = model.named_steps["tfidf"].get_feature_names_out()
        spam_index = list(classifier.classes_).index("spam")
        ham_index = list(classifier.classes_).index("ham")
        if hasattr(classifier, "coef_"):
            weights = classifier.coef_[0]
        else:
            weights = classifier.feature_log_prob_[spam_index] - classifier.feature_log_prob_[ham_index]
        contributions = [(features[index], float(value * weights[index]))
                         for index, value in zip(vector.indices, vector.data)]
        terms = [{"term": term, "direction": "spam" if weight > 0 else "ham", "contribution": round(weight, 4)}
                 for term, weight in sorted(contributions, key=lambda pair: -abs(pair[1]))[:6]]
    score = float(model.predict_proba([text])[0][list(model.classes_).index("spam")])
    return {"label": str(model.predict([text])[0]), "spam_score": round(score, 5), "terms": terms,
            "note": "Model score, not calibrated certainty. A ham label does not prove that a message or link is safe."}
