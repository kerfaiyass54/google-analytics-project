import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ml import (
    install_bucket,
    parse_installs,
)


FEATURE_COLUMNS = [
    "app",
    "category",
    "reviews",
    "size_mb",
    "type",
    "price",
    "content_rating",
    "genres",
    "last_updated",
    "current_version",
    "android_version",
]

DATA_QUERY = text("""
SELECT app, category, rating, reviews, size_mb, installs, type, price,
       content_rating, genres, last_updated, current_version, android_version
FROM google_play_apps
WHERE app IS NOT NULL AND category IS NOT NULL
""")


def load_training_data(
    db: Session,
    task: str,
) -> tuple[pd.DataFrame, pd.Series]:
    frame = pd.read_sql(
        DATA_QUERY,
        db.connection(),
    )
    if task == "regression":
        frame["rating"] = pd.to_numeric(
            frame["rating"],
            errors="coerce",
        )
        frame = frame[
            frame["rating"].between(0, 5)
        ].dropna(subset=["rating"])
        target = frame["rating"].astype(float)
    else:
        frame["installs_numeric"] = (
            frame["installs"].map(parse_installs)
        )
        frame = frame.dropna(
            subset=["installs_numeric"]
        )
        frame["target"] = (
            frame["installs_numeric"]
            .astype(int)
            .map(install_bucket)
        )
        target = frame["target"]
    return (
        frame[FEATURE_COLUMNS].copy(),
        target,
    )
