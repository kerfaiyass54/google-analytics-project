import pandas as pd

CATEGORICAL = [
    "app",
    "category",
    "type",
    "content_rating",
    "genres",
    "current_version",
    "android_version",
]

NUMERIC = [
    "reviews",
    "size_mb",
    "price",
    "last_updated_year",
    "last_updated_month",
]


def features_frame(records: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(records).copy()
    frame["last_updated"] = pd.to_datetime(
        frame["last_updated"],
        errors="coerce",
    )
    frame["last_updated_year"] = frame["last_updated"].dt.year
    frame["last_updated_month"] = frame["last_updated"].dt.month
    return frame[CATEGORICAL + NUMERIC]
