from __future__ import annotations
from datetime import date
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor, RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CATEGORICAL = ["app", "category", "type", "content_rating", "genres", "current_version", "android_version"]
NUMERIC = ["reviews", "size_mb", "price", "last_updated_year", "last_updated_month"]

def features_frame(records: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(records).copy()
    frame["last_updated"] = pd.to_datetime(frame["last_updated"], errors="coerce")
    frame["last_updated_year"] = frame["last_updated"].dt.year
    frame["last_updated_month"] = frame["last_updated"].dt.month
    return frame[CATEGORICAL + NUMERIC]

def build_pipeline(task: str, algorithm: str) -> Pipeline:
    numeric = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    categorical = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                            ("onehot", OneHotEncoder(handle_unknown="ignore"))])
    preprocessor = ColumnTransformer([("numeric", numeric, NUMERIC), ("categorical", categorical, CATEGORICAL)])
    choices = {
        "regression": {
            "linear_regression": LinearRegression(),
            "random_forest": RandomForestRegressor(n_estimators=250, random_state=42, n_jobs=-1),
            "extra_trees": ExtraTreesRegressor(n_estimators=250, random_state=42, n_jobs=-1),
            "gradient_boosting": GradientBoostingRegressor(random_state=42),
        },
        "classification": {
            "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
            "random_forest": RandomForestClassifier(n_estimators=250, random_state=42, n_jobs=-1, class_weight="balanced"),
            "extra_trees": ExtraTreesClassifier(n_estimators=250, random_state=42, n_jobs=-1, class_weight="balanced"),
            "gradient_boosting": GradientBoostingClassifier(random_state=42),
        },
    }
    if task not in choices or algorithm not in choices[task]:
        raise ValueError(f"Unsupported {task} algorithm: {algorithm}")
    return Pipeline([("preprocessor", preprocessor), ("estimator", choices[task][algorithm])])

def parse_installs(value) -> int | None:
    if value is None or pd.isna(value):
        return None
    digits = str(value).replace(",", "").replace("+", "").strip()
    return int(digits) if digits.isdigit() else None

def install_bucket(value: int) -> str:
    if value < 1_000: return "<1K"
    if value < 10_000: return "1K-<10K"
    if value < 100_000: return "10K-<100K"
    if value < 1_000_000: return "100K-<1M"
    if value < 10_000_000: return "1M-<10M"
    if value < 100_000_000: return "10M-<100M"
    return "100M+"

def validate_rating(value: float) -> float:
    if not np.isfinite(value):
        raise ValueError("Model returned a non-finite rating.")
    return float(np.clip(value, 0.0, 5.0))
